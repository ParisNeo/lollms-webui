from pathlib import Path
import shutil
from ascii_colors import ASCIIColors, trace_exception
from lollms.config import BaseConfig
import subprocess
import os
import yaml
import sys, platform

lollms_path = Path(__file__).parent
lollms_default_cfg_path = lollms_path / "configs/config.yaml"
lollms_bindings_zoo_path = lollms_path / "zoos/bindings_zoo"
lollms_personalities_zoo_path = lollms_path / "zoos/personalities_zoo"

lollms_core_repo = "https://github.com/ParisNeo/lollms_legacy.git"
safe_store_repo = "https://github.com/ParisNeo/safe_store.git"

personalities_zoo_repo = "https://github.com/ParisNeo/lollms_personalities_zoo.git"
bindings_zoo_repo = "https://github.com/ParisNeo/lollms_bindings_zoo.git"
models_zoo_repo = "https://github.com/ParisNeo/models_zoo.git"
services_zoo_repo = "https://github.com/ParisNeo/lollms_services_zoo.git"
functions_zoo_repo = "https://github.com/ParisNeo/lollms_functions_zoo.git"
gptqlora_repo = "https://github.com/ParisNeo/gptqlora.git"

lollms_webui_version = "v19.2242 (codename Twins 🔗)"

