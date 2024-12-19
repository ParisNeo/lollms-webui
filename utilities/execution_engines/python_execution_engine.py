"""
project: lollms_webui
file: python_execution_engine.py 
author: ParisNeo
description: 
    This is a utility for executing python code

"""

import json
import platform
import subprocess
import time
from pathlib import Path

from ascii_colors import get_trace_exception, trace_exception
from fastapi import routing
from lollms.client_session import Client

from lollms_webui import LOLLMSWebUI

lollmsElfServer: LOLLMSWebUI = LOLLMSWebUI.get_instance()


def execute_python(code, client, message_id, build_file=True):
    def spawn_process(code):
        """Executes Python code in a new terminal and returns the output as JSON."""

        # Start the timer.
        start_time = time.time()

        # Create a temporary file.
        root_folder = client.discussion.discussion_folder
        root_folder.mkdir(parents=True, exist_ok=True)
        tmp_file = root_folder / f"ai_code_{message_id}.py"
        with open(tmp_file, "w", encoding="utf8") as f:
            f.write(code)

        try:
            # Determine the platform and open a terminal to execute the Python code.
            system = platform.system()
            if system == "Windows":
                process = subprocess.Popen(
                    f"""start cmd /k "cd /d "{root_folder}" && python "{tmp_file}" && pause" """,
                    shell=True,
                )
            elif system == "Darwin":  # macOS
                process = subprocess.Popen(
                    [
                        "open",
                        "-a",
                        "Terminal",
                        f'cd "{root_folder}" && python "{tmp_file}"',
                    ],
                    shell=True,
                )
            elif system == "Linux":
                process = subprocess.Popen(
                    [
                        "x-terminal-emulator",
                        "-e",
                        f'bash -c "cd \\"{root_folder}\\" && python \\"{tmp_file}\\"; exec bash"',
                    ],
                    shell=True,
                )
            else:
                raise Exception(f"Unsupported platform: {system}")

            # Wait for the process to complete.
            process.wait()

            # Get the output and error from the process.
            output, error = process.communicate()
        except Exception as ex:
            # Stop the timer.
            execution_time = time.time() - start_time
            error_message = f"Error executing Python code: {ex}"
            error_json = {
                "output": "<div class='text-red-500'>"
                + error_message
                + "\n"
                + get_trace_exception(ex)
                + "</div>",
                "execution_time": execution_time,
            }
            return error_json

        # Stop the timer.
        execution_time = time.time() - start_time

        # Check if the process was successful.
        if process.returncode != 0:
            # The child process threw an exception.
            try:
                error_message = f"Output: {output.decode('utf-8', errors='ignore')}\nError executing Python code:\n{error.decode('utf-8', errors='ignore')}"
            except:
                error_message = f"Error executing Python code:\n{error}"
            error_json = {
                "output": "<div class='text-red-500'>" + error_message + "</div>",
                "execution_time": execution_time,
            }
            return error_json

        # The child process was successful.
        if output:
            output_json = {
                "output": output.decode("utf8"),
                "execution_time": execution_time,
            }
        else:
            output_json = {"output": "", "execution_time": execution_time}
        return output_json

    return spawn_process(code)


def execute_python_old(code, client: Client, message_id, build_file=True):
    def spawn_process(code):
        """Executes Python code and returns the output as JSON."""

        # Start the timer.
        start_time = time.time()

        # Create a temporary file.
        root_folder = client.discussion.discussion_folder
        root_folder.mkdir(parents=True, exist_ok=True)
        tmp_file = root_folder / f"ai_code_{message_id}.py"
        with open(tmp_file, "w", encoding="utf8") as f:
            f.write(code)

        try:
            # Execute the Python code in a temporary file.
            process = subprocess.Popen(
                ["python", str(tmp_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=root_folder,
            )

            # Get the output and error from the process.
            output, error = process.communicate()
        except Exception as ex:
            # Stop the timer.
            execution_time = time.time() - start_time
            error_message = f"Error executing Python code: {ex}"
            error_json = {
                "output": "<div class='text-red-500'>"
                + ex
                + "\n"
                + get_trace_exception(ex)
                + "</div>",
                "execution_time": execution_time,
            }
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
            error_json = {
                "output": "<div class='text-red-500'>" + error_message + "</div>",
                "execution_time": execution_time,
            }
            return error_json

        # The child process was successful.
        output_json = {
            "output": output.decode("utf8"),
            "execution_time": execution_time,
        }
        return output_json

    return spawn_process(code)


def create_and_execute_script(code, message_id, root_folder):
    try:
        # Ensure the root folder exists
        root_folder = Path(root_folder)
        root_folder.mkdir(parents=True, exist_ok=True)

        # Create the temporary Python file
        tmp_file = root_folder / f"ai_code_{message_id}.py"
        with open(tmp_file, "w", encoding="utf8") as f:
            f.write(code)

        # Determine the platform and open a terminal to execute the Python code
        system = platform.system()
        if system == "Windows":
            subprocess.Popen(
                f"""start cmd /k "cd /d "{root_folder}" && python "{tmp_file}" && pause" """,
                shell=True,
            )
        elif system == "Darwin":  # macOS
            subprocess.Popen(
                [
                    "open",
                    "-a",
                    "Terminal",
                    f'cd "{root_folder}" && python "{tmp_file}"',
                ],
                shell=True,
            )
        elif system == "Linux":
            subprocess.Popen(
                [
                    "x-terminal-emulator",
                    "-e",
                    f'bash -c "cd \\"{root_folder}\\" && python \\"{tmp_file}\\"; exec bash"',
                ],
                shell=True,
            )
        else:
            raise Exception(f"Unsupported platform: {system}")

    except Exception as ex:
        error_message = f"Error executing Python code: {ex}"
        error_json = {
            "output": "<div class='text-red-500'>"
            + error_message
            + "\n"
            + get_trace_exception(ex)
            + "</div>",
            "execution_time": 0,
        }
        print(error_json)


if __name__ == "__main__":
    code = "print('Hello world');input('hi')"
    message_id = 102
    root_folder = r"E:\lollms\discussion_databases\html stuff\105"
    create_and_execute_script(code, message_id, root_folder)
