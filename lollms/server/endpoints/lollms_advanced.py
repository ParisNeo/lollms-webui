"""
project: lollms_advanced
file: lollms_advanced.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide access to advanced functionalities of lollms. These routes allow users to do advanced stuff like executing code.

"""

import io
import os
import platform
import re
import shutil
import string
import subprocess
from pathlib import Path
from typing import Optional

import tqdm
from ascii_colors import ASCIIColors
from fastapi import (APIRouter, FastAPI, File, HTTPException, Query, Request,
                     UploadFile)
from fastapi.responses import FileResponse, StreamingResponse
from lollms.client_session import Client
from lollms.databases.discussions_database import DiscussionsDB
from lollms.main_config import BaseConfig
from lollms.security import (check_access, forbid_remote_access, sanitize_path,
                             sanitize_svg)
from lollms.types import MSG_OPERATION_TYPE
from lollms.utilities import (add_period, detect_antiprompt,
                              remove_text_from_string, show_yes_no_dialog,
                              trace_exception)
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse

from lollms_webui import LOLLMSWebUI


def validate_file_path(path):
    try:
        sanitized_path = sanitize_path(path, allow_absolute_path=False)
        return sanitized_path is not None
    except Exception as e:
        print(f"Path validation error: {str(e)}")
        return False


import os
import shutil
import tempfile

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from utilities.execution_engines.graphviz_execution_engine import \
    execute_graphviz
from utilities.execution_engines.html_execution_engine import execute_html
from utilities.execution_engines.javascript_execution_engine import \
    execute_javascript
from utilities.execution_engines.latex_execution_engine import execute_latex
from utilities.execution_engines.lilypond_execution_engine import \
    execute_lilypond
from utilities.execution_engines.mermaid_execution_engine import \
    execute_mermaid
from utilities.execution_engines.python_execution_engine import execute_python
from utilities.execution_engines.shell_execution_engine import execute_bash
from utilities.execution_engines.svg_execution_engine import execute_svg

# ----------------------- Defining router and main class ------------------------------

router = APIRouter()
lollmsElfServer: LOLLMSWebUI = LOLLMSWebUI.get_instance()


class Identification(BaseModel):
    client_id: str


class CodeRequest(BaseModel):
    client_id: str = Field(...)
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
        return {
            "status": False,
            "error": "Code execution is blocked when in headless mode for obvious security reasons!",
        }

    forbid_remote_access(
        lollmsElfServer,
        "Code execution is blocked when the server is exposed outside for very obvious reasons!",
    )
    if not lollmsElfServer.config.turn_on_code_execution:
        return {
            "status": False,
            "error": "Code execution is blocked by the configuration!",
        }

    if lollmsElfServer.config.turn_on_code_validation:
        if not show_yes_no_dialog(
            "Validation", "Do you validate the execution of the code?"
        ):
            return {"status": False, "error": "User refused the execution!"}

    try:
        code = request.code
        discussion_id = request.discussion_id
        message_id = request.message_id
        language = request.language

        if language == "function":
            ASCIIColors.info("Executing function call:")
            ASCIIColors.yellow(code)
            try:
                out = lollmsElfServer.execute_function(code, client)
                return (
                    out
                    if type(out) == str
                    else (
                        out[0] if type(out) is tuple and type(out[0]) == str else "Done"
                    )
                )
            except Exception as ex:
                trace_exception(ex)
                return ex
        if language == "python":
            ASCIIColors.info("Executing python code:")
            ASCIIColors.yellow(code)
            return execute_python(code, client, message_id)
        if language == "svg":
            ASCIIColors.info("Executing svg code:")
            ASCIIColors.yellow(code)
            return execute_svg(sanitize_svg(code), client, message_id)
        if language == "lilypond":
            ASCIIColors.info("Executing svg code:")
            ASCIIColors.yellow(code)
            return execute_lilypond(code, client, message_id)

        if language == "javascript":
            ASCIIColors.info("Executing javascript code:")
            ASCIIColors.yellow(code)
            return execute_javascript(code, client, message_id)
        if language in ["html", "html5", "svg"]:
            ASCIIColors.info("Executing javascript code:")
            ASCIIColors.yellow(code)
            return execute_html(code, client, message_id)

        elif language == "latex":
            ASCIIColors.info("Executing latex code:")
            ASCIIColors.yellow(code)
            return execute_latex(code, client, message_id)
        elif language in ["bash", "shell", "cmd", "powershell"]:
            ASCIIColors.info("Executing shell code:")
            ASCIIColors.yellow(code)
            return execute_bash(code, client, message_id)
        elif language in ["mermaid"]:
            ASCIIColors.info("Executing mermaid code:")
            ASCIIColors.yellow(code)
            return execute_mermaid(code, client, message_id)
        elif language in ["graphviz", "dot"]:
            ASCIIColors.info("Executing graphviz code:")
            ASCIIColors.yellow(code)
            return execute_graphviz(code, client, message_id)
        return {"status": False, "error": "Unsupported language", "execution_time": 0}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status": False, "error": str(ex)}


