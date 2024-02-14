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
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from lollms.types import MSG_TYPE
from lollms.main_config import BaseConfig
from lollms.utilities import detect_antiprompt, remove_text_from_string, trace_exception
from ascii_colors import ASCIIColors
from api.db import DiscussionsDB
from pathlib import Path
from safe_store.text_vectorizer import TextVectorizer, VectorizationMethod, VisualizationMethod
import tqdm
from fastapi import FastAPI, UploadFile, File
import shutil
import os
import platform
import string
import re

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

@router.post("/execute_code")
async def execute_code(request: Request):
    """
    Executes Python code and returns the output.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """
    if lollmsElfServer.config.headless_server_mode:
        return {"status":False,"error":"Code execution is blocked when in headless mode for obvious security reasons!"}

    if lollmsElfServer.config.host=="0.0.0.0":
        return {"status":False,"error":"Code execution is blocked when the server is exposed outside for very obvipous reasons!"}

    try:
        data = (await request.json())
        code = data["code"]
        discussion_id = int(data.get("discussion_id","unknown_discussion"))
        message_id = int(data.get("message_id","unknown_message"))
        language = data.get("language","python")
        


        if language=="python":
            ASCIIColors.info("Executing python code:")
            ASCIIColors.yellow(code)
            return execute_python(code, discussion_id, message_id)
        if language=="javascript":
            ASCIIColors.info("Executing javascript code:")
            ASCIIColors.yellow(code)
            return execute_javascript(code, discussion_id, message_id)
        if language in ["html","html5","svg"]:
            ASCIIColors.info("Executing javascript code:")
            ASCIIColors.yellow(code)
            return execute_html(code, discussion_id, message_id)
        
        elif language=="latex":
            ASCIIColors.info("Executing latex code:")
            ASCIIColors.yellow(code)
            return execute_latex(code, discussion_id, message_id)
        elif language in ["bash","shell","cmd","powershell"]:
            ASCIIColors.info("Executing shell code:")
            ASCIIColors.yellow(code)
            return execute_bash(code, discussion_id, message_id)
        elif language in ["mermaid"]:
            ASCIIColors.info("Executing mermaid code:")
            ASCIIColors.yellow(code)
            return execute_mermaid(code, discussion_id, message_id)
        elif language in ["graphviz","dot"]:
            ASCIIColors.info("Executing graphviz code:")
            ASCIIColors.yellow(code)
            return execute_graphviz(code, discussion_id, message_id)
        return {"status": False, "error": "Unsupported language", "execution_time": 0}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}
    


@router.post("/open_code_folder_in_vs_code")
async def open_code_folder_in_vs_code(request: Request):
    """
    Opens code folder.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """

    try:
        if "discussion_id" in data:        
            data = (await request.json())
            code = data["code"]
            discussion_id = int(data.get("discussion_id","unknown_discussion"))
            message_id = int(data.get("message_id","unknown_message"))

            ASCIIColors.info("Opening folder:")
            # Create a temporary file.
            root_folder = lollmsElfServer.lollms_paths.personal_outputs_path/"discussions"/f"d_{discussion_id}"
            root_folder.mkdir(parents=True,exist_ok=True)
            tmp_file = root_folder/f"ai_code_{message_id}.py"
            with open(tmp_file,"w") as f:
                f.write(code)
            
            os.system('code ' + str(root_folder))
        elif "folder_path" in data:
            ASCIIColors.info("Opening folder:")
            # Create a temporary file.
            root_folder = data["folder_path"]
            root_folder.mkdir(parents=True,exist_ok=True)
            os.system('code ' + str(root_folder))

        return {"status": True, "execution_time": 0}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}
    
@router.post("/open_file")
async def open_file(request: Request):
    """
    Opens code in vs code.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """

    try:
        data = (await request.json())
        
        # Validate the 'path' parameter
        path = data.get('path')
        if not validate_file_path(path):
            return {"status":False,"error":"Invalid file path"}
        
        # Sanitize the 'path' parameter
        path = os.path.realpath(path)
        
        # Use parameterized queries to pass the file path as a parameter
        os.system(["start", path])
        
        return {"status": True, "execution_time": 0}
    
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}


@router.post("/open_code_in_vs_code")
async def open_code_in_vs_code(request: Request):
    """
    Opens code in vs code.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """

    try:
        data = (await request.json())
        discussion_id = int(data.get("discussion_id","unknown_discussion"))
        message_id = int(data.get("message_id",""))
        code = data["code"]

        ASCIIColors.info("Opening folder:")
        # Create a temporary file.
        root_folder = Path(os.path.realpath(lollmsElfServer.lollms_paths.personal_outputs_path/"discussions"/f"d_{discussion_id}"/f"{message_id}.py"))
        root_folder.mkdir(parents=True,exist_ok=True)
        tmp_file = root_folder/f"ai_code_{message_id}.py"
        with open(tmp_file,"w") as f:
            f.write(code)
        os.system('code ' + str(root_folder))
        return {"status": True, "execution_time": 0}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}
    

@router.post("/open_code_folder")
async def open_code_folder(request: Request):
    """
    Opens code folder.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """

    try:
        data = (await request.json())
        if "discussion_id" in data:
            discussion_id = int(data.get("discussion_id", "unknown_discussion"))

            ASCIIColors.info("Opening folder:")
            # Create a temporary file.
            root_folder = lollmsElfServer.lollms_paths.personal_outputs_path / "discussions" / f"d_{discussion_id}"
            root_folder.mkdir(parents=True, exist_ok=True)
            if platform.system() == 'Windows':
                os.startfile(str(root_folder))
            elif platform.system() == 'Linux':
                os.system('xdg-open ' + str(root_folder))
            elif platform.system() == 'Darwin':
                os.system('open ' + str(root_folder))
            return {"status": True, "execution_time": 0}
        elif "folder_path" in data:
            folder_path = os.path.realpath(data["folder_path"])
            # Verify that this is a file and not an executable
            root_folder = Path(folder_path)
            is_valid_folder_path = root_folder.is_dir()

            if not is_valid_folder_path:
                return {"status":False, "error":"Invalid folder path"}

            ASCIIColors.info("Opening folder:")
            # Create a temporary file.
            root_folder.mkdir(parents=True, exist_ok=True)
            if platform.system() == 'Windows':
                os.startfile(str(root_folder))
            elif platform.system() == 'Linux':
                os.system('xdg-open ' + str(root_folder))
            elif platform.system() == 'Darwin':
                os.system('open ' + str(root_folder))
            return {"status": True, "execution_time": 0}

    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status": False, "error": str(ex)}
    

@router.get("/start_recording")
def start_recording():
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
    lollmsElfServer.info("Stopping audio capture")
    text = lollmsElfServer.audio_cap.stop_recording()
    return text

