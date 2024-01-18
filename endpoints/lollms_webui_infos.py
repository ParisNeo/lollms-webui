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
from pathlib import Path
from typing import List
import sys
import socketio
import time
# ----------------------- Defining router and main class ------------------------------

# Create an instance of the LoLLMSWebUI class
lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()
router = APIRouter()

@router.get("/get_lollms_webui_version")
async def get_lollms_webui_version():
   """Get the version of the LoLLMs Web UI application."""
   # Return the version string
   return lollmsElfServer.version


@router.get("/restart_program")
async def restart_program():
   """Restart the program."""
   # Stop the socketIO server
   run_async(lollmsElfServer.sio.shutdown)
   # Sleep for 1 second before rebooting
   time.sleep(1)
   # Reboot the program
   lollmsElfServer.sio.reboot = True

@router.get("/update_software")
async def update_software():
   """Update the software."""
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
   run_async(lollmsElfServer.sio.shutdown)
   # Sleep for 1 second before rebooting
   time.sleep(1)

   # Run the update script using the provided arguments
   lollmsElfServer.run_update_script(lollmsElfServer.args)
   # Exit the program after successful update
   sys.exit()


@router.get("/check_update")
def check_update():
    """Checks if an update is available"""
    if lollmsElfServer.config.auto_update:
        res = lollmsElfServer.check_update_()
        return {'update_availability':res}
    else:
        return {'update_availability':False}
