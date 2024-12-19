"""
project: lollms_webui
file: lollms_xtts.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes allow users to 

"""

import json
import os
import platform
from pathlib import Path

import yaml
from ascii_colors import ASCIIColors
from fastapi import APIRouter, HTTPException, Request
from lollms.main_config import BaseConfig
from lollms.security import (check_access, forbid_remote_access,
                             sanitize_path_from_endpoint, validate_path)
from lollms.types import MSG_OPERATION_TYPE
from lollms.utilities import (PackageManager, add_period, detect_antiprompt,
                              find_first_available_file_index,
                              remove_text_from_string, trace_exception)
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse

from lollms_webui import LOLLMSWebUI

# ----------------------- Defining router and main class ------------------------------

router = APIRouter()
lollmsElfServer: LOLLMSWebUI = LOLLMSWebUI.get_instance()


# ----------------------- voice ------------------------------
@router.get("/get_presets")
def get_presets():
    presets = []
    presets_folder = Path("__file__").parent / "presets"
    for filename in presets_folder.glob("*.yaml"):
        with open(filename, "r", encoding="utf-8") as file:
            try:
                print(filename)
                preset = yaml.safe_load(file)
                if preset is not None:
                    presets.append(preset)
            except Exception as ex:
                trace_exception(ex)
    presets_folder = (
        lollmsElfServer.lollms_paths.personal_discussions_path
        / "lollms_playground_presets"
    )
    presets_folder.mkdir(exist_ok=True, parents=True)
    for filename in presets_folder.glob("*.yaml"):
        with open(filename, "r", encoding="utf-8") as file:
            preset = yaml.safe_load(file)
            if preset is not None:
                presets.append(preset)
    return presets


class PresetData(BaseModel):
    client_id: str
    name: str = Field(..., min_length=1)


@router.post("/add_preset")
async def add_preset(preset_data: PresetData):
    """
    Changes current voice

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """
    forbid_remote_access(lollmsElfServer)
    check_access(lollmsElfServer, preset_data.client_id)
    try:

        presets_folder = (
            lollmsElfServer.lollms_paths.personal_discussions_path
            / "lollms_playground_presets"
        )
        if not presets_folder.exists():
            presets_folder.mkdir(exist_ok=True, parents=True)

        # Ensure the name doesn't contain any path manipulation characters
        sanitize_path_from_endpoint(
            preset_data.name, exception_text="Invalid preset name"
        )

        fn = preset_data.name.lower().replace(" ", "_")
        filename = presets_folder / f"{fn}.yaml"
        with open(filename, "w", encoding="utf-8") as file:
            yaml.dump(preset_data, file)
        return {"status": True}
    except Exception as ex:
        trace_exception(ex)  # Assuming 'trace_exception' function logs the error
        return {"status": False, "error": "There was an error adding the preset"}


@router.post("/del_preset")
async def del_preset(preset_data: PresetData):
    """
    Saves a preset to a file.

    :param preset_data: The data of the preset.
    :return: A JSON response with the status of the operation.
    """
    forbid_remote_access(lollmsElfServer)
    check_access(lollmsElfServer, preset_data.client_id)
    # Get the JSON data from the POST request.
    if preset_data.name is None:
        raise HTTPException(
            status_code=400, detail="Preset name is missing in the request"
        )

    # Ensure the name doesn't contain any path manipulation characters
    sanitize_path_from_endpoint(preset_data.name, exception_text="Invalid preset name")

    presets_file = (
        lollmsElfServer.lollms_paths.personal_discussions_path
        / "lollms_playground_presets"
        / preset_data.name
    )
    try:
        presets_file.unlink()
        return {"status": True}
    except:
        return {"status": False}


class PresetDataWithValue(BaseModel):
    client_id: str
    name: str = Field(..., min_length=1)
    preset: str


@router.post("/save_presets")
async def save_presets(preset_data: PresetDataWithValue):
    """
    Saves a preset to a file.

    :param preset_data: The data of the preset.
    :return: A JSON response with the status of the operation.
    """
    forbid_remote_access(lollmsElfServer)
    check_access(lollmsElfServer, preset_data.client_id)
    # Get the JSON data from the POST request.
    if preset_data.preset is None:
        raise HTTPException(
            status_code=400, detail="Preset data is missing in the request"
        )

    # Ensure the name doesn't contain any path manipulation characters
    sanitize_path_from_endpoint(preset_data.name, exception_text="Invalid preset name")

    presets_file = (
        lollmsElfServer.lollms_paths.personal_discussions_path / "presets.json"
    )
    # Save the JSON data to a file.
    with open(presets_file, "w") as f:
        json.dump(preset_data.preset, f, indent=4)

    return {"status": True, "message": "Preset saved successfully!"}
