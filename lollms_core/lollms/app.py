from lollms.main_config import LOLLMSConfig
from lollms.paths import LollmsPaths
from lollms.personality import PersonalityBuilder, AIPersonality
from lollms.binding import LLMBinding, BindingBuilder, ModelBuilder, BindingType
from lollms.databases.discussions_database import Message
from lollms.config import InstallOption
from lollms.helpers import ASCIIColors, trace_exception
from lollms.com import NotificationType, NotificationDisplayType, LoLLMsCom
from lollms.terminal import MainMenu
from lollms.types import MSG_OPERATION_TYPE, SENDER_TYPES
from lollms.utilities import convert_language_name, process_ai_output
from lollms.client_session import Client, Session
from lollms.databases.skills_database import SkillsLibrary
from lollms.tasks import TasksLibrary
from lollms.prompting import LollmsLLMTemplate, LollmsContextDetails
from lollms.types import MSG_OPERATION_TYPE, MSG_TYPE
from lollms.function_call import FunctionType, FunctionCall
from safe_store import SafeStore
import importlib
import asyncio
import re

from typing import Callable, Any
from pathlib import Path
from datetime import datetime
from functools import partial
from socketio import AsyncServer
from typing import Tuple, List, Dict
import subprocess
import importlib
import sys, os
import platform
import gc
import yaml
import time
from lollms.utilities import run_with_current_interpreter
import socket
import json
import pipmaster as pm

