"""
File: lollms_web_ui.py
Author: ParisNeo
Description: Singleton class for the LoLLMS web UI.

This class provides a singleton instance of the LoLLMS web UI, allowing access to its functionality and data across multiple endpoints.
"""

from lollms.server.elf_server import LOLLMSElfServer
from datetime import datetime
from lollms.databases.discussions_database import DiscussionsDB, Discussion
from pathlib import Path
from lollms.config import InstallOption
from lollms.types import MSG_TYPE, MSG_OPERATION_TYPE, MSG_OPERATION_TYPE, CONTENT_OPERATION_TYPES, SENDER_TYPES
from lollms.extension import LOLLMSExtension, ExtensionBuilder
from lollms.personality import AIPersonality, PersonalityBuilder
from lollms.binding import LOLLMSConfig, BindingBuilder, LLMBinding, ModelBuilder, BindingType
from lollms.paths import LollmsPaths
from lollms.helpers import ASCIIColors, trace_exception
from lollms.com import NotificationType, NotificationDisplayType, LoLLMsCom
from lollms.app import LollmsApplication
from lollms.utilities import File64BitsManager, PromptReshaper, PackageManager, find_first_available_file_index, run_async, is_asyncio_loop_running, yes_or_no_input, process_ai_output
from lollms.generation import RECEPTION_MANAGER, ROLE_CHANGE_DECISION, ROLE_CHANGE_OURTPUT
from lollms.client_session import Client
import git
import asyncio
import os


import threading
from tqdm import tqdm 
import traceback
import sys
import gc
import ctypes
from functools import partial
import json
import shutil
import re
import string
import requests
from datetime import datetime
from typing import List, Tuple,Callable, Any
import time
import numpy as np
from lollms.utilities import find_first_available_file_index, convert_language_name

if not PackageManager.check_package_installed("requests"):
    PackageManager.install_package("requests")
if not PackageManager.check_package_installed("bs4"):
    PackageManager.install_package("beautifulsoup4")
import requests

from lollms.internet import scrape_and_save


def terminate_thread(thread):
    if thread:
        if not thread.is_alive():
            ASCIIColors.yellow("Thread not alive")
            return

        thread_id = thread.ident
        exc = ctypes.py_object(SystemExit)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, exc)
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, None)
            del thread
            gc.collect()
            raise SystemError("Failed to terminate the thread.")
        else:
            ASCIIColors.yellow("Canceled successfully")# The current version of the webui

