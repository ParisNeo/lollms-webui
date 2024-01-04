"""
File: lollms_web_ui.py
Author: ParisNeo
Description: Singleton class for the LoLLMS web UI.

This class provides a singleton instance of the LoLLMS web UI, allowing access to its functionality and data across multiple endpoints.
"""

from lollms.server.elf_server import LOLLMSElfServer
from lollms.main_config import LOLLMSConfig
from lollms.paths import LollmsPaths

class LOLLMSWebUI(LOLLMSElfServer):
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
        socketio=None
    ) -> None:
        super().__init__(
            config,
            lollms_paths,
            load_binding=load_binding,
            load_model=load_model,
            load_sd_service=load_sd_service,
            load_voice_service=load_voice_service,
            try_select_binding=try_select_binding,
            try_select_model=try_select_model,
            callback=callback,
            socketio=socketio
        )
        self.app_name = "LOLLMSWebUI"

    # Other methods and properties of the LoLLMSWebUI singleton class
