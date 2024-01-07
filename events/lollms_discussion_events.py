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
lollmsElfServer = LOLLMSWebUI.get_instance()


# ----------------------------------- events -----------------------------------------
def add_events(sio:socketio):
        @sio.on('new_discussion')
        async def new_discussion(sid, data):   
            ASCIIColors.yellow("New descussion requested")
            client_id = sid
            title = data["title"]
            if lollmsElfServer.connections[client_id]["current_discussion"] is not None:
                if lollmsElfServer.long_term_memory is not None:
                    title, content = lollmsElfServer.connections[client_id]["current_discussion"].export_for_vectorization()
                    skill = lollmsElfServer.learn_from_discussion(title, content)
                    lollmsElfServer.long_term_memory.add_document(title, skill, chunk_size=lollmsElfServer.config.data_vectorization_chunk_size, overlap_size=lollmsElfServer.config.data_vectorization_overlap_size, force_vectorize=False, add_as_a_bloc=False, add_to_index=True)
                    ASCIIColors.yellow("4- Saving database")
                    lollmsElfServer.long_term_memory.save_to_json()
            lollmsElfServer.connections[client_id]["current_discussion"] = lollmsElfServer.db.create_discussion(title)
            # Get the current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Return a success response
            if lollmsElfServer.connections[client_id]["current_discussion"] is None:
                lollmsElfServer.connections[client_id]["current_discussion"] = lollmsElfServer.db.load_last_discussion()
        
            if lollmsElfServer.personality.welcome_message!="":
                if lollmsElfServer.config.force_output_language_to_be and lollmsElfServer.config.force_output_language_to_be.lower().strip() !="english":
                    welcome_message = lollmsElfServer.personality.fast_gen(f"!@>instruction: Translate the following text to {lollmsElfServer.config.force_output_language_to_be.lower()}:\n{lollmsElfServer.personality.welcome_message}\n!@>translation:")
                else:
                    welcome_message = lollmsElfServer.personality.welcome_message

                message = lollmsElfServer.connections[client_id]["current_discussion"].add_message(
                    message_type        = MSG_TYPE.MSG_TYPE_FULL.value if lollmsElfServer.personality.include_welcome_message_in_disucssion else MSG_TYPE.MSG_TYPE_FULL_INVISIBLE_TO_AI.value,
                    sender_type         = SENDER_TYPES.SENDER_TYPES_AI.value,
                    sender              = lollmsElfServer.personality.name,
                    content             = welcome_message,
                    metadata            = None,
                    rank                = 0, 
                    parent_message_id   = -1, 
                    binding             = lollmsElfServer.config.binding_name, 
                    model               = lollmsElfServer.config.model_name,
                    personality         = lollmsElfServer.config.personalities[lollmsElfServer.config.active_personality_id], 
                    created_at=None, 
                    finished_generating_at=None
                )
 
                await lollmsElfServer.socketio.emit('discussion_created',
                            {'id':lollmsElfServer.connections[client_id]["current_discussion"].discussion_id},
                            to=client_id
                )                        
            else:
                await lollmsElfServer.socketio.emit('discussion_created',
                            {'id':0},
                            to=client_id
                )                        

        @sio.on('load_discussion')
        async def load_discussion(sid, data):   
            client_id = sid
            ASCIIColors.yellow(f"Loading discussion for client {client_id} ... ", end="")
            if "id" in data:
                discussion_id = data["id"]
                lollmsElfServer.connections[client_id]["current_discussion"] = Discussion(discussion_id, lollmsElfServer.db)
            else:
                if lollmsElfServer.connections[client_id]["current_discussion"] is not None:
                    discussion_id = lollmsElfServer.connections[client_id]["current_discussion"].discussion_id
                    lollmsElfServer.connections[client_id]["current_discussion"] = Discussion(discussion_id, lollmsElfServer.db)
                else:
                    lollmsElfServer.connections[client_id]["current_discussion"] = lollmsElfServer.db.create_discussion()
            messages = lollmsElfServer.connections[client_id]["current_discussion"].get_messages()
            jsons = [m.to_json() for m in messages]
            await lollmsElfServer.socketio.emit('discussion',
                        jsons,
                        to=client_id
            )
            ASCIIColors.green(f"ok")