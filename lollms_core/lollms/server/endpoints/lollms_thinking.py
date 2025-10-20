"""
project: lollms
file: lollms_thinking.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes are specific to bindings

"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
import pkg_resources
from lollms.server.elf_server import LOLLMSElfServer
from lollms.binding import BindingBuilder, InstallOption
from ascii_colors import ASCIIColors
from lollms.utilities import load_config, trace_exception, gc
from lollms.security import sanitize_path_from_endpoint, sanitize_path, check_access
from lollms.security import check_access
from pathlib import Path
from typing import List, Any
import json
import os
# ----------------------------------- Personal files -----------------------------------------

class ClientAuthentication(BaseModel):
    client_id: str  = Field(...)

class ReloadBindingParams(BaseModel):
    binding_name: str = Field(..., min_length=1, max_length=50)

class BindingInstallParams(BaseModel):
    client_id: str
    name: str = Field(..., min_length=1, max_length=50)


# ----------------------- Defining router and main class ------------------------------
router = APIRouter()
lollmsElfServer = LOLLMSElfServer.get_instance()


# ----------------------------------- Endpoints -----------------------------------------

@router.post("/get_thinking_methods")
def get_thinking_methods(request: ClientAuthentication):
    """
    Retrieves the thinking methods from the thinking_methods.yaml file
    
    Args:
        request (ClientAuthentication): Client authentication information
        
    Returns:
        dict: Dictionary containing the thinking methods
        
    Raises:
        HTTPException: If file not found or invalid format
    """
    try:
        check_access(lollmsElfServer, request.client_id)
        # Get the current file's directory
        current_dir = Path(__file__).parent
        # Go up one level and construct path to thinking_methods.yaml
        yaml_path = current_dir.parent / "assets" / "thinking_methods.yaml"
        
        # Check if file exists
        if not yaml_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Thinking methods configuration file not found"
            )
            
        # Load yaml file
        import yaml
        with open(yaml_path, 'r', encoding='utf-8') as f:
            thinking_methods = yaml.safe_load(f)
            
        # Validate format
        if not isinstance(thinking_methods, list):
            raise HTTPException(
                status_code=400,
                detail="Invalid thinking methods format - expected list"
            )
            
        for method in thinking_methods:
            if not all(key in method for key in ['name', 'description', 'prompt']):
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid thinking method format - missing required fields"
                )
                
        return {
            "status": "success",
            "thinking_methods": thinking_methods
        }
        
    except Exception as e:
        trace_exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Error loading thinking methods: {str(e)}"
        )
