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
import yaml, json
# ----------------------- Defining router and main class ------------------------------

router = APIRouter()
lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()


# ----------------------- voice ------------------------------
@router.get("/get_presets")
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

@router.post("/add_preset")
async def add_preset(request: Request):
    """
    Changes current voice

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """
    # Get the JSON data from the POST request.
    preset_data = request.get_json()
    presets_folder = lollmsElfServer.lollms_paths.personal_databases_path/"lollms_playground_presets"
    if not presets_folder.exists():
        presets_folder.mkdir(exist_ok=True, parents=True)

    fn = preset_data["name"].lower().replace(" ","_")
    filename = presets_folder/f"{fn}.yaml"
    with open(filename, 'w', encoding='utf-8') as file:
        yaml.dump(preset_data, file)
    return {"status": True}

@router.post("/del_preset")
async def del_preset(request: Request):
    """
    Saves a preset to a file.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """
    # Get the JSON data from the POST request.
    preset_data = request.get_json()    
    presets_folder = lollmsElfServer.lollms_paths.personal_databases_path/"lollms_playground_presets"
    # TODO : process
    return {"status":True}


@router.post("/save_presets")
async def save_presets(request: Request):
    """
    Saves a preset to a file.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """
    # Get the JSON data from the POST request.
    preset_data = request.get_json()    

    presets_file = lollmsElfServer.lollms_paths.personal_databases_path/"presets.json"
    # Save the JSON data to a file.
    with open(presets_file, "w") as f:
        json.dump(preset_data, f, indent=4)

    return {"status":True,"message":"Preset saved successfully!"}