######
# Project       : lollms-webui
# Author        : ParisNeo with the help of the community
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

__version__ ="8.5"

main_repo = "https://github.com/ParisNeo/lollms-webui.git"



import os
import platform
import sys
from flask import request, jsonify, url_for
import io
import sys
import time
import traceback
import webbrowser
from pathlib import Path
from lollms.config import InstallOption
from lollms.main_config import LOLLMSConfig
from lollms.paths import LollmsPaths, gptqlora_repo
from lollms.com import NotificationType, NotificationDisplayType
from lollms.utilities import PackageManager, AdvancedGarbageCollector, reinstall_pytorch_with_cuda, convert_language_name, find_first_available_file_index, add_period
lollms_paths = LollmsPaths.find_paths(force_local=True, custom_default_cfg_path="configs/config.yaml")
# Configuration loading part
config = LOLLMSConfig.autoload(lollms_paths)

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
    from lollms.binding import BindingBuilder
    from lollms.personality import AIPersonality
    from lollms.config import BaseConfig
    from lollms.extension import LOLLMSExtension, ExtensionBuilder

    from flask_cors import CORS
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
    from api import LoLLMsAPI
    import shutil
    import socket
    from api.db import DiscussionsDB, Discussion
    from safe_store import TextVectorizer, VectorizationMethod, VisualizationMethod
    from tqdm import tqdm

    try:
        import mimetypes
        mimetypes.add_type('application/javascript', '.js')
        mimetypes.add_type('text/css', '.css')    
    except:
        ASCIIColors.yellow("Couldn't set mimetype")  

    def check_module_update_(repo_path, branch_name="main"):
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

    def check_update_(branch_name="main"):
        try:
            # Open the repository
            repo_path = str(Path(__file__).parent)
            if check_module_update_(repo_path, branch_name):
                return True
            repo_path = str(Path(__file__).parent/"lollms_core")
            if check_module_update_(repo_path, branch_name):
                return True
            repo_path = str(Path(__file__).parent/"utilities/safe_store")
            if check_module_update_(repo_path, branch_name):
                return True
            return False
        except Exception as e:
            # Handle any errors that may occur during the fetch process
            # trace_exception(e)
            return False

    

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    app = Flask("Lollms-WebUI", static_url_path="/static", static_folder="static")
    CORS(app)
    from flask_compress import Compress
    #  async_mode='gevent', ping_timeout=1200, ping_interval=120, 
    socketio = SocketIO(app,  cors_allowed_origins="*", async_mode='gevent', ping_timeout=1200, ping_interval=120, path='/socket.io')
    #socketio = SocketIO(app,  cors_allowed_origins="*", async_mode='threading',engineio_options={'websocket_compression': True, 'websocket_ping_interval': 20, 'websocket_ping_timeout': 120, 'websocket_max_queue': 100})
    compress = Compress(app)
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




    class LoLLMsWebUI(LoLLMsAPI):
        def __init__(self, args, _app, _socketio, config:LOLLMSConfig, config_file_path:Path|str, lollms_paths:LollmsPaths) -> None:
            self.args = args
            if config.auto_update:
                if check_update_():
                    ASCIIColors.info("New version found. Updating!")
                    run_update_script()

            if len(config.personalities)==0:
                config.personalities.append("generic/lollms")
                config["active_personality_id"] = 0
                config.save_config()

            if config["active_personality_id"]>=len(config["personalities"]) or config["active_personality_id"]<0:
                config["active_personality_id"] = 0
            super().__init__(config, _socketio, config_file_path, lollms_paths)


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
            
            self.add_endpoint("/get_current_personality_files_list", "get_current_personality_files_list", self.get_current_personality_files_list, methods=["GET"])
            self.add_endpoint("/clear_personality_files_list", "clear_personality_files_list", self.clear_personality_files_list, methods=["GET"])
            
            self.add_endpoint("/start_training", "start_training", self.start_training, methods=["POST"])
            self.add_endpoint("/get_lollms_version", "get_lollms_version", self.get_lollms_version, methods=["GET"])
            self.add_endpoint("/get_lollms_webui_version", "get_lollms_webui_version", self.get_lollms_webui_version, methods=["GET"])
            
            self.add_endpoint("/reload_binding", "reload_binding", self.reload_binding, methods=["POST"])


            self.add_endpoint("/restart_program", "restart_program", self.restart_program, methods=["GET"])
            self.add_endpoint("/update_software", "update_software", self.update_software, methods=["GET"])
            self.add_endpoint("/clear_uploads", "clear_uploads", self.clear_uploads, methods=["GET"])

            self.add_endpoint("/check_update", "check_update", self.check_update, methods=["GET"])
            
            self.add_endpoint("/disk_usage", "disk_usage", self.disk_usage, methods=["GET"])
            self.add_endpoint("/ram_usage", "ram_usage", self.ram_usage, methods=["GET"])
            self.add_endpoint("/vram_usage", "vram_usage", self.vram_usage, methods=["GET"])
        
            
            self.add_endpoint("/list_bindings", "list_bindings", self.list_bindings, methods=["GET"])
            self.add_endpoint("/install_binding", "install_binding", self.install_binding, methods=["POST"])
            self.add_endpoint("/unInstall_binding", "unInstall_binding", self.unInstall_binding, methods=["POST"])
            self.add_endpoint("/reinstall_binding", "reinstall_binding", self.reinstall_binding, methods=["POST"])
            self.add_endpoint("/get_active_binding_settings", "get_active_binding_settings", self.get_active_binding_settings, methods=["GET"])
            self.add_endpoint("/set_active_binding_settings", "set_active_binding_settings", self.set_active_binding_settings, methods=["POST"])


            self.add_endpoint("/list_models", "list_models", self.list_models, methods=["GET"])
            self.add_endpoint("/get_active_model", "get_active_model", self.get_active_model, methods=["GET"])
            self.add_endpoint("/add_reference_to_local_model", "add_reference_to_local_model", self.add_reference_to_local_model, methods=["POST"])
            self.add_endpoint("/get_model_status", "get_model_status", self.get_model_status, methods=["GET"])
            self.add_endpoint("/get_available_models", "get_available_models", self.get_available_models, methods=["GET"])

            self.add_endpoint("/post_to_personality", "post_to_personality", self.post_to_personality, methods=["POST"])
            self.add_endpoint("/reinstall_personality", "reinstall_personality", self.reinstall_personality, methods=["POST"])


            self.add_endpoint("/list_mounted_personalities", "list_mounted_personalities", self.list_mounted_personalities, methods=["POST"])
            self.add_endpoint("/list_personalities_categories", "list_personalities_categories", self.list_personalities_categories, methods=["GET"])
            self.add_endpoint("/list_personalities", "list_personalities", self.list_personalities, methods=["GET"])

            self.add_endpoint("/mount_personality", "mount_personality", self.p_mount_personality, methods=["POST"])
            self.add_endpoint("/remount_personality", "remount_personality", self.p_remount_personality, methods=["POST"])
            self.add_endpoint("/unmount_personality", "unmount_personality", self.p_unmount_personality, methods=["POST"])        
            self.add_endpoint("/unmount_all_personalities", "unmount_all_personalities", self.unmount_all_personalities, methods=["GET"])        
            self.add_endpoint("/select_personality", "select_personality", self.p_select_personality, methods=["POST"])
            self.add_endpoint("/get_personality_settings", "get_personality_settings", self.get_personality_settings, methods=["POST"])
            self.add_endpoint("/get_active_personality_settings", "get_active_personality_settings", self.get_active_personality_settings, methods=["GET"])
            self.add_endpoint("/set_active_personality_settings", "set_active_personality_settings", self.set_active_personality_settings, methods=["POST"])
            self.add_endpoint("/get_current_personality_path_infos", "get_current_personality_path_infos", self.get_current_personality_path_infos, methods=["GET"])
            self.add_endpoint("/get_personality", "get_personality", self.get_personality, methods=["GET"])
            self.add_endpoint("/get_current_personality", "get_current_personality", self.get_current_personality, methods=["GET"])
            self.add_endpoint("/get_all_personalities", "get_all_personalities", self.get_all_personalities, methods=["GET"])


            self.add_endpoint("/uploads/<path:filename>", "serve_uploads", self.serve_uploads, methods=["GET"])
            self.add_endpoint("/<path:filename>", "serve_static", self.serve_static, methods=["GET"])
            self.add_endpoint("/user_infos/<path:filename>", "serve_user_infos", self.serve_user_infos, methods=["GET"])

            self.add_endpoint("/bindings/<path:filename>", "serve_bindings", self.serve_bindings, methods=["GET"])
            self.add_endpoint("/personalities/<path:filename>", "serve_personalities", self.serve_personalities, methods=["GET"])
            self.add_endpoint("/extensions/<path:filename>", "serve_extensions", self.serve_extensions, methods=["GET"])
            self.add_endpoint("/outputs/<path:filename>", "serve_outputs", self.serve_outputs, methods=["GET"])
            self.add_endpoint("/data/<path:filename>", "serve_data", self.serve_data, methods=["GET"])
            self.add_endpoint("/help/<path:filename>", "serve_help", self.serve_help, methods=["GET"])

            self.add_endpoint("/audio/<path:filename>", "serve_audio", self.serve_audio, methods=["GET"])
            self.add_endpoint("/images/<path:filename>", "serve_images", self.serve_images, methods=["GET"])
            


            self.add_endpoint("/install_extension", "install_extension", self.install_extension, methods=["POST"])
            self.add_endpoint("/reinstall_extension", "reinstall_extension", self.reinstall_extension, methods=["POST"])
            self.add_endpoint("/mount_extension", "mount_extension", self.p_mount_extension, methods=["POST"])
            self.add_endpoint("/remount_extension", "remount_extension", self.p_remount_extension, methods=["POST"])
            self.add_endpoint("/unmount_extension", "unmount_extension", self.p_unmount_extension, methods=["POST"])
            self.add_endpoint("/list_extensions_categories", "list_extensions_categories", self.list_extensions_categories, methods=["GET"])
            self.add_endpoint("/list_extensions", "list_extensions", self.list_extensions, methods=["GET"])
            self.add_endpoint("/get_all_extensions", "get_all_extensions", self.get_all_extensions, methods=["GET"])


            self.add_endpoint("/list_discussions", "list_discussions", self.list_discussions, methods=["GET"])
            self.add_endpoint("/export_discussion", "export_discussion", self.export_discussion, methods=["GET"])
            self.add_endpoint("/list_databases", "list_databases", self.list_databases, methods=["GET"])
            self.add_endpoint("/select_database", "select_database", self.select_database, methods=["POST"])
            self.add_endpoint("/rename_discussion", "rename_discussion", self.rename_discussion, methods=["POST"])
            self.add_endpoint("/delete_discussion","delete_discussion",self.delete_discussion,methods=["POST"])
            self.add_endpoint("/edit_title", "edit_title", self.edit_title, methods=["POST"])
            self.add_endpoint("/make_title", "make_title", self.make_title, methods=["POST"])
            self.add_endpoint("/export", "export", self.export, methods=["GET"])

            self.add_endpoint("/export_multiple_discussions", "export_multiple_discussions", self.export_multiple_discussions, methods=["POST"])      
            self.add_endpoint("/import_multiple_discussions", "import_multiple_discussions", self.import_multiple_discussions, methods=["POST"])      


            self.add_endpoint("/get_generation_status", "get_generation_status", self.get_generation_status, methods=["GET"])
            self.add_endpoint("/stop_gen", "stop_gen", self.stop_gen, methods=["GET"])


            self.add_endpoint("/", "", self.index, methods=["GET"])
            self.add_endpoint("/settings/", "", self.index, methods=["GET"])
            self.add_endpoint("/playground/", "", self.index, methods=["GET"])
            self.add_endpoint("/extensions", "extensions", self.extensions, methods=["GET"])
            self.add_endpoint("/training", "training", self.training, methods=["GET"])
            self.add_endpoint("/main", "main", self.main, methods=["GET"])
            self.add_endpoint("/settings", "settings", self.settings, methods=["GET"])
            self.add_endpoint("/help", "help", self.help, methods=["GET"])            

            self.add_endpoint("/switch_personal_path", "switch_personal_path", self.switch_personal_path, methods=["POST"])
            self.add_endpoint("/upload_avatar", "upload_avatar", self.upload_avatar, methods=["POST"])


            self.add_endpoint("/edit_message", "edit_message", self.edit_message, methods=["GET"])
            self.add_endpoint("/message_rank_up", "message_rank_up", self.message_rank_up, methods=["GET"])
            self.add_endpoint("/message_rank_down", "message_rank_down", self.message_rank_down, methods=["GET"])
            self.add_endpoint("/delete_message", "delete_message", self.delete_message, methods=["GET"])


            self.add_endpoint("/get_config", "get_config", self.get_config, methods=["GET"])
            self.add_endpoint("/update_setting", "update_setting", self.update_setting, methods=["POST"])
            self.add_endpoint("/apply_settings", "apply_settings", self.apply_settings, methods=["POST"])

            self.add_endpoint("/save_settings", "save_settings", self.save_settings, methods=["POST"])        



            self.add_endpoint("/open_code_folder", "open_code_folder", self.open_code_folder, methods=["POST"])
            self.add_endpoint("/open_code_folder_in_vs_code", "open_code_folder_in_vs_code", self.open_code_folder_in_vs_code, methods=["POST"])
            self.add_endpoint("/open_code_in_vs_code", "open_code_in_vs_code", self.open_code_in_vs_code, methods=["POST"])
            self.add_endpoint("/open_file", "open_file", self.open_file, methods=["GET"])


            self.add_endpoint("/reset", "reset", self.reset, methods=["GET"])
            self.add_endpoint("/get_server_address", "get_server_address", self.get_server_address, methods=["GET"])



            self.add_endpoint("/list_voices", "list_voices", self.list_voices, methods=["GET"])
            self.add_endpoint("/set_voice", "set_voice", self.set_voice, methods=["POST"])
            self.add_endpoint("/text2Audio", "text2Audio", self.text2Audio, methods=["POST"])
            self.add_endpoint("/install_xtts", "install_xtts", self.install_xtts, methods=["GET"])

            # ----



            
            


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
                "/execute_code", "execute_code", self.execute_code, methods=["POST"]
            )

            self.add_endpoint(
                "/install_sd", "install_sd", self.install_sd, methods=["GET"]
            )
            

            self.add_endpoint("/update_binding_settings", "update_binding_settings", self.update_binding_settings, methods=["GET"])
            
            
        def update_binding_settings(self):
            if self.binding:
                self.binding.settings_updated()
                ASCIIColors.green("Binding setting updated successfully")
                return jsonify({"status":True})
            else:
                return jsonify({"status":False, 'error':"no binding found"})        
            
        def reload_binding(self, data):
            print(f"Roloading binding selected : {data['binding_name']}")
            self.config["binding_name"]=data['binding_name']
            try:
                if self.binding:
                    self.binding.destroy_model()
                self.binding = None
                self.model = None
                for per in self.mounted_personalities:
                    if per is not None:
                        per.model = None
                gc.collect()
                self.binding = BindingBuilder().build_binding(self.config, self.lollms_paths, InstallOption.INSTALL_IF_NECESSARY, lollmsCom=self)
                self.model = None
                self.config.save_config()
                ASCIIColors.green("Binding loaded successfully")
            except Exception as ex:
                ASCIIColors.error(f"Couldn't build binding: [{ex}]")
                trace_exception(ex)
                return jsonify({"status":False, 'error':str(ex)})
            
        def get_model_status(self):
            return jsonify({"status":self.model is not None})

        def get_server_address(self):
            server_address = request.host_url
            return server_address
        
        
        def install_xtts(self):
            try:
                self.ShowBlockingMessage("Installing xTTS api server\nPlease stand by")
                PackageManager.install_package("xtts-api-server")
                self.HideBlockingMessage()
                return jsonify({"status":True})
            except Exception as ex:
                self.HideBlockingMessage()
                return jsonify({"status":False, 'error':str(ex)})
            
        def install_sd(self):
            try:
                self.ShowBlockingMessage("Installing SD api server\nPlease stand by")
                from lollms.image_gen_modules.lollms_sd import install_sd
                install_sd()
                self.HideBlockingMessage()
                return jsonify({"status":True})
            except Exception as ex:
                self.HideBlockingMessage()
                return jsonify({"status":False, 'error':str(ex)})
            
        def execute_python(self, code, discussion_id, message_id):
            def spawn_process(code):
                """Executes Python code and returns the output as JSON."""

                # Start the timer.
                start_time = time.time()

                # Create a temporary file.
                root_folder = self.lollms_paths.personal_outputs_path/"discussions"/f"d_{discussion_id}"
                root_folder.mkdir(parents=True,exist_ok=True)
                tmp_file = root_folder/f"ai_code_{message_id}.py"
                with open(tmp_file,"w",encoding="utf8") as f:
                    f.write(code)

                try:
                    # Execute the Python code in a temporary file.
                    process = subprocess.Popen(
                        ["python", str(tmp_file)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=root_folder
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

        def execute_latex(self, code, discussion_id, message_id):
            def spawn_process(code):
                """Executes Python code and returns the output as JSON."""

                # Start the timer.
                start_time = time.time()

                # Create a temporary file.
                root_folder = self.lollms_paths.personal_outputs_path/"discussions"/f"d_{discussion_id}"
                root_folder.mkdir(parents=True,exist_ok=True)
                tmp_file = root_folder/f"latex_file_{message_id}.tex"
                with open(tmp_file,"w",encoding="utf8") as f:
                    f.write(code)
                try:
                    # Determine the pdflatex command based on the provided or default path
                    if self.config.pdf_latex_path:
                        pdflatex_command = self.config.pdf_latex_path
                    else:
                        pdflatex_command = 'pdflatex'
                    # Set the execution path to the folder containing the tmp_file
                    execution_path = tmp_file.parent
                    # Run the pdflatex command with the file path
                    result = subprocess.run([pdflatex_command, "-interaction=nonstopmode", tmp_file], check=True, capture_output=True, text=True, cwd=execution_path)
                    # Check the return code of the pdflatex command
                    if result.returncode != 0:
                        error_message = result.stderr.strip()
                        execution_time = time.time() - start_time
                        error_json = {"output": f"Error occurred while compiling LaTeX: {error_message}", "execution_time": execution_time}
                        return json.dumps(error_json)
                    # If the compilation is successful, you will get a PDF file
                    pdf_file = tmp_file.with_suffix('.pdf')
                    print(f"PDF file generated: {pdf_file}")

                except subprocess.CalledProcessError as ex:
                    self.error(f"Error occurred while compiling LaTeX: {ex}") 
                    error_json = {"output": "<div class='text-red-500'>"+str(ex)+"\n"+get_trace_exception(ex)+"</div>", "execution_time": execution_time}
                    return json.dumps(error_json)

                # Stop the timer.
                execution_time = time.time() - start_time

                # The child process was successful.
                pdf_file=str(pdf_file)
                url = f"{url_for('main')[:-4]}{pdf_file[pdf_file.index('outputs'):]}"
                output_json = {"output": f"Pdf file generated at: {pdf_file}\n<a href='{url}'>Click here to show</a>", "execution_time": execution_time}
                return json.dumps(output_json)
            return spawn_process(code)

        def execute_bash(self, code, discussion_id, message_id):
            def spawn_process(code):
                """Executes Python code and returns the output as JSON."""

                # Start the timer.
                start_time = time.time()

                # Create a temporary file.
                root_folder = self.lollms_paths.personal_outputs_path/"discussions"/f"d_{discussion_id}"
                root_folder.mkdir(parents=True,exist_ok=True)
                try:
                    # Execute the Python code in a temporary file.
                    process = subprocess.Popen(    
                        code,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )

                    # Get the output and error from the process.
                    output, error = process.communicate()
                except Exception as ex:
                    # Stop the timer.
                    execution_time = time.time() - start_time
                    error_message = f"Error executing shell cmmands: {ex}"
                    error_json = {"output": "<div class='text-red-500'>"+str(ex)+"\n"+get_trace_exception(ex)+"</div>", "execution_time": execution_time}
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

        def execute_code(self):
            """Executes Python code and returns the output."""
            
            data = request.get_json()
            code = data["code"]
            discussion_id = data.get("discussion_id","unknown_discussion")
            message_id = data.get("message_id","unknown_message")
            language = data.get("language","python")
            

            ASCIIColors.info("Executing code:")
            ASCIIColors.yellow(code)

            if language=="python":
                return self.execute_python(code, discussion_id, message_id)
            elif language=="latex":
                return self.execute_latex(code, discussion_id, message_id)
            elif language in ["bash","shell","cmd","powershell","sh"]:
                return self.execute_bash(code, discussion_id, message_id)
            return {"output": "Unsupported language", "execution_time": 0}
        

        def open_code_folder_in_vs_code(self):
            """Opens code folder in vs code."""
            
            data = request.get_json()
            code = data["code"]
            discussion_id = data.get("discussion_id","unknown_discussion")
            message_id = data.get("message_id","unknown_message")
            language = data.get("language","python")

            ASCIIColors.info("Opening folder:")
            # Create a temporary file.
            root_folder = self.lollms_paths.personal_outputs_path/"discussions"/f"d_{discussion_id}"
            root_folder.mkdir(parents=True,exist_ok=True)
            tmp_file = root_folder/f"ai_code_{message_id}.py"
            with open(tmp_file,"w") as f:
                f.write(code)
            
            os.system('code ' + str(root_folder))
            return {"output": "OK", "execution_time": 0}
        
        def open_file(self):
            """Opens code in vs code."""
            path = request.args.get('path')
            os.system("start "+path)
            return {"output": "OK", "execution_time": 0}
                    
        def open_code_in_vs_code(self):
            """Opens code in vs code."""
            
            data = request.get_json()
            discussion_id = data.get("discussion_id","unknown_discussion")
            message_id = data.get("message_id","")
            code = data["code"]
            discussion_id = data.get("discussion_id","unknown_discussion")
            message_id = data.get("message_id","unknown_message")
            language = data.get("language","python")

            ASCIIColors.info("Opening folder:")
            # Create a temporary file.
            root_folder = self.lollms_paths.personal_outputs_path/"discussions"/f"d_{discussion_id}"/f"{message_id}.py"
            root_folder.mkdir(parents=True,exist_ok=True)
            tmp_file = root_folder/f"ai_code_{message_id}.py"
            with open(tmp_file,"w") as f:
                f.write(code)
            os.system('code ' + str(root_folder))
            return {"output": "OK", "execution_time": 0}

        def open_code_folder(self):
            """Opens code folder."""
            
            data = request.get_json()
            discussion_id = data.get("discussion_id","unknown_discussion")

            ASCIIColors.info("Opening folder:")
            # Create a temporary file.
            root_folder = self.lollms_paths.personal_outputs_path/"discussions"/f"d_{discussion_id}"
            root_folder.mkdir(parents=True,exist_ok=True)
            if platform.system() == 'Windows':
                os.startfile(str(root_folder))
            elif platform.system() == 'Linux':
                os.system('xdg-open ' + str(root_folder))
            elif platform.system() == 'Darwin':
                os.system('open ' + str(root_folder))
            return {"output": "OK", "execution_time": 0}

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


        def list_voices(self):
            ASCIIColors.yellow("Listing voices")
            voices=["main_voice"]
            voices_dir:Path=lollms_paths.custom_voices_path
            voices += [v.stem for v in voices_dir.iterdir() if v.suffix==".wav"]
            return jsonify({"voices":voices})

        def set_voice(self):
            data = request.get_json()
            self.config.current_voice=data["voice"]
            if self.config.auto_save:
                self.config.save_config()
            return jsonify({"status":True})


        def text2Audio(self):
            # Get the JSON data from the POST request.
            try:
                from lollms.audio_gen_modules.lollms_xtts import LollmsXTTS
                if self.tts is None:
                    self.tts = LollmsXTTS(self, voice_samples_path=Path(__file__).parent/"voices")
            except:
                return jsonify({"url": None})
                
            data = request.get_json()
            voice=data.get("voice",self.config.current_voice)
            index = find_first_available_file_index(self.tts.output_folder, "voice_sample_",".wav")
            output_fn=data.get("fn",f"voice_sample_{index}.wav")
            if voice is None:
                voice = "main_voice"
            self.info("Starting to build voice")
            try:
                from lollms.audio_gen_modules.lollms_xtts import LollmsXTTS
                if self.tts is None:
                    self.tts = LollmsXTTS(self, voice_samples_path=Path(__file__).parent/"voices")
                language = self.config.current_language# convert_language_name()
                if voice!="main_voice":
                    voices_folder = self.lollms_paths.custom_voices_path
                else:
                    voices_folder = Path(__file__).parent/"voices"
                self.tts.set_speaker_folder(voices_folder)
                url = f"audio/{output_fn}"
                preprocessed_text= add_period(data['text'])

                self.tts.tts_to_file(preprocessed_text, f"{voice}.wav", f"{output_fn}", language=language)
                self.info("Voice file ready")
                return jsonify({"url": url})
            except:
                return jsonify({"url": None})

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
            export_format = data["export_format"]

            if export_format=="json":
                discussions = self.db.export_discussions_to_json(discussion_ids)
            elif export_format=="markdown":
                discussions = self.db.export_discussions_to_markdown(discussion_ids)
            else:
                discussions = self.db.export_discussions_to_markdown(discussion_ids)
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
            ASCIIColors.yellow("Listing all personalities")
            personalities_folder = self.lollms_paths.personalities_zoo_path
            personalities = {}

            for category_folder in  [self.lollms_paths.custom_personalities_path] + list(personalities_folder.iterdir()):
                cat = category_folder.stem
                if category_folder.is_dir() and not category_folder.stem.startswith('.'):
                    personalities[cat if category_folder!=self.lollms_paths.custom_personalities_path else "custom_personalities"] = []
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
                                    personality_info['disclaimer'] = config_data.get('disclaimer',"")
                                    
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
                                    personality_info['languages']= [""]+[f.stem for f in languages_path.iterdir() if f.suffix==".yaml"]
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
                                
                                personalities[cat if category_folder!=self.lollms_paths.custom_personalities_path else "custom_personalities"].append(personality_info)
                            except Exception as ex:
                                ASCIIColors.warning(f"Couldn't load personality from {personality_folder} [{ex}]")
                                trace_exception(ex)
            ASCIIColors.green("OK")

            return json.dumps(personalities)
        
        def get_personality(self):
            category = request.args.get('category')
            name = request.args.get('name')
            if category == "custom_personalities":
                personality_folder = self.lollms_paths.custom_personalities_path/f"{name}"
            else:
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
                    
                    if self.personality_category!="custom_personalities":
                        personality_fn = self.lollms_paths.personalities_zoo_path/self.config["personalities"][self.config["active_personality_id"]]
                    else:
                        personality_fn = self.lollms_paths.personal_personalities_path/self.config["personalities"][self.config["active_personality_id"]].split("/")[-1]
                    self.personality.load_personality(personality_fn)
                else:
                    self.config["personalities"].append(f"{self.personality_category}/{self.personality_name}")
            elif setting_name== "override_personality_model_parameters":
                self.config["override_personality_model_parameters"]=bool(data['setting_value'])

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
                            if per is not None:
                                per.model = None
                        gc.collect()
                        self.binding = BindingBuilder().build_binding(self.config, self.lollms_paths, InstallOption.INSTALL_IF_NECESSARY, lollmsCom=self)
                        self.model = None
                        self.config.save_config()
                        ASCIIColors.green("Binding loaded successfully")
                    except Exception as ex:
                        ASCIIColors.error(f"Couldn't build binding: [{ex}]")
                        trace_exception(ex)
                        return jsonify({"status":False, 'error':str(ex)})
                else:
                    if self.config["debug"]:
                        print(f"Configuration {data['setting_name']} set to {data['setting_value']}")
                    return jsonify({'setting_name': data['setting_name'], "status":True})


            elif setting_name == "model_name":
                ASCIIColors.yellow(f"Changing model to: {data['setting_value']}")
                self.config["model_name"]=data['setting_value']
                self.config.save_config()
                try:
                    self.model = None
                    for per in self.mounted_personalities:
                        if per is not None:
                            per.model = None
                    self.model = self.binding.build_model()
                    if self.model is not None:
                        ASCIIColors.yellow("New model OK")
                    for per in self.mounted_personalities:
                        if per is not None:
                            per.model = self.model
                except Exception as ex:
                    trace_exception(ex)
                    self.InfoMessage(f"It looks like you we couldn't load the model.\nHere is the error message:\n{ex}")


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
                trace_exception(ex)
                return jsonify({"status":False,"error":str(ex)})

        
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
                if f.stem!="binding_template":
                    card = f/"binding_card.yaml"
                    if card.exists():
                        try:
                            bnd = load_config(card)
                            bnd["folder"]=f.stem
                            installed = (self.lollms_paths.personal_configuration_path/"bindings"/f.stem/f"config.yaml").exists()
                            bnd["installed"]=installed
                            ui_file_path = f/"ui.html"
                            if ui_file_path.exists():
                                with ui_file_path.open("r") as file:
                                    text_content = file.read()
                                    bnd["ui"]=text_content
                            else:
                                bnd["ui"]=None
                            disclaimer_file_path = f/"disclaimer.md"
                            if disclaimer_file_path.exists():
                                with disclaimer_file_path.open("r") as file:
                                    text_content = file.read()
                                    bnd["disclaimer"]=text_content
                            else:
                                bnd["disclaimer"]=None
                            icon_file = self.find_extension(self.lollms_paths.bindings_zoo_path/f"{f.name}", "logo", [".svg",".gif",".png"])
                            if icon_file is not None:
                                icon_path = Path(f"bindings/{f.name}/logo{icon_file.suffix}")
                                bnd["icon"]=str(icon_path)

                            bindings.append(bnd)
                        except Exception as ex:
                            print(f"Couldn't load backend card : {f}\n\t{ex}")
            return jsonify(bindings)



        def list_extensions(self):
            return self.config.extensions

        def get_all_extensions(self):
            ASCIIColors.yellow("Gatting all extensions")
            extensions_folder = self.lollms_paths.extensions_zoo_path
            extensions = {}

            for category_folder in  extensions_folder.iterdir():
                cat = category_folder.stem
                if category_folder.is_dir() and not category_folder.stem.startswith('.'):
                    extensions[category_folder.name] = []
                    for extensions_folder in category_folder.iterdir():
                        ext = extensions_folder.stem
                        if extensions_folder.is_dir() and not extensions_folder.stem.startswith('.'):
                            extension_info = {"folder":extensions_folder.stem}
                            config_path = extensions_folder / 'config.yaml'
                            if not config_path.exists():
                                continue                                    
                            try:
                                with open(config_path) as config_file:
                                    config_data = yaml.load(config_file, Loader=yaml.FullLoader)
                                    extension_info['name'] = config_data.get('name',"No Name")
                                    extension_info['author'] = config_data.get('author', 'ParisNeo')
                                    extension_info['based_on'] = config_data.get('based_on',"")
                                    extension_info['description'] = config_data.get('description',"")
                                    extension_info['version'] = config_data.get('version', '1.0.0')
                                    extension_info['installed'] = (self.lollms_paths.personal_configuration_path/f"personality_{extensions_folder.stem}.yaml").exists()
                                    extension_info['help'] = config_data.get('help', '')

                                real_assets_path = extensions_folder/ 'assets'
                                assets_path = Path("extensions") / cat / ext / 'assets'
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
                                    
                                extension_info['has_logo'] = png_logo_path.is_file() or gif_logo_path.is_file()
                                
                                if gif_logo_path_.exists():
                                    extension_info['avatar'] = str(gif_logo_path).replace("\\","/")
                                elif webp_logo_path_.exists():
                                    extension_info['avatar'] = str(webp_logo_path).replace("\\","/")
                                elif png_logo_path_.exists():
                                    extension_info['avatar'] = str(png_logo_path).replace("\\","/")
                                elif jpg_logo_path_.exists():
                                    extension_info['avatar'] = str(jpg_logo_path).replace("\\","/")
                                elif jpeg_logo_path_.exists():
                                    extension_info['avatar'] = str(jpeg_logo_path).replace("\\","/")
                                elif svg_logo_path_.exists():
                                    extension_info['avatar'] = str(svg_logo_path).replace("\\","/")
                                elif bmp_logo_path_.exists():
                                    extension_info['avatar'] = str(bmp_logo_path).replace("\\","/")
                                else:
                                    extension_info['avatar'] = ""
                                
                                extensions[category_folder.name].append(extension_info)
                            except Exception as ex:
                                ASCIIColors.warning(f"Couldn't load personality from {extensions_folder} [{ex}]")
                                trace_exception(ex)
            return extensions        

        def list_models(self):
            if self.binding is not None:
                ASCIIColors.yellow("Listing models")
                models = self.binding.list_models()
                ASCIIColors.green("ok")
                return jsonify(models)
            else:
                return jsonify([])
        
        def get_active_model(self):
            if self.binding is not None:
                try:
                    ASCIIColors.yellow("Getting active model")
                    models = self.binding.list_models()
                    index = models.index(self.config.model_name)
                    ASCIIColors.green("ok")
                    return jsonify({"status":True,"model":models[index],"index":index})
                except Exception as ex:
                    return jsonify({"status":False})
            else:
                return jsonify({"status":False})

        def list_personalities_categories(self):
            personalities_categories_dir = self.lollms_paths.personalities_zoo_path  # replace with the actual path to the models folder
            personalities_categories = ["custom_personalities"]+[f.stem for f in personalities_categories_dir.iterdir() if f.is_dir() and not f.name.startswith(".")]
            return jsonify(personalities_categories)
        
        def list_personalities(self):
            category = request.args.get('category')
            if not category:
                return jsonify([])            
            try:
                if category=="custom_personalities":
                    personalities_dir = self.lollms_paths.custom_personalities_path  # replace with the actual path to the models folder
                else:
                    personalities_dir = self.lollms_paths.personalities_zoo_path/f'{category}'  # replace with the actual path to the models folder
                personalities = [f.stem for f in personalities_dir.iterdir() if f.is_dir() and not f.name.startswith(".")]
            except Exception as ex:
                personalities=[]
                ASCIIColors.error(f"No personalities found. Using default one {ex}")
            return jsonify(personalities)
        
        def list_databases(self):
            databases = [f.name for f in self.lollms_paths.personal_databases_path.iterdir() if f.suffix==".db"]
            return jsonify(databases)
        
        def select_database(self):
            data = request.get_json()
            if not data["name"].endswith(".db"):
                data["name"] += ".db"
            print(f'Selecting database {data["name"]}')
            # Create database object
            self.db = DiscussionsDB(self.lollms_paths.personal_databases_path/data["name"])
            ASCIIColors.info("Checking discussions database... ",end="")
            self.db.create_tables()
            self.db.add_missing_columns()
            self.config.db_path = data["name"]
            ASCIIColors.success("ok")

            if self.config.auto_save:
                self.config.save_config()
            
            if self.config.data_vectorization_activate and self.config.use_discussions_history:
                try:
                    ASCIIColors.yellow("0- Detected discussion vectorization request")
                    folder = self.lollms_paths.personal_databases_path/"vectorized_dbs"
                    folder.mkdir(parents=True, exist_ok=True)
                    self.long_term_memory = TextVectorizer(
                        vectorization_method=VectorizationMethod.TFIDF_VECTORIZER,#=VectorizationMethod.BM25_VECTORIZER,
                        database_path=folder/self.config.db_path,
                        data_visualization_method=VisualizationMethod.PCA,#VisualizationMethod.PCA,
                        save_db=True
                    )
                    ASCIIColors.yellow("1- Exporting discussions")
                    self.info("Exporting discussions")
                    discussions = self.db.export_all_as_markdown_list_for_vectorization()
                    ASCIIColors.yellow("2- Adding discussions to vectorizer")
                    self.info("Adding discussions to vectorizer")
                    index = 0
                    nb_discussions = len(discussions)

                    for (title,discussion) in tqdm(discussions):
                        self.socketio.emit('update_progress',{'value':int(100*(index/nb_discussions))})
                        index += 1
                        if discussion!='':
                            skill = self.learn_from_discussion(title, discussion)
                            self.long_term_memory.add_document(title, skill, chunk_size=self.config.data_vectorization_chunk_size, overlap_size=self.config.data_vectorization_overlap_size, force_vectorize=False, add_as_a_bloc=False)
                    ASCIIColors.yellow("3- Indexing database")
                    self.info("Indexing database",True, None)
                    self.long_term_memory.index()
                    ASCIIColors.yellow("Ready")
                except Exception as ex:
                    self.error(f"Couldn't vectorize the database:{ex}")
                    

            return jsonify({"status":True})


        

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
        
        def serve_audio(self, filename):
            root_dir = self.lollms_paths.personal_outputs_path
            path = os.path.join(root_dir, 'audio_out/')+"/".join(filename.split("/")[:-1])
                                
            fn = filename.split("/")[-1]
            return send_from_directory(path, fn)
        
        

        def serve_extensions(self, filename):
            path = str(self.lollms_paths.extensions_zoo_path/("/".join(filename.split("/")[:-1])))
                                
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
            if "custom_personalities" in filename:
                path = str(self.lollms_paths.custom_personalities_path/("/".join(filename.split("/")[1:-1])))
            else:
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
                personality_path = self.lollms_paths.personalities_zoo_path / data['name']
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

        def install_binding(self):
            try:
                data = request.get_json()
                # Further processing of the data
            except Exception as e:
                print(f"Error occurred while parsing JSON: {e}")
                return jsonify({"status":False, 'error':str(e)})
            ASCIIColors.info(f"- Reinstalling binding {data['name']}...")
            try:
                self.info("Unmounting binding and model")
                self.info("Reinstalling binding")
                old_bn = self.config.binding_name
                self.config.binding_name = data['name']
                self.binding =  BindingBuilder().build_binding(self.config, self.lollms_paths, InstallOption.FORCE_INSTALL, lollmsCom=self)
                self.success("Binding installed successfully")
                del self.binding
                self.binding = None
                self.config.binding_name = old_bn
                if old_bn is not None:
                    self.binding =  BindingBuilder().build_binding(self.config, self.lollms_paths, lollmsCom=self)
                    self.model = self.binding.build_model()
                    for per in self.mounted_personalities:
                        if per is not None:
                            per.model = self.model
                return jsonify({"status": True}) 
            except Exception as ex:
                self.error(f"Couldn't build binding: [{ex}]")
                trace_exception(ex)
                return jsonify({"status":False, 'error':str(ex)})

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
                del self.binding
                self.binding = None
                gc.collect()
                ASCIIColors.info("Reinstalling binding")
                old_bn = self.config.binding_name
                self.config.binding_name = data['name']
                self.binding =  BindingBuilder().build_binding(self.config, self.lollms_paths, InstallOption.FORCE_INSTALL, lollmsCom=self)
                self.success("Binding reinstalled successfully")
                self.config.binding_name = old_bn
                self.binding =  BindingBuilder().build_binding(self.config, self.lollms_paths, lollmsCom=self)
                self.model = self.binding.build_model()
                for per in self.mounted_personalities:
                    if per is not None:
                        per.model = self.model
                
                return jsonify({"status": True}) 
            except Exception as ex:
                ASCIIColors.error(f"Couldn't build binding: [{ex}]")
                trace_exception(ex)
                return jsonify({"status":False, 'error':str(ex)})

        def unInstall_binding(self):
            try:
                data = request.get_json()
                # Further processing of the data
            except Exception as e:
                ASCIIColors.error(f"Error occurred while parsing JSON: {e}")
                return jsonify({"status":False, 'error':str(e)})
            ASCIIColors.info(f"- Reinstalling binding {data['name']}...")
            try:
                ASCIIColors.info("Unmounting binding and model")
                if self.binding is not None:
                    del self.binding
                    self.binding = None
                    gc.collect()
                ASCIIColors.info("Uninstalling binding")
                old_bn = self.config.binding_name
                self.config.binding_name = data['name']
                self.binding =  BindingBuilder().build_binding(self.config, self.lollms_paths, InstallOption.NEVER_INSTALL, lollmsCom=self)
                self.binding.uninstall()
                ASCIIColors.green("Uninstalled successful")
                if old_bn!=self.config.binding_name:
                    self.config.binding_name = old_bn
                    self.binding =  BindingBuilder().build_binding(self.config, self.lollms_paths, lollmsCom=self)
                    self.model = self.binding.build_model()
                    for per in self.mounted_personalities:
                        if per is not None:
                            per.model = self.model
                else:
                    self.config.binding_name = None
                if self.config.auto_save:
                    ASCIIColors.info("Saving configuration")
                    self.config.save_config()
                    
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

        def check_update(self):
            if self.config.auto_update:
                res = check_update_()
                return jsonify({'update_availability':res})
            else:
                return jsonify({'update_availability':False})

        def restart_program(self):
            socketio.reboot=True
            self.socketio.stop()
            self.socketio.sleep(1)
            

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
            self.socketio.stop()
            run_update_script(self.args)
            sys.exit()
            
        def get_current_personality_files_list(self):
            if self.personality is None:
                return jsonify({"state":False, "error":"No personality selected"})
            return jsonify({"state":True, "files":[{"name":Path(f).name, "size":Path(f).stat().st_size} for f in self.personality.text_files]+[{"name":Path(f).name, "size":Path(f).stat().st_size} for f in self.personality.image_files]})

        def clear_personality_files_list(self):
            if self.personality is None:
                return jsonify({"state":False, "error":"No personality selected"})
            self.personality.remove_all_files()
            return jsonify({"state":True})

        def start_training(self):
            if self.config.hardware_mode=="nvidia-tensorcores" or self.config.hardware_mode=="nvidia" or self.config.hardware_mode=="apple-intel" or self.config.hardware_mode=="apple-silicon":
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
                    if per is not None:
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
            if category=="custom_personalities":
                package_full_path = self.lollms_paths.custom_personalities_path/f"{name}"
            else:            
                package_full_path = self.lollms_paths.personalities_zoo_path/package_path
            
            config_file = package_full_path / "config.yaml"
            if config_file.exists():
                if language:
                    package_path += ":" + language
                """
                if package_path in self.config["personalities"]:
                    ASCIIColors.error("Can't mount exact same personality twice")
                    return jsonify({"status": False,
                                    "error":"Can't mount exact same personality twice",
                                    "personalities":self.config["personalities"],
                                    "active_personality_id":self.config["active_personality_id"]
                                    })                
                """
                self.config["personalities"].append(package_path)
                self.mounted_personalities = self.rebuild_personalities()
                self.config["active_personality_id"]= len(self.config["personalities"])-1
                self.personality = self.mounted_personalities[self.config["active_personality_id"]]
                ASCIIColors.success("ok")
                if self.config["active_personality_id"]<0:
                    ASCIIColors.error("error:active_personality_id<0")
                    return jsonify({"status": False,
                                    "error":"active_personality_id<0",
                                    "personalities":self.config["personalities"],
                                    "active_personality_id":self.config["active_personality_id"]
                                    })         
                else:
                    if self.config.auto_save:
                        ASCIIColors.info("Saving configuration")
                        self.config.save_config()
                    ASCIIColors.success(f"Personality {name} mounted successfully")
                    return jsonify({"status": True,
                                    "personalities":self.config["personalities"],
                                    "active_personality_id":self.config["active_personality_id"]
                                    })         
            else:
                pth = str(config_file).replace('\\','/')
                ASCIIColors.error(f"nok : Personality not found @ {pth}")            
                ASCIIColors.yellow(f"Available personalities: {[p.name for p in self.mounted_personalities]}")
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
            if category=="custom_personalities":
                package_full_path = self.lollms_paths.custom_personalities_path/f"{name}"
            else:            
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
                self.config["active_personality_id"]= len(self.config["personalities"])-1
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
                ASCIIColors.yellow(f"Available personalities: {[p.name for p in self.mounted_personalities]}")
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
            language    = data.get('language',None)
            try:
                personality_id = f"{category}/{name}" if language is None or language=="" else f"{category}/{name}:{language}"
                index = self.config["personalities"].index(personality_id)
                self.config["personalities"].remove(personality_id)
                if self.config["active_personality_id"]>=index:
                    self.config["active_personality_id"]=0
                if len(self.config["personalities"])>0:
                    self.mounted_personalities = self.rebuild_personalities()
                    self.personality = self.mounted_personalities[self.config["active_personality_id"]]
                else:
                    self.personalities = ["generic/lollms"]
                    self.mounted_personalities = self.rebuild_personalities()
                    if self.config["active_personality_id"]<len(self.mounted_personalities):
                        self.personality = self.mounted_personalities[self.config["active_personality_id"]]
                    else:
                        self.config["active_personality_id"] = -1
                ASCIIColors.success("ok")
                if self.config.auto_save:
                    ASCIIColors.info("Saving configuration")
                    self.config.save_config()
                return jsonify({
                            "status": True,
                            "personalities":self.config["personalities"],
                            "active_personality_id":self.config["active_personality_id"]
                            })         
            except Exception as ex:
                trace_exception(ex)
                if language:
                    ASCIIColors.error(f"nok : Personality not found @ {category}/{name}:{language}")
                else:
                    ASCIIColors.error(f"nok : Personality not found @ {category}/{name}")
                    
                ASCIIColors.yellow(f"Available personalities: {[p.name for p in self.mounted_personalities]}")
                return jsonify({"status": False, "error":"Couldn't unmount personality"})         

        def unmount_all_personalities(self):
            self.config.personalities=["generic/lollms"]
            self.mounted_personalities=[]
            self.personality=None
            self.mount_personality(0)
            self.config.save_config()
            return jsonify({"status":True})
        



        def get_extension_settings(self):
            print("- Retreiving extension settings")
            data = request.get_json()
            extension:LOLLMSExtension = next((element for element in self.mounted_extensions if element.name == data["name"]), None)
            return jsonify(extension.extension_config.config_template.template)
        
        def set_extension_settings(self):
            print("- Setting extension settings")
            data = request.get_json()
            extension:LOLLMSExtension = next((element for element in self.mounted_extensions if element.name == data["name"]), None)
            extension.extension_config.update_template(data["config"])
            return jsonify(extension.extension_config.config_template.template)
        
                   
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

        
        def install_extension(self):
            try:
                data = request.get_json()
                # Further processing of the data
            except Exception as e:
                print(f"Error occurred while parsing JSON: {e}")
                return jsonify({"status":False, 'error':str(e)})
            if not 'name' in data.keys():
                try:
                    data['name']=self.config.extensions[-1]
                except Exception as ex:
                    self.error(ex)
                    return
            try:
                extension_path = self.lollms_paths.extensions_zoo_path / data['name']
                ASCIIColors.info(f"- Installing extension {data['name']}...")
                try:
                    self.mounted_extensions.append(ExtensionBuilder().build_extension(extension_path,self.lollms_paths, self, InstallOption.FORCE_INSTALL))
                    return jsonify({"status":True})
                except Exception as ex:
                    ASCIIColors.error(f"Extension file not found or is corrupted ({data['name']}).\nReturned the following exception:{ex}\nPlease verify that the personality you have selected exists or select another personality. Some updates may lead to change in personality name or category, so check the personality selection in settings to be sure.")
                    trace_exception(ex)
                    ASCIIColors.info("Trying to force reinstall")
                    return jsonify({"status":False, 'error':str(e)})

            except Exception as e:
                return jsonify({"status":False, 'error':str(e)})


        def reinstall_extension(self):
            try:
                data = request.get_json()
                # Further processing of the data
            except Exception as e:
                print(f"Error occurred while parsing JSON: {e}")
                return jsonify({"status":False, 'error':str(e)})
            if not 'name' in data.keys():
                try:
                    data['name']=self.config.extensions[-1]
                except Exception as ex:
                    self.error(ex)
                    return
            try:
                extension_path = self.lollms_paths.extensions_zoo_path / data['name']
                ASCIIColors.info(f"- Reinstalling extension {data['name']}...")
                ASCIIColors.info("Unmounting extension")
                if data['name'] in self.config.extensions:
                    idx = self.config.extensions.index(data['name'])
                    print(f"index = {idx}")
                    if len(self.mount_extensions)>idx:
                        del self.mounted_extensions[idx]
                    gc.collect()
                try:
                    self.mounted_extensions.append(ExtensionBuilder().build_extension(extension_path,self.lollms_paths, self, InstallOption.FORCE_INSTALL))
                    return jsonify({"status":True})
                except Exception as ex:
                    ASCIIColors.error(f"Extension file not found or is corrupted ({data['name']}).\nReturned the following exception:{ex}\nPlease verify that the personality you have selected exists or select another personality. Some updates may lead to change in personality name or category, so check the personality selection in settings to be sure.")
                    trace_exception(ex)
                    ASCIIColors.info("Trying to force reinstall")
                    return jsonify({"status":False, 'error':str(e)})

            except Exception as e:
                return jsonify({"status":False, 'error':str(e)})

        def p_mount_extension(self):
            print("- Mounting extension")
            try:
                data = request.get_json()
                # Further processing of the data
            except Exception as e:
                print(f"Error occurred while parsing JSON: {e}")
                return
            category = data['category']
            name = data['folder']

            package_path = f"{category}/{name}"
            package_full_path = self.lollms_paths.extensions_zoo_path/package_path
            config_file = package_full_path / "config.yaml"
            if config_file.exists():
                self.config["extensions"].append(package_path)
                self.mounted_extensions = self.rebuild_extensions()
                ASCIIColors.success("ok")
                if self.config.auto_save:
                    ASCIIColors.info("Saving configuration")
                    self.config.save_config()
                ASCIIColors.success(f"Extension {name} mounted successfully")
                return jsonify({"status": True,
                                "extensions":self.config["extensions"],
                                })         
            else:
                pth = str(config_file).replace('\\','/')
                ASCIIColors.error(f"nok : Extension not found @ {pth}")
                return jsonify({"status": False, "error":f"Extension not found @ {pth}"})         



        def p_remount_extension(self):
            print("- Remounting extension")
            try:
                data = request.get_json()
                # Further processing of the data
            except Exception as e:
                print(f"Error occurred while parsing JSON: {e}")
                return
            category = data['category']
            name = data['folder']




            package_path = f"{category}/{name}"
            package_full_path = self.lollms_paths.extensions_zoo_path/package_path
            config_file = package_full_path / "config.yaml"
            if config_file.exists():
                ASCIIColors.info(f"Unmounting personality {package_path}")
                index = self.config["extensions"].index(f"{category}/{name}")
                self.config["extensions"].remove(f"{category}/{name}")
                if len(self.config["extensions"])>0:
                    self.mounted_personalities = self.rebuild_extensions()
                else:
                    self.personalities = ["generic/lollms"]
                    self.mounted_personalities = self.rebuild_extensions()


                ASCIIColors.info(f"Mounting personality {package_path}")
                self.config["personalities"].append(package_path)
                self.mounted_personalities = self.rebuild_extensions()
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
                ASCIIColors.yellow(f"Available personalities: {[p.name for p in self.mounted_personalities]}")
                return jsonify({"status": False, "error":f"Personality not found @ {pth}"})         

        def p_unmount_extension(self):
            print("- Unmounting extension ...")
            try:
                data = request.get_json()
                # Further processing of the data
            except Exception as e:
                print(f"Error occurred while parsing JSON: {e}")
                return
            category    = data['category']
            name        = data['folder']
            language    = data.get('language',None)
            try:
                personality_id = f"{category}/{name}" if language is None else f"{category}/{name}:{language}"
                index = self.config["personalities"].index(personality_id)
                self.config["extensions"].remove(personality_id)
                self.mounted_extensions = self.rebuild_extensions()
                ASCIIColors.success("ok")
                if self.config.auto_save:
                    ASCIIColors.info("Saving configuration")
                    self.config.save_config()
                return jsonify({
                            "status": True,
                            "extensions":self.config["extensions"]
                            })         
            except:
                if language:
                    ASCIIColors.error(f"nok : Personality not found @ {category}/{name}:{language}")
                else:
                    ASCIIColors.error(f"nok : Personality not found @ {category}/{name}")
                    
                ASCIIColors.yellow(f"Available personalities: {[p.name for p in self.mounted_personalities]}")
                return jsonify({"status": False, "error":"Couldn't unmount personality"})     


        def list_extensions_categories(self):
            extensions_categories_dir = self.lollms_paths.extensions_zoo_path  # replace with the actual path to the models folder
            extensions_categories = [f.stem for f in extensions_categories_dir.iterdir() if f.is_dir() and not f.name.startswith(".")]
            return jsonify(extensions_categories)        


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
                    self.binding.settings_updated()
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
            ASCIIColors.info("Selecting personality")
            data = request.get_json()
            id = data['id']
            print(f"- Selecting active personality {id} ...",end="")
            if id<len(self.mounted_personalities):
                self.config["active_personality_id"]=id
                self.personality:AIPersonality = self.mounted_personalities[self.config["active_personality_id"]]
                if self.personality.processor:
                    self.personality.processor.selected()
                ASCIIColors.success("ok")
                print(f"Selected {self.personality.name}")
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
                        

        def upload_avatar(self):      
            file = request.files['avatar']
            file.save(self.lollms_paths.personal_user_infos_path/file.filename)
            return jsonify({"status": True,"fileName":file.filename})   
            
            
            
        def rename_discussion(self):
            data = request.get_json()
            client_id = data["client_id"]
            title = data["title"]
            self.connections[client_id]["current_discussion"].rename(title)
            return {"status":True}
        
        def edit_title(self):
            data                = request.get_json()
            client_id           = data["client_id"]
            title               = data["title"]
            discussion_id       = data["id"]
            self.connections[client_id]["current_discussion"] = Discussion(discussion_id, self.db)
            self.connections[client_id]["current_discussion"].rename(title)
            return jsonify({'status':True})
        
        def make_title(self):
            ASCIIColors.info("Making title")
            data                = request.get_json()
            discussion_id       = data["id"]
            discussion = Discussion(discussion_id, self.db)
            title = self.make_discussion_title(discussion)
            discussion.rename(title)
            return jsonify({'status':True, 'title':title})
        
        
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
            metadata        = request.args.get("metadata",None)
            try:
                self.connections[client_id]["current_discussion"].edit_message(message_id, new_message,new_metadata=metadata)
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
            try:
                model_list = self.binding.get_available_models(self)
            except Exception as ex:
                self.error("Coudln't list models. Please reinstall the binding or notify ParisNeo on the discord server")
                return jsonify([])

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
            if config['host']=="0.0.0.0":
                webbrowser.open(f"http://localhost:{config['port']}")
            else:
                webbrowser.open(f"http://{config['host']}:{config['port']}")


        try:
            socketio.reboot = False
            socketio.run(app, host=config["host"], port=config["port"],
                        # prevent error: The Werkzeug web server is not designed to run in production
                        allow_unsafe_werkzeug=True)
            if socketio.reboot:
                ASCIIColors.info("")
                ASCIIColors.info("")
                ASCIIColors.info("")
                ASCIIColors.info(" ╔══════════════════════════════════════════════════╗")
                ASCIIColors.info(" ║              Restarting backend                  ║")
                ASCIIColors.info(" ╚══════════════════════════════════════════════════╝")
                ASCIIColors.info("")
                ASCIIColors.info("")
                ASCIIColors.info("")
                run_restart_script(args)
                
        except Exception as ex:
            trace_exception(ex)
        # http_server = WSGIServer((config["host"], config["port"]), app, handler_class=WebSocketHandler)
        # http_server.serve_forever()
except Exception as ex:
    trace_exception(ex)
    run_update_script()
