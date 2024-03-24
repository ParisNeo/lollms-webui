"""
project: lollms_user
file: lollms_user.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes allow users to do advanced stuff like executing code.

"""
from fastapi import APIRouter, Request
from lollms_webui import LOLLMSWebUI
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse
from lollms.types import MSG_TYPE
from lollms.main_config import BaseConfig
from lollms.utilities import detect_antiprompt, remove_text_from_string, trace_exception, show_yes_no_dialog
from lollms.security import sanitize_path, forbid_remote_access
from ascii_colors import ASCIIColors
from lollms.databases.discussions_database import DiscussionsDB
from pathlib import Path
from safe_store.text_vectorizer import TextVectorizer, VectorizationMethod, VisualizationMethod
import tqdm
from fastapi import FastAPI, UploadFile, File
import shutil
import os
import platform
import string
import re
import subprocess   
from typing import Optional

# Regular expression pattern to validate file paths
FILE_PATH_REGEX = r'^[a-zA-Z0-9_\-\\\/]+$'

# Function to validate file paths using the regex pattern
def validate_file_path(path):
    return re.match(FILE_PATH_REGEX, path)

from utilities.execution_engines.python_execution_engine import execute_python
from utilities.execution_engines.latex_execution_engine import execute_latex
from utilities.execution_engines.shell_execution_engine import execute_bash
from utilities.execution_engines.javascript_execution_engine import execute_javascript
from utilities.execution_engines.html_execution_engine import execute_html

from utilities.execution_engines.mermaid_execution_engine import execute_mermaid
from utilities.execution_engines.graphviz_execution_engine import execute_graphviz



# ----------------------- Defining router and main class ------------------------------

router = APIRouter()
lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()


class CodeRequest(BaseModel):
    client_id: str  = Field(...)
    code: str = Field(..., description="Code to be executed")
    discussion_id: int = Field(..., description="Discussion ID")
    message_id: int = Field(..., description="Message ID")
    language: str = Field(..., description="Programming language of the code")

@router.post("/execute_code")
async def execute_code(request: CodeRequest):
    """
    Executes Python code and returns the output.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """
    client = lollmsElfServer.session.get_client(request.client_id)
    if lollmsElfServer.config.headless_server_mode:
        return {"status":False,"error":"Code execution is blocked when in headless mode for obvious security reasons!"}

    if lollmsElfServer.config.host!="localhost" and lollmsElfServer.config.host!="127.0.0.1":
        return {"status":False,"error":"Code execution is blocked when the server is exposed outside for very obvious reasons!"}

    if not lollmsElfServer.config.turn_on_code_execution:
        return {"status":False,"error":"Code execution is blocked by the configuration!"}

    if lollmsElfServer.config.turn_on_code_validation:
        if not show_yes_no_dialog("Validation","Do you validate the execution of the code?"):
            return {"status":False,"error":"User refused the execution!"}

    try:
        code = request.code
        discussion_id = request.discussion_id
        message_id = request.message_id
        language = request.language

        if language=="python":
            ASCIIColors.info("Executing python code:")
            ASCIIColors.yellow(code)
            return execute_python(code, client, message_id)
        if language=="javascript":
            ASCIIColors.info("Executing javascript code:")
            ASCIIColors.yellow(code)
            return execute_javascript(code)
        if language in ["html","html5","svg"]:
            ASCIIColors.info("Executing javascript code:")
            ASCIIColors.yellow(code)
            return execute_html(code)

        elif language=="latex":
            ASCIIColors.info("Executing latex code:")
            ASCIIColors.yellow(code)
            return execute_latex(code, client, message_id)
        elif language in ["bash","shell","cmd","powershell"]:
            ASCIIColors.info("Executing shell code:")
            ASCIIColors.yellow(code)
            return execute_bash(code, client)
        elif language in ["mermaid"]:
            ASCIIColors.info("Executing mermaid code:")
            ASCIIColors.yellow(code)
            return execute_mermaid(code)
        elif language in ["graphviz","dot"]:
            ASCIIColors.info("Executing graphviz code:")
            ASCIIColors.yellow(code)
            return execute_graphviz(code)
        return {"status": False, "error": "Unsupported language", "execution_time": 0}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}
    


class FilePath(BaseModel):
    path: Optional[str] = Field(None, max_length=500)

