######
# Project       : GPT4ALL-UI
# Author        : ParisNeo with the help of the community
# Supported by Nomic-AI
# Licence       : Apache 2.0
# Description   : 
# A front end Flask application for llamacpp models.
# The official GPT4All Web ui
# Made by the community for the community
######

__author__ = "parisneo"
__github__ = "https://github.com/nomic-ai/gpt4all-ui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

import os
import logging
import argparse
import json
import re
import traceback
import threading
import sys
from pyaipersonality import AIPersonality
from pyGpt4All.db import DiscussionsDB, Discussion
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
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer

app = Flask("GPT4All-WebUI", static_url_path="/static", static_folder="static")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent', ping_timeout=30, ping_interval=15)

app.config['SECRET_KEY'] = 'secret!'
# Set the logging level to WARNING or higher
logging.getLogger('socketio').setLevel(logging.WARNING)
logging.getLogger('engineio').setLevel(logging.WARNING)
# Suppress Flask's default console output
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

import time
from pyGpt4All.config import load_config, save_config
from pyGpt4All.api import GPT4AllAPI
import shutil
import markdown


class Gpt4AllWebUI(GPT4AllAPI):
    def __init__(self, _app, _socketio, config:dict, personality:dict, config_file_path) -> None:
        super().__init__(config, personality, config_file_path)

        self.app = _app
        self.cancel_gen = False
        self.socketio = _socketio

        if "use_new_ui" in self.config:
            if self.config["use_new_ui"]:
                app.template_folder = "web/dist"


        # =========================================================================================
        # Endpoints
        # =========================================================================================


        self.add_endpoint(
            "/list_backends", "list_backends", self.list_backends, methods=["GET"]
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
        
        self.add_endpoint("/set_personality_language", "set_personality_language", self.set_personality_language, methods=["GET"])
        self.add_endpoint("/set_personality_category", "set_personality_category", self.set_personality_category, methods=["GET"])
        
        
        self.add_endpoint("/", "", self.index, methods=["GET"])
        self.add_endpoint("/<path:filename>", "serve_static", self.serve_static, methods=["GET"])
        self.add_endpoint("/personalities/<path:filename>", "serve_personalities", self.serve_personalities, methods=["GET"])
        
        
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
            "/set_backend", "set_backend", self.set_backend, methods=["POST"]
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
            "/save_settings", "save_settings", self.save_settings, methods=["POST"]
        )

        self.add_endpoint(
            "/get_current_personality", "get_current_personality", self.get_current_personality, methods=["GET"]
        )
        
        # =========================================================================================
        # Socket IO stuff    
        # =========================================================================================
        @socketio.on('connect')
        def connect():
            print('Client connected')

        @socketio.on('disconnect')
        def disconnect():
            print('Client disconnected')
        
        @socketio.on('generate_msg')
        def generate_msg(data):
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

        @socketio.on('generate_msg_from')
        def handle_connection(data):
            message_id = int(data['id'])
            message = data["prompt"]
            self.current_user_message_id = message_id
            tpe = threading.Thread(target=self.start_message_generation, args=(message, message_id))
            tpe.start()



    def save_settings(self):
        save_config(self.config, self.config_file_path)
        if self.config["debug"]:
            print("Configuration saved")
        # Tell that the setting was changed
        self.socketio.emit('save_settings', {"status":True})
        return jsonify({"status":True})
    

    def get_current_personality(self):
        return jsonify({"personality":self.personality.as_dict()})
    
    

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
            back_language = self.config["personality_language"]
            if self.config["personality_language"]!=data['setting_value']:
                self.config["personality_language"]=data['setting_value']
                cats = self.list_personalities_categories()
                if len(cats)>0:
                    back_category = self.config["personality_category"]
                    self.config["personality_category"]=cats[0]
                    pers = json.loads(self.list_personalities().data.decode("utf8"))
                    if len(pers)>0:
                        self.config["personality"]=pers[0]
                        personality_fn = f"personalities/{self.config['personality_language']}/{self.config['personality_category']}/{self.config['personality']}"
                        self.personality.load_personality(personality_fn)
                    else:
                        self.config["personality_language"]=back_language
                        self.config["personality_category"]=back_category
                        return jsonify({'setting_name': data['setting_name'], "status":False})
                else:
                    self.config["personality_language"]=back_language
                    return jsonify({'setting_name': data['setting_name'], "status":False})
                
        elif setting_name== "personality_category":
            back_category = self.config["personality_category"]
            if self.config["personality_category"]!=data['setting_value']:
                self.config["personality_category"]=data['setting_value']
                pers = json.loads(self.list_personalities().data.decode("utf8"))
                if len(pers)>0:
                    self.config["personality"]=pers[0]
                    personality_fn = f"personalities/{self.config['personality_language']}/{self.config['personality_category']}/{self.config['personality']}"
                    self.personality.load_personality(personality_fn)
                    if self.config["debug"]:
                        print(self.personality)
                else:
                    self.config["personality_category"]=back_category
                    return jsonify({'setting_name': data['setting_name'], "status":False})

        elif setting_name== "personality":
            self.config["personality"]=data['setting_value']
            personality_fn = f"personalities/{self.config['personality_language']}/{self.config['personality_category']}/{self.config['personality']}"
            self.personality.load_personality(personality_fn)
        elif setting_name== "override_personality_model_parameters":
            self.config["override_personality_model_parameters"]=bool(data['setting_value'])
            
            


        elif setting_name== "model":
            self.config["model"]=data['setting_value']
            print("New model selected")            
            # Build chatbot
            self.chatbot_bindings = self.create_chatbot()

        elif setting_name== "backend":
            print("New backend selected")            
            if self.config['backend']!= data['setting_value']:
                print("New backend selected")
                self.config["backend"]=data['setting_value']
                
                backend_ =self.load_backend(self.BACKENDS_LIST[self.config["backend"]])
                models = backend_.list_models(self.config)
                if len(models)>0:      
                    self.backend = backend_
                    self.config['model'] = models[0]
                    # Build chatbot
                    self.chatbot_bindings = self.create_chatbot()
                    if self.config["debug"]:
                        print(f"Configuration {data['setting_name']} set to {data['setting_value']}")
                    return jsonify({'setting_name': data['setting_name'], "status":True})
                else:
                    if self.config["debug"]:
                        print(f"Configuration {data['setting_name']} couldn't be set to {data['setting_value']}")
                    return jsonify({'setting_name': data['setting_name'], "status":False})
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
        # Tell that the setting was changed
        return jsonify({'setting_name': data['setting_name'], "status":True})

    def list_backends(self):
        backends_dir = Path('./backends')  # replace with the actual path to the models folder
        backends = [f.stem for f in backends_dir.iterdir() if f.is_dir() and f.stem!="__pycache__"]
        return jsonify(backends)


    def list_models(self):
        models = self.backend.list_models(self.config)
        return jsonify(models)
    

    def list_personalities_languages(self):
        personalities_languages_dir = Path(f'./personalities')  # replace with the actual path to the models folder
        personalities_languages = [f.stem for f in personalities_languages_dir.iterdir() if f.is_dir()]
        return jsonify(personalities_languages)

    def list_personalities_categories(self):
        personalities_categories_dir = Path(f'./personalities/{self.config["personality_language"]}')  # replace with the actual path to the models folder
        personalities_categories = [f.stem for f in personalities_categories_dir.iterdir() if f.is_dir()]
        return jsonify(personalities_categories)
    
    def list_personalities(self):
        try:
            personalities_dir = Path(f'./personalities/{self.config["personality_language"]}/{self.config["personality_category"]}')  # replace with the actual path to the models folder
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


    def set_personality_language(self):
        lang = request.args.get('language')
        self.config['personality_language'] = lang
        return jsonify({'success':True})

    def set_personality_category(self):
        category = request.args.get('category')
        self.config['personality_category'] = category
        return jsonify({'success':True})

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
        if "use_new_ui" in self.config:
            if self.config["use_new_ui"]:
                path = os.path.join(root_dir, 'web/dist/')+"/".join(filename.split("/")[:-1])
            else:
                path = os.path.join(root_dir, 'static/')+"/".join(filename.split("/")[:-1])
        else:
            path = os.path.join(root_dir, 'static/')+"/".join(filename.split("/")[:-1])
                            
        fn = filename.split("/")[-1]
        return send_from_directory(path, fn)

    def serve_personalities(self, filename):
        root_dir = os.getcwd()
        path = os.path.join(root_dir, 'personalities/')+"/".join(filename.split("/")[:-1])
                            
        fn = filename.split("/")[-1]
        return send_from_directory(path, fn)

    def export(self):
        return jsonify(self.db.export_to_json())

    def export_discussion(self):
        return jsonify({"discussion_text":self.get_discussion_to()})
    

    def start_message_generation(self, message, message_id):
        bot_says = ""

        # send the message to the bot
        print(f"Received message : {message}")
        if self.current_discussion:
            # First we need to send the new message ID to the client
            self.current_ai_message_id = self.current_discussion.add_message(
                self.personality.name, "", parent = self.current_user_message_id
            )  # first the content is empty, but we'll fill it at the end
            socketio.emit('infos',
                    {
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
            # app.config['executor'] = ThreadPoolExecutor(max_workers=1)
            # app.config['executor'].submit(self.generate_message)
            print("## Generating message ##")
            self.generate_message()

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
    
    def get_generation_status(self):
        return jsonify({"status":self.generating}) 
    
    def stop_gen(self):
        self.cancel_gen = True
        print("Stop generation received")
        return jsonify({"status": "ok"}) 
           
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
        data = request.get_json()
        if "id" in data:
            discussion_id = data["id"]
            self.current_discussion = Discussion(discussion_id, self.db)
        else:
            if self.current_discussion is not None:
                discussion_id = self.current_discussion.discussion_id
                self.current_discussion = Discussion(discussion_id, self.db)
            else:
                self.current_discussion = self.db.create_discussion()
        messages = self.current_discussion.get_messages()
        #for message in messages:
        #    message["content"] =  markdown.markdown(message["content"])
        
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
        self.current_discussion.update_message(discussion_id, new_message)
        return jsonify({"status": "ok"})

    def message_rank_up(self):
        discussion_id = request.args.get("id")
        new_rank = self.current_discussion.message_rank_up(discussion_id)
        return jsonify({"new_rank": new_rank})

    def message_rank_down(self):
        discussion_id = request.args.get("id")
        new_rank = self.current_discussion.message_rank_down(discussion_id)
        return jsonify({"new_rank": new_rank})

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
        # app.config['executor'] = ThreadPoolExecutor(max_workers=1)
        # app.config['executor'].submit(self.create_chatbot)
        # target=self.create_chatbot()
        
        # Return a success response
        return json.dumps({"id": self.current_discussion.discussion_id, "time": timestamp, "welcome_message":self.personality.welcome_message, "sender":self.personality.name})

    def set_backend(self):
        data = request.get_json()
        backend =  str(data["backend"])
        if self.config['backend']!= backend:
            print("New backend selected")
            
            self.config['backend'] = backend
            backend_ =self.load_backend(self.BACKENDS_LIST[self.config["backend"]])
            models = backend_.list_models(self.config)
            if len(models)>0:      
                self.backend = backend_
                self.config['model'] = models[0]
                # Build chatbot
                self.chatbot_bindings = self.create_chatbot()
                return jsonify({"status": "ok"})
            else:
                return jsonify({"status": "no_models_found"})

        return jsonify({"status": "error"})

    def set_model(self):
        data = request.get_json()
        model =  str(data["model"])
        if self.config['model']!= model:
            print("New model selected")            
            self.config['model'] = model
            # Build chatbot
            self.chatbot_bindings = self.create_chatbot()
            return jsonify({"status": "ok"})

        return jsonify({"status": "error"})    
    
    def update_model_params(self):
        data = request.get_json()
        backend =  str(data["backend"])
        model =  str(data["model"])
        personality_language =  str(data["personality_language"])
        personality_category =  str(data["personality_category"])
        personality =  str(data["personality"])
        
        if self.config['backend']!=backend or  self.config['model'] != model:
            print("New model selected")
            
            self.config['backend'] = backend
            self.config['model'] = model
            self.create_chatbot()

        self.config['personality_language'] = personality_language
        self.config['personality_category'] = personality_category
        self.config['personality'] = personality

        personality_fn = f"personalities/{self.config['personality_language']}/{self.config['personality_category']}/{self.config['personality']}"
        print(f"Loading personality : {personality_fn}")
        self.personality = AIPersonality(personality_fn)

        self.config['n_predict'] = int(data["nPredict"])
        self.config['seed'] = int(data["seed"])
        self.config['model'] = str(data["model"])
        self.config['voice'] = str(data["voice"])
        self.config['language'] = str(data["language"])
        
        self.config['temperature'] = float(data["temperature"])
        self.config['top_k'] = int(data["topK"])
        self.config['top_p'] = float(data["topP"])
        self.config['repeat_penalty'] = float(data["repeatPenalty"])
        self.config['repeat_last_n'] = int(data["repeatLastN"])

        save_config(self.config, self.config_file_path)

        print("==============================================")
        print("Parameters changed to:")
        print(f"\tBackend:{self.config['backend']}")
        print(f"\tModel:{self.config['model']}")
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

        return jsonify({"status":"ok"})
    
    
    def get_config(self):
        return jsonify(self.config)

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

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the chatbot Flask app.")
    parser.add_argument(
        "-c", "--config", type=str, default="default", help="Sets the configuration file to be used."
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
    default_config = load_config(f"configs/default.yaml")

    if args.config=="default":
        args.config = "local_default"
        if not Path(f"configs/local_default.yaml").exists():
            print("No local configuration file found. Building from scratch")
            shutil.copy(f"configs/default.yaml", f"configs/local_default.yaml")

    config_file_path = f"configs/{args.config}.yaml"
    config = load_config(config_file_path)

    if "version" not in config or int(config["version"])<int(default_config["version"]):
        #Upgrade old configuration files to new format
        print("Configuration file is very old. Replacing with default configuration")
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
        save_config(config, config_file_path)

    # Override values in config with command-line arguments
    for arg_name, arg_value in vars(args).items():
        if arg_value is not None:
            config[arg_name] = arg_value

    try:
        personality_path = f"personalities/{config['personality_language']}/{config['personality_category']}/{config['personality']}"
        personality = AIPersonality(personality_path)
    except Exception as ex:
        print("Personality file not found. Please verify that the personality you have selected exists or select another personality. Some updates may lead to change in personality name or category, so check the personality selection in settings to be sure.")
        if config["debug"]:
            print(ex)
        personality = AIPersonality()
    # executor = ThreadPoolExecutor(max_workers=1)
    # app.config['executor'] = executor
    bot = Gpt4AllWebUI(app, socketio, config, personality, config_file_path)

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
        
    http_server = WSGIServer((config["host"], config["port"]), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
    #if config["debug"]:
    #    app.run(debug=True, host=config["host"], port=config["port"])
    #else:
    #    app.run(host=config["host"], port=config["port"])
