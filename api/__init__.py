######
# Project       : lollms-webui
# File          : api/__init__.py
# Author        : ParisNeo with the help of the community
# license       : Apache 2.0
# Description   : 
# A simple api to communicate with lollms-webui and its models.
######
from flask import request
from datetime import datetime
from api.db import DiscussionsDB, Discussion
from pathlib import Path
from lollms.config import InstallOption
from lollms.types import MSG_TYPE, SENDER_TYPES
from lollms.extension import LOLLMSExtension, ExtensionBuilder
from lollms.personality import AIPersonality, PersonalityBuilder
from lollms.binding import LOLLMSConfig, BindingBuilder, LLMBinding, ModelBuilder, BindingType
from lollms.paths import LollmsPaths
from lollms.helpers import ASCIIColors, trace_exception
from lollms.com import NotificationType, NotificationDisplayType, LoLLMsCom
from lollms.app import LollmsApplication
from lollms.utilities import File64BitsManager, PromptReshaper, PackageManager, find_first_available_file_index
from lollms.media import WebcamImageSender, AudioRecorder
from safe_store import TextVectorizer, VectorizationMethod, VisualizationMethod
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
from typing import List, Tuple
import time

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
            ASCIIColors.yellow("Canceled successfully")

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


class LoLLMsAPI(LollmsApplication):
    def __init__(self, config:LOLLMSConfig, socketio, config_file_path:str, lollms_paths: LollmsPaths) -> None:

        self.socketio = socketio
        super().__init__("Lollms_webui",config, lollms_paths, callback=self.process_chunk)


        self.busy = False
        self.nb_received_tokens = 0
        
        self.config_file_path = config_file_path
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
            self.rec_output_folder = None
        # =========================================================================================
        # Socket IO stuff    
        # =========================================================================================
        @socketio.on('connect')
        def connect():
            #Create a new connection information
            self.connections[request.sid] = {
                "current_discussion":self.db.load_last_discussion(),
                "generated_text":"",
                "continuing": False,
                "first_chunk": True,
                "cancel_generation": False,          
                "generation_thread": None,
                "processing":False,
                "schedule_for_deletion":False
            }
            self.socketio.emit('connected', room=request.sid) 
            ASCIIColors.success(f'Client {request.sid} connected')

        @socketio.on('disconnect')
        def disconnect():
            try:
                self.socketio.emit('disconnected', room=request.sid) 
                if self.connections[request.sid]["processing"]:
                    self.connections[request.sid]["schedule_for_deletion"]=True
                else:
                    del self.connections[request.sid]
            except Exception as ex:
                pass
            
            ASCIIColors.error(f'Client {request.sid} disconnected')

        @socketio.on('take_picture')
        def take_picture():
            try:
                if not PackageManager.check_package_installed("cv2"):
                    PackageManager.install_package("opencv-python")
                import cv2
                cap = cv2.VideoCapture(0)
                n = time.time()
                while(time.time()-n<2):
                    _, frame = cap.read()
                _, frame = cap.read()
                cap.release()
                self.info("Shot taken")
                cam_shot_path = self.lollms_paths.personal_uploads_path/"camera_shots"
                cam_shot_path.mkdir(parents=True, exist_ok=True)
                filename = find_first_available_file_index(cam_shot_path, "cam_shot_", extension=".png")
                save_path = cam_shot_path/f"cam_shot_{filename}.png"  # Specify the desired folder path

                try:
                    cv2.imwrite(str(save_path), frame)
                    if not self.personality.processor is None:
                        self.personality.processor.add_file(save_path, partial(self.process_chunk, client_id = request.sid))
                        # File saved successfully
                        socketio.emit('picture_taken', {'status':True, 'progress': 100})
                    else:
                        self.personality.add_file(save_path, partial(self.process_chunk, client_id = request.sid))
                        # File saved successfully
                        socketio.emit('picture_taken', {'status':True, 'progress': 100})
                except Exception as e:
                    # Error occurred while saving the file
                    socketio.emit('picture_taken', {'status':False, 'error': str(e)})
                    

            except Exception as ex:
                trace_exception(ex)
                self.error("Couldn't use the webcam")
        
        
        @socketio.on('start_webcam_video_stream')
        def start_webcam_video_stream():
            self.webcam.start_capture()

        @socketio.on('stop_webcam_video_stream')
        def stop_webcam_video_stream():
            self.webcam.stop_capture()

        @socketio.on('start_audio_stream')
        def start_audio_stream():
            self.audio_cap.start_recording()

        @socketio.on('stop_audio_stream')
        def stop_audio_stream():
            self.audio_cap.stop_recording()


        @socketio.on('upgrade_vectorization')
        def upgrade_vectorization():
            if self.config.data_vectorization_activate and self.config.use_discussions_history:
                try:
                    self.socketio.emit('show_progress')
                    self.socketio.sleep(0)
                    ASCIIColors.yellow("0- Detected discussion vectorization request")
                    folder = self.lollms_paths.personal_databases_path/"vectorized_dbs"
                    folder.mkdir(parents=True, exist_ok=True)
                    self.build_long_term_skills_memory()
                    
                    ASCIIColors.yellow("1- Exporting discussions")
                    discussions = self.db.export_all_as_markdown_list_for_vectorization()
                    ASCIIColors.yellow("2- Adding discussions to vectorizer")
                    index = 0
                    nb_discussions = len(discussions)
                    for (title,discussion) in tqdm(discussions):
                        self.socketio.emit('update_progress',{'value':int(100*(index/nb_discussions))})
                        self.socketio.sleep(0)
                        index += 1
                        if discussion!='':
                            skill = self.learn_from_discussion(title, discussion)
                            self.long_term_memory.add_document(title, skill, chunk_size=self.config.data_vectorization_chunk_size, overlap_size=self.config.data_vectorization_overlap_size, force_vectorize=False, add_as_a_bloc=False)
                    ASCIIColors.yellow("3- Indexing database")
                    self.long_term_memory.index()
                    ASCIIColors.yellow("4- Saving database")
                    self.long_term_memory.save_to_json()
                    
                    if self.config.data_vectorization_visualize_on_vectorization:
                        self.long_term_memory.show_document(show_interactive_form=True)
                    ASCIIColors.yellow("Ready")
                except Exception as ex:
                    ASCIIColors.error(f"Couldn't vectorize database:{ex}")
            self.socketio.emit('hide_progress')
            self.socketio.sleep(0)

        @socketio.on('cancel_install')
        def cancel_install(data):
            try:
                model_name = data["model_name"]
                binding_folder = data["binding_folder"]
                model_url = data["model_url"]
                signature = f"{model_name}_{binding_folder}_{model_url}"
                self.download_infos[signature]["cancel"]=True
                self.socketio.emit('canceled', {
                                                'status': True
                                                },
                                                room=request.sid 
                                    )            
            except Exception as ex:
                trace_exception(ex)
                self.socketio.emit('canceled', {
                                                'status': False,
                                                'error':str(ex)
                                                },
                                                room=request.sid 
                                    )            

        @socketio.on('install_model')
        def install_model(data):
            room_id = request.sid            
                     
            def install_model_():
                print("Install model triggered")
                model_path = data["path"].replace("\\","/")

                if data["type"].lower() in model_path.lower():
                    model_type:str=data["type"]
                else:
                    mtt = None
                    for mt in self.binding.models_dir_names:
                        if mt.lower() in  model_path.lower():
                            mtt = mt
                            break
                    if mtt:
                        model_type = mtt
                    else:
                        model_type:str=self.binding.models_dir_names[0]

                progress = 0
                installation_dir = self.binding.searchModelParentFolder(model_path.split('/')[-1], model_type)
                if model_type=="gptq" or  model_type=="awq":
                    parts = model_path.split("/")
                    if len(parts)==2:
                        filename = parts[1]
                    else:
                        filename = parts[4]
                    installation_path = installation_dir / filename
                elif model_type=="gpt4all":
                    filename = data["variant_name"]
                    model_path = "http://gpt4all.io/models/gguf/"+filename
                    installation_path = installation_dir / filename
                else:
                    filename = Path(model_path).name
                    installation_path = installation_dir / filename
                print("Model install requested")
                print(f"Model path : {model_path}")

                model_name = filename
                binding_folder = self.config["binding_name"]
                model_url = model_path
                signature = f"{model_name}_{binding_folder}_{model_url}"
                try:
                    self.download_infos[signature]={
                        "start_time":datetime.now(),
                        "total_size":self.binding.get_file_size(model_path),
                        "downloaded_size":0,
                        "progress":0,
                        "speed":0,
                        "cancel":False
                    }
                    
                    if installation_path.exists():
                        print("Error: Model already exists. please remove it first")
                        socketio.emit('install_progress',{
                                                            'status': False,
                                                            'error': f'model already exists. Please remove it first.\nThe model can be found here:{installation_path}',
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
                        return
                    
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
                            trace_exception(ex)
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
                                if installation_path.is_dir():
                                    shutil.rmtree(installation_path)
                                else:
                                    installation_path.unlink()
                            except Exception as ex:
                                trace_exception(ex)
                                ASCIIColors.error(f"Couldn't delete file. Please try to remove it manually.\n{installation_path}")
                            return

                    else:
                        try:
                            self.download_file(model_path, installation_path, callback)
                        except Exception as ex:
                            ASCIIColors.warning(str(ex))
                            trace_exception(ex)
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
                except Exception as ex:
                    trace_exception(ex)
                    socketio.emit('install_progress',{
                                'status': False,
                                'error': str(ex),
                                'model_name' : model_name,
                                'binding_folder' : binding_folder,
                                'model_url' : model_url,
                                'start_time': '',
                                'total_size': 0,
                                'downloaded_size': 0,
                                'progress': 0,
                                'speed': 0,
                            }, room=room_id
                    )                    
            tpe = threading.Thread(target=install_model_, args=())
            tpe.start()

        @socketio.on('uninstall_model')
        def uninstall_model(data):
            model_path = data['path']
            model_type:str=data.get("type","ggml")
            installation_dir = self.binding.searchModelParentFolder(model_path)
            
            binding_folder = self.config["binding_name"]
            if model_type=="gptq" or  model_type=="awq":
                filename = model_path.split("/")[4]
                installation_path = installation_dir / filename
            else:
                filename = Path(model_path).name
                installation_path = installation_dir / filename
            model_name = filename

            if not installation_path.exists():
                socketio.emit('uninstall_progress',{
                                                    'status': False,
                                                    'error': 'The model does not exist',
                                                    'model_name' : model_name,
                                                    'binding_folder' : binding_folder
                                                }, room=request.sid)
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
                socketio.emit('uninstall_progress',{
                                                    'status': True, 
                                                    'error': '',
                                                    'model_name' : model_name,
                                                    'binding_folder' : binding_folder
                                                }, room=request.sid)
            except Exception as ex:
                trace_exception(ex)
                ASCIIColors.error(f"Couldn't delete {installation_path}, please delete it manually and restart the app")
                socketio.emit('uninstall_progress',{
                                                    'status': False, 
                                                    'error': f"Couldn't delete {installation_path}, please delete it manually and restart the app",
                                                    'model_name' : model_name,
                                                    'binding_folder' : binding_folder
                                                }, room=request.sid)

        @socketio.on('new_discussion')
        def new_discussion(data):
            client_id = request.sid
            title = data["title"]
            if self.connections[client_id]["current_discussion"] is not None:
                if self.long_term_memory is not None:
                    title, content = self.connections[client_id]["current_discussion"].export_for_vectorization()
                    skill = self.learn_from_discussion(title, content)
                    self.long_term_memory.add_document(title, skill, chunk_size=self.config.data_vectorization_chunk_size, overlap_size=self.config.data_vectorization_overlap_size, force_vectorize=False, add_as_a_bloc=False, add_to_index=True)
                    ASCIIColors.yellow("4- Saving database")
                    self.long_term_memory.save_to_json()
            self.connections[client_id]["current_discussion"] = self.db.create_discussion(title)
            # Get the current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Return a success response
            if self.connections[client_id]["current_discussion"] is None:
                self.connections[client_id]["current_discussion"] = self.db.load_last_discussion()
        
            if self.personality.welcome_message!="":
                message = self.connections[client_id]["current_discussion"].add_message(
                    message_type        = MSG_TYPE.MSG_TYPE_FULL.value if self.personality.include_welcome_message_in_disucssion else MSG_TYPE.MSG_TYPE_FULL_INVISIBLE_TO_AI.value,
                    sender_type         = SENDER_TYPES.SENDER_TYPES_AI.value,
                    sender              = self.personality.name,
                    content             = self.personality.welcome_message,
                    metadata            = None,
                    rank                = 0, 
                    parent_message_id   = -1, 
                    binding             = self.config.binding_name, 
                    model               = self.config.model_name,
                    personality         = self.config.personalities[self.config.active_personality_id], 
                    created_at=None, 
                    finished_generating_at=None
                )
 
                self.socketio.emit('discussion_created',
                            {'id':self.connections[client_id]["current_discussion"].discussion_id},
                            room=client_id
                )                        
            else:
                self.socketio.emit('discussion_created',
                            {'id':0},
                            room=client_id
                )                        

        @socketio.on('load_discussion')
        def load_discussion(data):
            client_id = request.sid
            ASCIIColors.yellow(f"Loading discussion for client {client_id} ... ", end="")
            if "id" in data:
                discussion_id = data["id"]
                self.connections[client_id]["current_discussion"] = Discussion(discussion_id, self.db)
            else:
                if self.connections[client_id]["current_discussion"] is not None:
                    discussion_id = self.connections[client_id]["current_discussion"].discussion_id
                    self.connections[client_id]["current_discussion"] = Discussion(discussion_id, self.db)
                else:
                    self.connections[client_id]["current_discussion"] = self.db.create_discussion()
            messages = self.connections[client_id]["current_discussion"].get_messages()
            jsons = [m.to_json() for m in messages]
            self.socketio.emit('discussion',
                        jsons,
                        room=client_id
            )
            ASCIIColors.green(f"ok")
                
        @socketio.on('upload_file')
        def upload_file(data):
            ASCIIColors.yellow("Uploading file")
            file = data['file']
            filename = file.filename
            save_path = self.lollms_paths.personal_uploads_path/filename  # Specify the desired folder path

            try:
                if not self.personality.processor is None:
                    file.save(save_path)
                    self.personality.processor.add_file(save_path, partial(self.process_chunk, client_id = request.sid))
                    # File saved successfully
                    socketio.emit('progress', {'status':True, 'progress': 100})

                else:
                    file.save(save_path)
                    self.personality.add_file(save_path, partial(self.process_chunk, client_id = request.sid))
                    # File saved successfully
                    socketio.emit('progress', {'status':True, 'progress': 100})
            except Exception as e:
                # Error occurred while saving the file
                socketio.emit('progress', {'status':False, 'error': str(e)})
            
        @socketio.on('cancel_generation')
        def cancel_generation():
            client_id = request.sid
            self.cancel_gen = True
            #kill thread
            ASCIIColors.error(f'Client {request.sid} requested cancelling generation')
            terminate_thread(self.connections[client_id]['generation_thread'])
            ASCIIColors.error(f'Client {request.sid} canceled generation')
            self.busy=False
            
        @socketio.on('get_personality_files')
        def get_personality_files(data):
            client_id = request.sid
            self.connections[client_id]["generated_text"]       = ""
            self.connections[client_id]["cancel_generation"]    = False
            
            try:
                self.personality.setCallback(partial(self.process_chunk,client_id = client_id))
            except Exception as ex:
                trace_exception(ex)        

        @socketio.on('send_file_chunk')
        def send_file_chunk(data):
            client_id = request.sid
            filename = data['filename']
            chunk = data['chunk']
            offset = data['offset']
            is_last_chunk = data['isLastChunk']
            chunk_index = data['chunkIndex']
            path:Path = self.lollms_paths.personal_uploads_path / self.personality.personality_folder_name
            path.mkdir(parents=True, exist_ok=True)
            file_path = path / data["filename"]
            # Save the chunk to the server or process it as needed
            # For example:
            if chunk_index==0:
                with open(file_path, 'wb') as file:
                    file.write(chunk)
            else:
                with open(file_path, 'ab') as file:
                    file.write(chunk)

            if is_last_chunk:
                print('File received and saved successfully')
                if self.personality.processor:
                    result = self.personality.processor.add_file(file_path, partial(self.process_chunk, client_id=client_id))
                else:
                    result = self.personality.add_file(file_path, partial(self.process_chunk, client_id=client_id))

                self.socketio.emit('file_received', {'status': True, 'filename': filename})
            else:
                # Request the next chunk from the client
                self.socketio.emit('request_next_chunk', {'offset': offset + len(chunk)})


        @self.socketio.on('cancel_text_generation')
        def cancel_text_generation(data):
            client_id = request.sid
            self.connections[client_id]["requested_stop"]=True
            print(f"Client {client_id} requested canceling generation")
            self.socketio.emit("generation_canceled", {"message":"Generation is canceled."}, room=client_id)
            self.socketio.sleep(0)
            self.busy = False

        @self.socketio.on('execute_python_code')
        def execute_python_code(data):
            """Executes Python code and returns the output."""
            client_id = request.sid
            code = data["code"]
            # Import the necessary modules.
            import io
            import sys
            import time

            # Create a Python interpreter.
            interpreter = io.StringIO()
            sys.stdout = interpreter

            # Execute the code.
            start_time = time.time()
            exec(code)
            end_time = time.time()

            # Get the output.
            output = interpreter.getvalue()
            self.socketio.emit("execution_output", {"output":output,"execution_time":end_time - start_time}, room=client_id)

        @self.socketio.on('create_empty_message')
        def create_empty_message(data):
            client_id = request.sid
            type = data.get("type",0)
            if type==0:
                ASCIIColors.info(f"Building empty User message requested by : {client_id}")
                # send the message to the bot
                print(f"Creating an empty message for AI answer orientation")
                if self.connections[client_id]["current_discussion"]:
                    if not self.model:
                        self.error("No model selected. Please make sure you select a model before starting generation", client_id = client_id)
                        return          
                    self.new_message(client_id, self.config.user_name, "", sender_type=SENDER_TYPES.SENDER_TYPES_USER, open=True)
                    self.socketio.sleep(0.01)            
            else:
                if self.personality is None:
                    self.warning("Select a personality")
                    return
                ASCIIColors.info(f"Building empty AI message requested by : {client_id}")
                # send the message to the bot
                print(f"Creating an empty message for AI answer orientation")
                if self.connections[client_id]["current_discussion"]:
                    if not self.model:
                        self.error("No model selected. Please make sure you select a model before starting generation", client_id=client_id)
                        return          
                    self.new_message(client_id, self.personality.name, "[edit this to put your ai answer start]", open=True)
                    self.socketio.sleep(0.01)            

        # A copy of the original lollms-server generation code needed for playground
        @self.socketio.on('generate_text')
        def handle_generate_text(data):
            client_id = request.sid
            self.cancel_gen = False
            ASCIIColors.info(f"Text generation requested by client: {client_id}")
            if self.busy:
                self.socketio.emit("busy", {"message":"I am busy. Come back later."}, room=client_id)
                self.socketio.sleep(0)
                ASCIIColors.warning(f"OOps request {client_id}  refused!! Server busy")
                return
            def generate_text():
                self.busy = True
                try:
                    model = self.model
                    self.connections[client_id]["is_generating"]=True
                    self.connections[client_id]["requested_stop"]=False
                    prompt          = data['prompt']
                    tokenized = model.tokenize(prompt)
                    personality_id  = data.get('personality', -1)

                    n_crop          = data.get('n_crop', len(tokenized))
                    if n_crop!=-1:
                        prompt          = model.detokenize(tokenized[-n_crop:])

                    n_predicts      = data["n_predicts"]
                    parameters      = data.get("parameters",{
                        "temperature":self.config["temperature"],
                        "top_k":self.config["top_k"],
                        "top_p":self.config["top_p"],
                        "repeat_penalty":self.config["repeat_penalty"],
                        "repeat_last_n":self.config["repeat_last_n"],
                        "seed":self.config["seed"]
                    })

                    if personality_id==-1:
                        # Raw text generation
                        self.answer = {"full_text":""}
                        def callback(text, message_type: MSG_TYPE, metadata:dict={}):
                            if message_type == MSG_TYPE.MSG_TYPE_CHUNK:
                                ASCIIColors.success(f"generated:{len(self.answer['full_text'].split())} words", end='\r')
                                self.answer["full_text"] = self.answer["full_text"] + text
                                self.socketio.emit('text_chunk', {'chunk': text, 'type':MSG_TYPE.MSG_TYPE_CHUNK.value}, room=client_id)
                                self.socketio.sleep(0)
                            if client_id in self.connections:# Client disconnected                      
                                if self.connections[client_id]["requested_stop"]:
                                    return False
                                else:
                                    return True
                            else:
                                return False                            

                        tk = model.tokenize(prompt)
                        n_tokens = len(tk)
                        fd = model.detokenize(tk[-min(self.config.ctx_size-n_predicts,n_tokens):])

                        try:
                            ASCIIColors.print("warming up", ASCIIColors.color_bright_cyan)
                            
                            generated_text = model.generate(fd, 
                                                            n_predict=n_predicts, 
                                                            callback=callback,
                                                            temperature = parameters["temperature"],
                                                            top_k = parameters["top_k"],
                                                            top_p = parameters["top_p"],
                                                            repeat_penalty = parameters["repeat_penalty"],
                                                            repeat_last_n = parameters["repeat_last_n"],
                                                            seed = parameters["seed"],                                           
                                                            )
                            ASCIIColors.success(f"\ndone")

                            if client_id in self.connections:
                                if not self.connections[client_id]["requested_stop"]:
                                    # Emit the generated text to the client
                                    self.socketio.emit('text_generated', {'text': generated_text}, room=client_id)                
                                    self.socketio.sleep(0)
                        except Exception as ex:
                            self.socketio.emit('generation_error', {'error': str(ex)}, room=client_id)
                            ASCIIColors.error(f"\ndone")
                        self.busy = False
                    else:
                        try:
                            personality: AIPersonality = self.personalities[personality_id]
                            ump = self.config.discussion_prompt_separator +self.config.user_name.strip() if self.config.use_user_name_in_discussions else self.personality.user_message_prefix
                            personality.model = model
                            cond_tk = personality.model.tokenize(personality.personality_conditioning)
                            n_cond_tk = len(cond_tk)
                            # Placeholder code for text generation
                            # Replace this with your actual text generation logic
                            print(f"Text generation requested by client: {client_id}")

                            self.answer["full_text"] = ''
                            full_discussion_blocks = self.connections[client_id]["full_discussion_blocks"]

                            if prompt != '':
                                if personality.processor is not None and personality.processor_cfg["process_model_input"]:
                                    preprocessed_prompt = personality.processor.process_model_input(prompt)
                                else:
                                    preprocessed_prompt = prompt
                                
                                if personality.processor is not None and personality.processor_cfg["custom_workflow"]:
                                    full_discussion_blocks.append(ump)
                                    full_discussion_blocks.append(preprocessed_prompt)
                            
                                else:

                                    full_discussion_blocks.append(ump)
                                    full_discussion_blocks.append(preprocessed_prompt)
                                    full_discussion_blocks.append(personality.link_text)
                                    full_discussion_blocks.append(personality.ai_message_prefix)

                            full_discussion = personality.personality_conditioning + ''.join(full_discussion_blocks)

                            def callback(text, message_type: MSG_TYPE, metadata:dict={}):
                                if message_type == MSG_TYPE.MSG_TYPE_CHUNK:
                                    self.answer["full_text"] = self.answer["full_text"] + text
                                    self.socketio.emit('text_chunk', {'chunk': text}, room=client_id)
                                    self.socketio.sleep(0)
                                try:
                                    if self.connections[client_id]["requested_stop"]:
                                        return False
                                    else:
                                        return True
                                except: # If the client is disconnected then we stop talking to it
                                    return False

                            tk = personality.model.tokenize(full_discussion)
                            n_tokens = len(tk)
                            fd = personality.model.detokenize(tk[-min(self.config.ctx_size-n_cond_tk-personality.model_n_predicts,n_tokens):])
                            
                            if personality.processor is not None and personality.processor_cfg["custom_workflow"]:
                                ASCIIColors.info("processing...")
                                generated_text = personality.processor.run_workflow(prompt, previous_discussion_text=personality.personality_conditioning+fd, callback=callback)
                            else:
                                ASCIIColors.info("generating...")
                                generated_text = personality.model.generate(
                                                                            personality.personality_conditioning+fd, 
                                                                            n_predict=personality.model_n_predicts, 
                                                                            callback=callback)

                            if personality.processor is not None and personality.processor_cfg["process_model_output"]: 
                                generated_text = personality.processor.process_model_output(generated_text)

                            full_discussion_blocks.append(generated_text.strip())
                            ASCIIColors.success("\ndone")

                            # Emit the generated text to the client
                            self.socketio.emit('text_generated', {'text': generated_text}, room=client_id)
                            self.socketio.sleep(0)
                        except Exception as ex:
                            self.socketio.emit('generation_error', {'error': str(ex)}, room=client_id)
                            ASCIIColors.error(f"\ndone")
                        self.busy = False
                except Exception as ex:
                        trace_exception(ex)
                        self.socketio.emit('generation_error', {'error': str(ex)}, room=client_id)
                        self.busy = False

            # Start the text generation task in a separate thread
            task = self.socketio.start_background_task(target=generate_text)

        @socketio.on('execute_command')
        def execute_command(data):
            client_id = request.sid
            command = data["command"]
            parameters = data["parameters"]
            if self.personality.processor is not None:
                self.start_time = datetime.now()
                self.personality.processor.callback = partial(self.process_chunk, client_id=client_id)
                self.personality.processor.execute_command(command, parameters)
            else:
                self.warning("Non scripted personalities do not support commands",client_id=client_id)
            self.close_message(client_id)
        @socketio.on('generate_msg')
        def generate_msg(data):
            client_id = request.sid
            self.cancel_gen = False
            self.connections[client_id]["generated_text"]=""
            self.connections[client_id]["cancel_generation"]=False
            self.connections[client_id]["continuing"]=False
            self.connections[client_id]["first_chunk"]=True
            

            
            if not self.model:
                ASCIIColors.error("Model not selected. Please select a model")
                self.error("Model not selected. Please select a model", client_id=client_id)
                return
 
            if not self.busy:
                if self.connections[client_id]["current_discussion"] is None:
                    if self.db.does_last_discussion_have_messages():
                        self.connections[client_id]["current_discussion"] = self.db.create_discussion()
                    else:
                        self.connections[client_id]["current_discussion"] = self.db.load_last_discussion()

                prompt = data["prompt"]
                ump = self.config.discussion_prompt_separator +self.config.user_name.strip() if self.config.use_user_name_in_discussions else self.personality.user_message_prefix
                message = self.connections[client_id]["current_discussion"].add_message(
                    message_type    = MSG_TYPE.MSG_TYPE_FULL.value,
                    sender_type     = SENDER_TYPES.SENDER_TYPES_USER.value,
                    sender          = ump.replace(self.config.discussion_prompt_separator,"").replace(":",""),
                    content=prompt,
                    metadata=None,
                    parent_message_id=self.message_id
                )

                ASCIIColors.green("Starting message generation by "+self.personality.name)
                self.connections[client_id]['generation_thread'] = threading.Thread(target=self.start_message_generation, args=(message, message.id, client_id))
                self.connections[client_id]['generation_thread'].start()
                
                self.socketio.sleep(0.01)
                ASCIIColors.info("Started generation task")
                self.busy=True
                #tpe = threading.Thread(target=self.start_message_generation, args=(message, message_id, client_id))
                #tpe.start()
            else:
                self.error("I am busy. Come back later.", client_id=client_id)

        @socketio.on('generate_msg_from')
        def generate_msg_from(data):
            client_id = request.sid
            self.cancel_gen = False
            self.connections[client_id]["continuing"]=False
            self.connections[client_id]["first_chunk"]=True
            
            if self.connections[client_id]["current_discussion"] is None:
                ASCIIColors.warning("Please select a discussion")
                self.error("Please select a discussion first", client_id=client_id)
                return
            id_ = data['id']
            generation_type = data.get('msg_type',None)
            if id_==-1:
                message = self.connections[client_id]["current_discussion"].current_message
            else:
                message = self.connections[client_id]["current_discussion"].load_message(id_)
            if message is None:
                return            
            self.connections[client_id]['generation_thread'] = threading.Thread(target=self.start_message_generation, args=(message, message.id, client_id, False, generation_type))
            self.connections[client_id]['generation_thread'].start()

        @socketio.on('continue_generate_msg_from')
        def handle_connection(data):
            client_id = request.sid
            self.cancel_gen = False
            self.connections[client_id]["continuing"]=True
            self.connections[client_id]["first_chunk"]=True
            
            if self.connections[client_id]["current_discussion"] is None:
                ASCIIColors.yellow("Please select a discussion")
                self.error("Please select a discussion", client_id=client_id)
                return
            id_ = data['id']
            if id_==-1:
                message = self.connections[client_id]["current_discussion"].current_message
            else:
                message = self.connections[client_id]["current_discussion"].load_message(id_)

            self.connections[client_id]["generated_text"]=message.content
            self.connections[client_id]['generation_thread'] = threading.Thread(target=self.start_message_generation, args=(message, message.id, client_id, True))
            self.connections[client_id]['generation_thread'].start()

        # generation status
        self.generating=False
        ASCIIColors.blue(f"Your personal data is stored here :",end="")
        ASCIIColors.green(f"{self.lollms_paths.personal_path}")

    def audio_callback(self, output):
        if self.summoned:
            client_id = 0
            self.cancel_gen = False
            self.connections[client_id]["generated_text"]=""
            self.connections[client_id]["cancel_generation"]=False
            self.connections[client_id]["continuing"]=False
            self.connections[client_id]["first_chunk"]=True
            
            if not self.model:
                ASCIIColors.error("Model not selected. Please select a model")
                self.error("Model not selected. Please select a model", client_id=client_id)
                return
 
            if not self.busy:
                if self.connections[client_id]["current_discussion"] is None:
                    if self.db.does_last_discussion_have_messages():
                        self.connections[client_id]["current_discussion"] = self.db.create_discussion()
                    else:
                        self.connections[client_id]["current_discussion"] = self.db.load_last_discussion()

                prompt = text
                ump = self.config.discussion_prompt_separator +self.config.user_name.strip() if self.config.use_user_name_in_discussions else self.personality.user_message_prefix
                message = self.connections[client_id]["current_discussion"].add_message(
                    message_type    = MSG_TYPE.MSG_TYPE_FULL.value,
                    sender_type     = SENDER_TYPES.SENDER_TYPES_USER.value,
                    sender          = ump.replace(self.config.discussion_prompt_separator,"").replace(":",""),
                    content=prompt,
                    metadata=None,
                    parent_message_id=self.message_id
                )

                ASCIIColors.green("Starting message generation by "+self.personality.name)
                self.connections[client_id]['generation_thread'] = threading.Thread(target=self.start_message_generation, args=(message, message.id, client_id))
                self.connections[client_id]['generation_thread'].start()
                
                self.socketio.sleep(0.01)
                ASCIIColors.info("Started generation task")
                self.busy=True
                #tpe = threading.Thread(target=self.start_message_generation, args=(message, message_id, client_id))
                #tpe.start()
            else:
                self.error("I am busy. Come back later.", client_id=client_id)
        else:
            if output["text"].lower()=="lollms":
                self.summoned = True
    def rebuild_personalities(self, reload_all=False):
        if reload_all:
            self.mounted_personalities=[]

        loaded = self.mounted_personalities
        loaded_names = [f"{p.category}/{p.personality_folder_name}:{p.selected_language}" if p.selected_language else f"{p.category}/{p.personality_folder_name}" for p in loaded]
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
        discussion_messages = "!@>instruction: Create a short title to this discussion\n"
        discussion_title = "\n!@>Discussion title:"

        available_space = self.config.ctx_size - 150 - len(self.model.tokenize(discussion_messages))- len(self.model.tokenize(discussion_title))
        # Initialize a list to store the full messages
        full_message_list = []        
        # Accumulate messages until the cumulative number of tokens exceeds available_space
        tokens_accumulated = 0
        # Accumulate messages starting from message_index
        for message in messages:
            # Check if the message content is not empty and visible to the AI
            if message.content != '' and (
                    message.message_type <= MSG_TYPE.MSG_TYPE_FULL_INVISIBLE_TO_USER.value and message.message_type != MSG_TYPE.MSG_TYPE_FULL_INVISIBLE_TO_AI.value):

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
                        message_type:MSG_TYPE
                    ):
            if chunk:
                title[0] += chunk
            antiprompt = self.personality.detect_antiprompt(title[0])
            if antiprompt:
                ASCIIColors.warning(f"\nDetected hallucination with antiprompt: {antiprompt}")
                title[0] = self.remove_text_from_string(title[0],antiprompt)
                return False
            else:
                return True
            
        self._generate(discussion_messages, 150, client_id, receive)
        ASCIIColors.info(title[0])
        return title[0]
   

    def prepare_reception(self, client_id):
        if not self.connections[client_id]["continuing"]:
            self.connections[client_id]["generated_text"] = ""
            
        self.connections[client_id]["first_chunk"]=True
            
        self.nb_received_tokens = 0
        self.start_time = datetime.now()

    def prepare_query(self, client_id: str, message_id: int = -1, is_continue: bool = False, n_tokens: int = 0, generation_type = None) -> Tuple[str, str, List[str]]:
        """
        Prepares the query for the model.

        Args:
            client_id (str): The client ID.
            message_id (int): The message ID. Default is -1.
            is_continue (bool): Whether the query is a continuation. Default is False.
            n_tokens (int): The number of tokens. Default is 0.

        Returns:
            Tuple[str, str, List[str]]: The prepared query, original message content, and tokenized query.
        """

        # Get the list of messages
        messages = self.connections[client_id]["current_discussion"].get_messages()

        # Find the index of the message with the specified message_id
        message_index = -1
        for i, message in enumerate(messages):
            if message.id == message_id:
                message_index = i
                break
        
        # Define current message
        current_message = messages[message_index]

        # Build the conditionning text block
        conditionning = self.personality.personality_conditioning

        # Check if there are document files to add to the prompt
        documentation = ""
        history = ""

        if generation_type != "simple_question":
            if self.personality.persona_data_vectorizer:
                if documentation=="":
                    documentation="!@>Documentation:\n"

                if self.config.data_vectorization_build_keys_words:
                    query = self.personality.fast_gen("!@>prompt:"+current_message.content+"\n!@>instruction: Convert the prompt to a web search query."+"\nDo not answer the prompt. Do not add explanations. Use comma separated syntax to make a list of keywords in the same line.\nThe keywords should reflect the ideas written in the prompt so that a seach engine can process them efficiently.\n!@>query: ", max_generation_size=256, show_progress=True)
                    ASCIIColors.cyan(f"Query:{query}")
                else:
                    query = current_message.content

                docs, sorted_similarities = self.personality.persona_data_vectorizer.recover_text(query, top_k=self.config.data_vectorization_nb_chunks)
                for doc, infos in zip(docs, sorted_similarities):
                    documentation += f"document chunk:\n{doc}"

            
            if len(self.personality.text_files) > 0 and self.personality.vectorizer:
                if documentation=="":
                    documentation="!@>Documentation:\n"

                if self.config.data_vectorization_build_keys_words:
                    query = self.personality.fast_gen("!@>prompt:"+current_message.content+"\n!@>instruction: Convert the prompt to a web search query."+"\nDo not answer the prompt. Do not add explanations. Use comma separated syntax to make a list of keywords in the same line.\nThe keywords should reflect the ideas written in the prompt so that a seach engine can process them efficiently.\n!@>query: ", max_generation_size=256, show_progress=True)
                    ASCIIColors.cyan(f"Query:{query}")
                else:
                    query = current_message.content

                docs, sorted_similarities = self.personality.vectorizer.recover_text(query, top_k=self.config.data_vectorization_nb_chunks)
                for doc, infos in zip(docs, sorted_similarities):
                    documentation += f"document chunk:\nchunk path: {infos[0]}\nchunk content:{doc}"

            # Check if there is discussion history to add to the prompt
            if self.config.use_discussions_history and self.long_term_memory is not None:
                if history=="":
                    history="!@>previous discussions:\n"
                docs, sorted_similarities = self.long_term_memory.recover_text(current_message.content, top_k=self.config.data_vectorization_nb_chunks)
                for i,(doc, infos) in enumerate(zip(docs, sorted_similarities)):
                    history += f"!@>previous discussion {i}:\n!@>discussion title:\n{infos[0]}\ndiscussion content:\n{doc}"

        # Add information about the user
        user_description=""
        if self.config.use_user_name_in_discussions:
            user_description="!@>User description:\n"+self.config.user_description


        # Tokenize the conditionning text and calculate its number of tokens
        tokens_conditionning = self.model.tokenize(conditionning)
        n_cond_tk = len(tokens_conditionning)

        # Tokenize the documentation text and calculate its number of tokens
        if len(documentation)>0:
            tokens_documentation = self.model.tokenize(documentation)
            n_doc_tk = len(tokens_documentation)
        else:
            tokens_documentation = []
            n_doc_tk = 0

        # Tokenize the history text and calculate its number of tokens
        if len(history)>0:
            tokens_history = self.model.tokenize(history)
            n_history_tk = len(tokens_history)
        else:
            tokens_history = []
            n_history_tk = 0


        # Tokenize user description
        if len(user_description)>0:
            tokens_user_description = self.model.tokenize(user_description)
            n_user_description_tk = len(tokens_user_description)
        else:
            tokens_user_description = []
            n_user_description_tk = 0


        # Calculate the total number of tokens between conditionning, documentation, and history
        total_tokens = n_cond_tk + n_doc_tk + n_history_tk + n_user_description_tk

        # Calculate the available space for the messages
        available_space = self.config.ctx_size - n_tokens - total_tokens

        # Raise an error if the available space is 0 or less
        if available_space<1:
            raise Exception("Not enough space in context!!")

        # Accumulate messages until the cumulative number of tokens exceeds available_space
        tokens_accumulated = 0


        # Initialize a list to store the full messages
        full_message_list = []
        # If this is not a continue request, we add the AI prompt
        if not is_continue:
            message_tokenized = self.model.tokenize(
                "\n" +self.personality.ai_message_prefix.strip()
            )
            full_message_list.append(message_tokenized)
            # Update the cumulative number of tokens
            tokens_accumulated += len(message_tokenized)


        if generation_type != "simple_question":
            # Accumulate messages starting from message_index
            for i in range(message_index, -1, -1):
                message = messages[i]

                # Check if the message content is not empty and visible to the AI
                if message.content != '' and (
                        message.message_type <= MSG_TYPE.MSG_TYPE_FULL_INVISIBLE_TO_USER.value and message.message_type != MSG_TYPE.MSG_TYPE_FULL_INVISIBLE_TO_AI.value):

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
        else:
            message = messages[message_index]

            # Check if the message content is not empty and visible to the AI
            if message.content != '' and (
                    message.message_type <= MSG_TYPE.MSG_TYPE_FULL_INVISIBLE_TO_USER.value and message.message_type != MSG_TYPE.MSG_TYPE_FULL_INVISIBLE_TO_AI.value):

                # Tokenize the message content
                message_tokenized = self.model.tokenize(
                    "\n" + self.config.discussion_prompt_separator + message.sender + ": " + message.content.strip())

                # Add the tokenized message to the full_message_list
                full_message_list.insert(0, message_tokenized)

                # Update the cumulative number of tokens
                tokens_accumulated += len(message_tokenized)

        # Build the final discussion messages by detokenizing the full_message_list
        discussion_messages = ""
        for message_tokens in full_message_list:
            discussion_messages += self.model.detokenize(message_tokens)

        # Build the final prompt by concatenating the conditionning and discussion messages
        prompt_data = conditionning + documentation + history + user_description + discussion_messages

        # Tokenize the prompt data
        tokens = self.model.tokenize(prompt_data)

        # if this is a debug then show prompt construction details
        if self.config["debug"]:
            ASCIIColors.bold("CONDITIONNING")
            ASCIIColors.yellow(conditionning)
            ASCIIColors.bold("DOC")
            ASCIIColors.yellow(documentation)
            ASCIIColors.bold("HISTORY")
            ASCIIColors.yellow(history)
            ASCIIColors.bold("DISCUSSION")
            ASCIIColors.hilight(discussion_messages,"!@>",ASCIIColors.color_yellow,ASCIIColors.color_bright_red,False)
            ASCIIColors.bold("Final prompt")
            ASCIIColors.hilight(prompt_data,"!@>",ASCIIColors.color_yellow,ASCIIColors.color_bright_red,False)
            ASCIIColors.info(f"prompt size:{len(tokens)} tokens") 
            ASCIIColors.info(f"available space after doc and history:{available_space} tokens") 

        # Return the prepared query, original message content, and tokenized query
        return prompt_data, current_message.content, tokens


    def get_discussion_to(self, client_id,  message_id=-1):
        messages = self.connections[client_id]["current_discussion"].get_messages()
        full_message_list = []
        ump = self.config.discussion_prompt_separator +self.config.user_name.strip() if self.config.use_user_name_in_discussions else self.personality.user_message_prefix

        for message in messages:
            if message["id"]<= message_id or message_id==-1: 
                if message["type"]!=MSG_TYPE.MSG_TYPE_FULL_INVISIBLE_TO_USER:
                    if message["sender"]==self.personality.name:
                        full_message_list.append(self.personality.ai_message_prefix+message["content"])
                    else:
                        full_message_list.append(ump + message["content"])

        link_text = "\n"# self.personality.link_text

        if len(full_message_list) > self.config["nb_messages_to_remember"]:
            discussion_messages = self.personality.personality_conditioning+ link_text.join(full_message_list[-self.config["nb_messages_to_remember"]:])
        else:
            discussion_messages = self.personality.personality_conditioning+ link_text.join(full_message_list)
        
        return discussion_messages # Removes the last return

    def notify(
                self, 
                content, 
                notification_type:NotificationType=NotificationType.NOTIF_SUCCESS, 
                duration:int=4, 
                client_id=None, 
                display_type:NotificationDisplayType=NotificationDisplayType.TOAST,
                verbose=True
            ):
        self.socketio.emit('notification', {
                            'content': content,# self.connections[client_id]["generated_text"], 
                            'notification_type': notification_type.value,
                            "duration": duration,
                            'display_type':display_type.value
                        }, room=client_id
                        )  
        self.socketio.sleep(0.01)
        if verbose:
            if notification_type==NotificationType.NOTIF_SUCCESS:
                ASCIIColors.success(content)
            elif notification_type==NotificationType.NOTIF_INFO:
                ASCIIColors.info(content)
            elif notification_type==NotificationType.NOTIF_WARNING:
                ASCIIColors.warning(content)
            else:
                ASCIIColors.red(content)


    def new_message(self, 
                            client_id, 
                            sender=None, 
                            content="",
                            parameters=None,
                            metadata=None,
                            ui=None,
                            message_type:MSG_TYPE=MSG_TYPE.MSG_TYPE_FULL, 
                            sender_type:SENDER_TYPES=SENDER_TYPES.SENDER_TYPES_AI,
                            open=False
                        ):
        
        mtdt = metadata if metadata is None or type(metadata) == str else json.dumps(metadata, indent=4)
        if sender==None:
            sender= self.personality.name
        msg = self.connections[client_id]["current_discussion"].add_message(
            message_type        = message_type.value,
            sender_type         = sender_type.value,
            sender              = sender,
            content             = content,
            metadata            = mtdt,
            ui                  = ui,
            rank                = 0,
            parent_message_id   = self.connections[client_id]["current_discussion"].current_message.id,
            binding             = self.config["binding_name"],
            model               = self.config["model_name"], 
            personality         = self.config["personalities"][self.config["active_personality_id"]],
        )  # first the content is empty, but we'll fill it at the end  

        self.socketio.emit('new_message',
                {
                    "sender":                   sender,
                    "message_type":             message_type.value,
                    "sender_type":              SENDER_TYPES.SENDER_TYPES_AI.value,
                    "content":                  content,
                    "parameters":               parameters,
                    "metadata":                 metadata,
                    "ui":                       ui,
                    "id":                       msg.id,
                    "parent_message_id":        msg.parent_message_id,

                    'binding':                  self.config["binding_name"],
                    'model' :                   self.config["model_name"], 
                    'personality':              self.config["personalities"][self.config["active_personality_id"]],

                    'created_at':               self.connections[client_id]["current_discussion"].current_message.created_at,
                    'finished_generating_at':   self.connections[client_id]["current_discussion"].current_message.finished_generating_at,

                    'open':                     open
                }, room=client_id
        )

    def update_message(self, client_id, chunk,                             
                            parameters=None,
                            metadata=[], 
                            ui=None,
                            msg_type:MSG_TYPE=None
                        ):
        self.connections[client_id]["current_discussion"].current_message.finished_generating_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        mtdt = json.dumps(metadata, indent=4) if metadata is not None and type(metadata)== list else metadata
        if self.nb_received_tokens==1:
            self.socketio.emit('update_message', {
                                            "sender": self.personality.name,
                                            'id':self.connections[client_id]["current_discussion"].current_message.id, 
                                            'content': "✍ warming up ...",# self.connections[client_id]["generated_text"],
                                            'ui': ui,
                                            'discussion_id':self.connections[client_id]["current_discussion"].discussion_id,
                                            'message_type': MSG_TYPE.MSG_TYPE_STEP_END.value,
                                            'finished_generating_at': self.connections[client_id]["current_discussion"].current_message.finished_generating_at,
                                            'parameters':parameters,
                                            'metadata':metadata
                                        }, room=client_id
                                )


        self.socketio.emit('update_message', {
                                        "sender": self.personality.name,
                                        'id':self.connections[client_id]["current_discussion"].current_message.id, 
                                        'content': chunk,# self.connections[client_id]["generated_text"],
                                        'ui': ui,
                                        'discussion_id':self.connections[client_id]["current_discussion"].discussion_id,
                                        'message_type': msg_type.value if msg_type is not None else MSG_TYPE.MSG_TYPE_CHUNK.value if self.nb_received_tokens>1 else MSG_TYPE.MSG_TYPE_FULL.value,
                                        'finished_generating_at': self.connections[client_id]["current_discussion"].current_message.finished_generating_at,
                                        'parameters':parameters,
                                        'metadata':metadata
                                    }, room=client_id
                            )
        self.socketio.sleep(0.01)
        if msg_type != MSG_TYPE.MSG_TYPE_INFO:
            self.connections[client_id]["current_discussion"].update_message(self.connections[client_id]["generated_text"], new_metadata=mtdt, new_ui=ui)



    def close_message(self, client_id):
        if not self.connections[client_id]["current_discussion"]:
            return
        #fix halucination
        self.connections[client_id]["generated_text"]=self.connections[client_id]["generated_text"].split("!@>")[0]
        # Send final message
        self.connections[client_id]["current_discussion"].current_message.finished_generating_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.socketio.emit('close_message', {
                                        "sender": self.personality.name,
                                        "id": self.connections[client_id]["current_discussion"].current_message.id,
                                        "content":self.connections[client_id]["generated_text"],

                                        'binding': self.config["binding_name"],
                                        'model' : self.config["model_name"], 
                                        'personality':self.config["personalities"][self.config["active_personality_id"]],

                                        'created_at': self.connections[client_id]["current_discussion"].current_message.created_at,
                                        'finished_generating_at': self.connections[client_id]["current_discussion"].current_message.finished_generating_at,

                                    }, room=client_id
                            )
    def process_chunk(
                        self, 
                        chunk:str, 
                        message_type:MSG_TYPE,
                        parameters:dict=None, 
                        metadata:list=None, 
                        client_id:int=0,
                        personality:AIPersonality=None
                    ):
        """
        Processes a chunk of generated text
        """
        if chunk is None:
            return True
        if not client_id in list(self.connections.keys()):
            self.error("Connection lost", client_id=client_id)
            return
        if message_type == MSG_TYPE.MSG_TYPE_STEP:
            ASCIIColors.info("--> Step:"+chunk)
        if message_type == MSG_TYPE.MSG_TYPE_STEP_START:
            ASCIIColors.info("--> Step started:"+chunk)
        if message_type == MSG_TYPE.MSG_TYPE_STEP_END:
            if parameters['status']:
                ASCIIColors.success("--> Step ended:"+chunk)
            else:
                ASCIIColors.error("--> Step ended:"+chunk)
        if message_type == MSG_TYPE.MSG_TYPE_EXCEPTION:
            self.error(chunk, client_id=client_id)
            ASCIIColors.error("--> Exception from personality:"+chunk)
        if message_type == MSG_TYPE.MSG_TYPE_WARNING:
            self.warning(chunk,client_id=client_id)
            ASCIIColors.error("--> Exception from personality:"+chunk)
        if message_type == MSG_TYPE.MSG_TYPE_INFO:
            self.info(chunk, client_id=client_id)
            ASCIIColors.info("--> Info:"+chunk)
        if message_type == MSG_TYPE.MSG_TYPE_UI:
            self.update_message(client_id, "", parameters, metadata, chunk, MSG_TYPE.MSG_TYPE_UI)

        if message_type == MSG_TYPE.MSG_TYPE_NEW_MESSAGE:
            self.nb_received_tokens = 0
            self.start_time = datetime.now()
            self.new_message(
                                client_id, 
                                self.personality.name if personality is None else personality.name, 
                                chunk if parameters["type"]!=MSG_TYPE.MSG_TYPE_UI.value else '', 
                                metadata = [{
                                    "title":chunk,
                                    "content":parameters["metadata"]
                                    }
                                ] if parameters["type"]==MSG_TYPE.MSG_TYPE_JSON_INFOS.value else None, 
                                ui= chunk if parameters["type"]==MSG_TYPE.MSG_TYPE_UI.value else None, 
                                message_type= MSG_TYPE(parameters["type"]))

        elif message_type == MSG_TYPE.MSG_TYPE_FINISHED_MESSAGE:
            self.close_message(client_id)

        elif message_type == MSG_TYPE.MSG_TYPE_CHUNK:
            if self.nb_received_tokens==0:
                self.start_time = datetime.now()
            dt =(datetime.now() - self.start_time).seconds
            if dt==0:
                dt=1
            spd = self.nb_received_tokens/dt
            ASCIIColors.green(f"Received {self.nb_received_tokens} tokens (speed: {spd:.2f}t/s)              ",end="\r",flush=True) 
            sys.stdout = sys.__stdout__
            sys.stdout.flush()
            if chunk:
                self.connections[client_id]["generated_text"] += chunk
            antiprompt = self.personality.detect_antiprompt(self.connections[client_id]["generated_text"])
            if antiprompt:
                ASCIIColors.warning(f"\nDetected hallucination with antiprompt: {antiprompt}")
                self.connections[client_id]["generated_text"] = self.remove_text_from_string(self.connections[client_id]["generated_text"],antiprompt)
                self.update_message(client_id, self.connections[client_id]["generated_text"], parameters, metadata, None, MSG_TYPE.MSG_TYPE_FULL)
                return False
            else:
                self.nb_received_tokens += 1
                if self.connections[client_id]["continuing"] and self.connections[client_id]["first_chunk"]:
                    self.update_message(client_id, self.connections[client_id]["generated_text"], parameters, metadata)
                else:
                    self.update_message(client_id, chunk, parameters, metadata, msg_type=MSG_TYPE.MSG_TYPE_CHUNK)
                self.connections[client_id]["first_chunk"]=False
                # if stop generation is detected then stop
                if not self.cancel_gen:
                    return True
                else:
                    self.cancel_gen = False
                    ASCIIColors.warning("Generation canceled")
                    return False
 
        # Stream the generated text to the main process
        elif message_type == MSG_TYPE.MSG_TYPE_FULL:
            self.connections[client_id]["generated_text"] = chunk
            self.nb_received_tokens += 1
            dt =(datetime.now() - self.start_time).seconds
            if dt==0:
                dt=1
            spd = self.nb_received_tokens/dt
            ASCIIColors.green(f"Received {self.nb_received_tokens} tokens (speed: {spd:.2f}t/s)              ",end="\r",flush=True) 
            self.update_message(client_id, chunk,  parameters, metadata, ui=None, msg_type=message_type)
            return True
        # Stream the generated text to the frontend
        else:
            self.update_message(client_id, chunk, parameters, metadata, ui=None, msg_type=message_type)
        return True


    def generate(self, full_prompt, prompt, n_predict, client_id, callback=None):
        if self.personality.processor is not None:
            ASCIIColors.info("Running workflow")
            try:
                self.personality.processor.run_workflow( prompt, full_prompt, callback)
            except Exception as ex:
                trace_exception(ex)
                # Catch the exception and get the traceback as a list of strings
                traceback_lines = traceback.format_exception(type(ex), ex, ex.__traceback__)
                # Join the traceback lines into a single string
                traceback_text = ''.join(traceback_lines)
                ASCIIColors.error(f"Workflow run failed.\nError:{ex}")
                ASCIIColors.error(traceback_text)
                if callback:
                    callback(f"Workflow run failed\nError:{ex}", MSG_TYPE.MSG_TYPE_EXCEPTION)                   
            print("Finished executing the workflow")
            return


        self._generate(full_prompt, n_predict, client_id, callback)
        ASCIIColors.success("\nFinished executing the generation")

    def _generate(self, prompt, n_predict, client_id, callback=None):
        self.nb_received_tokens = 0
        self.start_time = datetime.now()
        if self.model is not None:
            if self.model.binding_type==BindingType.TEXT_IMAGE and len(self.personality.image_files)>0:
                ASCIIColors.info(f"warmup for generating up to {n_predict} tokens")
                if self.config["override_personality_model_parameters"]:
                    output = self.model.generate_with_images(
                        prompt,
                        self.personality.image_files,
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
                    output = self.model.generate_with_images(
                        prompt,
                        self.personality.image_files,
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
                ASCIIColors.info(f"warmup for generating up to {n_predict} tokens")
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
                     
    def start_message_generation(self, message, message_id, client_id, is_continue=False, generation_type=None):
        if self.personality is None:
            self.warning("Select a personality")
            return
        ASCIIColors.info(f"Text generation requested by client: {client_id}")
        # send the message to the bot
        print(f"Received message : {message.content}")
        if self.connections[client_id]["current_discussion"]:
            if not self.model:
                self.error("No model selected. Please make sure you select a model before starting generation", client_id=client_id)
                return          
            # First we need to send the new message ID to the client
            if is_continue:
                self.connections[client_id]["current_discussion"].load_message(message_id)
                self.connections[client_id]["generated_text"] = message.content
            else:
                self.new_message(client_id, self.personality.name, "")
                self.update_message(client_id, "✍ warming up ...", msg_type=MSG_TYPE.MSG_TYPE_STEP_START)
            self.socketio.sleep(0.01)

            # prepare query and reception
            self.discussion_messages, self.current_message, tokens = self.prepare_query(client_id, message_id, is_continue, n_tokens=self.config.min_n_predict, generation_type=generation_type)
            self.prepare_reception(client_id)
            self.generating = True
            self.connections[client_id]["processing"]=True
            self.generate(
                            self.discussion_messages, 
                            self.current_message, 
                            n_predict = self.config.ctx_size-len(tokens)-1,
                            client_id=client_id,
                            callback=partial(self.process_chunk,client_id = client_id)
                        )
            print()
            print("## Done Generation ##")
            print()
            self.cancel_gen = False

            # Send final message
            self.close_message(client_id)
            self.socketio.sleep(0.01)
            self.connections[client_id]["processing"]=False
            if self.connections[client_id]["schedule_for_deletion"]:
                del self.connections[client_id]

            ASCIIColors.success(f" ╔══════════════════════════════════════════════════╗ ")
            ASCIIColors.success(f" ║                        Done                      ║ ")
            ASCIIColors.success(f" ╚══════════════════════════════════════════════════╝ ")
            if self.config.auto_title:
                d = self.connections[client_id]["current_discussion"]
                ttl = d.title()
                if ttl is None or ttl=="" or ttl=="untitled":
                    title = self.make_discussion_title(d, client_id=client_id)
                    d.rename(title)
                    self.socketio.emit('disucssion_renamed',{
                                                'status': True,
                                                'discussion_id':d.discussion_id,
                                                'title':title
                                                }, room=client_id) 

            self.busy=False

        else:
            ump = self.config.discussion_prompt_separator +self.config.user_name.strip() if self.config.use_user_name_in_discussions else self.personality.user_message_prefix
            
            self.cancel_gen = False
            #No discussion available
            ASCIIColors.warning("No discussion selected!!!")

            self.error("No discussion selected!!!", client_id=client_id)
            
            print()
            self.busy=False
            return ""
