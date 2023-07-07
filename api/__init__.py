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
from lollms.app import LollmsApplication
import multiprocessing as mp
import threading
import time
import requests
from tqdm import tqdm 
import traceback
import sys
from lollms.console import MainMenu
import urllib
import gc

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


class LoLLMsAPPI(LollmsApplication):
    def __init__(self, config:LOLLMSConfig, socketio, config_file_path:str, lollms_paths: LollmsPaths) -> None:

        super().__init__("Lollms_webui",config, lollms_paths)
        self.is_ready = True
        
        self.socketio = socketio
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
        self.download_infos={}
        # =========================================================================================
        # Socket IO stuff    
        # =========================================================================================
        @socketio.on('connect')
        def connect():
            ASCIIColors.success(f'Client {request.sid} connected')

        @socketio.on('disconnect')
        def disconnect():
            ASCIIColors.error(f'Client {request.sid} disconnected')

        
        @socketio.on('cancel_install')
        def cancel_install(data):
            model_name = data["model_name"]
            binding_folder = data["binding_folder"]
            model_url = data["model_url"]
            signature = f"{model_name}_{binding_folder}_{model_url}"
            self.download_infos[signature]["cancel"]=True
            self.socketio.emit('canceled', {
                                            'status': True
                                            },
                                            room=self.current_room_id
                                )            
            
        @socketio.on('install_model')
        def install_model(data):
            room_id = request.sid 
            
            def get_file_size(url):
                # Send a HEAD request to retrieve file metadata
                response = urllib.request.urlopen(url)
                
                # Extract the Content-Length header value
                file_size = response.headers.get('Content-Length')
                
                # Convert the file size to integer
                if file_size:
                    file_size = int(file_size)
                
                return file_size   
                     
            def install_model_():
                print("Install model triggered")
                model_path = data["path"]
                progress = 0
                installation_dir = self.lollms_paths.personal_models_path/self.config["binding_name"]
                filename = Path(model_path).name
                installation_path = installation_dir / filename
                print("Model install requested")
                print(f"Model path : {model_path}")

                model_name = filename
                binding_folder = self.config["binding_name"]
                model_url = model_path
                signature = f"{model_name}_{binding_folder}_{model_url}"
                self.download_infos[signature]={
                    "start_time":datetime.now(),
                    "total_size":get_file_size(model_path),
                    "downloaded_size":0,
                    "progress":0,
                    "speed":0,
                    "cancel":False
                }
                
                if installation_path.exists():
                    print("Error: Model already exists")
                    socketio.emit('install_progress',{
                                                        'status': False,
                                                        'error': 'model already exists',
                                                        'model_name' : model_name,
                                                        'binding_folder' : binding_folder,
                                                        'model_url' : model_url,
                                                        'start_time': self.download_infos[signature]['start_time'].strftime("%Y-%m-%d %H:%M:%S"),
                                                        'total_size': self.download_infos[signature]['total_size'],
                                                        'downloaded_size': self.download_infos[signature]['downloaded_size'],
                                                        'progress': self.download_infos[signature]['progress'],
                                                        'speed': self.download_infos[signature]['speed'],
                                                    }, room=room_id
                                )
                
                socketio.emit('install_progress',{
                                                'status': True,
                                                'progress': progress,
                                                'model_name' : model_name,
                                                'binding_folder' : binding_folder,
                                                'model_url' : model_url,
                                                'start_time': self.download_infos[signature]['start_time'].strftime("%Y-%m-%d %H:%M:%S"),
                                                'total_size': self.download_infos[signature]['total_size'],
                                                'downloaded_size': self.download_infos[signature]['downloaded_size'],
                                                'progress': self.download_infos[signature]['progress'],
                                                'speed': self.download_infos[signature]['speed'],

                                                }, room=room_id)
                
                def callback(downloaded_size, total_size):
                    progress = (downloaded_size / total_size) * 100
                    now = datetime.now()
                    dt = (now - self.download_infos[signature]['start_time']).total_seconds()
                    speed = downloaded_size/dt
                    self.download_infos[signature]['downloaded_size'] = downloaded_size
                    self.download_infos[signature]['speed'] = speed

                    if progress - self.download_infos[signature]['progress']>2:
                        self.download_infos[signature]['progress'] = progress
                        socketio.emit('install_progress',{
                                                        'status': True,
                                                        'model_name' : model_name,
                                                        'binding_folder' : binding_folder,
                                                        'model_url' : model_url,
                                                        'start_time': self.download_infos[signature]['start_time'].strftime("%Y-%m-%d %H:%M:%S"),
                                                        'total_size': self.download_infos[signature]['total_size'],
                                                        'downloaded_size': self.download_infos[signature]['downloaded_size'],
                                                        'progress': self.download_infos[signature]['progress'],
                                                        'speed': self.download_infos[signature]['speed'],
                                                        }, room=room_id)
                    
                    if self.download_infos[signature]["cancel"]:
                        raise Exception("canceled")
                        
                    
                if hasattr(self.binding, "download_model"):
                    try:
                        self.binding.download_model(model_path, installation_path, callback)
                    except Exception as ex:
                        ASCIIColors.warning(str(ex))
                        socketio.emit('install_progress',{
                                    'status': False,
                                    'error': 'canceled',
                                    'model_name' : model_name,
                                    'binding_folder' : binding_folder,
                                    'model_url' : model_url,
                                    'start_time': self.download_infos[signature]['start_time'].strftime("%Y-%m-%d %H:%M:%S"),
                                    'total_size': self.download_infos[signature]['total_size'],
                                    'downloaded_size': self.download_infos[signature]['downloaded_size'],
                                    'progress': self.download_infos[signature]['progress'],
                                    'speed': self.download_infos[signature]['speed'],
                                }, room=room_id
                        )
                        del self.download_infos[signature]
                        try:
                            installation_path.unlink()
                        except Exception as ex:
                            ASCIIColors.error(f"Couldn't delete file. Please try to remove it manually.\n{installation_path}")
                        return

                else:
                    try:
                        self.download_file(model_path, installation_path, callback)
                    except Exception as ex:
                        ASCIIColors.warning(str(ex))
                        socketio.emit('install_progress',{
                                    'status': False,
                                    'error': 'canceled',
                                    'model_name' : model_name,
                                    'binding_folder' : binding_folder,
                                    'model_url' : model_url,
                                    'start_time': self.download_infos[signature]['start_time'].strftime("%Y-%m-%d %H:%M:%S"),
                                    'total_size': self.download_infos[signature]['total_size'],
                                    'downloaded_size': self.download_infos[signature]['downloaded_size'],
                                    'progress': self.download_infos[signature]['progress'],
                                    'speed': self.download_infos[signature]['speed'],
                                }, room=room_id
                        )
                        del self.download_infos[signature]
                        installation_path.unlink()
                        return                        
                socketio.emit('install_progress',{
                                                'status': True, 
                                                'error': '',
                                                'model_name' : model_name,
                                                'binding_folder' : binding_folder,
                                                'model_url' : model_url,
                                                'start_time': self.download_infos[signature]['start_time'].strftime("%Y-%m-%d %H:%M:%S"),
                                                'total_size': self.download_infos[signature]['total_size'],
                                                'downloaded_size': self.download_infos[signature]['downloaded_size'],
                                                'progress': 100,
                                                'speed': self.download_infos[signature]['speed'],
                                                }, room=room_id)
                del self.download_infos[signature]
                
            tpe = threading.Thread(target=install_model_, args=())
            tpe.start()

        @socketio.on('uninstall_model')
        def uninstall_model(data):
            model_path = data['path']
            installation_dir = self.lollms_paths.personal_models_path/self.config["binding_name"]
            filename = Path(model_path).name
            installation_path = installation_dir / filename
            
            model_name = filename
            binding_folder = self.config["binding_name"]

            if not installation_path.exists():
                socketio.emit('install_progress',{
                                                    'status': False,
                                                    'error': 'The model does not exist',
                                                    'model_name' : model_name,
                                                    'binding_folder' : binding_folder
                                                }, room=request.sid)
            try:
                installation_path.unlink()
            except Exception as ex:
                ASCIIColors.error(f"Couldn't delete {installation_path}, please delete it manually and restart the app")
            socketio.emit('install_progress',{
                                                'status': True, 
                                                'error': '',
                                                'model_name' : model_name,
                                                'binding_folder' : binding_folder
                                            }, room=request.sid)


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
            
        @socketio.on('cancel_generation')
        def cancel_generation():
            self.cancel_gen = True
            ASCIIColors.error(f'Client {request.sid} canceled generation')

        
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
                    message_type=MSG_TYPE.MSG_TYPE_FULL.value,
                    parent=self.message_id
                )

                self.current_user_message_id = message_id
                ASCIIColors.green("Starting message generation by"+self.personality.name)

                task = self.socketio.start_background_task(self.start_message_generation, message, message_id)
                self.socketio.sleep(0.01)
                ASCIIColors.info("Started generation task")
                #tpe = threading.Thread(target=self.start_message_generation, args=(message, message_id))
                #tpe.start()
            else:
                self.socketio.emit("buzzy", {"message":"I am buzzy. Come back later."}, room=self.current_room_id)
                self.socketio.sleep(0.01)
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
                self.socketio.sleep(0.01)

        @socketio.on('generate_msg_from')
        def handle_connection(data):
            message_id = int(data['id'])
            message = data["prompt"]
            self.current_user_message_id = message_id
            tpe = threading.Thread(target=self.start_message_generation, args=(message, message_id))
            tpe.start()
        # generation status
        self.generating=False
        ASCIIColors.blue(f"Your personal data is stored here :",end="")
        ASCIIColors.green(f"{self.lollms_paths.personal_path}")


        @socketio.on('continue_generate_msg_from')
        def handle_connection(data):
            message_id = int(data['id'])
            message = data["prompt"]
            self.current_user_message_id = message_id
            tpe = threading.Thread(target=self.start_message_generation, args=(message, message_id))
            tpe.start()
        # generation status
        self.generating=False
        ASCIIColors.blue(f"Your personal data is stored here :",end="")
        ASCIIColors.green(f"{self.lollms_paths.personal_path}")


    def rebuild_personalities(self):
        loaded = self.mounted_personalities
        loaded_names = [f"{p.language}/{p.category}/{p.personality_folder_name}" for p in loaded]
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
                personality_path = self.lollms_paths.personalities_zoo_path/f"{personality}"
                try:
                    personality = AIPersonality(personality_path,
                                                self.lollms_paths, 
                                                self.config,
                                                model=self.model,
                                                run_scripts=True)
                    mounted_personalities.append(personality)
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
                                                    run_scripts=True,
                                                    installation_option=InstallOption.FORCE_INSTALL)
                        mounted_personalities.append(personality)
                    except:
                        ASCIIColors.error(f"Couldn't load personality at {personality_path}")
                        ASCIIColors.info(f"Unmounting personality")
                        to_remove.append(i)
                        personality = AIPersonality(None,                                                    self.lollms_paths, 
                                                    self.config, 
                                                    self.model, 
                                                    run_scripts=True,
                                                    installation_option=InstallOption.FORCE_INSTALL)
                        mounted_personalities.append(personality)
                        ASCIIColors.info("Reverted to default personality")
        print(f'selected : {self.config["active_personality_id"]}')
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
    # ================================== LOLLMSApp

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
                                callback(downloaded_size, total_size)
                            progress_bar.update(len(chunk))

            if callback is not None:
                callback(total_size, total_size)

            print("File downloaded successfully")
        except Exception as e:
            print("Couldn't download file:", str(e))


   
    def condition_chatbot(self):
        if self.current_discussion is None:
            self.current_discussion = self.db.load_last_discussion()
    
        if self.personality.welcome_message!="":
            message_type = MSG_TYPE.MSG_TYPE_FULL.value# if self.personality.include_welcome_message_in_disucssion else MSG_TYPE.MSG_TYPE_FULL_INVISIBLE_TO_AI.value
            message_id = self.current_discussion.add_message(
                self.personality.name, self.personality.welcome_message,
                message_type,
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
        self.nb_received_tokens = 0
        self.full_text = ""
        self.is_bot_text_started = False

    def create_new_discussion(self, title):
        self.current_discussion = self.db.create_discussion(title)
        # Get the current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Chatbot conditionning
        self.condition_chatbot()
        return timestamp

    def prepare_query(self, message_id=-1, is_continue=False):
        messages = self.current_discussion.get_messages()
        self.full_message_list = []
        for message in messages:
            if message["id"]< message_id or message_id==-1: 
                if message["type"]==MSG_TYPE.MSG_TYPE_FULL:
                    if message["sender"]==self.personality.name:
                        self.full_message_list.append(self.personality.ai_message_prefix+message["content"])
                    else:
                        self.full_message_list.append(self.personality.user_message_prefix + message["content"])
            else:
                break

        link_text = self.personality.link_text
        if not is_continue:
            self.full_message_list.append(self.personality.user_message_prefix+message["content"]+self.personality.link_text+self.personality.ai_message_prefix)
        else:
            self.full_message_list.append(self.personality.ai_message_prefix+message["content"])


        discussion_messages = self.personality.personality_conditioning+ link_text.join(self.full_message_list)

        
        return discussion_messages, message["content"]

    def get_discussion_to(self, message_id=-1):
        messages = self.current_discussion.get_messages()
        self.full_message_list = []
        for message in messages:
            if message["id"]<= message_id or message_id==-1: 
                if message["type"]!=MSG_TYPE.MSG_TYPE_FULL_INVISIBLE_TO_USER:
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
        if message_type == MSG_TYPE.MSG_TYPE_STEP:
            ASCIIColors.info("--> Step:"+chunk)
        if message_type == MSG_TYPE.MSG_TYPE_STEP_START:
            ASCIIColors.info("--> Step started:"+chunk)
        if message_type == MSG_TYPE.MSG_TYPE_STEP_END:
            ASCIIColors.success("--> Step ended:"+chunk)
        if message_type == MSG_TYPE.MSG_TYPE_EXCEPTION:
            ASCIIColors.error("--> Exception from personality:"+chunk)
        
        if message_type == MSG_TYPE.MSG_TYPE_CHUNK:
            self.current_generated_text += chunk
            self.nb_received_tokens += 1
            ASCIIColors.green(f"Received {self.nb_received_tokens} tokens",end="\r")
            sys.stdout = sys.__stdout__
            sys.stdout.flush()
            detected_anti_prompt = False
            anti_prompt_to_remove=""
            for prompt in self.personality.anti_prompts:
                if prompt.lower() in self.current_generated_text.lower():
                    detected_anti_prompt=True
                    anti_prompt_to_remove = prompt.lower()
                    
            if not detected_anti_prompt:
                    self.socketio.emit('message', {
                                                    'data': self.current_generated_text, 
                                                    'user_message_id':self.current_user_message_id, 
                                                    'ai_message_id':self.current_ai_message_id, 
                                                    'discussion_id':self.current_discussion.discussion_id,
                                                    'message_type': MSG_TYPE.MSG_TYPE_FULL.value
                                                }, room=self.current_room_id
                                        )
                    self.socketio.sleep(0.01)
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
                ASCIIColors.warning("The model is halucinating")
                return False

        # Stream the generated text to the main process
        elif message_type == MSG_TYPE.MSG_TYPE_FULL:
            self.current_generated_text = chunk
            self.nb_received_tokens += 1
            ASCIIColors.green(f"Received {self.nb_received_tokens} tokens",end="\r",flush=True)
            self.socketio.emit('message', {
                                            'data': self.current_generated_text, 
                                            'user_message_id':self.current_user_message_id, 
                                            'ai_message_id':self.current_ai_message_id, 
                                            'discussion_id':self.current_discussion.discussion_id,
                                            'message_type': message_type.value
                                        }, room=self.current_room_id
                                )
            self.socketio.sleep(0.01)
            return True
        # Stream the generated text to the frontend
        else:
            self.socketio.emit('message', {
                                            'data': chunk, 
                                            'user_message_id':self.current_user_message_id, 
                                            'ai_message_id':self.current_ai_message_id, 
                                            'discussion_id':self.current_discussion.discussion_id,
                                            'message_type': message_type.value
                                        }, room=self.current_room_id
                                )
            self.socketio.sleep(0.01)

        return True


    def generate(self, full_prompt, prompt, n_predict=50, callback=None):
        if self.personality.processor is not None:
            ASCIIColors.success("Running workflow")
            try:
                output = self.personality.processor.run_workflow( prompt, full_prompt, self.process_chunk)
                self.process_chunk(output, MSG_TYPE.MSG_TYPE_FULL)
            except Exception as ex:
                # Catch the exception and get the traceback as a list of strings
                traceback_lines = traceback.format_exception(type(ex), ex, ex.__traceback__)
                # Join the traceback lines into a single string
                traceback_text = ''.join(traceback_lines)
                ASCIIColors.error(f"Workflow run failed.\nError:{ex}")
                ASCIIColors.error(traceback_text)
                self.process_chunk(f"Workflow run failed\nError:{ex}", MSG_TYPE.MSG_TYPE_EXCEPTION)                   
            print("Finished executing the workflow")
            return

        self._generate(full_prompt, n_predict, callback)
        print("Finished executing the generation")

    def _generate(self, prompt, n_predict=1024, callback=None):
        self.current_generated_text = ""
        self.nb_received_tokens = 0
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
                    n_predict=min(n_predict,self.personality.model_n_predicts),
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
                     
    def start_message_generation(self, message, message_id, is_continue=False):
        ASCIIColors.info(f"Text generation requested by client: {self.current_room_id}")
        # send the message to the bot
        print(f"Received message : {message}")
        if self.current_discussion:
            # First we need to send the new message ID to the client
            if is_continue:
                self.current_ai_message_id = message_id
            else:
                self.current_ai_message_id = self.current_discussion.add_message(
                    self.personality.name, 
                    "", 
                    message_type    = MSG_TYPE.MSG_TYPE_FULL.value,
                    parent          = self.current_user_message_id,
                    binding         = self.config["binding_name"],
                    model           = self.config["model_name"], 
                    personality     = self.config["personalities"][self.config["active_personality_id"]]
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
            self.socketio.sleep(0.01)

            # prepare query and reception
            self.discussion_messages, self.current_message = self.prepare_query(message_id, is_continue)
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
            self.socketio.sleep(0.01)

            ASCIIColors.success(f" ╔══════════════════════════════════════════════════╗ ")
            ASCIIColors.success(f" ║                        Done                      ║ ")
            ASCIIColors.success(f" ╚══════════════════════════════════════════════════╝ ")
        else:
            self.cancel_gen = False
            #No discussion available
            ASCIIColors.warning("No discussion selected!!!")
            self.socketio.emit('message', {
                                            'data': "No discussion selected!!!", 
                                            'user_message_id':self.current_user_message_id, 
                                            'ai_message_id':self.current_ai_message_id, 
                                            'discussion_id':0,
                                            'message_type': MSG_TYPE.MSG_TYPE_EXCEPTION.value
                                        }, room=self.current_room_id
                                )            
            print()
            return ""
    