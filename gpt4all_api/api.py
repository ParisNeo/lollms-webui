######
# Project       : GPT4ALL-UI
# File          : api.py
# Author        : ParisNeo with the help of the community
# Supported by Nomic-AI
# Licence       : Apache 2.0
# Description   : 
# A simple api to communicate with gpt4all-ui and its models.
######
import gc
import sys
from datetime import datetime
from gpt4all_api.db import DiscussionsDB
from pathlib import Path
import importlib
from pyaipersonality import AIPersonality
import multiprocessing as mp
import threading
import time
import requests
import urllib.request
from tqdm import tqdm 

__author__ = "parisneo"
__github__ = "https://github.com/nomic-ai/gpt4all-ui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"



class ModelProcess:
    def __init__(self, config=None):
        self.config = config
        self.generate_queue = mp.Queue()
        self.generation_queue = mp.Queue()
        self.cancel_queue = mp.Queue(maxsize=1)
        self.clear_queue_queue = mp.Queue(maxsize=1)
        self.set_config_queue = mp.Queue(maxsize=1)
        self.started_queue = mp.Queue()
        self.process = None
        self.is_generating  = mp.Value('i', 0)
        self.model_ready  = mp.Value('i', 0)
        self.ready = False
            
    def load_backend(self, backend_path):

        # define the full absolute path to the module
        absolute_path = backend_path.resolve()

        # infer the module name from the file path
        module_name = backend_path.stem

        # use importlib to load the module from the file path
        loader = importlib.machinery.SourceFileLoader(module_name, str(absolute_path/"__init__.py"))
        backend_module = loader.load_module()
        backend_class = getattr(backend_module, backend_module.backend_name)
        return backend_class

    def start(self):
        if self.process is None:
            self.process = mp.Process(target=self._run)
            self.process.start()

    def stop(self):
        if self.process is not None:
            self.generate_queue.put(None)
            self.process.join()
            self.process = None

    def set_backend(self, backend_path):
        self.backend = backend_path

    def set_model(self, model_path):
        self.model = model_path
        
    def set_config(self, config):
        self.set_config_queue.put(config)
        

    def generate(self, prompt, id, n_predict):
        self.generate_queue.put((prompt, id, n_predict))

    def cancel_generation(self):
        self.cancel_queue.put(('cancel',))

    def clear_queue(self):
        self.clear_queue_queue.put(('clear_queue',))
    
    def rebuild_backend(self, config):
        try:
            backend = self.load_backend(Path("backends")/config["backend"])
            print("Backend loaded successfully")
        except Exception as ex:
            print("Couldn't build backend")
            print(ex)
            backend = None
        return backend
            
    def _rebuild_model(self):
        try:
            print("Rebuilding model")
            self.backend = self.load_backend(Path("backends")/self.config["backend"])
            print("Backend loaded successfully")
            try:
                model_file = Path("models")/self.config["backend"]/self.config["model"]
                print(f"Loading model : {model_file}")
                self.model = self.backend(self.config)
                self.model_ready.value = 1
                print("Model created successfully")
            except Exception as ex:
                print("Couldn't build model")
                print(ex)
                self.model = None
        except Exception as ex:
            print("Couldn't build backend")
            print(ex)
            self.backend = None
            self.model = None

    def rebuild_personality(self):
        try:
            personality_path = f"personalities/{self.config['personality_language']}/{self.config['personality_category']}/{self.config['personality']}"
            personality = AIPersonality(personality_path)
        except Exception as ex:
            print("Personality file not found. Please verify that the personality you have selected exists or select another personality. Some updates may lead to change in personality name or category, so check the personality selection in settings to be sure.")
            if self.config["debug"]:
                print(ex)
            personality = AIPersonality()
        return personality
    
    def _rebuild_personality(self):
        try:
            personality_path = f"personalities/{self.config['personality_language']}/{self.config['personality_category']}/{self.config['personality']}"
            self.personality = AIPersonality(personality_path)
        except Exception as ex:
            print("Personality file not found. Please verify that the personality you have selected exists or select another personality. Some updates may lead to change in personality name or category, so check the personality selection in settings to be sure.")
            if self.config["debug"]:
                print(ex)
            self.personality = AIPersonality()
            
    def _run(self):        
        self._rebuild_model()
        self._rebuild_personality()
        if self.model_ready.value == 1:
            self._generate("I",0,1)
            print()
            print("Ready to receive data")
        else:
            print("No model loaded. Waiting for new configuration instructions")
                    
        self.ready = True
        print(f"Listening on :http://{self.config['host']}:{self.config['port']}")
        while True:
            try:
                self._check_set_config_queue()
                self._check_cancel_queue()
                self._check_clear_queue()

                if not self.generate_queue.empty():
                    command = self.generate_queue.get()
                    if command is None:
                        break

                    if self.cancel_queue.empty() and self.clear_queue_queue.empty():
                        self.is_generating.value = 1
                        self.started_queue.put(1)
                        self._generate(*command)
                        while not self.generation_queue.empty():
                            time.sleep(1)
                        self.is_generating.value = 0
                time.sleep(1)
            except Exception as ex:
                time.sleep(1)
                print(ex)
    def _generate(self, prompt, id, n_predict):
        if self.model is not None:
            self.id = id
            if self.config["override_personality_model_parameters"]:
                self.model.generate(
                    prompt,
                    new_text_callback=self._callback,
                    n_predict=n_predict,
                    temp=self.config['temperature'],
                    top_k=self.config['top_k'],
                    top_p=self.config['top_p'],
                    repeat_penalty=self.config['repeat_penalty'],
                    repeat_last_n = self.config['repeat_last_n'],
                    seed=self.config['seed'],
                    n_threads=self.config['n_threads']
                )
            else:
                self.model.generate(
                    prompt,
                    new_text_callback=self._callback,
                    n_predict=n_predict,
                    temp=self.personality.model_temperature,
                    top_k=self.personality.model_top_k,
                    top_p=self.personality.model_top_p,
                    repeat_penalty=self.personality.model_repeat_penalty,
                    repeat_last_n = self.personality.model_repeat_last_n,
                    #seed=self.config['seed'],
                    n_threads=self.config['n_threads']
                )
        else:
            print("No model is installed or selected. Please make sure to install a model and select it inside your configuration before attempting to communicate with the model.")
            print("To do this: Install the model to your models/<backend name> folder.")
            print("Then set your model information in your local configuration file that you can find in configs/local_default.yaml")
            print("You can also use the ui to set your model in the settings page.")
    def _callback(self, text):
        if not self.ready:
            print(".",end="")
            sys.stdout.flush()
            return True
        else:
            # Stream the generated text to the main process
            self.generation_queue.put((text,self.id))
            self._check_set_config_queue()
            self._check_cancel_queue()
            self._check_clear_queue()        
            # if stop generation is detected then stop
            if self.is_generating.value==1:
                return True
            else:
                return False

    def _check_cancel_queue(self):
        while not self.cancel_queue.empty():
            command = self.cancel_queue.get()
            if command is not None:
                self._cancel_generation()

    def _check_clear_queue(self):
        while not self.clear_queue_queue.empty():
            command = self.clear_queue_queue.get()
            if command is not None:
                self._clear_queue()

    def _check_set_config_queue(self):
        while not self.set_config_queue.empty():
            config = self.set_config_queue.get()
            if config is not None:
                self._set_config(config)

    def _cancel_generation(self):
        self.is_generating.value = 0
            
    def _clear_queue(self):
        while not self.generate_queue.empty():
            self.generate_queue.get()

    def _set_config(self, config):
        bk_cfg = self.config
        self.config = config
        print("Changing configuration")
        # verify that the backend is the same
        if self.config["backend"]!=bk_cfg["backend"] or self.config["model"]!=bk_cfg["model"]:
            self._rebuild_model()
            
        # verify that the personality is the same
        if self.config["personality"]!=bk_cfg["personality"] or self.config["personality_category"]!=bk_cfg["personality_category"] or self.config["personality_language"]!=bk_cfg["personality_language"]:
            self._rebuild_personality()


