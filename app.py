######
# Project       : lollms-webui
# Author        : ParisNeo with the help of the community
# Supported by Nomic-AI
# license       : Apache 2.0
# Description   : 
# A front end Flask application for llamacpp models.
# The official LOLLMS Web ui
# Made by the community for the community
######

__author__ = "parisneo"
__github__ = "https://github.com/ParisNeo/lollms-webui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

__version__ ="6.5(RC2)"

main_repo = "https://github.com/ParisNeo/lollms-webui.git"
import os
import sys
from flask import request, jsonify
import io
import sys
import time
import traceback
import webbrowser
from pathlib import Path

def run_update_script(args=None):
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

from lollms.helpers import ASCIIColors, get_trace_exception, trace_exception
    
try:
    import git
    import logging
    import argparse
    import json
    import traceback
    import subprocess
    import signal
    from lollms.config import InstallOption
    from lollms.binding import LOLLMSConfig, BindingBuilder
    from lollms.personality import AIPersonality
    from lollms.config import BaseConfig
    from lollms.paths import LollmsPaths, gptqlora_repo

    from api.db import Discussion
    from flask import (
        Flask,
        jsonify,
        render_template,
        request,
        send_from_directory
    )

    from flask_socketio import SocketIO
    import yaml
    from geventwebsocket.handler import WebSocketHandler
    import logging
    import psutil
    from lollms.main_config import LOLLMSConfig
    from typing import Optional
    import gc
    import pkg_resources
    
    from api.config import load_config
    from api import LoLLMsAPPI
    import shutil
    import socket

except Exception as ex:
    trace_exception(ex)
    run_update_script()


try:
    import mimetypes
    mimetypes.add_type('application/javascript', '.js')
    mimetypes.add_type('text/css', '.css')    
except:
    ASCIIColors.yellow("Couldn't set mimetype")    
    

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask("Lollms-WebUI", static_url_path="/static", static_folder="static")

#  async_mode='gevent', ping_timeout=1200, ping_interval=120, 
socketio = SocketIO(app,  cors_allowed_origins="*", async_mode='threading',engineio_options={'websocket_compression': False, 'websocket_ping_interval': 20, 'websocket_ping_timeout': 120, 'websocket_max_queue': 100})

app.config['SECRET_KEY'] = 'secret!'
# Set the logging level to WARNING or higher
logging.getLogger('socketio').setLevel(logging.WARNING)
logging.getLogger('engineio').setLevel(logging.WARNING)
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.basicConfig(level=logging.WARNING)



def get_ip_address():
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # Connect to a remote host (doesn't matter which one)
        sock.connect(('8.8.8.8', 80))
        
        # Get the local IP address of the socket
        ip_address = sock.getsockname()[0]
        return ip_address
    except socket.error:
        return None
    finally:
        # Close the socket
        sock.close()


def check_update_(branch_name="main"):
    try:
        # Open the repository
        repo_path = str(Path(__file__).parent)
        ASCIIColors.yellow(f"Checking for updates from {repo_path}")
        repo = git.Repo(repo_path)
        
        # Fetch updates from the remote for the specified branch
        repo.remotes.origin.fetch(refspec=f"refs/heads/{branch_name}:refs/remotes/origin/{branch_name}")
        
        # Compare the local and remote commit IDs for the specified branch
        local_commit = repo.head.commit
        remote_commit = repo.remotes.origin.refs[branch_name].commit
        
        ASCIIColors.yellow(f"update availability: {local_commit != remote_commit}")
        # Return True if there are updates, False otherwise
        return local_commit != remote_commit
    except Exception as e:
        # Handle any errors that may occur during the fetch process
        # trace_exception(e)
        return False


def run_restart_script(args):
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




