"""
Project: LoLLMs
Personality: # Placeholder: Personality name (e.g., "Science Enthusiast")
Author: # Placeholder: Creator name (e.g., "ParisNeo")
Description: # Placeholder: Personality description (e.g., "A personality designed for enthusiasts of science and technology, promoting engaging and informative interactions.")
"""

from lollms.types import MSG_OPERATION_TYPE
from typing import Any

from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality
from lollms.client_session import Client
from lollms.functions.generate_image import build_image, build_image_function
from lollms.functions.select_image_file import select_image_file_function
from lollms.functions.take_a_photo import take_a_photo_function
from lollms.prompting import LollmsContextDetails

from lollms.utilities import discussion_path_to_url
import subprocess
from typing import Callable, Any
from functools import partial
from ascii_colors import trace_exception

class Processor(APScript):
    """
    Defines the behavior of a personality in a programmatic manner, inheriting from APScript.
    
    Attributes:
        callback (Callable): Optional function to call after processing.
    """
    
    def __init__(
                 self, 
                 personality: AIPersonality,
                 callback: Callable = None,
                ) -> None:
        """
        Initializes the Processor class with a personality and an optional callback.

        Parameters:
            personality (AIPersonality): The personality instance.
            callback (Callable, optional): A function to call after processing. Defaults to None.
        """
        
        self.callback = callback
        
        # Configuration entry examples and types description:
        # Supported types: int, float, str, string (same as str, for back compatibility), text (multiline str),
        # btn (button for special actions), bool, list, dict.
        # An 'options' entry can be added for types like string, to provide a dropdown of possible values.
        personality_config_template = ConfigTemplate(
            [
                {"name":"models_to_use","type":"str","value":"", "help":"This is only if you need to use multi models for this personality. List of coma separated models to test in format binding_name::model_name"},
                {"name":"master_model","type":"str","value":"", "help":"This is only if you need to use multi models for this personality. A single powerful model in format binding_name::model_name which is going to judge the other models based on the human test file. This model will just compare the output of the model and the human provided answer."},
                {"name":"nb_rounds","type":"int","value":2, "help":"This is only if you need to use multi models for this personality. The number of rounds in the generation process."},
                {"name":"mode","type":"str","value":"discussion_long","options":["discussion_long","discussion_medium","discussion_short"], "help":"This sets how the AI builds code. The long version assumes large context and rewrites everything every time. The medium one writes the whole code the first time then does modifications on the code that are automatically stitched together by the software. The small one will only build snippets."},
                {"name":"use_explainer","type":"bool","value":True, "help":"If true, then explain the code before writing it."},

                # Boolean configuration for enabling scripted AI
                #{"name":"make_scripted", "type":"bool", "value":False, "help":"Enables a scripted AI that can perform operations using python scripts."},
                
                # String configuration with options
                #{"name":"response_mode", "type":"string", "options":["verbose", "concise"], "value":"concise", "help":"Determines the verbosity of AI responses."},
                
                # Integer configuration example
                #{"name":"max_attempts", "type":"int", "value":3, "help":"Maximum number of attempts for retryable operations."},
                
                # List configuration example
                #{"name":"favorite_topics", "type":"list", "value":["AI", "Robotics", "Space"], "help":"List of favorite topics for personalized responses."}
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
                            states_list=[
                                {
                                    "name": "idle",
                                    "commands": {
                                        "help": self.help, # Command triggering the help method
                                    },
                                    "default": None
                                },                           
                            ],
                            callback=callback
                        )
    

    def mounted(self):
        """
        triggered when mounted
        """
        pass


    def selected(self):
        """
        triggered when selected
        """
        pass
        # self.play_mp3(Path(__file__).parent.parent/"assets"/"borg_threat.mp3")


    # Note: Remember to add command implementations and additional states as needed.

    def install(self):
        """
        Install the necessary dependencies for the personality.

        This method is responsible for setting up any dependencies or environment requirements
        that the personality needs to operate correctly. It can involve installing packages from
        a requirements.txt file, setting up virtual environments, or performing initial setup tasks.
        
        The method demonstrates how to print a success message using the ASCIIColors helper class
        upon successful installation of dependencies. This step can be expanded to include error
        handling and logging for more robust installation processes.

        Example Usage:
            processor = Processor(personality)
            processor.install()
        
        Returns:
            None
        """        
        super().install()
        # Example of implementing installation logic. Uncomment and modify as needed.
        # requirements_file = self.personality.personality_package_path / "requirements.txt"
        # subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])      
        ASCIIColors.success("Installed successfully")

    def help(self, prompt="", full_context=""):
        """
        Displays help information about the personality and its available commands.

        This method provides users with guidance on how to interact with the personality,
        detailing the commands that can be executed and any additional help text associated
        with those commands. It's an essential feature for enhancing user experience and
        ensuring users can effectively utilize the personality's capabilities.

        Args:
            prompt (str, optional): A specific prompt or command for which help is requested.
                                    If empty, general help for the personality is provided.
            full_context (str, optional): Additional context information that might influence
                                          the help response. This can include user preferences,
                                          historical interaction data, or any other relevant context.

        Example Usage:
            processor = Processor(personality)
            processor.help("How do I use the 'add_file' command?")
        
        Returns:
            None
        """
        # Example implementation that simply calls a method on the personality to get help information.
        # This can be expanded to dynamically generate help text based on the current state,
        # available commands, and user context.
        self.set_message_content(self.personality.help)


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
        if context_details.is_continue:
            full_prompt = context_details.build_prompt(self.personality.app.template, suppress= ["ai_prefix"])
        else:
            custom_entries = self.system_custom_header("important information") + "\n"
            if self.personality_config.mode=="discussion_long":
                custom_entries +="Code mode: Always rewrite the full code\n"
            elif self.personality_config.mode=="discussion_medium":
                custom_entries +="Code mode: Write the full code only if this is the first message inside the discussion or if the user asked for a new code. If this is not the first time you write the code, only answer with updates. specify the position of changes\n"
            elif self.personality_config.mode=="discussion_short":
                custom_entries +="Code mode: Only answer with code snippets. The user needs to write the code, you are just his coach and you help him update his code\n"
            if self.personality_config.use_explainer:
                custom_entries +="Explanation Mode: Explain your reasoning and what you are about to change before giving the code."

            full_prompt = context_details.build_prompt(self.personality.app.template, custom_entries)
        if len(self.personality_config.models_to_use)>0:
            out = self.mix_it_up(full_prompt,self.personality_config.models_to_use.split(","), self.personality_config.master_model, nb_rounds=self.personality_config.nb_rounds, callback=self.sink)
            self.json("Rounds details",out)
            out = out["final_output"]
        else:
            out = self.fast_gen(full_prompt)
            nb_tokens = len(self.personality.model.tokenize(out))
            if nb_tokens >= self.config.max_n_predict-1:
                out = out+self.fast_gen(full_prompt+out)

        if not context_details.is_continue:
            self.set_message_content(out)

