from lollms.config import BaseConfig
from lollms.binding import BindingBuilder
from api.config import load_config
import gc
import pkg_resources
from flask import jsonify, request
from lollms.helpers import ASCIIColors
from pathlib import Path
import traceback
from ...config.scripts import install_bindings_requirements

__version__ ="6.5"


def save_settings(self):
    self.config.save_config(self.config_file_path)
    if self.config["debug"]:
        print("Configuration saved")
    # Tell that the setting was changed
    self.socketio.emit('save_settings', {"status":True})
    return jsonify({"status":True})

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
            except ModuleNotFoundError:
                install_bindings_requirements(big_class=self)
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

def get_lollms_version(self):
    version = pkg_resources.get_distribution('lollms').version
    ASCIIColors.yellow("Lollms version : "+ version)
    return jsonify({"version":version})

def get_lollms_webui_version(self):
    version = __version__
    ASCIIColors.yellow("Lollms webui version : "+ version)
    return jsonify({"version":version})

def get_config(self):
    return jsonify(self.config.to_dict())

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

def upload_avatar(self):      
    file = request.files['avatar']
    file.save(self.lollms_paths.personal_user_infos_path/file.filename)
    return jsonify({"status": True,"fileName":file.filename})