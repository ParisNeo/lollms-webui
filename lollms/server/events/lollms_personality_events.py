"""
project: lollms
file: lollms_files_events.py
author: ParisNeo
description:
    Events related to socket io personality events

"""
from fastapi import APIRouter, Request
from fastapi import HTTPException
from pydantic import BaseModel
import pkg_resources
from lollms.server.elf_server import LOLLMSElfServer
from lollms.types import SENDER_TYPES
from fastapi.responses import FileResponse
from lollms.binding import BindingBuilder, InstallOption
from ascii_colors import ASCIIColors
from lollms.personality import AIPersonality
from lollms.utilities import load_config, trace_exception, gc, terminate_thread, run_async
from lollms.types import MSG_TYPE
from pathlib import Path
from typing import List
import socketio
from functools import partial
from datetime import datetime
import threading
import os
from lollms.security import check_access
router = APIRouter()
lollmsElfServer = LOLLMSElfServer.get_instance()


# ----------------------------------- events -----------------------------------------
def add_events(sio:socketio):

    @sio.on('get_personality_files')
    def get_personality_files(sid, data):
        client_id = sid
        client = lollmsElfServer.session.get_client(client_id)

        client.generated_text       = ""
        client.cancel_generation    = False

        try:
            lollmsElfServer.personality.setCallback(partial(lollmsElfServer.process_data,client_id = client_id))
        except Exception as ex:
            trace_exception(ex)

    import os
    import imghdr
    import mimetypes

    ALLOWED_EXTENSIONS = {
        'asm', 'avi', 'bat', 'bmp', 'c', 'cpp', 'cs', 'csproj', 'css', 'csv', 'doc', 'docx',
        'gif', 'h', 'hh', 'hpp', 'html', 'ico', 'inc', 'ini', 'java', 'jpeg', 'jpg',
        'js', 'json', 'log', 'lua', 'map', 'md', 'mov', 'mp3', 'mp4', 'pas', 'pdf',
        'php', 'png', 'ppt', 'pptx', 'ps1', 'py', 'rb', 'rtf', 's', 'se', 'sh', 'sln', 'snippet',
        'snippets', 'sql', 'svg', 'sym', 'tif', 'tiff', 'ts', 'txt', 'wav', 'webp',
        'xlsx', 'xls', 'xml', 'yaml', 'yml', "vue"
    }

    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @sio.on('send_file_chunk')
    def send_file_chunk(sid, data):
        ASCIIColors.yellow("Receiving file")
        
        client_id = sid
        client = lollmsElfServer.session.get_client(client_id)

        filename:str = os.path.basename(data['filename'])  # sanitize filename
        filename = filename.lower()
        chunk = data['chunk']
        offset = data['offset']
        is_last_chunk = data['isLastChunk']
        chunk_index = data['chunkIndex']

        if not allowed_file(filename):
            print(f"Invalid file type: {filename}")
            lollmsElfServer.InfoMessage(f"Invalid file type: {filename}")
            return
        ext = filename.split(".")[-1].lower()
        if ext in ["wav", "mp3"]:
            path:Path = client.discussion.discussion_audio_folder
        elif ext in ["png","jpg","jpeg","gif","bmp","svg","webp"]:
            path:Path = client.discussion.discussion_images_folder
        else:
            path:Path = client.discussion.discussion_text_folder

        path.mkdir(parents=True, exist_ok=True)
        file_path:Path = path / filename

        try:
            if chunk_index==0:
                lollmsElfServer.ShowBlockingMessage(f"Receiving File {file_path.name}")
                with open(file_path, 'wb') as file:
                    file.write(chunk)
            else:
                with open(file_path, 'ab') as file:
                    file.write(chunk)
        except Exception as e:
            lollmsElfServer.HideBlockingMessage()
            print(f"Error writing to file: {e}")
            return

        if is_last_chunk:
            lollmsElfServer.success('File received and saved successfully')
            lollmsElfServer.HideBlockingMessage()
            lollmsElfServer.ShowBlockingMessage(f"File received {file_path.name}.\nProcessing the file ...")

            if lollmsElfServer.personality.processor:
                result = client.discussion.add_file(file_path, client, lollmsElfServer.tasks_library, partial(lollmsElfServer.process_data, client_id=client_id))
            else:
                result = client.discussion.add_file(file_path, client, lollmsElfServer.tasks_library, partial(lollmsElfServer.process_data, client_id=client_id))

            ASCIIColors.success('File processed successfully')
            run_async(partial(sio.emit,'file_received', {'status': True, 'filename': filename}))
            lollmsElfServer.HideBlockingMessage()
        else:
            run_async(partial(sio.emit,'request_next_chunk', {'offset': offset + len(chunk)}))


    @sio.on('execute_command')
    def execute_command(sid, data):
        client_id = sid
        client = check_access(lollmsElfServer, client_id)

        lollmsElfServer.cancel_gen = False
        client.generated_text=""
        client.cancel_generation=False
        client.continuing=False
        client.first_chunk=True
        def do_generation():
            if not lollmsElfServer.model:
                ASCIIColors.error("Model not selected. Please select a model")
                lollmsElfServer.error("Model not selected. Please select a model", client_id=client_id)
                return

            if not lollmsElfServer.busy:
                if client.discussion is None:
                    if lollmsElfServer.db.does_last_discussion_have_messages():
                        client.discussion = lollmsElfServer.db.create_discussion()
                    else:
                        client.discussion = lollmsElfServer.db.load_last_discussion()

                ump = lollmsElfServer.config.discussion_prompt_separator + lollmsElfServer.config.user_name.strip() if lollmsElfServer.config.use_user_name_in_discussions else lollmsElfServer.personality.user_message_prefix
                created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')                 
                message = client.discussion.add_message(
                    message_type    = MSG_TYPE.MSG_TYPE_CONTENT.value,
                    sender_type     = SENDER_TYPES.SENDER_TYPES_USER.value,
                    sender          = ump.replace(lollmsElfServer.config.discussion_prompt_separator,"").replace(":",""),
                    content         = "",
                    metadata        = None,
                    steps           = [],
                    parent_message_id=lollmsElfServer.message_id,
                    created_at      = created_at,
                    nb_tokens       = None
                )
                lollmsElfServer.busy=True
                command = data["command"]
                parameters = data["parameters"]
                lollmsElfServer.prepare_reception(client_id)
                if lollmsElfServer.personality.processor is not None:
                    lollmsElfServer.start_time = datetime.now()
                    lollmsElfServer.personality.processor.callback = partial(lollmsElfServer.process_data, client_id=client_id)
                    lollmsElfServer.personality.vectorizer = client.discussion.vectorizer
                    lollmsElfServer.personality.text_files = client.discussion.text_files
                    lollmsElfServer.personality.image_files = client.discussion.image_files
                    lollmsElfServer.personality.audio_files = client.discussion.audio_files
                    
                    lollmsElfServer.personality.processor.execute_command(command, parameters, client)
                else:
                    lollmsElfServer.warning("Non scripted personalities do not support commands",client_id=client_id)
                lollmsElfServer.close_message(client_id)
                lollmsElfServer.busy=False

                #tpe = threading.Thread(target=lollmsElfServer.start_message_generation, args=(message, message_id, client_id))
                #tpe.start()
            else:
                lollmsElfServer.error("I am busy. Come back later.", client_id=client_id)

            lollmsElfServer.busy=False

        client.generation_thread = threading.Thread(target=do_generation)
        client.generation_thread.start()
