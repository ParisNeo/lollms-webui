"""
project: lollms_webui
file: python_execution_engine.py 
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

def execute_python(code, discussion_id, message_id):
    def spawn_process(code):
        """Executes Python code and returns the output as JSON."""

        # Start the timer.
        start_time = time.time()

        # Create a temporary file.
        root_folder = lollmsElfServer.lollms_paths.personal_outputs_path/"discussions"/f"d_{discussion_id}"
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

def execute_latex(lollmsElfServer:LOLLMSWebUI, code, discussion_id, message_id):
    def spawn_process(code):
        """Executes Python code and returns the output as JSON."""

        # Start the timer.
        start_time = time.time()

        # Create a temporary file.
        root_folder = lollmsElfServer.lollms_paths.personal_outputs_path/"discussions"/f"d_{discussion_id}"
        root_folder.mkdir(parents=True,exist_ok=True)
        tmp_file = root_folder/f"latex_file_{message_id}.tex"
        with open(tmp_file,"w",encoding="utf8") as f:
            f.write(code)
        try:
            # Determine the pdflatex command based on the provided or default path
            if lollmsElfServer.config.pdf_latex_path:
                pdflatex_command = lollmsElfServer.config.pdf_latex_path
            else:
                pdflatex_command = 'pdflatex'
            # Set the execution path to the folder containing the tmp_file
            execution_path = tmp_file.parent
            # Run the pdflatex command with the file path
            result = subprocess.run([pdflatex_command, "-interaction=nonstopmode", tmp_file], check=True, capture_output=True, text=True, cwd=execution_path)
            # Check the return code of the pdflatex command
            if result.returncode != 0:
                error_message = result.stderr.strip()
                execution_time = time.time() - start_time
                error_json = {"output": f"Error occurred while compiling LaTeX: {error_message}", "execution_time": execution_time}
                return json.dumps(error_json)
            # If the compilation is successful, you will get a PDF file
            pdf_file = tmp_file.with_suffix('.pdf')
            print(f"PDF file generated: {pdf_file}")

        except subprocess.CalledProcessError as ex:
            lollmsElfServer.error(f"Error occurred while compiling LaTeX: {ex}") 
            error_json = {"output": "<div class='text-red-500'>"+str(ex)+"\n"+get_trace_exception(ex)+"</div>", "execution_time": execution_time}
            return json.dumps(error_json)

        # Stop the timer.
        execution_time = time.time() - start_time

        # The child process was successful.
        pdf_file=str(pdf_file)
        url = f"{routing.get_url_path_for(lollmsElfServer.app.router, 'main')[:-4]}{pdf_file[pdf_file.index('outputs'):]}"
        output_json = {"output": f"Pdf file generated at: {pdf_file}\n<a href='{url}'>Click here to show</a>", "execution_time": execution_time}
        return json.dumps(output_json)
    return spawn_process(code)

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