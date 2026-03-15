from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality
from lollms.prompting import LollmsContextDetails
from lollms.types import MSG_OPERATION_TYPE
from typing import Any
import subprocess
from pathlib import Path
# Helper functions
import csv
from pathlib import Path
import importlib
import shutil
from typing import Callable, Any

class Processor(APScript):
    """
    A class that processes model inputs and outputs.

    Inherits from APScript.
    """
    def __init__(
                 self, 
                 personality: AIPersonality,
                 callback = None,
                ) -> None:
        
        self.callback = None
        # Get the current directory
        root_dir = personality.lollms_paths.personal_path
        # We put this in the shared folder in order as this can be used by other personalities.
        shared_folder = root_dir/"shared"
        self.sd_folder = shared_folder / "auto_sd"    
        self.output_folder = personality.lollms_paths.personal_outputs_path/"nft_reshaper"
        self.output_folder.mkdir(parents=True, exist_ok=True)
        # Example entry
        #       {"name":"make_scripted","type":"bool","value":False, "help":"Makes a scriptred AI that can perform operations using python script"},
        # Supported types:
        # str, int, float, bool, list
        # options can be added using : "options":["option1","option2"...]
        personality_config_template = ConfigTemplate(
            [
                {"name":"folder_path","type":"str","value":"", "help":"The folder containing the files of the nft collection"},
            ]
            )
        personality_config_vals = BaseConfig.from_template(personality_config_template)

        personality_config = TypedConfig(
            personality_config_template,
            personality_config_vals
        )
        super().__init__(
                            personality,
                            personality_config,
                            [
                                {
                                    "name": "idle",
                                    "commands": { # list of commands
                                        "help":self.help,
                                    },
                                    "default": None
                                },                           
                            ],
                            callback=callback
                        )
        self.sd = None
        
    def install(self):
        super().install()
        
        requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Install dependencies using pip from requirements.txt
        subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])      
        ASCIIColors.success("Installed successfully")

    def help(self, prompt="", full_context=""):
        self.set_message_content(self.personality.help)
    
    def add_file(self, path, client, callback=None):
        """
        Here we implement the file reception handling
        """
        super().add_file(path, client, callback)

        
    def prepare(self):
        if self.sd is None:
            from lollms.services.tti.sd.lollms_sd import LollmsSD
            self.step_start("Loading ParisNeo's fork of AUTOMATIC1111's stable diffusion service")
            self.sd = LollmsSD.get()(self.personality.lollms_paths, "Artbot", max_retries=-1)
            self.step_end("Loading ParisNeo's fork of AUTOMATIC1111's stable diffusion service")

    def create_csv_from_folder(self, path):
        counter = 1
        rows = []
        
        folder_path = Path(path)
        all_descriptions=""
        for file_path in folder_path.glob('*.png'):
            name = file_path.stem
            filename = file_path.name
            shutil.copy(file_path, self.output_folder/filename)

            external_url = ""
            self.step_start(f"Processing : {name}")
            description = self.sd.interrogate(str(file_path)).info
            self.print_prompt("Blip description",description)

            description = self.fast_gen(f"@!>Instruction:Make a description of this png file: {filename} out of the fast description and the file name.\n@!>Fast description:{description}\n@!>Description:",256).replace("\"","")
            style_collection = file_path.parent.name
            all_descriptions += f"## {name}\n![](outputs/nft_reshaper/{filename})\n{description}\n"
            self.set_message_content(all_descriptions)
            rows.append([counter, name, description, filename, external_url, style_collection])
            self.step_end(f"Processing : {name}")
            counter += 1
        
        with open(file_path.parent/"metadata.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["tokenID", "name", "description", "file_name", "external_url", "attributes[style_collection]"])
            writer.writerows(rows)

    from lollms.client_session import Client
    def run_workflow(self,  context_details:LollmsContextDetails=None, client:Client=None,  callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, AIPersonality| None], bool]=None):
        """
        This function generates code based on the given parameters.

        Args:
            context_details (dict): A dictionary containing the following context details for code generation:
                - conditionning (str): The conditioning information.
                - documentation (str): The documentation information.
                - knowledge (str): The knowledge information.
                - user_description (str): The user description information.
                - discussion_messages (str): The discussion messages information.
                - positive_boost (str): The positive boost information.
                - negative_boost (str): The negative boost information.
                - current_language (str): The force language information.
                - fun_mode (str): The fun mode conditionning text
                - ai_prefix (str): The AI prefix information.
            client_id: The client ID for code generation.
            callback (function, optional): The callback function for code generation.

        Returns:
            None
        """
        prompt = context_details.prompt
        previous_discussion_text = context_details.discussion_messages
        self.callback = callback
        self.prepare()

        if self.personality_config.folder_path!="":
            self.create_csv_from_folder(self.personality_config.folder_path)
        else:
            self.set_message_content("Please specify a valid folder path in the configurations of the personality")
        return ""

