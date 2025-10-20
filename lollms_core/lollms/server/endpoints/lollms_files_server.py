"""
project: lollms
file: lollms_binding_files_server.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes are specific to serving files

"""
from fastapi import APIRouter, Request, Depends
from fastapi import HTTPException
from pydantic import BaseModel, validator
import pkg_resources
from lollms.server.elf_server import LOLLMSElfServer
from fastapi.responses import FileResponse
from lollms.binding import BindingBuilder, InstallOption
from lollms.security import sanitize_path_from_endpoint
from ascii_colors import ASCIIColors
from lollms.utilities import load_config, trace_exception, gc
from pathlib import Path
from typing import List
from lollms.security import sanitize_svg
import os
import re

# ----------------------- Defining router and main class ------------------------------
router = APIRouter()
lollmsElfServer = LOLLMSElfServer.get_instance()


# ----------------------------------- Personal files -----------------------------------------
@router.get("/user_infos/{path:path}")
async def serve_user_infos(path: str):
    """
    Serve user information file.

    Args:
        path (FilePath): The validated path to the file to be served.

    Returns:
        FileResponse: The file response containing the requested file.
    """ 
    path = sanitize_path_from_endpoint(path)

    file_path:Path = lollmsElfServer.lollms_paths.personal_user_infos_path / path
    if not file_path.exists():
        raise HTTPException(status_code=400, detail="File not found")
    return FileResponse(str(file_path))

# ----------------------------------- Lollms zoos -----------------------------------------
@router.get("/bindings/{path:path}")
async def serve_bindings(path: str):
    """
    Serve bindings file.

    Args:
        path (FilePath): The path of the bindings file to serve.

    Returns:
        FileResponse: The file response containing the requested bindings file.
    """
    
    path = sanitize_path_from_endpoint(path)    
    file_path = lollmsElfServer.lollms_paths.bindings_zoo_path / path

    if not Path(file_path).exists():
        raise HTTPException(status_code=400, detail="File not found")

    return FileResponse(str(file_path))

@router.get("/personalities/{path:path}")
async def serve_personalities(path: str):
    """
    Serve personalities file.

    Args:
        path (FilePath): The path of the personalities file to serve.

    Returns:
        FileResponse: The file response containing the requested personalities file.
    """
    path = sanitize_path_from_endpoint(path)    
    
    if "custom_personalities" in path:
        file_path = lollmsElfServer.lollms_paths.custom_personalities_path / "/".join(str(path).split("/")[1:])
    else:
        file_path = lollmsElfServer.lollms_paths.personalities_zoo_path / path

    if not Path(file_path).exists():
        raise HTTPException(status_code=400, detail="File not found")

    return FileResponse(str(file_path))


# ----------------------------------- Services -----------------------------------------

@router.get("/audio/{path:path}")
async def serve_audio(path: str):
    """
    Serve audio file.

    Args:
        filename (str): The name of the audio file to serve.

    Returns:
        FileResponse: The file response containing the requested audio file.
    """
    path = sanitize_path_from_endpoint(path)    

    root_dir = Path(lollmsElfServer.lollms_paths.personal_outputs_path).resolve()
    file_path = root_dir/ 'audio_out' / path

    if not Path(file_path).exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(str(file_path))


@router.get("/images/{path:path}")
async def serve_images(path: str):
    """
    Serve image file.

    Args:
        filename (str): The name of the image file to serve.

    Returns:
        FileResponse: The file response containing the requested image file.
    """
    path = sanitize_path_from_endpoint(path)    

    root_dir = Path(os.getcwd())/ "images/"
    file_path = root_dir / path

    if not Path(file_path).exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(str(file_path))


# ----------------------------------- User content -----------------------------------------

@router.get("/outputs/{path:path}")
async def serve_outputs(path: str):
    """
    Serve image file.

    Args:
        filename (str): The name of the output file to serve.

    Returns:
        FileResponse: The file response containing the requested output file.
    """
    path = sanitize_path_from_endpoint(path)    

    root_dir = lollmsElfServer.lollms_paths.personal_outputs_path
    root_dir.mkdir(exist_ok=True, parents=True)
    file_path = root_dir / path

    if not Path(file_path).exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(str(file_path))



@router.get("/data/{path:path}")
async def serve_data(path: str):
    """
    Serve image file.

    Args:
        filename (str): The name of the data file to serve.

    Returns:
        FileResponse: The file response containing the requested data file.
    """
    path = sanitize_path_from_endpoint(path)    

    root_dir = lollmsElfServer.lollms_paths.personal_path / "data"
    root_dir.mkdir(exist_ok=True, parents=True)
    file_path = root_dir / path

    if not Path(file_path).exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(str(file_path))




@router.get("/uploads/{path:path}")
async def serve_uploads(path: str):
    """
    Serve image file.

    Args:
        filename (str): The name of the uploads file to serve.

    Returns:
        FileResponse: The file response containing the requested uploads file.
    """
    path = sanitize_path_from_endpoint(path)    

    root_dir = lollmsElfServer.lollms_paths.personal_path / "uploads"
    root_dir.mkdir(exist_ok=True, parents=True)
    file_path = root_dir / path

    if not Path(file_path).exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(str(file_path))



@router.get("/discussions/{path:path}")
async def serve_discussions(path: str):
    """
    Serve discussion file.

    Args:
        filename (str): The name of the uploads file to serve.

    Returns:
        FileResponse: The file response containing the requested uploads file.
    """
    path = sanitize_path_from_endpoint(path)    

    root_dir = lollmsElfServer.lollms_paths.personal_discussions_path
    root_dir.mkdir(exist_ok=True, parents=True)
    file_path = root_dir / path

    if not Path(file_path).exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Check if the file is an SVG
    if file_path.suffix.lower() == '.svg':
        with open(file_path, 'r', encoding='utf-8') as file:
            svg_content = file.read()
        sanitized_svg_content = sanitize_svg(svg_content)
        
        # Save the sanitized SVG content to a temporary file
        temp_svg_path = file_path.with_suffix('.sanitized.svg')
        with open(temp_svg_path, 'w', encoding='utf-8') as file:
            file.write(sanitized_svg_content)
        
        return FileResponse(str(temp_svg_path))

    return FileResponse(str(file_path))


