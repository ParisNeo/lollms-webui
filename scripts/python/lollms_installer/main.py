"""
Project: lollms_installer
Author: ParisNeo
Description: This tool is designed to install and configure the LoLLMS system on your machine. LoLLMS is a multi-bindings, multi-personalities LLM full-stack system for AI applications in robotics. It provides a user-friendly interface for setting up and managing the system.
"""

import webbrowser
from pathlib import Path

import socketio
import uvicorn
from ascii_colors import ASCIIColors
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from lollms.app import LollmsApplication
from lollms.com import LoLLMsCom, NotificationDisplayType, NotificationType
from lollms.main_config import LOLLMSConfig
from lollms.paths import LollmsPaths
from lollms.types import MSG_OPERATION_TYPE, SENDER_TYPES
from lollms.utilities import (PackageManager, check_and_install_torch,
                              check_torch_version, reinstall_pytorch_with_cpu,
                              reinstall_pytorch_with_cuda,
                              reinstall_pytorch_with_rocm)
from pydantic import BaseModel
from socketio import ASGIApp

root_path = Path(__file__).parent.parent.parent.parent
global_path = root_path / "global_paths_cfg.yaml"
if global_path.exists():
    ASCIIColors.yellow(f"global_path: {global_path}")
    lollms_paths = LollmsPaths(global_path, prepare_configuration=False)
    config = LOLLMSConfig.autoload(
        lollms_paths, lollms_paths.personal_configuration_path / "local_config.yaml"
    )
else:
    ASCIIColors.yellow(f"global_path: {global_path}")
    lollms_paths = LollmsPaths(global_path, prepare_configuration=False)
    config = LOLLMSConfig.autoload(
        lollms_paths, lollms_paths.personal_configuration_path / "local_config.yaml"
    )


ASCIIColors.red("                                     ")
ASCIIColors.red(" __    _____ __    __    _____ _____ ")
ASCIIColors.red("|  |  |     |  |  |  |  |     |   __|")
ASCIIColors.red("|  |__|  |  |  |__|  |__| | | |__   |")
ASCIIColors.red("|_____|_____|_____|_____|_|_|_|_____|")
ASCIIColors.red(" Configurator                        ")
ASCIIColors.red(" LoLLMS configuratoin tool")
ASCIIColors.yellow(f"Root dir : {root_path}")

sio = socketio.AsyncServer(async_mode="asgi")
app = FastAPI(title="LoLLMS", description="This is the LoLLMS-Webui documentation")

lollms_app = LollmsApplication(
    "lollms_installer",
    config=config,
    lollms_paths=lollms_paths,
    load_binding=False,
    load_model=False,
    load_voice_service=False,
    load_sd_service=False,
    socketio=sio,
    free_mode=True,
)


class InstallProperties(BaseModel):
    mode: str


@app.get("/get_personal_path")
def get_personal_path():
    return lollms_paths.personal_path


@app.post("/start_installing")
def start_installing(data: InstallProperties):
    """
    Handle the start_installing endpoint.

    Parameters:
    - **data**: An instance of the `InstallProperties` model containing the installation mode.

    Returns:
    - A dictionary with a "message" key indicating the success of the installation.
    """
    # Install mode (cpu, cpu-noavx, nvidia-tensorcores, nvidia, amd-noavx, amd, apple-intel, apple-silicon)
    if data.mode == "cpu":
        config.hardware_mode = "cpu"
        try:
            lollms_app.ShowBlockingMessage("Setting hardware configuration to CPU")
            config.save_config()
            lollms_app.HideBlockingMessage()
        except:
            lollms_app.HideBlockingMessage()
    if data.mode == "cpu-noavx":
        config.hardware_mode = "cpu-noavx"
        try:
            lollms_app.ShowBlockingMessage(
                "Setting hardware configuration to CPU with no avx support"
            )
            config.save_config()
            lollms_app.HideBlockingMessage()
        except:
            lollms_app.HideBlockingMessage()
    elif data.mode == "nvidia":
        config.hardware_mode = "nvidia"
        try:
            lollms_app.ShowBlockingMessage("Installing pytorch for nVidia GPU (cuda)")
            config.save_config()
            lollms_app.HideBlockingMessage()
        except:
            lollms_app.HideBlockingMessage()
    elif data.mode == "nvidia-tensorcores":
        config.hardware_mode = "nvidia-tensorcores"
        try:
            lollms_app.ShowBlockingMessage("Installing pytorch for nVidia GPU (cuda)")
            config.save_config()
            lollms_app.HideBlockingMessage()
        except:
            lollms_app.HideBlockingMessage()
    elif data.mode == "amd":
        config.hardware_mode = "amd"
        try:
            lollms_app.ShowBlockingMessage("Installing pytorch for AMD GPU (rocm)")
            config.save_config()
            lollms_app.HideBlockingMessage()
        except:
            lollms_app.HideBlockingMessage()
    elif data.mode == "apple-silicon":
        config.hardware_mode = "apple-silicon"
        try:
            lollms_app.ShowBlockingMessage(
                "Installing pytorch for Apple Silicon (Metal)"
            )
            config.save_config()
            lollms_app.HideBlockingMessage()
        except:
            lollms_app.HideBlockingMessage()
    elif data.mode == "apple-intel":
        config.hardware_mode = "apple-intel"
        try:
            lollms_app.ShowBlockingMessage(
                "Installing pytorch for Apple Silicon (Metal)"
            )
            config.save_config()
            lollms_app.HideBlockingMessage()
        except:
            lollms_app.HideBlockingMessage()
    # Your code here
    return {"message": "Item created successfully"}


app.mount(
    "/",
    StaticFiles(directory=Path(__file__).parent / "frontend" / "dist", html=True),
    name="static",
)
app = ASGIApp(socketio_server=sio, other_asgi_app=app)

if __name__ == "__main__":
    webbrowser.open(f"http://localhost:8000")
    uvicorn.run(app, host="localhost", port=8000)