@router.post("/open_file")
async def open_file(file_path: FilePath):
    """
    Opens code in vs code.

    :param file_path: The file path object.
    :return: A JSON response with the status of the operation.
    """
    if lollmsElfServer.config.headless_server_mode:
        return {"status":False,"error":"Open file is blocked when in headless mode for obvious security reasons!"}

    if lollmsElfServer.config.host!="localhost" and lollmsElfServer.config.host!="127.0.0.1":
        return {"status":False,"error":"Open file is blocked when the server is exposed outside for very obvious reasons!"}

    if lollmsElfServer.config.turn_on_open_file_validation:
        if not show_yes_no_dialog("Validation","Do you validate the opening of a file?"):
            return {"status":False,"error":"User refused the opeining file!"}

    forbid_remote_access(lollmsElfServer)
    try:
        # Validate the 'path' parameter
        path = sanitize_path(file_path.path)
        if not validate_file_path(path):
            return {"status":False,"error":"Invalid file path"}
        
        # Sanitize the 'path' parameter
        path = os.path.realpath(path)
        
        # Use subprocess.Popen to safely open the file
        subprocess.Popen(["start", path])
        
        return {"status": True, "execution_time": 0}
    
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}



class FilePath(BaseModel):
    path: Optional[str] = Field(None, max_length=500)

@router.post("/open_folder")
async def open_folder(file_path: FilePath):
    """
    Opens a folder

    :param file_path: The file path object.
    :return: A JSON response with the status of the operation.
    """
    if lollmsElfServer.config.headless_server_mode:
        return {"status":False,"error":"Open file is blocked when in headless mode for obvious security reasons!"}

    if lollmsElfServer.config.host!="localhost" and lollmsElfServer.config.host!="127.0.0.1":
        return {"status":False,"error":"Open file is blocked when the server is exposed outside for very obvious reasons!"}

    if lollmsElfServer.config.turn_on_open_file_validation:
        if not show_yes_no_dialog("Validation","Do you validate the opening of a file?"):
            return {"status":False,"error":"User refused the opeining file!"}

    forbid_remote_access(lollmsElfServer)
    try:
        # Validate the 'path' parameter
        path = file_path.path
       
        # Sanitize the 'path' parameter
        path = os.path.realpath(path)
        
        # Use subprocess.Popen to safely open the file
        if platform.system() == 'Windows':
            subprocess.Popen(f'explorer "{path}"')
        elif platform.system() == 'Linux':
            subprocess.run(['xdg-open', str(path)], check=True)
        elif platform.system() == 'Darwin':
            subprocess.run(['open', str(path)], check=True)

        
        return {"status": True, "execution_time": 0}
    
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}

class OpenCodeFolderInVsCodeRequestModel(BaseModel):
    client_id: str = Field(...)
    discussion_id: Optional[int] = Field(None, gt=0)
    message_id: Optional[int] = Field(None, gt=0)
    code: Optional[str]

@router.post("/open_code_folder_in_vs_code")
async def open_code_folder_in_vs_code(request: OpenCodeFolderInVsCodeRequestModel):

    client = lollmsElfServer.session.get_client(request.client_id)

    if lollmsElfServer.config.headless_server_mode:
        return {"status":False,"error":"Open code folder in vscode is blocked when in headless mode for obvious security reasons!"}

    if lollmsElfServer.config.host!="localhost" and lollmsElfServer.config.host!="127.0.0.1":
        return {"status":False,"error":"Open code folder in vscode is blocked when the server is exposed outside for very obvious reasons!"}

    if lollmsElfServer.config.turn_on_open_file_validation:
        if not show_yes_no_dialog("Validation","Do you validate the opening of folder in vscode?"):
            return {"status":False,"error":"User refused the execution!"}

    try:
        if request.discussion_id:        
            ASCIIColors.info("Opening folder:")
            root_folder = client.discussion.discussion_folder
            root_folder.mkdir(parents=True,exist_ok=True)
            tmp_file = root_folder/f"ai_code_{request.message_id}.py"
            with open(tmp_file,"w") as f:
                f.write(request.code)
            
            if os.path.isdir(root_folder):
                path = '"'+str(root_folder)+'"'.replace("\\","/")
                subprocess.run(['code', path], shell=True)


        return {"status": True, "execution_time": 0}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(str(ex))
        return {"status":False,"error":"An error occurred during processing."}
    
class VSCodeData(BaseModel):
    client_id: str = Field(...)
    discussion_id: Optional[int] = Field(None, ge=0)
    message_id: Optional[int] = Field(None, ge=0)
    code: str = Field(...)

