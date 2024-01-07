"""
project: lollms_webui
file: shell_execution_engine.py 
author: ParisNeo
description: 
    This is a utility for executing python code

"""
from fastapi import APIRouter, Request, routing
from lollms_webui import LOLLMSWebUI
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from lollms.types import MSG_TYPE
from lollms.main_config import BaseConfig
from lollms.utilities import detect_antiprompt, remove_text_from_string, trace_exception, get_trace_exception
from ascii_colors import ASCIIColors
from api.db import DiscussionsDB
from pathlib import Path
from safe_store.text_vectorizer import TextVectorizer, VectorizationMethod, VisualizationMethod
import tqdm
from fastapi import FastAPI, UploadFile, File
import shutil
import time
import subprocess
import json

lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()           
def execute_bash(lollmsElfServer, code, discussion_id, message_id):
    def spawn_process(code):
        """Executes Python code and returns the output as JSON."""

        # Start the timer.
        start_time = time.time()

        # Create a temporary file.
        root_folder = lollmsElfServer.lollms_paths.personal_outputs_path/"discussions"/f"d_{discussion_id}"
        root_folder.mkdir(parents=True,exist_ok=True)
        try:
            # Execute the Python code in a temporary file.
            process = subprocess.Popen(    
                code,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Get the output and error from the process.
            output, error = process.communicate()
        except Exception as ex:
            # Stop the timer.
            execution_time = time.time() - start_time
            error_message = f"Error executing Python code: {ex}"
            error_json = {"output": "<div class='text-red-500'>"+str(ex)+"\n"+get_trace_exception(ex)+"</div>", "execution_time": execution_time}
            return json.dumps(error_json)

        # Stop the timer.
        execution_time = time.time() - start_time

        # Check if the process was successful.
        if process.returncode != 0:
            # The child process threw an exception.
            error_message = f"Error executing Python code: {error.decode('utf8')}"
            error_json = {"output": "<div class='text-red-500'>"+error_message+"</div>", "execution_time": execution_time}
            return json.dumps(error_json)

        # The child process was successful.
        output_json = {"output": output.decode("utf8"), "execution_time": execution_time}
        return json.dumps(output_json)
    return spawn_process(code)