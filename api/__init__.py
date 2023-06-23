######
# Project       : lollms-webui
# File          : api.py
# Author        : ParisNeo with the help of the community
# Supported by Nomic-AI
# license       : Apache 2.0
# Description   : 
# A simple api to communicate with lollms-webui and its models.
######
from flask import request
from datetime import datetime
from api.db import DiscussionsDB
from api.helpers import compare_lists
from pathlib import Path
import importlib
from lollms.config import InstallOption
from lollms.types import MSG_TYPE
from lollms.personality import AIPersonality, PersonalityBuilder
from lollms.binding import LOLLMSConfig, BindingBuilder, LLMBinding, ModelBuilder
from lollms.paths import LollmsPaths
from lollms.helpers import ASCIIColors
import multiprocessing as mp
import threading
import time
import requests
from tqdm import tqdm 
import traceback
import sys
from lollms.console import MainMenu

__author__ = "parisneo"
__github__ = "https://github.com/ParisNeo/lollms-webui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"



import subprocess
import pkg_resources


# ===========================================================
# Manage automatic install scripts

def is_package_installed(package_name):
    try:
        dist = pkg_resources.get_distribution(package_name)
        return True
    except pkg_resources.DistributionNotFound:
        return False


def install_package(package_name):
    try:
        # Check if the package is already installed
        __import__(package_name)
        print(f"{package_name} is already installed.")
    except ImportError:
        print(f"{package_name} is not installed. Installing...")
        
        # Install the package using pip
        subprocess.check_call(["pip", "install", package_name])
        
        print(f"{package_name} has been successfully installed.")


