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
import os, sys
# The current version of the webui
lollms_webui_version="9.0 (alpha)"

import git

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
        self.version= lollms_webui_version


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
    def check_module_update_(self, repo_path, branch_name="main"):
        try:
            # Open the repository
            ASCIIColors.yellow(f"Checking for updates from {repo_path}")
            repo = git.Repo(repo_path)
            
            # Fetch updates from the remote for the specified branch
            repo.remotes.origin.fetch(refspec=f"refs/heads/{branch_name}:refs/remotes/origin/{branch_name}")
            
            # Compare the local and remote commit IDs for the specified branch
            local_commit = repo.head.commit
            remote_commit = repo.remotes.origin.refs[branch_name].commit
            
            # Check if the local branch is behind the remote branch
            is_behind = repo.is_ancestor(local_commit, remote_commit) and local_commit!= remote_commit
            
            ASCIIColors.yellow(f"update availability: {is_behind}")
            
            # Return True if the local branch is behind the remote branch
            return is_behind
        except Exception as e:
            # Handle any errors that may occur during the fetch process
            # trace_exception(e)
            return False        
            
    def check_update_(self, branch_name="main"):
        try:
            # Open the repository
            repo_path = str(Path(__file__).parent)
            if self.check_module_update_(repo_path, branch_name):
                return True
            repo_path = str(Path(__file__).parent/"lollms_core")
            if self.check_module_update_(repo_path, branch_name):
                return True
            repo_path = str(Path(__file__).parent/"utilities/safe_store")
            if self.check_module_update_(repo_path, branch_name):
                return True
            return False
        except Exception as e:
            # Handle any errors that may occur during the fetch process
            # trace_exception(e)
            return False
                    
    def run_update_script(self, args=None):
        update_script = Path(__file__).parent/"update_script.py"

        # Convert Namespace object to a dictionary
        if args:
            args_dict = vars(args)
        else:
            args_dict = {}
        # Filter out any key-value pairs where the value is None
        valid_args = {key: value for key, value in args_dict.items() if value is not None}

        # Save the arguments to a temporary file
        temp_file = Path(__file__).parent/"temp_args.txt"
        with open(temp_file, "w") as file:
            # Convert the valid_args dictionary to a string in the format "key1 value1 key2 value2 ..."
            arg_string = " ".join([f"--{key} {value}" for key, value in valid_args.items()])
            file.write(arg_string)

        os.system(f"python {update_script}")
        sys.exit(0)