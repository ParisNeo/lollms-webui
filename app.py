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
import threading
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from fastapi.encoders import jsonable_encoder
import socket
import psutil

def get_ip_addresses():
    hostname = socket.gethostname()    
    ip_addresses = [socket.gethostbyname(hostname)]

    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        for address in interface_addresses:
            if str(address.family) == 'AddressFamily.AF_INET':
                ip_addresses.append(address.address)

    return ip_addresses

app = FastAPI(title="LoLLMS", description="This is the LoLLMS-Webui API documentation")



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

    if config.debug_log_file_path!="":
        ASCIIColors.log_path = config.debug_log_file_path
    if args.host:
        config.host=args.host
    if args.port:
        config.port=args.port

    cert_file_path = lollms_paths.personal_certificates/"cert.pem"
    key_file_path = lollms_paths.personal_certificates/"key.pem"
    if os.path.exists(cert_file_path) and os.path.exists(key_file_path):
        is_https = True
    else:
        is_https = False        

    # Create a Socket.IO server
    if config["host"]!="localhost":
        if config["host"]!="0.0.0.0":
            config.allowed_origins.append(f"https://{config['host']}:{config['port']}" if is_https else f"http://{config['host']}:{config['port']}")
        else:
            config.allowed_origins += [f"https://{ip}:{config['port']}" if is_https else f"http://{ip}:{config['port']}" for ip in get_ip_addresses()]
    allowed_origins = config.allowed_origins+[f"https://localhost:{config['port']}" if is_https else f"http://localhost:{config['port']}"]
    sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=allowed_origins, ping_timeout=1200, ping_interval=30)  # Enable CORS for selected origins

    LOLLMSWebUI.build_instance(config=config, lollms_paths=lollms_paths, args=args, sio=sio)
    lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()
    lollmsElfServer.verbose = True


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
    from lollms.server.endpoints.lollms_skills_library import router as lollms_skills_library_router

    from lollms.server.endpoints.lollms_user import router as lollms_user_router
    from lollms.server.endpoints.lollms_xtts import router as lollms_xtts_add_router
    from lollms.server.endpoints.lollms_sd import router as lollms_sd_router    
    from lollms.server.endpoints.lollms_ollama import router as lollms_ollama_router    
    from lollms.server.endpoints.lollms_vllm import router as lollms_vllm_router    
    from lollms.server.endpoints.lollms_motion_ctrl import router as lollms_motion_ctrl_router

    from endpoints.lollms_webui_infos import router as lollms_webui_infos_router
    from lollms.server.endpoints.lollms_discussion import router as lollms_discussion_router
    from endpoints.lollms_message import router as lollms_message_router
    from endpoints.lollms_advanced import router as lollms_advanced_router
    from endpoints.chat_bar import router as chat_bar_router
    from lollms.server.endpoints.lollms_petals import router as lollms_petals_router    
    
    from endpoints.lollms_playground import router as lollms_playground_router    
    


    from lollms.server.events.lollms_generation_events import add_events as lollms_generation_events_add
    from lollms.server.events.lollms_personality_events import add_events as lollms_personality_events_add
    from lollms.server.events.lollms_files_events import add_events as lollms_files_events_add
    from lollms.server.events.lollms_model_events import add_events as lollms_model_events_add
    from lollms.server.events.lollms_rag_events import add_events as lollms_rag_events_add
    


    from events.lollms_generation_events import add_events as lollms_webui_generation_events_add
    from events.lollms_discussion_events import add_events as lollms_webui_discussion_events_add
    from events.lollms_chatbox_events import add_events as lollms_chatbox_events_add
    from events.lollms_interactive_events import add_events as lollms_interactive_events_add


    # endpoints for remote access
    app.include_router(lollms_generator_router)

    # Endpoints reserved for local access    
    if (not config.headless_server_mode) or config.force_accept_remote_access: # Be aware that forcing force_accept_remote_access can expose the server to attacks 
        app.include_router(lollms_infos_router)
        app.include_router(lollms_binding_files_server_router)
        app.include_router(lollms_hardware_infos_router)    
        app.include_router(lollms_binding_infos_router)
        app.include_router(lollms_models_infos_router)   
        app.include_router(lollms_personalities_infos_router)   
        app.include_router(lollms_extensions_infos_router)   
        app.include_router(lollms_skills_library_router)   
        
        app.include_router(lollms_webui_infos_router)
        app.include_router(lollms_discussion_router)
        app.include_router(lollms_message_router)
        app.include_router(lollms_user_router)
        app.include_router(lollms_advanced_router)
        app.include_router(chat_bar_router)
        app.include_router(lollms_xtts_add_router)
        
        app.include_router(lollms_sd_router)   
        app.include_router(lollms_ollama_router)  
        app.include_router(lollms_petals_router)  
        app.include_router(lollms_vllm_router)  
        app.include_router(lollms_motion_ctrl_router)  
        
        
        app.include_router(lollms_playground_router)   
        app.include_router(lollms_configuration_infos_router)
    



    @sio.event
    async def disconnect(sid):
        ASCIIColors.yellow(f"Disconnected: {sid}")

    @sio.event
    async def message(sid, data):
        ASCIIColors.yellow(f"Message from {sid}: {data}")
        await sio.send(sid, "Message received!")


    lollms_generation_events_add(sio)
    lollms_personality_events_add(sio)
    lollms_files_events_add(sio)
    lollms_model_events_add(sio)
    lollms_rag_events_add(sio)

    lollms_webui_generation_events_add(sio)
    lollms_webui_discussion_events_add(sio)
    lollms_chatbox_events_add(sio)
    lollms_interactive_events_add(sio)


    app.mount("/extensions", StaticFiles(directory=Path(__file__).parent/"web"/"dist", html=True), name="extensions")
    app.mount("/playground", StaticFiles(directory=Path(__file__).parent/"web"/"dist", html=True), name="playground")
    app.mount("/settings", StaticFiles(directory=Path(__file__).parent/"web"/"dist", html=True), name="settings")
    app.mount("/", StaticFiles(directory=Path(__file__).parent/"web"/"dist", html=True), name="static")


    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        print(f"Error: {exc.errors()}")  # Print the validation error details
        return JSONResponse(
            status_code=422,
            content=jsonable_encoder({"detail": exc.errors(), "body": await exc.body}),  # Send the error details and the original request body
        )

    app = ASGIApp(socketio_server=sio, other_asgi_app=app)



    lollmsElfServer.app = app

    try:
        sio.reboot = False
        # if config.enable_lollms_service:
        #     ASCIIColors.yellow("Starting Lollms service")
        #     #uvicorn.run(app, host=config.host, port=6523)
        #     def run_lollms_server():
        #         parts = config.lollms_base_url.split(":")
        #         host = ":".join(parts[0:2])
        #         port = int(parts[2])
        #         uvicorn.run(app, host=host, port=port)
            # New thread
        #     thread = threading.Thread(target=run_lollms_server)

            # start thread
        #   thread.start()

        # if autoshow


        if config.auto_show_browser and not config.headless_server_mode:
            if config['host']=="0.0.0.0":
                webbrowser.open(f"https://localhost:{config['port']}" if is_https else f"http://localhost:{config['port']}")
                #webbrowser.open(f"http://localhost:{6523}") # needed for debug (to be removed in production)
            else:
                webbrowser.open(f"https://{config['host']}:{config['port']}" if is_https else f"http://{config['host']}:{config['port']}")
                #webbrowser.open(f"http://{config['host']}:{6523}") # needed for debug (to be removed in production)
                
        if is_https:
            uvicorn.run(app, host=config.host, port=config.port, ssl_certfile=cert_file_path, ssl_keyfile=key_file_path)
        else:
            uvicorn.run(app, host=config.host, port=config.port)
           
    except Exception as ex:
        trace_exception(ex)


    
