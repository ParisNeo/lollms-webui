"""
project: lollms
file: lollms_models_infos.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes are specific to handling models related operations.

"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import pkg_resources
from lollms.server.elf_server import LOLLMSElfServer
from lollms.security import sanitize_path, forbid_remote_access
from ascii_colors import ASCIIColors
from lollms.utilities import load_config
from pathlib import Path
from typing import List
import psutil

from lollms.utilities import trace_exception
class ModelReferenceParams(BaseModel):
    path: str


# ----------------------- Defining router and main class ------------------------------
router = APIRouter()
lollmsElfServer = LOLLMSElfServer.get_instance()


@router.get("/list_models")
async def list_models():
    """
    List all available models for the specified binding.

    Parameters:
        - binding (str): Name of the binding to retrieve models from.

    Returns:
        List[str]: A list of model names.
    """
    if lollmsElfServer.binding is not None:
        ASCIIColors.yellow("Listing models", end="")
        models = lollmsElfServer.binding.list_models()
        ASCIIColors.green("ok")
        return models
    else:
        return []

   
@router.get("/get_available_models")
async def get_available_models():
    """
    Retrieve a list of available models for the currently selected binding.

    Returns:
        List[str]: A list of model names.
    """
    if lollmsElfServer.binding is None:
        return []
    try:
        model_list = lollmsElfServer.binding.get_available_models(lollmsElfServer)
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error("Coudln't list models. Please reinstall the binding or notify ParisNeo on the discord server")
        return []

    return model_list

@router.get("/get_active_model")
def get_active_model():
    if lollmsElfServer.binding is not None:
        try:
            ASCIIColors.yellow("Getting active model")
            models = lollmsElfServer.binding.list_models()
            index = models.index(lollmsElfServer.config.model_name)
            ASCIIColors.green("ok")
            return {"status":True,"model":models[index],"index":index}
        except Exception as ex:
            return {"status":False}
    else:
        return {"status":False}

@router.get("/get_model_status")
def get_model_status():
    return {"status":lollmsElfServer.model is not None}

@router.post("/add_reference_to_local_model")
def add_reference_to_local_model(data:ModelReferenceParams):     
   
    forbid_remote_access(lollmsElfServer)
    data.path = sanitize_path(data.path, allow_absolute_path=True)
    
    if data.path=="":
        return {"status": False, "error":"Empty model path"}   

    path = Path(data.path)
    if path.exists():
        lollmsElfServer.binding.reference_model(path)
        return {"status": True} 
    else:        
        return {"status": False, "error":"Model not found"}       





@router.get("/api/pull")
async def ollama_pull_model():
    raise HTTPException(400, "Not implemented")

@router.get("/api/tags")
async def ollama_list_models():
    """
    Retrieve a list of available models for the currently selected binding.

    Returns:
        List[str]: A list of model names.
    """
    if lollmsElfServer.binding is None:
        return []
    try:
        model_list = lollmsElfServer.binding.get_available_models(lollmsElfServer)

        md = {
        "models": [
            {
            "name": model["name"],
            "modified_at": model["last_commit_time"],
            "size": model["variants"][0]["size"],
            "digest": "9f438cb9cd581fc025612d27f7c1a6669ff83a8bb0ed86c94fcf4c5440555697",
            "details": {
                "format": "gguf",
                "family": "llama",
                "families": None,
                "parameter_size": "13B",
                "quantization_level": "Q4_0"
            }
            }
            for model in model_list
        ]
        }
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error("Coudln't list models. Please reinstall the binding or notify ParisNeo on the discord server")
        return []

    return md