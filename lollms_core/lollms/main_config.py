__author__ = "ParisNeo"
__github__ = "https://github.com/ParisNeo/lollms"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

from ascii_colors       import ASCIIColors
from lollms.paths       import LollmsPaths
from lollms.config      import BaseConfig
#from lollms.binding import  LLMBinding
import shutil
import urllib.request as rq
from tqdm               import tqdm
from pathlib            import Path


import sys
DEFAULT_CONFIG = {
    # =================== Lord Of Large Language Models Configuration file =========================== 
    "version": 5,
    "binding_name": "llama_cpp_official",
    "model_name": "Wizard-Vicuna-7B-Uncensored.ggmlv3.q4_0.bin",

    # Host information
    "host": "localhost",
    "port": 9600,

    # Genreration parameters 
    "seed": -1,
    "n_predict": 1024,
    "ctx_size": 2048,
    "temperature": 0.9,
    "top_k": 50,
    "top_p": 0.95,
    "repeat_last_n": 40,
    "repeat_penalty": 1.2,

    "n_threads": 8,

    #Personality parameters
    "personalities": ["generic/lollms"],
    "active_personality_id": 0,
    "override_personality_model_parameters": False, #if true the personality parameters are overriden by those of the configuration (may affect personality behaviour) 

    "user_name": "user",

}

class LOLLMSConfig(BaseConfig):
    def __init__(self, file_path=None, lollms_paths:LollmsPaths = None):
        super().__init__(["file_path", "config", "lollms_paths"])
                
        if file_path:
            self.file_path = Path(file_path)
        else:
            self.file_path = None

        if file_path is not None:
            self.load_config(file_path)
        else:
            self.config = DEFAULT_CONFIG.copy()

        if lollms_paths is None:
            self.lollms_paths = LollmsPaths()
        else:
            self.lollms_paths = lollms_paths
        
    def copy(self):
        cfg = LOLLMSConfig(self.file_path, self.lollms_paths)
        cfg.config = self.config.copy()
        return cfg
    @staticmethod
    def autoload(lollms_paths:LollmsPaths, config_path:str=None):
        # Configuration loading part
        original_cfg_path = lollms_paths.default_cfg_path
        if config_path is None:
            local = lollms_paths.personal_configuration_path / f"{lollms_paths.tool_prefix}local_config.yaml"
            if not local.exists():
                shutil.copy(original_cfg_path, local)
            cfg_path = local
        else:
            cfg_path = config_path

        if cfg_path.exists():
            original_config = LOLLMSConfig(original_cfg_path, lollms_paths)
            config = LOLLMSConfig(cfg_path, lollms_paths)
            if "version" not in config or int(config["version"])<int(original_config["version"]):
                #Upgrade old configuration files to new format
                ASCIIColors.error("Configuration file is very old.\nReplacing with default configuration")
                _, added, removed = config.sync_cfg(original_config)
                print(f"Added entries : {added}, removed entries:{removed}")
                config.save_config(cfg_path)
        else:
            config = LOLLMSConfig(lollms_paths=lollms_paths)
        
        return config
            
    def sync_cfg(self, default_config):
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
        for key, value in default_config.config.items():
            if key not in self:
                self[key] = value
                added_entries.append(key)

        # Remove fields from config that don't exist in default_config
        for key in list(self.config.keys()):
            if key not in default_config.config:
                del self.config[key]
                removed_entries.append(key)

        ASCIIColors.yellow(default_config.config)
        self["version"]=default_config["version"]
        
        return self, added_entries, removed_entries

    def get_model_path_infos(self):
        return f"personal_models_path: {self.lollms_paths.personal_models_path}\nBinding name:{self.binding_name}\nModel name:{self.model_name}"

    def get_personality_path_infos(self):
        return f"personalities_zoo_path: {self.lollms_paths.personalities_zoo_path}\nPersonalities:{self.personalities}\nActive personality id:{self.active_personality_id}"

    def get_model_full_path(self):
        try:
            return self.lollms_paths.personal_models_path/self.binding_name/self.model_name
        except:
            return None
    def check_model_existance(self):
        try:
            model_path = self.lollms_paths.personal_models_path/self.binding_name/self.model_name
            return model_path.exists()
        except Exception as ex:
            print(f"Exception in checking model existance: {ex}")
            return False 