@router.post("/open_code_in_vs_code")
async def open_code_in_vs_code(vs_code_data: VSCodeData):
    """
    Opens code in vs code.

    :param vs_code_data: The data object.
    :return: A JSON response with the status of the operation.
    """
    client = lollmsElfServer.session.get_client(vs_code_data.client_id)
    if lollmsElfServer.config.headless_server_mode:
        return {"status":False,"error":"Open code in vs code is blocked when in headless mode for obvious security reasons!"}

    if lollmsElfServer.config.host!="localhost" and lollmsElfServer.config.host!="127.0.0.1":
        return {"status":False,"error":"Open code in vs code is blocked when the server is exposed outside for very obvious reasons!"}

    if lollmsElfServer.config.turn_on_open_file_validation:
        if not show_yes_no_dialog("Validation","Do you validate the opening of a code in vscode?"):
            return {"status":False,"error":"User refused the opeining file!"}

    try:
        discussion_id = vs_code_data.discussion_id
        message_id = vs_code_data.message_id
        code = vs_code_data.code

        ASCIIColors.info("Opening folder:")
        # Create a temporary file.
        root_folder = client.discussion.discussion_folder

        root_folder.mkdir(parents=True,exist_ok=True)
        tmp_file = root_folder/f"ai_code_{message_id}.py"
        with open(tmp_file,"w") as f:
            f.write(code)
        
        # Use subprocess.Popen to safely open the file
        subprocess.Popen(["code", str(tmp_file)], shell=True)
        
        return {"status": True, "execution_time": 0}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}
    
class FolderRequest(BaseModel):
    client_id: str = Field(...)
    discussion_id: Optional[int] = Field(None, title="The discussion ID")
    folder_path: Optional[str] = Field(None, title="The folder path")

@router.post("/open_code_folder")
async def open_code_folder(request: FolderRequest):
    """
    Opens code folder.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """
    client = lollmsElfServer.session.get_client(request.client_id)
    if lollmsElfServer.config.headless_server_mode:
        return {"status":False,"error":"Open code folder is blocked when in headless mode for obvious security reasons!"}

    if lollmsElfServer.config.host!="localhost" and lollmsElfServer.config.host!="127.0.0.1":
        return {"status":False,"error":"Open code folder is blocked when the server is exposed outside for very obvious reasons!"}
    
    if lollmsElfServer.config.turn_on_open_file_validation:
        if not show_yes_no_dialog("Validation","Do you validate the opening of a folder?"):
            return {"status":False,"error":"User refused the opeining folder!"}

    try:
        ASCIIColors.info("Opening folder:")
        # Create a temporary file.
        root_folder = client.discussion.discussion_folder
        root_folder.mkdir(parents=True, exist_ok=True)
        if platform.system() == 'Windows':
            subprocess.Popen(f'explorer "{root_folder}"')
        elif platform.system() == 'Linux':
            subprocess.run(['xdg-open', str(root_folder)], check=True)
        elif platform.system() == 'Darwin':
            subprocess.run(['open', str(root_folder)], check=True)
        return {"status": True, "execution_time": 0}

    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status": False, "error": "An error occurred while processing the request"}

@router.get("/start_recording")
def start_recording():
    if lollmsElfServer.config.headless_server_mode:
        return {"status":False,"error":"Start recording is blocked when in headless mode for obvious security reasons!"}

    if lollmsElfServer.config.host!="localhost" and lollmsElfServer.config.host!="127.0.0.1":
        return {"status":False,"error":"Start recording is blocked when the server is exposed outside for very obvious reasons!"}

    lollmsElfServer.info("Starting audio capture")
    try:
        from lollms.media import AudioRecorder
        lollmsElfServer.rec_output_folder = lollmsElfServer.lollms_paths.personal_outputs_path/"audio_rec"
        lollmsElfServer.rec_output_folder.mkdir(exist_ok=True, parents=True)
        lollmsElfServer.summoned = False
        lollmsElfServer.audio_cap = AudioRecorder(lollmsElfServer.sio,lollmsElfServer.rec_output_folder/"rt.wav", callback=lollmsElfServer.audio_callback,lollmsCom=lollmsElfServer, transcribe=True)
        lollmsElfServer.audio_cap.start_recording()
    except:
        lollmsElfServer.InfoMessage("Couldn't load media library.\nYou will not be able to perform any of the media linked operations. please verify the logs and install any required installations")


@router.get("/stop_recording")
def stop_recording():
    if lollmsElfServer.config.headless_server_mode:
        return {"status":False,"error":"Stop recording is blocked when in headless mode for obvious security reasons!"}

    if lollmsElfServer.config.host!="localhost" and lollmsElfServer.config.host!="127.0.0.1":
        return {"status":False,"error":"Stop recording is blocked when the server is exposed outside for very obvious reasons!"}

    lollmsElfServer.info("Stopping audio capture")
    text = lollmsElfServer.audio_cap.stop_recording()
    return text

