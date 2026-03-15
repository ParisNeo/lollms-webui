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
from lollms.prompting import LollmsContextDetails
import subprocess
from typing import Callable, Any

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
                {"name":"current_conditionning","type":"str","value":"", "help":"Adaptix is a self reprogramming AI, the conditionning is rewri"},
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
        self.personality.info("Rewriting Adaptix")
        self.callback = callback
        new_conditionning = self.fast_gen("\n".join([
           f"{self.config.start_header_id_template}{self.config.system_message_template}{self.config.end_header_id_template}Build a new system prompt to adapt Adaptix to the current user request. if no changes are needed, then respond with the current system prompt.",
           context_details.conditionning,
           context_details.discussion_messages,
           f"{self.config.start_header_id_template}adaptix:"
           "Here is the new system prompt that is fine tuned to maximize the probability that the AI acheives the requested task:"
        ]), callback=self.sink)
        self.personality_config.current_conditionning=new_conditionning
        self.set_message_content(new_conditionning)
        self.personality.info("Generating")
        self.callback = callback
        out = self.fast_gen("\n".join([
           f"{self.config.start_header_id_template}{self.config.system_message_template}{self.config.end_header_id_template}{self.personality_config.current_conditionning}",
           context_details.discussion_messages,
           context_details.documentation,
           context_details.user_description,
           context_details.discussion_messages,
           f"{self.config.start_header_id_template}current user prompt:",
           prompt,
           context_details.positive_boost,
           context_details.negative_boost,
           context_details.current_language,
           context_details.fun_mode,
           f"{self.config.start_header_id_template}adaptix:"]))
        self.set_message_content(out)
        return out