@router.post("/execute_code_in_new_tab")
async def execute_code_in_new_tab(request: CodeRequest):
    """
    Executes Python code and returns the output.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """
    client = check_access(lollmsElfServer, request.client_id)
    if lollmsElfServer.config.headless_server_mode:
        return {
            "status": False,
            "error": "Code execution is blocked when in headless mode for obvious security reasons!",
        }

    forbid_remote_access(
        lollmsElfServer,
        "Code execution is blocked when the server is exposed outside for very obvious reasons!",
    )
    if not lollmsElfServer.config.turn_on_code_execution:
        return {
            "status": False,
            "error": "Code execution is blocked by the configuration!",
        }

    if lollmsElfServer.config.turn_on_code_validation:
        if not show_yes_no_dialog(
            "Validation", "Do you validate the execution of the code?"
        ):
            return {"status": False, "error": "User refused the execution!"}

    try:
        code = request.code
        discussion_id = request.discussion_id
        message_id = request.message_id
        language = request.language

        if language == "python":
            ASCIIColors.info("Executing python code:")
            ASCIIColors.yellow(code)
            return execute_python(code, client, message_id, True)
        if language == "javascript":
            ASCIIColors.info("Executing javascript code:")
            ASCIIColors.yellow(code)
            return execute_javascript(code, client, message_id, True)
        if language in ["html", "html5", "svg"]:
            ASCIIColors.info("Executing javascript code:")
            ASCIIColors.yellow(code)
            return execute_html(code, client, message_id, True)

        elif language == "latex":
            ASCIIColors.info("Executing latex code:")
            ASCIIColors.yellow(code)
            return execute_latex(code, client, message_id, True)
        elif language in ["bash", "shell", "cmd", "powershell"]:
            ASCIIColors.info("Executing shell code:")
            ASCIIColors.yellow(code)
            return execute_bash(code, client)
        elif language in ["mermaid"]:
            ASCIIColors.info("Executing mermaid code:")
            ASCIIColors.yellow(code)
            return execute_mermaid(code, client, message_id, True)
        elif language in ["graphviz", "dot"]:
            ASCIIColors.info("Executing graphviz code:")
            ASCIIColors.yellow(code)
            return execute_graphviz(code, client, message_id, True)
        return {"status": False, "error": "Unsupported language", "execution_time": 0}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status": False, "error": str(ex)}


class FilePath(BaseModel):
    client_id: str
    path: Optional[str] = Field(None, max_length=500)


