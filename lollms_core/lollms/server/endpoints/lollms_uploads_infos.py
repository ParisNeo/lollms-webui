"""
project: lollms
file: lollms_uploads_infos.py 
author: ParisNeo
description: 
   This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
   application. These routes are specific to uploaded files. They include functionality to remove all uploaded files from the server.
"""
from fastapi import APIRouter, Request
from pydantic import BaseModel
import pkg_resources
from lollms.server.elf_server import LOLLMSElfServer
from lollms.binding import BindingBuilder, InstallOption
from ascii_colors import ASCIIColors
from lollms.utilities import load_config, trace_exception, gc
from pathlib import Path
from typing import List
import shutil

# ----------------------- Defining router and main class ------------------------------
router = APIRouter()
lollmsElfServer = LOLLMSElfServer.get_instance()

@router.get("/clear_uploads")
def clear_uploads():
    """
    Clears all uploads from the specified path.
    
    Parameters:
        None
    
    Returns:
        status (bool): Whether the operation was successful or not.
        error (Optional[str]): An optional error message if the operation failed.
    
    """    
    ASCIIColors.info("")
    ASCIIColors.info("")
    ASCIIColors.info("")
    ASCIIColors.info(" ╔══════════════════════════════════════════════════╗")
    ASCIIColors.info(" ║               Removing all uploads               ║")
    ASCIIColors.info(" ╚══════════════════════════════════════════════════╝")
    ASCIIColors.info("")
    ASCIIColors.info("")
    ASCIIColors.info("")        
    try:
        folder_path = lollmsElfServer.lollms_paths.personal_uploads_path
        # Iterate over all files and directories in the folder
        for entry in folder_path.iterdir():
            if entry.is_file():
                # Remove file
                entry.unlink()
            elif entry.is_dir():
                # Remove directory (recursively)
                shutil.rmtree(entry)
        print(f"All files and directories inside '{folder_path}' have been removed successfully.")
        return {"status": True}
    except OSError as e:
        ASCIIColors.error(f"Couldn't clear the upload folder.\nMaybe some files are opened somewhere else.\Try doing it manually")
        return {"status": False, 'error': "Couldn't clear the upload folder.\nMaybe some files are opened somewhere else.\Try doing it manually"}
