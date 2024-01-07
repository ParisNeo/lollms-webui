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
from lollms.utilities import trace_exception
from lollms_webui import LOLLMSWebUI
from pathlib import Path
from ascii_colors import ASCIIColors
import socketio
import uvicorn
import argparse
from socketio import ASGIApp
import webbrowser

app = FastAPI()

# Create a Socket.IO server
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")  # Enable CORS for all origins


@sio.event
async def disconnect(sid):
    ASCIIColors.yellow(f"Disconnected: {sid}")

@sio.event
async def message(sid, data):
    ASCIIColors.yellow(f"Message from {sid}: {data}")
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
    lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()
    # Import all endpoints
    from lollms.server.endpoints.lollms_binding_files_server import router as lollms_binding_files_server_router
    from lollms.server.endpoints.lollms_infos import router as lollms_infos_router
    from lollms.server.endpoints.lollms_hardware_infos import router as lollms_hardware_infos_router
    from lollms.server.endpoints.lollms_binding_infos import router as lollms_binding_infos_router
    from lollms.server.endpoints.lollms_models_infos import router as lollms_models_infos_router
    from lollms.server.endpoints.lollms_personalities_infos import router as lollms_personalities_infos_router
    from lollms.server.endpoints.lollms_extensions_infos import router as lollms_extensions_infos_router
    from lollms.server.endpoints.lollms_generator import router as lollms_generator_router
    from lollms.server.endpoints.lollms_configuration_infos import router as lollms_configuration_infos_router
    from endpoints.lollms_webui_infos import router as lollms_webui_infos_router
    from endpoints.lollms_discussion import router as lollms_discussion_router
    from endpoints.lollms_message import router as lollms_message_router
    from endpoints.lollms_user import router as lollms_user_router
    from endpoints.lollms_advanced import router as lollms_advanced_router
    from endpoints.chat_bar import router as chat_bar_router
    


    from lollms.server.events.lollms_generation_events import add_events as lollms_generation_events_add
    from events.lollms_generation_events import add_events as lollms_webui_generation_events_add
    from events.lollms_discussion_events import add_events as lollms_webui_discussion_events_add

    app.include_router(lollms_infos_router)
    app.include_router(lollms_binding_files_server_router)
    app.include_router(lollms_hardware_infos_router)    
    app.include_router(lollms_binding_infos_router)    
    app.include_router(lollms_models_infos_router)   
    app.include_router(lollms_personalities_infos_router)   
    app.include_router(lollms_extensions_infos_router)   
    
    

    app.include_router(lollms_webui_infos_router)
    app.include_router(lollms_generator_router)
    app.include_router(lollms_discussion_router)
    app.include_router(lollms_message_router)
    app.include_router(lollms_user_router)
    app.include_router(lollms_advanced_router)
    app.include_router(chat_bar_router)
    
    
    app.include_router(lollms_configuration_infos_router)


    lollms_generation_events_add(sio)
    lollms_webui_generation_events_add(sio)
    lollms_webui_discussion_events_add(sio)


    app.mount("/extensions", StaticFiles(directory=Path(__file__).parent/"web"/"dist", html=True), name="extensions")
    app.mount("/playground", StaticFiles(directory=Path(__file__).parent/"web"/"dist", html=True), name="playground")
    app.mount("/settings", StaticFiles(directory=Path(__file__).parent/"web"/"dist", html=True), name="settings")
    app.mount("/", StaticFiles(directory=Path(__file__).parent/"web"/"dist", html=True), name="static")
    app = ASGIApp(socketio_server=sio, other_asgi_app=app)

    lollmsElfServer.app = app


    # if autoshow
    if config.auto_show_browser:
        if config['host']=="0.0.0.0":
            webbrowser.open(f"http://localhost:{config['port']}")
            #webbrowser.open(f"http://localhost:{6523}") # needed for debug (to be removed in production)
        else:
            webbrowser.open(f"http://{config['host']}:{config['port']}")
            #webbrowser.open(f"http://{config['host']}:{6523}") # needed for debug (to be removed in production)


    try:
        sio.reboot = False
        #uvicorn.run(app, host=config.host, port=6523)
        uvicorn.run(app, host=config.host, port=config.port)
        if sio.reboot:
            ASCIIColors.info("")
            ASCIIColors.info("")
            ASCIIColors.info("")
            ASCIIColors.info(" ╔══════════════════════════════════════════════════╗")
            ASCIIColors.info(" ║              Restarting backend                  ║")
            ASCIIColors.info(" ╚══════════════════════════════════════════════════╝")
            ASCIIColors.info("")
            ASCIIColors.info("")
            ASCIIColors.info("")
            lollmsElfServer.run_restart_script(args)
            
    except Exception as ex:
        trace_exception(ex)


    