@router.post("/open_file")
async def open_file(file_path: FilePath):
    """
    Opens code in vs code.

    :param file_path: The file path object.
    :return: A JSON response with the status of the operation.
    """
    check_access(lollmsElfServer, client_id=file_path.client_id)

    if lollmsElfServer.config.headless_server_mode:
        return {
            "status": False,
            "error": "Open file is blocked when in headless mode for obvious security reasons!",
        }

    if (
        lollmsElfServer.config.host != "localhost"
        and lollmsElfServer.config.host != "127.0.0.1"
    ):
        return {
            "status": False,
            "error": "Open file is blocked when the server is exposed outside for very obvious reasons!",
        }

    if lollmsElfServer.config.turn_on_open_file_validation:
        if not show_yes_no_dialog(
            "Validation", "Do you validate the opening of a file?"
        ):
            return {"status": False, "error": "User refused the opeining file!"}

    forbid_remote_access(lollmsElfServer)
    # Validate the 'path' parameter
    path = sanitize_path(file_path.path, allow_absolute_path=True)

    try:
        if Path(path).exists():
            # Use subprocess.Popen to safely open the file
            ASCIIColors.yellow(f"Starting file : {path}")
            if os.name == "nt":  # if the operating system is Windows
                subprocess.Popen(f"start {path}", shell=True)
            else:  # for other operating systems
                subprocess.Popen([path], shell=True)

        return {"status": True, "execution_time": 0}

    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status": False, "error": str(ex)}


@router.post("/open_folder")
async def open_folder(file_path: FilePath):
    """
    Opens a folder

    :param file_path: The file path object.
    :return: A JSON response with the status of the operation.
    """
    forbid_remote_access(
        lollmsElfServer,
        "Open file is blocked when the server is exposed outside for very obvious reasons!",
    )

    if lollmsElfServer.config.headless_server_mode:
        return {
            "status": False,
            "error": "Open file is blocked when in headless mode for obvious security reasons!",
        }

    if lollmsElfServer.config.turn_on_open_file_validation:
        if not show_yes_no_dialog(
            "Validation", "Do you validate the opening of a folder?"
        ):
            return {"status": False, "error": "User refused the opening folder!"}

    forbid_remote_access(lollmsElfServer)
    try:
        # Validate the 'path' parameter
        path = sanitize_path(file_path.path, allow_absolute_path=True)
        ASCIIColors.yellow(f"Opening folder : {path}")
        if Path(path).exists():
            # Use subprocess.Popen to safely open the file
            if platform.system() == "Windows":
                path = path.replace("/", "\\")
                subprocess.Popen(f'explorer "{path}"')
            elif platform.system() == "Linux":
                subprocess.run(["xdg-open", str(path)], check=True, shell=True)
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(path)], check=True, shell=True)

        return {"status": True, "execution_time": 0}

    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status": False, "error": str(ex)}


class OpenCodeFolderInVsCodeRequestModel(BaseModel):
    client_id: str = Field(...)
    discussion_id: Optional[int] = Field(None, gt=0)
    message_id: Optional[int] = Field(None, gt=0)
    code: Optional[str]


