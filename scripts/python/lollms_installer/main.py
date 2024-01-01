"""
Project: lollms_installer
Author: Your Name
Description: This tool is designed to install and configure the LoLLMS system on your machine. LoLLMS is a multi-bindings, multi-personalities LLM full-stack system for AI applications in robotics. It provides a user-friendly interface for setting up and managing the system.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from lollms.paths import LollmsPaths
from lollms.main_config import LOLLMSConfig
from lollms.utilities import check_and_install_torch, PackageManager, check_torch_version, reinstall_pytorch_with_cuda, reinstall_pytorch_with_cpu, reinstall_pytorch_with_rocm
from lollms.com import NotificationType, NotificationDisplayType, LoLLMsCom
from lollms.types import MSG_TYPE, SENDER_TYPES
from lollms.app import LollmsApplication
from pathlib import Path
from ascii_colors import ASCIIColors
import subprocess
from pathlib import Path

from starlette.responses import FileResponse
from starlette.requests import Request
import webbrowser
import socketio

root_path = Path(__file__).parent.parent.parent.parent
global_path = root_path/"global_paths_cfg.yaml"
ASCIIColors.yellow(f"global_path: {global_path}")
lollms_paths = LollmsPaths(global_path)
config = LOLLMSConfig(lollms_paths.personal_configuration_path/"local_config.yaml")
shared_folder = lollms_paths.personal_path/"shared"
sd_folder = shared_folder / "auto_sd"
output_dir = lollms_paths.personal_path / "outputs/sd"
output_dir.mkdir(parents=True, exist_ok=True)
script_path = sd_folder / "lollms_sd.bat"
output_folder = lollms_paths.personal_outputs_path/"audio_out"

ASCIIColors.red("                                     ")
ASCIIColors.red(" __    _____ __    __    _____ _____ ")
ASCIIColors.red("|  |  |     |  |  |  |  |     |   __|")
ASCIIColors.red("|  |__|  |  |  |__|  |__| | | |__   |")
ASCIIColors.red("|_____|_____|_____|_____|_|_|_|_____|")
ASCIIColors.red(" Configurator                        ")
ASCIIColors.red(" LoLLMS configuratoin tool")
ASCIIColors.yellow(f"Root dir : {root_path}")

sio = socketio.AsyncServer(async_mode='asgi')
app = FastAPI(debug=True)
app.mount("/socket.io", socketio.ASGIApp(sio))

lollms_app = LollmsApplication("lollms_installer",config=config,lollms_paths=lollms_paths, load_binding=False, load_model=False, socketio=sio)

# Serve the index.html file for all routes
@app.get("/{full_path:path}")
async def serve_index(request: Request, full_path: Path):
    if str(full_path).endswith(".js"):
        return FileResponse(root_path/"scripts/python/lollms_installer/frontend/dist"/full_path, media_type="application/javascript")    
    if str(full_path).endswith(".css"):
        return FileResponse(root_path/"scripts/python/lollms_installer/frontend/dist"/full_path)    
    if str(full_path).endswith(".html"):
        return FileResponse(root_path/"scripts/python/lollms_installer/frontend/dist"/full_path)    
    return FileResponse(root_path/"scripts/python/lollms_installer/frontend/dist/index.html")

#  app.mount("/", StaticFiles(directory=root_path/"scripts/python/lollms_installer/frontend/dist"), name="static")

class InstallProperties(BaseModel):
    mode: str

@app.post("/start_installing")
def start_installing(data: InstallProperties):
    """
    Handle the start_installing endpoint.

    Parameters:
    - **data**: An instance of the `InstallProperties` model containing the installation mode.

    Returns:
    - A dictionary with a "message" key indicating the success of the installation.
    """
    if data.mode=="cpu":
        config.enable_gpu=False
        try:
            lollms_app.ShowBlockingMessage("Installing pytorch for CPU")
            reinstall_pytorch_with_cpu()
            config.save_config()
            lollms_app.HideBlockingMessage()
        except:
            lollms_app.HideBlockingMessage()

    elif data.mode=="cuda":
        config.enable_gpu=True
        try:
            lollms_app.ShowBlockingMessage("Installing pytorch for nVidia GPU (cuda)")
            reinstall_pytorch_with_cuda()
            config.save_config()
            lollms_app.HideBlockingMessage()
        except:
            lollms_app.HideBlockingMessage()
    elif data.mode=="rocm":
        config.enable_gpu=True
        try:
            lollms_app.ShowBlockingMessage("Installing pytorch for AMD GPU (rocm)")
            reinstall_pytorch_with_rocm()
            config.save_config()
            lollms_app.HideBlockingMessage()
        except:
            lollms_app.HideBlockingMessage()
    elif data.mode=="metal":
        try:
            lollms_app.ShowBlockingMessage("Installing pytorch for Apple Silicon (Metal)")
            config.enable_gpu=False
            reinstall_pytorch_with_cpu()
            config.save_config()
            lollms_app.HideBlockingMessage()
        except:
            lollms_app.HideBlockingMessage()
    # Your code here
    return {"message": "Item created successfully"}

if __name__ == "__main__":
    webbrowser.open(f"http://localhost:8000")
    uvicorn.run(app, host="localhost", port=8000)