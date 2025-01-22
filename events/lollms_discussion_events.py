"""
project: lollms
file: lollms_discussion_events.py 
author: ParisNeo
description: 
    This module contains a set of Socketio routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes are specific to discussion operation

"""

import os
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import List

import pkg_resources
import socketio
import yaml
from ascii_colors import ASCIIColors
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from lollms.binding import BindingBuilder, InstallOption
from lollms.databases.discussions_database import Discussion
from lollms.personality import AIPersonality
from lollms.security import forbid_remote_access
from lollms.server.elf_server import LOLLMSElfServer
from lollms.types import MSG_OPERATION_TYPE, SENDER_TYPES
from lollms.utilities import (PackageManager, convert_language_name,
                              find_first_available_file_index, gc, load_config,
                              trace_exception)
from pydantic import BaseModel

from lollms_webui import LOLLMSWebUI

router = APIRouter()
lollmsElfServer = LOLLMSWebUI.get_instance()


# ----------------------------------- events -----------------------------------------
def add_events(sio: socketio):
    forbid_remote_access(lollmsElfServer)

    @sio.on("new_discussion")
    async def new_discussion(sid, data):
        if lollmsElfServer.personality is None:
            lollmsElfServer.error("Please select a personality first")
            return
        ASCIIColors.yellow("New descussion requested")
        client_id = sid
        title = data["title"]
        client = lollmsElfServer.session.get_client(client_id)
        client.discussion = lollmsElfServer.db.create_discussion(title)
        # Get the current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Return a success response
        if lollmsElfServer.session.get_client(client_id).discussion is None:
            lollmsElfServer.session.get_client(client_id).discussion = (
                lollmsElfServer.db.load_last_discussion()
            )

        if lollmsElfServer.personality.welcome_message != "":
            if lollmsElfServer.personality.welcome_audio_path.exists():
                for voice in lollmsElfServer.personality.welcome_audio_path.iterdir():
                    if voice.suffix.lower() in [".wav", ".mp3"]:
                        try:
                            if not PackageManager.check_package_installed("pygame"):
                                PackageManager.install_package("pygame")
                            import pygame

                            pygame.mixer.init()
                            pygame.mixer.music.load(voice)
                            pygame.mixer.music.play()
                        except Exception as ex:
                            pass
            if lollmsElfServer.personality.language:
                default_language = (
                    lollmsElfServer.personality.language.lower().strip().split()[0]
                )
            else:
                default_language = "english"

            current_language = (
                lollmsElfServer.config.current_language.lower().strip().split()[0]
            )

            if (
                lollmsElfServer.config.current_language
                and current_language != default_language
            ):
                language_path = (
                    lollmsElfServer.lollms_paths.personal_configuration_path
                    / "personalities"
                    / lollmsElfServer.personality.name
                    / f"languages_{current_language}.yaml"
                )
                if not language_path.exists():
                    # checking if there is already a translation in the personality folder
                    persona_language_path = (
                        lollmsElfServer.lollms_paths.personalities_zoo_path
                        / lollmsElfServer.personality.category
                        / lollmsElfServer.personality.name.replace(" ", "_")
                        / "languages"
                        / f"{current_language}.yaml"
                    )
                    if persona_language_path.exists():
                        shutil.copy(persona_language_path, language_path)
                        with open(
                            language_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            language_pack = yaml.safe_load(f)
                            conditionning = language_pack["personality_conditioning"]
                    else:
                        lollmsElfServer.ShowBlockingMessage(
                            f"This is the first time this personality speaks {current_language}\nLollms is reconditionning the persona in that language.\nThis will be done just once. Next time, the personality will speak {current_language} out of the box"
                        )
                        language_path.parent.mkdir(exist_ok=True, parents=True)
                        # Translating
                        conditionning = (
                            lollmsElfServer.tasks_library.translate_conditionning(
                                lollmsElfServer.personality._personality_conditioning,
                                lollmsElfServer.personality.language,
                                current_language,
                            )
                        )
                        welcome_message = (
                            lollmsElfServer.tasks_library.translate_message(
                                lollmsElfServer.personality.welcome_message,
                                lollmsElfServer.personality.language,
                                current_language,
                            )
                        )
                        with open(
                            language_path, "w", encoding="utf-8", errors="ignore"
                        ) as f:
                            yaml.safe_dump(
                                {
                                    "personality_conditioning": conditionning,
                                    "welcome_message": welcome_message,
                                },
                                f,
                            )
                        lollmsElfServer.HideBlockingMessage()
                else:
                    with open(
                        language_path, "r", encoding="utf-8", errors="ignore"
                    ) as f:
                        language_pack = yaml.safe_load(f)
                        welcome_message = language_pack.get(
                            "welcome_message",
                            lollmsElfServer.personality.welcome_message,
                        )
            else:
                welcome_message = lollmsElfServer.personality.welcome_message

            if lollmsElfServer.personality.processor:
                lollmsElfServer.ShowBlockingMessage(
                    "Building custom welcome message.\nPlease standby."
                )
                try:
                    welcome_message = lollmsElfServer.personality.processor.get_welcome(
                        welcome_message, client
                    )
                    if welcome_message is None:
                        welcome_message = lollmsElfServer.personality.welcome_message
                except Exception as ex:
                    trace_exception(ex)
                lollmsElfServer.HideBlockingMessage()

            try:
                nb_tokens = len(lollmsElfServer.model.tokenize(welcome_message))
            except:
                nb_tokens = None
                
            message = lollmsElfServer.session.get_client(
                client_id
            ).discussion.add_message(
                message_type=(
                    MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT.value
                    if lollmsElfServer.personality.include_welcome_message_in_discussion
                    else MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI.value
                ),
                sender_type=SENDER_TYPES.SENDER_TYPES_AI.value,
                sender=lollmsElfServer.personality.name,
                content=welcome_message,
                steps=[],
                metadata=None,
                rank=0,
                parent_message_id=-1,
                binding=lollmsElfServer.config.binding_name,
                model=lollmsElfServer.config.model_name,
                personality=lollmsElfServer.config.personalities[
                    lollmsElfServer.config.active_personality_id
                ],
                created_at=None,
                started_generating_at=None,
                finished_generating_at=None,
                nb_tokens=nb_tokens,
            )

            await lollmsElfServer.sio.emit(
                "discussion_created",
                {
                    "id": lollmsElfServer.session.get_client(
                        client_id
                    ).discussion.discussion_id
                },
                to=client_id,
            )
        else:
            await lollmsElfServer.sio.emit(
                "discussion_created",
                {
                    "id": lollmsElfServer.session.get_client(
                        client_id
                    ).discussion.discussion_id
                },
                to=client_id,
            )

    @sio.on("load_discussion")
    async def load_discussion(sid, data):
        client_id = sid
        ASCIIColors.yellow(f"Loading discussion for client {client_id} ... ", end="")
        if "id" in data:
            discussion_id = data["id"]
            lollmsElfServer.session.get_client(client_id).discussion = Discussion(
                lollmsElfServer, discussion_id, lollmsElfServer.db
            )
        else:
            if lollmsElfServer.session.get_client(client_id).discussion is not None:
                discussion_id = lollmsElfServer.session.get_client(
                    client_id
                ).discussion.discussion_id
                lollmsElfServer.session.get_client(client_id).discussion = Discussion(
                    lollmsElfServer, discussion_id, lollmsElfServer.db
                )
            else:
                lollmsElfServer.session.get_client(client_id).discussion = (
                    lollmsElfServer.db.create_discussion()
                )
        messages = lollmsElfServer.session.get_client(
            client_id
        ).discussion.get_messages()
        jsons = [m.to_json() for m in messages]
        await lollmsElfServer.sio.emit("discussion", jsons, to=client_id)
        ASCIIColors.green(f"ok")
