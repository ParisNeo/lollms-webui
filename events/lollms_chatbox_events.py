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
from lollms.utilities import find_first_available_file_index, convert_language_name, PackageManager, run_async
from lollms_webui import LOLLMSWebUI
from pathlib import Path
from typing import List
from functools import partial
import socketio
import threading
import os
import time

from lollms.internet import scrape_and_save
from lollms.databases.discussions_database import Discussion
from lollms.security import forbid_remote_access
from datetime import datetime

router = APIRouter()
lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()


# ----------------------------------- events -----------------------------------------
def add_events(sio:socketio):
    forbid_remote_access(lollmsElfServer)
    @sio.on('create_empty_message')
    def create_empty_message(sid, data):
        client_id = sid
        type = int(data.get("type",0))
        message = data.get("message","")
        if type==0:
            ASCIIColors.info(f"Building empty User message requested by : {client_id}")
            # send the message to the bot
            print(f"Creating an empty message for AI answer orientation")
            if lollmsElfServer.session.get_client(client_id).discussion:
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
            if lollmsElfServer.session.get_client(client_id).discussion:
                if not lollmsElfServer.model:
                    lollmsElfServer.error("No model selected. Please make sure you select a model before starting generation", client_id=client_id)
                    return          
                lollmsElfServer.new_message(client_id, lollmsElfServer.personality.name, "[edit this to put your ai answer start]", open=True)


    @sio.on('add_webpage')
    def add_webpage(sid, data):
        lollmsElfServer.ShowBlockingMessage("Scraping web page\nPlease wait...")
        ASCIIColors.yellow("Scaping web page")
        client = lollmsElfServer.session.get_client(sid)
        url = data['url']
        index =  find_first_available_file_index(lollmsElfServer.lollms_paths.personal_uploads_path,"web_",".txt")
        file_path=lollmsElfServer.lollms_paths.personal_uploads_path/f"web_{index}.txt"
        scrape_and_save(url=url, file_path=file_path)
        try:
            if not lollmsElfServer.personality.processor is None:
                lollmsElfServer.personality.processor.add_file(file_path, client, partial(lollmsElfServer.process_chunk, client_id = sid))
                # File saved successfully
                run_async(partial(sio.emit,'web_page_added', {'status':True,}))
            else:
                lollmsElfServer.personality.add_file(file_path, client, partial(lollmsElfServer.process_chunk, client_id = sid))
                # File saved successfully
                run_async(partial(sio.emit,'web_page_added', {'status':True}))
            lollmsElfServer.HideBlockingMessage()
        except Exception as e:
            # Error occurred while saving the file
            run_async(partial(sio.emit,'web_page_added', {'status':False}))
            lollmsElfServer.HideBlockingMessage()

    @sio.on('take_picture')
    def take_picture(sid):
        try:
            client = lollmsElfServer.session.get_client(sid)
            lollmsElfServer.info("Loading camera")
            if not PackageManager.check_package_installed("cv2"):
                PackageManager.install_package("opencv-python")
            import cv2
            cap = cv2.VideoCapture(0)
            n = time.time()
            lollmsElfServer.info("Stand by for taking a shot in 2s")
            while(time.time()-n<2):
                _, frame = cap.read()
            _, frame = cap.read()
            cap.release()
            lollmsElfServer.info("Shot taken")
            cam_shot_path = client.discussion.discussion_images_folder
            cam_shot_path.mkdir(parents=True, exist_ok=True)
            filename = find_first_available_file_index(cam_shot_path, "cam_shot_", extension=".png")
            save_path = cam_shot_path/f"cam_shot_{filename}.png"  # Specify the desired folder path

            try:
                cv2.imwrite(str(save_path), frame)
                if not lollmsElfServer.personality.processor is None:
                    lollmsElfServer.info("Sending file to scripted persona")
                    lollmsElfServer.personality.processor.add_file(save_path, client, partial(lollmsElfServer.process_chunk, client_id = sid))
                    # File saved successfully
                    run_async(partial(sio.emit,'picture_taken', {'status':True, 'progress': 100}))
                    lollmsElfServer.info("File sent to scripted persona")
                else:
                    lollmsElfServer.info("Sending file to persona")
                    lollmsElfServer.personality.add_file(save_path, client, partial(lollmsElfServer.process_chunk, client_id = sid))
                    # File saved successfully
                    run_async(partial(sio.emit,'picture_taken', {'status':True, 'progress': 100}))
                    lollmsElfServer.info("File sent to persona")
            except Exception as e:
                trace_exception(e)
                # Error occurred while saving the file
                run_async(partial(sio.emit,'picture_taken', {'status':False, 'error': str(e)}))
                

        except Exception as ex:
            trace_exception(ex)
            lollmsElfServer.error("Couldn't use the webcam")
