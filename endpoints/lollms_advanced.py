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
from lollms.utilities import detect_antiprompt, remove_text_from_string, trace_exception, show_yes_no_dialog, add_period
from lollms.security import sanitize_path, forbid_remote_access, check_access, sanitize_svg
from ascii_colors import ASCIIColors
from lollms.databases.discussions_database import DiscussionsDB
from lollms.client_session import Client
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

def validate_file_path(path):
    try:
        sanitized_path = sanitize_path(path, allow_absolute_path=False)
        return sanitized_path is not None
    except Exception as e:
        print(f"Path validation error: {str(e)}")
        return False

from utilities.execution_engines.python_execution_engine import execute_python
from utilities.execution_engines.latex_execution_engine import execute_latex
from utilities.execution_engines.shell_execution_engine import execute_bash
from utilities.execution_engines.javascript_execution_engine import execute_javascript
from utilities.execution_engines.html_execution_engine import execute_html

from utilities.execution_engines.mermaid_execution_engine import execute_mermaid
from utilities.execution_engines.graphviz_execution_engine import execute_graphviz
from utilities.execution_engines.svg_execution_engine import execute_svg




# ----------------------- Defining router and main class ------------------------------

router = APIRouter()
lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()
class Identification(BaseModel):
    client_id:str

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
    client = check_access(lollmsElfServer, request.client_id)
    if lollmsElfServer.config.headless_server_mode:
        return {"status":False,"error":"Code execution is blocked when in headless mode for obvious security reasons!"}

    forbid_remote_access(lollmsElfServer, "Code execution is blocked when the server is exposed outside for very obvious reasons!")
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

        if language=="function":
            ASCIIColors.info("Executing function call:")
            ASCIIColors.yellow(code)
            lollmsElfServer.personality.execute_function()
            return execute_python(code, client, message_id)

        if language=="python":
            ASCIIColors.info("Executing python code:")
            ASCIIColors.yellow(code)
            return execute_python(code, client, message_id)
        if language=="svg":
            ASCIIColors.info("Executing svg code:")
            ASCIIColors.yellow(code)
            return execute_svg(sanitize_svg(code), client, message_id)
        if language=="javascript":
            ASCIIColors.info("Executing javascript code:")
            ASCIIColors.yellow(code)
            return execute_javascript(code, client, message_id)
        if language in ["html","html5","svg"]:
            ASCIIColors.info("Executing javascript code:")
            ASCIIColors.yellow(code)
            return execute_html(code, client, message_id)

        elif language=="latex":
            ASCIIColors.info("Executing latex code:")
            ASCIIColors.yellow(code)
            return execute_latex(code, client, message_id)
        elif language in ["bash","shell","cmd","powershell"]:
            ASCIIColors.info("Executing shell code:")
            ASCIIColors.yellow(code)
            return execute_bash(code, client, message_id)
        elif language in ["mermaid"]:
            ASCIIColors.info("Executing mermaid code:")
            ASCIIColors.yellow(code)
            return execute_mermaid(code, client, message_id)
        elif language in ["graphviz","dot"]:
            ASCIIColors.info("Executing graphviz code:")
            ASCIIColors.yellow(code)
            return execute_graphviz(code, client, message_id)
        return {"status": False, "error": "Unsupported language", "execution_time": 0}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}
    
@router.post("/execute_code_in_new_tab")
async def execute_code_in_new_tab(request: CodeRequest):
    """
    Executes Python code and returns the output.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """
    client = check_access(lollmsElfServer, request.client_id)
    if lollmsElfServer.config.headless_server_mode:
        return {"status":False,"error":"Code execution is blocked when in headless mode for obvious security reasons!"}

    forbid_remote_access(lollmsElfServer, "Code execution is blocked when the server is exposed outside for very obvious reasons!")
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
            return execute_python(code, client, message_id, True)
        if language=="javascript":
            ASCIIColors.info("Executing javascript code:")
            ASCIIColors.yellow(code)
            return execute_javascript(code, client, message_id, True)
        if language in ["html","html5","svg"]:
            ASCIIColors.info("Executing javascript code:")
            ASCIIColors.yellow(code)
            return execute_html(code, client, message_id, True)

        elif language=="latex":
            ASCIIColors.info("Executing latex code:")
            ASCIIColors.yellow(code)
            return execute_latex(code, client, message_id, True)
        elif language in ["bash","shell","cmd","powershell"]:
            ASCIIColors.info("Executing shell code:")
            ASCIIColors.yellow(code)
            return execute_bash(code, client)
        elif language in ["mermaid"]:
            ASCIIColors.info("Executing mermaid code:")
            ASCIIColors.yellow(code)
            return execute_mermaid(code, client, message_id, True)
        elif language in ["graphviz","dot"]:
            ASCIIColors.info("Executing graphviz code:")
            ASCIIColors.yellow(code)
            return execute_graphviz(code, client, message_id, True)
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
    # Validate the 'path' parameter
    path = sanitize_path(file_path.path, allow_absolute_path=True)

    try:        
        if Path(path).exists():
            # Use subprocess.Popen to safely open the file
            ASCIIColors.yellow(f"Starting file : {path}")
            if os.name == "nt": # if the operating system is Windows
                subprocess.Popen(f'start {path}', shell=True)
            else: # for other operating systems
                subprocess.Popen([path], shell=True)
        
        return {"status": True, "execution_time": 0}
    
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}
    