def parse_requirements_file(requirements_path):
    with open(requirements_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                # Skip empty and commented lines
                continue
            package_name, _, version_specifier = line.partition('==')
            package_name, _, version_specifier = line.partition('>=')
            if is_package_installed(package_name):
                # The package is already installed
                print(f"{package_name} is already installed.")
            else:
                # The package is not installed, install it
                if version_specifier:
                    install_package(f"{package_name}{version_specifier}")
                else:
                    install_package(package_name)


# ===========================================================


class LoLLMsAPPI():
    def __init__(self, config:LOLLMSConfig, socketio, config_file_path:str, lollms_paths: LollmsPaths) -> None:
        self.lollms_paths = lollms_paths
        self.config = config
        self.is_ready = True
        self.menu = MainMenu(self)

        
        self.socketio = socketio
        # Check model
        if config.binding_name is None:
            self.menu.select_model()

        self.binding = BindingBuilder().build_binding(self.config, self.lollms_paths)
        
        # Check model
        if config.model_name is None:
            self.menu.select_model()

        self.model = self.binding.build_model()

        self.mounted_personalities = []
        self.mounted_personalities = self.rebuild_personalities()
        if self.config["active_personality_id"]<len(self.mounted_personalities):
            self.personality:AIPersonality = self.mounted_personalities[self.config["active_personality_id"]]
        else:
            self.personality:AIPersonality = None
        if config["debug"]:
            print(print(f"{self.personality}"))
        self.config_file_path = config_file_path
        self.cancel_gen = False

        # Keeping track of current discussion and message
        self.current_discussion = None
        self._current_user_message_id = 0
        self._current_ai_message_id = 0
        self._message_id = 0

        self.db_path = config["db_path"]
        if Path(self.db_path).is_absolute():
            # Create database object
            self.db = DiscussionsDB(self.db_path)
        else:
            # Create database object
            self.db = DiscussionsDB(self.lollms_paths.personal_path/"databases"/self.db_path)

        # If the database is empty, populate it with tables
        ASCIIColors.info("Checking discussions database... ",end="")
        self.db.create_tables()
        self.db.add_missing_columns()
        ASCIIColors.success("ok")

        # This is used to keep track of messages 
        self.full_message_list = []
        self.current_room_id = None
        # =========================================================================================
        # Socket IO stuff    
        # =========================================================================================
        @socketio.on('connect')
        def connect():
            ASCIIColors.success(f'Client {request.sid} connected')

        @socketio.on('disconnect')
        def disconnect():
            ASCIIColors.error(f'Client {request.sid} disconnected')

        @socketio.on('cancel_generation')
        def cancel_generation():
            self.cancel_gen = True
            ASCIIColors.error(f'Client {request.sid} canceled generation')
        

        @socketio.on('install_model')
        def install_model(data):
            room_id = request.sid 
            def install_model_():
                print("Install model triggered")
                model_path = data["path"]
                progress = 0
                installation_dir = self.lollms_paths.personal_models_path/self.config["binding_name"]
                filename = Path(model_path).name
                installation_path = installation_dir / filename
                print("Model install requested")
                print(f"Model path : {model_path}")

                if installation_path.exists():
                    print("Error: Model already exists")
                    socketio.emit('install_progress',{'status': False, 'error': 'model already exists'}, room=room_id)
                
                socketio.emit('install_progress',{'status': 'progress', 'progress': progress}, room=room_id)
                
                def callback(progress):
                    socketio.emit('install_progress',{'status': 'progress', 'progress': progress}, room=room_id)
                    
                if hasattr(self.binding, "download_model"):
                    self.binding.download_model(model_path, installation_path, callback)
                else:
                    self.download_file(model_path, installation_path, callback)
                socketio.emit('install_progress',{'status': True, 'error': ''}, room=room_id)
            tpe = threading.Thread(target=install_model_, args=())
            tpe.start()

        @socketio.on('uninstall_model')
        def uninstall_model(data):
            model_path = data['path']
            installation_dir = self.lollms_paths.personal_models_path/self.config["binding_name"]
            filename = Path(model_path).name
            installation_path = installation_dir / filename

            if not installation_path.exists():
                socketio.emit('install_progress',{'status': False, 'error': 'The model does not exist'}, room=request.sid)

            installation_path.unlink()
            socketio.emit('install_progress',{'status': True, 'error': ''}, room=request.sid)


        @socketio.on('upload_file')
        def upload_file(data):
            file = data['file']
            filename = file.filename
            save_path = self.lollms_paths.personal_uploads_path/filename  # Specify the desired folder path

            try:
                if not self.personality.processor is None:
                    self.personality.processor.add_file(save_path)
                    file.save(save_path)
                    # File saved successfully
                    socketio.emit('progress', {'status':True, 'progress': 100})

                else:
                    # Personality doesn't support file sending
                    socketio.emit('progress', {'status':False, 'error': "Personality doesn't support file sending"})
            except Exception as e:
                # Error occurred while saving the file
                socketio.emit('progress', {'status':False, 'error': str(e)})
            

        
        @socketio.on('generate_msg')
        def generate_msg(data):
            self.current_room_id = request.sid
            if self.is_ready:
                if self.current_discussion is None:
                    if self.db.does_last_discussion_have_messages():
                        self.current_discussion = self.db.create_discussion()
                    else:
                        self.current_discussion = self.db.load_last_discussion()

                message = data["prompt"]
                message_id = self.current_discussion.add_message(
                    "user", 
                    message, 
                    parent=self.message_id
                )

                self.current_user_message_id = message_id
                ASCIIColors.green("Starting message generation by"+self.personality.name)

                task = self.socketio.start_background_task(self.start_message_generation, message, message_id)
                ASCIIColors.info("Started generation task")
                #tpe = threading.Thread(target=self.start_message_generation, args=(message, message_id))
                #tpe.start()
            else:
                self.socketio.emit("buzzy", {"message":"I am buzzy. Come back later."}, room=self.current_room_id)
                self.socketio.sleep(0)
                ASCIIColors.warning(f"OOps request {self.current_room_id}  refused!! Server buzy")
                self.socketio.emit('infos',
                        {
                            "status":'model_not_ready',
                            "type": "input_message_infos",
                            'logo': "",
                            "bot": self.personality.name,
                            "user": self.personality.user_name,
                            "message":"",
                            "user_message_id": self.current_user_message_id,
                            "ai_message_id": self.current_ai_message_id,

                            'binding': self.current_discussion.current_message_binding,
                            'model': self.current_discussion.current_message_model,
                            'personality': self.current_discussion.current_message_personality,
                            'created_at': self.current_discussion.current_message_created_at,
                            'finished_generating_at': self.current_discussion.current_message_finished_generating_at,
                        }, room=self.current_room_id
                )
                self.socketio.sleep(0)

        @socketio.on('generate_msg_from')
        def handle_connection(data):
            message_id = int(data['id'])
            message = data["prompt"]
            self.current_user_message_id = message_id
            tpe = threading.Thread(target=self.start_message_generation, args=(message, message_id))
            tpe.start()
        # generation status
        self.generating=False
        ASCIIColors.blue(f"Your personal data is stored here :{self.lollms_paths.personal_path}")
        ASCIIColors.blue(f"Listening on :http://{self.config['host']}:{self.config['port']}")


    def rebuild_personalities(self):
        loaded = self.mounted_personalities
        loaded_names = [f"{p.language}/{p.category}/{p.personality_folder_name}" for p in loaded]
        mounted_personalities=[]
        ASCIIColors.success(f" ╔══════════════════════════════════════════════════╗ ")
        ASCIIColors.success(f" ║           Building mounted Personalities         ║ ")
        ASCIIColors.success(f" ╚══════════════════════════════════════════════════╝ ")
        for i,personality in enumerate(self.config['personalities']):
            if personality in loaded_names:
                mounted_personalities.append(loaded[loaded_names.index(personality)])
            else:
                personality_path = self.lollms_paths.personalities_zoo_path/f"{personality}"
                try:
                    if i==self.config["active_personality_id"]:
                        ASCIIColors.red("*", end="")
                        ASCIIColors.green(f" {personality}")
                    else:
                        ASCIIColors.yellow(f" {personality}")
                        
                    personality = AIPersonality(personality_path,
                                                self.lollms_paths, 
                                                self.config,
                                                model=self.model,
                                                run_scripts=True)
                    mounted_personalities.append(personality)
                except Exception as ex:
                    ASCIIColors.error(f"Personality file not found or is corrupted ({personality_path}).\nReturned the following exception:{ex}\nPlease verify that the personality you have selected exists or select another personality. Some updates may lead to change in personality name or category, so check the personality selection in settings to be sure.")
                    if self.config["debug"]:
                        print(ex)
                    try:
                        personality = AIPersonality(
                                                    personality_path, 
                                                    self.lollms_paths, 
                                                    self.config, 
                                                    self.model, 
                                                    run_scripts=True,
                                                    installation_option=InstallOption.FORCE_INSTALL)
                    except:
                        ASCIIColors.error(f"Couldn't load personality at {personality_path}")
                        personality = AIPersonality(None,                                                    self.lollms_paths, 
                                                    self.config, 
                                                    self.model, 
                                                    run_scripts=True,
                                                    installation_option=InstallOption.FORCE_INSTALL)
                        ASCIIColors.info("Reverted to default personality")
        print(f'selected : {self.config["active_personality_id"]}')
        ASCIIColors.success(f" ╔══════════════════════════════════════════════════╗ ")
        ASCIIColors.success(f" ║                      Done                        ║ ")
        ASCIIColors.success(f" ╚══════════════════════════════════════════════════╝ ")
            
        return mounted_personalities




    # ================================== LOLLMSApp

    def load_binding(self):
        if self.config.binding_name is None:
            print(f"No bounding selected")
            print("Please select a valid model or install a new one from a url")
            self.menu.select_binding()
            # cfg.download_model(url)
        else:
            try:
                self.binding = BindingBuilder().build_binding(self.config, self.lollms_paths)
            except Exception as ex:
                print(ex)
                print(f"Couldn't find binding. Please verify your configuration file at {self.config.file_path} or use the next menu to select a valid binding")
                print(f"Trying to reinstall binding")
                self.binding = BindingBuilder().build_binding(self.config, self.lollms_paths, InstallOption.FORCE_INSTALL)
                self.menu.select_binding()

    def load_model(self):
        try:
            self.active_model = ModelBuilder(self.binding).get_model()
            ASCIIColors.success("Model loaded successfully")
        except Exception as ex:
            ASCIIColors.error(f"Couldn't load model.")
            ASCIIColors.error(f"Binding returned this exception : {ex}")
            ASCIIColors.error(f"{self.config.get_model_path_infos()}")
            print("Please select a valid model or install a new one from a url")
            self.menu.select_model()

    def load_personality(self):
        try:
            self.personality = PersonalityBuilder(self.lollms_paths, self.config, self.model).build_personality()
        except Exception as ex:
            ASCIIColors.error(f"Couldn't load personality.")
            ASCIIColors.error(f"Binding returned this exception : {ex}")
            ASCIIColors.error(f"{self.config.get_personality_path_infos()}")
            print("Please select a valid model or install a new one from a url")
            self.menu.select_model()
        self.cond_tk = self.personality.model.tokenize(self.personality.personality_conditioning)
        self.n_cond_tk = len(self.cond_tk)


    #properties
    @property
    def message_id(self):
        return self._message_id

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
                                percentage = (downloaded_size / total_size) * 100
                                callback(percentage)
                            progress_bar.update(len(chunk))

            if callback is not None:
                callback(100.0)

            print("File downloaded successfully")
        except Exception as e:
            print("Couldn't download file:", str(e))


   
    def condition_chatbot(self):
        if self.current_discussion is None:
            self.current_discussion = self.db.load_last_discussion()
    
        if self.personality.welcome_message!="":
            message_id = self.current_discussion.add_message(
                self.personality.name, self.personality.welcome_message, 
                DiscussionsDB.MSG_TYPE_NORMAL,
                0,
                -1,
                binding= self.config["binding_name"],
                model = self.config["model_name"], 
                personality=self.config["personalities"][self.config["active_personality_id"]]
            )
        
            self.current_ai_message_id = message_id
        else:
            message_id = 0
        return message_id

    def prepare_reception(self):
        self.current_generated_text = ""
        self.full_text = ""
        self.is_bot_text_started = False

    def create_new_discussion(self, title):
        self.current_discussion = self.db.create_discussion(title)
        # Get the current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Chatbot conditionning
        self.condition_chatbot()
        return timestamp

    def prepare_query(self, message_id=-1):
        messages = self.current_discussion.get_messages()
        self.full_message_list = []
        for message in messages:
            if message["id"]< message_id or message_id==-1: 
                if message["type"]==self.db.MSG_TYPE_NORMAL:
                    if message["sender"]==self.personality.name:
                        self.full_message_list.append(self.personality.ai_message_prefix+message["content"])
                    else:
                        self.full_message_list.append(self.personality.user_message_prefix + message["content"])
            else:
                break

        if self.personality.processor is not None:
            preprocessed_prompt = self.personality.processor.process_model_input(message["content"])
        else:
            preprocessed_prompt = message["content"]
        if preprocessed_prompt is not None:
            self.full_message_list.append(self.personality.user_message_prefix+preprocessed_prompt+self.personality.link_text+self.personality.ai_message_prefix)
        else:
            self.full_message_list.append(self.personality.user_message_prefix+message["content"]+self.personality.link_text+self.personality.ai_message_prefix)


        link_text = self.personality.link_text

        discussion_messages = self.personality.personality_conditioning+ link_text.join(self.full_message_list)

        
        return discussion_messages, message["content"]

    def get_discussion_to(self, message_id=-1):
        messages = self.current_discussion.get_messages()
        self.full_message_list = []
        for message in messages:
            if message["id"]<= message_id or message_id==-1: 
                if message["type"]!=self.db.MSG_TYPE_CONDITIONNING:
                    if message["sender"]==self.personality.name:
                        self.full_message_list.append(self.personality.ai_message_prefix+message["content"])
                    else:
                        self.full_message_list.append(self.personality.user_message_prefix + message["content"])

        link_text = self.personality.link_text

        if len(self.full_message_list) > self.config["nb_messages_to_remember"]:
            discussion_messages = self.personality.personality_conditioning+ link_text.join(self.full_message_list[-self.config["nb_messages_to_remember"]:])
        else:
            discussion_messages = self.personality.personality_conditioning+ link_text.join(self.full_message_list)
        
        return discussion_messages # Removes the last return

    def remove_text_from_string(self, string, text_to_find):
        """
        Removes everything from the first occurrence of the specified text in the string (case-insensitive).

        Parameters:
        string (str): The original string.
        text_to_find (str): The text to find in the string.

        Returns:
        str: The updated string.
        """
        index = string.lower().find(text_to_find.lower())

        if index != -1:
            string = string[:index]

        return string
    
    def process_chunk(self, chunk, message_type:MSG_TYPE):
        """
        0 : a regular message
        1 : a notification message
        2 : A hidden message
        """
        if message_type == MSG_TYPE.MSG_TYPE_CHUNK:
            self.current_generated_text += chunk
            detected_anti_prompt = False
            anti_prompt_to_remove=""
            for prompt in self.personality.anti_prompts:
                if prompt.lower() in self.current_generated_text.lower():
                    detected_anti_prompt=True
                    anti_prompt_to_remove = prompt.lower()
                    
            if not detected_anti_prompt:
                    ASCIIColors.green(f"generated:{len(self.current_generated_text)} words", end='\r')
                    self.socketio.emit('message', {
                                                    'data': self.current_generated_text, 
                                                    'user_message_id':self.current_user_message_id, 
                                                    'ai_message_id':self.current_ai_message_id, 
                                                    'discussion_id':self.current_discussion.discussion_id,
                                                    'message_type': message_type.value
                                                }, room=self.current_room_id
                                        )
                    self.socketio.sleep(0)
                    self.current_discussion.update_message(self.current_ai_message_id, self.current_generated_text)
                    # if stop generation is detected then stop
                    if not self.cancel_gen:
                        return True
                    else:
                        self.cancel_gen = False
                        ASCIIColors.warning("Generation canceled")
                        return False
            else:
                self.current_generated_text = self.remove_text_from_string(self.current_generated_text, anti_prompt_to_remove)
                print("The model is halucinating")
                return False

        # Stream the generated text to the main process
        elif message_type == MSG_TYPE.MSG_TYPE_FULL:
            self.current_generated_text = chunk
            self.socketio.emit('message', {
                                            'data': self.current_generated_text, 
                                            'user_message_id':self.current_user_message_id, 
                                            'ai_message_id':self.current_ai_message_id, 
                                            'discussion_id':self.current_discussion.discussion_id,
                                            'message_type': message_type.value
                                        }, room=self.current_room_id
                                )
            self.socketio.sleep(0)
            return True
        # Stream the generated text to the main process
        else:
            self.socketio.emit('message', {
                                            'data': self.current_generated_text, 
                                            'user_message_id':self.current_user_message_id, 
                                            'ai_message_id':self.current_ai_message_id, 
                                            'discussion_id':self.current_discussion.discussion_id,
                                            'message_type': message_type.value
                                        }, room=self.current_room_id
                                )
            self.socketio.sleep(0)

        return True


    def generate(self, full_prompt, prompt, n_predict=50, callback=None):
        if self.personality.processor is not None:
            if self.personality.processor_cfg is not None:
                if "custom_workflow" in self.personality.processor_cfg:
                    if self.personality.processor_cfg["custom_workflow"]:
                        ASCIIColors.success("Running workflow")
                        try:
                            output = self.personality.processor.run_workflow( prompt, full_prompt, self.process_chunk)
                            self.process_chunk(output, MSG_TYPE.MSG_TYPE_FULL)
                        except Exception as ex:
                            ASCIIColors.error(f"Workflow run failed.\nError:{ex}")
                            self.process_chunk(f"Workflow run failed\nError:{ex}", MSG_TYPE.MSG_TYPE_EXCEPTION)                   
                        print("Finished executing the workflow")
                        return

        self._generate(full_prompt, n_predict, callback)
        print("Finished executing the generation")

    def _generate(self, prompt, n_predict=50, callback=None):
        self.current_generated_text = ""
        if self.model is not None:
            ASCIIColors.info("warmup")
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
                    n_predict=self.personality.model_n_predicts,
                    temperature=self.personality.model_temperature,
                    top_k=self.personality.model_top_k,
                    top_p=self.personality.model_top_p,
                    repeat_penalty=self.personality.model_repeat_penalty,
                    repeat_last_n = self.personality.model_repeat_last_n,
                    #seed=self.config['seed'],
                    n_threads=self.config['n_threads']
                )
        else:
            print("No model is installed or selected. Please make sure to install a model and select it inside your configuration before attempting to communicate with the model.")
            print("To do this: Install the model to your models/<binding name> folder.")
            print("Then set your model information in your local configuration file that you can find in configs/local_config.yaml")
            print("You can also use the ui to set your model in the settings page.")
            output = ""
        return output
                     
    def start_message_generation(self, message, message_id):
        ASCIIColors.info(f"Text generation requested by client: {self.current_room_id}")
        # send the message to the bot
        print(f"Received message : {message}")
        if self.current_discussion:
            # First we need to send the new message ID to the client
            self.current_ai_message_id = self.current_discussion.add_message(
                self.personality.name, 
                "", 
                parent = self.current_user_message_id,
                binding = self.config["binding_name"],
                model = self.config["model_name"], 
                personality = self.config["personalities"][self.config["active_personality_id"]]
            )  # first the content is empty, but we'll fill it at the end
            self.socketio.emit('infos',
                    {
                        "status":'generation_started',
                        "type": "input_message_infos",
                        "bot": self.personality.name,
                        "user": self.personality.user_name,
                        "message":message,#markdown.markdown(message),
                        "user_message_id": self.current_user_message_id,
                        "ai_message_id": self.current_ai_message_id,

                        'binding': self.current_discussion.current_message_binding,
                        'model': self.current_discussion.current_message_model,
                        'personality': self.current_discussion.current_message_personality,
                        'created_at': self.current_discussion.current_message_created_at,
                        'finished_generating_at': self.current_discussion.current_message_finished_generating_at,                        
                    }, room=self.current_room_id
            )
            self.socketio.sleep(0)

            # prepare query and reception
            self.discussion_messages, self.current_message = self.prepare_query(message_id)
            self.prepare_reception()
            self.generating = True
            self.generate(self.discussion_messages, self.current_message, n_predict = self.config['n_predict'], callback=self.process_chunk)
            print()
            print("## Done Generation ##")
            print()

            self.current_discussion.update_message(self.current_ai_message_id, self.current_generated_text)
            self.full_message_list.append(self.current_generated_text)
            self.cancel_gen = False

            # Send final message
            self.socketio.emit('final', {
                                            'data': self.current_generated_text, 
                                            'ai_message_id':self.current_ai_message_id, 
                                            'parent':self.current_user_message_id, 'discussion_id':self.current_discussion.discussion_id,
                                            "status":'model_not_ready',
                                            "type": "input_message_infos",
                                            'logo': "",
                                            "bot": self.personality.name,
                                            "user": self.personality.user_name,
                                            "message":self.current_generated_text,
                                            "user_message_id": self.current_user_message_id,
                                            "ai_message_id": self.current_ai_message_id,

                                            'binding': self.current_discussion.current_message_binding,
                                            'model': self.current_discussion.current_message_model,
                                            'personality': self.current_discussion.current_message_personality,
                                            'created_at': self.current_discussion.current_message_created_at,
                                            'finished_generating_at': self.current_discussion.current_message_finished_generating_at,

                                        }, room=self.current_room_id
                                )
            self.socketio.sleep(0)

            print()
            print("## Done ##")
            print()
        else:
            #No discussion available
            print("No discussion selected!!!")
            print("## Done ##")
            print()
            self.cancel_gen = False
            return ""
    