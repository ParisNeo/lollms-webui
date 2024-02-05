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

from utilities.execution_engines.python_execution_engine import execute_python
from utilities.execution_engines.latex_execution_engine import execute_latex
from utilities.execution_engines.shell_execution_engine import execute_bash

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

    try:
        data = (await request.json())
        code = data["code"]
        discussion_id = data.get("discussion_id","unknown_discussion")
        message_id = data.get("message_id","unknown_message")
        language = data.get("language","python")
        

        ASCIIColors.info("Executing python code:")
        ASCIIColors.yellow(code)

        if language=="python":
            return execute_python(code, discussion_id, message_id)
        elif language=="latex":
            return execute_latex(code, discussion_id, message_id)
        elif language in ["bash","shell","cmd","powershell"]:
            return execute_bash(code, discussion_id, message_id)
        return {"output": "Unsupported language", "execution_time": 0}
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
        discussion_id = data.get("discussion_id","unknown_discussion")

        ASCIIColors.info("Opening folder:")
        # Create a temporary file.
        root_folder = lollmsElfServer.lollms_paths.personal_outputs_path/"discussions"/f"d_{discussion_id}"
        root_folder.mkdir(parents=True,exist_ok=True)
        if platform.system() == 'Windows':
            os.startfile(str(root_folder))
        elif platform.system() == 'Linux':
            os.system('xdg-open ' + str(root_folder))
        elif platform.system() == 'Darwin':
            os.system('open ' + str(root_folder))
        return {"output": "OK", "execution_time": 0}
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
            discussion_id = data.get("discussion_id","unknown_discussion")
            message_id = data.get("message_id","unknown_message")
            language = data.get("language","python")

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

        return {"output": "OK", "execution_time": 0}
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
        path = data.get('path')
        os.system("start "+path)
        return {"output": "OK", "execution_time": 0}
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
        discussion_id = data.get("discussion_id","unknown_discussion")
        message_id = data.get("message_id","")
        code = data["code"]
        discussion_id = data.get("discussion_id","unknown_discussion")
        message_id = data.get("message_id","unknown_message")
        language = data.get("language","python")

        ASCIIColors.info("Opening folder:")
        # Create a temporary file.
        root_folder = lollmsElfServer.lollms_paths.personal_outputs_path/"discussions"/f"d_{discussion_id}"/f"{message_id}.py"
        root_folder.mkdir(parents=True,exist_ok=True)
        tmp_file = root_folder/f"ai_code_{message_id}.py"
        with open(tmp_file,"w") as f:
            f.write(code)
        os.system('code ' + str(root_folder))
        return {"output": "OK", "execution_time": 0}
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
            discussion_id = data.get("discussion_id","unknown_discussion")

            ASCIIColors.info("Opening folder:")
            # Create a temporary file.
            root_folder = lollmsElfServer.lollms_paths.personal_outputs_path/"discussions"/f"d_{discussion_id}"
            root_folder.mkdir(parents=True,exist_ok=True)
            if platform.system() == 'Windows':
                os.startfile(str(root_folder))
            elif platform.system() == 'Linux':
                os.system('xdg-open ' + str(root_folder))
            elif platform.system() == 'Darwin':
                os.system('open ' + str(root_folder))
            return {"output": "OK", "execution_time": 0}
        elif "folder_path" in data:
            ASCIIColors.info("Opening folder:")
            # Create a temporary file.
            root_folder = data["folder_path"]
            root_folder.mkdir(parents=True,exist_ok=True)
            if platform.system() == 'Windows':
                os.startfile(str(root_folder))
            elif platform.system() == 'Linux':
                os.system('xdg-open ' + str(root_folder))
            elif platform.system() == 'Darwin':
                os.system('open ' + str(root_folder))
            return {"output": "OK", "execution_time": 0}

    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}
    

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
