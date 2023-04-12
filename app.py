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

import argparse
import json
import re
import traceback
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import sys
from db import DiscussionsDB, Discussion
from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    stream_with_context,
    send_from_directory
)
from pyllamacpp.model import Model
from queue import Queue
from pathlib import Path
import gc
app = Flask("GPT4All-WebUI", static_url_path="/static", static_folder="static")
import time
from config import load_config

class Gpt4AllWebUI:

    def __init__(self, _app, config:dict) -> None:
        self.config = config
        self.current_discussion = None
        self.app = _app
        self.db_path = config["db_path"]
        self.db = DiscussionsDB(self.db_path)
        # If the database is empty, populate it with tables
        self.db.populate()

        # workaround for non interactive mode
        self.full_message = ""
        self.full_message_list = []
        self.prompt_message = ""
        # This is the queue used to stream text to the ui as the bot spits out its response
        self.text_queue = Queue(0)

        self.add_endpoint(
            "/list_models", "list_models", self.list_models, methods=["GET"]
        )
        self.add_endpoint(
            "/list_discussions", "list_discussions", self.list_discussions, methods=["GET"]
        )
        
        
        self.add_endpoint("/", "", self.index, methods=["GET"])
        self.add_endpoint("/export_discussion", "export_discussion", self.export_discussion, methods=["GET"])
        self.add_endpoint("/export", "export", self.export, methods=["GET"])
        self.add_endpoint(
            "/new_discussion", "new_discussion", self.new_discussion, methods=["GET"]
        )
        self.add_endpoint("/bot", "bot", self.bot, methods=["POST"])
        self.add_endpoint("/rename", "rename", self.rename, methods=["POST"])
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
            "/help", "help", self.help, methods=["GET"]
        )

        self.prepare_a_new_chatbot()

    def list_models(self):
        models_dir = Path('./models')  # replace with the actual path to the models folder
        models = [f.name for f in models_dir.glob('*.bin')]
        return jsonify(models)

    def list_discussions(self):
        discussions = self.db.get_discussions()
        return jsonify(discussions)


    def prepare_a_new_chatbot(self):
        # Create chatbot
        self.chatbot_bindings = self.create_chatbot()
        # Chatbot conditionning
        self.condition_chatbot()
        

    def create_chatbot(self):
        return Model(
            ggml_model=f"./models/{self.config['model']}", 
            n_ctx=self.config['ctx_size'], 
            seed=self.config['seed'],
            )

    def condition_chatbot(self, conditionning_message = """
Instruction: Act as GPT4All. A kind and helpful AI bot built to help users solve problems.
GPT4All:Welcome! I'm here to assist you with anything you need. What can I do for you today?"""
                          ):
        self.full_message += conditionning_message
        if self.current_discussion is None:
            if self.db.does_last_discussion_have_messages():
                self.current_discussion = self.db.create_discussion()
            else:
                self.current_discussion = self.db.load_last_discussion()
        
        message_id = self.current_discussion.add_message(
            "conditionner", conditionning_message, DiscussionsDB.MSG_TYPE_CONDITIONNING,0
        )
        
        self.full_message_list.append(conditionning_message)


    def prepare_query(self):
        self.bot_says = ""
        self.full_text = ""
        self.is_bot_text_started = False
        #self.current_message = message

    def new_text_callback(self, text: str):
        print(text, end="")
        sys.stdout.flush()
        self.full_text += text
        if self.is_bot_text_started:
            self.bot_says += text
            self.full_message += text
            self.text_queue.put(text)
        #if self.current_message in self.full_text:
        if len(self.prompt_message) <= len(self.full_text):
            self.is_bot_text_started = True

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
        return render_template("chat.html")

    def format_message(self, message):
        # Look for a code block within the message
        pattern = re.compile(r"(```.*?```)", re.DOTALL)
        match = pattern.search(message)

        # If a code block is found, replace it with a <code> tag
        if match:
            code_block = match.group(1)
            message = message.replace(code_block, f"<code>{code_block[3:-3]}</code>")

        # Return the formatted message
        return message

    def export(self):
        return jsonify(self.db.export_to_json())

    def export_discussion(self):
        return jsonify(self.full_message)
    
    def generate_message(self):
        self.generating=True
        self.text_queue=Queue()
        gc.collect()

        self.chatbot_bindings.generate(
            self.prompt_message,#self.full_message,#self.current_message,
            new_text_callback=self.new_text_callback,
            n_predict=len(self.current_message)+self.config['n_predict'],
            temp=self.config['temp'],
            top_k=self.config['top_k'],
            top_p=self.config['top_p'],
            repeat_penalty=self.config['repeat_penalty'],
            repeat_last_n = self.config['repeat_last_n'],
            #seed=self.config['seed'],
            n_threads=8
        )
        self.generating=False

    @stream_with_context
    def parse_to_prompt_stream(self, message, message_id):
        bot_says = ""
        self.stop = False

        # send the message to the bot
        print(f"Received message : {message}")
        # First we need to send the new message ID to the client
        response_id = self.current_discussion.add_message(
            "GPT4All", ""
        )  # first the content is empty, but we'll fill it at the end
        yield (
            json.dumps(
                {
                    "type": "input_message_infos",
                    "message": message,
                    "id": message_id,
                    "response_id": response_id,
                }
            )
        )

        self.current_message = "\nUser: " + message + "\nGPT4All: "
        self.full_message += self.current_message
        self.full_message_list.append(self.current_message)
        
        if len(self.full_message_list) > 5:
            self.prompt_message = '\n'.join(self.full_message_list[-5:])
        else:
            self.prompt_message = self.full_message
        self.prepare_query()
        self.generating = True
        app.config['executor'].submit(self.generate_message)
        while self.generating or not self.text_queue.empty():
            try:
                value = self.text_queue.get(False)
                yield value
            except :
                time.sleep(1)



        self.current_discussion.update_message(response_id, self.bot_says)
        self.full_message_list.append(self.bot_says)
        #yield self.bot_says# .encode('utf-8').decode('utf-8')
        # TODO : change this to use the yield version in order to send text word by word

        return "\n".join(bot_says)

    def bot(self):
        self.stop = True

        if self.current_discussion is None:
            if self.db.does_last_discussion_have_messages():
                self.current_discussion = self.db.create_discussion()
            else:
                self.current_discussion = self.db.load_last_discussion()

        message_id = self.current_discussion.add_message(
            "user", request.json["message"]
        )
        message = f"{request.json['message']}"

        # Segmented (the user receives the output as it comes)
        # We will first send a json entry that contains the message id and so on, then the text as it goes
        return Response(
            stream_with_context(
                self.parse_to_prompt_stream(message, message_id)
            )
        )

    def rename(self):
        data = request.get_json()
        title = data["title"]
        self.current_discussion.rename(title)
        return "renamed successfully"

    def restore_discussion(self, full_message):
        self.prompt_message = full_message

        if len(self.full_message_list)>5:
            self.prompt_message = "\n".join(self.full_message_list[-5:])

        self.chatbot_bindings.generate(
            self.prompt_message,#full_message,
            new_text_callback=self.new_text_callback,
            n_predict=0,#len(full_message),
            temp=self.config['temp'],
            top_k=self.config['top_k'],
            top_p=self.config['top_p'],
            repeat_penalty= self.config['repeat_penalty'],
            repeat_last_n = self.config['repeat_last_n'],
            n_threads=8
        )

    def load_discussion(self):
        data = request.get_json()
        discussion_id = data["id"]
        self.current_discussion = Discussion(discussion_id, self.db)
        messages = self.current_discussion.get_messages()
        
        self.full_message = ""
        self.full_message_list = []
        for message in messages:
            self.full_message += message['sender'] + ": " + message['content'] + "\n"
            self.full_message_list.append(message['sender'] + ": " + message['content'])
        app.config['executor'].submit(self.restore_discussion, self.full_message)

        return jsonify(messages)

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

    def new_discussion(self):
        title = request.args.get("title")
        self.current_discussion = self.db.create_discussion(title)
        # Get the current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        app.config['executor'].submit(self.prepare_a_new_chatbot)

        self.full_message =""

        # Return a success response
        return json.dumps({"id": self.current_discussion.discussion_id, "time": timestamp})

    def update_model_params(self):
        data = request.get_json()
        model =  str(data["model"])
        if self.config['model'] != model:
            print("New model selected")
            self.config['model'] = model
            self.prepare_a_new_chatbot()

        self.config['n_predict'] = int(data["nPredict"])
        self.config['seed'] = int(data["seed"])
        
        self.config['temp'] = float(data["temp"])
        self.config['top_k'] = int(data["topK"])
        self.config['top_p'] = float(data["topP"])
        self.config['repeat_penalty'] = float(data["repeatPenalty"])
        self.config['repeat_last_n'] = int(data["repeatLastN"])

        print("Parameters changed to:")
        print(f"\tTemperature:{self.config['temp']}")
        print(f"\tNPredict:{self.config['n_predict']}")
        print(f"\tSeed:{self.config['seed']}")
        print(f"\top_k:{self.config['top_k']}")
        print(f"\top_p:{self.config['top_p']}")
        print(f"\trepeat_penalty:{self.config['repeat_penalty']}")
        print(f"\trepeat_last_n:{self.config['repeat_last_n']}")
        return jsonify({"status":"ok"})
    
    
    def get_config(self):
        return jsonify(self.config)

    def help(self):
        return render_template("help.html")
    
    def training(self):
        return render_template("training.html")

    def extensions(self):
        return render_template("extensions.html")

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the chatbot Flask app.")
    parser.add_argument(
        "-s", "--seed", type=int, default=None, help="Force using a specific model."
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
        help="launch Flask server in debug mode",
    )
    parser.add_argument(
        "--host", type=str, default="localhost", help="the hostname to listen on"
    )
    parser.add_argument("--port", type=int, default=None, help="the port to listen on")
    parser.add_argument(
        "--db_path", type=str, default=None, help="Database path"
    )
    parser.set_defaults(debug=False)
    args = parser.parse_args()
    config_file_path = "configs/default.yaml"
    config = load_config(config_file_path)

    # Override values in config with command-line arguments
    for arg_name, arg_value in vars(args).items():
        if arg_value is not None:
            config[arg_name] = arg_value

    executor = ThreadPoolExecutor(max_workers=2)
    app.config['executor'] = executor

    bot = Gpt4AllWebUI(app, config)

    if config["debug"]:
        app.run(debug=True, host=config["host"], port=config["port"])
    else:
        app.run(host=config["host"], port=config["port"])
