from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails
import subprocess
import shlex
from pathlib import Path
from ascii_colors import trace_exception
import subprocess
import sys
from typing import List, Dict

import subprocess
import sys
import threading
import queue
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig

class PersistentShell:
    def __init__(self, client:Client):
        # Choose the shell based on the platform
        shell_cmd = "cmd.exe" if sys.platform == "win32" else "/bin/bash"
        self.proc = subprocess.Popen(
            shell_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self.client = client
        self.output_queue = queue.Queue()
        # Start a thread to continuously read stdout
        self.output_thread = threading.Thread(target=self._enqueue_output, args=(self.proc.stdout, self.output_queue))
        self.output_thread.daemon = True
        self.output_thread.start()

    def _enqueue_output(self, stream, queue_obj):
        for line in iter(stream.readline, ''):
            queue_obj.put(line)
        stream.close()

    def execute(self, command, timeout=5):
        """
        Send a command to the shell and collect its output.
        Note: This is a simplified approach; in a production scenario, you'd need a robust way
        to determine when the command has finished executing.
        """
        path_str = self.client.discussion_path
        if sys.platform == "win32":
            # For cmd.exe, 'cd /d' changes drive and directory.
            # We chain commands using '&'. '&&' could also be used for conditional execution.
            full_command = f'cd /d {path_str} & {command}'
        else:
            # For bash/sh, 'cd' changes directory.
            # We chain commands using ';'. '&&' for conditional execution.
            full_command = f'cd {path_str} && {command}'
        if self.proc.stdin:
            self.proc.stdin.write(full_command + "\n")
            self.proc.stdin.flush()
        output_lines = []
        try:
            # Read available output for a fixed amount of time
            while True:
                line = self.output_queue.get(timeout=timeout)
                output_lines.append(line)
                # A heuristic: break if we see the prompt (this might need customization)
                if line.strip() in [">", "$"]:
                    break
        except queue.Empty:
            pass  # Timeout reached
        return ''.join(output_lines)

    def close(self):
        if self.proc.stdin:
            self.proc.stdin.write("exit\n")
            self.proc.stdin.flush()
        self.proc.terminate()
        self.proc.wait()
    
class ExecuteBashCommand(FunctionCall):
    """
    Execute a bash command and return its output to be analyzed by the LLM.
    
    This function wraps around subprocess to execute shell commands safely.
    """

    def __init__(self, app: LollmsApplication, client: Client):
        static_parameters = TypedConfig(
            ConfigTemplate([
            ]),
            BaseConfig(config={
            })
        )        
        super().__init__("execute_bash_command", app,FunctionType.CLASSIC, client, static_parameters)
    
    def update_context(self, context, constructed_context:List[str]):
        """
        Update the context if needed.
        This method should be overridden by subclasses.
        """
        constructed_context.append(f"running platform: {sys.platform}")
        constructed_context.append(f"Make sure the commands you use are compatible with the platform")
        constructed_context.append(f"Try to put all commands in a single function call as each one has its own shell")
        if sys.platform == "win32":
            constructed_context.append(f"Don't forget, in windows, to change the drive, you need to use cd /d")

        return constructed_context

    def execute(self,context:LollmsContextDetails, command: str) -> str:
        """
        Execute the provided bash command.

        Args:
            command (str): The bash command to execute.

        Returns:
            str: The command's output or an error message if execution failed.
        """
        try:
            # Split the command into a list of arguments
            shell = PersistentShell(self.client)

            # The following command will change the directory and then clone the repository in that folder.
            output = shell.execute(command=command)
            ai_output = self.personality.fast_gen(context.build_prompt(self.app.template,custom_entries=self.app.ai_full_header+context.ai_output+f"\nExecution output:\n```\n{output}\n```"+self.app.ai_full_header),callback=self.personality.sink)
            output = f"Execution output:\n```\n{output}\n```\n{ai_output}"    
            return output
        except subprocess.TimeoutExpired:
            return "Command execution timed out."
        except Exception as e:
            trace_exception(e)
            return f"An error occurred while executing the command: {str(e)}"