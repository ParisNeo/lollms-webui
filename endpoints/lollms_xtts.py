"""
project: lollms_webui
file: lollms_xtts.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes allow users to 

"""
from fastapi import APIRouter, Request
from lollms_webui import LOLLMSWebUI
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from lollms.types import MSG_TYPE
from lollms.main_config import BaseConfig
from lollms.utilities import detect_antiprompt, remove_text_from_string, trace_exception, find_first_available_file_index, add_period
from pathlib import Path
from ascii_colors import ASCIIColors
import os
import platform

# ----------------------- Defining router and main class ------------------------------

router = APIRouter()
lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()


# ----------------------- voice ------------------------------

@router.get("/set_voice")
def list_voices():
    ASCIIColors.yellow("Listing voices")
    voices=["main_voice"]
    voices_dir:Path=lollmsElfServer.lollms_paths.custom_voices_path
    voices += [v.stem for v in voices_dir.iterdir() if v.suffix==".wav"]
    return {"voices":voices}

@router.post("/set_voice")
async def set_voice(request: Request):
    """
    Executes Python code and returns the output.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """

    try:
        data = (await request.json())
        lollmsElfServer.config.current_voice=data["voice"]
        if lollmsElfServer.config.auto_save:
            lollmsElfServer.config.save_config()
        return {"status":True}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}

@router.post("/text2Audio")
async def text2Audio(request: Request):
    """
    Executes Python code and returns the output.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """

    try:
        data = (await request.json())
        # Get the JSON data from the POST request.
        try:
            from lollms.audio_gen_modules.lollms_xtts import LollmsXTTS
            if lollmsElfServer.tts is None:
                lollmsElfServer.tts = LollmsXTTS(lollmsElfServer, voice_samples_path=Path(__file__).parent/"voices")
        except:
            return {"url": None}
            
        data = request.get_json()
        voice=data.get("voice",lollmsElfServer.config.current_voice)
        index = find_first_available_file_index(lollmsElfServer.tts.output_folder, "voice_sample_",".wav")
        output_fn=data.get("fn",f"voice_sample_{index}.wav")
        if voice is None:
            voice = "main_voice"
        lollmsElfServer.info("Starting to build voice")
        try:
            from lollms.audio_gen_modules.lollms_xtts import LollmsXTTS
            if lollmsElfServer.tts is None:
                lollmsElfServer.tts = LollmsXTTS(lollmsElfServer, voice_samples_path=Path(__file__).parent/"voices")
            language = lollmsElfServer.config.current_language# convert_language_name()
            if voice!="main_voice":
                voices_folder = lollmsElfServer.lollms_paths.custom_voices_path
            else:
                voices_folder = Path(__file__).parent/"voices"
            lollmsElfServer.tts.set_speaker_folder(voices_folder)
            url = f"audio/{output_fn}"
            preprocessed_text= add_period(data['text'])

            lollmsElfServer.tts.tts_to_file(preprocessed_text, f"{voice}.wav", f"{output_fn}", language=language)
            lollmsElfServer.info("Voice file ready")
            return {"url": url}
        except:
            return {"url": None}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}