@router.post("/open_discussion_folder_in_vs_code")
async def open_discussion_folder_in_vs_code(
    request: OpenCodeFolderInVsCodeRequestModel,
):

    client = check_access(lollmsElfServer, request.client_id)

    if lollmsElfServer.config.headless_server_mode:
        return {
            "status": False,
            "error": "Open code folder in vscode is blocked when in headless mode for obvious security reasons!",
        }

    if (
        lollmsElfServer.config.host != "localhost"
        and lollmsElfServer.config.host != "127.0.0.1"
    ):
        return {
            "status": False,
            "error": "Open code folder in vscode is blocked when the server is exposed outside for very obvious reasons!",
        }

    if lollmsElfServer.config.turn_on_open_file_validation:
        if not show_yes_no_dialog(
            "Validation", "Do you validate the opening of folder in vscode?"
        ):
            return {"status": False, "error": "User refused the execution!"}

    try:
        if request.discussion_id:
            ASCIIColors.info("Opening folder:")
            root_folder = client.discussion.discussion_folder
            root_folder.mkdir(parents=True, exist_ok=True)
            tmp_file = root_folder / f"ai_code_{request.message_id}.py"
            with open(tmp_file, "w", encoding="utf-8", errors="ignore") as f:
                f.write(request.code)

            if os.path.isdir(root_folder):
                path = '"' + str(root_folder) + '"'.replace("\\", "/")
                subprocess.run(["code", "-n", path], shell=True)

        return {"status": True, "execution_time": 0}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(str(ex))
        return {"status": False, "error": "An error occurred during processing."}


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
        return {
            "status": False,
            "error": "Open code in vs code is blocked when in headless mode for obvious security reasons!",
        }

    if (
        lollmsElfServer.config.host != "localhost"
        and lollmsElfServer.config.host != "127.0.0.1"
    ):
        return {
            "status": False,
            "error": "Open code in vs code is blocked when the server is exposed outside for very obvious reasons!",
        }

    if lollmsElfServer.config.turn_on_open_file_validation:
        if not show_yes_no_dialog(
            "Validation", "Do you validate the opening of a code in vscode?"
        ):
            return {"status": False, "error": "User refused the opeining file!"}

    try:
        discussion_id = vs_code_data.discussion_id
        message_id = vs_code_data.message_id
        code = vs_code_data.code

        ASCIIColors.info("Opening folder:")
        # Create a temporary file.
        root_folder = client.discussion.discussion_folder

        root_folder.mkdir(parents=True, exist_ok=True)
        tmp_file = root_folder / f"ai_code_{message_id}.py"
        with open(tmp_file, "w", encoding="utf-8", errors="ignore") as f:
            f.write(code)

        # Use subprocess.Popen to safely open the file
        os.system(f'code -n "{tmp_file}"')

        return {"status": True, "execution_time": 0}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status": False, "error": str(ex)}
class ClientAuthentication(BaseModel):
    client_id: str = Field(...)

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
        return {
            "status": False,
            "error": "Open code folder is blocked when in headless mode for obvious security reasons!",
        }

    if (
        lollmsElfServer.config.host != "localhost"
        and lollmsElfServer.config.host != "127.0.0.1"
    ):
        return {
            "status": False,
            "error": "Open code folder is blocked when the server is exposed outside for very obvious reasons!",
        }

    if lollmsElfServer.config.turn_on_open_file_validation:
        if not show_yes_no_dialog(
            "Validation", "Do you validate the opening of a folder?"
        ):
            return {"status": False, "error": "User refused the opeining folder!"}

    try:
        ASCIIColors.info("Opening folder:")
        # Create a temporary file.
        root_folder = client.discussion.discussion_folder
        root_folder.mkdir(parents=True, exist_ok=True)
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer "{root_folder}"')
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", str(root_folder)], check=True)
        elif platform.system() == "Darwin":
            subprocess.run(["open", str(root_folder)], check=True)
        return {"status": True, "execution_time": 0}

    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {
            "status": False,
            "error": "An error occurred while processing the request",
        }



@router.post("/open_custom_function_calls_folder")
async def open_custom_function_calls_folder(request: ClientAuthentication):
    """
    Opens custom function calls folder.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """
    client = check_access(lollmsElfServer, request.client_id)

    if lollmsElfServer.config.headless_server_mode:
        return {
            "status": False,
            "error": "Open code folder is blocked when in headless mode for obvious security reasons!",
        }

    if (
        lollmsElfServer.config.host != "localhost"
        and lollmsElfServer.config.host != "127.0.0.1"
    ):
        return {
            "status": False,
            "error": "Open code folder is blocked when the server is exposed outside for very obvious reasons!",
        }

    if lollmsElfServer.config.turn_on_open_file_validation:
        if not show_yes_no_dialog(
            "Validation", "Do you validate the opening of a folder?"
        ):
            return {"status": False, "error": "User refused the opeining folder!"}

    try:
        ASCIIColors.info("Opening folder:")
        # Create a temporary file.
        root_folder = lollmsElfServer.lollms_paths.custom_function_calls_path
        root_folder.mkdir(parents=True, exist_ok=True)
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer "{root_folder}"')
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", str(root_folder)], check=True)
        elif platform.system() == "Darwin":
            subprocess.run(["open", str(root_folder)], check=True)
        return {"status": True, "execution_time": 0}

    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {
            "status": False,
            "error": "An error occurred while processing the request",
        }



