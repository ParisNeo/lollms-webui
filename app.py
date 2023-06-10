######
# Project       : lollms-webui
# Author        : ParisNeo with the help of the community
# Supported by Nomic-AI
# license       : Apache 2.0
# Description   : 
# A front end Flask application for llamacpp models.
# The official GPT4All Web ui
# Made by the community for the community
######

__author__ = "parisneo"
__github__ = "https://github.com/ParisNeo/lollms-webui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

import os
import logging
import argparse
import json
import re
import traceback
import sys
from tqdm import tqdm
import subprocess
import signal
from lollms.personality import AIPersonality, MSG_TYPE
from lollms.helpers import ASCIIColors, BaseConfig
from lollms.paths import LollmsPaths
from api.db import DiscussionsDB, Discussion
from api.helpers import compare_lists
from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    stream_with_context,
    send_from_directory
)
from flask_socketio import SocketIO, emit
from pathlib import Path
import gc
import yaml
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import psutil
from lollms.binding import LOLLMSConfig

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask("GPT4All-WebUI", static_url_path="/static", static_folder="static")
socketio = SocketIO(app,  cors_allowed_origins="*", async_mode='gevent', ping_timeout=200, ping_interval=15)

app.config['SECRET_KEY'] = 'secret!'
# Set the logging level to WARNING or higher
logging.getLogger('socketio').setLevel(logging.WARNING)
logging.getLogger('engineio').setLevel(logging.WARNING)
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.basicConfig(level=logging.WARNING)

import time
from api.config import load_config, save_config
from api import LoLLMsAPPI
import shutil
import markdown


