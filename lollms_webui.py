"""
File: lollms_web_ui.py
Author: ParisNeo
Description: Singleton class for the LoLLMS web UI.

This class provides a singleton instance of the LoLLMS web UI, allowing access to its functionality and data across multiple endpoints.
"""

from lollms.server.elf_server import LOLLMSElfServer
from lollms.main_config import LOLLMSConfig
from lollms.helpers import trace_exception
from lollms.paths import LollmsPaths
from ascii_colors import ASCIIColors
from datetime import datetime
from api.db import DiscussionsDB, Discussion
from pathlib import Path

try:
    from lollms.media import WebcamImageSender, AudioRecorder
    Media_on=True
except:
    ASCIIColors.warning("Couldn't load media library.\nYou will not be able to perform any of the media linked operations. please verify the logs and install any required installations")
    Media_on=False


class LOLLMSWebUI(LOLLMSElfServer):
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
        socketio = None
    ):
        if LOLLMSWebUI.__instance is None:
            LOLLMSWebUI(
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
        return LOLLMSWebUI.__instance    
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


        self.busy = False
        self.nb_received_tokens = 0
        
        self.config_file_path = config.file_path
        self.cancel_gen = False

        

        # Keeping track of current discussion and message
        self._current_user_message_id = 0
        self._current_ai_message_id = 0
        self._message_id = 0

        self.db_path = config["db_path"]
        if Path(self.db_path).is_absolute():
            # Create database object
            self.db = DiscussionsDB(self.db_path)
        else:
            # Create database object
            self.db = DiscussionsDB(self.lollms_paths.personal_databases_path/self.db_path)

        # If the database is empty, populate it with tables
        ASCIIColors.info("Checking discussions database... ",end="")
        self.db.create_tables()
        self.db.add_missing_columns()
        ASCIIColors.success("ok")



        # prepare vectorization
        if self.config.data_vectorization_activate and self.config.use_discussions_history:
            try:
                ASCIIColors.yellow("Loading long term memory")
                folder = self.lollms_paths.personal_databases_path/"vectorized_dbs"
                folder.mkdir(parents=True, exist_ok=True)
                self.build_long_term_skills_memory()
                ASCIIColors.yellow("Ready")

            except Exception as ex:
                trace_exception(ex)
                self.long_term_memory = None
        else:
            self.long_term_memory = None

        # This is used to keep track of messages 
        self.download_infos={}
        
        self.connections = {
            0:{
                "current_discussion":None,
                "generated_text":"",
                "cancel_generation": False,          
                "generation_thread": None,
                "processing":False,
                "schedule_for_deletion":False,
                "continuing": False,
                "first_chunk": True,
            }
        }
        if Media_on:
            try:
                self.webcam = WebcamImageSender(socketio,lollmsCom=self)
            except:
                self.webcam = None
            try:
                self.rec_output_folder = lollms_paths.personal_outputs_path/"audio_rec"
                self.rec_output_folder.mkdir(exist_ok=True, parents=True)
                self.summoned = False
                self.audio_cap = AudioRecorder(socketio,self.rec_output_folder/"rt.wav", callback=self.audio_callback,lollmsCom=self)
            except:
                self.audio_cap = None
                self.rec_output_folder = None
        else:
            self.webcam = None
            self.rec_output_folder = None
    # Other methods and properties of the LoLLMSWebUI singleton class
