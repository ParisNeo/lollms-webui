from lollms.types import MSG_OPERATION_TYPE
from typing import Any
from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality
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
                {"name":"template_file","type":"str","value":"", "help":"A template file is a file that contains example of the structure of the code to generate. Just link to a file. The file should contain a structuire and placeholders put as comments. # Placeholder: Here you do this thing. You can place multiple placeholders in your code. Make sure the code is not very long as you may envounter context size problems."},
                {"name":"documentation_file","type":"str","value":"", "help":"A documentation file is a file that contains some documentation that can be used to fill in the placeholders in the template."},
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
        self.settings_updated()
    def settings_updated(self):
        """
        
        """
        if self.personality_config.template_file!="":
            with open(self.personality_config.template_file,"r") as f:
                self.template = f.read()
        else:
            self.template=None
        if self.personality_config.documentation_file!="":
            with open(self.personality_config.documentation_file,"r") as f:
                self.documentation = f.read()
        else:
            self.documentation=None
            
        
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
        if context_details is None:
            self.set_message_content("<b>The context details is none. This is probably due to the fact that you are using an old version of lollms. Please upgrade lollms to use this persona.</b>")
            return ""
        self.personality.info("Generating")
        self.callback = callback
        if self.template is not None:
            crafted_prompt=self.build_prompt([
                                    context_details.conditionning,
                                    context_details.user_description,
                                    f"{self.config.start_header_id_template}template: \n"+self.template,
                                    context_details.documentation,
                                    context_details.discussion_messages,
                                    context_details.positive_boost,
                                    context_details.negative_boost,
                                    context_details.current_language,
                                    context_details.ai_prefix,
            ],5)
        else:
            crafted_prompt=self.build_prompt([
                                    context_details.conditionning,
                                    context_details.user_description,
                                    context_details.documentation,
                                    context_details.discussion_messages,
                                    context_details.positive_boost,
                                    context_details.negative_boost,
                                    context_details.current_language,
                                    context_details.ai_prefix,
            ],4)

        out = self.fast_gen(crafted_prompt)
        self.set_message_content(out)
        return out

