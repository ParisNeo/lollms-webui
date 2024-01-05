"""
File: lollms_web_ui.py
Author: ParisNeo
Description: Singleton class for the LoLLMS web UI.

This file is the entry point to the webui.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from lollms.app import LollmsApplication
from lollms.paths import LollmsPaths
from lollms.main_config import LOLLMSConfig
from lollms_webui import LOLLMSWebUI
from pathlib import Path
from ascii_colors import ASCIIColors
import socketio
import uvicorn
import argparse

app = FastAPI()




# Create a Socket.IO server
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")  # Enable CORS for all origins
app.mount("/socket.io", socketio.ASGIApp(sio))

# Define a WebSocket event handler
@sio.event
async def connect(sid, environ):
    print(f"Connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Disconnected: {sid}")

@sio.event
async def message(sid, data):
    print(f"Message from {sid}: {data}")
    await sio.send(sid, "Message received!")


#app.mount("/socket.io", StaticFiles(directory="path/to/socketio.js"))

if __name__ == "__main__":
    # Parsong parameters
    parser = argparse.ArgumentParser(description="Start the chatbot FastAPI app.")
    
    parser.add_argument(
        "--host", type=str, default=None, help="the hostname to listen on"
    )
    parser.add_argument("--port", type=int, default=None, help="the port to listen on")

    args = parser.parse_args()
    root_path = Path(__file__).parent
    lollms_paths = LollmsPaths.find_paths(force_local=True, custom_default_cfg_path="configs/config.yaml")
    config = LOLLMSConfig.autoload(lollms_paths)
    if args.host:
        config.host=args.host
    if args.port:
        config.port=args.port

    LOLLMSWebUI.build_instance(config=config, lollms_paths=lollms_paths, socketio=sio)

    # Import all endpoints
    from lollms.server.endpoints.lollms_infos import router as lollms_infos_router
    from lollms.server.endpoints.lollms_generator import router as lollms_generator_router
    from endpoints.lollms_discussion import router as lollms_discussion_router

    app.include_router(lollms_infos_router)
    app.include_router(lollms_generator_router)
    app.include_router(lollms_discussion_router)
    
    app.mount("/", StaticFiles(directory=Path(__file__).parent/"web"/"dist", html=True), name="static")


    uvicorn.run(app, host=config.host, port=config.port)