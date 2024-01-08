"""
project: lollms
file: lollms_discussion_events.py 
author: ParisNeo
description: 
    This module contains a set of Socketio routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes are specific to discussion operation

"""
from fastapi import APIRouter, Request
from fastapi import HTTPException
from pydantic import BaseModel
import pkg_resources
from lollms.server.elf_server import LOLLMSElfServer
from fastapi.responses import FileResponse
from lollms.binding import BindingBuilder, InstallOption
from ascii_colors import ASCIIColors
from lollms.personality import MSG_TYPE, AIPersonality
from lollms.types import MSG_TYPE, SENDER_TYPES
from lollms.utilities import load_config, trace_exception, gc
from lollms.utilities import find_first_available_file_index, convert_language_name
from lollms_webui import LOLLMSWebUI
from pathlib import Path
from typing import List
import socketio
import threading
import os

from api.db import Discussion
from datetime import datetime

router = APIRouter()
lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()


# ----------------------------------- events -----------------------------------------
def add_events(sio:socketio):
    @sio.on('create_empty_message')
    def create_empty_message(sid, data):
        client_id = sid
        type = data.get("type",0)
        message = data.get("message","")
        if type==0:
            ASCIIColors.info(f"Building empty User message requested by : {client_id}")
            # send the message to the bot
            print(f"Creating an empty message for AI answer orientation")
            if lollmsElfServer.connections[client_id]["current_discussion"]:
                if not lollmsElfServer.model:
                    lollmsElfServer.error("No model selected. Please make sure you select a model before starting generation", client_id = client_id)
                    return          
                lollmsElfServer.new_message(client_id, lollmsElfServer.config.user_name, message, sender_type=SENDER_TYPES.SENDER_TYPES_USER, open=True)
        else:
            if lollmsElfServer.personality is None:
                lollmsElfServer.warning("Select a personality")
                return
            ASCIIColors.info(f"Building empty AI message requested by : {client_id}")
            # send the message to the bot
            print(f"Creating an empty message for AI answer orientation")
            if lollmsElfServer.connections[client_id]["current_discussion"]:
                if not lollmsElfServer.model:
                    lollmsElfServer.error("No model selected. Please make sure you select a model before starting generation", client_id=client_id)
                    return          
                lollmsElfServer.new_message(client_id, lollmsElfServer.personality.name, "[edit this to put your ai answer start]", open=True)