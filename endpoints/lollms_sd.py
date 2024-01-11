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
from lollms.utilities import detect_antiprompt, remove_text_from_string, trace_exception, find_first_available_file_index, add_period, PackageManager
from pathlib import Path
from ascii_colors import ASCIIColors
import os
import platform

# ----------------------- Defining router and main class ------------------------------

router = APIRouter()
lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()


# ----------------------- voice ------------------------------

@router.get("/install_xtts")
def install_sd():
    try:
        lollmsElfServer.ShowBlockingMessage("Installing SD api server\nPlease stand by")
        from lollms.services.sd.lollms_sd import install_sd
        install_sd()
        lollmsElfServer.HideBlockingMessage()
        return {"status":True}
    except Exception as ex:
        lollmsElfServer.HideBlockingMessage()
        return {"status":False, 'error':str(ex)}