"""
File: lollms_web_ui.py
Author: ParisNeo
Description: Singleton class for the LoLLMS web UI.

This class provides a singleton instance of the LoLLMS web UI, allowing access to its functionality and data across multiple endpoints.
"""

from lollms.app import LollmsApplication
from lollms.main_config import LOLLMSConfig
from lollms.paths import LollmsPaths
from lollms.personality import AIPersonality
from pathlib import Path
from socketio import AsyncServer
from functools import partial
from lollms.utilities import trace_exception, run_async

from datetime import datetime
class LOLLMSElfServer(LollmsApplication):
    __instance = None

    @staticmethod
    def build_instance(
        config: LOLLMSConfig,
        lollms_paths: LollmsPaths,
        load_binding=True,
        load_model=True,
        load_voice_service=True,
        load_sd_service=True,
        try_select_binding=False,
        try_select_model=False,
        callback=None,
        sio:AsyncServer = None
    ):
        if LOLLMSElfServer.__instance is None:
            LOLLMSElfServer(
                config,
                lollms_paths,
                load_binding=load_binding,
                load_model=load_model,
                load_sd_service=load_sd_service,
                load_voice_service=load_voice_service,
                try_select_binding=try_select_binding,
                try_select_model=try_select_model,
                callback=callback,
                sio=sio
            )
        return LOLLMSElfServer.__instance
    @staticmethod
    def get_instance()->'LOLLMSElfServer':
        return LOLLMSElfServer.__instance

    def __init__(
        self,
        config: LOLLMSConfig,
        lollms_paths: LollmsPaths,
        load_binding=True,
        load_model=True,
        load_voice_service=True,  
        load_sd_service=True, 
        try_select_binding=False,
        try_select_model=False,
        callback=None,
        sio:AsyncServer=None
    ) -> None:
        super().__init__(
            "LOLLMSElfServer",
            config,
            lollms_paths,
            load_binding=load_binding,
            load_model=load_model,
            try_select_binding=try_select_binding,
            try_select_model=try_select_model,
            callback=callback,
            sio=sio
        )
        if LOLLMSElfServer.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            LOLLMSElfServer.__instance = self

    # Other methods and properties of the LoLLMSWebUI singleton class
    def find_extension(self, path:Path, filename:str, exts:list)->Path:
        for ext in exts:
            full_path = path/(filename+ext)
            if full_path.exists():
                return full_path
        return None



    async def notify_model_install(self, 
                            installation_path,
                            model_name,
                            binding_folder,
                            model_url,
                            start_time,
                            total_size,
                            downloaded_size,
                            progress,
                            speed,
                            client_id,
                            status=True,
                            error="",
                             ):
        await self.sio.emit('install_progress',{
                                            'status': status,
                                            'error': error,
                                            'model_name' : model_name,
                                            'binding_folder' : binding_folder,
                                            'model_url' : model_url,
                                            'start_time': start_time,
                                            'total_size': total_size,
                                            'downloaded_size': downloaded_size,
                                            'progress': progress,
                                            'speed': speed,
                                        }, room=client_id
        )