class PersonalityFolderRequest(BaseModel):
    client_id: str = Field(...)
    category: str = Field(...)
    name: str = Field(...)

@router.post("/open_personality_folder")
async def open_personality_folder(request: PersonalityFolderRequest):
    """
    Opens code folder.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """
    client = check_access(lollmsElfServer, request.client_id)
    request.name = sanitize_path(request.name)
    request.category = sanitize_path(request.category)
    if request.category == "custom_personalities":
        folder = lollmsElfServer.lollms_paths.custom_personalities_path/request.name
    else:
        folder = lollmsElfServer.lollms_paths.personalities_zoo_path/request.category/request.name

    if lollmsElfServer.config.headless_server_mode:
        return {
            "status": False,
            "error": "Open code folder is blocked when in headless mode for obvious security reasons!",
        }

    if (
        lollmsElfServer.config.host != "localhost"
        and lollmsElfServer.config.host != "127.0.0.1"
    ):
        return {
            "status": False,
            "error": "Open code folder is blocked when the server is exposed outside for very obvious reasons!",
        }

    if lollmsElfServer.config.turn_on_open_file_validation:
        if not show_yes_no_dialog(
            "Validation", "Do you validate the opening of a folder?"
        ):
            return {"status": False, "error": "User refused the opeining folder!"}

    try:
        ASCIIColors.info("Opening folder:")
        # Create a temporary file.
        if request.category!="custom_personalities":
            root_folder = (
                lollmsElfServer.lollms_paths.custom_personalities_path / request.name
            )
        else:
            personality_folder = request.category +"/"+ request.name
            root_folder = (
                lollmsElfServer.lollms_paths.personalities_zoo_path / personality_folder
            )
        root_folder.mkdir(parents=True, exist_ok=True)
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer "{root_folder}"')
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", str(root_folder)], check=True)
        elif platform.system() == "Darwin":
            subprocess.run(["open", str(root_folder)], check=True)
        return {"status": True, "execution_time": 0}

    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {
            "status": False,
            "error": "An error occurred while processing the request",
        }


@router.get("/is_rt_on")
def is_rt_on():
    return {"status": lollmsElfServer.rt_com is not None}


@router.post("/start_recording")
def start_recording(data: Identification):
    client = check_access(lollmsElfServer, data.client_id)

    if lollmsElfServer.config.headless_server_mode:
        return {
            "status": False,
            "error": "Start recording is blocked when in headless mode for obvious security reasons!",
        }

    if (
        lollmsElfServer.config.host != "localhost"
        and lollmsElfServer.config.host != "127.0.0.1"
    ):
        return {
            "status": False,
            "error": "Start recording is blocked when the server is exposed outside for very obvious reasons!",
        }

    lollmsElfServer.info("Starting audio capture")
    if not lollmsElfServer.tts or not lollmsElfServer.stt:
        lollmsElfServer.InfoMessage(
            "TTS or STT are not configured.\nPlease go to settings and configure them first"
        )
        return {"status": False, "error": "TTS or STT not configured"}

    if not lollmsElfServer.tts.ready or not lollmsElfServer.stt.ready:
        lollmsElfServer.InfoMessage("TTS is not ready yet.\nPlease wait")
        return {"status": False, "error": "TTS not ready"}

    lollmsElfServer.info("Starting audio capture")
    try:
        from lollms.media import AudioNinja

        lollmsElfServer.rec_output_folder = (
            lollmsElfServer.lollms_paths.personal_outputs_path / "audio_rec"
        )
        lollmsElfServer.rec_output_folder.mkdir(exist_ok=True, parents=True)
        lollmsElfServer.summoned = False
        lollmsElfServer.audioNinja = AudioNinja(
            lollmsElfServer, logs_folder=lollmsElfServer.rec_output_folder
        )
        lollmsElfServer.audioNinja.start_recording()
    except:
        lollmsElfServer.InfoMessage(
            "Couldn't load media library.\nYou will not be able to perform any of the media linked operations. please verify the logs and install any required installations"
        )


