"""
project: lollms
personality: # Place holder: Personality name 
Author: # Place holder: creator name 
description: # Place holder: personality description
"""
from lollms.types import MSG_OPERATION_TYPE
from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality
import subprocess
from typing import Callable, Any
from lollms.prompting import LollmsContextDetails

# Helper functions
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
        # Example entries
        #       {"name":"make_scripted","type":"bool","value":False, "help":"Makes a scriptred AI that can perform operations using python script"},
        #       {"name":"make_scripted","type":"bool","value":False, "help":"Makes a scriptred AI that can perform operations using python script"},
        # Supported types:
        # str, int, float, bool, list
        # options can be added using : "options":["option1","option2"...]        
        personality_config_template = ConfigTemplate(
            [
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
                                    "commands": { # list of commands (don't forget to add these to your config.yaml file)
                                        "scan_and_fix_files":self.scan_and_fix_files,
                                        "help":self.help,
                                    },
                                    "default": None
                                },                           
                            ],
                            callback=callback
                        )
        
    def install(self):
        super().install()
        
        # requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Install dependencies using pip from requirements.txt
        # subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])      
        ASCIIColors.success("Installed successfully")        

    def help(self, prompt="", full_context=""):
        self.set_message_content(self.personality.help)
    

    def process_data(self, title, chunk, message = ""):
        self.step_start(f"Processing {title}")
        prompt = self.build_prompt([
            f"{self.config.start_header_id_template}{self.config.system_message_template}{self.config.end_header_id_template}Read the code chunk and try to detect any portential vulenerabilities. Point out the error by rewriting the code line where it occures, then propose a fix to it with a small example.",
            f"{self.config.start_header_id_template}code:\n",
            chunk,
            f"{self.config.start_header_id_template}analysis:\n"
        ])
        self.step_end(f"Processing {title}")
        analysis = self.fast_gen(prompt)
        message += analysis
        self.set_message_content(message)
        return message

    def scan_and_fix_files(self, prompt="", full_context=""):
        self.new_message("")
        if len(self.personality.text_files)==0:
            self.set_message_content("Please send me the files you want me to analyze through the add file button in the chat tab of Lollms-webui.")
        else:
            message =""
            for txt_pth in self.personality.text_files:
                with open(txt_pth,"r",encoding="utf-8") as f:
                    txt = f.read()
                tk = self.personality.model.tokenize(txt)
                message +=f"<h2>{txt_pth}</h2>\n"
                if len(tk)<self.personality.config.ctx_size/2:
                    message = self.process_data(f"{txt_pth}",txt, message)
                else:
                    self.step_start(f"Chunking file {txt_pth}")
                    cs = int(self.personality.config.ctx_size/2)
                    n = int(len(tk)/(cs))+1
                    last_pos = 0
                    chunk_id = 0
                    while last_pos<len(tk):
                        message +=f"<h3>chunk : {chunk_id+1}</h3>\n"
                        chunk = tk[last_pos:last_pos+cs]
                        last_pos= last_pos+cs
                        message = self.process_data(f"{txt_pth} chunk {chunk_id+1}/({n+1})", self.personality.model.detokenize(chunk), message)
                        chunk_id += 1
                    self.step_end(f"Chunking file {txt_pth}")



    def add_file(self, path, client, callback=None):
        """
        Here we implement the file reception handling
        """
        super().add_file(path, client, callback)

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
        self.personality.info("Generating")
        self.callback = callback
        out = self.fast_gen(previous_discussion_text)
        self.set_message_content(out)
        return out