@router.post("/open_folder")
async def open_folder(file_path: FilePath):
    """
    Opens a folder

    :param file_path: The file path object.
    :return: A JSON response with the status of the operation.
    """
    forbid_remote_access(lollmsElfServer, "Open file is blocked when the server is exposed outside for very obvious reasons!")

    if lollmsElfServer.config.headless_server_mode:
        return {"status":False,"error":"Open file is blocked when in headless mode for obvious security reasons!"}

    if lollmsElfServer.config.turn_on_open_file_validation:
        if not show_yes_no_dialog("Validation","Do you validate the opening of a folder?"):
            return {"status":False,"error":"User refused the opening folder!"}

    forbid_remote_access(lollmsElfServer)
    try:
        # Validate the 'path' parameter
        path = sanitize_path(file_path.path, allow_absolute_path=True)
        ASCIIColors.yellow(f"Opening folder : {path}")
        if Path(path).exists():
            # Use subprocess.Popen to safely open the file
            if platform.system() == 'Windows':
                subprocess.Popen(f'explorer "{path}"', shell=True)
            elif platform.system() == 'Linux':
                subprocess.run(['xdg-open', str(path)], check=True, shell=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', str(path)], check=True, shell=True)

        
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

@router.post("/open_discussion_folder_in_vs_code")
async def open_discussion_folder_in_vs_code(request: OpenCodeFolderInVsCodeRequestModel):

    client = check_access(lollmsElfServer, request.client_id)

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
    client = check_access(lollmsElfServer, vs_code_data.client_id)

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
    
class DiscussionFolderRequest(BaseModel):
    client_id: str = Field(...)
    discussion_id: int = Field(...)

@router.post("/open_discussion_folder")
async def open_discussion_folder(request: DiscussionFolderRequest):
    """
    Opens code folder.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """
    client = check_access(lollmsElfServer, request.client_id)

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

class PersonalityFolderRequest(BaseModel):
    client_id: str = Field(...)
    personality_folder: int = Field(...)

@router.post("/open_personality_folder")
async def open_personality_folder(request: PersonalityFolderRequest):
    """
    Opens code folder.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """
    client = check_access(lollmsElfServer, request.client_id)
    personality_folder = sanitize_path(request.personality_folder)

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
        root_folder = lollmsElfServer.lollms_paths.personalities_zoo_path/personality_folder
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

@router.get("/is_rt_on")
def is_rt_on():
    return {"status": lollmsElfServer.rt_com is not None}

@router.post("/start_recording")
def start_recording(data:Identification):
    client = check_access(lollmsElfServer, data.client_id)

    if lollmsElfServer.config.headless_server_mode:
        return {"status":False,"error":"Start recording is blocked when in headless mode for obvious security reasons!"}

    if lollmsElfServer.config.host!="localhost" and lollmsElfServer.config.host!="127.0.0.1":
        return {"status":False,"error":"Start recording is blocked when the server is exposed outside for very obvious reasons!"}

    lollmsElfServer.info("Starting audio capture")
    try:
        from lollms.media import RTCom
        lollmsElfServer.rec_output_folder = lollmsElfServer.lollms_paths.personal_outputs_path/"audio_rec"
        lollmsElfServer.rec_output_folder.mkdir(exist_ok=True, parents=True)
        lollmsElfServer.summoned = False
        lollmsElfServer.rt_com = RTCom(
                                                lollmsElfServer, 
                                                lollmsElfServer.sio, 
                                                lollmsElfServer.personality, 
                                                client=client,
                                                threshold=1000, 
                                                silence_duration=2, 
                                                sound_threshold_percentage=10, 
                                                gain=1.0, 
                                                rate=44100, 
                                                channels=1, 
                                                buffer_size=10, 
                                                model=lollmsElfServer.config.whisper_model,
                                                snd_input_device=lollmsElfServer.config.stt_input_device, 
                                                snd_output_device=lollmsElfServer.config.tts_output_device, 
                                                logs_folder=lollmsElfServer.rec_output_folder, 
                                                voice=None, 
                                                block_while_talking=True, 
                                                context_size=4096
                                            ) 
        lollmsElfServer.rt_com.start_recording()
    except:
        lollmsElfServer.InfoMessage("Couldn't load media library.\nYou will not be able to perform any of the media linked operations. please verify the logs and install any required installations")


@router.post("/stop_recording")
def stop_recording(data:Identification):
    client = check_access(lollmsElfServer, data.client_id)

    if lollmsElfServer.config.headless_server_mode:
        return {"status":False,"error":"Stop recording is blocked when in headless mode for obvious security reasons!"}

    if lollmsElfServer.config.host!="localhost" and lollmsElfServer.config.host!="127.0.0.1":
        return {"status":False,"error":"Stop recording is blocked when the server is exposed outside for very obvious reasons!"}

    lollmsElfServer.info("Stopping audio capture")
    text = lollmsElfServer.rt_com.stop_recording()

    # ai_text = lollmsElfServer.receive_and_generate(text, client, n_predict=lollmsElfServer.config, callback= lollmsElfServer.tasks_library.sink)
    # if lollmsElfServer.tts and lollmsElfServer.tts.ready:
    #     personality_audio:Path = lollmsElfServer.personality.personality_package_path/"audio"
    #     voice=lollmsElfServer.config.xtts_current_voice
    #     if personality_audio.exists() and len([v for v in personality_audio.iterdir()])>0:
    #         voices_folder = personality_audio
    #     elif voice!="main_voice":
    #         voices_folder = lollmsElfServer.lollms_paths.custom_voices_path
    #     else:
    #         voices_folder = Path(__file__).parent.parent.parent/"services/xtts/voices"
    #     language = lollmsElfServer.config.xtts_current_language# convert_language_name()
    #     lollmsElfServer.tts.set_speaker_folder(voices_folder)
    #     preprocessed_text= add_period(ai_text)
    #     voice_file =  [v for v in voices_folder.iterdir() if v.stem==voice and v.suffix==".wav"]

    #     lollmsElfServer.tts.tts_audio(preprocessed_text, voice_file[0].name, language=language)
    return text