@router.post("/stop_recording")
def stop_recording(data: Identification):
    client = check_access(lollmsElfServer, data.client_id)

    if lollmsElfServer.config.headless_server_mode:
        return {
            "status": False,
            "error": "Stop recording is blocked when in headless mode for obvious security reasons!",
        }

    if (
        lollmsElfServer.config.host != "localhost"
        and lollmsElfServer.config.host != "127.0.0.1"
    ):
        return {
            "status": False,
            "error": "Stop recording is blocked when the server is exposed outside for very obvious reasons!",
        }

    lollmsElfServer.info("Stopping audio capture")
    fn = lollmsElfServer.audioNinja.stop_recording()
    lollmsElfServer.audioNinja = None
    if lollmsElfServer.stt and fn:
        text = lollmsElfServer.stt.transcribe(fn)
        return text
    else:
        return ""


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        # Copy the contents of the uploaded file to the temporary file
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name

    try:
        if hasattr(lollmsElfServer, "stt") and lollmsElfServer.stt:
            text = lollmsElfServer.stt.transcribe(temp_file_path)
            return JSONResponse(content={"transcription": text})
        else:
            return JSONResponse(
                content={"error": "STT service not available"}, status_code=503
            )
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


class TTSRequest(BaseModel):
    text: str
    speaker: str = None
    language: str = "en"


@router.post("/tts/file")
async def text_to_speech_file(request: TTSRequest):
    try:
        file_path = lollmsElfServer.tts.tts_file(
            text=request.text,
            file_name_or_path=lollmsElfServer.lollms_paths.personal_outputs_path
            / "output.wav",
            speaker=request.speaker,
            language=request.language,
        )
        return FileResponse(file_path, media_type="audio/wav", filename="speech.wav")
    except Exception as e:
        trace_exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tts/stream")
async def text_to_speech_stream(request: TTSRequest):
    try:
        audio_data = lollmsElfServer.tts.tts_audio(
            text=request.text, speaker=request.speaker, language=request.language
        )
        return StreamingResponse(io.BytesIO(audio_data), media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tts/voices")
async def get_available_voices():
    try:
        voices = lollmsElfServer.tts.get_voices()
        return JSONResponse(content={"voices": voices})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)




class PersonalFolderRequest(BaseModel):
    client_id: str = Field(...)
    folder:str = Field(...)

@router.post("/open_personal_folder")
async def open_personality_folder(request: PersonalFolderRequest):
    """
    Opens a personal data folder.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """
    client = check_access(lollmsElfServer, request.client_id)
    if(request.folder=="custom-personalities"):
        root_folder =  lollmsElfServer.lollms_paths.custom_personalities_path
    elif(request.folder=="custom-function-calls"):
        root_folder =  lollmsElfServer.lollms_paths.custom_function_calls_path
    elif(request.folder=="configurations"):
        root_folder =  lollmsElfServer.lollms_paths.personal_configuration_path
    elif(request.folder=="ai-outputs"):
        root_folder =  lollmsElfServer.lollms_paths.personal_outputs_path
    elif(request.folder=="discussions"):
        root_folder =  lollmsElfServer.lollms_paths.personal_discussions_path
    else:
        return JSONResponse(content={"error": "Unknown folder"})
        

    if platform.system() == "Windows":
        subprocess.Popen(f'explorer "{root_folder}"')
    elif platform.system() == "Linux":
        subprocess.run(["xdg-open", str(root_folder)], check=True)
    elif platform.system() == "Darwin":
        subprocess.run(["open", str(root_folder)], check=True)
    return {"status": True, "execution_time": 0}