import importlib.util
class LollmsApplication(LoLLMsCom):
    def __init__(
                    self, 
                    app_name:str, 
                    config:LOLLMSConfig, 
                    lollms_paths:LollmsPaths, 
                    load_binding=True, 
                    load_model=True, 
                    try_select_binding=False, 
                    try_select_model=False,
                    callback=None,
                    sio:AsyncServer=None,
                    free_mode=False
                ) -> None:
        """
        Creates a LOLLMS Application
        """
        super().__init__(sio)
        self.app_name                   = app_name
        self.config                     = config
        ASCIIColors.warning(f"Configuration fix ")
        try:
            config.personalities = [p.split(":")[0] for p in config.personalities]
            config.save_config()
        except Exception as ex:
            trace_exception(ex)

        self.lollms_paths               = lollms_paths

        # TODO : implement
        self.embedding_models           = []

        self.menu                       = MainMenu(self, callback)
        self.mounted_personalities      = []
        self.personality:AIPersonality  = None

        self.binding                    = None
        self.model:LLMBinding           = None
        self.long_term_memory           = None

        self.tts                        = None

        self.handle_generate_msg: Callable[[str, Dict], None]               = None
        self.generate_msg_with_internet: Callable[[str, Dict], None]        = None
        self.handle_continue_generate_msg_from: Callable[[str, Dict], None] = None
        
        # Trust store 
        self.bk_store = None
        
        # services
        self.ollama         = None
        self.vllm           = None
        self.tti = None
        self.tts = None
        self.stt = None
        self.ttm = None
        self.ttv = None
        
        self.rt_com = None
        self.is_internet_available = self.check_internet_connection()
        self.template = LollmsLLMTemplate(self.config, self.personality)


        # Keeping track of current discussion and message
        self._current_user_message_id = 0
        self._current_ai_message_id = 0
        self._message_id = 0

        self.current_generation_task = None




        if not free_mode:
            try:
                if config.auto_update and self.is_internet_available:
                    def check_lollms_bindings_zoo():
                        subprocess.run(["git", "-C", self.lollms_paths.bindings_zoo_path, "checkout", "main"])            
                        subprocess.run(["git", "-C", self.lollms_paths.bindings_zoo_path, "pull"])
                    ASCIIColors.blue("Bindings zoo found in your personal space.")
                    ASCIIColors.execute_with_animation("Pulling last bindings zoo", check_lollms_bindings_zoo)

                    # Pull the repository if it already exists
                    def check_lollms_personalities_zoo():
                        subprocess.run(["git", "-C", self.lollms_paths.personalities_zoo_path, "checkout", "main"])            
                        subprocess.run(["git", "-C", self.lollms_paths.personalities_zoo_path, "pull"])            
                    ASCIIColors.blue("Personalities zoo found in your personal space.")
                    ASCIIColors.execute_with_animation("Pulling last personalities zoo", check_lollms_personalities_zoo)

                    # Pull the repository if it already exists
                    def check_lollms_models_zoo():
                        subprocess.run(["git", "-C", self.lollms_paths.models_zoo_path, "checkout", "main"])            
                        subprocess.run(["git", "-C", self.lollms_paths.models_zoo_path, "pull"])            
                    ASCIIColors.blue("Models zoo found in your personal space.")
                    ASCIIColors.execute_with_animation("Pulling last Models zoo", check_lollms_models_zoo)

                    # Pull the repository if it already exists
                    def check_lollms_function_calling_zoo():
                        subprocess.run(["git", "-C", self.lollms_paths.functions_zoo_path, "checkout", "main"])            
                        subprocess.run(["git", "-C", self.lollms_paths.functions_zoo_path, "pull"])            
                    ASCIIColors.blue("Function calling zoo found in your personal space.")
                    ASCIIColors.execute_with_animation("Pulling last Function calling zoo", check_lollms_function_calling_zoo)

                    # Pull the repository if it already exists
                    def check_lollms_services_zoo():
                        subprocess.run(["git", "-C", self.lollms_paths.services_zoo_path, "checkout", "main"])            
                        subprocess.run(["git", "-C", self.lollms_paths.services_zoo_path, "pull"])            
                    ASCIIColors.blue("Services zoo found in your personal space.")
                    ASCIIColors.execute_with_animation("Pulling last services zoo", check_lollms_services_zoo)


            except Exception as ex:
                ASCIIColors.error("Couldn't pull zoos. Please contact the main dev on our discord channel and report the problem.")
                trace_exception(ex)

            if self.config.binding_name is None:
                ASCIIColors.warning(f"No binding selected")
                if try_select_binding:
                    ASCIIColors.info("Please select a valid model or install a new one from a url")
                    self.menu.select_binding()
            else:
                if load_binding:
                    try:
                        ASCIIColors.info(f">Loading binding {self.config.binding_name}. Please wait ...")
                        self.binding = self.load_binding()
                    except Exception as ex:
                        ASCIIColors.error(f"Failed to load binding.\nReturned exception: {ex}")
                        trace_exception(ex)

                    if self.binding is not None:
                        ASCIIColors.success(f"Binding {self.config.binding_name} loaded successfully.")
                        if load_model:
                            if self.config.model_name is None:
                                ASCIIColors.warning(f"No model selected")
                                if try_select_model:
                                    print("Please select a valid model")
                                    self.menu.select_model()
                                    
                            if self.config.model_name is not None:
                                try:
                                    ASCIIColors.info(f">Loading model {self.config.model_name}. Please wait ...")
                                    self.model          = self.load_model()
                                    if self.model is not None:
                                        ASCIIColors.success(f"Model {self.config.model_name} loaded successfully.")

                                except Exception as ex:
                                    ASCIIColors.error(f"Failed to load model.\nReturned exception: {ex}")
                                    trace_exception(ex)
                    else:
                        ASCIIColors.warning(f"Couldn't load binding {self.config.binding_name}.")
                
            self.mount_personalities()
            
            try:
                self.load_rag_dbs()
            except Exception as ex:
                trace_exception(ex)
                
                
        self.session                    = Session(lollms_paths)
        self.tasks_library              = TasksLibrary(self)
        if self.config.activate_skills_lib:
            self.skills_library             = SkillsLibrary(self.lollms_paths.personal_skills_path/(self.config.skills_lib_database_name+".db"), config = self.config)
        else:
            self.skills_library = None

    # properties
    @property
    def message_id(self):
        return self._message_id

    @message_id.setter
    def message_id(self, id):
        self._message_id = id

    @property
    def current_user_message_id(self):
        return self._current_user_message_id

    @current_user_message_id.setter
    def current_user_message_id(self, id):
        self._current_user_message_id = id
        self._message_id = id

    @property
    def current_ai_message_id(self):
        return self._current_ai_message_id

    @current_ai_message_id.setter
    def current_ai_message_id(self, id):
        self._current_ai_message_id = id
        self._message_id = id



    def load_function_call(self, fc, client):
        dr = Path(fc["dir"])
        try:
            with open(dr/"config.yaml", "r") as f:
                fc_dict = yaml.safe_load(f.read())
                # let us check static settings from fc_dict
                # Step 1: Construct the full path to the function.py module
                module_path = dr / "function.py"
                module_name = "function"  # Name for the loaded module

                # Step 2: Use importlib.util to load the module from the file path
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None:
                    raise ImportError(f"Could not load module from {module_path}")
                
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module  # Add the module to sys.modules
                spec.loader.exec_module(module)    # Execute the module

                # Step 3: Retrieve the class from the module using the class name
                class_name = fc_dict["class_name"]
                class_ = getattr(module, class_name)
                
                # Step 4: Create an instance of the class and store it in fc_dict["class"]
                fc_dict["class"] = class_(self, client)
                return fc_dict
        except Exception as ex:
            self.error("Couldn't add function call to context")
            trace_exception(ex)
        return None
    
    def execute_function(self, code, client):
        function_call=json.loads(code)
        name = function_call["function_name"]
        for fc in self.config.mounted_function_calls:
            if fc["selected"]:
                if fc["name"] == name:
                    fci = self.load_function_call(fc, client)
                    if fci:
                        output = fci["class"].execute(LollmsContextDetails(client),**function_call["function_parameters"])
                        return output
        


    def embed_function_call_in_prompt(self, original_prompt):
        """Embeds function call descriptions in the system prompt"""
        function_descriptions = [
            "You have access to these functions. Use them when needed:",
            "Format: <lollms_function_call>{JSON}</lollms_function_call>"
        ]
        
        # Get mounted functions
        mounted_functions = [
            fc for fc in self.config.mounted_function_calls 
            if fc["mounted"]
        ]
        
        for fc in mounted_functions:
            try:
                # Load function config
                fn_path = self.paths.functions_zoo_path / fc["name"]
                with open(fn_path/"config.yaml") as f:
                    config = yaml.safe_load(f)
                    
                # Build function description
                desc = [
                    f"Function: {config['name']}",
                    f"Description: {config['description']}",
                    f"Parameters: {json.dumps(config.get('parameters', {}))}",
                    f"Returns: {json.dumps(config.get('returns', {}))}",
                    f"Needs Processing: {str(config.get('needs_processing', True)).lower()}",
                    f"Examples: {', '.join(config.get('examples', []))}"
                ]
                function_descriptions.append("\n".join(desc))
                
            except Exception as e:
                print(f"Error loading function {fc['name']}: {e}")

        return original_prompt + "\n\n" + "\n\n".join(function_descriptions)

    def detect_function_calls(self, text):
        """Detects and parses function calls in AI output"""
        import re
        import json
        
        pattern = r'<lollms_function_call>(.*?)</lollms_function_call>'
        matches = re.findall(pattern, text, re.DOTALL)
        
        valid_calls = []
        
        for match in matches:
            try:
                call_data = json.loads(match.strip())
                
                # Validate required fields
                if not all(k in call_data for k in ["function_name", "parameters"]):
                    continue
                    
                # Check if function is mounted
                is_mounted = any(
                    fc["name"] == call_data["function_name"] and fc["mounted"]
                    for fc in self.config.mounted_function_calls
                )
                
                if not is_mounted:
                    continue
                    
                # Set default needs_processing if missing
                if "needs_processing" not in call_data:
                    call_data["needs_processing"] = True
                    
                valid_calls.append({
                    "function_name": call_data["function_name"],
                    "parameters": call_data["parameters"],
                    "needs_processing": call_data["needs_processing"]
                })
                
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error parsing function call: {e}")
                continue
                
        return valid_calls

    @staticmethod
    def check_internet_connection():
        global is_internet_available
        try:
            # Attempt to connect to a reliable server (in this case, Google's DNS)
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            is_internet_available = True
            return True
        except OSError:
            is_internet_available = False
            return False


    def backup_trust_store(self):
        self.bk_store = None
        if 'REQUESTS_CA_BUNDLE' in os.environ:
            self.bk_store = os.environ['REQUESTS_CA_BUNDLE']
            del os.environ['REQUESTS_CA_BUNDLE']

    def restore_trust_store(self):
        if self.bk_store is not None:
            os.environ['REQUESTS_CA_BUNDLE'] = self.bk_store

    def model_path_to_binding_model(self, model_path:str):
        parts = model_path.strip().split("::")
        if len(parts)<2:
            raise Exception("Model path is not in the format binding:model_name!")
        binding = parts[0]
        model_name = parts[1]
        return binding, model_name
      
    def select_model(self, binding_name, model_name, destroy_previous_model=True):
        self.config["binding_name"] = binding_name
        self.config["model_name"] = model_name
        print(f"New binding selected : {binding_name}")

        try:
            if self.binding and destroy_previous_model:
                self.binding.destroy_model()
            self.binding = None
            self.model = None
            for per in self.mounted_personalities:
                if per is not None:
                    per.model = None
            gc.collect()
            self.binding = BindingBuilder().build_binding(self.config, self.lollms_paths, InstallOption.INSTALL_IF_NECESSARY, lollmsCom=self)
            self.config["model_name"] = model_name
            self.model = self.binding.build_model()
            for per in self.mounted_personalities:
                if per is not None:
                    per.model = self.model
            self.config.save_config()
            ASCIIColors.green("Binding loaded successfully")
            return True
        except Exception as ex:
            ASCIIColors.error(f"Couldn't build binding: [{ex}]")
            trace_exception(ex)
            return False
        

    def set_active_model(self, model):
        print(f"New model active : {model.model_name}")
        self.model = model
        self.binding = model
        self.personality.model = model
        for per in self.mounted_personalities:
            if per is not None:
                per.model = self.model
        self.config["binding_name"] = model.binding_folder_name
        self.config["model_name"] = model.model_name

                
    def add_discussion_to_skills_library(self, client: Client):
        messages = client.discussion.get_messages()

        # Extract relevant information from messages
        def cb(str, MSG_TYPE_=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT, dict=None, list=None):
            if MSG_TYPE_!=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK:
                self.ShowBlockingMessage(f"Learning\n{str}")
        bk_cb = self.tasks_library.callback
        self.tasks_library.callback = cb
        content = self._extract_content(messages, cb)
        self.tasks_library.callback = bk_cb

        # Generate title
        title_prompt =  f"{self.separator_template}".join([
            f"{self.system_full_header}Generate a concise and descriptive title and category for the following content:",
            content
            ])
        template =  f"{self.separator_template}".join([
            "{",
            '   "title":"here you put the title"',
            '   "category":"here you put the category"',
            "}"])
        language = "json"
        title_category_json = json.loads(self._generate_code(title_prompt, template, language))
        title = title_category_json["title"]
        category = title_category_json["category"]

        # Add entry to skills library
        self.skills_library.add_entry(1, category, title, content)
        return category, title, content

    def _extract_content(self, messages:List[Message], callback = None):      
        message_content = ""

        for message in messages:
            rank = message.rank
            sender = message.sender
            text = message.content
            message_content += f"Rank {rank} - {sender}: {text}\n"

        return self.tasks_library.summarize_text(
            message_content,
            "\n".join([
                "Find out important information from the discussion and report them.",
                "Format the output as sections if applicable:",
                "Global context: Explain in a sentense or two the subject of the discussion",
                "Interesting things (if applicable): If you find interesting information or something that was discovered or built in this discussion, list it here with enough details to be reproducible just by reading this text.",
                "Code snippet (if applicable): If there are important code snippets, write them here in a markdown code tag.",
                "Make the output easy to understand.",
                "The objective is not to talk about the discussion but to store the important information for future usage. Do not report useless information.",
                "Do not describe the discussion and focuse more on reporting the most important information from the discussion."
            ]),
            doc_name="discussion",
            callback=callback)
        

    def _generate_text(self, prompt):
        max_tokens = min(self.config.ctx_size - self.model.count_tokens(prompt),self.config.max_n_predict if self.config.max_n_predict else self.config.ctx_size- self.model.count_tokens(prompt))
        generated_text = self.model.generate(prompt, max_tokens)
        return generated_text.strip()
    
    def _generate_code(self, prompt, template, language):
        max_tokens = min(self.config.ctx_size - self.model.count_tokens(prompt),self.config.max_n_predict if self.config.max_n_predict else self.config.ctx_size- self.model.count_tokens(prompt))
        generated_code = self.personality.generate_code(prompt, self.personality.image_files, template, language, max_size= max_tokens)
        return generated_code

    def get_uploads_path(self, client_id):
        return self.lollms_paths.personal_uploads_path
    
    def load_rag_dbs(self):
        ASCIIColors.info("Loading RAG datalakes")
        self.active_datalakes = []
        for rag_db in self.config.datalakes:
            if rag_db['mounted']:
                if rag_db['type']=='safe_store':
                    try:                    
                        from safe_store import SafeStore
                        # Vectorizer selection
                        vectorizer_name = self.config.rag_vectorizer_model or "st:all-MiniLM-L6-v2"
                        # Create database path and initialize VectorDatabase
                        db_path = Path(rag_db['path']) / f"{rag_db['alias']}.sqlite"
                        vdb = SafeStore(db_path)   

                        # Add to active databases
                        self.active_datalakes.append(
                            rag_db | {"binding": vdb, "vectorizer_name":vectorizer_name}
                        )

                    except Exception as ex:
                        trace_exception(ex)
                        ASCIIColors.error(f"Couldn't load {db_path} consider revectorizing it")
    def load_service_from_folder(self, folder_path, target_name):
        # Convert folder_path to a Path object
        folder_path = Path(folder_path)

        # List all folders in the given directory
        folders = [f for f in folder_path.iterdir() if f.is_dir()]

        # Check if the target_name matches any folder name
        target_folder = folder_path / target_name
        if target_folder in folders:
            try:
                # Load the config.yaml file
                config_path = target_folder / "config.yaml"
                with open(config_path, 'r') as file:
                    config = yaml.safe_load(file)

                # Extract the class_name from the config
                class_name = config.get('class_name')
                if not class_name:
                    raise ValueError(f"class_name not found in {config_path}")

                # Load the Python file
                python_file_path = target_folder / f"service.py"
                spec = importlib.util.spec_from_file_location(target_name, python_file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Import the class and instantiate it
                class_ = getattr(module, class_name)
                instance = class_(self)  # Pass the config as a parameter to the constructor

                return instance
            except Exception as ex:
                trace_exception(ex)
        else:
            ASCIIColors.error(f"No folder named {target_name} found in {folder_path}")

    def start_servers(self):
        ASCIIColors.yellow("* - * - * - Starting services - * - * - *")
        def start_local_services(*args, **kwargs):
            for rag_server in self.config.rag_local_services:
                try:
                    # - alias: datalake
                    #     key: ''
                    #     path: ''
                    #     start_at_startup: false
                    #     type: lightrag
                    #     url: http://localhost:9621/

                    if rag_server["start_at_startup"]:
                        if rag_server["type"]=="lightrag":
                            try:
                                self.ShowBlockingMessage("Installing Lightrag\nPlease wait...")
                                # Define the path to the apps folder
                                if not pm.is_installed("lightrag-hku"):
                                    apps_folder = self.lollms_paths.personal_user_infos_path / "apps"
                                    apps_folder.mkdir(parents=True, exist_ok=True)  # Ensure the apps folder exists
                                    # Define the path to clone the repository
                                    clone_path = apps_folder / "LightRAG"
                                    
                                    # Clone the repository if it doesn't already exist
                                    if not clone_path.exists():
                                        subprocess.run(["git", "clone", "https://github.com/ParisNeo/LightRAG.git", str(clone_path)])
                                        print(f"Repository cloned to: {clone_path}")
                                    else:
                                        print(f"Repository already exists at: {clone_path}")
                                    
                                    # Install the package in editable mode with extras
                                    subprocess.run([sys.executable, "-m", "pip", "install", "-e", f"{str(clone_path)}[api,tools]"])                                    
                                subprocess.Popen(
                                ["lightrag-server", "--llm-binding", "lollms", "--embedding-binding", "lollms", "--input-dir", rag_server["input_path"], "--working-dir", rag_server["working_path"]],
                                text=True,
                                stdout=None, # This will make the output go directly to console
                                stderr=None  # This will make the errors go directly to console
                                )
                                self.HideBlockingMessage()
                            except Exception as ex:
                                self.HideBlockingMessage()
                                trace_exception(ex)
                except Exception as ex:
                    trace_exception(ex)
                    self.warning(f"Couldn't start lightrag")

        ASCIIColors.execute_with_animation("Loading RAG servers", start_local_services,ASCIIColors.color_blue)

        if self.config.active_stt_service and self.config.active_stt_service!="None":
            def start_stt(*args, **kwargs):
                self.stt = self.load_service_from_folder(self.lollms_paths.services_zoo_path/"stt", self.config.active_stt_service)
            ASCIIColors.execute_with_animation("Loading loacal STT services", start_stt, ASCIIColors.color_blue)

        if self.config.active_tts_service and self.config.active_tts_service!="None":
            def start_tts(*args, **kwargs):
                try:
                    self.tti = self.load_service_from_folder(self.lollms_paths.services_zoo_path/"tts", self.config.active_tts_service)
                except Exception as ex:
                    trace_exception(ex)
            ASCIIColors.execute_with_animation("Loading TTS services", start_tts, ASCIIColors.color_blue)

        if self.config.active_tti_service and self.config.active_tti_service!="None":
            def start_tti(*args, **kwargs):
                self.tti = self.load_service_from_folder(self.lollms_paths.services_zoo_path/"tti", self.config.active_tti_service)
            ASCIIColors.execute_with_animation("Loading loacal TTI services", start_tti, ASCIIColors.color_blue)

        if self.config.active_ttm_service and self.config.active_ttm_service!="None":
            def start_ttm(*args, **kwargs):
                self.ttm = self.load_service_from_folder(self.lollms_paths.services_zoo_path/"ttm", self.config.active_ttm_service)
            ASCIIColors.execute_with_animation("Loading loacal TTM services", start_ttm, ASCIIColors.color_blue)

        if self.config.active_ttv_service:
            def start_ttv(*args, **kwargs):
                self.ttv = self.load_service_from_folder(self.lollms_paths.services_zoo_path/"ttv", self.config.active_ttv_service)
            ASCIIColors.execute_with_animation("Loading loacal TTV services", start_ttv, ASCIIColors.color_blue)



    def verify_servers(self, reload_all=False):
        ASCIIColors.yellow("* - * - * - Verifying services - * - * - *")

        try:
            ASCIIColors.blue("Loading active local TTT services")
            
            if self.config.active_tti_service:
                def start_tti(*args, **kwargs):
                    self.tti = self.load_service_from_folder(self.lollms_paths.services_zoo_path/"tti", self.config.active_tti_service)
                ASCIIColors.execute_with_animation("Loading loacal TTI services", start_tti, ASCIIColors.color_blue)


            if self.config.active_stt_service:
                def start_stt(*args, **kwargs):
                    self.stt = self.load_service_from_folder(self.lollms_paths.services_zoo_path/"stt", self.config.active_stt_service)
                ASCIIColors.execute_with_animation("Loading loacal STT services", start_stt, ASCIIColors.color_blue)

            if self.config.active_tts_service:
                def start_tts(*args, **kwargs):
                    self.tts = self.load_service_from_folder(self.lollms_paths.services_zoo_path/"tts", self.config.active_tts_service)
                ASCIIColors.execute_with_animation("Loading loacal TTS services", start_tts, ASCIIColors.color_blue)


            if self.config.active_ttm_service:
                def start_ttm(*args, **kwargs):
                    self.ttm = self.load_service_from_folder(self.lollms_paths.services_zoo_path/"ttm", self.config.active_ttm_service)
                ASCIIColors.execute_with_animation("Loading loacal TTM services", start_ttm, ASCIIColors.color_blue)
            
            if self.config.active_ttv_service:
                def start_ttv(*args, **kwargs):
                    self.ttv = self.load_service_from_folder(self.lollms_paths.services_zoo_path/"ttv", self.config.active_ttv_service)
                ASCIIColors.execute_with_animation("Loading loacal TTV services", start_ttv, ASCIIColors.color_blue)



        except Exception as ex:
            trace_exception(ex)
            

    async def new_message(
        self,
        client_id,
        sender=None,
        content="",
        message_type: MSG_OPERATION_TYPE = MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT,
        sender_type: SENDER_TYPES = SENDER_TYPES.SENDER_TYPES_AI,
        open=False,
        compute_nb_tokens=False
    ):
        client = self.session.get_client(client_id)
        # self.close_message(client_id)
        if sender == None:
            sender = self.personality.name
        try:
            if compute_nb_tokens:
                nb_tokens = self.model.count_tokens(content)
            else:
                nb_tokens = 0
        except:
            nb_tokens = 0
        msg = client.discussion.add_message(
            message_type=message_type.value,
            sender_type=sender_type.value,
            sender=sender,
            content=content,
            steps=[],
            metadata=None,
            ui=None,
            rank=0,
            parent_message_id=(
                client.discussion.current_message.id
                if client.discussion.current_message is not None
                else 0
            ),
            binding=self.config["binding_name"],
            model=self.config["model_name"],
            personality=self.config["personalities"][
                self.config["active_personality_id"]
            ],
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            nb_tokens = nb_tokens
        )
        await self.sio.emit(
                "new_message",
                {
                    "sender": sender,
                    "message_type": message_type.value,
                    "sender_type": sender_type.value,
                    "content": content if message_type!= MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI else "",
                    "metadata": None,
                    "ui": content if message_type== MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI else None,
                    "discussion_id":client.discussion.discussion_id,
                    "id": msg.id,
                    "parent_message_id": msg.parent_message_id,
                    "binding": self.binding.binding_folder_name if self.binding else None,
                    "model": self.model.model_name  if self.model else "undefined",
                    "personality": self.personality.name,
                    "created_at": client.discussion.current_message.created_at,
                    "started_generating_at": client.discussion.current_message.started_generating_at,
                    "finished_generating_at": client.discussion.current_message.finished_generating_at,
                    "nb_tokens": client.discussion.current_message.nb_tokens,
                    "open": open,
                },
                to=client_id,
            )
        return msg


    async def set_message_html(self, client_id:str, ui_text:str):
        """This sends ui text to front end

        Args:
            ui_text (dict): The ui code to be sent to the front end
            client_id the id of the client
        """
        await self.update_message_ui(client_id, ui_text)

    async def emit_socket_io_info(self, name, data, client_id):
        await self.sio.emit(name, data, to=client_id)

    async def notify(
        self,
        content,
        notification_type: NotificationType = NotificationType.NOTIF_SUCCESS,
        duration: int = 4,
        client_id=None,
        display_type: NotificationDisplayType = NotificationDisplayType.TOAST,
        verbose: bool | None = None,
    ):
        if verbose is None:
            verbose = self.verbose
        await self.sio.emit(
            "notification",
            {
                "content": content,
                "notification_type": notification_type.value,
                "duration": duration,
                "display_type": display_type.value,
            },
            to=client_id,
        )
        if verbose:
            if notification_type == NotificationType.NOTIF_SUCCESS:
                ASCIIColors.success(content)
            elif notification_type == NotificationType.NOTIF_INFO:
                ASCIIColors.info(content)
            elif notification_type == NotificationType.NOTIF_WARNING:
                ASCIIColors.warning(content)
            else:
                ASCIIColors.red(content)

    def sync_notify(
        self,
        content,
        notification_type: NotificationType = NotificationType.NOTIF_SUCCESS,
        duration: int = 4,
        client_id=None,
        display_type: NotificationDisplayType = NotificationDisplayType.TOAST,
        verbose: bool | None = None,
    ):
        if verbose is None:
            verbose = self.verbose
        self.schedule_task(
            self.sio.emit(
                "notification",
                {
                    "content": content,
                    "notification_type": notification_type.value,
                    "duration": duration,
                    "display_type": display_type.value,
                },
                to=client_id,
            )
        )
        
        if verbose:
            if notification_type == NotificationType.NOTIF_SUCCESS:
                ASCIIColors.success(content)
            elif notification_type == NotificationType.NOTIF_INFO:
                ASCIIColors.info(content)
            elif notification_type == NotificationType.NOTIF_WARNING:
                ASCIIColors.warning(content)
            else:
                ASCIIColors.red(content)
    async def refresh_files(self, client_id=None):
       await self.sio.emit("refresh_files", to=client_id)


    async def new_block(
        self,
        client_id,
        sender=None,
        content="",
        parameters=None,
        metadata=None,
        ui=None,
        message_type: MSG_OPERATION_TYPE = MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT,
        sender_type: SENDER_TYPES = SENDER_TYPES.SENDER_TYPES_AI,
        open=False,
    ):
        # like new_message but without adding the information to the database
        client = self.session.get_client(client_id)
        await self.sio.emit(
            "new_message",
            {
                "sender": sender,
                "message_type": message_type.value,
                "sender_type": sender_type.value,
                "content": content,
                "parameters": parameters,
                "metadata": metadata,
                "ui": ui,
                "id": 0,
                "parent_message_id": 0,
                "binding": self.binding.binding_folder_name,
                "model": self.model.model_name,
                "personality": self.personality.name,
                "created_at": client.discussion.current_message.created_at,
                "started_generating_at": client.discussion.current_message.started_generating_at,
                "finished_generating_at": client.discussion.current_message.finished_generating_at,
                "nb_tokens": client.discussion.current_message.nb_tokens,
                "open": open,
            },
            to=client_id,
        )
    

    async def send_refresh(self, client_id):
        client = self.session.get_client(client_id)
        await self.sio.emit(
            "update_message",
            {
                "sender": client.discussion.current_message.sender,
                "id": client.discussion.current_message.id,
                "content": client.discussion.current_message.content,
                "discussion_id": client.discussion.discussion_id,
                "operation_type": MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT.value,
                "message_type": client.discussion.current_message.message_type,
                "created_at": client.discussion.current_message.created_at,
                "started_generating_at": client.discussion.current_message.started_generating_at,
                "finished_generating_at": client.discussion.current_message.finished_generating_at,
                "nb_tokens": client.discussion.current_message.nb_tokens,
                "binding": self.binding.binding_folder_name,
                "model": self.model.model_name,
                "personality": self.personality.name,
            },
            to=client_id,
        )

    async def update_message(
        self,
        client_id,
        chunk,
        parameters=None,
        metadata=[],
        ui=None,
        operation_type: MSG_OPERATION_TYPE = None,
    ):
        client = self.session.get_client(client_id)
        client.discussion.current_message.finished_generating_at = (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        client.discussion.current_message.nb_tokens = self.nb_received_tokens
        mtdt = (
            json.dumps(metadata, indent=4)
            if metadata is not None and type(metadata) == list
            else metadata
        )

        if self.nb_received_tokens == 1:
            client.discussion.current_message.started_generating_at = (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            await self.update_message_step(
                client_id,
                "✍ generating ...",
                MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS,
            )

        await self.sio.emit(
            "update_message",
            {
                "sender": self.personality.name,
                "id": client.discussion.current_message.id,
                "content": chunk,
                "ui": client.discussion.current_message.ui if ui is None else ui,
                "discussion_id": client.discussion.discussion_id,
                "operation_type": (
                    operation_type.value
                    if operation_type is not None
                    else (
                        MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK.value
                        if self.nb_received_tokens > 1
                        else MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT.value
                    )
                ),
                "message_type": MSG_TYPE.MSG_TYPE_CONTENT.value,
                "created_at": client.discussion.current_message.created_at,
                "started_generating_at": client.discussion.current_message.started_generating_at,
                "finished_generating_at": client.discussion.current_message.finished_generating_at,
                "nb_tokens": client.discussion.current_message.nb_tokens,
                "parameters": parameters,
                "metadata": metadata,
                "binding": self.binding.binding_folder_name,
                "model": self.model.model_name,
                "personality": self.personality.name,
            },
            to=client_id,
        )
        
        if (
            operation_type
            and operation_type.value < MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_INFO.value
        ):
            client.discussion.update_message(
                client.generated_text,
                new_metadata=mtdt,
                new_ui=ui,
                started_generating_at=client.discussion.current_message.started_generating_at,
                nb_tokens=client.discussion.current_message.nb_tokens,
            )

    async def update_message_content(
        self,
        client_id,
        chunk,
        operation_type: MSG_OPERATION_TYPE = MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT,
        message_type: MSG_TYPE = None,
    ):
        client = self.session.get_client(client_id)
        client.discussion.current_message.finished_generating_at = (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        client.discussion.current_message.nb_tokens = self.nb_received_tokens

        if self.nb_received_tokens == 1:
            client.discussion.current_message.started_generating_at = (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

        await self.sio.emit(
            "update_message",
            {
                "sender": self.personality.name,
                "id": client.discussion.current_message.id,
                "content": chunk,
                "discussion_id": client.discussion.discussion_id,
                "operation_type": operation_type.value,
                "message_type": (
                    client.discussion.current_message.message_type
                    if message_type is None
                    else message_type
                ),
                "created_at": client.discussion.current_message.created_at,
                "started_generating_at": client.discussion.current_message.started_generating_at,
                "finished_generating_at": client.discussion.current_message.finished_generating_at,
                "nb_tokens": client.discussion.current_message.nb_tokens,
                "binding": self.binding.binding_folder_name,
                "model": self.model.model_name,
                "personality": self.personality.name,
            },
            to=client_id,
        
        )

        client.discussion.update_message_content(
            client.generated_text,
            started_generating_at=client.discussion.current_message.started_generating_at,
            nb_tokens=client.discussion.current_message.nb_tokens,
        )

    async def update_message_step(
        self, client_id, step_text, msg_operation_type: MSG_OPERATION_TYPE = None
    ):
        client = self.session.get_client(client_id)
        if msg_operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP:
            client.discussion.current_message.add_step(step_text, "instant", True, True)
        elif msg_operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_START:
            client.discussion.current_message.add_step(
                step_text, "start_end", True, False
            )
        elif (
            msg_operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS
        ):
            client.discussion.current_message.add_step(
                step_text, "start_end", True, True
            )
        elif (
            msg_operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_FAILURE
        ):
            client.discussion.current_message.add_step(
                step_text, "start_end", False, True
            )

        await self.sio.emit(
            "update_message",
            {
                "id": client.discussion.current_message.id,
                "discussion_id": client.discussion.discussion_id,
                "operation_type": msg_operation_type.value,
                "steps": client.discussion.current_message.steps,
            },
            to=client_id,
        )

    async def update_message_metadata(self, client_id, metadata):
        client = self.session.get_client(client_id)
        md = (
            json.dumps(metadata)
            if type(metadata) == dict or type(metadata) == list
            else metadata
        )
        await self.sio.emit(
            "update_message",
            {
                "sender": self.personality.name,
                "id": client.discussion.current_message.id,
                "metadata": md,
                "discussion_id": client.discussion.discussion_id,
                "operation_type": MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_JSON_INFOS.value,
            },
            to=client_id,
        )
    
        client.discussion.update_message_metadata(metadata)

    async def update_message_ui(self, client_id, ui):
        client = self.session.get_client(client_id)

        await self.sio.emit(
            "update_message",
            {
                "sender": self.personality.name,
                "id": client.discussion.current_message.id,
                "ui": ui,
                "discussion_id": client.discussion.discussion_id,
                "operation_type": MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI.value,
            },
            to=client_id,
        
        )

        client.discussion.update_message_ui(ui)

    async def close_message(self, client_id, fix_content= False):
        client = self.session.get_client(client_id)
        for msg in client.discussion.messages:
            if msg.steps is not None:
                for step in msg.steps:
                    step["done"] = True
        if not client.discussion:
            return
        
        if fix_content:

            # fix halucination
            if len(client.generated_text) > 0 and len(self.start_header_id_template) > 0:
                client.generated_text = client.generated_text.split(
                    f"{self.start_header_id_template}"
                )[0]
            # Send final message
            client.discussion.current_message.finished_generating_at = (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            try:
                client.discussion.current_message.nb_tokens = self.model.count_tokens(client.generated_text)
            except:
                client.discussion.current_message.nb_tokens = None
            # client.discussion.current_message.update()
            await self.sio.emit(
                "close_message",
                {
                    "sender": self.personality.name,
                    "id": client.discussion.current_message.id,
                    "discussion_id": client.discussion.discussion_id,
                    "content": client.generated_text,
                    "binding": self.binding.binding_folder_name,
                    "model": self.model.model_name,
                    "personality": self.personality.name,
                    "created_at": client.discussion.current_message.created_at,
                    "started_generating_at": client.discussion.current_message.started_generating_at,
                    "finished_generating_at": client.discussion.current_message.finished_generating_at,
                    "nb_tokens": client.discussion.current_message.nb_tokens,
                },
                to=client_id,
            )
        else:
            # client.discussion.current_message.update_db()
            await self.sio.emit(
                "close_message",
                {
                    "sender": self.personality.name,
                    "id": client.discussion.current_message.id,
                    "discussion_id": client.discussion.discussion_id,
                    "binding": self.binding.binding_folder_name,
                    "model": self.model.model_name,
                    "personality": self.personality.name,
                    "created_at": client.discussion.current_message.created_at,
                    "started_generating_at": client.discussion.current_message.started_generating_at,
                    "finished_generating_at": client.discussion.current_message.finished_generating_at,
                    "nb_tokens": client.discussion.current_message.nb_tokens,
                },
                to=client_id,
            )

    def prepare_reception(self, client_id):
        if not self.session.get_client(client_id).continuing:
            self.session.get_client(client_id).generated_text = ""
            
        self.session.get_client(client_id).first_chunk=True
            
        self.nb_received_tokens = 0
        self.start_time = datetime.now()

    def generate(self, context_details:LollmsContextDetails, is_continue:bool, message_id:int, client_id:str, callback=None, force_using_internet:bool=False, generation_type="default"):
        full_prompt, tokens = self.personality.build_context(
            context_details, is_continue, True
        )
        n_predict = self.personality.compute_n_predict(tokens)
        if self.config.debug and self.config.debug_show_final_full_prompt:
            ASCIIColors.highlight(
                full_prompt,
                [
                    r
                    for r in [
                        self.config.discussion_prompt_separator,
                        self.config.start_header_id_template,
                        self.config.end_header_id_template,
                        self.config.separator_template,
                        self.config.start_user_header_id_template,
                        self.config.end_user_header_id_template,
                        self.config.end_user_message_id_template,
                        self.config.start_ai_header_id_template,
                        self.config.end_ai_header_id_template,
                        self.config.end_ai_message_id_template,
                        self.config.system_message_template,
                    ]
                    if r != "" and r != "\n"
                ],
            )

        if self.config.use_smart_routing:
            if (
                self.config.smart_routing_router_model != ""
                and len(self.config.smart_routing_models_description) >= 2
            ):
                ASCIIColors.yellow("Using smart routing")
                self.personality.step_start("Routing request")
                self.back_model = (
                    f"{self.binding.binding_folder_name}::{self.model.model_name}"
                )
                try:
                    if not hasattr(self, "routing_model") or self.routing_model is None:
                        binding, model_name = self.model_path_to_binding_model(
                            self.config.smart_routing_router_model
                        )
                        self.select_model(binding, model_name)
                        self.routing_model = self.model
                    else:
                        self.set_active_model(self.routing_model)

                    models = [
                        f"{k}"
                        for k, v in self.config.smart_routing_models_description.items()
                    ]
                    
                    code = self.personality.generate_custom_code(
                        "\n".join([
                            self.system_full_header,
                        "Given the following list of models:"]+
                        [
                            f"{k}: {v}"
                            for k, v in self.config.smart_routing_models_description.items()
                        ]+[
                        "!@>prompt:" + context_details.prompt,
                        """Given the prompt, which model among the previous list is the most suited and why?

You must answer with json code placed inside the markdown code tag like this:
```json
{
    "choice_index": [an int representing the index of the choice made]
    "justification": "[Justify the choice]",
}
Make sure you fill all fields and to use the exact same keys as the template.
Don't forget encapsulate the code inside a markdown code tag. This is mandatory.

!@>assistant:"""
                        ]
                    ))

                    if code:
                        output_id = code["choice_index"]
                        explanation = code["justification"]
                        binding, model_name = self.model_path_to_binding_model(
                            models[output_id]
                        )
                        self.select_model(
                            binding, model_name, destroy_previous_model=False
                        )
                        self.personality.step_end("Routing request")
                        self.personality.step(f"Choice explanation: {explanation}")
                        self.personality.step(f"Selected {models[output_id]}")
                    else:
                        ASCIIColors.error(
                            "Model failed to find the most suited model for your request"
                        )
                        self.info(
                            "Model failed to find the most suited model for your request"
                        )
                        binding, model_name = self.model_path_to_binding_model(
                            models[0]
                        )
                        self.select_model(
                            binding, model_name, destroy_previous_model=False
                        )
                        self.personality.step_end("Routing request")
                        self.personality.step(f"Complexity level: {output_id}")
                        self.personality.step(f"Selected {models[output_id]}")
                except Exception as ex:
                    self.error("Failed to route beceause of this error : " + str(ex))
                    self.personality.step_end("Routing request", False)
            else:
                ASCIIColors.yellow(
                    "Warning! Smart routing is active but one of the following requirements are not met"
                )
                ASCIIColors.yellow("- smart_routing_router_model must be set correctly")
                ASCIIColors.yellow(
                    "- smart_routing_models_description must contain at least one model"
                )

        if self.personality.processor is not None:
            ASCIIColors.info("Running workflow")
            try:
                self.personality.callback = callback
                client = self.session.get_client(client_id)
                self.personality.vectorizer = client.discussion.vectorizer
                self.personality.text_files = client.discussion.text_files
                self.personality.image_files = client.discussion.image_files
                self.personality.audio_files = client.discussion.audio_files
                output = self.personality.processor.run_workflow(
                    context_details, client, callback
                )
            except Exception as ex:
                trace_exception(ex)
                if callback:
                    callback(
                        f"Workflow run failed\nError:{ex}",
                        MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_EXCEPTION,
                    )
                return
            print("Finished executing the workflow")
            return output

        txt = self._generate(full_prompt, n_predict, client_id, callback)
        ASCIIColors.success("\nFinished executing the generation")

        if (
            self.config.use_smart_routing
            and self.config.restore_model_after_smart_routing
        ):
            if (
                self.config.smart_routing_router_model != ""
                and len(self.config.smart_routing_models_description) >= 2
            ):
                ASCIIColors.yellow("Restoring model")
                self.personality.step_start("Restoring main model")
                binding, model_name = self.model_path_to_binding_model(self.back_model)
                self.select_model(binding, model_name)
                self.personality.step_end("Restoring main model")

        try:
            if len(context_details.function_calls)>0:
                for function_call in context_details.function_calls:
                    fc:FunctionCall = function_call["class"]
                    if fc.function_type == FunctionType.CONTEXT_UPDATE:
                        process_output = fc.process_output(context_details, txt)
                        self.set_message_content(process_output,client_id=client_id)
                                    
        except Exception as ex:
            trace_exception(ex)

        if (
            self.tts
            and self.config.auto_read
            and len(self.personality.audio_samples) > 0
        ):
            try:
                self.process_data(
                    "Generating voice output",
                    MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_START,
                    client_id=client_id,
                )
                if self.tts.ready:
                    language = convert_language_name(
                        self.personality.language
                    )
                    fn = (
                        self.personality.name.lower()
                        .replace(" ", "_")
                        .replace(".", "")
                    )
                    fn = f"{fn}_{message_id}.wav"
                    url = f"audio/{fn}"
                    self.tts.tts_file(
                        client.generated_text,
                        Path(self.personality.audio_samples[0]).name,
                        f"{fn}",
                        language=language,
                    )
                    fl = f"\n".join(
                        [
                            f"<audio controls>",
                            f'    <source src="{url}" type="audio/wav">',
                            f"    Your browser does not support the audio element.",
                            f"</audio>",
                        ]
                    )
                    self.process_data(
                        "Generating voice output",
                        operation_type=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS,
                        client_id=client_id,
                    )
                    self.process_data(
                        fl,
                        MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI,
                        client_id=client_id,
                    )
                else:
                    self.InfoMessage(
                        "xtts is not up yet.\nPlease wait for it to load then try again. This may take some time."
                    )

            except Exception as ex:
                ASCIIColors.error("Couldn't read")
                trace_exception(ex)
        print()
        ASCIIColors.success("## Done Generation ##")
        print()

        if len(context_details.documentation_entries) > 0:
            sources_text += '<div class="text-gray-400 mr-10px flex items-center gap-2"><i class="fas fa-book"></i>Sources:</div>'
            sources_text += '<div class="mt-4 flex flex-col items-start gap-x-2 gap-y-1.5 text-sm">'
            for source in context_details.documentation_entries:
                title = source["document_title"]
                path = source["document_path"]
                content = source["chunk_content"]
                size = source["chunk_size"]
                similarity = source["similarity"]
                sources_text += f"""
                    <div class="source-item w-full">
                        <div class="flex items-center gap-2 p-2 bg-gray-100 rounded cursor-pointer hover:bg-gray-200" 
                            onclick="document.getElementById('source-details-{title}-{message_id}').classList.toggle('hidden')">
                            <i class="fas fa-file-alt"></i>
                            <span class="font-bold">{title}</span>
                            <span class="text-gray-500 ml-2">({similarity*100:.2f}%)</span>
                            <i class="fas fa-chevron-down ml-auto"></i>
                        </div>
                        <div id="source-details-{title}-{message_id}" class="hidden p-3 border-l-2 ml-6">
                            <p class="mb-2"><i class="fas fa-folder-open mr-2"></i>{path}</p>
                            <p class="mb-2 whitespace-pre-wrap">{content}</p>
                            <p class="text-sm text-gray-500">Size: {size}</p>
                        </div>
                    </div>
                """
            sources_text += "</div>"
            self.personality.set_message_html(sources_text)

        if len(context_details.skills) > 0:
            sources_text += '<div class="text-gray-400 mr-10px flex items-center gap-2"><i class="fas fa-brain"></i>Memories:</div>'
            sources_text += '<div class="mt-4 w-full flex flex-col items-start gap-x-2 gap-y-1.5 text-sm">'
            for ind, skill in enumerate(context_details.skills):
                sources_text += f"""
                    <div class="source-item w-full">
                        <div class="flex items-center gap-2 p-2 bg-gray-100 rounded cursor-pointer hover:bg-gray-200"
                            onclick="document.getElementById('source-details-{ind}-{message_id}').classList.toggle('hidden')">
                            <i class="fas fa-lightbulb"></i>
                            <span class="font-bold">Memory {ind}: {skill['title']}</span>
                            <span class="text-gray-500 ml-2">({skill['similarity']*100:.2f}%)</span>
                            <i class="fas fa-chevron-down ml-auto"></i>
                        </div>
                        <div id="source-details-{ind}-{message_id}" class="hidden p-3 border-l-2 ml-6">
                            <pre class="whitespace-pre-wrap">{skill['content']}</pre>
                        </div>
                    </div>
                """
            sources_text += "</div>"
            self.personality.set_message_html(sources_text)

        # Send final message
        if (
            self.config.activate_internet_search
            or force_using_internet
            or generation_type == "full_context_with_internet"
        ):
            from lollms.internet import get_favicon_url, get_root_url

            sources_text += """
            <div class="mt-4 text-sm">
                <div class="text-gray-500 font-semibold mb-2">Sources:</div>
                <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 h-64 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
            """

            for source in context_details.internet_search_infos:
                url = source["url"]
                title = source["title"]
                brief = source["brief"]
                favicon_url = (
                    get_favicon_url(url)
                    or "/personalities/generic/lollms/assets/logo.png"
                )
                root_url = get_root_url(url)

                sources_text += f"""
                <div class="relative flex flex-col items-start gap-2 rounded-lg border border-gray-200 bg-white p-3 shadow-sm transition duration-200 ease-in-out transform hover:scale-105 hover:border-gray-300 hover:shadow-lg dark:border-gray-700 dark:bg-gray-800 dark:hover:border-gray-600 dark:hover:shadow-lg animate-fade-in">
                    <a class="flex items-center w-full" target="_blank" href="{url}" title="{brief}">
                        <img class="h-8 w-8 rounded-full" src="{favicon_url}" alt="{title}" onerror="this.onerror=null;this.src='/personalities/generic/lollms/assets/logo.png';">
                        <div class="ml-2">
                            <div class="text-gray-700 dark:text-gray-300 font-semibold text-sm">{title}</div>
                            <div class="text-gray-500 dark:text-gray-400 text-xs">{root_url}</div>
                            <div class="text-gray-400 dark:text-gray-500 text-xs">{brief}</div>
                        </div>
                    </a>
                </div>
                """

            sources_text += """
                </div>
            </div>
            """

            # Add CSS for animations and scrollbar styles
            sources_text += """
            <style>
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .animate-fade-in {
                animation: fadeIn 0.5s ease-in-out;
            }
            .scrollbar-thin::-webkit-scrollbar {
                width: 8px;
            }
            .scrollbar-thin::-webkit-scrollbar-thumb {
                background-color: #cbd5e1; /* Tailwind gray-300 */
                border-radius: 10px;
            }
            .scrollbar-thin::-webkit-scrollbar-track {
                background: #f9fafb; /* Tailwind gray-100 */
            }
            </style>
            """
            self.personality.set_message_html(sources_text)
        try:
            self.personality.step_end(
                "🔥 warming up ..."
            )
            self.personality.step_end(
                "✍ generating ..."
            )
        except Exception as ex:
            ASCIIColors.warning("Couldn't send status update to client")            


        try:
            final_ui_update =""
            final_text_update = ""
            if len(context_details.function_calls)>0:
                codes = self.personality.extract_code_blocks(txt)
                for function_call in context_details.function_calls:
                    fc:FunctionCall = function_call["class"]
                    for code in codes:
                        if code["type"]=="function":
                            infos = json.loads(code["content"])
                            if infos["function_name"]==function_call["name"]:
                                if fc.function_type == FunctionType.CLASSIC:
                                    context_details.ai_output = txt
                                    output = fc.execute(context_details,**infos["function_parameters"])
                                    if output:
                                        if output[0]=="<":
                                            final_ui_update+=output+"\n"
                                        else:
                                            final_text_update+=output+"\n"
            if final_ui_update or final_text_update:
                self.personality.new_message(final_text_update)
                self.personality.set_message_content(final_text_update)
            if final_ui_update:
                self.personality.set_message_html(final_ui_update)
                                    
        except Exception as ex:
            trace_exception(ex)

        return txt

    def _generate(self, prompt, n_predict, client_id, callback=None):
        client = self.session.get_client(client_id)
        if client is None:
            return None
        self.nb_received_tokens = 0
        self.start_time = datetime.now()
        if self.model is not None:
            if (
                self.model.binding_type == BindingType.TEXT_IMAGE
                and len(client.discussion.image_files) > 0
            ):
                if self.config["override_personality_model_parameters"]:
                    output = self.model.generate_with_images(
                        prompt,
                        client.discussion.image_files,
                        callback=callback,
                        n_predict=int(n_predict),
                        temperature=float(self.config["temperature"]),
                        top_k=int(self.config["top_k"]),
                        top_p=float(self.config["top_p"]),
                        repeat_penalty=float(self.config["repeat_penalty"]),
                        repeat_last_n=int(self.config["repeat_last_n"]),
                        seed=int(self.config["seed"]),
                        n_threads=int(self.config["n_threads"]),
                    )
                else:
                    prompt = "\n".join(
                        [
                            f"{self.system_full_header}I am an AI assistant that can converse and analyze images. When asked to locate something in an image you send, I will reply with:",
                            "boundingbox(image_index, label, left, top, width, height)",
                            "Where:",
                            "image_index: 0-based index of the image",
                            "label: brief description of what is located",
                            "left, top: x,y coordinates of top-left box corner (0-1 scale)",
                            "width, height: box dimensions as fraction of image size",
                            "Coordinates have origin (0,0) at top-left, (1,1) at bottom-right.",
                            "For other queries, I will respond conversationally to the best of my abilities.",
                            prompt,
                        ]
                    )
                    output = self.model.generate_with_images(
                        prompt,
                        client.discussion.image_files,
                        callback=callback,
                        n_predict=n_predict,
                        temperature=self.personality.model_temperature,
                        top_k=self.personality.model_top_k,
                        top_p=self.personality.model_top_p,
                        repeat_penalty=self.personality.model_repeat_penalty,
                        repeat_last_n=self.personality.model_repeat_last_n,
                        seed=self.config["seed"],
                        n_threads=self.config["n_threads"],
                    )
                    try:
                        post_processed_output = process_ai_output(
                            output,
                            client.discussion.image_files,
                            client.discussion.discussion_folder,
                        )
                        if len(post_processed_output) != output:
                            self.process_data(
                                post_processed_output,
                                MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT,
                                client_id=client_id,
                            )
                    except Exception as ex:
                        ASCIIColors.error(str(ex))
            else:
                if self.config["override_personality_model_parameters"]:
                    output = self.model.generate(
                        prompt,
                        callback=callback,
                        n_predict=n_predict,
                        temperature=float(self.config["temperature"]),
                        top_k=int(self.config["top_k"]),
                        top_p=float(self.config["top_p"]),
                        repeat_penalty=float(self.config["repeat_penalty"]),
                        repeat_last_n=int(self.config["repeat_last_n"]),
                        seed=int(self.config["seed"]),
                        n_threads=int(self.config["n_threads"]),
                    )
                else:
                    output = self.model.generate(
                        prompt,
                        callback=callback,
                        n_predict=n_predict,
                        temperature=self.personality.model_temperature,
                        top_k=self.personality.model_top_k,
                        top_p=self.personality.model_top_p,
                        repeat_penalty=self.personality.model_repeat_penalty,
                        repeat_last_n=self.personality.model_repeat_last_n,
                        seed=self.config["seed"],
                        n_threads=self.config["n_threads"],
                    )
        else:
            print(
                "No model is installed or selected. Please make sure to install a model and select it inside your configuration before attempting to communicate with the model."
            )
            print("To do this: Install the model to your models/<binding name> folder.")
            print(
                "Then set your model information in your local configuration file that you can find in configs/local_config.yaml"
            )
            print("You can also use the ui to set your model in the settings page.")
            output = ""
        return output
            
    async def start_message_generation(
        self,
        message,
        message_id,
        client_id,
        is_continue=False,
        generation_type=None,
        force_using_internet=False,
    ):
        client = self.session.get_client(client_id)
        if self.personality is None:
            self.warning("Select a personality")
            return
        ASCIIColors.info(f"Text generation requested by client: {client_id}")
        # send the message to the bot
        if client.discussion:
            try:
                ASCIIColors.info(
                    f"Received message : {message.content} ({self.model.count_tokens(message.content)})"
                )
                # First we need to send the new message ID to the client
                if is_continue:
                    client.discussion.load_message(message_id)
                    client.generated_text = message.content
                else:
                    await self.send_refresh(client_id)
                    await self.update_message_step(
                        client_id,
                        "🔥 warming up ...",
                        MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_START,
                    )

                # prepare query and reception
                context_details = self.prepare_query(
                    client_id,
                    message_id,
                    is_continue,
                    n_tokens=self.config.min_n_predict,
                    generation_type=generation_type,
                    force_using_internet=force_using_internet,
                    previous_chunk=client.generated_text if is_continue else "",
                )
                EMOJI_YES = "✅"
                EMOJI_NO = "❌" 
                ASCIIColors.multicolor(
                    texts=[
                        "🚀 Generation Options:\n",
                        "• Fun Mode: ",
                        f"{EMOJI_YES if context_details.fun_mode else EMOJI_NO}",
                        "\n",
                        "• Think First Mode: ",
                        f"{EMOJI_YES if context_details.think_first_mode else EMOJI_NO}",
                        "\n",
                        "• Continuation: ",
                        f"{EMOJI_YES if context_details.is_continue else EMOJI_NO}",
                        "\n",
                        "🎮 Generating up to ",
                        f"{min(context_details.available_space, self.config.max_n_predict)}",
                        " tokens...",
                        "\n",
                        "Available context space: ",
                        f"{context_details.available_space}",
                        "\n",
                        "Prompt tokens used: ",
                        f"{self.config.ctx_size - context_details.available_space}",
                        "\n",
                        "Max tokens allowed: ",
                        f"{self.config.max_n_predict}",
                        "\n",
                        "⚡ Powered by LoLLMs"
                    ],
                    colors=[
                        ASCIIColors.color_bright_cyan,
                        ASCIIColors.color_bright_green,
                        ASCIIColors.color_bright_green,
                        ASCIIColors.color_reset,
                        ASCIIColors.color_bright_cyan,
                        ASCIIColors.color_bright_green,
                        ASCIIColors.color_bright_green,
                        ASCIIColors.color_reset,
                        ASCIIColors.color_bright_cyan,
                        ASCIIColors.color_bright_green,
                        ASCIIColors.color_bright_green,
                        ASCIIColors.color_reset,
                        ASCIIColors.color_bright_blue,
                        ASCIIColors.color_bright_green,
                        ASCIIColors.color_bright_green,
                        ASCIIColors.color_reset,
                        ASCIIColors.color_bright_yellow,
                        ASCIIColors.color_bright_green,
                        ASCIIColors.color_bright_green,
                        ASCIIColors.color_reset,
                        ASCIIColors.color_bright_magenta,
                        ASCIIColors.color_bright_blue,
                        ASCIIColors.color_reset,
                        ASCIIColors.color_bright_magenta
                    ],
                    end="\n",
                    flush=True
                )

                self.prepare_reception(client_id)
                self.generating = True
                client.processing = True
                try:
                    self.loop = asyncio.get_running_loop() # Get loop in the main async thread
                    ASCIIColors.magenta(f"Starting library process (threaded), loop acquired: {self.loop}")

                    client.generation_routine = self.loop.run_in_executor(
                        None, # Use default ThreadPoolExecutor
                        partial(self.generate, # The potentially blocking function
                        context_details,
                        message_id=message_id,
                        client_id=client_id,
                        is_continue=is_continue,
                        callback=partial(self.process_data, client_id=client_id),
                        force_using_internet=force_using_internet,
                        generation_type=generation_type
                        ),
                    )
                    await client.generation_routine
                    ASCIIColors.yellow("Closing message")
                    await self.close_message(client_id, True)
                except Exception as ex:
                    trace_exception(ex)
                    print()
                    ASCIIColors.error("## Generation Error ##")
                    print()

                self.cancel_gen = False
                sources_text = ""

            except Exception as ex:
                trace_exception(ex)
                try:
                    await self.update_message_step(
                        client_id,
                        "🔥 warming up ...",
                        MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS,
                    )
                    await self.update_message_step(
                        client_id,
                        "✍ generating ...",
                        MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_FAILURE,
                    )
                except Exception as ex:
                    ASCIIColors.warning("Couldn't send status update to client")

            finally:
                self.busy = False
                self.cancel_gen = False

            client.processing = False


            ASCIIColors.multicolor(
                texts=[
                f" ╔══════════════════════════════════════════════════╗\n",
                f" ║","                        Done                      ","║\n",
                f" ╚══════════════════════════════════════════════════╝\n",
                ],
                colors=[
                    ASCIIColors.color_bright_cyan,
                    ASCIIColors.color_bright_cyan,ASCIIColors.color_bright_green,ASCIIColors.color_bright_cyan,
                    ASCIIColors.color_bright_cyan,
                ]
            )
            

            if self.config.auto_title:
                d = client.discussion
                ttl = d.title()
                if ttl is None or ttl == "" or ttl == "untitled":
                    title = self.make_discussion_title(d, client_id=client_id)
                    d.rename(title)
                    await self.sio.emit(
                        "disucssion_renamed",
                        {
                            "status": True,
                            "discussion_id": d.discussion_id,
                            "title": title,
                        },
                        to=client_id,
                    )
            await self.close_message(client_id)
            
        else:
            self.cancel_gen = False
            # No discussion available
            ASCIIColors.warning("No discussion selected!!!")

            self.error("No discussion selected!!!", client_id=client_id)
            await self.close_message(client_id)

            return ""

    def make_discussion_title(self, discussion, client_id=None):
        """
        Builds a title for a discussion
        """

        # Get the list of messages
        messages = discussion.get_messages()
        discussion_messages = f"{self.system_full_header}Create a short title to this discussion\n--- discussion ---\n"
        discussion_title = f"\n{self.ai_custom_header('assistant')}"

        available_space = (
            self.config.ctx_size
            - 150
            - self.model.count_tokens(discussion_messages)
            - self.model.count_tokens(discussion_title)
        )
        # Initialize a list to store the full messages
        full_message_list = []
        # Accumulate messages until the cumulative number of tokens exceeds available_space
        tokens_accumulated = 0
        # Accumulate messages starting from message_index
        for message in messages:
            # Check if the message content is not empty and visible to the AI
            if message.content != "" and (
                message.message_type
                <= MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_USER.value
                and message.message_type
                != MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI.value
            ):

                # Tokenize the message content
                message_tokenized = self.model.tokenize(
                    "\n"
                    + self.config.discussion_prompt_separator
                    + message.sender
                    + ": "
                    + message.content.strip()
                )

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
        discussion_messages +"\n--- ---\n"
        discussion_messages +f"\n{self.user_custom_header('user')}Your response should only contain the title without any comments or thoughts.\n"
        discussion_messages += discussion_title
        title = [""]

        def receive(chunk: str, message_type: MSG_OPERATION_TYPE):
            if chunk:
                title[0] += chunk
            antiprompt = self.personality.detect_antiprompt(title[0])
            if antiprompt:
                ASCIIColors.warning(f"\n{antiprompt} detected. Stopping generation")
                title[0] = self.remove_text_from_string(title[0], antiprompt)
                return False
            else:
                return True

        self._generate(discussion_messages, 1024, client_id, receive)
        title[0] = self.personality.remove_thinking_blocks(title[0])
        ASCIIColors.info(f"TITLE:{title[0]}")
        return title[0]
    def rebuild_personalities(self, reload_all=False):
        if reload_all:
            self.mounted_personalities = []

        loaded = self.mounted_personalities
        loaded_names = [
            f"{p.category}/{p.personality_folder_name}" for p in loaded if p is not None
        ]
        mounted_personalities = []
        ASCIIColors.success(f" ╔══════════════════════════════════════════════════╗ ")
        ASCIIColors.success(f" ║           Building mounted Personalities         ║ ")
        ASCIIColors.success(f" ╚══════════════════════════════════════════════════╝ ")
        to_remove = []
        for i, personality in enumerate(self.config["personalities"]):
            if i == self.config["active_personality_id"]:
                ASCIIColors.red("*", end="")
                ASCIIColors.green(f" {personality}")
            else:
                ASCIIColors.yellow(f" {personality}")
            if personality in loaded_names:
                mounted_personalities.append(loaded[loaded_names.index(personality)])
            else:
                personality_path = f"{personality}"
                try:
                    personality = AIPersonality(
                        personality_path,
                        self.lollms_paths,
                        self.config,
                        model=self.model,
                        app=self,
                        selected_language=self.config.current_language,
                        run_scripts=True,
                    )

                    mounted_personalities.append(personality)
                    if self.config.auto_read and len(personality.audio_samples) > 0:
                        pass # self.tts
                except Exception as ex:
                    trace_exception(ex)
                    ASCIIColors.error(
                        f"Personality file not found or is corrupted ({personality_path}).\nReturned the following exception:{ex}\nPlease verify that the personality you have selected exists or select another personality. Some updates may lead to change in personality name or category, so check the personality selection in settings to be sure."
                    )
                    ASCIIColors.info("Trying to force reinstall")
                    if self.config["debug"]:
                        print(ex)
                    try:
                        personality = AIPersonality(
                            personality_path,
                            self.lollms_paths,
                            self.config,
                            self.model,
                            app=self,
                            run_scripts=True,
                            selected_language=self.config.current_language,
                            installation_option=InstallOption.FORCE_INSTALL,
                        )
                        mounted_personalities.append(personality)
                        if personality.processor:
                            personality.processor.mounted()
                    except Exception as ex:
                        ASCIIColors.error(
                            f"Couldn't load personality at {personality_path}"
                        )
                        trace_exception(ex)
                        ASCIIColors.info(f"Unmounting personality")
                        to_remove.append(i)
                        personality = AIPersonality(
                            None,
                            self.lollms_paths,
                            self.config,
                            self.model,
                            app=self,
                            run_scripts=True,
                            installation_option=InstallOption.FORCE_INSTALL,
                        )
                        mounted_personalities.append(personality)
                        if personality.processor:
                            personality.processor.mounted()

                        ASCIIColors.info("Reverted to default personality")
        if self.config["active_personality_id"] >= 0 and self.config[
            "active_personality_id"
        ] < len(self.config["personalities"]):
            ASCIIColors.success(
                f'selected model : {self.config["personalities"][self.config["active_personality_id"]]}'
            )
        else:
            ASCIIColors.warning(
                "An error was encountered while trying to mount personality"
            )
        ASCIIColors.multicolor(
            texts=[
            f" ╔══════════════════════════════════════════════════╗\n",
            f" ║","                        Done                      ","║\n",
            f" ╚══════════════════════════════════════════════════╝\n",
            ],
            colors=[
                ASCIIColors.color_bright_cyan,
                ASCIIColors.color_bright_cyan,ASCIIColors.color_bright_green,ASCIIColors.color_bright_cyan,
                ASCIIColors.color_bright_cyan,
            ]
        )
        # Sort the indices in descending order to ensure correct removal
        to_remove.sort(reverse=True)

        # Remove elements from the list based on the indices
        for index in to_remove:
            if 0 <= index < len(mounted_personalities):
                mounted_personalities.pop(index)
                self.config["personalities"].pop(index)
                ASCIIColors.info(f"removed personality {personality_path}")

        if self.config["active_personality_id"] >= len(self.config["personalities"]):
            self.config["active_personality_id"] = 0

        return mounted_personalities
    

    def set_message_content(
        self,
        full_text: str,
        callback: (
            Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]
            | None
        ) = None,
        client_id=0,
    ):
        """This sends full text to front end

        Args:
            step_text (dict): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the text to. Defaults to None.
        """
        if not callback:
            callback = partial(self.process_data, client_id=client_id)

        if callback:
            callback(full_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT)



    def process_data(
        self,
        data: str | list | None,
        operation_type: MSG_OPERATION_TYPE,
        client_id: str = 0,
        personality: AIPersonality = None, # Passed by the library caller if needed
    ):
        """
        Processes data from the synchronous library and schedules async updates.
        This function itself MUST remain synchronous.
        Assumes self.loop is set and we are in the event loop's thread (Scenario A).
        """
        if not self.loop:
            print("ERROR: Event loop not set in process_data callback!")
            # Or raise an exception, depending on your error handling strategy
            return False # Indicate failure if possible




        # Use the passed personality or the default one
        current_personality = personality if personality is not None else self.personality
        if current_personality is None:
             print(f"WARNING: No personality available for client {client_id}")
             # Handle error appropriately - maybe schedule an error emit
             self.schedule_task(self.error(f"Configuration error: Personality not found for operation {operation_type}", client_id=client_id))
             return False # Stop processing if personality is required


        client = self.session.get_client(client_id)
        if client is None:
            print(f"ERROR: Client {client_id} not found in session.")
            # Schedule an error emit if appropriate
            self.error(f"Client {client_id} session error", client_id=client_id)
            return False # Stop if client is essential


        if data is None and operation_type in [
            MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT,
            MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK,
        ]:
            return True # Or False depending on library expectation

        # --- Process different operation types ---

        if operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP:
            ASCIIColors.info("--> Step:" + str(data))
            # Schedule the async update
            self.schedule_task(self.update_message_step(client_id, data, operation_type))

        elif operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_START:
            ASCIIColors.info("--> Step started:" + str(data))
            self.schedule_task(self.update_message_step(client_id, data, operation_type))

        elif operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS:
            ASCIIColors.success("--> Step ended:" + str(data))
            self.schedule_task(self.update_message_step(client_id, data, operation_type))

        elif operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_FAILURE:
            ASCIIColors.error("--> Step ended (Failure):" + str(data)) # Use error color
            self.schedule_task(self.update_message_step(client_id, data, operation_type))

        elif operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_WARNING:
            ASCIIColors.warning("--> Warning from personality:" + str(data)) # Use warning color
            self.warning(data, client_id=client_id)

        elif operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_EXCEPTION:
            ASCIIColors.error("--> Exception from personality:" + str(data))
            self.error(data, client_id=client_id)
            # Decide if the library expects True/False after an exception
            return False # Often indicates stop

        elif operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_INFO:
            ASCIIColors.info("--> Info:" + str(data))
            # Assuming self.info is async? If not, call directly. If async, schedule.
            # If self.info just logs locally, it might be sync: self.info(...)
            # If it emits to client, it's async:
            self.info(data, client_id=client_id)
            # return True # Don't stop processing on info

        elif operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI:
            ASCIIColors.info("--> UI Update:" + str(data))
            self.schedule_task(self.update_message_ui(client_id, data))
            # return True

        elif operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_JSON_INFOS:
            ASCIIColors.info("--> JSON Infos:" + str(data))
            self.schedule_task(self.update_message_metadata(client_id, data))
            # return True

        elif operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_NEW_MESSAGE:
            ASCIIColors.info("--> Building new message")
            self.nb_received_tokens = 0
            self.start_time = datetime.now()
            # Schedule multiple tasks
            self.schedule_task(
                self.update_message_step(
                    client_id,
                    "🔥 warming up ...",
                    MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS, # Reuse type for status
                )
            )
            self.schedule_task(
                self.update_message_step(
                    client_id,
                    "✍ generating ...",
                    MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS, # Reuse type for status
                )
            )
            self.schedule_task(
                self.new_message(
                    client_id,
                    current_personality.name,
                    data, # Assuming data might contain initial context for new message
                    message_type=MSG_TYPE.MSG_TYPE_CONTENT,
                )
            )
            # return True

        elif operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_FINISHED_MESSAGE:
            ASCIIColors.info("--> Finished message")
            # Assuming self.close_message is async? If sync, call directly.
            self.schedule_task(self.close_message(client_id))
            # return True # Indicate normal finish

        elif operation_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK:
            if not isinstance(data, str):
                 ASCIIColors.warning(f"Received non-string chunk: {type(data)}. Skipping.")
                 return True # Or False if this is an error condition

            if self.nb_received_tokens == 0:
                self.start_time = datetime.now()
                # Schedule status updates (fire and forget exceptions here)
                self.schedule_task(
                    self.update_message_step(
                        client_id, "🔥 warming up ...", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS
                    )
                )
                self.schedule_task(
                    self.update_message_step(
                        client_id, "✍ generating ...", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS
                    )
                )

            # Sync calculations
            dt = (datetime.now() - self.start_time).seconds if self.start_time else 1
            if dt <= 0: dt = 1
            spd = self.nb_received_tokens / dt
            if self.config.debug_show_chunks:
                print(data, end="", flush=True) # This is sync console output

            # Append data (sync)
            if data:
                client.generated_text += data

            # Detect antiprompt (sync - assuming detect_antiprompt is sync)
            antiprompt = current_personality.detect_antiprompt(client.generated_text)
            if antiprompt:
                ASCIIColors.warning(f"\n{antiprompt} detected. Stopping generation")
                # Modify text (sync)
                client.generated_text = self.remove_text_from_string(
                    client.generated_text, antiprompt
                )
                # Schedule final update (async)
                self.schedule_task(
                    self.update_message_content(
                        client_id,
                        client.generated_text,
                        MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT, # Send the final corrected content
                    )
                )
                return False # Signal to the library to stop (if applicable)
            else:
                # Increment token count (sync)
                self.nb_received_tokens += 1
                # Schedule content update (async)
                if client.continuing and client.first_chunk:
                     # This logic seems complex - ensure client state is managed correctly
                     self.schedule_task(
                         self.update_message_content(
                             client_id,
                             client.generated_text, # Send the whole text on first chunk if continuing
                             MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT,
                         )
                     )
                else:
                    self.schedule_task(
                        self.update_message_content(
                            client_id, data, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK
                        )
                    )

                # Update client state (sync)
                client.first_chunk = False

                # Check cancellation flag (sync)
                if not self.cancel_gen:
                    return True # Continue generation
                else:
                    self.cancel_gen = False # Reset flag
                    ASCIIColors.warning("Generation canceled")
                    # Optionally schedule a cancellation message
                    # self.schedule_task(self.info("Generation cancelled by user.", client_id=client_id))
                    return False # Stop generation

        elif operation_type in [
            MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT,
            MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI,
            MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_USER,
        ]:
            if not isinstance(data, str):
                 ASCIIColors.warning(f"Received non-string content: {type(data)}. Skipping.")
                 return True # Or False?

            if self.nb_received_tokens == 0: # First time seeing content?
                self.start_time = datetime.now()
                # Schedule status updates
                self.schedule_task(
                    self.update_message_step(
                        client_id, "🔥 warming up ...", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS
                    )
                )
                self.schedule_task(
                    self.update_message_step(
                        client_id, "✍ generating ...", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS
                    )
                )

            # Set content (sync)
            client.generated_text = data
            # Detect antiprompt (sync)
            antiprompt = current_personality.detect_antiprompt(client.generated_text)
            if antiprompt:
                ASCIIColors.warning(f"\n{antiprompt} detected. Stopping generation")
                client.generated_text = self.remove_text_from_string(
                    client.generated_text, antiprompt
                )
                # Schedule final update (async)
                self.schedule_task(
                    self.update_message_content(
                        client_id, client.generated_text, operation_type # Use original type? Or SET_CONTENT?
                    )
                )
                return False # Stop

            # Schedule normal content update (async)
            self.schedule_task(self.update_message_content(client_id, data, operation_type))
            return True # Continue normally

        # Fallback for potentially unknown types?
        else:
             ASCIIColors.warning(f"Unknown operation type encountered: {operation_type}")
             # Maybe schedule an error or info message
             # self.schedule_task(self.info(f"Received unknown operation: {operation_type}", client_id=client_id))


        return True # Default return, assuming we continue unless specified otherwise



    async def receive_and_generate(self, text, client: Client, callback=None):
        prompt = text
        try:
            nb_tokens = self.model.count_tokens(prompt)
        except:
            nb_tokens = None

        message = client.discussion.add_message(
            operation_type=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT.value,
            sender_type=SENDER_TYPES.SENDER_TYPES_USER.value,
            sender=(
                self.config.user_name.strip()
                if self.config.use_user_name_in_discussions
                else self.personality.user_message_prefix
            ),
            content=prompt,
            metadata=None,
            parent_message_id=self.message_id,
            nb_tokens=nb_tokens,
        )
        context_details = self.prepare_query(
            client.client_id,
            client.discussion.current_message.id,
            False,
            n_tokens=self.config.min_n_predict,
            force_using_internet=False,
        )
        await self.new_message(
            client.client_id,
            self.personality.name,
            operation_type=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT,
            content="",
        )
        client.generated_text = ""
        ASCIIColors.info(
            f"prompt has {self.config.ctx_size-context_details.available_space} tokens"
        )
        ASCIIColors.info(
            f"warmup for generating up to {min(context_details.available_space,self.config.max_n_predict if self.config.max_n_predict else self.config.ctx_size)} tokens"
        )
        self.current_generation_task = self.loop.run_in_executor(
            None, # Use default ThreadPoolExecutor
            partial(self.generate, # The potentially blocking function
            context_details,
            client_id=client.client_id,
            is_continue=False,
            callback=(
                callback
                if callback
                else partial(self.process_data, client_id=client.client_id)
            )
            ),
        )
        await self.current_generation_task
        await self.close_message(client.client_id)
        return client.generated_text


    async def default_callback(self, chunk, type, generation_infos:dict):
        if generation_infos["nb_received_tokens"]==0:
            self.start_time = datetime.now()
        dt =(datetime.now() - self.start_time).seconds
        if dt==0:
            dt=1
        spd = generation_infos["nb_received_tokens"]/dt
        ASCIIColors.green(f"Received {generation_infos['nb_received_tokens']} tokens (speed: {spd:.2f}t/s)              ",end="\r",flush=True) 
        sys.stdout = sys.__stdout__
        sys.stdout.flush()
        if chunk:
            generation_infos["generated_text"] += chunk
        antiprompt = self.personality.detect_antiprompt(generation_infos["generated_text"])
        if antiprompt:
            ASCIIColors.warning(f"\n{antiprompt} detected. Stopping generation")
            generation_infos["generated_text"] = self.remove_text_from_string(generation_infos["generated_text"],antiprompt)
            return False
        else:
            generation_infos["nb_received_tokens"] += 1
            generation_infos["first_chunk"]=False
            # if stop generation is detected then stop
            if not self.cancel_gen:
                return True
            else:
                self.cancel_gen = False
                ASCIIColors.warning("Generation canceled")
                return False
   
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

    def load_binding(self):
        try:
            binding = BindingBuilder().build_binding(self.config, self.lollms_paths, lollmsCom=self)
            return binding    
        except Exception as ex:
            self.error("Couldn't load binding")
            self.info("Trying to reinstall binding")
            trace_exception(ex)
            try:
                binding = BindingBuilder().build_binding(self.config, self.lollms_paths,installation_option=InstallOption.FORCE_INSTALL, lollmsCom=self)
            except Exception as ex:
                self.error("Couldn't reinstall binding")
                trace_exception(ex)
            return None    

    
    def load_model(self):
        try:
            model = ModelBuilder(self.binding).get_model()
            for personality in self.mounted_personalities:
                if personality is not None:
                    personality.model = model
        except Exception as ex:
            self.error("Couldn't load model.")
            ASCIIColors.error(f"Couldn't load model. Please verify your configuration file at {self.lollms_paths.personal_configuration_path} or use the next menu to select a valid model")
            ASCIIColors.error(f"Binding returned this exception : {ex}")
            trace_exception(ex)
            ASCIIColors.error(f"{self.config.get_model_path_infos()}")
            print("Please select a valid model or install a new one from a url")
            model = None

        return model



    def mount_personality(self, id:int, callback=None):
        try:
            personality = PersonalityBuilder(self.lollms_paths, self.config, self.model, self, callback=callback).build_personality(id)
            if personality.model is not None:
                try:
                    self.cond_tk = personality.model.tokenize(personality.personality_conditioning)
                    self.n_cond_tk = len(self.cond_tk)
                    ASCIIColors.success(f"Personality  {personality.name} mounted successfully")
                except:
                    self.cond_tk = []      
                    self.n_cond_tk = 0      
            else:
                ASCIIColors.success(f"Personality  {personality.name} mounted successfully but no model is selected")
        except Exception as ex:
            ASCIIColors.error(f"Couldn't load personality. Please verify your configuration file at {self.lollms_paths.personal_configuration_path} or use the next menu to select a valid personality")
            ASCIIColors.error(f"Binding returned this exception : {ex}")
            trace_exception(ex)
            ASCIIColors.error(f"{self.config.get_personality_path_infos()}")
            if id == self.config.active_personality_id:
                self.config.active_personality_id=len(self.config.personalities)-1
            personality = None
        
        self.mounted_personalities.append(personality)
        return personality
    
    def mount_personalities(self, callback = None):
        self.mounted_personalities = []
        to_remove = []
        for i in range(len(self.config["personalities"])):
            p = self.mount_personality(i, callback = None)
            if p is None:
                to_remove.append(i)
        to_remove.sort(reverse=True)
        for i in to_remove:
            self.unmount_personality(i)

        if self.config.active_personality_id>=0 and self.config.active_personality_id<len(self.mounted_personalities):
            self.personality = self.mounted_personalities[self.config.active_personality_id]
        else:
            self.config["personalities"].insert(0, "generic/lollms")
            self.mount_personality(0, callback = None)
            self.config.active_personality_id = 0
            self.personality = self.mounted_personalities[self.config.active_personality_id]


    def set_personalities_callbacks(self, callback: Callable[[str, int, dict], bool]=None):
        for personality in self.mount_personalities:
            personality.setCallback(callback)


            
    def unmount_personality(self, id:int)->bool:
        if id<len(self.config.personalities):
            del self.config.personalities[id]
            del self.mounted_personalities[id]
            if self.config.active_personality_id>=id:
                self.config.active_personality_id-=1

            self.config.save_config()
            return True
        else:
            return False


    def select_personality(self, id:int):
        if id<len(self.config.personalities):
            self.config.active_personality_id = id
            self.personality = self.mounted_personalities[id]
            self.config.save_config()
            return True
        else:
            return False


    def load_personality(self, callback=None):
        try:
            personality = PersonalityBuilder(self.lollms_paths, self.config, self.model, self, callback=callback).build_personality()
        except Exception as ex:
            ASCIIColors.error(f"Couldn't load personality. Please verify your configuration file at {self.configuration_path} or use the next menu to select a valid personality")
            ASCIIColors.error(f"Binding returned this exception : {ex}")
            ASCIIColors.error(f"{self.config.get_personality_path_infos()}")
            print("Please select a valid model or install a new one from a url")
            personality = None
        return personality

    @staticmethod   
    def reset_paths(lollms_paths:LollmsPaths):
        lollms_paths.resetPaths()

    @staticmethod   
    def reset_all_installs(lollms_paths:LollmsPaths):
        ASCIIColors.info("Removeing all configuration files to force reinstall")
        ASCIIColors.info(f"Searching files from {lollms_paths.personal_configuration_path}")
        for file_path in lollms_paths.personal_configuration_path.iterdir():
            if file_path.name!=f"{lollms_paths.tool_prefix}local_config.yaml" and file_path.suffix.lower()==".yaml":
                file_path.unlink()
                ASCIIColors.info(f"Deleted file: {file_path}")


    #languages:
    def get_personality_languages(self):
        languages = [self.personality.default_language]
        persona_language_path = self.lollms_paths.personalities_zoo_path/self.personality.category/self.personality.name.replace(" ","_")/"languages"
        for language_file in persona_language_path.glob("*.yaml"):
            language_code = language_file.stem
            languages.append(language_code)
        # Construire le chemin vers le dossier contenant les fichiers de langue pour la personnalité actuelle
        languages_dir = self.lollms_paths.personal_configuration_path / "personalities" / self.personality.name
        if self.personality.language:
            default_language = self.personality.language.lower().strip().split()[0]
        else:
            default_language = "english"
        # Vérifier si le dossier existe
        languages_dir.mkdir(parents=True, exist_ok=True)
        
        # Itérer sur chaque fichier YAML dans le dossier
        for language_file in languages_dir.glob("languages_*.yaml"):
            # Improved extraction of the language code to handle names with underscores
            parts = language_file.stem.split("_")
            if len(parts) > 2:
                language_code = "_".join(parts[1:])  # Rejoin all parts after "languages"
            else:
                language_code = parts[-1]
            
            if language_code != default_language and language_code not in languages:
                languages.append(language_code)
        
        return languages

    def set_personality_language(self, language:str):
        if language is None or  language == "":
            return False
        language = language.lower().strip().split()[0]
        self.personality.set_language(language)

        self.config.current_language=language
        self.config.save_config()
        return True

    def del_personality_language(self, language:str):
        if language is None or  language == "":
            return False
        
        language = language.lower().strip().split()[0]
        default_language = self.personality.language.lower().strip().split()[0]
        if language == default_language:
            return False # Can't remove the default language
                
        language_path = self.lollms_paths.personal_configuration_path/"personalities"/self.personality.name/f"languages_{language}.yaml"
        if language_path.exists():
            try:
                language_path.unlink()
            except Exception as ex:
                return False
            if self.config.current_language==language:
                self.config.current_language="english"
                self.config.save_config()
        return True

    def recover_discussion(self,client_id, message_index=-1):
        messages = self.session.get_client(client_id).discussion.get_messages()
        discussion=""
        for msg in messages[:-1]:
            if message_index!=-1 and msg>message_index:
                break
            discussion += "\n" + self.config.discussion_prompt_separator + msg.sender + ": " + msg.content.strip()
        return discussion
    # -------------------------------------- Prompt preparing
    def prepare_query(self, client_id: str, message_id: int = -1, is_continue: bool = False, n_tokens: int = 0, generation_type = None, force_using_internet=False, previous_chunk="") -> LollmsContextDetails:
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
        skills_detials=[]
        skills = []
        documentation_entries = []

        if self.personality.callback is None:
            self.personality.callback = partial(self.process_data, client_id=client_id)
        # Get the list of messages
        client = self.session.get_client(client_id)
        discussion = client.discussion
        messages = discussion.get_messages()

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

        block_rag = False
        function_calls = []
        if len(self.config.mounted_function_calls)>0:            
            for fc in self.config.mounted_function_calls:
                if fc["selected"]:
                    fci = self.load_function_call(fc, client)
                    if "block_rag" in fci and fci["block_rag"]:
                        block_rag = True
                    if fci:
                        function_calls.append(fci)
                        
        # Check if there are document files to add to the prompt
        internet_search_results = ""
        internet_search_infos = []
        documentation = ""


        # boosting information
        if self.config.positive_boost:
            positive_boost=f"{self.system_custom_header('important information')}"+self.config.positive_boost+"\n"
            n_positive_boost = self.model.count_tokens(positive_boost)
        else:
            positive_boost=""
            n_positive_boost = 0

        if self.config.negative_boost:
            negative_boost=f"{self.system_custom_header('important information')}"+self.config.negative_boost+"\n"
            n_negative_boost = self.model.count_tokens(negative_boost)
        else:
            negative_boost=""
            n_negative_boost = 0

        if self.config.fun_mode:
            fun_mode=f"""{self.system_custom_header('important information')} 
Fun mode activated. In this mode you must answer in a funny playful way. Do not be serious in your answers. Each answer needs to make the user laugh.\n"
"""
            n_fun_mode = self.model.count_tokens(positive_boost)
        else:
            fun_mode=""
            n_fun_mode = 0

        if self.config.think_first_mode:
            think_first_mode=f"""{self.system_custom_header('important information')} 
{self.config.thinking_prompt}
"""
            n_think_first_mode = self.model.count_tokens(positive_boost)
        else:
            think_first_mode=""
            n_think_first_mode = 0

        discussion = None
        if generation_type != "simple_question":

            # Standard RAG
            if not self.personality.ignore_discussion_documents_rag and not block_rag:
                if self.personality.persona_data_vectorizer or len(self.active_datalakes) > 0 or ((len(client.discussion.text_files) > 0) and client.discussion.vectorizer is not None) or self.config.activate_skills_lib:
                    #Prepare query

                    # Recover or initialize discussion
                    if discussion is None:
                        discussion = self.recover_discussion(client_id)

                    # Build documentation if empty
                    if documentation == "":
                        documentation = f"{self.separator_template}".join([
                            f"{self.system_custom_header('important information')}",
                            "Utilize Documentation Data: Always refer to the provided documentation to answer user questions accurately.",
                            "Absence of Information: If the required information is not available in the documentation, inform the user that the requested information is not present in the documentation section.",
                            "Strict Adherence to Documentation: It is strictly prohibited to provide answers without concrete evidence from the documentation.",
                            "Cite Your Sources: After providing an answer, include the full path to the document where the information was found.",
                            f"{self.system_custom_header('Documentation')}"
                        ])
                        documentation += f"{self.separator_template}"

                    # Process query
                    if self.config.rag_build_keys_words:
                        self.personality.step_start("Building vector store query")
                        prompt = f"""{self.system_full_header} You are a prompt to query converter assistant. Read the discussion and rewrite the last user prompt as a self sufficient prompt containing all neeeded information.\n
Do not answer the prompt. Do not add explanations.
{self.separator_template}
--- discussion ---
{self.system_custom_header('discussion')}'\n{discussion[-4096:]}
---
Answer directly with the reformulation of the last prompt.
{self.ai_custom_header('assistant')}"""
                        query = self.personality.fast_gen(
                            prompt,
                            max_generation_size=256,
                            show_progress=True,
                            callback=self.personality.sink
                        )
                        query = self.personality.remove_thinking_blocks(query)
                        self.personality.step_end("Building vector store query")
                        self.personality.step(f"Query: {query}")
                    else:
                        query = current_message.content

                    # Inform the user    
                    self.personality.step_start("Querying the RAG datalake")

                    # RAGs
                    # if len(self.active_datalakes) > 0:
                    #     recovered_ids=[[] for _ in range(len(self.active_datalakes))]
                    #     for i,db in enumerate(self.active_datalakes):
                    #         if db['mounted']:
                    #             try:
                    #                 if db["type"]=="safe_store":
                                        
                    #                     ss:SafeStore = db["binding"]
                    #                     vectorizer_name:str = db["vectorizer_name"]
                    #                     r=ss.query(query, vectorizer_name, top_k= self.config.rag_n_chunks)
                    #                     recovered_ids[i]+=[rg.chunk_id for rg in r]
                    #                     if self.config.rag_activate_multi_hops:
                    #                         r = [rg for rg in r if self.personality.verify_rag_entry(query, rg.text)]
                    #                     documentation += "\n".join(["## chunk" + research_result[]  for research_result in r])+"\n"
                    #             except Exception as ex:
                    #                 trace_exception(ex)
                    #                 self.personality.error(f"Couldn't recover information from Datalake {db['alias']}")

                    # TODO : upgrade to safe_store
                    # if self.personality.persona_data_vectorizer:
                    #     chunks:List[Chunk] = self.personality.persona_data_vectorizer.search(query, int(self.config.rag_n_chunks))
                    #     for chunk in chunks:
                    #         if self.config.rag_put_chunk_informations_into_context:
                    #             documentation += f"{self.system_custom_header('document chunk')}\n## document title: {chunk.doc.title}\n## chunk content:\n{chunk.text}\n"
                    #         else:
                    #             documentation += f"{self.system_custom_header('chunk')}\n{chunk.text}\n"

                    if (len(client.discussion.text_files) > 0) and client.discussion.vectorizer is not None:
                        chunks = client.discussion.vectorizer.query(query, self.config.rag_vectorizer)
                        for chunk in chunks:
                            if self.config.rag_put_chunk_informations_into_context:
                                documentation += f"{self.system_custom_header('document chunk')}\n## document title: {chunk.doc['metadata']}\n## chunk content:\n{chunk['chunk_text']}\n"
                            else:
                                documentation += f"{self.start_header_id_template}chunk{self.end_header_id_template}\n{chunk['chunk_text']}\n"                    
                    # Check if there is discussion knowledge to add to the prompt
                    # if self.config.activate_skills_lib:
                    #     try:
                    #         # skills = self.skills_library.query_entry(query)
                    #         self.personality.step_start("Adding skills")
                    #         if self.config.debug:
                    #             ASCIIColors.info(f"Query : {query}")
                    #         skill_titles, skills, similarities = self.skills_library.query_vector_db(query, top_k=3, min_similarity=self.config.rag_min_correspondance)#query_entry_fts(query)
                    #         skills_detials=[{"title": title, "content":content, "similarity":similarity} for title, content, similarity in zip(skill_titles, skills, similarities)]

                    #         if len(skills)>0:
                    #             if documentation=="":
                    #                 documentation=f"{self.system_custom_header('skills library knowledges')}\n"
                    #             for i,skill in enumerate(skills_detials):
                    #                 documentation += "---\n"+ self.system_custom_header(f"knowledge {i}") +f"\ntitle:\n{skill['title']}\ncontent:\n{skill['content']}\n---\n"
                    #         self.personality.step_end("Adding skills")
                    #     except Exception as ex:
                    #         trace_exception(ex)
                    #         self.warning("Couldn't add long term memory information to the context. Please verify the vector database")        # Add information about the user
                    #         self.personality.step_end("Adding skills")

                    # Inform the user    
                    self.personality.step_end("Querying the RAG datalake")

                    documentation += f"{self.separator_template}{self.system_custom_header('important information')}Use the documentation data to answer the user questions. If the data is not present in the documentation, please tell the user that the information he is asking for does not exist in the documentation section. It is strictly forbidden to give the user an answer without having actual proof from the documentation.\n"


            # Internet
            if self.config.activate_internet_search or force_using_internet or generation_type == "full_context_with_internet":
                if discussion is None:
                    discussion = self.recover_discussion(client_id)
                if self.config.internet_activate_search_decision:
                    self.personality.step_start(f"Requesting if {self.personality.name} needs to search internet to answer the user")
                    q = f"{self.separator_template}".join([
                        self.system_full_header,
                        f"Do you need internet search to answer the user prompt?"
                    ])
                    need = not self.personality.yes_no(q, self.user_custom_header("user") + current_message)
                    self.personality.step_end(f"Requesting if {self.personality.name} needs to search internet to answer the user")
                    self.personality.step("Yes" if need else "No")
                else:
                    need=True
                if need:
                    self.personality.step_start("Crafting internet search query")
                    q = f"{self.separator_template}".join([
                        f"{self.system_custom_header('discussion')}",
                        f"{discussion[-2048:]}",  # Use the last 2048 characters of the discussion for context
                        self.system_full_header,
                        f"You are a sophisticated web search query builder. Your task is to help the user by crafting a precise and concise web search query based on their request.",
                        f"Carefully read the discussion and generate a web search query that will retrieve the most relevant information to answer the last message from {self.config.user_name}.",
                        f"Do not answer the prompt directly. Do not provide explanations or additional information.",
                        f"{self.system_custom_header('current date')}{datetime.now()}",
                        f"{self.ai_custom_header('websearch query')}"
                    ])
                    query = self.personality.fast_gen(q, max_generation_size=256, show_progress=True, callback=self.personality.sink)
                    query = self.personality.remove_thinking_blocks(query)
                    query = query.replace("\"","")
                    self.personality.step_end("Crafting internet search query")
                    self.personality.step(f"web search query: {query}")

                    if self.config.internet_quick_search:
                        self.personality.step_start("Performing Internet search (quick mode)")
                    else:
                        self.personality.step_start("Performing Internet search (advanced mode: slower but more accurate)")

                    internet_search_results=f"{self.system_full_header}Use the web search results data to answer {self.config.user_name}. Try to extract information from the web search and use it to perform the requested task or answer the question. Do not come up with information that is not in the websearch results. Try to stick to the websearch results and clarify if your answer was based on the resuts or on your own culture. If you don't know how to perform the task, then tell the user politely that you need more data inputs.{self.separator_template}{self.start_header_id_template}Web search results{self.end_header_id_template}\n"


                    chunks:List[Chunk] = self.personality.internet_search_with_vectorization(query, self.config.internet_quick_search, asses_using_llm=self.config.activate_internet_pages_judgement)
                    
                    if len(chunks)>0:
                        for chunk in chunks:
                            internet_search_infos.append({
                                "title":chunk.doc.title,
                                "url":chunk.doc.path,
                                "brief":chunk.text
                            })
                            internet_search_results += self.system_custom_header("search result chunk")+f"\nchunk_infos:{chunk.doc.path}\nchunk_title:{chunk.doc.title}\ncontent:{chunk.text}\n"
                    else:
                        internet_search_results += "The search response was empty!\nFailed to recover useful information from the search engine.\n"
                    internet_search_results += self.system_custom_header("information") + "Use the search results to answer the user question."
                    if self.config.internet_quick_search:
                        self.personality.step_end("Performing Internet search (quick mode)")
                    else:
                        self.personality.step_end("Performing Internet search (advanced mode: slower but more advanced)")


        #User description
        user_description=""
        if self.config.use_user_informations_in_discussion:
            user_description=self.config.user_description


        # Tokenize the conditionning text and calculate its number of tokens
        tokens_conditionning = self.model.tokenize(conditionning)
        n_cond_tk = len(tokens_conditionning)


        # Tokenize the internet search results text and calculate its number of tokens
        if len(internet_search_results)>0:
            tokens_internet_search_results = self.model.tokenize(internet_search_results)
            n_isearch_tk = len(tokens_internet_search_results)
        else:
            tokens_internet_search_results = []
            n_isearch_tk = 0


        # Tokenize the documentation text and calculate its number of tokens
        if len(documentation)>0:
            tokens_documentation = self.model.tokenize(documentation)
            n_doc_tk = len(tokens_documentation)
            self.info(f"The documentation consumes {n_doc_tk} tokens")
            if n_doc_tk>3*self.config.ctx_size/4:
                ASCIIColors.warning("The documentation is bigger than 3/4 of the context ")
                self.warning("The documentation is bigger than 3/4 of the context ")
            if n_doc_tk>=self.config.ctx_size-512:
                ASCIIColors.warning("The documentation is too big for the context")
                self.warning("The documentation is too big for the context it'll be cropped")
                documentation = self.model.detokenize(tokens_documentation[:(self.config.ctx_size-512)])
                n_doc_tk = self.config.ctx_size-512

        else:
            tokens_documentation = []
            n_doc_tk = 0



        # Tokenize user description
        if len(user_description)>0:
            tokens_user_description = self.model.tokenize(user_description)
            n_user_description_tk = len(tokens_user_description)
        else:
            tokens_user_description = []
            n_user_description_tk = 0

        # Calculate the total number of tokens between conditionning, documentation, and knowledge
        total_tokens = n_cond_tk + n_isearch_tk + n_doc_tk + n_user_description_tk + n_positive_boost + n_negative_boost + n_fun_mode + n_think_first_mode

        # Calculate the available space for the messages
        available_space = self.config.ctx_size - n_tokens - total_tokens

        # if self.config.debug:
        #     self.info(f"Tokens summary:\nConditionning:{n_cond_tk}\nn_isearch_tk:{n_isearch_tk}\ndoc:{n_doc_tk}\nhistory:{n_history_tk}\nuser description:{n_user_description_tk}\nAvailable space:{available_space}",10)

        # Raise an error if the available space is 0 or less
        if available_space<1:
            ASCIIColors.red(f"available_space:{available_space}")
            ASCIIColors.red(f"n_doc_tk:{n_doc_tk}")
            
            ASCIIColors.red(f"n_isearch_tk:{n_isearch_tk}")
            
            ASCIIColors.red(f"n_tokens:{n_tokens}")
            ASCIIColors.red(f"self.config.max_n_predict:{self.config.max_n_predict}")
            self.InfoMessage(f"Not enough space in context!!\nVerify that your vectorization settings for documents or internet search are realistic compared to your context size.\nYou are {available_space} short of context!")
            raise Exception("Not enough space in context!!")

        # Accumulate messages until the cumulative number of tokens exceeds available_space
        tokens_accumulated = 0


        # Initialize a list to store the full messages
        full_message_list = []
        # If this is not a continue request, we add the AI prompt
        if not is_continue:
            message_tokenized = self.model.tokenize(
                self.personality.ai_message_prefix.strip()
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
                        message.message_type <= MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_USER.value and message.message_type != MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI.value):

                    if self.config.keep_thoughts:
                        content = message.content
                    else:
                        content = self.personality.remove_thinking_blocks(message.content)
                        
                    if message.sender_type == SENDER_TYPES.SENDER_TYPES_AI.value:
                        if self.config.use_assistant_name_in_discussion:
                            if self.config.use_model_name_in_discussions:
                                msg = self.ai_custom_header(message.sender+f"({message.model})") + content.strip()
                            else:
                                msg = self.ai_full_header + content.strip()
                        else:
                            if self.config.use_model_name_in_discussions:
                                msg = self.ai_custom_header("assistant"+f"({message.model})") + content.strip()
                            else:
                                msg = self.ai_custom_header("assistant") + content.strip()
                    else:
                        if self.config.use_user_name_in_discussions:
                            msg = self.user_full_header + content.strip()
                        else:
                            msg = self.user_custom_header("user") + content.strip()
                    msg += self.separator_template
                    message_tokenized = self.model.tokenize(msg)

                    # Check if adding the message will exceed the available space
                    if tokens_accumulated + len(message_tokenized) > available_space:
                        # Update the cumulative number of tokens
                        msg = message_tokenized[-(available_space-tokens_accumulated):]
                        tokens_accumulated += available_space-tokens_accumulated
                        full_message_list.insert(0, msg)
                        break

                    # Add the tokenized message to the full_message_list
                    full_message_list.insert(0, message_tokenized)

                    # Update the cumulative number of tokens
                    tokens_accumulated += len(message_tokenized)
        else:
            message = messages[message_index]

            # Check if the message content is not empty and visible to the AI
            if message.content != '' and (
                    message.message_type <= MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_USER.value and message.message_type != MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI.value):
                if self.config.keep_thoughts:
                    content = message.content
                else:
                    content = self.personality.remove_thinking_blocks(message.content)

                if message.sender_type == SENDER_TYPES.SENDER_TYPES_AI.value:
                    if self.config.use_assistant_name_in_discussion:
                        if self.config.use_model_name_in_discussions:
                            msg = self.ai_custom_header(message.sender+f"({message.model})") + content.strip()
                        else:
                            msg = self.ai_full_header + content.strip()
                    else:
                        if self.config.use_model_name_in_discussions:
                            msg = self.ai_custom_header("assistant"+f"({message.model})") + content.strip()
                        else:
                            msg = self.ai_custom_header("assistant") + content.strip()
                else:
                    if self.config.use_user_name_in_discussions:
                        msg = self.user_full_header + content.strip()
                    else:
                        msg = self.user_custom_header("user") + content.strip()
                message_tokenized = self.model.tokenize(msg)

                # Add the tokenized message to the full_message_list
                full_message_list.insert(0, message_tokenized)

                # Update the cumulative number of tokens
                tokens_accumulated += len(message_tokenized)

        # Build the final discussion messages by detokenizing the full_message_list
        discussion_messages = ""
        for i in range(len(full_message_list)-1 if not is_continue else len(full_message_list)):
            message_tokens = full_message_list[i]
            discussion_messages += self.model.detokenize(message_tokens)
        
        if len(full_message_list)>0:
            ai_prefix = self.personality.ai_message_prefix
        else:
            ai_prefix = ""


        # Details
        context_details = LollmsContextDetails(
            client=client,
            conditionning=conditionning,
            internet_search_infos=internet_search_infos,
            internet_search_results=internet_search_results,
            documentation=documentation,
            documentation_entries=documentation_entries,
            user_description=user_description,
            discussion_messages=discussion_messages,
            positive_boost=positive_boost,
            negative_boost=negative_boost,
            current_language=self.config.current_language,
            fun_mode=fun_mode,
            think_first_mode=think_first_mode,
            ai_prefix=ai_prefix,
            extra="",
            available_space=available_space,
            skills=skills_detials,
            is_continue=is_continue,
            previous_chunk=previous_chunk,
            prompt=current_message.content,
            function_calls=function_calls,

            debug= self.config.debug,
            ctx_size= self.config.ctx_size,
            max_n_predict= self.config.max_n_predict,

            model= self.model
        )
        
        
        if self.config.debug and not self.personality.processor:
            ASCIIColors.highlight(documentation,"source_document_title", ASCIIColors.color_yellow, ASCIIColors.color_red, False)
        # Return the prepared query, original message content, and tokenized query
        return context_details      


    # Properties ===============================================
    @property
    def start_header_id_template(self) -> str:
        """Get the start_header_id_template."""
        return self.config.start_header_id_template

    @property
    def end_header_id_template(self) -> str:
        """Get the end_header_id_template."""
        return self.config.end_header_id_template
    
    @property
    def system_message_template(self) -> str:
        """Get the system_message_template."""
        return self.config.system_message_template


    @property
    def separator_template(self) -> str:
        """Get the separator template."""
        return self.config.separator_template


    @property
    def start_user_header_id_template(self) -> str:
        """Get the start_user_header_id_template."""
        return self.config.start_user_header_id_template
    @property
    def end_user_header_id_template(self) -> str:
        """Get the end_user_header_id_template."""
        return self.config.end_user_header_id_template
    @property
    def end_user_message_id_template(self) -> str:
        """Get the end_user_message_id_template."""
        return self.config.end_user_message_id_template




    # Properties ===============================================
    @property
    def start_header_id_template(self) -> str:
        """Get the start_header_id_template."""
        return self.config.start_header_id_template

    @property
    def end_header_id_template(self) -> str:
        """Get the end_header_id_template."""
        return self.config.end_header_id_template
    
    @property
    def system_message_template(self) -> str:
        """Get the system_message_template."""
        return self.config.system_message_template


    @property
    def separator_template(self) -> str:
        """Get the separator template."""
        return self.config.separator_template


    @property
    def start_user_header_id_template(self) -> str:
        """Get the start_user_header_id_template."""
        return self.config.start_user_header_id_template
    @property
    def end_user_header_id_template(self) -> str:
        """Get the end_user_header_id_template."""
        return self.config.end_user_header_id_template
    @property
    def end_user_message_id_template(self) -> str:
        """Get the end_user_message_id_template."""
        return self.config.end_user_message_id_template





    @property
    def start_ai_header_id_template(self) -> str:
        """Get the start_ai_header_id_template."""
        return self.config.start_ai_header_id_template
    @property
    def end_ai_header_id_template(self) -> str:
        """Get the end_ai_header_id_template."""
        return self.config.end_ai_header_id_template
    @property
    def end_ai_message_id_template(self) -> str:
        """Get the end_ai_message_id_template."""
        return self.config.end_ai_message_id_template
    @property
    def system_full_header(self) -> str:
        """Get the start_header_id_template."""
        return f"{self.start_header_id_template}{self.system_message_template}{self.end_header_id_template}"
    @property
    def user_full_header(self) -> str:
        """Get the start_header_id_template."""
        if self.config.use_user_name_in_discussions:
            return f"{self.start_user_header_id_template}{self.config.user_name}{self.end_user_header_id_template}"
        else:
            return f"{self.start_user_header_id_template}user{self.end_user_header_id_template}"
    @property
    def ai_full_header(self) -> str:
        """Get the start_header_id_template."""
        if self.config.use_user_name_in_discussions:
            return f"{self.start_ai_header_id_template}{self.personality.name}{self.end_ai_header_id_template}"
        else:
            return f"{self.start_ai_header_id_template}assistant{self.end_ai_header_id_template}"

    def system_custom_header(self, system_header) -> str:
        """Get the start_header_id_template."""
        return f"{self.start_header_id_template}{system_header}{self.end_user_header_id_template}"

    def user_custom_header(self, ai_name) -> str:
        """Get the start_header_id_template."""
        return f"{self.start_user_header_id_template}{ai_name}{self.end_user_header_id_template}"

    def ai_custom_header(self, ai_name) -> str:
        """Get the start_header_id_template."""
        return f"{self.start_ai_header_id_template}{ai_name}{self.end_ai_header_id_template}"

    def parse_to_openai(self, lollms_prompt_string: str) -> list:
        """
        Parses a LoLLMs-formatted prompt string into an OpenAI-compatible messages list.
        """
        # --- Start of Delimiter and Regex Setup (as in your provided code) ---
        # This part is kept inside the method, assuming self.config or self.personality
        # might change between calls. If they are stable for the parser instance,
        # move this setup to __init__ for efficiency.

        self.full_delimiter_to_internal_role = {}
        escaped_delimiter_patterns = []

        # CRITICAL CHECK POINT FOR "INCORRECT EXTRACTION":
        # Ensure the tags derived here (e.g., self.config.user_name) MATCH the
        # actual tags used in `lollms_prompt_string`.
        # For `full_prompt_example` to work, self.config.user_name needs to be "user"
        # and the assistant tag logic needs to result in "assistant".
        user_actual_tag = self.config.user_name if self.config.use_user_name_in_discussions else "user"
        assistant_actual_tag = self.personality.name if self.config.use_assistant_name_in_discussion else "assistant"

        self.role_definitions = {
            "system": ("system", self.start_header_id_template, self.end_user_header_id_template),
            "user": (user_actual_tag, self.start_user_header_id_template, self.end_user_header_id_template),
            "assistant": (assistant_actual_tag, self.start_ai_header_id_template, self.end_ai_header_id_template),
            "discussion": ("discussion", self.start_header_id_template, self.end_user_header_id_template)
        }

        for internal_role, definition in self.role_definitions.items():
            tag, prefix, suffix = definition
            if not tag:
                print(f"Warning: No tag configured for internal role '{internal_role}'. It won't be parsed.")
                continue
            full_delimiter = f"{prefix}{tag}{suffix}"
            self.full_delimiter_to_internal_role[full_delimiter] = internal_role
            escaped_delimiter_patterns.append(re.escape(full_delimiter))
        
        escaped_delimiter_patterns.sort(key=len, reverse=True)
        self.delimiter_choices_pattern = "|".join(escaped_delimiter_patterns)
        
        if not self.delimiter_choices_pattern:
            # This can happen if all tags are None or empty.
            # Consider if an empty prompt string should return [] or raise error earlier.
            if not lollms_prompt_string.strip(): return [] # Handle empty prompt gracefully
            raise ValueError("No valid delimiters could be constructed. "
                             "Please ensure role tags (user_name, assistant_name etc.) and templates are configured.")

        self.parsing_regex = re.compile(
            f"({self.delimiter_choices_pattern})"
            r"([\s\S]*?)"
            f"(?=\\n(?:{self.delimiter_choices_pattern})|$)"
        )        
        # --- End of Delimiter and Regex Setup ---

        matches = self.parsing_regex.finditer(lollms_prompt_string)
        all_segments = []
        for match in matches:
            full_delimiter_string = match.group(1)
            content = match.group(2).strip()
            internal_role = self.full_delimiter_to_internal_role.get(full_delimiter_string)
            
            if internal_role:
                all_segments.append({"role_key": internal_role, "content": content})
            else:
                # This should ideally not be hit if regex and config are correct.
                # It might indicate a new, unconfigured delimiter in the prompt.
                print(f"Warning: Unrecognized delimiter segment encountered: {full_delimiter_string[:50]}...")

        # If all_segments is empty, it means no delimiters were found.
        # This could be an empty prompt, a prompt with no known delimiters,
        # or an issue with delimiter_choices_pattern becoming empty.
        if not all_segments and lollms_prompt_string.strip():
            # If the prompt is not empty but no segments were found, it's likely a pure user message.
            # However, the current logic relies on delimiters. If this scenario is possible,
            # it needs specific handling (e.g., treat as a single user message).
            # For now, this will result in an empty openai_messages list.
            pass


        openai_messages = []
        system_parts = []
        first_assistant_content = None
        processed_first_assistant = False
        chat_start_index = 0 

        for i, segment in enumerate(all_segments):
            chat_start_index = i 
            role = segment["role_key"]
            content = segment["content"]

            if not processed_first_assistant:
                if role == "system":
                    if content: system_parts.append(content)
                elif role == "discussion": 
                    if content: system_parts.append(content)
                elif role == "assistant": 
                    first_assistant_content = content 
                    processed_first_assistant = True
                    chat_start_index = i + 1 
                    break 
                elif role == "user": 
                    break 
            else: # processed_first_assistant is True
                  # This means the loop should have broken when the first assistant msg was processed.
                  # If it reaches here, it means the first segment AFTER the first assistant
                  # is at index `i`.
                break 
        
        remaining_segments_for_chat = all_segments[chat_start_index:]
            
        initial_system_message_content = "\n".join(system_parts).strip()
        if first_assistant_content is not None: 
            if initial_system_message_content and first_assistant_content:
                initial_system_message_content += "\n" + first_assistant_content
            elif first_assistant_content: 
                initial_system_message_content = first_assistant_content
            
        if initial_system_message_content: 
            openai_messages.append({"role": "system", "content": initial_system_message_content})

        for segment in remaining_segments_for_chat:
            role = segment["role_key"]
            content = segment["content"]
            if role == "user":
                openai_messages.append({"role": "user", "content": content})
            elif role == "assistant":
                openai_messages.append({"role": "assistant", "content": content})
            elif role == "discussion":
                # Policy: Mid-chat discussion segments are currently ignored.
                pass 

        # MODIFICATION: Remove the last message if it's from the assistant
        if openai_messages and openai_messages[-1]["role"] == "assistant":
            openai_messages.pop()

        if len(openai_messages)==1:
            openai_messages[0]["role"]="user"
        elif len(openai_messages)==0:
            openai_messages=[
                {"role":"user","content":lollms_prompt_string}
            ]
        return openai_messages