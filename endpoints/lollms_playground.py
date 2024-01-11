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
import yaml
# ----------------------- Defining router and main class ------------------------------

router = APIRouter()
lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()


# ----------------------- voice ------------------------------
@router.get("/install_ollama")
def get_presets():
    presets = []
    presets_folder = Path("__file__").parent/"presets"
    for filename in presets_folder.glob('*.yaml'):
        with open(filename, 'r', encoding='utf-8') as file:
            preset = yaml.safe_load(file)
            if preset is not None:
                presets.append(preset)
    presets_folder = lollmsElfServer.lollms_paths.personal_databases_path/"lollms_playground_presets"
    presets_folder.mkdir(exist_ok=True, parents=True)
    for filename in presets_folder.glob('*.yaml'):
        with open(filename, 'r', encoding='utf-8') as file:
            preset = yaml.safe_load(file)
            if preset is not None:
                presets.append(preset)
    return presets