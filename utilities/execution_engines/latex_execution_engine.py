"""
project: lollms_webui
file: latex_execution_engine.py 
author: ParisNeo
description: 
    This is a utility for executing latex code

"""
from fastapi import APIRouter, Request, routing
from lollms_webui import LOLLMSWebUI
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from lollms.types import MSG_TYPE
from lollms.main_config import BaseConfig
from ascii_colors import get_trace_exception, trace_exception
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

def execute_latex(code, discussion_id, message_id):
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
                return error_json
            # If the compilation is successful, you will get a PDF file
            pdf_file = tmp_file.with_suffix('.pdf')
            print(f"PDF file generated: {pdf_file}")

        except subprocess.CalledProcessError as ex:
            lollmsElfServer.error(f"Error occurred while compiling LaTeX: {ex}") 
            error_json = {"output": "<div class='text-red-500'>"+str(ex)+"\n"+get_trace_exception(ex)+"</div>", "execution_time": execution_time}
            return error_json

        # Stop the timer.
        execution_time = time.time() - start_time

        # The child process was successful.
        pdf_file=str(pdf_file).replace("\\","/")
        if not "http" in lollmsElfServer.config.host:
            host = "http://"+lollmsElfServer.config.host
        else:
            host = lollmsElfServer.config.host
        url = f"{host}:{lollmsElfServer.config.port}/{pdf_file[pdf_file.index('outputs'):]}"
        output_json = {"output": f"Pdf file generated at: {pdf_file}\n<a href='{url}'>Click here to show</a>", "execution_time": execution_time}
        return output_json
    return spawn_process(code)
