"""
project: lollms_webui
file: latex_execution_engine.py 
author: ParisNeo
description: 
    This is a utility for executing latex code

"""

import json
import shutil
import subprocess
import time
from pathlib import Path

import tqdm
from ascii_colors import ASCIIColors, get_trace_exception, trace_exception
from fastapi import APIRouter, FastAPI, File, Request, UploadFile, routing
from lollms.client_session import Client
from lollms.databases.discussions_database import DiscussionsDB
from lollms.main_config import BaseConfig
from lollms.types import MSG_OPERATION_TYPE
from lollms.utilities import discussion_path_to_url
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from lollms_webui import LOLLMSWebUI

lollmsElfServer: LOLLMSWebUI = LOLLMSWebUI.get_instance()


def execute_latex(code, client: Client, message_id):
    # Start the timer.
    start_time = time.time()

    # Create a temporary file.
    root_folder = client.discussion.discussion_folder
    root_folder.mkdir(parents=True, exist_ok=True)
    tmp_file = root_folder / f"latex_file_{message_id}.tex"
    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write(code)

    try:
        # Determine the pdflatex command based on the provided or default path
        if lollmsElfServer.config.pdf_latex_path:
            pdflatex_command = lollmsElfServer.config.pdf_latex_path
        else:
            pdflatex_command = "pdflatex"
        # Set the execution path to the folder containing the tmp_file
        execution_path = tmp_file.parent

        # Execute the Python code in a temporary file.
        process = subprocess.Popen(
            [pdflatex_command, "-interaction=nonstopmode", str(tmp_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=execution_path,
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
        pdf_file = tmp_file.with_suffix(".pdf")
        print(f"PDF file generated: {pdf_file}")
        try:
            error_message = f"Error executing Python code:\n{error.decode('utf-8', errors='ignore')}"
        except:
            error_message = f"Error executing Python code:\n{error}"
        if pdf_file.exists():
            # The child process was successful.
            pdf_file = str(pdf_file).replace("\\", "/")
            if (
                not "http" in lollmsElfServer.config.host
                and not "https" in lollmsElfServer.config.host
            ):
                host = "http://" + lollmsElfServer.config.host
            else:
                host = lollmsElfServer.config.host

            url = f"{host}:{lollmsElfServer.config.port}/{discussion_path_to_url(pdf_file)}"
            error_json = {
                "output": f"<div>Pdf file generated at: {pdf_file}\n<a href='{url}' target='_blank'>Click here to show</a></div><div>Output:{output.decode('utf-8', errors='ignore')}\n</div><div class='text-red-500'>"
                + error_message
                + "</div>",
                "execution_time": execution_time,
            }

        else:
            error_json = {
                "output": f"<div>Output:{output.decode('utf-8', errors='ignore')}\n</div><div class='text-red-500'>"
                + error_message
                + "</div>",
                "execution_time": execution_time,
            }
        return error_json

    # The child process was successful.
    # If the compilation is successful, you will get a PDF file
    pdf_file = tmp_file.with_suffix(".pdf")
    print(f"PDF file generated: {pdf_file}")

    # The child process was successful.
    pdf_file = str(pdf_file).replace("\\", "/")
    if (
        not "http" in lollmsElfServer.config.host
        and not "https" in lollmsElfServer.config.host
    ):
        host = "http://" + lollmsElfServer.config.host
    else:
        host = lollmsElfServer.config.host

    url = f"{host}:{lollmsElfServer.config.port}{discussion_path_to_url(pdf_file)}"
    output_json = {
        "output": f"Pdf file generated at: {pdf_file}\n<a href='{url}' target='_blank'>Click here to show</a>",
        "execution_time": execution_time,
    }
    return output_json
