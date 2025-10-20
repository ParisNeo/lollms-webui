"""
project: lollms_webui
file: lollms_webui_infos.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes allow users to retrieve details such as the current version number, a list of available databases, and options for 
    updating or restarting the software.

"""

import sys
import time
from pathlib import Path
from typing import List

import pkg_resources
import socketio
from ascii_colors import ASCIIColors
from fastapi import APIRouter, Request
from lollms.security import check_access, forbid_remote_access, sanitize_path
from lollms.utilities import load_config, run_async, show_yes_no_dialog
from pydantic import BaseModel, Field

from lollms_webui import LOLLMSWebUI

# ----------------------- Defining router and main class ------------------------------

# Create an instance of the LoLLMSWebUI class
lollmsElfServer: LOLLMSWebUI = LOLLMSWebUI.get_instance()
router = APIRouter()


class LastViewedVideoUrlRequest(BaseModel):
    client_id: str = Field(...)
    last_viewed_video_url: str = Field(..., description="Last viewed model")


@router.get("/get_versionID")
async def get_lollms_version():
    """Get the version of the LoLLMs Web UI application."""
    # Return the version string
    return {"id": 9}


@router.get("/get_changelog")
async def get_lollms_version():
    """Get the changelog."""
    # Return the version string
    with open("CHANGELOG.md", "r", encoding="utf8") as f:
        infos = f.read()
    return infos


@router.get("/get_news")
async def get_lollms_version():
    """Get the changelog."""
    base_path = Path(__file__).parent
    infos = base_path / "news" / "current.html"
    return infos.read_text(encoding="utf8")

import json
from pathlib import Path


@router.get("/get_last_video_url")
async def get_last_video_url():
    """Get the URL and type of the last video."""
    base_path = Path(__file__).parent
    info_file = base_path / "news" / "latest_video.json"

    try:
        with open(info_file, "r", encoding="utf-8") as file:
            video_info = json.load(file)

        return {"url": video_info["url"], "type": video_info["type"]}
    except FileNotFoundError:
        return {"error": "Video information not found"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in the video information file"}
    except KeyError as e:
        return {"error": f"Missing key in JSON: {str(e)}"}


@router.get("/get_last_viewed_video_url")
async def get_last_video_url():
    """Get the URL of the last video."""
    # This is a static URL for demonstration purposes
    return lollmsElfServer.config.last_viewed_video


@router.post("/set_last_viewed_video_url")
async def set_last_video_url(req: LastViewedVideoUrlRequest):
    """Get the URL of the last video."""
    # This is a static URL for demonstration purposes
    check_access(lollmsElfServer, req.client_id)
    lollmsElfServer.config.last_viewed_video = req.last_viewed_video_url
    lollmsElfServer.config.save_config()



# First, add this to your request models
class LastViewedChangelogVersionRequest(BaseModel):
    client_id: str
    version: str

@router.get("/get_last_viewed_changelog_version")
async def get_last_viewed_changelog_version():
    """Get the last changelog version viewed by the user."""
    return lollmsElfServer.config.last_viewed_changelog_version

@router.post("/set_last_viewed_changelog_version")
async def set_last_viewed_changelog_version(req: LastViewedChangelogVersionRequest):
    """Set the last changelog version viewed by the user."""
    check_access(lollmsElfServer, req.client_id)
    lollmsElfServer.config.last_viewed_changelog_version = req.version
    lollmsElfServer.config.save_config()
    return {"status": "success"}

@router.get("/get_themes")
async def get_themes():
    """Get the list of available themes."""
    base_path = Path(__file__).parent.parent
    themes_path = base_path / "web" / "dist" / "themes"

    # Get all .css files in the themes directory
    theme_files = list(themes_path.glob("*.css"))

    # Remove the .css extension from each file name
    themes = [theme_file.stem for theme_file in theme_files]

    return themes


@router.get("/get_lollms_webui_version")
async def get_lollms_webui_version():
    """Get the version of the LoLLMs Web UI application."""
    # Return the version string
    return lollmsElfServer.version


class Identification(BaseModel):
    client_id: str


@router.post("/restart_program")
async def restart_program(data: Identification):
    check_access(lollmsElfServer, data.client_id)
    """Restart the program."""
    forbid_remote_access(lollmsElfServer)
    if lollmsElfServer.config.headless_server_mode:
        return {
            "status": False,
            "error": "Restarting app is blocked when in headless mode for obvious security reasons!",
        }

    if (
        lollmsElfServer.config.host != "localhost"
        and lollmsElfServer.config.host != "127.0.0.1"
    ):
        return {
            "status": False,
            "error": "Restarting app is blocked when the server is exposed outside for very obvious reasons!",
        }

    if lollmsElfServer.config.turn_on_setting_update_validation:
        if not show_yes_no_dialog(
            "Validation",
            "Reboot requested from client\nDo you validate rebooting the app?",
        ):
            return {"status": False, "error": "User refused the execution!"}

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


@router.post("/update_software")
async def update_software(data: Identification):
    check_access(lollmsElfServer, data.client_id)
    """Update the software."""
    forbid_remote_access(lollmsElfServer)
    if lollmsElfServer.config.headless_server_mode:
        return {
            "status": False,
            "error": "Updating app is blocked when in headless mode for obvious security reasons!",
        }

    if (
        lollmsElfServer.config.host != "localhost"
        and lollmsElfServer.config.host != "127.0.0.1"
    ):
        return {
            "status": False,
            "error": "Updating app is blocked when the server is exposed outside for very obvious reasons!",
        }

    if lollmsElfServer.config.turn_on_setting_update_validation:
        if not show_yes_no_dialog(
            "Validation",
            "App upgrade requested from client\nDo you validate rebooting the app?",
        ):
            return {"status": False, "error": "User refused the execution!"}

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
        return {
            "status": False,
            "error": "Checking updates is blocked when in headless mode for obvious security reasons!",
        }

    if (
        lollmsElfServer.config.host != "localhost"
        and lollmsElfServer.config.host != "127.0.0.1"
    ):
        return {
            "status": False,
            "error": "Checking updates is blocked when the server is exposed outside for very obvious reasons!",
        }

    if lollmsElfServer.config.auto_update:
        res = lollmsElfServer.check_update_()
        return {"update_availability": res}
    else:
        return {"update_availability": False}
