"""
project: lollms
file: lollms_files_events.py 
author: ParisNeo
description: 
    Events related to socket io model events

"""
from fastapi import APIRouter, Request
from fastapi import HTTPException
from pydantic import BaseModel
import pkg_resources
from lollms.server.elf_server import LOLLMSElfServer
from fastapi.responses import FileResponse
from lollms.binding import BindingBuilder, InstallOption
from lollms.security import sanitize_path

from ascii_colors import ASCIIColors
from lollms.personality import AIPersonality
from lollms.utilities import load_config, trace_exception, gc, terminate_thread, run_async
from pathlib import Path
from typing import List
import socketio
from datetime import datetime
from functools import partial
import shutil
import threading
import os

lollmsElfServer = LOLLMSElfServer.get_instance()


# ----------------------------------- events -----------------------------------------
def add_events(sio:socketio):
    @sio.on('install_model')
    def install_model(sid, data):
        client_id = sid
        variant_id = data["variant_id"]
        #sanitize_path(variant_id)
        ASCIIColors.info(f"Received install request for {variant_id} from {client_id}. Starting background thread.")
        # Target the NEW synchronous wrapper method
        tpe = threading.Thread(
            target=lollmsElfServer.binding.install_model_sync_wrapper, # <-- Important change
            args=(variant_id, client_id),
            name=f"InstallThread-{client_id}-{variant_id[:20]}" # Optional: Give thread a useful name
        )
        tpe.daemon = True # Optional: Make thread daemon so it doesn't block exit
        tpe.start()
        ASCIIColors.info(f"Thread {tpe.name} started.")

    @sio.on('uninstall_model')
    def uninstall_model(sid, data):
        variant_id:str = data['variant_id']
        sanitize_path(variant_id)

        model_path = os.path.realpath(data['path'])
        model_type:str=data.get("type","gguf")
        installation_dir = lollmsElfServer.binding.searchModelParentFolder(model_path, model_type)
        
        binding_folder = lollmsElfServer.config["binding_name"]
        if model_type=="gptq" or  model_type=="awq" or  model_type=="exl2":
            filename = model_path.split("/")[4]
            installation_path = installation_dir / filename
        else:
            filename = Path(model_path).name
            installation_path = installation_dir / filename
        model_name = filename

        if not installation_path.exists():
            run_async( partial(sio.emit,'uninstall_progress',{
                                                'status': False,
                                                'error': 'The model does not exist',
                                                'model_name' : model_name,
                                                'binding_folder' : binding_folder
                                            }, room=sid)
            )
        try:
            if not installation_path.exists():
                # Try to find a version


                model_path = installation_path.name.lower().replace("-ggml","").replace("-gguf","")
                candidates = [m for m in installation_dir.iterdir() if model_path in m.name]
                if len(candidates)>0:
                    model_path = candidates[0]
                    installation_path = model_path
                    
            if installation_path.is_dir():
                shutil.rmtree(installation_path)
            else:
                installation_path.unlink()
            run_async( partial(sio.emit,'uninstall_progress',{
                                                'status': True, 
                                                'error': '',
                                                'model_name' : model_name,
                                                'binding_folder' : binding_folder
                                            }, room=sid)
            )
        except Exception as ex:
            trace_exception(ex)
            ASCIIColors.error(f"Couldn't delete {installation_path}, please delete it manually and restart the app")
            run_async( partial(sio.emit,'uninstall_progress',{
                                                'status': False, 
                                                'error': f"Couldn't delete {installation_path}, please delete it manually and restart the app",
                                                'model_name' : model_name,
                                                'binding_folder' : binding_folder
                                            }, room=sid)
            )


    @sio.on('cancel_install')
    def cancel_install(sid,data):
        try:
            model_name = data["model_name"]
            binding_folder = data["binding_folder"]
            model_url = data["model_url"]
            signature = f"{model_name}_{binding_folder}_{model_url}"
            lollmsElfServer.download_infos[signature]["cancel"]=True

            run_async( partial(sio.emit,'canceled', {
                                            'status': True
                                            },
                                            room=sid 
                                ) 
            )           
        except Exception as ex:
            trace_exception(ex)
            run_async( partial(sio.emit,'canceled', {
                                            'status': False,
                                            'error':str(ex)
                                            },
                                            room=sid 
                                )     
            )       