# Now we speify the personal folders
class LollmsPaths:
    def __init__(self, global_paths_cfg_path=None, lollms_path=None, personal_path=None, custom_default_cfg_path=None, tool_prefix="", prepare_configuration=True):
        self.global_paths_cfg_path  = global_paths_cfg_path
        if self.global_paths_cfg_path is not None:
            if self.global_paths_cfg_path.exists():
                try:
                    with(open(self.global_paths_cfg_path,"r") as f):
                        infos = yaml.safe_load(f)
                        if lollms_path is None:
                            lollms_path = infos["lollms_path"]
                        if personal_path is None:
                            personal_path = infos["lollms_personal_path"]
                except Exception as ex:
                    ASCIIColors.error(ex)
            else:
                infos={
                    "lollms_path":None,
                    "lollms_personal_path":None
                }



        self.tool_prefix            = tool_prefix
        if lollms_path is None:
            lollms_path             = Path(__file__).parent
        else:
            lollms_path             = Path(lollms_path)
        if personal_path is None:
            personal_path           = Path("../personal_data")
        else:
            personal_path           = Path(personal_path)
        
        if custom_default_cfg_path is not None:
            self.default_cfg_path   = Path(custom_default_cfg_path)
        else:
            self.default_cfg_path   = lollms_path / "configs/config.yaml"

        self.personal_path                  = personal_path.resolve()
        self.personal_configuration_path    = self.personal_path / "configs"
        self.personal_data_path             = self.personal_path / "data"
        self.personal_memory_path           = self.personal_path / "memory"
        self.personal_discussions_path      = self.personal_path / "discussion_databases"
        self.personal_skills_path           = self.personal_path / "skill_databases"
        self.personal_models_path           = self.personal_path / "models"
        self.personal_uploads_path          = self.personal_path / "uploads"
        self.personal_log_path              = self.personal_path / "logs"
        self.personal_certificates          = self.personal_path / "certs"
        self.personal_outputs_path          = self.personal_path / "outputs"
        self.personal_user_infos_path       = self.personal_path / "user_infos"
        self.personal_apps_path             = self.personal_path / "apps"

        self.personal_services_path         = self.personal_path / "services"
        self.personal_stt_services_path     = self.personal_services_path / "stt"
        self.personal_tts_services_path     = self.personal_services_path / "tts"
        self.personal_tti_services_path     = self.personal_services_path / "tti"
        self.personal_ttm_services_path     = self.personal_services_path / "ttm"

        self.apps_zoo_path                  = self.personal_path / "apps_zoo"



        self.personal_trainers_path         = self.personal_path / "trainers"
        self.gptqlora_path                  = self.personal_trainers_path / "gptqlora"

        self.custom_personalities_path      = self.personal_path / "custom_personalities"
        self.custom_function_calls_path      = self.personal_path / "custom_function_calls"
        self.custom_voices_path             = self.personal_path / "custom_voices"

        self.binding_models_paths   = []

        self.execution_path = Path(os.getcwd())

        self.lollms_core_path = self.execution_path/"lollms_core"
        self.safe_store_path = self.execution_path/"utilities/safe_store"
    
        if (self.execution_path/"zoos").exists():
            ASCIIColors.green("Local zoos folder found")
            rt = self.execution_path / "zoos"
            rt.mkdir(parents=True, exist_ok=True)
            self.bindings_zoo_path              = rt / "bindings_zoo"
            self.personalities_zoo_path         = rt / "personalities_zoo"
            self.models_zoo_path                = rt / "models_zoo"
            self.services_zoo_path              = rt / "services_zoo"
            
            self.functions_zoo_path             = rt / "functions_zoo"
        else:
            ASCIIColors.orange("local zoos folder not found")
            rt = self.personal_path / "zoos"
            rt.mkdir(parents=True, exist_ok=True)
            self.bindings_zoo_path              = rt / "bindings_zoo"
            self.personalities_zoo_path         = rt / "personalities_zoo"
            self.models_zoo_path                = rt / "models_zoo"
            self.services_zoo_path              = rt / "services_zoo"
            self.functions_zoo_path             = rt / "functions_zoo"


        self.display_splash_screen()

        if prepare_configuration:
            self.create_directories()
            self.copy_default_config()
    def display_splash_screen(self) -> None:
        """
        Display a colorful splash screen showing LoLLMs configuration, paths and system information
        """
        # Banner
        ASCIIColors.cyan("""
        ╔══════════════════════════════════════════════════════════════╗
        ║             🤖 LoLLMs - Lord of LLMs                         ║
        ║        One AI Assistant to Rule Them All                     ║
        ║        By ParisNeo (https://github.com/ParisNeo)             ║
        ╚══════════════════════════════════════════════════════════════╝
        """)

        # Version Information
        ASCIIColors.magenta("\n📦 Version Information:")
        ASCIIColors.white("    ├─ WebUI Version: ", end="")
        ASCIIColors.yellow(f"{lollms_webui_version}")
        ASCIIColors.white("    └─ Release Date: ", end="")
        ASCIIColors.yellow("January 18, 2025")

        # Python Environment Information
        ASCIIColors.magenta("\n🐍 Python Environment:")
        ASCIIColors.white("    ├─ Python Version: ", end="")
        ASCIIColors.yellow(f"{sys.version.split()[0]}")
        ASCIIColors.white("    ├─ Python Path: ", end="")
        ASCIIColors.yellow(f"{sys.executable}")
        ASCIIColors.white("    └─ Platform: ", end="")
        ASCIIColors.yellow(f"{platform.platform()}")

        # System Information
        ASCIIColors.magenta("\n🖥️  System Configuration:")
        ASCIIColors.white("    ├─ Execution Path: ", end="")
        ASCIIColors.yellow(f"{self.execution_path}")
        
        # Zoo Status
        if (self.execution_path/"zoos").exists():
            ASCIIColors.white("    └─ Zoo Status: ", end="")
            ASCIIColors.green("Local zoos folder found")
        else:
            ASCIIColors.white("    └─ Zoo Status: ", end="")
            ASCIIColors.orange("Using personal zoos folder")

        # Personal Paths Section
        ASCIIColors.magenta("\n📁 Personal Paths:")
        paths_info = [
            ("Personal Path", self.personal_path),
            ("Configuration Path", self.personal_configuration_path),
            ("Discussions Path", self.personal_discussions_path),
            ("Skills Path", self.personal_skills_path),
            ("Models Path", self.personal_models_path),
            ("User Info Path", self.personal_user_infos_path),
            ("User Info Path", self.personal_apps_path),
            ("Custom Personalities", self.custom_personalities_path),
            ("Custom Voices", self.custom_voices_path),
            ("Custom function calls",self.custom_function_calls_path)

        ]
        
        for i, (name, path) in enumerate(paths_info):
            prefix = "    ├─ " if i < len(paths_info)-1 else "    └─ "
            ASCIIColors.white(f"{prefix}{name}: ", end="")
            ASCIIColors.yellow(f"{path}")

        # Services Section
        ASCIIColors.magenta("\n🛠️  Services Configuration:")
        services = [
            ("Main Services", self.personal_services_path),
            ("Speech-to-Text", self.personal_stt_services_path),
            ("Text-to-Speech", self.personal_tts_services_path),
            ("Text-to-Image", self.personal_tti_services_path),
            ("Text-to-Music", self.personal_ttm_services_path)
        ]
        
        for i, (name, path) in enumerate(services):
            prefix = "    ├─ " if i < len(services)-1 else "    └─ "
            ASCIIColors.white(f"{prefix}{name}: ", end="")
            ASCIIColors.yellow(f"{path}")

        # Zoo Information
        ASCIIColors.magenta("\n🏰 Zoo Configuration:")
        zoos = [
            ("Bindings Zoo", self.bindings_zoo_path),
            ("Personalities Zoo", self.personalities_zoo_path),
            ("Models Zoo", self.models_zoo_path),
            ("Servicesq Zoo", self.services_zoo_path)
        ]
        
        for i, (name, path) in enumerate(zoos):
            prefix = "    ├─ " if i < len(zoos)-1 else "    └─ "
            ASCIIColors.white(f"{prefix}{name}: ", end="")
            ASCIIColors.yellow(f"{path}")

        # Ready Message
        ASCIIColors.green("\n✨ LoLLMs is ready to serve! Let's build something amazing! 🚀\n")


    def __str__(self) -> str:
        directories = {
            "Global paths configuration Path": self.global_paths_cfg_path,
            "Personal Configuration Path": self.personal_configuration_path,
            "Personal Data Path": self.personal_data_path,
            "Personal Databases Path": self.personal_discussions_path,
            "Personal Skills Path": self.personal_skills_path,
            "Personal Models Path": self.personal_models_path,
            "Personal Uploads Path": self.personal_uploads_path,
            "Personal Log Path": self.personal_log_path,
            "Personal outputs Path": self.personal_outputs_path,
            "Bindings Zoo Path": self.bindings_zoo_path,
            "Personalities Zoo Path": self.personalities_zoo_path,
            "Personal user infos path": self.personal_user_infos_path,
            "apps path": self.personal_apps_path,
            "Personal trainers path": self.personal_trainers_path,
            "Personal gptqlora trainer path": self.gptqlora_path,

            "Personal services path": self.personal_services_path,
            "Personal STT services path": self.personal_stt_services_path,
            "Personal TTS services path": self.personal_tts_services_path,
            "Personal TTI services path": self.personal_tti_services_path,
            "Personal TTM services path": self.personal_ttm_services_path, 

            "Applications zoo path": self.apps_zoo_path,
            "Functions zoo path": self.functions_zoo_path,
            "Custom Functions zoo path": self.custom_function_calls_path,          
        }
        return "\n".join([f"{category}: {path}" for category, path in directories.items()])

    def change_personal_path(self, path):
        self.personal_path = path

    def create_directories(self):
        self.personal_path.mkdir(parents=True, exist_ok=True)
        self.personal_configuration_path.mkdir(parents=True, exist_ok=True)
        self.personal_models_path.mkdir(parents=True, exist_ok=True)
        self.personal_data_path.mkdir(parents=True, exist_ok=True)
        self.personal_discussions_path.mkdir(parents=True, exist_ok=True)
        self.personal_skills_path.mkdir(parents=True, exist_ok=True)
        self.personal_log_path.mkdir(parents=True, exist_ok=True)
        self.personal_certificates.mkdir(parents=True, exist_ok=True)
        self.personal_outputs_path.mkdir(parents=True, exist_ok=True)
        self.personal_uploads_path.mkdir(parents=True, exist_ok=True)
        self.personal_user_infos_path.mkdir(parents=True, exist_ok=True)
        self.personal_apps_path.mkdir(parents=True, exist_ok=True)

        self.personal_services_path.mkdir(parents=True, exist_ok=True)
        self.personal_stt_services_path.mkdir(parents=True, exist_ok=True)
        self.personal_tts_services_path.mkdir(parents=True, exist_ok=True)
        self.personal_tti_services_path.mkdir(parents=True, exist_ok=True)
        self.personal_ttm_services_path.mkdir(parents=True, exist_ok=True)        
        self.personal_trainers_path.mkdir(parents=True, exist_ok=True)
        self.custom_personalities_path.mkdir(parents=True, exist_ok=True)
        self.custom_function_calls_path.mkdir(parents=True, exist_ok=True)
        self.custom_voices_path.mkdir(parents=True, exist_ok=True)

        self.apps_zoo_path.mkdir(parents=True, exist_ok=True)
        self.custom_function_calls_path.mkdir(parents=True, exist_ok=True)

        
        if not self.bindings_zoo_path.exists():
            # Clone the repository to the target path
            ASCIIColors.info("No bindings found in your personal space.\nCloning the personalities zoo")
            subprocess.run(["git", "clone", bindings_zoo_repo, self.bindings_zoo_path])

        if not self.personalities_zoo_path.exists():
            # Clone the repository to the target path
            ASCIIColors.info("No personalities found in your personal space.\nCloning the personalities zoo")
            subprocess.run(["git", "clone", personalities_zoo_repo, self.personalities_zoo_path])

        if not self.models_zoo_path.exists():
            # Clone the repository to the target path
            ASCIIColors.info("No models found in your personal space.\nCloning the models zoo")
            subprocess.run(["git", "clone", models_zoo_repo, self.models_zoo_path])

        if not self.services_zoo_path.exists():
            # Clone the repository to the target path
            ASCIIColors.info("No services found in your personal space.\nCloning the services zoo")
            subprocess.run(["git", "clone", services_zoo_repo, self.services_zoo_path])
            

        if not self.functions_zoo_path.exists():
            # Clone the repository to the target path
            ASCIIColors.info("No functions found in your personal space.\nCloning the functions zoo")
            subprocess.run(["git", "clone", functions_zoo_repo, self.functions_zoo_path])


    def copy_default_config(self):
        local_config_path = self.personal_configuration_path / f"{self.tool_prefix}local_config.yaml"
        if not local_config_path.exists():
            shutil.copy(self.default_cfg_path, str(local_config_path))

    def resetPaths(self, force_local=None):
        global_paths_cfg_path = Path(f"./{self.tool_prefix}global_paths_cfg.yaml")
        
        if force_local is None:
            if global_paths_cfg_path.exists():
                force_local = True
            else:
                force_local = False
        print(f"To make it clear where your data are stored, we now give the user the choice where to put its data.")
        print(f"This allows you to mutualize models which are heavy, between multiple lollms compatible apps.")
        print(f"You can change this at any time using the lollms-settings script or by simply change the content of the global_paths_cfg.yaml file.")
        found = False
        while not found:
            print(f"Please provide a folder to store your configurations files, your models and your personal data (database, custom personalities etc).")
            cfg = BaseConfig(config={
                "lollms_path":str(Path(__file__).parent),
                "lollms_personal_path":str(Path("../personal_data"))
            })

            cfg.lollms_personal_path = input(f"Folder path: ({cfg.lollms_personal_path}):")
            if cfg.lollms_personal_path=="":
                cfg.lollms_personal_path = str(Path("../personal_data"))

            print(f"Selected: {cfg.lollms_personal_path}")
            pp= Path(cfg.lollms_personal_path)
            if not pp.exists():
                try:
                    pp.mkdir(parents=True)
                except:
                    print(f"{ASCIIColors.color_red}It seams there is an error in the path you rovided{ASCIIColors.color_reset}")
                    continue
            if force_local:
                global_paths_cfg_path = Path(f"./{self.tool_prefix}global_paths_cfg.yaml")
            else:
                global_paths_cfg_path = Path.home()/f"{self.tool_prefix}global_paths_cfg.yaml"
            cfg.save_config(global_paths_cfg_path)
            found = True
        
        return LollmsPaths(global_paths_cfg_path, cfg.lollms_path, cfg.lollms_personal_path, custom_default_cfg_path=self.default_cfg_path)        

    @staticmethod
    def find_paths(force_local=False, custom_default_cfg_path=None, custom_global_paths_cfg_path=None, tool_prefix="", force_personal_path=None):
        lollms_path = Path(__file__).parent
        if custom_global_paths_cfg_path is None:
            global_paths_cfg_path = Path(f"./{tool_prefix}global_paths_cfg.yaml")
        else:
            global_paths_cfg_path = Path(custom_global_paths_cfg_path)

        ASCIIColors.cyan(f"Trying to use Configuration at :{global_paths_cfg_path}")
        if global_paths_cfg_path.exists():
            ASCIIColors.green(f"{global_paths_cfg_path} found!")
            try:
                cfg = BaseConfig()
                cfg.load_config(global_paths_cfg_path)
                #lollms_path = cfg.lollms_path
                lollms_personal_path = cfg.lollms_personal_path

                if(not Path(lollms_personal_path).exists()):
                    ASCIIColors.warning("One of the paths does not exist lollms_path or lollms_personal_path")
                    ASCIIColors.warning(f"{lollms_path}")
                    ASCIIColors.warning(f"{lollms_personal_path}")
                    raise Exception("Wrong configuration file")
                return LollmsPaths(global_paths_cfg_path, lollms_path, lollms_personal_path, tool_prefix=tool_prefix)
            except Exception as ex:
                ASCIIColors.error(f"Global paths configuration file found but seems to be corrupted")
                trace_exception(ex)
                print("Couldn't find your personal data path!")
                cfg.lollms_path = lollms_path
                cfg["lollms_personal_path"] = str(Path("../personal_data"))
                print("Please specify the folder where your configuration files, your models and your custom personalities need to be stored:")
                lollms_personal_path = input(f"Folder path: ({cfg.lollms_personal_path}):")
                if lollms_personal_path!="":
                    cfg.lollms_personal_path=lollms_personal_path
                cfg.save_config(global_paths_cfg_path)
                lollms_path = cfg.lollms_path
                lollms_personal_path = cfg.lollms_personal_path
                return LollmsPaths(global_paths_cfg_path, lollms_path, lollms_personal_path, custom_default_cfg_path=custom_default_cfg_path, tool_prefix=tool_prefix)
        else:
            ASCIIColors.red(f"{global_paths_cfg_path} not found! Searching in your home folder.")
            # if the app is not forcing a specific path, then try to find out if the default installed library has specified a default path
            global_paths_cfg_path = Path.home()/f"{tool_prefix}global_paths_cfg.yaml"
            if global_paths_cfg_path.exists():
                ASCIIColors.green(f"{global_paths_cfg_path} found!")
                cfg = BaseConfig()
                cfg.load_config(global_paths_cfg_path)
                try:
                    # lollms_path = cfg.lollms_path
                    lollms_personal_path = cfg.lollms_personal_path
                    return LollmsPaths(global_paths_cfg_path, lollms_path, lollms_personal_path, custom_default_cfg_path=custom_default_cfg_path, tool_prefix=tool_prefix)
                except Exception as ex:
                    print(f"{ASCIIColors.color_red}Global paths configuration file found but seems to be corrupted{ASCIIColors.color_reset}")
                    cfg.lollms_path = Path(__file__).parent
                    cfg.lollms_personal_path = input("Please specify the folder where your configuration files, your models and your custom personalities need to be stored:")
                    cfg.save_config(global_paths_cfg_path)
                    lollms_path = cfg.lollms_path
                    lollms_personal_path = cfg.lollms_personal_path
                    return LollmsPaths(global_paths_cfg_path, lollms_path, lollms_personal_path, custom_default_cfg_path=custom_default_cfg_path, tool_prefix=tool_prefix)
            else: # First time 
                if force_personal_path is not None:
                    cfg = BaseConfig(config={
                        "lollms_path":str(Path(__file__).parent),
                        "lollms_personal_path":force_personal_path
                    })
                    print(f"Selected: {cfg.lollms_personal_path}")
                    pp= Path(cfg.lollms_personal_path)
                    if not pp.exists():
                        try:
                            pp.mkdir(parents=True)
                        except:
                            print(f"{ASCIIColors.color_red}It seams there is an error in the path you rovided{ASCIIColors.color_reset}")
                    if force_local:
                        global_paths_cfg_path = Path(f"./{tool_prefix}global_paths_cfg.yaml")
                    else:
                        global_paths_cfg_path = Path.home()/f"{tool_prefix}global_paths_cfg.yaml"
                    cfg.save_config(global_paths_cfg_path)
                    found = True
                else:
                    print(f"{ASCIIColors.color_green}Welcome! It seems this is your first use of the new lollms app.{ASCIIColors.color_reset}")
                    print(f"To make it clear where your data are stored, we now give the user the choice where to put its data.")
                    print(f"This allows you to mutualize models which are heavy, between multiple lollms compatible apps.")
                    print(f"You can change this at any time using the lollms-settings script or by simply change the content of the global_paths_cfg.yaml file.")
                    found = False
                    while not found:
                        print(f"Please provide a folder to store your configurations files, your models and your personal data (database, custom personalities etc).")
                        cfg = BaseConfig(config={
                            "lollms_path":str(Path(__file__).parent),
                            "lollms_personal_path":str(Path("../personal_data"))
                        })
                        cfg.lollms_personal_path = input(f"Folder path: ({cfg.lollms_personal_path}):")
                        if cfg.lollms_personal_path=="":
                            cfg.lollms_personal_path = str(Path("../personal_data"))

                        print(f"Selected: {cfg.lollms_personal_path}")
                        pp= Path(cfg.lollms_personal_path)
                        if not pp.exists():
                            try:
                                pp.mkdir(parents=True)
                            except:
                                print(f"{ASCIIColors.color_red}It seams there is an error in the path you rovided{ASCIIColors.color_reset}")
                                continue
                        if force_local:
                            global_paths_cfg_path = Path(f"./{tool_prefix}global_paths_cfg.yaml")
                        else:
                            global_paths_cfg_path = Path.home()/f"{tool_prefix}global_paths_cfg.yaml"
                        cfg.save_config(global_paths_cfg_path)
                        found = True
                
                return LollmsPaths(global_paths_cfg_path, cfg.lollms_path, cfg.lollms_personal_path, custom_default_cfg_path=custom_default_cfg_path, tool_prefix=tool_prefix)
            
            
    @staticmethod     
    def reset_configs(tool_prefix=""):
        lollms_path = Path(__file__).parent
        global_paths_cfg_path = Path(f"./{tool_prefix}global_paths_cfg.yaml")
        if global_paths_cfg_path.exists():
            ASCIIColors.error("Resetting local settings")
            global_paths_cfg_path.unlink()
            return
        global_paths_cfg_path = Path.home()/f"{tool_prefix}global_paths_cfg.yaml"
        if global_paths_cfg_path.exists():
            ASCIIColors.error("Resetting global settings")
            global_paths_cfg_path.unlink()