class LoLLMsWebUI(LoLLMsAPPI):
    def __init__(self, _app, _socketio, config:LOLLMSConfig, config_file_path:Path|str, lollms_paths:LollmsPaths) -> None:
        super().__init__(config, _socketio, config_file_path, lollms_paths)

        self.app = _app
        self.cancel_gen = False
        

        app.template_folder = "web/dist"

        self.personality_language= config["personalities"][config["active_personality_id"]].split("/")[0]
        self.personality_category= config["personalities"][config["active_personality_id"]].split("/")[1]
        self.personality_name= config["personalities"][config["active_personality_id"]].split("/")[2]

        # =========================================================================================
        # Endpoints
        # =========================================================================================




        self.add_endpoint("/switch_personal_path", "switch_personal_path", self.switch_personal_path, methods=["POST"])

        self.add_endpoint("/add_reference_to_local_model", "add_reference_to_local_model", self.add_reference_to_local_model, methods=["POST"])
        
        self.add_endpoint("/send_file", "send_file", self.send_file, methods=["POST"])
        
        self.add_endpoint("/list_mounted_personalities", "list_mounted_personalities", self.list_mounted_personalities, methods=["POST"])
        self.add_endpoint("/mount_personality", "mount_personality", self.mount_personality, methods=["POST"])
        self.add_endpoint("/unmount_personality", "unmount_personality", self.unmount_personality, methods=["POST"])
        self.add_endpoint("/select_personality", "select_personality", self.select_personality, methods=["POST"])


        self.add_endpoint(
            "/disk_usage", "disk_usage", self.disk_usage, methods=["GET"]
        )

        self.add_endpoint(
            "/ram_usage", "ram_usage", self.ram_usage, methods=["GET"]
        )


        self.add_endpoint(
            "/list_bindings", "list_bindings", self.list_bindings, methods=["GET"]
        )
        self.add_endpoint(
            "/list_models", "list_models", self.list_models, methods=["GET"]
        )
        self.add_endpoint(
            "/list_personalities_languages", "list_personalities_languages", self.list_personalities_languages, methods=["GET"]
        )        
        self.add_endpoint(
            "/list_personalities_categories", "list_personalities_categories", self.list_personalities_categories, methods=["GET"]
        )
        self.add_endpoint(
            "/list_personalities", "list_personalities", self.list_personalities, methods=["GET"]
        )

        self.add_endpoint(
            "/list_languages", "list_languages", self.list_languages, methods=["GET"]
        )
        
        self.add_endpoint(
            "/list_discussions", "list_discussions", self.list_discussions, methods=["GET"]
        )
        
        self.add_endpoint("/delete_personality", "delete_personality", self.delete_personality, methods=["GET"])
        
        
        self.add_endpoint("/", "", self.index, methods=["GET"])
        self.add_endpoint("/<path:filename>", "serve_static", self.serve_static, methods=["GET"])
        
        self.add_endpoint("/images/<path:filename>", "serve_images", self.serve_images, methods=["GET"])
        self.add_endpoint("/bindings/<path:filename>", "serve_bindings", self.serve_bindings, methods=["GET"])
        self.add_endpoint("/personalities/<path:filename>", "serve_personalities", self.serve_personalities, methods=["GET"])
        self.add_endpoint("/outputs/<path:filename>", "serve_outputs", self.serve_outputs, methods=["GET"])
        self.add_endpoint("/data/<path:filename>", "serve_data", self.serve_data, methods=["GET"])
        self.add_endpoint("/help/<path:filename>", "serve_help", self.serve_help, methods=["GET"])
        
        self.add_endpoint("/uploads/<path:filename>", "serve_uploads", self.serve_uploads, methods=["GET"])

        
        self.add_endpoint("/export_discussion", "export_discussion", self.export_discussion, methods=["GET"])
        self.add_endpoint("/export", "export", self.export, methods=["GET"])
        self.add_endpoint(
            "/new_discussion", "new_discussion", self.new_discussion, methods=["GET"]
        )
        self.add_endpoint("/stop_gen", "stop_gen", self.stop_gen, methods=["GET"])

        self.add_endpoint("/rename", "rename", self.rename, methods=["POST"])
        self.add_endpoint("/edit_title", "edit_title", self.edit_title, methods=["POST"])
        self.add_endpoint(
            "/load_discussion", "load_discussion", self.load_discussion, methods=["POST"]
        )
        self.add_endpoint(
            "/delete_discussion",
            "delete_discussion",
            self.delete_discussion,
            methods=["POST"],
        )

        self.add_endpoint(
            "/update_message", "update_message", self.update_message, methods=["GET"]
        )
        self.add_endpoint(
            "/message_rank_up", "message_rank_up", self.message_rank_up, methods=["GET"]
        )
        self.add_endpoint(
            "/message_rank_down", "message_rank_down", self.message_rank_down, methods=["GET"]
        )
        self.add_endpoint(
            "/delete_message", "delete_message", self.delete_message, methods=["GET"]
        )
        
        self.add_endpoint(
            "/set_binding", "set_binding", self.set_binding, methods=["POST"]
        )
        
        self.add_endpoint(
            "/set_model", "set_model", self.set_model, methods=["POST"]
        )
        
        self.add_endpoint(
            "/update_model_params", "update_model_params", self.update_model_params, methods=["POST"]
        )

        self.add_endpoint(
            "/get_config", "get_config", self.get_config, methods=["GET"]
        )

        self.add_endpoint(
            "/get_current_personality_path_infos", "get_current_personality_path_infos", self.get_current_personality_path_infos, methods=["GET"]
        )

        self.add_endpoint(
            "/get_available_models", "get_available_models", self.get_available_models, methods=["GET"]
        )


        self.add_endpoint(
            "/extensions", "extensions", self.extensions, methods=["GET"]
        )

        self.add_endpoint(
            "/training", "training", self.training, methods=["GET"]
        )
        self.add_endpoint(
            "/main", "main", self.main, methods=["GET"]
        )
        
        self.add_endpoint(
            "/settings", "settings", self.settings, methods=["GET"]
        )

        self.add_endpoint(
            "/help", "help", self.help, methods=["GET"]
        )
        
        self.add_endpoint(
            "/get_generation_status", "get_generation_status", self.get_generation_status, methods=["GET"]
        )
        
        self.add_endpoint(
            "/update_setting", "update_setting", self.update_setting, methods=["POST"]
        )
        self.add_endpoint(
            "/apply_settings", "apply_settings", self.apply_settings, methods=["POST"]
        )
        

        self.add_endpoint(
            "/save_settings", "save_settings", self.save_settings, methods=["POST"]
        )

        self.add_endpoint(
            "/get_current_personality", "get_current_personality", self.get_current_personality, methods=["GET"]
        )
        

        self.add_endpoint(
            "/get_all_personalities", "get_all_personalities", self.get_all_personalities, methods=["GET"]
        )

        self.add_endpoint(
            "/get_personality", "get_personality", self.get_personality, methods=["GET"]
        )
        
        
        self.add_endpoint(
            "/reset", "reset", self.reset, methods=["GET"]
        )
        
        self.add_endpoint(
            "/export_multiple_discussions", "export_multiple_discussions", self.export_multiple_discussions, methods=["POST"]
        )      
        self.add_endpoint(
            "/import_multiple_discussions", "import_multiple_discussions", self.import_multiple_discussions, methods=["POST"]
        )      

        
        
    def export_multiple_discussions(self):
        data = request.get_json()
        discussion_ids = data["discussion_ids"]
        discussions = self.db.export_discussions_to_json(discussion_ids)
        return jsonify(discussions)
          
    def import_multiple_discussions(self):
        discussions = request.get_json()["jArray"]
        self.db.import_from_json(discussions)
        return jsonify(discussions)
        
    def reset(self):
        os.kill(os.getpid(), signal.SIGINT)  # Send the interrupt signal to the current process
        subprocess.Popen(['python', 'app.py'])  # Restart the app using subprocess

        return 'App is resetting...'

    def save_settings(self):
        self.config.save_config(self.config_file_path)
        if self.config["debug"]:
            print("Configuration saved")
        # Tell that the setting was changed
        self.socketio.emit('save_settings', {"status":True})
        return jsonify({"status":True})
    

    def get_current_personality(self):
        return jsonify({"personality":self.personality.as_dict()})
    
    def get_all_personalities(self):
        personalities_folder = self.lollms_paths.personalities_zoo_path
        personalities = {}
        for language_folder in personalities_folder.iterdir():
            lang = language_folder.stem
            if language_folder.is_dir():
                personalities[language_folder.name] = {}
                for category_folder in  language_folder.iterdir():
                    cat = category_folder.stem
                    if category_folder.is_dir():
                        personalities[language_folder.name][category_folder.name] = []
                        for personality_folder in category_folder.iterdir():
                            pers = personality_folder.stem
                            if personality_folder.is_dir():
                                try:
                                    personality_info = {"folder":personality_folder.stem}
                                    config_path = personality_folder / 'config.yaml'
                                    with open(config_path) as config_file:
                                        config_data = yaml.load(config_file, Loader=yaml.FullLoader)
                                        personality_info['name'] = config_data.get('name',"No Name")
                                        personality_info['description'] = config_data.get('personality_description',"")
                                        personality_info['author'] = config_data.get('author', 'ParisNeo')
                                        personality_info['version'] = config_data.get('version', '1.0.0')
                                    scripts_path = personality_folder / 'scripts'
                                    personality_info['has_scripts'] = scripts_path.is_dir()
                                    real_assets_path = personality_folder/ 'assets'
                                    assets_path = Path("personalities") / lang / cat / pers / 'assets'
                                    gif_logo_path = assets_path / 'logo.gif'
                                    webp_logo_path = assets_path / 'logo.webp'
                                    png_logo_path = assets_path / 'logo.png'
                                    jpg_logo_path = assets_path / 'logo.jpg'
                                    jpeg_logo_path = assets_path / 'logo.jpeg'
                                    bmp_logo_path = assets_path / 'logo.bmp'

                                    gif_logo_path_ = real_assets_path / 'logo.gif'
                                    webp_logo_path_ = real_assets_path / 'logo.webp'
                                    png_logo_path_ = real_assets_path / 'logo.png'
                                    jpg_logo_path_ = real_assets_path / 'logo.jpg'
                                    jpeg_logo_path_ = real_assets_path / 'logo.jpeg'
                                    bmp_logo_path_ = real_assets_path / 'logo.bmp'

                                    personality_info['has_logo'] = png_logo_path.is_file() or gif_logo_path.is_file()
                                    
                                    if gif_logo_path_.exists():
                                        personality_info['avatar'] = str(gif_logo_path).replace("\\","/")
                                    elif webp_logo_path_.exists():
                                        personality_info['avatar'] = str(webp_logo_path).replace("\\","/")
                                    elif png_logo_path_.exists():
                                        personality_info['avatar'] = str(png_logo_path).replace("\\","/")
                                    elif jpg_logo_path_.exists():
                                        personality_info['avatar'] = str(jpg_logo_path).replace("\\","/")
                                    elif jpeg_logo_path_.exists():
                                        personality_info['avatar'] = str(jpeg_logo_path).replace("\\","/")
                                    elif bmp_logo_path_.exists():
                                        personality_info['avatar'] = str(bmp_logo_path).replace("\\","/")
                                    else:
                                        personality_info['avatar'] = ""
                                    personalities[language_folder.name][category_folder.name].append(personality_info)
                                except Exception as ex:
                                    print(f"Couldn't load personality from {personality_folder} [{ex}]")
        return json.dumps(personalities)
    
    def get_personality():
        lang = request.args.get('language')
        category = request.args.get('category')
        name = request.args.get('name')
        personality_folder = Path("personalities")/f"{lang}"/f"{category}"/f"{name}"
        personality_path = personality_folder/f"config.yaml"
        personality_info = {}
        with open(personality_path) as config_file:
            config_data = yaml.load(config_file, Loader=yaml.FullLoader)
            personality_info['name'] = config_data.get('name',"unnamed")
            personality_info['description'] = config_data.get('personality_description',"")
            personality_info['author'] = config_data.get('creator', 'ParisNeo')
            personality_info['version'] = config_data.get('version', '1.0.0')
        scripts_path = personality_folder / 'scripts'
        personality_info['has_scripts'] = scripts_path.is_dir()
        assets_path = personality_folder / 'assets'
        gif_logo_path = assets_path / 'logo.gif'
        webp_logo_path = assets_path / 'logo.webp'
        png_logo_path = assets_path / 'logo.png'
        jpg_logo_path = assets_path / 'logo.jpg'
        jpeg_logo_path = assets_path / 'logo.jpeg'
        bmp_logo_path = assets_path / 'logo.bmp'
        
        personality_info['has_logo'] = png_logo_path.is_file() or gif_logo_path.is_file()
        
        if gif_logo_path.exists():
            personality_info['avatar'] = str(gif_logo_path).replace("\\","/")
        elif webp_logo_path.exists():
            personality_info['avatar'] = str(webp_logo_path).replace("\\","/")
        elif png_logo_path.exists():
            personality_info['avatar'] = str(png_logo_path).replace("\\","/")
        elif jpg_logo_path.exists():
            personality_info['avatar'] = str(jpg_logo_path).replace("\\","/")
        elif jpeg_logo_path.exists():
            personality_info['avatar'] = str(jpeg_logo_path).replace("\\","/")
        elif bmp_logo_path.exists():
            personality_info['avatar'] = str(bmp_logo_path).replace("\\","/")
        else:
            personality_info['avatar'] = ""
        return json.dumps(personality_info)
        
    # Settings (data: {"setting_name":<the setting name>,"setting_value":<the setting value>})
    def update_setting(self):
        data = request.get_json()
        setting_name = data['setting_name']
        if setting_name== "temperature":
            self.config["temperature"]=float(data['setting_value'])
        elif setting_name== "n_predict":
            self.config["n_predict"]=int(data['setting_value'])
        elif setting_name== "top_k":
            self.config["top_k"]=int(data['setting_value'])
        elif setting_name== "top_p":
            self.config["top_p"]=float(data['setting_value'])
            
        elif setting_name== "repeat_penalty":
            self.config["repeat_penalty"]=float(data['setting_value'])
        elif setting_name== "repeat_last_n":
            self.config["repeat_last_n"]=int(data['setting_value'])

        elif setting_name== "n_threads":
            self.config["n_threads"]=int(data['setting_value'])
        elif setting_name== "ctx_size":
            self.config["ctx_size"]=int(data['setting_value'])


        elif setting_name== "language":
            self.config["language"]=data['setting_value']

        elif setting_name== "personality_language":
            self.personality_language=data['setting_value']
                
        elif setting_name== "personality_category":
            self.personality_category=data['setting_value']

        elif setting_name== "personality_folder":
            self.personality_name=data['setting_value']
            if len(self.config["personalities"])>0:
                if self.config["active_personality_id"]<len(self.config["personalities"]):
                    self.config["personalities"][self.config["active_personality_id"]] = f"{self.personality_language}/{self.personality_category}/{self.personality_name}"
                else:
                    self.config["active_personality_id"] = 0
                    self.config["personalities"][self.config["active_personality_id"]] = f"{self.personality_language}/{self.personality_category}/{self.personality_name}"
                personality_fn = self.lollms_paths.personalities_zoo_path/self.config["personalities"][self.config["active_personality_id"]]
                self.personality.load_personality(personality_fn)
            else:
                self.config["personalities"].append(f"{self.personality_language}/{self.personality_category}/{self.personality_name}")
        elif setting_name== "override_personality_model_parameters":
            self.config["override_personality_model_parameters"]=bool(data['setting_value'])
            
            


        elif setting_name== "model_name":
            self.config["model_name"]=data['setting_value']
            print("update_settings : New model selected")            

        elif setting_name== "binding_name":
            if self.config['binding_name']!= data['setting_value']:
                print(f"New binding selected : {data['setting_value']}")
                self.config["binding_name"]=data['setting_value']
                try:
                    self.binding = self.process.load_binding(self.config["binding_name"], install=True)

                except Exception as ex:
                    print(f"Couldn't build binding: [{ex}]")
                    return jsonify({'setting_name': data['setting_name'], "status":False, 'error':str(ex)})
            else:
                if self.config["debug"]:
                    print(f"Configuration {data['setting_name']} set to {data['setting_value']}")
                return jsonify({'setting_name': data['setting_name'], "status":True})

        else:
            if self.config["debug"]:
                print(f"Configuration {data['setting_name']} couldn't be set to {data['setting_value']}")
            return jsonify({'setting_name': data['setting_name'], "status":False})

        if self.config["debug"]:
            print(f"Configuration {data['setting_name']} set to {data['setting_value']}")
            
        print(f"Configuration {data['setting_name']} updated")
        # Tell that the setting was changed
        return jsonify({'setting_name': data['setting_name'], "status":True})


    def apply_settings(self):
        result = self.process.set_config(self.config)
        print("Set config results:")
        print(result)
        return jsonify(result)
    
    def ram_usage(self):
        """
        Returns the RAM usage in bytes.
        """
        ram = psutil.virtual_memory()
        return jsonify({
            "total_space":ram.total,
            "available_space":ram.free,

            "percent_usage":ram.percent,
            "ram_usage": ram.used
            })

    def disk_usage(self):
        current_drive = Path.cwd().anchor
        drive_disk_usage = psutil.disk_usage(current_drive)
        try:
            models_folder_disk_usage = psutil.disk_usage(self.lollms_paths.personal_models_path/f'{self.config["binding_name"]}')
            return jsonify({
                "total_space":drive_disk_usage.total,
                "available_space":drive_disk_usage.free,

                "percent_usage":drive_disk_usage.percent,
                "binding_models_usage": models_folder_disk_usage.used
                })
        except:
            return jsonify({
                "total_space":drive_disk_usage.total,
                "available_space":drive_disk_usage.free,
                
                "percent_usage":drive_disk_usage.percent,
                "models_folder_usage": None
                })

    def list_bindings(self):
        bindings_dir = self.lollms_paths.bindings_zoo_path  # replace with the actual path to the models folder
        bindings=[]
        for f in bindings_dir.iterdir():
            card = f/"binding_card.yaml"
            if card.exists():
                try:
                    bnd = load_config(card)
                    bnd["folder"]=f.stem
                    icon_path = Path(f"bindings/{f.name}/logo.png")
                    if Path(self.lollms_paths.bindings_zoo_path/f"{f.name}/logo.png").exists():
                        bnd["icon"]=str(icon_path)

                    bindings.append(bnd)
                except Exception as ex:
                    print(f"Couldn't load backend card : {f}\n\t{ex}")
        return jsonify(bindings)


    def list_models(self):
        if self.binding is not None:
            models = self.binding.list_models(self.config)
            return jsonify(models)
        else:
            return jsonify([])
    

    def list_personalities_languages(self):
        personalities_languages_dir = self.lollms_paths.personalities_zoo_path  # replace with the actual path to the models folder
        personalities_languages = [f.stem for f in personalities_languages_dir.iterdir() if f.is_dir()]
        return jsonify(personalities_languages)

    def list_personalities_categories(self):
        personalities_categories_dir = self.lollms_paths.personalities_zoo_path/f'{self.personality_language}'  # replace with the actual path to the models folder
        personalities_categories = [f.stem for f in personalities_categories_dir.iterdir() if f.is_dir()]
        return jsonify(personalities_categories)
    
    def list_personalities(self):
        try:
            personalities_dir = self.lollms_paths.personalities_zoo_path/f'{self.personality_language}/{self.personality_category}'  # replace with the actual path to the models folder
            personalities = [f.stem for f in personalities_dir.iterdir() if f.is_dir()]
        except Exception as ex:
            personalities=[]
            if self.config["debug"]:
                print(f"No personalities found. Using default one {ex}")
        return jsonify(personalities)

    def list_languages(self):
        lanuguages= [
        { "value": "en-US", "label": "English" },
        { "value": "fr-FR", "label": "Français" },
        { "value": "ar-AR", "label": "العربية" },
        { "value": "it-IT", "label": "Italiano" },
        { "value": "de-DE", "label": "Deutsch" },
        { "value": "nl-XX", "label": "Dutch" },
        { "value": "zh-CN", "label": "中國人" }
        ]
        return jsonify(lanuguages)


    def list_discussions(self):
        discussions = self.db.get_discussions()
        return jsonify(discussions)


    def delete_personality(self):
        lang = request.args.get('language')
        category = request.args.get('category')
        name = request.args.get('name')
        path = Path("personalities")/lang/category/name
        try:
            shutil.rmtree(path)
            return jsonify({'status':'success'})
        except Exception as ex:
            return jsonify({'status':'failure','error':str(ex)})

    def add_endpoint(
        self,
        endpoint=None,
        endpoint_name=None,
        handler=None,
        methods=["GET"],
        *args,
        **kwargs,
    ):
        self.app.add_url_rule(
            endpoint, endpoint_name, handler, methods=methods, *args, **kwargs
        )

    def index(self):
        return render_template("index.html")
    
    def serve_static(self, filename):
        root_dir = os.getcwd()
        path = os.path.join(root_dir, 'web/dist/')+"/".join(filename.split("/")[:-1])                            
        fn = filename.split("/")[-1]
        return send_from_directory(path, fn)

    
    def serve_images(self, filename):
        root_dir = os.getcwd()
        path = os.path.join(root_dir, 'images/')+"/".join(filename.split("/")[:-1])
                            
        fn = filename.split("/")[-1]
        return send_from_directory(path, fn)
    
    def serve_bindings(self, filename):
        path = str(self.lollms_paths.bindings_zoo_path/("/".join(filename.split("/")[:-1])))
                            
        fn = filename.split("/")[-1]
        return send_from_directory(path, fn)

    def serve_personalities(self, filename):
        path = str(self.lollms_paths.personalities_zoo_path/("/".join(filename.split("/")[:-1])))
                            
        fn = filename.split("/")[-1]
        return send_from_directory(path, fn)

    def serve_outputs(self, filename):
        root_dir = self.lollms_paths.personal_path / "outputs"
        root_dir.mkdir(exist_ok=True, parents=True)
        path = str(root_dir/"/".join(filename.split("/")[:-1]))
                            
        fn = filename.split("/")[-1]
        return send_from_directory(path, fn)

    def serve_help(self, filename):
        root_dir = Path(__file__).parent/f"help"
        root_dir.mkdir(exist_ok=True, parents=True)
        path = str(root_dir/"/".join(filename.split("/")[:-1]))
                            
        fn = filename.split("/")[-1]
        return send_from_directory(path, fn)

    def serve_data(self, filename):
        root_dir = self.lollms_paths.personal_path / "data"
        root_dir.mkdir(exist_ok=True, parents=True)
        path = str(root_dir/"/".join(filename.split("/")[:-1]))
                            
        fn = filename.split("/")[-1]
        return send_from_directory(path, fn)

    def serve_uploads(self, filename):
        root_dir = self.lollms_paths.personal_path / "uploads"
        root_dir.mkdir(exist_ok=True, parents=True)

        path = str(root_dir+"/".join(filename.split("/")[:-1]))
                            
        fn = filename.split("/")[-1]
        return send_from_directory(path, fn)



    def export(self):
        return jsonify(self.db.export_to_json())

    def export_discussion(self):
        return jsonify({"discussion_text":self.get_discussion_to()})
    

            
    def get_generation_status(self):
        return jsonify({"status":self.process.start_signal.is_set()}) 
    
    def stop_gen(self):
        self.cancel_gen = True
        self.process.cancel_generation()
        return jsonify({"status": True})    
    

    def switch_personal_path(self):
        data = request.get_json()
        path = data["path"]
        global_paths_cfg = Path("./global_paths_cfg.yaml")
        if global_paths_cfg.exists():
            try:
                cfg = BaseConfig()
                cfg.load_config(global_paths_cfg)
                cfg.lollms_personal_path = path
                cfg.save_config(global_paths_cfg)
                return jsonify({"status": True})         
            except Exception as ex:
                print(ex)
                return jsonify({"status": False, 'error':f"Couldn't switch path: {ex}"})         
    
    def add_reference_to_local_model(self):     
        data = request.get_json()
        path = data["path"]
        if path.exists():
            self.conversation.config.reference_model(path)
            return jsonify({"status": True})         
        else:        
            return jsonify({"status": True})         

    def list_mounted_personalities(self):
        print("- Listing mounted personalities")
        return jsonify({"status": True,
                        "personalities":self.config["personalities"],
                        "active_personality_id":self.config["active_personality_id"]
                        })         


    def mount_personality(self):
        print("- Mounting personality")
        try:
            data = request.get_json()
            # Further processing of the data
        except Exception as e:
            print(f"Error occurred while parsing JSON: {e}")
            return
        language = data['language']
        category = data['category']
        name = data['name']

        package_path = f"{language}/{category}/{name}"
        package_full_path = self.lollms_paths.personalities_zoo_path/package_path
        config_file = package_full_path / "config.yaml"
        if config_file.exists():
            self.config["personalities"].append(package_path)
            self.mounted_personalities = self.process.rebuild_personalities()
            self.personality = self.mounted_personalities[self.config["active_personality_id"]]
            self.apply_settings()
            return jsonify({"status": True,
                            "personalities":self.config["personalities"],
                            "active_personality_id":self.config["active_personality_id"]
                            })         
        else:
            pth = str(config_file).replace('\\','/')
            return jsonify({"status": False, "error":f"Personality not found @ {pth}"})         

    def unmount_personality(self):
        print("- Unmounting personality")
        try:
            data = request.get_json()
            # Further processing of the data
        except Exception as e:
            print(f"Error occurred while parsing JSON: {e}")
            return
        language    = data['language']
        category    = data['category']
        name        = data['name']
        try:
            index = self.config["personalities"].index(f"{language}/{category}/{name}")
            self.config["personalities"].remove(f"{language}/{category}/{name}")
            if self.config["active_personality_id"]>=index:
                self.config["active_personality_id"]=0
            if len(self.config["personalities"])>0:
                self.personalities = self.process.rebuild_personalities()
                self.personality = self.mounted_personalities[self.config["active_personality_id"]]
            else:
                self.personalities = []
                self.personality = None
            self.apply_settings()
            return jsonify({
                        "status": True,
                        "personalities":self.config["personalities"],
                        "active_personality_id":self.config["active_personality_id"]
                        })         
        except:
            return jsonify({"status": False, "error":"Couldn't unmount personality"})         
            
    def select_personality(self):
        data = request.get_json()
        id = data['id']
        if id<len(self.config["personalities"]):
            self.config["active_personality_id"]=id
            self.personality = self.mounted_personalities[self.config["active_personality_id"]]
            self.apply_settings()
            return jsonify({
                "status": True,
                "personalities":self.config["personalities"],
                "active_personality_id":self.config["active_personality_id"]                
                })
        else:
            return jsonify({"status": False, "error":"Invalid ID"})         
                    

    def send_file(self):
        file = request.files['file']
        Path("uploads").mkdir(exist_ok=True, parents=True)
        file.save('uploads/' + file.filename)
        return jsonify({"status": True})         

    def rename(self):
        data = request.get_json()
        title = data["title"]
        self.current_discussion.rename(title)
        return "renamed successfully"
    
    def edit_title(self):
        data = request.get_json()
        title = data["title"]
        discussion_id = data["id"]
        self.current_discussion = Discussion(discussion_id, self.db)
        self.current_discussion.rename(title)
        return "title renamed successfully"
    
    def load_discussion(self):
        print("- Loading discussion")
        data = request.get_json()
        print("    Recovered json data")
        if "id" in data:
            discussion_id = data["id"]
            self.current_discussion = Discussion(discussion_id, self.db)
        else:
            if self.current_discussion is not None:
                discussion_id = self.current_discussion.discussion_id
                self.current_discussion = Discussion(discussion_id, self.db)
            else:
                self.current_discussion = self.db.create_discussion()
        print(f"    Discussion id :{discussion_id}")
        messages = self.current_discussion.get_messages()

        
        return jsonify(messages), {'Content-Type': 'application/json; charset=utf-8'}

    def delete_discussion(self):
        data = request.get_json()
        discussion_id = data["id"]
        self.current_discussion = Discussion(discussion_id, self.db)
        self.current_discussion.delete_discussion()
        self.current_discussion = None
        return jsonify({})

    def update_message(self):
        discussion_id = request.args.get("id")
        new_message = request.args.get("message")
        try:
            self.current_discussion.update_message(discussion_id, new_message)
            return jsonify({"status": True})
        except Exception as ex:
            return jsonify({"status": False, "error":str(ex)})


    def message_rank_up(self):
        discussion_id = request.args.get("id")
        try:
            new_rank = self.current_discussion.message_rank_up(discussion_id)
            return jsonify({"status": True, "new_rank": new_rank})
        except Exception as ex:
            return jsonify({"status": False, "error":str(ex)})

    def message_rank_down(self):
        discussion_id = request.args.get("id")
        try:
            new_rank = self.current_discussion.message_rank_down(discussion_id)
            return jsonify({"status": True, "new_rank": new_rank})
        except Exception as ex:
            return jsonify({"status": False, "error":str(ex)})

    def delete_message(self):
        discussion_id = request.args.get("id")
        if self.current_discussion is None:
            return jsonify({"status": False,"message":"No discussion is selected"})
        else:
            new_rank = self.current_discussion.delete_message(discussion_id)
            return jsonify({"status":True,"new_rank": new_rank})


    def new_discussion(self):
        title = request.args.get("title")
        timestamp = self.create_new_discussion(title)
        
        # Return a success response
        return json.dumps({"id": self.current_discussion.discussion_id, "time": timestamp, "welcome_message":self.personality.welcome_message, "sender":self.personality.name})

    def set_binding(self):
        data = request.get_json()
        binding =  str(data["binding"])
        if self.config['binding_name']!= binding:
            print("New binding selected")
            
            self.config['binding_name'] = binding
            try:
                binding_ =self.process.load_binding(config["binding_name"],True)
                models = binding_.list_models(self.config)
                if len(models)>0:      
                    self.binding = binding_
                    self.config['model_name'] = models[0]
                    # Build chatbot
                    return jsonify(self.process.set_config(self.config))
                else:
                    return jsonify({"status": "no_models_found"})
            except :
                return jsonify({"status": "failed"})
                
        return jsonify({"status": "error"})

    def set_model(self):
        data = request.get_json()
        model =  str(data["model_name"])
        if self.config['model_name']!= model:
            print("set_model: New model selected")            
            self.config['model_name'] = model
            # Build chatbot            
            return jsonify(self.process.set_config(self.config))

        return jsonify({"status": "succeeded"})    
    
    def update_model_params(self):
        data = request.get_json()
        binding =  str(data["binding"])
        model =  str(data["model_name"])
        personality_language =  str(data["personality_language"])
        personality_category =  str(data["personality_category"])
        personality =  str(data["personality"])
        
        if self.config['binding_name']!=binding or  self.config['model_name'] != model:
            print("update_model_params: New model selected")
            
            self.config['binding_name'] = binding
            self.config['model_name'] = model

        self.config['personality_language'] = personality_language
        self.config['personality_category'] = personality_category
        self.config['personality'] = personality

        personality_fn = lollms_path/f"personalities_zoo/{self.personality_language}/{self.personality_category}/{self.personality_name}"
        print(f"Loading personality : {personality_fn}")

        self.config['n_predict'] = int(data["nPredict"])
        self.config['seed'] = int(data["seed"])
        self.config['model_name'] = str(data["model_name"])
        self.config['voice'] = str(data["voice"])
        self.config['language'] = str(data["language"])
        
        self.config['temperature'] = float(data["temperature"])
        self.config['top_k'] = int(data["topK"])
        self.config['top_p'] = float(data["topP"])
        self.config['repeat_penalty'] = float(data["repeatPenalty"])
        self.config['repeat_last_n'] = int(data["repeatLastN"])

        self.config.save_config(self.config_file_path)

        
        # Fixed missing argument
        self.binding = self.process.rebuild_binding(self.config)

        print("==============================================")
        print("Parameters changed to:")
        print(f"\tBinding:{self.config['binding_name']}")
        print(f"\tModel:{self.config['model_name']}")
        print(f"\tPersonality language:{self.config['personality_language']}")
        print(f"\tPersonality category:{self.config['personality_category']}")
        print(f"\tPersonality:{self.config['personality']}")
        print(f"\tLanguage:{self.config['language']}")
        print(f"\tVoice:{self.config['voice']}")
        print(f"\tTemperature:{self.config['temperature']}")
        print(f"\tNPredict:{self.config['n_predict']}")
        print(f"\tSeed:{self.config['seed']}")
        print(f"\top_k:{self.config['top_k']}")
        print(f"\top_p:{self.config['top_p']}")
        print(f"\trepeat_penalty:{self.config['repeat_penalty']}")
        print(f"\trepeat_last_n:{self.config['repeat_last_n']}")
        print("==============================================")

        return jsonify(self.process.set_config(self.config))
    
    
    def get_available_models(self):
        """Get the available models

        Returns:
            _type_: _description_
        """
        if self.binding is None:
            return jsonify([])
        model_list = self.binding.get_available_models()

        models = []
        for model in model_list:
            try:
                filename = model.get('filename',"")
                server = model.get('server',"")
                image_url = model.get("icon", '/images/default_model.png')
                license = model.get("license", 'unknown')
                owner = model.get("owner", 'unknown')
                owner_link = model.get("owner_link", 'https://github.com/ParisNeo')
                filesize = int(model.get('filesize',0))
                description = model.get('description',"")
                model_type = model.get("model_type","")
                if server.endswith("/"):
                    path = f'{server}{filename}'
                else:
                    path = f'{server}/{filename}'
                local_path = lollms_paths.personal_models_path/f'{self.config["binding_name"]}/{filename}'
                is_installed = local_path.exists() or model_type.lower()=="api"
                models.append({
                    'title': filename,
                    'icon': image_url,  # Replace with the path to the model icon
                    'license': license,
                    'owner': owner,
                    'owner_link': owner_link,
                    'description': description,
                    'isInstalled': is_installed,
                    'path': path,
                    'filesize': filesize,
                    'model_type': model_type
                })
            except Exception as ex:
                print("#################################")
                print(ex)
                print("#################################")
                print(f"Problem with model : {model}")
        return jsonify(models)


    def train(self):
        form_data = request.form

        # Create and populate the config file
        config = {
            'model_name': form_data['model_name'],
            'tokenizer_name': form_data['tokenizer_name'],
            'dataset_path': form_data['dataset_path'],
            'max_length': form_data['max_length'],
            'batch_size': form_data['batch_size'],
            'lr': form_data['lr'],
            'num_epochs': form_data['num_epochs'],
            'output_dir': form_data['output_dir'],
        }

        with open('train/configs/train/local_cfg.yaml', 'w') as f:
            yaml.dump(config, f)

        # Trigger the train.py script
        # Place your code here to run the train.py script with the created config file
        # accelerate launch --dynamo_backend=inductor --num_processes=8 --num_machines=1 --machine_rank=0 --deepspeed_multinode_launcher standard --mixed_precision=bf16  --use_deepspeed --deepspeed_config_file=configs/deepspeed/ds_config_gptj.json train.py --config configs/train/finetune_gptj.yaml

        subprocess.check_call(["accelerate","launch", "--dynamo_backend=inductor", "--num_processes=8", "--num_machines=1", "--machine_rank=0", "--deepspeed_multinode_launcher standard", "--mixed_precision=bf16", "--use_deepspeed", "--deepspeed_config_file=train/configs/deepspeed/ds_config_gptj.json", "train/train.py", "--config", "train/configs/train/local_cfg.yaml"])

        return jsonify({'message': 'Training started'})
    
    def get_config(self):
        return jsonify(self.config.to_dict())
    
    def get_current_personality_path_infos(self):
        return jsonify({
            "personality_language":self.personality_language,
            "personality_category":self.personality_category, 
            "personality_name":self.personality_name
        })

    def main(self):
        return render_template("main.html")
    
    def settings(self):
        return render_template("settings.html")

    def help(self):
        return render_template("help.html")
    
    def training(self):
        return render_template("training.html")

    def extensions(self):
        return render_template("extensions.html")

