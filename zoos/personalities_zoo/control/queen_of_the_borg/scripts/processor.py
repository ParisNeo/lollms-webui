from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality
from lollms.utilities import PackageManager
from lollms.types import MSG_OPERATION_TYPE
from typing import Callable, Any
from ascii_colors import trace_exception
from lollms.prompting import LollmsContextDetails

from pathlib import Path
from typing import List
if PackageManager.check_package_installed("pygame"):
    import pygame
else:
    PackageManager.install_package("pygame")
    import pygame

pygame.mixer.init()
import subprocess

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
        # Example entry
        #       {"name":"make_scripted","type":"bool","value":False, "help":"Makes a scriptred AI that can perform operations using python script"},
        # Supported types:
        # str, int, float, bool, list
        # options can be added using : "options":["option1","option2"...]        
        personality_config_template = ConfigTemplate(
            [
                
                {"name":"nb_attempts","type":"int","value":5, "help":"Maximum number of attempts to summon a drone"},
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
        
    def install(self):
        super().install()
        
        # requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Install dependencies using pip from requirements.txt
        # subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])      
        ASCIIColors.success("Installed successfully")        

    def mounted(self):
        """
        triggered when mounted
        """
        pass

    def play_mp3(self, file_path):
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

    def selected(self):
        """
        triggered when mounted
        """
        self.play_mp3(Path(__file__).parent.parent/"assets"/"borg_threat.mp3")

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

        self.callback = callback
        ASCIIColors.info("Generating")
        collective:List[AIPersonality] = self.personality.app.mounted_personalities


        answer = ""
        q_prompt = f"{self.system_full_header}You are the queen of borgs, you are a great leader and you know which drone is most suitable to answer the user request.\n"
        q_prompt += f"{self.user_full_header}{prompt}\n"
        attempts = 0




        self.step_start("Summoning collective")
        while attempts<self.personality_config.nb_attempts:
            try:
                selection = self.multichoice_question('which drone is the best to fulfill the user request?',[f"{drone.name} : {drone.personality_description[:4000]}" for drone in collective],q_prompt)
                q_prompt += f"{selection}\n"
                self.step_end("Summoning collective")
                self.step(f"Selected drone {collective[selection]}")
                collective[selection].callback=callback

                q_prompt += f"{self.system_full_header}Reformulate the question for the drone.{self.config.separator_template}{self.ai_custom_header(collective[selection].name)}"
                if collective[selection].processor and collective[selection].name!="Queen of the Borg":
                    reformulated_request=self.fast_gen(q_prompt, show_progress=True)
                    self.set_message_content(f"{collective[selection].name}, {reformulated_request}")
                    previous_discussion_text= previous_discussion_text.replace(prompt,reformulated_request)
                    collective[selection].new_message("")
                    collective[selection].set_message_content(f"At your service my queen.\n")
                    collective[selection].processor.text_files = self.personality.text_files
                    collective[selection].processor.image_files = self.personality.image_files
                    context_details.prompt = reformulated_request
                    collective[selection].processor.run_workflow(context_details, client, callback)
                else:
                    if collective[selection].name!="Queen of the Borg":
                        reformulated_request=self.fast_gen(q_prompt, show_progress=True)
                        self.set_message_content(f"{collective[selection].name}, {reformulated_request}")
                        previous_discussion_text= previous_discussion_text.replace(prompt,reformulated_request)
                        collective[selection].new_message("")
                        collective[selection].set_message_content(f"At your service my queen.\n")
                    collective[selection].generate(previous_discussion_text,callback=callback)
                break
            except Exception as ex:
                trace_exception(ex)
                self.step_end("Summoning collective", False)
                attempts += 1
        return answer

