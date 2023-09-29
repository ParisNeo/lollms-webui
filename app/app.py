######
# Project       : lollms-webui
# Author        : ParisNeo with the help of the community
# Supported by Nomic-AI
# license       : Apache 2.0
# Description   : 
# A front end Flask application for llamacpp models.
# The official LOLLMS Web ui
# Made by the community for the community
######

__author__ = "parisneo"
__github__ = "https://github.com/ParisNeo/lollms-webui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

__version__ ="6.5"

main_repo = "https://github.com/ParisNeo/lollms-webui.git"
import os
import sys
from flask import request, jsonify
import io
import sys
import time
import traceback
import webbrowser
import logging
from pathlib import Path
import json
import traceback
from flask_socketio import SocketIO
import yaml
from geventwebsocket.handler import WebSocketHandler
import logging

import socket
from flask import (
    Flask,
    jsonify,
    request,
)

from lollms.helpers import ASCIIColors, trace_exception


try:
    import mimetypes
    mimetypes.add_type('application/javascript', '.js')
    mimetypes.add_type('text/css', '.css')    
except:
    ASCIIColors.yellow("Couldn't set mimetype")    
    

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask("Lollms-WebUI", static_url_path="/static", static_folder="static")

#  async_mode='gevent', ping_timeout=1200, ping_interval=120, 
socketio = SocketIO(app,  cors_allowed_origins="*", async_mode='threading',engineio_options={'websocket_compression': False, 'websocket_ping_interval': 20, 'websocket_ping_timeout': 120, 'websocket_max_queue': 100})

app.config['SECRET_KEY'] = 'secret!'
# Set the logging level to WARNING or higher
logging.getLogger('socketio').setLevel(logging.WARNING)
logging.getLogger('engineio').setLevel(logging.WARNING)
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.basicConfig(level=logging.WARNING)

from LoLLMsWebUI_server.config.scripts import (
    get_ip_address, 
    check_update_, 
    run_restart_script,
    sync_cfg,
)

from LoLLMsWebUI_server.big_class import LoLLMsWebUI

if __name__ == "__main__":
    lollms_paths = LollmsPaths.find_paths(force_local=True, custom_default_cfg_path="configs/config.yaml")
    db_folder = lollms_paths.personal_path/"databases"
    db_folder.mkdir(parents=True, exist_ok=True)
    
    # Parsong parameters
    from LoLLMsWebUI_server.config.parser import parser
    from LoLLMsWebUI_server.config.config import make_config
    parser.parse_args()
    config = make_config()
    
    bot = LoLLMsWebUI(args, app, socketio, config, config.file_path, lollms_paths)

    # chong Define custom WebSocketHandler with error handling 
    class CustomWebSocketHandler(WebSocketHandler):
        def handle_error(self, environ, start_response, e):
            # Handle the error here
            print("WebSocket error:", e)
            super().handle_error(environ, start_response, e)

    # chong -add socket server    
    app.config['debug'] = config["debug"]

    if config["debug"]:
        ASCIIColors.info("debug mode:true")    
    else:
        ASCIIColors.info("debug mode:false")
       
    
    url = f'http://{config["host"]}:{config["port"]}'
    if config["host"]!="localhost":
        print(f'Please open your browser and go to http://localhost:{config["port"]} to view the ui')
        ASCIIColors.success(f'This server is visible from a remote PC. use this address http://{get_ip_address()}:{config["port"]}')
    else:
        print(f"Please open your browser and go to {url} to view the ui")

    if config.auto_show_browser:
        webbrowser.open(f"http://{config['host']}:{config['port']}")
    socketio.run(app, host=config["host"], port=config["port"],
                 # prevent error: The Werkzeug web server is not designed to run in production
                 allow_unsafe_werkzeug=True)
    # http_server = WSGIServer((config["host"], config["port"]), app, handler_class=WebSocketHandler)
    # http_server.serve_forever()