def sync_cfg(default_config, config):
    """Syncs a configuration with the default configuration

    Args:
        default_config (_type_): _description_
        config (_type_): _description_

    Returns:
        _type_: _description_
    """
    added_entries = []
    removed_entries = []

    # Ensure all fields from default_config exist in config
    for key, value in default_config.items():
        if key not in config:
            config[key] = value
            added_entries.append(key)

    # Remove fields from config that don't exist in default_config
    for key in list(config.config.keys()):
        if key not in default_config:
            del config.config[key]
            removed_entries.append(key)

    config["version"]=default_config["version"]
    
    return config, added_entries, removed_entries

if __name__ == "__main__":

    lollms_paths = LollmsPaths.find_paths(force_local=True)
    db_folder = lollms_paths.personal_path/"databases"
    db_folder.mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser(description="Start the chatbot Flask app.")
    parser.add_argument(
        "-c", "--config", type=str, default="local_config", help="Sets the configuration file to be used."
    )

    parser.add_argument(
        "-p", "--personality", type=str, default=None, help="Selects the personality to be using."
    )

    parser.add_argument(
        "-s", "--seed", type=int, default=None, help="Force using a specific seed value."
    )

    parser.add_argument(
        "-m", "--model", type=str, default=None, help="Force using a specific model."
    )
    parser.add_argument(
        "--temp", type=float, default=None, help="Temperature parameter for the model."
    )
    parser.add_argument(
        "--n_predict",
        type=int,
        default=None,
        help="Number of tokens to predict at each step.",
    )
    parser.add_argument(
        "--n_threads",
        type=int,
        default=None,
        help="Number of threads to use.",
    )
    parser.add_argument(
        "--top_k", type=int, default=None, help="Value for the top-k sampling."
    )
    parser.add_argument(
        "--top_p", type=float, default=None, help="Value for the top-p sampling."
    )
    parser.add_argument(
        "--repeat_penalty", type=float, default=None, help="Penalty for repeated tokens."
    )
    parser.add_argument(
        "--repeat_last_n",
        type=int,
        default=None,
        help="Number of previous tokens to consider for the repeat penalty.",
    )
    parser.add_argument(
        "--ctx_size",
        type=int,
        default=None,#2048,
        help="Size of the context window for the model.",
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=None,
        help="launch Flask server in debug mode",
    )
    parser.add_argument(
        "--host", type=str, default=None, help="the hostname to listen on"
    )
    parser.add_argument("--port", type=int, default=None, help="the port to listen on")
    parser.add_argument(
        "--db_path", type=str, default=None, help="Database path"
    )
    args = parser.parse_args()

    # The default configuration must be kept unchanged as it is committed to the repository, 
    # so we have to make a copy that is not comitted
    default_config = load_config("configs/config.yaml")

    if args.config!="local_config":
        args.config = "local_config"
        if not lollms_paths.personal_configuration_path/f"local_config.yaml".exists():
            print("No local configuration file found. Building from scratch")
            shutil.copy(default_config, lollms_paths.personal_configuration_path/f"local_config.yaml")

    config_file_path = lollms_paths.personal_configuration_path/f"local_config.yaml"
    config = LOLLMSConfig(config_file_path)

    
    if "version" not in config or int(config["version"])<int(default_config["version"]):
        #Upgrade old configuration files to new format
        ASCIIColors.print(ASCIIColors.color_red,"Configuration file is very old.\nReplacing with default configuration")
        config, added, removed = sync_cfg(default_config, config)
        print(f"Added entries : {added}, removed entries:{removed}")
        config.save_config(config_file_path)

    # Override values in config with command-line arguments
    for arg_name, arg_value in vars(args).items():
        if arg_value is not None:
            config[arg_name] = arg_value

    # executor = ThreadPoolExecutor(max_workers=1)
    # app.config['executor'] = executor
    bot = LoLLMsWebUI(app, socketio, config, config_file_path, lollms_paths)

    # chong Define custom WebSocketHandler with error handling 
    class CustomWebSocketHandler(WebSocketHandler):
        def handle_error(self, environ, start_response, e):
            # Handle the error here
            print("WebSocket error:", e)
            super().handle_error(environ, start_response, e)
    
    url = f'http://{config["host"]}:{config["port"]}'
    
    print(f"Please open your browser and go to {url} to view the ui")

    # chong -add socket server    
    app.config['debug'] = config["debug"]

    if config["debug"]:
        print("debug mode:true")    
    else:
        print("debug mode:false")
    
    socketio.run(app, host=config["host"], port=config["port"])
    # http_server = WSGIServer((config["host"], config["port"]), app, handler_class=WebSocketHandler)
    # http_server.serve_forever()
