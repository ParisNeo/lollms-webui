"""
project: lollms_webui
file: shell_execution_engine.py 
author: ParisNeo
description: 
    This is a utility for executing python code

"""

import json
import subprocess
import time

from ascii_colors import get_trace_exception, trace_exception
from lollms.client_session import Client

from lollms_webui import LOLLMSWebUI

lollmsElfServer: LOLLMSWebUI = LOLLMSWebUI.get_instance()


def execute_bash(code, client: Client, message_id, build_file=False):
    def spawn_process(code):
        """Executes Python code and returns the output as JSON."""

        # Start the timer.
        start_time = time.time()

        # Create a temporary file.
        root_folder = client.discussion.discussion_folder
        root_folder.mkdir(parents=True, exist_ok=True)
        try:
            # Execute the Python code in a temporary file.
            process = subprocess.Popen(
                code,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=client.discussion.discussion_folder,
            )

            # Get the output and error from the process.
            output, error = process.communicate()
        except Exception as ex:
            # Stop the timer.
            execution_time = time.time() - start_time
            error_message = f"Error executing Python code: {ex}"
            error_json = {
                "output": "<div class='text-red-500'>"
                + str(ex)
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
            error_message = (
                f"Error executing Python code: {error.decode('utf8','ignore')}"
            )
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
