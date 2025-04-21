"""
project: lollms
file: lollms_generation_events.py 
author: ParisNeo
description: 
    This module contains a set of Socketio routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes are specific to text generation operation

"""

import os
import threading
from datetime import datetime
from pathlib import Path
from typing import List

import pkg_resources
import socketio
from ascii_colors import ASCIIColors
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from lollms.binding import BindingBuilder, InstallOption
from lollms.personality import AIPersonality
from lollms.security import forbid_remote_access
from lollms.server.elf_server import LOLLMSElfServer
from lollms.types import MSG_OPERATION_TYPE, SENDER_TYPES
from lollms.utilities import (convert_language_name,
                              find_first_available_file_index, gc, load_config,
                              trace_exception)
from pydantic import BaseModel

from lollms_webui import LOLLMSWebUI

router = APIRouter()
lollmsElfServer = LOLLMSWebUI.get_instance()


# ----------------------------------- events -----------------------------------------
def add_events(sio: socketio):
    forbid_remote_access(lollmsElfServer)
    @sio.on('cancel_generation')
    async def cancel_generation(sid):
        client_id = sid
        client = lollmsElfServer.session.get_client(client_id)
        lollmsElfServer.model.stop_generation()
        lollmsElfServer.cancel_gen = True
        #kill thread
        ASCIIColors.error(f'Client {sid} requested cancelling generation')
        try:
            client.generation_routine.cancel()
        except Exception as ex:
            pass
        lollmsElfServer.busy=False
        if lollmsElfServer.tts:
            lollmsElfServer.tts.stop()
        
        ASCIIColors.error(f'Client {sid} canceled generation')
    
    
    @sio.on('cancel_text_generation')
    async def cancel_text_generation(sid, data):
        client_id = sid
        client = lollmsElfServer.session.get_client(client_id)
        client.requested_stop=True
        print(f"Client {client_id} requested canceling generation")
        await lollmsElfServer.sio.emit("generation_canceled", {"message":"Generation is canceled."}, to=client_id)
        lollmsElfServer.busy = False


    @sio.on("generate_msg")
    async def handle_generate_msg(sid, data, use_threading=True):
        client_id = sid
        lollmsElfServer.cancel_gen = False
        client = lollmsElfServer.session.get_client(client_id)

        client.generated_text = ""
        client.cancel_generation = False
        client.continuing = False
        client.first_chunk = True

        if not lollmsElfServer.model:
            ASCIIColors.error("Model not selected. Please select a model")
            lollmsElfServer.error(
                "Model not selected. Please select a model", client_id=client_id
            )
            return

        if not lollmsElfServer.busy:
            if lollmsElfServer.session.get_client(client_id).discussion is None:
                if lollmsElfServer.db.does_last_discussion_have_messages():
                    lollmsElfServer.session.get_client(client_id).discussion = (
                        lollmsElfServer.db.create_discussion()
                    )
                else:
                    lollmsElfServer.session.get_client(client_id).discussion = (
                        lollmsElfServer.db.load_last_discussion()
                    )

            prompt = data["prompt"]
            ump = lollmsElfServer.config.user_name.strip() if lollmsElfServer.config.use_user_name_in_discussions else lollmsElfServer.personality.user_message_prefix
            await lollmsElfServer.new_message(client_id = client_id,sender= ump, content= prompt, message_type= MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT, sender_type= SENDER_TYPES.SENDER_TYPES_USER)
            message = await lollmsElfServer.new_message(client_id, lollmsElfServer.personality.name, "", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT, SENDER_TYPES.SENDER_TYPES_AI)

            ASCIIColors.green(
                "Starting message generation by " + lollmsElfServer.personality.name
            )

            await lollmsElfServer.start_message_generation(message, message.id, client_id)
        else:
            lollmsElfServer.error("I am busy. Come back later.", client_id=client_id)

    @sio.on("generate_msg_with_internet")
    async def generate_msg_with_internet(sid, data):
        client_id = sid
        lollmsElfServer.cancel_gen = False
        client = lollmsElfServer.session.get_client(client_id)

        client.generated_text = ""
        client.cancel_generation = False
        client.continuing = False
        client.first_chunk = True

        if not lollmsElfServer.model:
            ASCIIColors.error("Model not selected. Please select a model")
            lollmsElfServer.error(
                "Model not selected. Please select a model", client_id=client_id
            )
            return

        if not lollmsElfServer.busy:
            if lollmsElfServer.session.get_client(client_id).discussion is None:
                if lollmsElfServer.db.does_last_discussion_have_messages():
                    lollmsElfServer.session.get_client(client_id).discussion = (
                        lollmsElfServer.db.create_discussion()
                    )
                else:
                    lollmsElfServer.session.get_client(client_id).discussion = (
                        lollmsElfServer.db.load_last_discussion()
                    )

            prompt = data["prompt"]
            try:
                nb_tokens = len(lollmsElfServer.model.tokenize(prompt))
            except:
                nb_tokens = None
            ump = lollmsElfServer.config.user_name.strip() if lollmsElfServer.config.use_user_name_in_discussions else lollmsElfServer.personality.user_message_prefix
            await lollmsElfServer.new_message(client_id = client_id,sender= ump, content= prompt, message_type= MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT, sender_type= SENDER_TYPES.SENDER_TYPES_USER)
            message = await lollmsElfServer.new_message(client_id, lollmsElfServer.personality.name, "", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT, SENDER_TYPES.SENDER_TYPES_AI)

            ASCIIColors.green(
                "Starting message generation by " + lollmsElfServer.personality.name
            )

            await lollmsElfServer.start_message_generation(message, message.id, client_id, force_using_internet=True)

        else:
            lollmsElfServer.error("I am busy. Come back later.", client_id=client_id)

    @sio.on("generate_msg_from")
    async def handle_generate_msg_from(sid, data):
        client_id = sid
        client = lollmsElfServer.session.get_client(client_id)
        lollmsElfServer.cancel_gen = False
        client.continuing = False
        client.first_chunk = True

        if lollmsElfServer.session.get_client(client_id).discussion is None:
            ASCIIColors.warning("Please select a discussion")
            lollmsElfServer.error(
                "Please select a discussion first", client_id=client_id
            )
            return
        id_ = data["id"]
        generation_type = data.get("msg_type", None)
        if id_ == -1:
            message = client.discussion.messages[-1]
        else:
            message = client.discussion.load_message(id_)
        if message is None:
            return
        await lollmsElfServer.new_message(client_id, lollmsElfServer.personality.name, "", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT, SENDER_TYPES.SENDER_TYPES_AI)
        await lollmsElfServer.start_message_generation(message, message.id, client_id, False, generation_type)

    @sio.on("continue_generate_msg_from")
    async def handle_continue_generate_msg_from(sid, data):
        client_id = sid
        client = lollmsElfServer.session.get_client(client_id)
        lollmsElfServer.cancel_gen = False
        client.continuing = True
        client.first_chunk = True

        if lollmsElfServer.session.get_client(client_id).discussion is None:
            ASCIIColors.yellow("Please select a discussion")
            lollmsElfServer.error("Please select a discussion", client_id=client_id)
            return
        id_ = data["id"]
        if id_ == -1:
            message = lollmsElfServer.session.get_client(
                client_id
            ).discussion.current_message
        else:
            message = lollmsElfServer.session.get_client(
                client_id
            ).discussion.load_message(id_)

        client.generated_text = message.content
        await lollmsElfServer.start_message_generation(message, message.id, client_id, True)

    # add functions to lollm
    lollmsElfServer.handle_generate_msg = handle_generate_msg
    lollmsElfServer.generate_msg_with_internet = generate_msg_with_internet
    lollmsElfServer.handle_generate_msg_from = handle_generate_msg_from
    lollmsElfServer.handle_continue_generate_msg_from = handle_continue_generate_msg_from
