"""
project: lollms_user
file: lollms_user.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes allow users to manipulate user information.

"""
from fastapi import APIRouter, HTTPException
from lollms_webui import LOLLMSWebUI
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from lollms.types import MSG_OPERATION_TYPE
from lollms.main_config import BaseConfig
from lollms.utilities import detect_antiprompt, remove_text_from_string
from ascii_colors import ASCIIColors
from lollms.databases.discussions_database import DiscussionsDB
from lollms.security import check_access
from pathlib import Path
import tqdm
from fastapi import FastAPI, UploadFile, File
import shutil
import uuid
import os
from PIL import Image

class PersonalPathParameters(BaseModel):
    client_id:str
    path:str
    
# ----------------------- Defining router and main class ------------------------------

router = APIRouter()
lollmsElfServer = LOLLMSWebUI.get_instance()

"""
@router.post("/switch_personal_path")
def switch_personal_path(data:PersonalPathParameters):
    client = check_access(lollmsElfServer, data.client_id)
    path = data.path
    global_paths_cfg = Path("./global_paths_cfg.yaml")
    if global_paths_cfg.exists():
        try:
            cfg = BaseConfig()
            cfg.load_config(global_paths_cfg)
            cfg.lollms_personal_path = path
            cfg.save_config(global_paths_cfg)
            return {"status": True}      
        except Exception as ex:
            print(ex)
            return {"status": False, 'error':f"Couldn't switch path: {ex}"}    
"""

        
@router.post("/upload_avatar")
async def upload_avatar(avatar: UploadFile = File(...)):
    """
    Uploads a user avatar file to a dedicated directory, preventing path traversal attacks.

    Parameters:
        - avatar: UploadFile object representing the user avatar file.

    Returns:
        - Dictionary with the status of the upload and the generated file name.

    Raises:
        - HTTPException with a 400 status code and an error message if the file is invalid or has an invalid type.
    """
    # Only allow certain file types
    if avatar.filename.endswith((".jpg", ".png")):
        # Create a random file name
        random_filename = str(uuid.uuid4())
        
        # Use the file extension of the uploaded file
        extension = os.path.splitext(avatar.filename)[1]
        
        # Create the new file path in a dedicated directory
        file_location = os.path.join(lollmsElfServer.lollms_paths.personal_user_infos_path, f"{random_filename}{extension}")

        try:
            # Open the image to check if it's a valid image
            img = Image.open(avatar.file)
            
            # Save the file
            img.save(file_location)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid image file.")
    else:
        raise HTTPException(status_code=400, detail="Invalid file type.")
        
    return {"status": True,"fileName": f"{random_filename}{extension}"}

@router.post("/upload_logo")
async def upload_logo(logo: UploadFile = File(...)):
    """
    Uploads a user avatar file to a dedicated directory, preventing path traversal attacks.

    Parameters:
        - logo: UploadFile object representing the user avatar file.

    Returns:
        - Dictionary with the status of the upload and the generated file name.

    Raises:
        - HTTPException with a 400 status code and an error message if the file is invalid or has an invalid type.
    """
    # Only allow certain file types
    if logo.filename.endswith((".jpg", ".png")):
        # Create a random file name
        random_filename = str(uuid.uuid4())
        
        # Use the file extension of the uploaded file
        extension = os.path.splitext(logo.filename)[1]
        
        # Create the new file path in a dedicated directory
        file_location = os.path.join(lollmsElfServer.lollms_paths.personal_user_infos_path, f"{random_filename}{extension}")

        try:
            # Open the image to check if it's a valid image
            img = Image.open(logo.file)
            
            # Save the file
            img.save(file_location)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid image file.")
    else:
        raise HTTPException(status_code=400, detail="Invalid file type.")
        
    return {"status": True,"fileName": f"{random_filename}{extension}"}

@router.post("/remove_logo")
async def remove_logo():
    """
    Uploads a user avatar file to a dedicated directory, preventing path traversal attacks.

    Parameters:
        - logo: UploadFile object representing the user avatar file.

    Returns:
        - Dictionary with the status of the upload and the generated file name.

    Raises:
        - HTTPException with a 400 status code and an error message if the file is invalid or has an invalid type.
    """
        
    return {"status": True}