class LoLLMsWebUI(LoLLMsAPPI):
    def __init__(self, args, _app, _socketio, config:LOLLMSConfig, config_file_path:Path|str, lollms_paths:LollmsPaths) -> None:
        self.args = args
        if len(config.personalities)==0:
            config.personalities.append("generic/lollms")
            config["active_personality_id"] = 0
            config.save_config()

        if config["active_personality_id"]>=len(config["personalities"]) or config["active_personality_id"]<0:
            config["active_personality_id"] = 0
        super().__init__(config, _socketio, config_file_path, lollms_paths)

        if config.auto_update:
            if check_update_():
                ASCIIColors.info("New version found. Updating!")
                self.update_software()

        self.app = _app
        self.cancel_gen = False

        app.template_folder = "web/dist"

        if len(config["personalities"])>0:
            self.personality_category= config["personalities"][config["active_personality_id"]].split("/")[0]
            self.personality_name= config["personalities"][config["active_personality_id"]].split("/")[1]
        else:
            self.personality_category = "generic"
            self.personality_name = "lollms"

        # =========================================================================================
        # Endpoints
        # =========================================================================================
        
        self.add_endpoint(
            "/get_current_personality_files_list", "get_current_personality_files_list", self.get_current_personality_files_list, methods=["GET"]
        )
        self.add_endpoint(
            "/clear_personality_files_list", "clear_personality_files_list", self.clear_personality_files_list, methods=["GET"]
        )
        
        self.add_endpoint("/start_training", "start_training", self.start_training, methods=["POST"])

        self.add_endpoint("/get_lollms_version", "get_lollms_version", self.get_lollms_version, methods=["GET"])
        self.add_endpoint("/get_lollms_webui_version", "get_lollms_webui_version", self.get_lollms_webui_version, methods=["GET"])
        

        self.add_endpoint("/reload_binding", "reload_binding", self.reload_binding, methods=["POST"])
        self.add_endpoint("/update_software", "update_software", self.update_software, methods=["GET"])
        self.add_endpoint("/clear_uploads", "clear_uploads", self.clear_uploads, methods=["GET"])
        self.add_endpoint("/selectdb", "selectdb", self.selectdb, methods=["GET"])

        self.add_endpoint("/restart_program", "restart_program", self.restart_program, methods=["GET"])
        
        self.add_endpoint("/check_update", "check_update", self.check_update, methods=["GET"])
        

    
        self.add_endpoint("/post_to_personality", "post_to_personality", self.post_to_personality, methods=["POST"])

        
        self.add_endpoint("/install_model_from_path", "install_model_from_path", self.install_model_from_path, methods=["GET"])
        
        self.add_endpoint("/reinstall_binding", "reinstall_binding", self.reinstall_binding, methods=["POST"])
        self.add_endpoint("/reinstall_personality", "reinstall_personality", self.reinstall_personality, methods=["POST"])

        self.add_endpoint("/switch_personal_path", "switch_personal_path", self.switch_personal_path, methods=["POST"])

        self.add_endpoint("/add_reference_to_local_model", "add_reference_to_local_model", self.add_reference_to_local_model, methods=["POST"])
        
        
        self.add_endpoint("/add_model_reference", "add_model_reference", self.add_model_reference, methods=["POST"])
        
        self.add_endpoint("/upload_model", "upload_model", self.upload_model, methods=["POST"])
        self.add_endpoint("/upload_avatar", "upload_avatar", self.upload_avatar, methods=["POST"])
        
        
        self.add_endpoint("/list_mounted_personalities", "list_mounted_personalities", self.list_mounted_personalities, methods=["POST"])

        self.add_endpoint("/mount_personality", "mount_personality", self.p_mount_personality, methods=["POST"])
        self.add_endpoint("/remount_personality", "remount_personality", self.p_remount_personality, methods=["POST"])
        
        self.add_endpoint("/unmount_personality", "unmount_personality", self.p_unmount_personality, methods=["POST"])        
        self.add_endpoint("/select_personality", "select_personality", self.p_select_personality, methods=["POST"])

        self.add_endpoint("/get_personality_settings", "get_personality_settings", self.get_personality_settings, methods=["POST"])

        self.add_endpoint("/get_active_personality_settings", "get_active_personality_settings", self.get_active_personality_settings, methods=["GET"])
        self.add_endpoint("/get_active_binding_settings", "get_active_binding_settings", self.get_active_binding_settings, methods=["GET"])

        self.add_endpoint("/set_active_personality_settings", "set_active_personality_settings", self.set_active_personality_settings, methods=["POST"])
        self.add_endpoint("/set_active_binding_settings", "set_active_binding_settings", self.set_active_binding_settings, methods=["POST"])

        self.add_endpoint(
            "/disk_usage", "disk_usage", self.disk_usage, methods=["GET"]
        )

        self.add_endpoint(
            "/ram_usage", "ram_usage", self.ram_usage, methods=["GET"]
        )
        self.add_endpoint(
            "/vram_usage", "vram_usage", self.vram_usage, methods=["GET"]
        )


        self.add_endpoint(
            "/list_bindings", "list_bindings", self.list_bindings, methods=["GET"]
        )
        self.add_endpoint(
            "/list_extensions", "list_extensions", self.list_extensions, methods=["GET"]
        )
        
        self.add_endpoint(
            "/list_models", "list_models", self.list_models, methods=["GET"]
        )
        self.add_endpoint(
            "/get_active_model", "get_active_model", self.get_active_model, methods=["GET"]
        )
        
        self.add_endpoint(
            "/list_personalities_categories", "list_personalities_categories", self.list_personalities_categories, methods=["GET"]
        )
        self.add_endpoint(
            "/list_personalities", "list_personalities", self.list_personalities, methods=["GET"]
        )
        
        self.add_endpoint(
            "/list_discussions", "list_discussions", self.list_discussions, methods=["GET"]
        )
        
        self.add_endpoint("/delete_personality", "delete_personality", self.delete_personality, methods=["GET"])
                
        self.add_endpoint("/", "", self.index, methods=["GET"])
        self.add_endpoint("/settings/", "", self.index, methods=["GET"])
        self.add_endpoint("/playground/", "", self.index, methods=["GET"])
        
        self.add_endpoint("/<path:filename>", "serve_static", self.serve_static, methods=["GET"])
        self.add_endpoint("/user_infos/<path:filename>", "serve_user_infos", self.serve_user_infos, methods=["GET"])
        
        self.add_endpoint("/images/<path:filename>", "serve_images", self.serve_images, methods=["GET"])
        self.add_endpoint("/bindings/<path:filename>", "serve_bindings", self.serve_bindings, methods=["GET"])
        self.add_endpoint("/personalities/<path:filename>", "serve_personalities", self.serve_personalities, methods=["GET"])
        self.add_endpoint("/outputs/<path:filename>", "serve_outputs", self.serve_outputs, methods=["GET"])
        self.add_endpoint("/data/<path:filename>", "serve_data", self.serve_data, methods=["GET"])
        self.add_endpoint("/help/<path:filename>", "serve_help", self.serve_help, methods=["GET"])
        
        self.add_endpoint("/uploads/<path:filename>", "serve_uploads", self.serve_uploads, methods=["GET"])

        
        self.add_endpoint("/export_discussion", "export_discussion", self.export_discussion, methods=["GET"])
        self.add_endpoint("/export", "export", self.export, methods=["GET"])

        self.add_endpoint("/stop_gen", "stop_gen", self.stop_gen, methods=["GET"])

        self.add_endpoint("/rename", "rename", self.rename, methods=["POST"])
        self.add_endpoint("/edit_title", "edit_title", self.edit_title, methods=["POST"])

        self.add_endpoint(
            "/delete_discussion",
            "delete_discussion",
            self.delete_discussion,
            methods=["POST"],
        )

        self.add_endpoint(
            "/edit_message", "edit_message", self.edit_message, methods=["GET"]
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
            "/upgrade_to_gpu", "upgrade_to_gpu", self.upgrade_to_gpu, methods=["GET"]
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

        self.add_endpoint(
            "/get_presets", "get_presets", self.get_presets, methods=["GET"]
        )      

        self.add_endpoint(
            "/add_preset", "add_preset", self.add_preset, methods=["POST"]
        )

        self.add_endpoint(
            "/save_presets", "save_presets", self.save_presets, methods=["POST"]
        )

        self.add_endpoint(
            "/execute_python_code", "execute_python_code", self.execute_python_code, methods=["POST"]
        )
        



    def execute_python_code(self):
        """Executes Python code and returns the output."""
        
        data = request.get_json()
        code = data["code"]

        ASCIIColors.info("Executing python code:")
        ASCIIColors.yellow(code)

        def spawn_process(code):
            """Executes Python code and returns the output as JSON."""

            # Start the timer.
            start_time = time.time()

            # Create a temporary file.
            tmp_file = self.lollms_paths.personal_data_path/"ai_code.py"
            with open(tmp_file,"w") as f:
                f.write(code)

            try:
                # Execute the Python code in a temporary file.
                process = subprocess.Popen(
                    ["python", str(tmp_file)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                # Get the output and error from the process.
                output, error = process.communicate()
            except Exception as ex:
                # Stop the timer.
                execution_time = time.time() - start_time
                error_message = f"Error executing Python code: {ex}"
                error_json = {"output": "<div class='text-red-500'>"+ex+"\n"+get_trace_exception(ex)+"</div>", "execution_time": execution_time}
                return json.dumps(error_json)

            # Stop the timer.
            execution_time = time.time() - start_time

            # Check if the process was successful.
            if process.returncode != 0:
                # The child process threw an exception.
                error_message = f"Error executing Python code: {error.decode('utf8')}"
                error_json = {"output": "<div class='text-red-500'>"+error_message+"</div>", "execution_time": execution_time}
                return json.dumps(error_json)

            # The child process was successful.
            output_json = {"output": output.decode("utf8"), "execution_time": execution_time}
            return json.dumps(output_json)
        return spawn_process(code)

    def copy_files(self, src, dest):
        for item in os.listdir(src):
            src_file = os.path.join(src, item)
            dest_file = os.path.join(dest, item)
            
            if os.path.isfile(src_file):
                shutil.copy2(src_file, dest_file)
                
    def get_presets(self):
        presets = []
        presets_folder = Path("__file__").parent/"presets"
        for filename in presets_folder.glob('*.yaml'):
            with open(filename, 'r', encoding='utf-8') as file:
                preset = yaml.safe_load(file)
                if preset is not None:
                    presets.append(preset)
        presets_folder = self.lollms_paths.personal_databases_path/"lollms_playground_presets"
        presets_folder.mkdir(exist_ok=True, parents=True)
        for filename in presets_folder.glob('*.yaml'):
            with open(filename, 'r', encoding='utf-8') as file:
                preset = yaml.safe_load(file)
                if preset is not None:
                    presets.append(preset)
        return jsonify(presets)

    def add_preset(self):
        # Get the JSON data from the POST request.
        preset_data = request.get_json()
        presets_folder = self.lollms_paths.personal_databases_path/"lollms_playground_presets"
        if not presets_folder.exists():
            presets_folder.mkdir(exist_ok=True, parents=True)

        fn = preset_data["name"].lower().replace(" ","_")
        filename = presets_folder/f"{fn}.yaml"
        with open(filename, 'w', encoding='utf-8') as file:
            yaml.dump(preset_data, file)
        return jsonify({"status": True})

    def del_preset(self):
        presets_folder = self.lollms_paths.personal_databases_path/"lollms_playground_presets"
        if not presets_folder.exists():
            presets_folder.mkdir(exist_ok=True, parents=True)
            self.copy_files("presets",presets_folder)
        presets = []
        for filename in presets_folder.glob('*.yaml'):
            print(filename)
            with open(filename, 'r') as file:
                preset = yaml.safe_load(file)
                if preset is not None:
                    presets.append(preset)
        return jsonify(presets)


    def save_presets(self):
        """Saves a preset to a file.

        Args:
            None.

        Returns:
            None.
        """

        # Get the JSON data from the POST request.
        preset_data = request.get_json()

        presets_file = self.lollms_paths.personal_databases_path/"presets.json"
        # Save the JSON data to a file.
        with open(presets_file, "w") as f:
            json.dump(preset_data, f, indent=4)

        return jsonify({"status":True,"message":"Preset saved successfully!"})
        
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

        for category_folder in  personalities_folder.iterdir():
            cat = category_folder.stem
            if category_folder.is_dir() and not category_folder.stem.startswith('.'):
                personalities[category_folder.name] = []
                for personality_folder in category_folder.iterdir():
                    pers = personality_folder.stem
                    if personality_folder.is_dir() and not personality_folder.stem.startswith('.'):
                        personality_info = {"folder":personality_folder.stem}
                        config_path = personality_folder / 'config.yaml'
                        if not config_path.exists():
                            """
                            try:
                                shutil.rmtree(str(config_path.parent))
                                ASCIIColors.warning(f"Deleted useless personality: {config_path.parent}")
                            except Exception as ex:
                                ASCIIColors.warning(f"Couldn't delete personality ({ex})")
                            """
                            continue                                    
                        try:
                            scripts_path = personality_folder / 'scripts'
                            personality_info['has_scripts'] = scripts_path.exists()
                            with open(config_path) as config_file:
                                config_data = yaml.load(config_file, Loader=yaml.FullLoader)
                                personality_info['name'] = config_data.get('name',"No Name")
                                personality_info['description'] = config_data.get('personality_description',"")
                                personality_info['author'] = config_data.get('author', 'ParisNeo')
                                personality_info['version'] = config_data.get('version', '1.0.0')
                                personality_info['installed'] = (self.lollms_paths.personal_configuration_path/f"personality_{personality_folder.stem}.yaml").exists() or personality_info['has_scripts']
                                personality_info['help'] = config_data.get('help', '')
                                personality_info['commands'] = config_data.get('commands', '')

                            languages_path = personality_folder/ 'languages'

                            real_assets_path = personality_folder/ 'assets'
                            assets_path = Path("personalities") / cat / pers / 'assets'
                            gif_logo_path = assets_path / 'logo.gif'
                            webp_logo_path = assets_path / 'logo.webp'
                            png_logo_path = assets_path / 'logo.png'
                            jpg_logo_path = assets_path / 'logo.jpg'
                            jpeg_logo_path = assets_path / 'logo.jpeg'
                            svg_logo_path = assets_path / 'logo.svg'
                            bmp_logo_path = assets_path / 'logo.bmp'

                            gif_logo_path_ = real_assets_path / 'logo.gif'
                            webp_logo_path_ = real_assets_path / 'logo.webp'
                            png_logo_path_ = real_assets_path / 'logo.png'
                            jpg_logo_path_ = real_assets_path / 'logo.jpg'
                            jpeg_logo_path_ = real_assets_path / 'logo.jpeg'
                            svg_logo_path_ = real_assets_path / 'logo.svg'
                            bmp_logo_path_ = real_assets_path / 'logo.bmp'

                            if languages_path.exists():
                                personality_info['languages']=[f.stem for f in languages_path.iterdir() if f.suffix==".yaml"]
                            else:
                                personality_info['languages']=None
                                
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
                            elif svg_logo_path_.exists():
                                personality_info['avatar'] = str(svg_logo_path).replace("\\","/")
                            elif bmp_logo_path_.exists():
                                personality_info['avatar'] = str(bmp_logo_path).replace("\\","/")
                            else:
                                personality_info['avatar'] = ""
                            
                            personalities[category_folder.name].append(personality_info)
                        except Exception as ex:
                            ASCIIColors.warning(f"Couldn't load personality from {personality_folder} [{ex}]")
                            trace_exception(ex)
        return json.dumps(personalities)
    
    def get_personality(self):
        category = request.args.get('category')
        name = request.args.get('name')
        personality_folder = self.lollms_paths.personalities_zoo_path/f"{category}"/f"{name}"
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

        ASCIIColors.info(f"Requested updating of setting {data['setting_name']} to {data['setting_value']}")
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

        elif setting_name== "personality_folder":
            self.personality_name=data['setting_value']
            if len(self.config["personalities"])>0:
                if self.config["active_personality_id"]<len(self.config["personalities"]):
                    self.config["personalities"][self.config["active_personality_id"]] = f"{self.personality_category}/{self.personality_name}"
                else:
                    self.config["active_personality_id"] = 0
                    self.config["personalities"][self.config["active_personality_id"]] = f"{self.personality_category}/{self.personality_name}"
                
                if self.personality_category!="Custom":
                    personality_fn = self.lollms_paths.personalities_zoo_path/self.config["personalities"][self.config["active_personality_id"]]
                else:
                    personality_fn = self.lollms_paths.personal_personalities_path/self.config["personalities"][self.config["active_personality_id"]].split("/")[-1]
                self.personality.load_personality(personality_fn)
            else:
                self.config["personalities"].append(f"{self.personality_category}/{self.personality_name}")
        elif setting_name== "override_personality_model_parameters":
            self.config["override_personality_model_parameters"]=bool(data['setting_value'])

        elif setting_name == "model_name":
            self.config["model_name"]=data['setting_value']
            if self.config["model_name"] is not None:
                try:
                    self.model = None
                    if self.binding:
                        del self.binding

                    self.binding = None
                    for per in self.mounted_personalities:
                        per.model = None
                    gc.collect()
                    self.binding = BindingBuilder().build_binding(self.config, self.lollms_paths)
                    self.model = self.binding.build_model()
                    for per in self.mounted_personalities:
                        per.model = self.model
                except Exception as ex:
                    # Catch the exception and get the traceback as a list of strings
                    traceback_lines = traceback.format_exception(type(ex), ex, ex.__traceback__)

                    # Join the traceback lines into a single string
                    traceback_text = ''.join(traceback_lines)
                    ASCIIColors.error(f"Couldn't load model: [{ex}]")
                    ASCIIColors.error(traceback_text)
                    return jsonify({ "status":False, 'error':str(ex)})
            else:
                ASCIIColors.warning("Trying to set a None model. Please select a model for the binding")
            print("update_settings : New model selected")

        elif setting_name== "binding_name":
            if self.config['binding_name']!= data['setting_value']:
                print(f"New binding selected : {data['setting_value']}")
                self.config["binding_name"]=data['setting_value']
                try:
                    if self.binding:
                        self.binding.destroy_model()

                    self.binding = None
                    self.model = None
                    for per in self.mounted_personalities:
                        per.model = None
                    gc.collect()
                    self.binding = BindingBuilder().build_binding(self.config, self.lollms_paths)
                    self.model = None
                    self.config.save_config()
                    ASCIIColors.green("Model loaded successfully")
                except Exception as ex:
                    ASCIIColors.error(f"Couldn't build binding: [{ex}]")
                    trace_exception(ex)
                    return jsonify({"status":False, 'error':str(ex)})
            else:
                if self.config["debug"]:
                    print(f"Configuration {data['setting_name']} set to {data['setting_value']}")
                return jsonify({'setting_name': data['setting_name'], "status":True})

        else:
            if data['setting_name'] in self.config.config.keys():
                self.config[data['setting_name']] = data['setting_value']
            else:
                if self.config["debug"]:
                    print(f"Configuration {data['setting_name']} couldn't be set to {data['setting_value']}")
                return jsonify({'setting_name': data['setting_name'], "status":False})

        if self.config["debug"]:
            print(f"Configuration {data['setting_name']} set to {data['setting_value']}")
            
        ASCIIColors.success(f"Configuration {data['setting_name']} updated")
        if self.config.auto_save:
            self.config.save_config()
        # Tell that the setting was changed
        return jsonify({'setting_name': data['setting_name'], "status":True})



    def apply_settings(self):
        data = request.get_json()
        try:
            for key in self.config.config.keys():
                self.config.config[key] = data["config"].get(key, self.config.config[key])
            ASCIIColors.success("OK")
            self.rebuild_personalities()
            if self.config.auto_save:
                self.config.save_config()
            return jsonify({"status":True})
        except Exception as ex:    
            return jsonify({"status":False,"error":str(ex)})

    
    def upgrade_to_gpu(self):
        ASCIIColors.yellow("Received command to upgrade to GPU")
        ASCIIColors.info("Installing cuda toolkit")
        res = subprocess.check_call(["conda", "install", "-c", "nvidia/label/cuda-11.7.0", "-c", "nvidia", "-c", "conda-forge",  "cuda-toolkit", "ninja", "git",  "--force-reinstall", "-y"])
        if res!=0:
            ASCIIColors.red("Couldn't install cuda toolkit")
            return jsonify({'status':False, "error": "Couldn't install cuda toolkit. Make sure you are running from conda environment"})
        ASCIIColors.green("Cuda toolkit installed successfully")
        ASCIIColors.yellow("Removing pytorch")
        try:
            res = subprocess.check_call(["pip","uninstall","torch", "torchvision", "torchaudio", "-y"])
        except :
            pass
        ASCIIColors.green("PyTorch unstalled successfully")
        ASCIIColors.yellow("Installing pytorch with cuda support")
        res = subprocess.check_call(["pip","install","--upgrade","torch==2.0.1+cu117", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cu117","--no-cache"])
        if res==0:
            ASCIIColors.green("PyTorch installed successfully")
            import torch
            if torch.cuda.is_available():
                ASCIIColors.success("CUDA is supported.")
            else:
                ASCIIColors.warning("CUDA is not supported. This may mean that the upgrade didn't succeed. Try rebooting the application")
        else:
            ASCIIColors.green("An error hapened")
        self.config.enable_gpu=True
        return jsonify({'status':res==0})
    


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

    def vram_usage(self) -> Optional[dict]:
        try:
            output = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.total,memory.used,gpu_name', '--format=csv,nounits,noheader'])
            lines = output.decode().strip().split('\n')
            vram_info = [line.split(',') for line in lines]
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {
            "nb_gpus": 0
            }
        
        ram_usage = {
            "nb_gpus": len(vram_info)
        }
        
        if vram_info is not None:
            for i, gpu in enumerate(vram_info):
                ram_usage[f"gpu_{i}_total_vram"] = int(gpu[0])*1024*1024
                ram_usage[f"gpu_{i}_used_vram"] = int(gpu[1])*1024*1024
                ram_usage[f"gpu_{i}_model"] = gpu[2].strip()
        else:
            # Set all VRAM-related entries to None
            ram_usage["gpu_0_total_vram"] = None
            ram_usage["gpu_0_used_vram"] = None
            ram_usage["gpu_0_model"] = None
        
        return jsonify(ram_usage)

    def disk_usage(self):
        current_drive = Path.cwd().anchor
        drive_disk_usage = psutil.disk_usage(current_drive)
        try:
            models_folder_disk_usage = psutil.disk_usage(str(self.lollms_paths.personal_models_path/f'{self.config["binding_name"]}'))
            return jsonify( {
                "total_space":drive_disk_usage.total,
                "available_space":drive_disk_usage.free,
                "usage":drive_disk_usage.used,
                "percent_usage":drive_disk_usage.percent,

                "binding_disk_total_space":models_folder_disk_usage.total,
                "binding_disk_available_space":models_folder_disk_usage.free,
                "binding_models_usage": models_folder_disk_usage.used,
                "binding_models_percent_usage": models_folder_disk_usage.percent,
                })
        except Exception as ex:
            return jsonify({
                "total_space":drive_disk_usage.total,
                "available_space":drive_disk_usage.free,
                "percent_usage":drive_disk_usage.percent,

                "binding_disk_total_space": None,
                "binding_disk_available_space": None,
                "binding_models_usage": None,
                "binding_models_percent_usage": None,
                })

    def find_extension(self, path:Path, filename:str, exts:list)->Path:
        for ext in exts:
            full_path = path/(filename+ext)
            if full_path.exists():
                return full_path
        return None

    def list_bindings(self):
        bindings_dir = self.lollms_paths.bindings_zoo_path  # replace with the actual path to the models folder
        bindings=[]
        for f in bindings_dir.iterdir():
            card = f/"binding_card.yaml"
            if card.exists():
                try:
                    bnd = load_config(card)
                    bnd["folder"]=f.stem
                    installed = (self.lollms_paths.personal_configuration_path/"bindings"/f.stem/f"config.yaml").exists()
                    bnd["installed"]=installed
                    icon_file = self.find_extension(self.lollms_paths.bindings_zoo_path/f"{f.name}", "logo", [".svg",".gif",".png"])
                    if icon_file is not None:
                        icon_path = Path(f"bindings/{f.name}/logo{icon_file.suffix}")
                        bnd["icon"]=str(icon_path)

                    bindings.append(bnd)
                except Exception as ex:
                    print(f"Couldn't load backend card : {f}\n\t{ex}")
        return jsonify(bindings)

    def list_extensions(self):
        return jsonify([])

    

    def list_models(self):
        if self.binding is not None:
            models = self.binding.list_models(self.config)
            ASCIIColors.yellow("Listing models")
            return jsonify(models)
        else:
            return jsonify([])
    
    def get_active_model(self):
        if self.binding is not None:
            try:
                models = self.binding.list_models(self.config)
                index = models.index(self.config.model_name)
                ASCIIColors.yellow("Listing models")
                return jsonify({"model":models[index],"index":index})
            except Exception as ex:
                return jsonify(None)
        else:
            return jsonify(None)

    def list_personalities_categories(self):
        personalities_categories_dir = self.lollms_paths.personalities_zoo_path  # replace with the actual path to the models folder
        personalities_categories = [f.stem for f in personalities_categories_dir.iterdir() if f.is_dir() and not f.name.startswith(".")]
        return jsonify(personalities_categories)
    
    def list_personalities(self):
        category = request.args.get('category')
        if not category:
            return jsonify([])
            
        try:
            personalities_dir = self.lollms_paths.personalities_zoo_path/f'{category}'  # replace with the actual path to the models folder
            personalities = [f.stem for f in personalities_dir.iterdir() if f.is_dir() and not f.name.startswith(".")]
        except Exception as ex:
            personalities=[]
            ASCIIColors.error(f"No personalities found. Using default one {ex}")
        return jsonify(personalities)



    def list_discussions(self):
        discussions = self.db.get_discussions()
        return jsonify(discussions)


    def delete_personality(self):
        category = request.args.get('category')
        name = request.args.get('name')
        path = Path("personalities")/category/name
        try:
            shutil.rmtree(path)
            return jsonify({'status':True})
        except Exception as ex:
            return jsonify({'status':False,'error':str(ex)})

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

    def serve_user_infos(self, filename):
        path = str(self.lollms_paths.personal_user_infos_path/("/".join(filename.split("/")[:-1])))
                            
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

        path = str(root_dir/"/".join(filename.split("/")[:-1]))
                            
        fn = filename.split("/")[-1]
        return send_from_directory(path, fn)



    def export(self):
        return jsonify(self.db.export_to_json())

    def export_discussion(self):
        return jsonify({"discussion_text":self.get_discussion_to()})
    

            
    def get_generation_status(self):
        return jsonify({"status":self.busy}) 
    
    def stop_gen(self):
        self.cancel_gen = True
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
        if data["path"]=="":
            return jsonify({"status": False, "error":"Empty model path"})         
            
        path = Path(data["path"])
        if path.exists():
            self.config.reference_model(path)
            return jsonify({"status": True})         
        else:        
            return jsonify({"status": False, "error":"Model not found"})         

    def list_mounted_personalities(self):
        ASCIIColors.yellow("- Listing mounted personalities")
        return jsonify({"status": True,
                        "personalities":self.config["personalities"],
                        "active_personality_id":self.config["active_personality_id"]
                        })         

    def install_model_from_path(self):
        from tkinter import Tk
        from tkinter.filedialog import askopenfilename
        
        ASCIIColors.info(f"- Selecting model ...")
        # Define the file types
        filetypes = [
            ("Model file", self.binding.supported_file_extensions),
        ]
        # Create the Tkinter root window
        root = Tk()

        # Hide the root window
        root.withdraw()

        # Open the file dialog
        file_path = askopenfilename(filetypes=filetypes)
        
        file_path = Path(file_path)
        #
        with open(str(self.lollms_paths.personal_models_path/self.config.binding_name/(file_path.stem+".reference")),"w") as f:
            f.write(file_path)
        
        return jsonify({
                        "status": True
                    })
        
    def reinstall_personality(self):
        try:
            data = request.get_json()
            # Further processing of the data
        except Exception as e:
            print(f"Error occurred while parsing JSON: {e}")
            return jsonify({"status":False, 'error':str(e)})
        if not 'name' in data:
            data['name']=self.config.personalities[self.config["active_personality_id"]]
        try:
            personality_path = lollms_paths.personalities_zoo_path / data['name']
            ASCIIColors.info(f"- Reinstalling personality {data['name']}...")
            ASCIIColors.info("Unmounting personality")
            idx = self.config.personalities.index(data['name'])
            print(f"index = {idx}")
            self.mounted_personalities[idx] = None
            gc.collect()
            try:
                self.mounted_personalities[idx] = AIPersonality(personality_path,
                                            self.lollms_paths, 
                                            self.config,
                                            model=self.model,
                                            app=self,
                                            run_scripts=True,installation_option=InstallOption.FORCE_INSTALL)
                return jsonify({"status":True})
            except Exception as ex:
                ASCIIColors.error(f"Personality file not found or is corrupted ({data['name']}).\nReturned the following exception:{ex}\nPlease verify that the personality you have selected exists or select another personality. Some updates may lead to change in personality name or category, so check the personality selection in settings to be sure.")
                ASCIIColors.info("Trying to force reinstall")
                return jsonify({"status":False, 'error':str(e)})

        except Exception as e:
            return jsonify({"status":False, 'error':str(e)})
    
    def post_to_personality(self):
        data = request.get_json()
        if hasattr(self.personality.processor,'handle_request'):
            return self.personality.processor.handle_request(data)
        else:
            return jsonify({})


    def reinstall_binding(self):
        try:
            data = request.get_json()
            # Further processing of the data
        except Exception as e:
            print(f"Error occurred while parsing JSON: {e}")
            return jsonify({"status":False, 'error':str(e)})
        ASCIIColors.info(f"- Reinstalling binding {data['name']}...")
        try:
            ASCIIColors.info("Unmounting binding and model")
            self.binding = None
            self.model = None
            for per in self.mounted_personalities:
                per.model = None
            gc.collect()
            ASCIIColors.info("Reinstalling binding")
            self.binding =  BindingBuilder().build_binding(self.config, self.lollms_paths, InstallOption.FORCE_INSTALL)
            ASCIIColors.success("Binding reinstalled successfully")

            ASCIIColors.info("Please select a model")
            return jsonify({"status": True}) 
        except Exception as ex:
            ASCIIColors.error(f"Couldn't build binding: [{ex}]")
            trace_exception(ex)
            return jsonify({"status":False, 'error':str(ex)})
        

    def clear_uploads(self):
        ASCIIColors.info("")
        ASCIIColors.info("")
        ASCIIColors.info("")
        ASCIIColors.info(" ╔══════════════════════════════════════════════════╗")
        ASCIIColors.info(" ║               Removing all uploads               ║")
        ASCIIColors.info(" ╚══════════════════════════════════════════════════╝")
        ASCIIColors.info("")
        ASCIIColors.info("")
        ASCIIColors.info("")        
        try:
            folder_path = self.lollms_paths.personal_uploads_path
            # Iterate over all files and directories in the folder
            for entry in folder_path.iterdir():
                if entry.is_file():
                    # Remove file
                    entry.unlink()
                elif entry.is_dir():
                    # Remove directory (recursively)
                    shutil.rmtree(entry)
            print(f"All files and directories inside '{folder_path}' have been removed successfully.")
            return {"status": True}
        except OSError as e:
            ASCIIColors.error(f"Couldn't clear the upload folder.\nMaybe some files are opened somewhere else.\Try doing it manually")
            return {"status": False, 'error': "Couldn't clear the upload folder.\nMaybe some files are opened somewhere else.\Try doing it manually"}


    def update_software(self):
        ASCIIColors.info("")
        ASCIIColors.info("")
        ASCIIColors.info("")
        ASCIIColors.info(" ╔══════════════════════════════════════════════════╗")
        ASCIIColors.info(" ║               Upgrading backend                  ║")
        ASCIIColors.info(" ╚══════════════════════════════════════════════════╝")
        ASCIIColors.info("")
        ASCIIColors.info("")
        ASCIIColors.info("")        
        # Perform a 'git pull' to check for updates
        try:
            # Execute 'git pull' and redirect the output to the console
            process = subprocess.Popen(['git', 'pull'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            # Read and print the output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())

            # Wait for the process to finish and get the return code
            return_code = process.poll()

            if return_code == 0:
                return {"status": True}
            else:
                return {"status": False, 'error': f"git pull failed with return code {return_code}"}
        
        except subprocess.CalledProcessError as ex:
            # There was an error in 'git pull' command
            return {"status": False, 'error': str(ex)}
        
    def selectdb(self):
        from tkinter import Tk, filedialog
        # Initialize Tkinter
        root = Tk()
        root.withdraw()

        # Show file selection dialog
        file_path = filedialog.askopenfilename()

    def check_update(self):
        if self.config.auto_update:
            res = check_update_()
            return jsonify({'update_availability':res})
        else:
            return jsonify({'update_availability':False})

    def restart_program(self):
        ASCIIColors.info("")
        ASCIIColors.info("")
        ASCIIColors.info("")
        ASCIIColors.info(" ╔══════════════════════════════════════════════════╗")
        ASCIIColors.info(" ║              Restarting backend                  ║")
        ASCIIColors.info(" ╚══════════════════════════════════════════════════╝")
        ASCIIColors.info("")
        ASCIIColors.info("")
        ASCIIColors.info("")
        run_restart_script(self.args)
        


    def update_software(self):
        ASCIIColors.info("")
        ASCIIColors.info("")
        ASCIIColors.info("")
        ASCIIColors.info(" ╔══════════════════════════════════════════════════╗")
        ASCIIColors.info(" ║                Updating backend                  ║")
        ASCIIColors.info(" ╚══════════════════════════════════════════════════╝")
        ASCIIColors.info("")
        ASCIIColors.info("")
        ASCIIColors.info("")
        run_update_script(self.args)
        
    def get_current_personality_files_list(self):
        if self.personality is None:
            return jsonify({"state":False, "error":"No personality selected"})
        return jsonify({"state":True, "files":[{"name":Path(f).name, "size":Path(f).stat().st_size} for f in self.personality.files]})

    def clear_personality_files_list(self):
        if self.personality is None:
            return jsonify({"state":False, "error":"No personality selected"})
        self.personality.remove_all_files()
        return jsonify({"state":True})

    def start_training(self):
        if self.config.enable_gpu:
            if not self.lollms_paths.gptqlora_path.exists():
                # Clone the repository to the target path
                ASCIIColors.info("No gptqlora found in your personal space.\nCloning the gptqlora repo")
                subprocess.run(["git", "clone", gptqlora_repo, self.lollms_paths.gptqlora_path])
                subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=self.lollms_paths.gptqlora_path)
                
            data = request.get_json()
            ASCIIColors.info(f"--- Trainging of model {data['model_name']} requested ---")
            ASCIIColors.info(f"Cleaning memory:")
            fn = self.binding.binding_folder_name
            del self.binding
            self.binding = None
            self.model = None
            for per in self.mounted_personalities:
                per.model = None
            gc.collect()
            ASCIIColors.info(f"issuing command : python gptqlora.py --model_path {self.lollms_paths.personal_models_path/fn/data['model_name']}")
            subprocess.run(["python", "gptqlora.py", "--model_path", self.lollms_paths.personal_models_path/fn/data["model_name"]],cwd=self.lollms_paths.gptqlora_path)    
            return jsonify({'status':True})

    def get_lollms_version(self):
        version = pkg_resources.get_distribution('lollms').version
        ASCIIColors.yellow("Lollms version : "+ version)
        return jsonify({"version":version})

    def get_lollms_webui_version(self):
        version = __version__
        ASCIIColors.yellow("Lollms webui version : "+ version)
        return jsonify({"version":version})
    
    
    def reload_binding(self):
        try:
            data = request.get_json()
            # Further processing of the data
        except Exception as e:
            print(f"Error occurred while parsing JSON: {e}")
            return jsonify({"status":False, 'error':str(e)})
        ASCIIColors.info(f"- Reloading binding {data['name']}...")
        try:
            ASCIIColors.info("Unmounting binding and model")
            self.binding = None
            self.model = None
            for personality in self.mounted_personalities:
                personality.model = None
            gc.collect()
            ASCIIColors.info("Reloading binding")
            self.binding =  BindingBuilder().build_binding(self.config, self.lollms_paths)
            ASCIIColors.info("Binding loaded successfully")

            try:
                ASCIIColors.info("Reloading model")
                self.model = self.binding.build_model()
                ASCIIColors.info("Model reloaded successfully")
            except Exception as ex:
                print(f"Couldn't build model: [{ex}]")
                trace_exception(ex)
            try:
                self.rebuild_personalities(reload_all=True)
            except Exception as ex:
                print(f"Couldn't reload personalities: [{ex}]")
            return jsonify({"status": True}) 
        except Exception as ex:
            ASCIIColors.error(f"Couldn't build binding: [{ex}]")
            trace_exception(ex)
            return jsonify({"status":False, 'error':str(ex)})
                

    def p_mount_personality(self):
        print("- Mounting personality")
        try:
            data = request.get_json()
            # Further processing of the data
        except Exception as e:
            print(f"Error occurred while parsing JSON: {e}")
            return
        category = data['category']
        name = data['folder']

        language = data.get('language', None)

        package_path = f"{category}/{name}"
        package_full_path = self.lollms_paths.personalities_zoo_path/package_path
        config_file = package_full_path / "config.yaml"
        if config_file.exists():
            if language:
                package_path += ":" + language
            self.config["personalities"].append(package_path)
            self.mounted_personalities = self.rebuild_personalities()
            self.personality = self.mounted_personalities[self.config["active_personality_id"]]
            ASCIIColors.success("ok")
            if self.config["active_personality_id"]<0:
                return jsonify({"status": False,
                                "personalities":self.config["personalities"],
                                "active_personality_id":self.config["active_personality_id"]
                                })         
            else:
                if self.config.auto_save:
                    ASCIIColors.info("Saving configuration")
                    self.config.save_config()
                return jsonify({"status": True,
                                "personalities":self.config["personalities"],
                                "active_personality_id":self.config["active_personality_id"]
                                })         
        else:
            pth = str(config_file).replace('\\','/')
            ASCIIColors.error(f"nok : Personality not found @ {pth}")
            return jsonify({"status": False, "error":f"Personality not found @ {pth}"})         



    def p_remount_personality(self):
        print("- Remounting personality")
        try:
            data = request.get_json()
            # Further processing of the data
        except Exception as e:
            print(f"Error occurred while parsing JSON: {e}")
            return
        category = data['category']
        name = data['folder']




        package_path = f"{category}/{name}"
        package_full_path = self.lollms_paths.personalities_zoo_path/package_path
        config_file = package_full_path / "config.yaml"
        if config_file.exists():
            ASCIIColors.info(f"Unmounting personality {package_path}")
            index = self.config["personalities"].index(f"{category}/{name}")
            self.config["personalities"].remove(f"{category}/{name}")
            if self.config["active_personality_id"]>=index:
                self.config["active_personality_id"]=0
            if len(self.config["personalities"])>0:
                self.mounted_personalities = self.rebuild_personalities()
                self.personality = self.mounted_personalities[self.config["active_personality_id"]]
            else:
                self.personalities = ["generic/lollms"]
                self.mounted_personalities = self.rebuild_personalities()
                self.personality = self.mounted_personalities[self.config["active_personality_id"]]


            ASCIIColors.info(f"Mounting personality {package_path}")
            self.config["personalities"].append(package_path)
            self.mounted_personalities = self.rebuild_personalities()
            self.personality = self.mounted_personalities[self.config["active_personality_id"]]
            ASCIIColors.success("ok")
            if self.config["active_personality_id"]<0:
                return jsonify({"status": False,
                                "personalities":self.config["personalities"],
                                "active_personality_id":self.config["active_personality_id"]
                                })         
            else:
                return jsonify({"status": True,
                                "personalities":self.config["personalities"],
                                "active_personality_id":self.config["active_personality_id"]
                                })         
        else:
            pth = str(config_file).replace('\\','/')
            ASCIIColors.error(f"nok : Personality not found @ {pth}")
            return jsonify({"status": False, "error":f"Personality not found @ {pth}"})         

    def p_unmount_personality(self):
        print("- Unmounting personality ...")
        try:
            data = request.get_json()
            # Further processing of the data
        except Exception as e:
            print(f"Error occurred while parsing JSON: {e}")
            return
        category    = data['category']
        name        = data['folder']
        try:
            index = self.config["personalities"].index(f"{category}/{name}")
            self.config["personalities"].remove(f"{category}/{name}")
            if self.config["active_personality_id"]>=index:
                self.config["active_personality_id"]=0
            if len(self.config["personalities"])>0:
                self.mounted_personalities = self.rebuild_personalities()
                self.personality = self.mounted_personalities[self.config["active_personality_id"]]
            else:
                self.personalities = ["generic/lollms"]
                self.mounted_personalities = self.rebuild_personalities()
                self.personality = self.mounted_personalities[self.config["active_personality_id"]]
            ASCIIColors.success("ok")
            if self.config.auto_save:
                ASCIIColors.info("Saving configuration")
                self.config.save_config()
            return jsonify({
                        "status": True,
                        "personalities":self.config["personalities"],
                        "active_personality_id":self.config["active_personality_id"]
                        })         
        except:
            ASCIIColors.error(f"nok : Personality not found @ {category}/{name}")
            return jsonify({"status": False, "error":"Couldn't unmount personality"})         
         
    def get_active_personality_settings(self):
        print("- Retreiving personality settings")
        if self.personality.processor is not None:
            if hasattr(self.personality.processor,"personality_config"):
                return jsonify(self.personality.processor.personality_config.config_template.template)
            else:
                return jsonify({})        
        else:
            return jsonify({})               

    def get_active_binding_settings(self):
        print("- Retreiving binding settings")
        if self.binding is not None:
            if hasattr(self.binding,"binding_config"):
                return jsonify(self.binding.binding_config.config_template.template)
            else:
                return jsonify({})        
        else:
            return jsonify({})  
        

    def set_active_personality_settings(self):
        print("- Setting personality settings")
        try:
            data = request.get_json()
            # Further processing of the data
        except Exception as e:
            print(f"Error occurred while parsing JSON: {e}")
            return
        
        if self.personality.processor is not None:
            if hasattr(self.personality.processor,"personality_config"):
                self.personality.processor.personality_config.update_template(data)
                self.personality.processor.personality_config.config.save_config()
                if self.config.auto_save:
                    ASCIIColors.info("Saving configuration")
                    self.config.save_config()
                return jsonify({'status':True})
            else:
                return jsonify({'status':False})        
        else:
            return jsonify({'status':False})            

    
    def set_active_binding_settings(self):
        print("- Setting binding settings")
        try:
            data = request.get_json()
            # Further processing of the data
        except Exception as e:
            print(f"Error occurred while parsing JSON: {e}")
            return
        
        if self.binding is not None:
            if hasattr(self.binding,"binding_config"):
                for entry in data:
                    if entry["type"]=="list" and type(entry["value"])==str:
                        try:
                            v = json.loads(entry["value"])
                        except:
                            v= ""
                        if type(v)==list:
                            entry["value"] = v
                        else:
                            entry["value"] = [entry["value"]]
                self.binding.binding_config.update_template(data)
                self.binding.binding_config.config.save_config()
                self.binding = None
                self.model = None
                for per in self.mounted_personalities:
                    per.model = None
                gc.collect()
                self.binding= BindingBuilder().build_binding(self.config, self.lollms_paths)
                self.model = self.binding.build_model()
                if self.config.auto_save:
                    ASCIIColors.info("Saving configuration")
                    self.config.save_config()
                return jsonify({'status':True})
            else:
                return jsonify({'status':False})        
        else:
            return jsonify({'status':False})     
    
         
    def get_personality_settings(self):
        print("- Retreiving personality settings")
        try:
            data = request.get_json()
            # Further processing of the data
        except Exception as e:
            print(f"Error occurred while parsing JSON: {e}")
            return
        category = data['category']
        name = data['folder']

        if category.startswith("personal"):
            personality_folder = self.lollms_paths.personal_personalities_path/f"{category}"/f"{name}"
        else:
            personality_folder = self.lollms_paths.personalities_zoo_path/f"{category}"/f"{name}"

        personality = AIPersonality(personality_folder,
                                    self.lollms_paths, 
                                    self.config,
                                    model=self.model,
                                    app=self,
                                    run_scripts=True)
        if personality.processor is not None:
            if hasattr(personality.processor,"personality_config"):
                return jsonify(personality.processor.personality_config.config_template.template)
            else:
                return jsonify({})        
        else:
            return jsonify({})       


    def p_select_personality(self):

        data = request.get_json()
        id = data['id']
        print(f"- Selecting active personality {id} ...",end="")
        if id<len(self.mounted_personalities):
            self.config["active_personality_id"]=id
            self.personality = self.mounted_personalities[self.config["active_personality_id"]]
            ASCIIColors.success("ok")
            print(f"Mounted {self.personality.name}")
            if self.config.auto_save:
                ASCIIColors.info("Saving configuration")
                self.config.save_config()
            return jsonify({
                "status": True,
                "personalities":self.config["personalities"],
                "active_personality_id":self.config["active_personality_id"]                
                })
        else:
            ASCIIColors.error(f"nok : personality id out of bounds @ {id} >= {len(self.mounted_personalities)}")
            return jsonify({"status": False, "error":"Invalid ID"})         
                    

    def add_model_reference(self):
        try:
            ASCIIColors.info("Creating a model reference")
            path = Path(request.path)
            ref_path=self.lollms_paths.personal_models_path/self.config.binding_name/(path.name+".reference")
            with open(ref_path,"w") as f:
                f.write(str(path))

            return jsonify({"status": True})   
        except Exception as ex:
            ASCIIColors.error(ex)
            trace_exception(ex)
            return jsonify({"status": False})   

    def upload_model(self):      
        file = request.files['file']
        file.save(self.lollms_paths.personal_models_path/self.config.binding_name/file.filename)
        return jsonify({"status": True})   

    def upload_avatar(self):      
        file = request.files['avatar']
        file.save(self.lollms_paths.personal_user_infos_path/file.filename)
        return jsonify({"status": True,"fileName":file.filename})   
        
        
        
    def rename(self):
        data = request.get_json()
        client_id = data["client_id"]
        title = data["title"]
        self.connections[client_id]["current_discussion"].rename(title)
        return "renamed successfully"
    
    def edit_title(self):
        data                = request.get_json()
        client_id           = data["client_id"]
        title               = data["title"]
        discussion_id       = data["id"]
        self.connections[client_id]["current_discussion"] = Discussion(discussion_id, self.db)
        self.connections[client_id]["current_discussion"].rename(title)
        return jsonify({'status':True})
    
    def delete_discussion(self):
        data            = request.get_json()
        client_id       = data["client_id"]
        discussion_id   = data["id"]
        self.connections[client_id]["current_discussion"] = Discussion(discussion_id, self.db)
        self.connections[client_id]["current_discussion"].delete_discussion()
        self.connections[client_id]["current_discussion"] = None
        return jsonify({'status':True})

    def edit_message(self):
        client_id       = request.args.get("client_id")
        message_id      = request.args.get("id")
        new_message     = request.args.get("message")
        try:
            self.connections[client_id]["current_discussion"].edit_message(message_id, new_message)
            return jsonify({"status": True})
        except Exception as ex:
            trace_exception(ex)
            return jsonify({"status": False, "error":str(ex)})


    def message_rank_up(self):
        client_id       = request.args.get("client_id")
        discussion_id   = request.args.get("id")
        try:
            new_rank = self.connections[client_id]["current_discussion"].message_rank_up(discussion_id)
            return jsonify({"status": True, "new_rank": new_rank})
        except Exception as ex:
            return jsonify({"status": False, "error":str(ex)})

    def message_rank_down(self):
        client_id = request.args.get("client_id")
        discussion_id = request.args.get("id")
        try:
            new_rank = self.connections[client_id]["current_discussion"].message_rank_down(discussion_id)
            return jsonify({"status": True, "new_rank": new_rank})
        except Exception as ex:
            return jsonify({"status": False, "error":str(ex)})

    def delete_message(self):
        client_id = request.args.get("client_id")
        discussion_id = request.args.get("id")
        if self.connections[client_id]["current_discussion"] is None:
            return jsonify({"status": False,"message":"No discussion is selected"})
        else:
            new_rank = self.connections[client_id]["current_discussion"].delete_message(discussion_id)
            ASCIIColors.yellow("Message deleted")
            return jsonify({"status":True,"new_rank": new_rank})

   
    def get_available_models(self):
        """Get the available models

        Returns:
            _type_: _description_
        """
        if self.binding is None:
            return jsonify([])
        model_list = self.binding.get_available_models()
        return jsonify(model_list)


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
        if self.personality is None:
            return jsonify({
                "personality_category":"", 
                "personality_name":""
            })
        else:
            return jsonify({
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
    lollms_paths = LollmsPaths.find_paths(force_local=True, custom_default_cfg_path="configs/config.yaml")
    db_folder = lollms_paths.personal_path/"databases"
    db_folder.mkdir(parents=True, exist_ok=True)
    
    # Parsong parameters
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

    # Configuration loading part
    config = LOLLMSConfig.autoload(lollms_paths)
    
    # Override values in config with command-line arguments
    for arg_name, arg_value in vars(args).items():
        if arg_value is not None:
            config[arg_name] = arg_value

    # Copy user
    # Assuming the current file's directory contains the 'assets' subfolder
    current_file_dir = Path(__file__).parent
    assets_dir = current_file_dir / "assets"
    default_user_avatar = assets_dir / "default_user.svg"    
    user_avatar_path = lollms_paths.personal_user_infos_path / "default_user.svg"
    if not user_avatar_path.exists():
        # If the user avatar doesn't exist, copy the default avatar from the assets folder
        shutil.copy(default_user_avatar, user_avatar_path)
    # executor = ThreadPoolExecutor(max_workers=1)
    # app.config['executor'] = executor
    # Check if .no_gpu file exists
    no_gpu_file = Path('.no_gpu')
    if no_gpu_file.exists():
        # If the file exists, change self.config.use_gpu to False
        config.enable_gpu = False
        config.save_config()
        
        # Remove the .no_gpu file
        no_gpu_file.unlink()
    
    bot = LoLLMsWebUI(args, app, socketio, config, config.file_path, lollms_paths)

    # chong Define custom WebSocketHandler with error handling 
    class CustomWebSocketHandler(WebSocketHandler):
        def handle_error(self, environ, start_response, e):
            # Handle the error here
            print("WebSocket error:", e)
            super().handle_error(environ, start_response, e)
    


    # chong -add socket server    
    app.config['debug'] = config["debug"]

    if config["debug"]:
        ASCIIColors.info("debug mode:true")    
    else:
        ASCIIColors.info("debug mode:false")
       
    
    url = f'http://{config["host"]}:{config["port"]}'
    if config["host"]!="localhost":
        print(f'Please open your browser and go to http://localhost:{config["port"]} to view the ui')
        ASCIIColors.success(f'This server is visible from a remote PC. use this address http://{get_ip_address()}:{config["port"]}')
    else:
        print(f"Please open your browser and go to {url} to view the ui")
    
    # if autoshow
    if config.auto_show_browser:
        webbrowser.open(f"http://{config['host']}:{config['port']}")
    socketio.run(app, host=config["host"], port=config["port"],
                 # prevent error: The Werkzeug web server is not designed to run in production
                 allow_unsafe_werkzeug=True)
    # http_server = WSGIServer((config["host"], config["port"]), app, handler_class=WebSocketHandler)
    # http_server.serve_forever()