class GPT4AllAPI():
    def __init__(self, config:dict, socketio, config_file_path:str) -> None:
        self.socketio = socketio
        #Create and launch the process
        self.process = ModelProcess(config)
        self.process.start()
        self.config = config
        
        self.backend = self.process.rebuild_backend(self.config)
        self.personality = self.process.rebuild_personality()
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

        # Create database object
        self.db = DiscussionsDB(self.db_path)

        # If the database is empty, populate it with tables
        self.db.populate()

        # This is used to keep track of messages 
        self.full_message_list = []
        
        # =========================================================================================
        # Socket IO stuff    
        # =========================================================================================
        @socketio.on('connect')
        def connect():
            print('Client connected')

        @socketio.on('disconnect')
        def disconnect():
            print('Client disconnected')

        @socketio.on('install_model')
        def install_model(data):
            def install_model_():
                print("Install model triggered")
                model_path = data["path"]
                progress = 0
                installation_dir = Path(f'./models/{self.config["backend"]}/')
                filename = Path(model_path).name
                installation_path = installation_dir / filename
                print("Model install requested")
                print(f"Model path : {model_path}")

                if installation_path.exists():
                    print("Error: Model already exists")
                    socketio.emit('install_progress',{'status': 'failed', 'error': 'model already exists'})
                
                socketio.emit('install_progress',{'status': 'progress', 'progress': progress})
                
                def callback(progress):
                    socketio.emit('install_progress',{'status': 'progress', 'progress': progress})
                    
                self.download_file(model_path, installation_path, callback)
                socketio.emit('install_progress',{'status': 'succeeded', 'error': ''})
            tpe = threading.Thread(target=install_model_, args=())
            tpe.start()
            
        @socketio.on('uninstall_model')
        def uninstall_model(data):
            model_path = data['path']
            installation_dir = Path(f'./models/{self.config["backend"]}/')
            filename = Path(model_path).name
            installation_path = installation_dir / filename

            if not installation_path.exists():
                socketio.emit('install_progress',{'status': 'failed', 'error': 'The model does not exist'})

            installation_path.unlink()
            socketio.emit('install_progress',{'status': 'succeeded', 'error': ''})
            

        
        @socketio.on('generate_msg')
        def generate_msg(data):
            if self.process.model_ready.value==1:
                if self.current_discussion is None:
                    if self.db.does_last_discussion_have_messages():
                        self.current_discussion = self.db.create_discussion()
                    else:
                        self.current_discussion = self.db.load_last_discussion()

                message = data["prompt"]
                message_id = self.current_discussion.add_message(
                    "user", message, parent=self.message_id
                )

                self.current_user_message_id = message_id
                tpe = threading.Thread(target=self.start_message_generation, args=(message, message_id))
                tpe.start()
            else:
                self.socketio.emit('infos',
                        {
                            "status":'model_not_ready',
                            "type": "input_message_infos",
                            "bot": self.personality.name,
                            "user": self.personality.user_name,
                            "message":"",
                            "user_message_id": self.current_user_message_id,
                            "ai_message_id": self.current_ai_message_id,
                        }
                )

        @socketio.on('generate_msg_from')
        def handle_connection(data):
            message_id = int(data['id'])
            message = data["prompt"]
            self.current_user_message_id = message_id
            tpe = threading.Thread(target=self.start_message_generation, args=(message, message_id))
            tpe.start()
        # generation status
        self.generating=False

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



            
    def load_backend(self, backend_path):

        # define the full absolute path to the module
        absolute_path = backend_path.resolve()

        # infer the module name from the file path
        module_name = backend_path.stem

        # use importlib to load the module from the file path
        loader = importlib.machinery.SourceFileLoader(module_name, str(absolute_path/"__init__.py"))
        backend_module = loader.load_module()
        backend_class = getattr(backend_module, backend_module.backend_name)
        return backend_class

    
    def condition_chatbot(self):
        if self.current_discussion is None:
            self.current_discussion = self.db.load_last_discussion()
    
        if self.personality.welcome_message!="":
            message_id = self.current_discussion.add_message(
                self.personality.name, self.personality.welcome_message, 
                DiscussionsDB.MSG_TYPE_NORMAL,
                0,
                -1
            )
        
            self.current_ai_message_id = message_id
        return message_id

    def prepare_reception(self):
        self.bot_says = ""
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
            if message["id"]<= message_id or message_id==-1: 
                if message["type"]==self.db.MSG_TYPE_NORMAL:
                    if message["sender"]==self.personality.name:
                        self.full_message_list.append(self.personality.ai_message_prefix+message["content"])
                    else:
                        self.full_message_list.append(self.personality.user_message_prefix + message["content"])

        link_text = self.personality.link_text

        if len(self.full_message_list) > self.config["nb_messages_to_remember"]:
            discussion_messages = self.personality.personality_conditioning+ link_text.join(self.full_message_list[-self.config["nb_messages_to_remember"]:])
        else:
            discussion_messages = self.personality.personality_conditioning+ link_text.join(self.full_message_list)
        
        discussion_messages += link_text + self.personality.ai_message_prefix
        return discussion_messages # Removes the last return

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

    def process_chunk(self, chunk):
        print(chunk[0],end="")
        sys.stdout.flush()
        self.bot_says += chunk[0]
        if not self.personality.detect_antiprompt(self.bot_says):
            self.socketio.emit('message', {
                                            'data': self.bot_says, 
                                            'user_message_id':self.current_user_message_id, 
                                            'ai_message_id':self.current_ai_message_id, 
                                            'discussion_id':self.current_discussion.discussion_id
                                        }
                                )
            if self.cancel_gen:
                print("Generation canceled")
                self.process.cancel_generation()
                self.cancel_gen = False
        else:
            self.bot_says = self.remove_text_from_string(self.bot_says, self.personality.user_message_prefix.strip())
            self.process.cancel_generation()
            print("The model is halucinating")
            
    def start_message_generation(self, message, message_id):
        bot_says = ""

        # send the message to the bot
        print(f"Received message : {message}")
        if self.current_discussion:
            # First we need to send the new message ID to the client
            self.current_ai_message_id = self.current_discussion.add_message(
                self.personality.name, "", parent = self.current_user_message_id
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
                    }
            )

            # prepare query and reception
            self.discussion_messages = self.prepare_query(message_id)
            self.prepare_reception()
            self.generating = True
            print("## Generating message ##")
            self.process.generate(self.discussion_messages, message_id, n_predict = self.config['n_predict'])
            self.process.started_queue.get()
            while(self.process.is_generating.value):  # Simulating other commands being issued
                while not self.process.generation_queue.empty():
                    self.process_chunk(self.process.generation_queue.get())

            print()
            print("## Done ##")
            print()

            # Send final message
            self.socketio.emit('final', {
                                            'data': self.bot_says, 
                                            'ai_message_id':self.current_ai_message_id, 
                                            'parent':self.current_user_message_id, 'discussion_id':self.current_discussion.discussion_id
                                        }
                                )

            self.current_discussion.update_message(self.current_ai_message_id, self.bot_says)
            self.full_message_list.append(self.bot_says)
            self.cancel_gen = False      
            return bot_says
        else:
            #No discussion available
            print("No discussion selected!!!")
            print("## Done ##")
            print()
            self.cancel_gen = False
            return ""
    