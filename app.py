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
from concurrent.futures import ThreadPoolExecutor
import sys
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
from pathlib import Path
import gc
app = Flask("GPT4All-WebUI", static_url_path="/static", static_folder="static")
import time
from pyGpt4All.config import load_config, save_config
from pyGpt4All.api import GPT4AllAPI
import shutil
import markdown
class Gpt4AllWebUI(GPT4AllAPI):
    def __init__(self, _app, config:dict, personality:dict, config_file_path) -> None:
        super().__init__(config, personality, config_file_path)

        self.app = _app


        self.add_endpoint(
            "/list_models", "list_models", self.list_models, methods=["GET"]
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
        
        
        self.add_endpoint("/", "", self.index, methods=["GET"])
        self.add_endpoint("/export_discussion", "export_discussion", self.export_discussion, methods=["GET"])
        self.add_endpoint("/export", "export", self.export, methods=["GET"])
        self.add_endpoint(
            "/new_discussion", "new_discussion", self.new_discussion, methods=["GET"]
        )
        self.add_endpoint("/bot", "bot", self.bot, methods=["POST"])
        self.add_endpoint("/run_to", "run_to", self.run_to, methods=["POST"])
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
            "/delete_message", "delete_message", self.delete_message, methods=["GET"]
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


    def list_models(self):
        models_dir = Path('./models')  # replace with the actual path to the models folder
        models = [f.name for f in models_dir.glob('*.bin')]
        return jsonify(models)
    
    def list_personalities(self):
        personalities_dir = Path('./personalities')  # replace with the actual path to the models folder
        personalities = [f.stem for f in personalities_dir.glob('*.yaml')]
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
        return jsonify({"discussion_text":self.get_discussion_to()})
    

    @stream_with_context
    def parse_to_prompt_stream(self, message, message_id):
        bot_says = ""
        self.stop = False

        # send the message to the bot
        print(f"Received message : {message}")
        # First we need to send the new message ID to the client
        response_id = self.current_discussion.add_message(
            self.personality["name"], "", parent = message_id
        )  # first the content is empty, but we'll fill it at the end
        yield (
            json.dumps(
                {
                    "type": "input_message_infos",
                    "bot": self.personality["name"],
                    "user": self.personality["user_name"],
                    "message":markdown.markdown(message),
                    "id": message_id,
                    "response_id": response_id,
                }
            )
        )

        # prepare query and reception
        self.discussion_messages = self.prepare_query(message_id)
        self.prepare_reception()
        self.generating = True
        app.config['executor'].submit(self.generate_message)
        while self.generating:
            try:
                while not self.text_queue.empty():
                    value = self.text_queue.get(False)
                    yield value#.replace("\n","<br>")
            except :
                time.sleep(0.1)

        self.current_discussion.update_message(response_id, self.bot_says)
        self.full_message_list.append(self.bot_says)
        bot_says = markdown.markdown(self.bot_says)

        yield "FINAL:"+bot_says
        return bot_says

    def bot(self):
        self.stop = True

        if self.current_discussion is None:
            if self.db.does_last_discussion_have_messages():
                self.current_discussion = self.db.create_discussion()
            else:
                self.current_discussion = self.db.load_last_discussion()

        message = request.json["message"]
        message_id = self.current_discussion.add_message(
            "user", message, parent=self.current_message_id
        )
        message = f"{request.json['message']}"
        self.current_message_id = message_id

        # Segmented (the user receives the output as it comes)
        # We will first send a json entry that contains the message id and so on, then the text as it goes
        return Response(
            stream_with_context(
                self.parse_to_prompt_stream(message, message_id)
            )
        )
    

    def run_to(self):
        data = request.get_json()
        message_id = int(data["id"])
        self.stop = True
        # Segmented (the user receives the output as it comes)
        # We will first send a json entry that contains the message id and so on, then the text as it goes
        return Response(
            stream_with_context(
                self.parse_to_prompt_stream("",message_id)
            )
        )

    def rename(self):
        data = request.get_json()
        title = data["title"]
        self.current_discussion.rename(title)
        return "renamed successfully"

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
        for message in messages:
            message["content"] = markdown.markdown(message["content"])
        
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

    def delete_message(self):
        discussion_id = request.args.get("id")
        new_rank = self.current_discussion.delete_message(discussion_id)
        return jsonify({"new_rank": new_rank})


    def new_discussion(self):
        title = request.args.get("title")
        timestamp = self.create_new_discussion(title)
        app.config['executor'].submit(self.create_chatbot)

        # Return a success response
        return json.dumps({"id": self.current_discussion.discussion_id, "time": timestamp, "welcome_message":self.personality["welcome_message"]})

    def update_model_params(self):
        data = request.get_json()
        model =  str(data["model"])
        personality =  str(data["personality"])
        if self.config['model'] != model:
            print("New model selected")
            self.config['model'] = model
            self.create_chatbot()

        if self.config['personality']!=data["personality"]:
            self.config['personality'] = data["personality"]
            self.personality = load_config(f"personalities/{self.config['personality']}.yaml")

        self.config['n_predict'] = int(data["nPredict"])
        self.config['seed'] = int(data["seed"])
        self.config['model'] = str(data["model"])
        self.config['voice'] = str(data["voice"])
        self.config['language'] = str(data["language"])
        
        self.config['temp'] = float(data["temp"])
        self.config['top_k'] = int(data["topK"])
        self.config['top_p'] = float(data["topP"])
        self.config['repeat_penalty'] = float(data["repeatPenalty"])
        self.config['repeat_last_n'] = int(data["repeatLastN"])

        save_config(self.config, self.config_file_path)

        print("Parameters changed to:")
        print(f"\tModel:{self.config['model']}")
        print(f"\tPersonality:{self.config['personality']}")
        print(f"\tLanguage:{self.config['language']}")
        print(f"\tVoice:{self.config['voice']}")
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
        help="launch Flask server in debug mode",
    )
    parser.add_argument(
        "--host", type=str, default=None, help="the hostname to listen on"
    )
    parser.add_argument("--port", type=int, default=None, help="the port to listen on")
    parser.add_argument(
        "--db_path", type=str, default=None, help="Database path"
    )
    parser.set_defaults(debug=False)
    args = parser.parse_args()

    # The default configuration must be kept unchanged as it is committed to the repository, 
    # so we have to make a copy that is not comitted
    if args.config=="default":
        args.config = "local_default"
        if not Path(f"configs/local_default.yaml").exists():
            print("No local configuration file found. Building from scratch")
            shutil.copy(f"configs/default.yaml", f"configs/local_default.yaml")
    config_file_path = f"configs/{args.config}.yaml"
    config = load_config(config_file_path)

    # Override values in config with command-line arguments
    for arg_name, arg_value in vars(args).items():
        if arg_value is not None:
            config[arg_name] = arg_value

    personality = load_config(f"personalities/{config['personality']}.yaml")

    executor = ThreadPoolExecutor(max_workers=2)
    app.config['executor'] = executor

    bot = Gpt4AllWebUI(app, config, personality, config_file_path)

    if config["debug"]:
        app.run(debug=True, host=config["host"], port=config["port"])
    else:
        app.run(host=config["host"], port=config["port"])
