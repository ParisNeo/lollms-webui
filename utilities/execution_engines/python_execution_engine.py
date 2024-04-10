"""
project: lollms_webui
file: python_execution_engine.py 
author: ParisNeo
description: 
    This is a utility for executing python code

"""
from fastapi import routing
from lollms_webui import LOLLMSWebUI
from ascii_colors import get_trace_exception, trace_exception
import time
import subprocess
import json
from lollms.client_session import Client

lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()           

def execute_python(code, client:Client, message_id):
    def spawn_process(code):
        """Executes Python code and returns the output as JSON."""

        # Start the timer.
        start_time = time.time()

        # Create a temporary file.
        root_folder = client.discussion.discussion_folder
        root_folder.mkdir(parents=True,exist_ok=True)
        tmp_file = root_folder/f"ai_code_{message_id}.py"
        with open(tmp_file,"w",encoding="utf8") as f:
            f.write(code)

        try:
            # Execute the Python code in a temporary file.
            process = subprocess.Popen(
                ["python", str(tmp_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=root_folder
            )

            # Get the output and error from the process.
            output, error = process.communicate()
        except Exception as ex:
            # Stop the timer.
            execution_time = time.time() - start_time
            error_message = f"Error executing Python code: {ex}"
            error_json = {"output": "<div class='text-red-500'>"+ex+"\n"+get_trace_exception(ex)+"</div>", "execution_time": execution_time}
            return error_json

        # Stop the timer.
        execution_time = time.time() - start_time

        # Check if the process was successful.
        if process.returncode != 0:
            # The child process threw an exception.
            try:
                error_message = f"Output:{output.decode('utf-8', errors='ignore')}\nError executing Python code:\n{error.decode('utf-8', errors='ignore')}"
            except:
                error_message = f"Error executing Python code:\n{error}"
            error_json = {"output": "<div class='text-red-500'>"+error_message+"</div>", "execution_time": execution_time}
            return error_json

        # The child process was successful.
        output_json = {"output": output.decode("utf8"), "execution_time": execution_time}
        return output_json
    return spawn_process(code)