lollms_webui_version="11 code name: Wonder"



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
        args=None,
        sio = None
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
                args=args,
                sio=sio
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
        args=None,
        sio=None
    ) -> None:
        super().__init__(
            config,
            lollms_paths,
            load_binding=load_binding,
            load_model=load_model,
            try_select_binding=try_select_binding,
            try_select_model=try_select_model,
            callback=callback,
            sio=sio
        )
        self.app_name:str = "LOLLMSWebUI"
        self.version:str = lollms_webui_version
        self.args = args


        self.busy = False
        self.nb_received_tokens = 0
        
        self.config_file_path = config.file_path
        self.cancel_gen = False
        
        if self.config.auto_update:
            if self.check_update_():
                ASCIIColors.info("New version found. Updating!")
                self.run_update_script()
        # Keeping track of current discussion and message
        self._current_user_message_id = 0
        self._current_ai_message_id = 0
        self._message_id = 0



        # migrate old databases to new ones:
        databases_path = self.lollms_paths.personal_path/"databases"
        if databases_path.exists() and len([f for f in databases_path.iterdir() if f.suffix==".db"])>0:
            if yes_or_no_input("Old databases have been spotted on your system. Do you want me to migrate them to the new format?"):
                databases_found = False
                for database_path in databases_path.iterdir():
                    if database_path.suffix==".db":
                        ASCIIColors.red(f"Found old discussion database format : {database_path}")
                        ASCIIColors.red(f"Migrating to new format... ",end="")
                        new_db_path = self.lollms_paths.personal_discussions_path/database_path.stem
                        new_db_path.mkdir(exist_ok=True, parents=True)
                        try:
                            shutil.copy(database_path,new_db_path/"database.db")
                            ASCIIColors.green("ok")
                            databases_found = True
                        except Exception as ex:
                            ASCIIColors.warning(ex)
                if databases_found:
                    ASCIIColors.green(f"Databases are migrated from {databases_path} to the new {self.lollms_paths.personal_discussions_path} path")
                    if yes_or_no_input("Databases are migrated to the new format. Do you want me to delete the previous version?"):
                        for database_path in databases_path.iterdir():
                            if database_path.suffix==".db":
                                ASCIIColors.red(f"Deleting {database_path}")
                                database_path.unlink()
        if config["discussion_db_name"].endswith(".db"):
            config["discussion_db_name"]=config["discussion_db_name"].replace(".db","")
            config.save_config()

        self.discussion_db_name = config["discussion_db_name"]

        # Create database object
        self.db = DiscussionsDB(self, self.lollms_paths, self.discussion_db_name)

        # If the database is empty, populate it with tables
        ASCIIColors.info("Checking discussions database... ",end="")
        self.db.create_tables()
        self.db.add_missing_columns()
        ASCIIColors.success("ok")

        # This is used to keep track of messages 
        self.download_infos={}

        # Define a WebSocket event handler
        @sio.event
        async def connect(sid, environ):
            self.session.add_client(sid, sid, self.db.load_last_discussion(), self.db)
            await self.sio.emit('connected', to=sid) 
            ASCIIColors.success(f'Client {sid} connected')

        @sio.event
        def disconnect(sid):
            try:
                self.session.add_client(sid, sid, self.db.load_last_discussion(), self.db)
                if self.session.get_client(sid).processing:
                    self.session.get_client(sid).schedule_for_deletion=True
                else:
                    # Clients are now kept forever
                    pass# self.session.remove_client(sid, sid)
            except Exception as ex:
                pass
            
            ASCIIColors.error(f'Client {sid} disconnected')

        # generation status
        self.generating=False
        ASCIIColors.blue(f"Your personal data is stored here :",end="")
        ASCIIColors.green(f"{self.lollms_paths.personal_path}")

        self.start_servers()

    def get_uploads_path(self, client_id):
        return self.session.get_client(client_id).discussion_path # self.db.discussion_db_path/f'{["discussion"].discussion_id}'
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
            return False
        except Exception as e:
            # Handle any errors that may occur during the fetch process
            # trace_exception(e)
            return False
                    
    def run_update_script(self, args=None):
        # deactivate trust store for github and pip package install
        if 'REQUESTS_CA_BUNDLE' in os.environ:
            del os.environ['REQUESTS_CA_BUNDLE']
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


    def run_restart_script(self, args):
        restart_script = Path(__file__).parent/"restart_script.py"

        # Convert Namespace object to a dictionary
        args_dict = vars(args)

        # Filter out any key-value pairs where the value is None
        valid_args = {key: value for key, value in args_dict.items() if value is not None}

        # Save the arguments to a temporary file
        temp_file = Path(__file__).parent/"temp_args.txt"
        with open(temp_file, "w") as file:
            # Convert the valid_args dictionary to a string in the format "key1 value1 key2 value2 ..."
            arg_string = " ".join([f"--{key} {value}" for key, value in valid_args.items()])
            file.write(arg_string)

        os.system(f"python {restart_script}")
        sys.exit(0)

    def audio_callback(self, text):
        
        if self.summoned:
            client_id = 0
            self.cancel_gen = False
            client = self.session.get_client(client_id)
            client.generated_text=""
            client.cancel_generation=False
            client.continuing=False
            client.first_chunk=True
            
            if not self.model:
                ASCIIColors.error("Model not selected. Please select a model")
                self.error("Model not selected. Please select a model", client_id=client_id)
                return
 
            if not self.busy:
                if client.discussion is None:
                    if self.db.does_last_discussion_have_messages():
                        client.discussion = self.db.create_discussion()
                    else:
                        client.discussion = self.db.load_last_discussion()

                prompt = text
                try:
                    nb_tokens = len(self.model.tokenize(prompt))
                except:
                    nb_tokens = None
                message = client.discussion.add_message(
                    message_type    = MSG_TYPE.MSG_TYPE_CONTENT.value,
                    sender_type     = SENDER_TYPES.SENDER_TYPES_USER.value,
                    sender          = self.config.user_name.strip() if self.config.use_user_name_in_discussions else self.config.user_name,
                    content         = prompt,
                    metadata        = None,
                    parent_message_id=self.message_id,
                    nb_tokens=nb_tokens
                )

                ASCIIColors.green("Starting message generation by "+self.personality.name)
                client.generation_thread = threading.Thread(target=self.start_message_generation, args=(message, message.id, client_id))
                client.generation_thread.start()
                
                self.sio.sleep(0.01)
                ASCIIColors.info("Started generation task")
                self.busy=True
                #tpe = threading.Thread(target=self.start_message_generation, args=(message, message_id, client_id))
                #tpe.start()
            else:
                self.error("I am busy. Come back later.", client_id=client_id)
        else:
            if "lollms" in text.lower():
                self.summoned = True

    # def scrape_and_save(self, url, file_path):
    #     # Send a GET request to the URL
    #     response = requests.get(url)
        
    #     # Parse the HTML content using BeautifulSoup
    #     soup = BeautifulSoup(response.content, 'html.parser')
        
    #     # Find all the text content in the webpage
    #     text_content = soup.get_text()
        
    #     # Remove extra returns and spaces
    #     text_content = ' '.join(text_content.split())
        
    #     # Save the text content as a text file
    #     with open(file_path, 'w', encoding="utf-8") as file:
    #         file.write(text_content)
        
    #     self.info(f"Webpage content saved to {file_path}")







    def rebuild_personalities(self, reload_all=False):
        if reload_all:
            self.mounted_personalities=[]

        loaded = self.mounted_personalities
        loaded_names = [f"{p.category}/{p.personality_folder_name}:{p.selected_language}" if p.selected_language else f"{p.category}/{p.personality_folder_name}" for p in loaded if p is not None]
        mounted_personalities=[]
        ASCIIColors.success(f" ╔══════════════════════════════════════════════════╗ ")
        ASCIIColors.success(f" ║           Building mounted Personalities         ║ ")
        ASCIIColors.success(f" ╚══════════════════════════════════════════════════╝ ")
        to_remove=[]
        for i,personality in enumerate(self.config['personalities']):
            if i==self.config["active_personality_id"]:
                ASCIIColors.red("*", end="")
                ASCIIColors.green(f" {personality}")
            else:
                ASCIIColors.yellow(f" {personality}")
            if personality in loaded_names:
                mounted_personalities.append(loaded[loaded_names.index(personality)])
            else:
                personality_path = f"{personality}" if not ":" in personality else f"{personality.split(':')[0]}"
                try:
                    personality = AIPersonality(personality_path,
                                                self.lollms_paths, 
                                                self.config,
                                                model=self.model,
                                                app=self,
                                                selected_language=personality.split(":")[1] if ":" in personality else None,
                                                run_scripts=True)

                    mounted_personalities.append(personality)
                    if self.config.auto_read and len(personality.audio_samples)>0:
                        try:
                            from lollms.services.xtts.lollms_xtts import LollmsXTTS
                            if self.tts is None:
                                voice=self.config.xtts_current_voice
                                if voice!="main_voice":
                                    voices_folder = self.lollms_paths.custom_voices_path
                                else:
                                    voices_folder = Path(__file__).parent.parent.parent/"services/xtts/voices"

                                self.tts = LollmsXTTS(
                                                        self, 
                                                        voices_folders=[voices_folder, Path(__file__).parent.parent.parent/"services/xtts/voices"],
                                                        freq=self.config.xtts_freq
                                                        )
                            
                        except Exception as ex:
                            trace_exception(ex)
                            self.warning(f"Personality {personality.name} request using custom voice but couldn't load XTTS")
                except Exception as ex:
                    ASCIIColors.error(f"Personality file not found or is corrupted ({personality_path}).\nReturned the following exception:{ex}\nPlease verify that the personality you have selected exists or select another personality. Some updates may lead to change in personality name or category, so check the personality selection in settings to be sure.")
                    ASCIIColors.info("Trying to force reinstall")
                    if self.config["debug"]:
                        print(ex)
                    try:
                        personality = AIPersonality(
                                                    personality_path, 
                                                    self.lollms_paths, 
                                                    self.config, 
                                                    self.model, 
                                                    app = self,
                                                    run_scripts=True,                                                    
                                                    selected_language=personality.split(":")[1] if ":" in personality else None,
                                                    installation_option=InstallOption.FORCE_INSTALL)
                        mounted_personalities.append(personality)
                        if personality.processor:
                            personality.processor.mounted()
                    except Exception as ex:
                        ASCIIColors.error(f"Couldn't load personality at {personality_path}")
                        trace_exception(ex)
                        ASCIIColors.info(f"Unmounting personality")
                        to_remove.append(i)
                        personality = AIPersonality(None,                                                    
                                                    self.lollms_paths, 
                                                    self.config, 
                                                    self.model,
                                                    app=self,
                                                    run_scripts=True,
                                                    installation_option=InstallOption.FORCE_INSTALL)
                        mounted_personalities.append(personality)
                        if personality.processor:
                            personality.processor.mounted()

                        ASCIIColors.info("Reverted to default personality")
        if self.config["active_personality_id"]>=0 and self.config["active_personality_id"]<len(self.config["personalities"]):
            ASCIIColors.success(f'selected model : {self.config["personalities"][self.config["active_personality_id"]]}')
        else:
            ASCIIColors.warning('An error was encountered while trying to mount personality')
        ASCIIColors.success(f" ╔══════════════════════════════════════════════════╗ ")
        ASCIIColors.success(f" ║                      Done                        ║ ")
        ASCIIColors.success(f" ╚══════════════════════════════════════════════════╝ ")
        # Sort the indices in descending order to ensure correct removal
        to_remove.sort(reverse=True)

        # Remove elements from the list based on the indices
        for index in to_remove:
            if 0 <= index < len(mounted_personalities):
                mounted_personalities.pop(index)
                self.config["personalities"].pop(index)
                ASCIIColors.info(f"removed personality {personality_path}")

        if self.config["active_personality_id"]>=len(self.config["personalities"]):
            self.config["active_personality_id"]=0
            
        return mounted_personalities
    

    def rebuild_extensions(self, reload_all=False):
        if reload_all:
            self.mounted_extensions=[]

        loaded = self.mounted_extensions
        loaded_names = [f"{p.category}/{p.extension_folder_name}" for p in loaded]
        mounted_extensions=[]
        ASCIIColors.success(f" ╔══════════════════════════════════════════════════╗ ")
        ASCIIColors.success(f" ║           Building mounted Extensions            ║ ")
        ASCIIColors.success(f" ╚══════════════════════════════════════════════════╝ ")
        to_remove=[]
        for i,extension in enumerate(self.config['extensions']):
            ASCIIColors.yellow(f" {extension}")
            if extension in loaded_names:
                mounted_extensions.append(loaded[loaded_names.index(extension)])
            else:
                extension_path = self.lollms_paths.extensions_zoo_path/f"{extension}" 
                try:
                    extension = ExtensionBuilder().build_extension(extension_path,self.lollms_paths, self)
                    mounted_extensions.append(extension)
                except Exception as ex:
                    ASCIIColors.error(f"Extension file not found or is corrupted ({extension_path}).\nReturned the following exception:{ex}\nPlease verify that the personality you have selected exists or select another personality. Some updates may lead to change in personality name or category, so check the personality selection in settings to be sure.")
                    trace_exception(ex)
                    ASCIIColors.info("Trying to force reinstall")
                    if self.config["debug"]:
                        print(ex)
        ASCIIColors.success(f" ╔══════════════════════════════════════════════════╗ ")
        ASCIIColors.success(f" ║                      Done                        ║ ")
        ASCIIColors.success(f" ╚══════════════════════════════════════════════════╝ ")
        # Sort the indices in descending order to ensure correct removal
        to_remove.sort(reverse=True)

        # Remove elements from the list based on the indices
        for index in to_remove:
            if 0 <= index < len(mounted_extensions):
                mounted_extensions.pop(index)
                self.config["extensions"].pop(index)
                ASCIIColors.info(f"removed personality {extension_path}")

            
        return mounted_extensions
    # ================================== LOLLMSApp

    #properties
    @property
    def message_id(self):
        return self._message_id
    @message_id.setter
    def message_id(self, id):
        self._message_id=id

    @property
    def current_user_message_id(self):
        return self._current_user_message_id
    @current_user_message_id.setter
    def current_user_message_id(self, id):
        self._current_user_message_id=id
        self._message_id = id
    @property
    def current_ai_message_id(self):
        return self._current_ai_message_id
    @current_ai_message_id.setter
    def current_ai_message_id(self, id):
        self._current_ai_message_id=id
        self._message_id = id

    def download_file(self, url, installation_path, callback=None):
        """
        Downloads a file from a URL, reports the download progress using a callback function, and displays a progress bar.

        Args:
            url (str): The URL of the file to download.
            installation_path (str): The path where the file should be saved.
            callback (function, optional): A callback function to be called during the download
                with the progress percentage as an argument. Defaults to None.
        """
        try:
            response = requests.get(url, stream=True)

            # Get the file size from the response headers
            total_size = int(response.headers.get('content-length', 0))

            with open(installation_path, 'wb') as file:
                downloaded_size = 0
                with tqdm(total=total_size, unit='B', unit_scale=True, ncols=80) as progress_bar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                            downloaded_size += len(chunk)
                            if callback is not None:
                                callback(downloaded_size, total_size)
                            progress_bar.update(len(chunk))

            if callback is not None:
                callback(total_size, total_size)

            print("File downloaded successfully")
        except Exception as e:
            print("Couldn't download file:", str(e))



    def clean_string(self, input_string):
        # Remove extra spaces by replacing multiple spaces with a single space
        #cleaned_string = re.sub(r'\s+', ' ', input_string)

        # Remove extra line breaks by replacing multiple consecutive line breaks with a single line break
        cleaned_string = re.sub(r'\n\s*\n', '\n', input_string)
        # Create a string containing all punctuation characters
        punctuation_chars = string.punctuation        
        # Define a regular expression pattern to match and remove non-alphanumeric characters
        #pattern = f'[^a-zA-Z0-9\s{re.escape(punctuation_chars)}]'  # This pattern matches any character that is not a letter, digit, space, or punctuation
        pattern = f'[^a-zA-Z0-9\u00C0-\u017F\s{re.escape(punctuation_chars)}]'
        # Use re.sub to replace the matched characters with an empty string
        cleaned_string = re.sub(pattern, '', cleaned_string)
        return cleaned_string
    
    def make_discussion_title(self, discussion, client_id=None):
        """
        Builds a title for a discussion
        """

        # Get the list of messages
        messages = discussion.get_messages()
        discussion_messages = f"{self.start_header_id_template}instruction{self.end_header_id_template}Create a short title to this discussion\nYour response should only contain the title without any comments.\n"
        discussion_title = f"\n{self.start_header_id_template}Discussion title{self.end_header_id_template}"

        available_space = self.config.ctx_size - 150 - len(self.model.tokenize(discussion_messages))- len(self.model.tokenize(discussion_title))
        # Initialize a list to store the full messages
        full_message_list = []        
        # Accumulate messages until the cumulative number of tokens exceeds available_space
        tokens_accumulated = 0
        # Accumulate messages starting from message_index
        for message in messages:
            # Check if the message content is not empty and visible to the AI
            if message.content != '' and (
                    message.message_type <= MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_USER.value and message.message_type != MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI.value):

                # Tokenize the message content
                message_tokenized = self.model.tokenize(
                    "\n" + self.config.discussion_prompt_separator + message.sender + ": " + message.content.strip())

                # Check if adding the message will exceed the available space
                if tokens_accumulated + len(message_tokenized) > available_space:
                    break

                # Add the tokenized message to the full_message_list
                full_message_list.insert(0, message_tokenized)

                # Update the cumulative number of tokens
                tokens_accumulated += len(message_tokenized)

        # Build the final discussion messages by detokenizing the full_message_list
        
        for message_tokens in full_message_list:
            discussion_messages += self.model.detokenize(message_tokens)
        discussion_messages += discussion_title
        title = [""]
        def receive(
                        chunk:str, 
                        message_type:MSG_OPERATION_TYPE
                    ):
            if chunk:
                title[0] += chunk
            antiprompt = self.personality.detect_antiprompt(title[0])
            if antiprompt:
                ASCIIColors.warning(f"\n{antiprompt} detected. Stopping generation")
                title[0] = self.remove_text_from_string(title[0],antiprompt)
                return False
            else:
                return True
            
        self._generate(discussion_messages, 150, client_id, receive)
        ASCIIColors.info(title[0])
        return title[0]
   

  

    def get_discussion_to(self, client_id,  message_id=-1):        
        messages = self.session.get_client(client_id).discussion.get_messages()
        full_message_list = []
        ump = f"{self.start_header_id_template}{self.config.user_name.strip()if self.config.use_user_name_in_discussions else self.personality.user_message_prefix}{self.end_header_id_template}"

        for message in messages:
            if message["id"]<= message_id or message_id==-1: 
                if message["type"]!=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_USER:
                    if message["sender"]==self.personality.name:
                        full_message_list.append(self.config.discussion_prompt_separator+self.personality.ai_message_prefix+message["content"])
                    else:
                        full_message_list.append(ump + message["content"])

        link_text = "\n"# self.personality.link_text

        if len(full_message_list) > self.config["nb_messages_to_remember"]:
            discussion_messages = self.config.discussion_prompt_separator + self.personality.personality_conditioning+ link_text.join(full_message_list[-self.config["nb_messages_to_remember"]:])
        else:
            discussion_messages = self.config.discussion_prompt_separator + self.personality.personality_conditioning+ link_text.join(full_message_list)
        
        return discussion_messages # Removes the last return

    def set_message_content(self, full_text:str, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]|None=None, client_id=0):
        """This sends full text to front end

        Args:
            step_text (dict): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the text to. Defaults to None.
        """
        if not callback:
            callback = partial(self.process_data,client_id = client_id)

        if callback:
            callback(full_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT)

    def emit_socket_io_info(self, name, data, client_id):
        run_async(partial(self.sio.emit,name, data, to=client_id))

    def notify(
                self, 
                content, 
                notification_type:NotificationType=NotificationType.NOTIF_SUCCESS, 
                duration:int=4, 
                client_id=None, 
                display_type:NotificationDisplayType=NotificationDisplayType.TOAST,
                verbose:bool|None=None,
            ):
        if verbose is None:
            verbose = self.verbose

        run_async(partial(self.sio.emit,'notification', {
                                'content': content,
                                'notification_type': notification_type.value,
                                "duration": duration,
                                'display_type':display_type.value
                            }, to=client_id
                            )
        )
        if verbose:
            if notification_type==NotificationType.NOTIF_SUCCESS:
                ASCIIColors.success(content)
            elif notification_type==NotificationType.NOTIF_INFO:
                ASCIIColors.info(content)
            elif notification_type==NotificationType.NOTIF_WARNING:
                ASCIIColors.warning(content)
            else:
                ASCIIColors.red(content)

    def refresh_files(self, client_id=None):
        run_async(partial(self.sio.emit,'refresh_files', to=client_id
                            )
        )


    def new_message(self, 
                            client_id, 
                            sender=None, 
                            content="",
                            message_type:MSG_OPERATION_TYPE=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT, 
                            sender_type:SENDER_TYPES=SENDER_TYPES.SENDER_TYPES_AI,
                            open=False
                        ):
        client = self.session.get_client(client_id)
        #self.close_message(client_id)
        if sender==None:
            sender= self.personality.name
        msg = client.discussion.add_message(
            message_type        = message_type.value,
            sender_type         = sender_type.value,
            sender              = sender,
            content             = content,
            steps               = [],
            metadata            = None,
            ui                  = None,
            rank                = 0,
            parent_message_id   = client.discussion.current_message.id if client.discussion.current_message is not None else 0,
            binding             = self.config["binding_name"],
            model               = self.config["model_name"], 
            personality         = self.config["personalities"][self.config["active_personality_id"]],
            created_at          = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )  # first the content is empty, but we'll fill it at the end  
        run_async(partial(
                    self.sio.emit,'new_message',
                        {
                            "sender":                   sender,
                            "message_type":             message_type.value,
                            "sender_type":              SENDER_TYPES.SENDER_TYPES_AI.value,
                            "content":                  content,
                            "metadata":                 None,
                            "ui":                       None,
                            "id":                       msg.id,
                            "parent_message_id":        msg.parent_message_id,

                            'binding':                  self.config["binding_name"],
                            'model' :                   self.config["model_name"], 
                            'personality':              self.config["personalities"][self.config["active_personality_id"]],

                            'created_at':               client.discussion.current_message.created_at,
                            'started_generating_at': client.discussion.current_message.started_generating_at,
                            'finished_generating_at': client.discussion.current_message.finished_generating_at,
                            'nb_tokens': client.discussion.current_message.nb_tokens,

                            'open':                     open
                        }, to=client_id
                )
            )
        
    def new_block(          self,                  
                            client_id, 
                            sender=None, 
                            content="",
                            parameters=None,
                            metadata=None,
                            ui=None,
                            message_type:MSG_OPERATION_TYPE=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT, 
                            sender_type:SENDER_TYPES=SENDER_TYPES.SENDER_TYPES_AI,
                            open=False
                        ):
        # like new_message but without adding the information to the database
        client = self.session.get_client(client_id)
        run_async(partial(
                    self.sio.emit,'new_message',
                        {
                            "sender":                   sender,
                            "message_type":             message_type.value,
                            "sender_type":              SENDER_TYPES.SENDER_TYPES_AI.value,
                            "content":                  content,
                            "parameters":               parameters,
                            "metadata":                 metadata,
                            "ui":                       ui,
                            "id":                       0,
                            "parent_message_id":        0,

                            'binding':                  self.config["binding_name"],
                            'model' :                   self.config["model_name"], 
                            'personality':              self.config["personalities"][self.config["active_personality_id"]],

                            'created_at':               client.discussion.current_message.created_at,
                            'started_generating_at': client.discussion.current_message.started_generating_at,
                            'finished_generating_at': client.discussion.current_message.finished_generating_at,
                            'nb_tokens': client.discussion.current_message.nb_tokens,

                            'open':                     open
                        }, to=client_id
                )
            )        
    def send_refresh(self, client_id):
        client = self.session.get_client(client_id)
        run_async(
            partial(self.sio.emit,'update_message', {
                                            "sender": client.discussion.current_message.sender,
                                            'id':client.discussion.current_message.id, 
                                            'content': client.discussion.current_message.content,
                                            'discussion_id':client.discussion.discussion_id,
                                            'operation_type': MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT.value,
                                            'message_type': client.discussion.current_message.message_type,
                                            'created_at':client.discussion.current_message.created_at,
                                            'started_generating_at': client.discussion.current_message.started_generating_at,
                                            'finished_generating_at': client.discussion.current_message.finished_generating_at,
                                            'nb_tokens': client.discussion.current_message.nb_tokens,
                                        }, to=client_id
                                )
        )

    def update_message(self, client_id, chunk,                             
                            parameters=None,
                            metadata=[], 
                            ui=None,
                            operation_type:MSG_OPERATION_TYPE=None
                        ):
        client = self.session.get_client(client_id)
        client.discussion.current_message.finished_generating_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client.discussion.current_message.nb_tokens = self.nb_received_tokens
        mtdt = json.dumps(metadata, indent=4) if metadata is not None and type(metadata)== list else metadata

        
        if self.nb_received_tokens==1:
            client.discussion.current_message.started_generating_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.update_message_step(client_id, "🔥 warming up ...",MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS)
            self.update_message_step(client_id, "✍ generating ...",MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS)

        run_async(
            partial(self.sio.emit,'update_message', {
                                            "sender": self.personality.name,
                                            'id':client.discussion.current_message.id, 
                                            'content': chunk,
                                            'ui': client.discussion.current_message.ui if ui is None else ui,
                                            'discussion_id':client.discussion.discussion_id,
                                            'operation_type': operation_type.value if operation_type is not None else MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK.value if self.nb_received_tokens>1 else MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT.value,
                                            'message_type': MSG_TYPE.MSG_TYPE_CONTENT.value,
                                            'created_at':client.discussion.current_message.created_at,
                                            'started_generating_at': client.discussion.current_message.started_generating_at,
                                            'finished_generating_at': client.discussion.current_message.finished_generating_at,
                                            'nb_tokens': client.discussion.current_message.nb_tokens,
                                            'parameters':parameters,
                                            'metadata':metadata
                                        }, to=client_id
                                )
        )
        if operation_type and operation_type.value < MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_INFO.value:
            client.discussion.update_message(client.generated_text, new_metadata=mtdt, new_ui=ui, started_generating_at=client.discussion.current_message.started_generating_at, nb_tokens=client.discussion.current_message.nb_tokens)



    def update_message_content(self, client_id, chunk, operation_type:MSG_OPERATION_TYPE=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT, message_type: MSG_TYPE=None):
        client = self.session.get_client(client_id)
        client.discussion.current_message.finished_generating_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client.discussion.current_message.nb_tokens = self.nb_received_tokens

        
        if self.nb_received_tokens==1:
            client.discussion.current_message.started_generating_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        run_async(
            partial(self.sio.emit,'update_message', {
                                            "sender": self.personality.name,
                                            'id':client.discussion.current_message.id, 
                                            'content': chunk,
                                            'discussion_id':client.discussion.discussion_id,
                                            'operation_type': operation_type.value,
                                            'message_type': client.discussion.current_message.message_type if message_type is None else message_type,
                                            'created_at':client.discussion.current_message.created_at,
                                            'started_generating_at': client.discussion.current_message.started_generating_at,
                                            'finished_generating_at': client.discussion.current_message.finished_generating_at,
                                            'nb_tokens': client.discussion.current_message.nb_tokens,
                                        }, to=client_id
                                )
        )

        client.discussion.update_message_content(client.generated_text, started_generating_at=client.discussion.current_message.started_generating_at, nb_tokens=client.discussion.current_message.nb_tokens)

    def update_message_step(self, client_id, step_text, msg_operation_type:MSG_OPERATION_TYPE=None):
        client = self.session.get_client(client_id)
        if msg_operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP:
            client.discussion.current_message.add_step(step_text,"instant",True, True)
        elif msg_operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_START:
            client.discussion.current_message.add_step(step_text,"start_end",True,False)
        elif msg_operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS:
            client.discussion.current_message.add_step(step_text,"start_end",True, True)
        elif msg_operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_FAILURE:
            client.discussion.current_message.add_step(step_text,"start_end",False, True)

        run_async(
            partial(self.sio.emit,'update_message', {
                                            'id':client.discussion.current_message.id, 
                                            'discussion_id':client.discussion.discussion_id,
                                            'operation_type': msg_operation_type.value,
                                            'steps': client.discussion.current_message.steps,

                                        }, to=client_id
                                )
        )
        

    def update_message_metadata(self, client_id, metadata):
        client = self.session.get_client(client_id)
        run_async(
            partial(self.sio.emit,'update_message', {
                                            "sender": self.personality.name,
                                            'id':client.discussion.current_message.id, 
                                            'metadata': metadata if type(metadata) in [str, None] else json.dumps(metadata) if type(metadata)==dict else None,
                                            'discussion_id':client.discussion.discussion_id,
                                            'operation_type': MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_JSON_INFOS.value,
                                        }, to=client_id
                                )
        )

        client.discussion.update_message_metadata(metadata)

    def update_message_ui(self, client_id, ui):
        client = self.session.get_client(client_id)
        run_async(
            partial(self.sio.emit,'update_message', {
                                            "sender": self.personality.name,
                                            'id':client.discussion.current_message.id, 
                                            'ui': ui,
                                            'discussion_id':client.discussion.discussion_id,
                                            'operation_type': MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI.value,
                                        }, to=client_id
                                )
        )

        client.discussion.update_message_ui(ui)



    def close_message(self, client_id):
        client = self.session.get_client(client_id)
        for msg in client.discussion.messages:
            if msg.steps is not None:
                for step in msg.steps:
                    step["done"]=True
        if not client.discussion:
            return
        #fix halucination
        if len(client.generated_text)>0 and len(self.start_header_id_template)>0:
            client.generated_text=client.generated_text.split(f"{self.start_header_id_template}")[0]
        # Send final message
        client.discussion.current_message.finished_generating_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            client.discussion.current_message.nb_tokens = len(self.model.tokenize(client.generated_text))
        except:
            client.discussion.current_message.nb_tokens = None
        run_async(
            partial(self.sio.emit,'close_message', {
                                            "sender": self.personality.name,
                                            "id": client.discussion.current_message.id,
                                            "content":client.generated_text,

                                            'binding': self.config["binding_name"],
                                            'model' : self.config["model_name"], 
                                            'personality':self.config["personalities"][self.config["active_personality_id"]],

                                            'created_at': client.discussion.current_message.created_at,
                                            'started_generating_at': client.discussion.current_message.started_generating_at,
                                            'finished_generating_at': client.discussion.current_message.finished_generating_at,
                                            'nb_tokens': client.discussion.current_message.nb_tokens,

                                        }, to=client_id
                                )
        )

    def process_data(
                        self, 
                        data:str|list|None, 
                        operation_type:MSG_OPERATION_TYPE,
                        client_id:str=0,
                        personality:AIPersonality=None
                    ):
        """
        Processes a data of generated text
        """
        client = self.session.get_client(client_id)
        if data is None and operation_type in [MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK]:
            return
        
        if data is not None:
            if not client_id in list(self.session.clients.keys()):
                self.error("Connection lost", client_id=client_id)
                return
        if operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP:
            ASCIIColors.info("--> Step:"+data)
        if operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_START:
            ASCIIColors.info("--> Step started:"+data)
            self.update_message_step(client_id, data, operation_type)
        if operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS:
            ASCIIColors.success("--> Step ended:"+data)
            self.update_message_step(client_id, data, operation_type)
        if operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_FAILURE:
            ASCIIColors.success("--> Step ended:"+data)
            self.update_message_step(client_id, data, operation_type)
        if operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_WARNING:
            self.warning(data,client_id=client_id)
            ASCIIColors.error("--> Exception from personality:"+data)
        if operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_EXCEPTION:
            self.error(data, client_id=client_id)
            ASCIIColors.error("--> Exception from personality:"+data)
            return
        if operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_INFO:
            self.info(data, client_id=client_id)
            ASCIIColors.info("--> Info:"+data)
            return
        if operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI:
            self.update_message_ui(client_id, data)
            return
        if operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_JSON_INFOS:
            self.update_message_metadata(client_id, data)
            return
        if operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_NEW_MESSAGE:
            self.nb_received_tokens = 0
            self.start_time = datetime.now()
            self.update_message_step(client_id, "🔥 warming up ...", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS)
            self.update_message_step(client_id, "✍ generating ...",MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS)
            self.new_message(
                                    client_id, 
                                    self.personality.name if personality is None else personality.name,
                                    data,
                                    message_type = MSG_TYPE.MSG_TYPE_CONTENT
                            )
            return
        elif operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_FINISHED_MESSAGE:
            self.close_message(client_id)
            return
        elif operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK:
            if self.nb_received_tokens==0:
                self.start_time = datetime.now()
                try:
                    self.update_message_step(client_id, "🔥 warming up ...",MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS)
                    self.update_message_step(client_id, "✍ generating ...",MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS)
                except Exception as ex:
                    trace_exception(ex)
                    ASCIIColors.warning("Couldn't send status update to client")
            dt =(datetime.now() - self.start_time).seconds
            if dt==0:
                dt=1
            spd = self.nb_received_tokens/dt
            if self.config.debug_show_chunks:
                print(data,end="",flush=True)
            #ASCIIColors.green(f"Received {self.nb_received_tokens} tokens (speed: {spd:.2f}t/s)              ",end="\r",flush=True) 
            sys.stdout = sys.__stdout__
            sys.stdout.flush()
            if data:
                client.generated_text += data
            antiprompt = self.personality.detect_antiprompt(client.generated_text)
            if antiprompt:
                ASCIIColors.warning(f"\n{antiprompt} detected. Stopping generation")
                client.generated_text = self.remove_text_from_string(client.generated_text,antiprompt)
                self.update_message_content(client_id, client.generated_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT)
                return False
            else:
                self.nb_received_tokens += 1
                if client.continuing and client.first_chunk:
                    self.update_message_content(client_id, client.generated_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT)
                else:
                    self.update_message_content(client_id, data, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK)

                client.first_chunk=False
                # if stop generation is detected then stop
                if not self.cancel_gen:
                    return True
                else:
                    self.cancel_gen = False
                    ASCIIColors.warning("Generation canceled")
                    return False
        # Stream the generated text to the main process
        elif operation_type in [MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_USER]:
            if self.nb_received_tokens==0:
                self.start_time = datetime.now()
                try:
                    self.update_message_step(client_id, "🔥 warming up ...", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS)
                    self.update_message_step(client_id, "✍ generating ...",MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS)

                except Exception as ex:
                    ASCIIColors.warning("Couldn't send status update to client")

            client.generated_text = data
            antiprompt = self.personality.detect_antiprompt(client.generated_text)
            if antiprompt:
                ASCIIColors.warning(f"\n{antiprompt} detected. Stopping generation")
                client.generated_text = self.remove_text_from_string(client.generated_text,antiprompt)
                self.update_message_content(client_id, client.generated_text, operation_type)
                return False

            self.update_message_content(client_id, data, operation_type)
            return True
        # Stream the generated text to the frontend
        else:
            self.update_message_content(client_id, data, operation_type)
        return True


    def generate(self, full_prompt, prompt, context_details, n_predict, client_id, callback=None):
        if self.config.debug and self.config.debug_show_final_full_prompt:
            ASCIIColors.highlight(full_prompt,[r for r in [
                        self.config.discussion_prompt_separator,
                        self.config.start_header_id_template,
                        self.config.end_header_id_template,
                        self.config.separator_template,
                        self.config.start_user_header_id_template,
                        self.config.end_user_header_id_template,
                        self.config.end_user_message_id_template,
                        self.config.start_ai_header_id_template,
                        self.config.end_ai_header_id_template,
                        self.config.end_ai_message_id_template,
                        self.config.system_message_template,
                        ] if r!="" and r!="\n"])

        if self.config.use_smart_routing:
            if self.config.smart_routing_router_model!="" and len(self.config.smart_routing_models_by_power)>=2:
                ASCIIColors.yellow("Using smart routing")
                self.personality.step_start("Routing request")
                self.back_model = f"{self.binding.binding_folder_name}::{self.model.model_name}"
                try:
                    binding, model_name = self.model_path_to_binding_model(self.config.smart_routing_router_model)
                    self.select_model(binding, model_name)
                    output_id = self.personality.multichoice_question("assess the complexity of the following prompt (higher means more complex, lower less complex), if the user asking simple questions or just saying hello, please select the lowest model.", [str(i) for i in range(len(self.config.smart_routing_models_by_power))], full_prompt)
                    if output_id >=0 and output_id<len(self.config.smart_routing_models_by_power):
                        binding, model_name = self.model_path_to_binding_model(self.config.smart_routing_models_by_power[output_id])
                        self.select_model(binding, model_name)
                        self.personality.step_end("Routing request")
                        self.personality.step(f"Selected {self.config.smart_routing_models_by_power[output_id]}")
                except Exception as ex:
                    self.error("Failed to route beceause of this error : " + str(ex))
                    self.personality.step_end("Routing request", False)
            else:
                ASCIIColors.yellow("Warning! Smart routing is active but one of the following requirements are not met")
                ASCIIColors.yellow("- smart_routing_router_model must be set correctly")
                ASCIIColors.yellow("- smart_routing_models_by_power must contain at least one model")


        if self.personality.processor is not None:
            ASCIIColors.info("Running workflow")
            try:
                self.personality.callback = callback
                client = self.session.get_client(client_id)
                self.personality.vectorizer = client.discussion.vectorizer
                self.personality.text_files = client.discussion.text_files
                self.personality.image_files = client.discussion.image_files
                self.personality.audio_files = client.discussion.audio_files
                output = self.personality.processor.run_workflow(prompt, full_prompt, callback, context_details,client=client)
            except Exception as ex:
                trace_exception(ex)
                # Catch the exception and get the traceback as a list of strings
                traceback_lines = traceback.format_exception(type(ex), ex, ex.__traceback__)
                # Join the traceback lines into a single string
                traceback_text = ''.join(traceback_lines)
                ASCIIColors.error(f"Workflow run failed.\nError:{ex}")
                ASCIIColors.error(traceback_text)
                if callback:
                    callback(f"Workflow run failed\nError:{ex}", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_EXCEPTION)
                return          
            print("Finished executing the workflow")
            return output


        txt = self._generate(full_prompt, n_predict, client_id, callback)
        ASCIIColors.success("\nFinished executing the generation")

        if self.config.use_smart_routing and self.config.restore_model_after_smart_routing:
            if self.config.smart_routing_router_model!="" and len(self.config.smart_routing_models_by_power)>=2:
                ASCIIColors.yellow("Restoring model")
                self.personality.step_start("Restoring main model")
                binding, model_name = self.model_path_to_binding_model(self.back_model)
                self.select_model(binding, model_name)
                self.personality.step_end("Restoring main model")

        return txt

    def _generate(self, prompt, n_predict, client_id, callback=None):
        client = self.session.get_client(client_id)
        if client is None:
            return None
        self.nb_received_tokens = 0
        self.start_time = datetime.now()
        if self.model is not None:
            if self.model.binding_type==BindingType.TEXT_IMAGE and len(client.discussion.image_files)>0:
                if self.config["override_personality_model_parameters"]:
                    output = self.model.generate_with_images(
                        prompt,
                        client.discussion.image_files,
                        callback=callback,
                        n_predict=n_predict,
                        temperature=self.config['temperature'],
                        top_k=self.config['top_k'],
                        top_p=self.config['top_p'],
                        repeat_penalty=self.config['repeat_penalty'],
                        repeat_last_n = self.config['repeat_last_n'],
                        seed=self.config['seed'],
                        n_threads=self.config['n_threads']
                    )
                else:
                    prompt = "\n".join([
                        f"{self.start_header_id_template}{self.system_message_template}{self.end_header_id_template}I am an AI assistant that can converse and analyze images. When asked to locate something in an image you send, I will reply with:",
                        "boundingbox(image_index, label, left, top, width, height)",
                        "Where:",
                        "image_index: 0-based index of the image",
                        "label: brief description of what is located",
                        "left, top: x,y coordinates of top-left box corner (0-1 scale)",
                        "width, height: box dimensions as fraction of image size",
                        "Coordinates have origin (0,0) at top-left, (1,1) at bottom-right.",
                        "For other queries, I will respond conversationally to the best of my abilities.",
                        prompt
                    ])
                    output = self.model.generate_with_images(
                        prompt,
                        client.discussion.image_files,
                        callback=callback,
                        n_predict=n_predict,
                        temperature=self.personality.model_temperature,
                        top_k=self.personality.model_top_k,
                        top_p=self.personality.model_top_p,
                        repeat_penalty=self.personality.model_repeat_penalty,
                        repeat_last_n = self.personality.model_repeat_last_n,
                        seed=self.config['seed'],
                        n_threads=self.config['n_threads']
                    )
                    try:
                        post_processed_output = process_ai_output(output, client.discussion.image_files, client.discussion.discussion_folder)
                        if len(post_processed_output)!=output:
                            self.process_data(post_processed_output, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT,client_id=client_id)
                    except Exception as ex:
                        ASCIIColors.error(str(ex))                                 
            else:
                if self.config["override_personality_model_parameters"]:
                    output = self.model.generate(
                        prompt,
                        callback=callback,
                        n_predict=n_predict,
                        temperature=self.config['temperature'],
                        top_k=self.config['top_k'],
                        top_p=self.config['top_p'],
                        repeat_penalty=self.config['repeat_penalty'],
                        repeat_last_n = self.config['repeat_last_n'],
                        seed=self.config['seed'],
                        n_threads=self.config['n_threads']
                    )
                else:
                    output = self.model.generate(
                        prompt,
                        callback=callback,
                        n_predict=n_predict,
                        temperature=self.personality.model_temperature,
                        top_k=self.personality.model_top_k,
                        top_p=self.personality.model_top_p,
                        repeat_penalty=self.personality.model_repeat_penalty,
                        repeat_last_n = self.personality.model_repeat_last_n,
                        seed=self.config['seed'],
                        n_threads=self.config['n_threads']
                    )
        else:
            print("No model is installed or selected. Please make sure to install a model and select it inside your configuration before attempting to communicate with the model.")
            print("To do this: Install the model to your models/<binding name> folder.")
            print("Then set your model information in your local configuration file that you can find in configs/local_config.yaml")
            print("You can also use the ui to set your model in the settings page.")
            output = ""
        return output

    def start_message_generation(self, message, message_id, client_id, is_continue=False, generation_type=None, force_using_internet=False):
        client = self.session.get_client(client_id)
        if self.personality is None:
            self.warning("Select a personality")
            return
        ASCIIColors.info(f"Text generation requested by client: {client_id}")
        # send the message to the bot
        print(f"Received message : {message.content}")
        if client.discussion:
            try:
                # First we need to send the new message ID to the client
                if is_continue:
                    client.discussion.load_message(message_id)
                    client.generated_text = message.content
                else:
                    self.send_refresh(client_id)
                    self.new_message(client_id, self.personality.name, "")
                    self.update_message_step(client_id, "🔥 warming up ...", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_START)

                # prepare query and reception
                self.discussion_messages, self.current_message, tokens, context_details, internet_search_infos = self.prepare_query(client_id, message_id, is_continue, n_tokens=self.config.min_n_predict, generation_type=generation_type, force_using_internet=force_using_internet, previous_chunk = client.generated_text if is_continue else "")
                ASCIIColors.info(f"prompt has {self.config.ctx_size-context_details['available_space']} tokens")
                ASCIIColors.info(f"warmup for generating up to {min(context_details['available_space'],self.config.max_n_predict)} tokens")
                self.prepare_reception(client_id)
                self.generating = True
                client.processing=True
                try:
                    self.generate(
                                    self.discussion_messages, 
                                    self.current_message,
                                    context_details=context_details,
                                    n_predict = min(self.config.ctx_size-len(tokens)-1,self.config.max_n_predict),
                                    client_id=client_id,
                                    callback=partial(self.process_data,client_id = client_id)
                                )
                    if self.tts and self.config.auto_read and len(self.personality.audio_samples)>0:
                        try:
                            self.process_data("Generating voice output",MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_START,client_id=client_id)
                            from lollms.services.xtts.lollms_xtts import LollmsXTTS
                            voice=self.config.xtts_current_voice
                            if voice!="main_voice":
                                voices_folder = self.lollms_paths.custom_voices_path
                            else:
                                voices_folder = Path(__file__).parent.parent.parent/"services/xtts/voices"

                            if self.xtts.ready:
                                language = convert_language_name(self.personality.language)
                                self.xtts.set_speaker_folder(Path(self.personality.audio_samples[0]).parent)
                                fn = self.personality.name.lower().replace(' ',"_").replace('.','')    
                                fn = f"{fn}_{message_id}.wav"
                                url = f"audio/{fn}"
                                self.xtts.tts_file(client.generated_text, Path(self.personality.audio_samples[0]).name, f"{fn}", language=language)
                                fl = f"\n".join([
                                f"<audio controls>",
                                f'    <source src="{url}" type="audio/wav">',
                                f'    Your browser does not support the audio element.',
                                f'</audio>'                        
                                ])
                                self.process_data("Generating voice output", operation_type= MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS,client_id=client_id)
                                self.process_data(fl,MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI, client_id=client_id)
                            else:
                                self.InfoMessage("xtts is not up yet.\nPlease wait for it to load then try again. This may take some time.") 

                        except Exception as ex:
                            ASCIIColors.error("Couldn't read")
                            trace_exception(ex)
                    print()
                    ASCIIColors.success("## Done Generation ##")
                    print()
                except Exception as ex:
                    trace_exception(ex)
                    print()
                    ASCIIColors.error("## Generation Error ##")
                    print()

                self.cancel_gen = False
                sources_text = ""
                if len(context_details["documentation_entries"]) > 0:
                    sources_text += '<div class="text-gray-400 mr-10px">Sources:</div>'
                    sources_text += '<div class="mt-4 flex flex-col items-start gap-x-2 gap-y-1.5 text-sm" style="max-height: 500px; overflow-y: auto;">'
                    for source in context_details["documentation_entries"]:
                        title = source["document_title"]
                        path = source["document_path"]
                        content = source["chunk_content"]
                        size = source["chunk_size"]
                        distance = source["distance"]
                        sources_text += f'''
                            <div class="source-item">
                                <button onclick="var details = document.getElementById('source-details-{title}'); details.style.display = details.style.display === 'none' ? 'block' : 'none';" style="text-align: left; font-weight: bold;"><strong>{title}</strong></button>
                                <div id="source-details-{title}" style="display:none;">
                                    <div style="max-height: 200px; overflow-y: auto;">
                                        <p><strong>Path:</strong> {path}</p>
                                        <p><strong>Content:</strong> {content}</p>
                                        <p><strong>Size:</strong> {size}</p>
                                        <p><strong>Distance:</strong> {distance}</p>
                                    </div>
                                </div>
                            </div>
                        '''
                    sources_text += '</div>'                    
                    self.personality.ui(sources_text)  
                if len(context_details["skills"]) > 0:
                    sources_text += '<div class="text-gray-400 mr-10px">Memories:</div>'
                    sources_text += '<div class="mt-4 flex flex-col items-start gap-x-2 gap-y-1.5 text-sm" style="max-height: 500px; overflow-y: auto;">'
                    ind = 0
                    for skill in context_details["skills"]:
                        sources_text += f'''
                            <div class="source-item">
                                <button onclick="var details = document.getElementById('source-details-{ind}'); details.style.display = details.style.display === 'none' ? 'block' : 'none';" style="text-align: left; font-weight: bold;"><strong>Memory {ind}</strong></button>
                                <div id="source-details-{ind}" style="display:none;">
                                    <div style="max-height: 200px; overflow-y: auto;">
                                        <pre>{skill}</pre>
                                    </div>    
                                </div>
                            </div>
                        '''
                        ind += 1
                    sources_text += '</div>'                 
                    self.personality.ui(sources_text)  
                # Send final message
                if self.config.activate_internet_search or force_using_internet or generation_type == "full_context_with_internet":
                    from lollms.internet import get_favicon_url, get_root_url
                    sources_text += '''
                    <div class="mt-4 text-sm">
                        <div class="text-gray-500 font-semibold mb-2">Sources:</div>
                        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 h-64 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
                    '''

                    for source in internet_search_infos:
                        url = source["url"]
                        title = source["title"]
                        brief = source["brief"]
                        favicon_url = get_favicon_url(url) or "/personalities/generic/lollms/assets/logo.png"
                        root_url = get_root_url(url)
                        
                        sources_text += f'''
                        <div class="relative flex flex-col items-start gap-2 rounded-lg border border-gray-200 bg-white p-3 shadow-sm transition duration-200 ease-in-out transform hover:scale-105 hover:border-gray-300 hover:shadow-lg dark:border-gray-700 dark:bg-gray-800 dark:hover:border-gray-600 dark:hover:shadow-lg animate-fade-in">
                            <a class="flex items-center w-full" target="_blank" href="{url}" title="{brief}">
                                <img class="h-8 w-8 rounded-full" src="{favicon_url}" alt="{title}" onerror="this.onerror=null;this.src='/personalities/generic/lollms/assets/logo.png';">
                                <div class="ml-2">
                                    <div class="text-gray-700 dark:text-gray-300 font-semibold text-sm">{title}</div>
                                    <div class="text-gray-500 dark:text-gray-400 text-xs">{root_url}</div>
                                    <div class="text-gray-400 dark:text-gray-500 text-xs">{brief}</div>
                                </div>
                            </a>
                        </div>
                        '''

                    sources_text += '''
                        </div>
                    </div>
                    '''

                    # Add CSS for animations and scrollbar styles
                    sources_text += '''
                    <style>
                    @keyframes fadeIn {
                        from { opacity: 0; transform: translateY(10px); }
                        to { opacity: 1; transform: translateY(0); }
                    }
                    .animate-fade-in {
                        animation: fadeIn 0.5s ease-in-out;
                    }
                    .scrollbar-thin::-webkit-scrollbar {
                        width: 8px;
                    }
                    .scrollbar-thin::-webkit-scrollbar-thumb {
                        background-color: #cbd5e1; /* Tailwind gray-300 */
                        border-radius: 10px;
                    }
                    .scrollbar-thin::-webkit-scrollbar-track {
                        background: #f9fafb; /* Tailwind gray-100 */
                    }
                    </style>
                    '''
                    self.personality.ui(sources_text)

            except Exception as ex:
                trace_exception(ex)
            try:
                self.update_message_step(client_id, "🔥 warming up ...", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS)
                self.update_message_step(client_id, "✍ generating ...",MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS)
            except Exception as ex:
                ASCIIColors.warning("Couldn't send status update to client")
            self.close_message(client_id)

            client.processing=False
            # Clients are now kept forever
            #if client.schedule_for_deletion:
            #    self.session.remove_client(client.client_id, client.client_id)

            ASCIIColors.success(f" ╔══════════════════════════════════════════════════╗ ")
            ASCIIColors.success(f" ║                        Done                      ║ ")
            ASCIIColors.success(f" ╚══════════════════════════════════════════════════╝ ")
            if self.config.auto_title:
                d = client.discussion
                ttl = d.title()
                if ttl is None or ttl=="" or ttl=="untitled":
                    title = self.make_discussion_title(d, client_id=client_id)
                    d.rename(title)
                    asyncio.run(
                        self.sio.emit('disucssion_renamed',{
                                        'status': True,
                                        'discussion_id':d.discussion_id,
                                        'title':title
                                        }, to=client_id) 
                    )
            self.busy=False

        else:
            self.cancel_gen = False
            #No discussion available
            ASCIIColors.warning("No discussion selected!!!")

            self.error("No discussion selected!!!", client_id=client_id)
            
            print()
            self.busy=False
            return ""

    def receive_and_generate(self, text, client:Client, callback=None):
        prompt = text
        try:
            nb_tokens = len(self.model.tokenize(prompt))
        except:
            nb_tokens = None
        
        message = client.discussion.add_message(
            operation_type    = MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT.value,
            sender_type     = SENDER_TYPES.SENDER_TYPES_USER.value,
            sender          = self.config.user_name.strip() if self.config.use_user_name_in_discussions else self.personality.user_message_prefix,
            content         = prompt,
            metadata        = None,
            parent_message_id=self.message_id,
            nb_tokens=nb_tokens
        )
        discussion_messages, current_message, tokens, context_details, internet_search_infos = self.prepare_query(client.client_id, client.discussion.current_message.id, False, n_tokens=self.config.min_n_predict, force_using_internet=False)
        self.new_message(
                        client.client_id, 
                        self.personality.name,
                        operation_type= MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT,
                        content=""
        )
        client.generated_text = ""
        ASCIIColors.info(f"prompt has {self.config.ctx_size-context_details['available_space']} tokens")
        ASCIIColors.info(f"warmup for generating up to {min(context_details['available_space'],self.config.max_n_predict)} tokens")
        self.generate(discussion_messages, current_message, context_details, min(self.config.ctx_size-len(tokens)-1, self.config.max_n_predict), client.client_id, callback if callback else partial(self.process_data, client_id=client.client_id))
        self.close_message(client.client_id)        
        return client.generated_text
