"""
project: lollms_webui
file: lollms_webui_infos.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes allow users to retrieve details such as the current version number, a list of available databases, and options for 
    updating or restarting the software.

"""

from fastapi import APIRouter, Request
import pkg_resources
from lollms_webui import LOLLMSWebUI
from ascii_colors import ASCIIColors
from lollms.utilities import load_config, run_async
from lollms.security import sanitize_path, forbid_remote_access
from pathlib import Path
from typing import List
import sys
import socketio
import time
# ----------------------- Defining router and main class ------------------------------

# Create an instance of the LoLLMSWebUI class
lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()
router = APIRouter()


@router.get("/get_versionID")
async def get_lollms_webui_version():
   """Get the version of the LoLLMs Web UI application."""
   # Return the version string
   return {"id":4}

@router.get("/get_lollms_webui_version")
async def get_lollms_webui_version():
   """Get the version of the LoLLMs Web UI application."""
   # Return the version string
   return lollmsElfServer.version


@router.get("/restart_program")
async def restart_program():
    """Restart the program."""
    forbid_remote_access(lollmsElfServer)
    if lollmsElfServer.config.headless_server_mode:
        return {"status":False,"error":"Restarting app is blocked when in headless mode for obvious security reasons!"}

    if lollmsElfServer.config.host!="localhost" and lollmsElfServer.config.host!="127.0.0.1":
        return {"status":False,"error":"Restarting app is blocked when the server is exposed outside for very obvious reasons!"}

    lollmsElfServer.ShowBlockingMessage("Restarting program.\nPlease stand by...")
    # Stop the socketIO server
    run_async(lollmsElfServer.sio.shutdown)
    # Sleep for 1 second before rebooting
    time.sleep(1)
    lollmsElfServer.HideBlockingMessage()
    # Reboot the program
    ASCIIColors.info("")
    ASCIIColors.info("")
    ASCIIColors.info("")
    ASCIIColors.info(" ╔══════════════════════════════════════════════════╗")
    ASCIIColors.info(" ║              Restarting backend                  ║")
    ASCIIColors.info(" ╚══════════════════════════════════════════════════╝")
    ASCIIColors.info("")
    ASCIIColors.info("")
    ASCIIColors.info("")
    lollmsElfServer.run_restart_script(lollmsElfServer.args)
    
@router.get("/update_software")
async def update_software():
    """Update the software."""
    forbid_remote_access(lollmsElfServer)
    if lollmsElfServer.config.headless_server_mode:
        return {"status":False,"error":"Updating app is blocked when in headless mode for obvious security reasons!"}

    if lollmsElfServer.config.host!="localhost" and lollmsElfServer.config.host!="127.0.0.1":
        return {"status":False,"error":"Updating app is blocked when the server is exposed outside for very obvious reasons!"}

    # Display an informative message
    ASCIIColors.info("")
    ASCIIColors.info("")
    ASCIIColors.info("")
    ASCIIColors.info("╔══════════════════════════════════════════════════╗")
    ASCIIColors.info("║                Updating backend                  ║")
    ASCIIColors.info("╚══════════════════════════════════════════════════╝")
    ASCIIColors.info("")
    ASCIIColors.info("")
    ASCIIColors.info("")
    # Stop the socketIO server
    await lollmsElfServer.sio.shutdown()
    # Sleep for 1 second before rebooting
    time.sleep(1) 

    # Run the update script using the provided arguments
    lollmsElfServer.run_update_script(lollmsElfServer.args)
    # Exit the program after successful update
    sys.exit()


@router.get("/check_update")
def check_update():
    """Checks if an update is available"""
    forbid_remote_access(lollmsElfServer)
    if lollmsElfServer.config.headless_server_mode:
        return {"status":False,"error":"Checking updates is blocked when in headless mode for obvious security reasons!"}

    if lollmsElfServer.config.host!="localhost" and lollmsElfServer.config.host!="127.0.0.1":
        return {"status":False,"error":"Checking updates is blocked when the server is exposed outside for very obvious reasons!"}
    
    if lollmsElfServer.config.auto_update:
        res = lollmsElfServer.check_update_()
        return {'update_availability':res}
    else:
        return {'update_availability':False}
