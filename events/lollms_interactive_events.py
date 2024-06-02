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
from lollms.utilities import find_first_available_file_index, convert_language_name, PackageManager, run_async, add_period
from lollms.security import forbid_remote_access, check_access
from lollms_webui import LOLLMSWebUI
from pathlib import Path
from typing import List
from functools import partial
import socketio
import threading
import os
import time

from lollms.databases.discussions_database import Discussion
from datetime import datetime

router = APIRouter()
lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()


# ----------------------------------- events -----------------------------------------
def add_events(sio:socketio):
    forbid_remote_access(lollmsElfServer)
    @sio.on('start_webcam_video_stream')
    def start_webcam_video_stream(sid):
        lollmsElfServer.info("Starting video capture")
        try:
            from lollms.media import WebcamImageSender
            lollmsElfServer.webcam = WebcamImageSender(sio,lollmsCom=lollmsElfServer)
            lollmsElfServer.webcam.start_capture()
        except:
            lollmsElfServer.InfoMessage("Couldn't load media library.\nYou will not be able to perform any of the media linked operations. please verify the logs and install any required installations")

    @sio.on('stop_webcam_video_stream')
    def stop_webcam_video_stream(sid):
        lollmsElfServer.info("Stopping video capture")
        lollmsElfServer.webcam.stop_capture()

    @sio.on('start_bidirectional_audio_stream')
    def start_bidirectional_audio_stream(sid):
        client = check_access(lollmsElfServer, sid)
        if lollmsElfServer.config.headless_server_mode:
            return {"status":False,"error":"Start recording is blocked when in headless mode for obvious security reasons!"}

        if lollmsElfServer.config.host!="localhost" and lollmsElfServer.config.host!="127.0.0.1":
            return {"status":False,"error":"Start recording is blocked when the server is exposed outside for very obvious reasons!"}

        lollmsElfServer.info("Starting audio capture")
        if not lollmsElfServer.tts or not lollmsElfServer.stt:
            lollmsElfServer.InfoMessage("TTS or STT are not configured.\nPlease go to settings and configure them first")
            return  {"status":False,"error":"TTS or STT not configured"}

        if not lollmsElfServer.tts.ready or not lollmsElfServer.stt.ready:
            lollmsElfServer.InfoMessage("TTS is not ready yet.\nPlease wait")
            return  {"status":False,"error":"TTS not ready"}

        if lollmsElfServer.rt_com:
            lollmsElfServer.info("audio_mode is already on\nTurning it off")
            lollmsElfServer.info("Stopping audio capture")
            lollmsElfServer.rt_com.stop_recording()
            lollmsElfServer.rt_com = None
            lollmsElfServer.emit_socket_io_info("rtcom_status_changed",{"status":False}, client.client_id)
            return  {"status":False,"error":"Already running"}

        try:
            from lollms.media import RTCom
            lollmsElfServer.rec_output_folder = lollmsElfServer.lollms_paths.personal_outputs_path/"audio_rec"
            lollmsElfServer.rec_output_folder.mkdir(exist_ok=True, parents=True)
            lollmsElfServer.summoned = False
            lollmsElfServer.rt_com = RTCom(
                                                lollmsElfServer, 
                                                lollmsElfServer.sio,
                                                lollmsElfServer.personality,
                                                client=client,
                                                threshold=lollmsElfServer.config.stt_listening_threshold, 
                                                silence_duration=lollmsElfServer.config.stt_silence_duration, 
                                                sound_threshold_percentage=lollmsElfServer.config.stt_sound_threshold_percentage, 
                                                gain=lollmsElfServer.config.stt_gain, 
                                                rate=lollmsElfServer.config.stt_rate, 
                                                channels=lollmsElfServer.config.stt_channels, 
                                                buffer_size=lollmsElfServer.config.stt_buffer_size, 
                                                snd_input_device=lollmsElfServer.config.stt_input_device, 
                                                snd_output_device=lollmsElfServer.config.tts_output_device, 
                                                logs_folder=lollmsElfServer.rec_output_folder,
                                                block_while_talking=True, 
                                                use_keyword_audio=lollmsElfServer.config.stt_activate_word_detection,
                                                keyword_audio_path=lollmsElfServer.config.stt_word_detection_file
                                            )
            lollmsElfServer.rt_com.start_recording()
            lollmsElfServer.emit_socket_io_info("rtcom_status_changed",{"status":True}, client.client_id)
        except Exception as ex:
            trace_exception(ex)
            lollmsElfServer.InfoMessage("Couldn't load media library.\nYou will not be able to perform any of the media linked operations. please verify the logs and install any required installations")
            lollmsElfServer.emit_socket_io_info("rtcom_status_changed",{"status":False}, client.client_id)



    @sio.on('stop_bidirectional_audio_stream')
    def stop_bidirectional_audio_stream(sid):
        client = check_access(lollmsElfServer, sid)
        lollmsElfServer.info("Stopping audio capture")
        lollmsElfServer.rt_com.stop_recording()
        lollmsElfServer.rt_com = None



