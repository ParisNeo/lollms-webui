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
from lollms.utilities import discussion_path_to_url, PackageManager, find_first_available_file_index
from lollms.client_session import Client
from lollms.functions.take_screen_shot import take_screenshot_function
from lollms.functions.calculator import calculate_function
from lollms.functions.take_a_photo import take_a_photo_function
from lollms.functions.generate_image import build_image_function
from lollms.functions.peripherals import move_mouse_to_position_function, press_mouse_button_function, type_text_function
from lollms.functions.timers import set_timer_with_alert_function
from lollms.functions.music_gen import open_and_fill_udio_function, open_and_fill_suno_function
from lollms.prompting import LollmsContextDetails

from typing import Callable, Any
from functools import partial
from ascii_colors import trace_exception

if not PackageManager.check_package_installed("pyautogui"):
    PackageManager.install_package("pyautogui")
if not PackageManager.check_package_installed("cv2"):
    PackageManager.install_package("opencv-python")

import pyautogui


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
                # Boolean configuration for enabling scripted AI
                {"name":"activate_function_call", "type":"bool", "value":False, "help":"This will activate function call"},
                {"name":"make_song_in_suno_ai", "type":"bool", "value":False, "help":"This will build the song in suno. ai after writing it"},
                {"name":"make_song_in_udio", "type":"bool", "value":False, "help":"This will build the song in udio. ai after writing it"},
                {"name":"clean_images_between_sessions", "type":"bool", "value":False, "help":"This will remove images between two prompts"},

                {"name":"hide_function_call", "type":"bool", "value":False, "help":"Hides the function call commands."},
                {"name":"allow_infinete_operations", "type":"bool", "value":True, "help":"If checked, the AI will be able to do much more complex operations that involve multi steps interactions"},
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



    def move_mouse_to(self, x, y):
        pyautogui.moveTo(x, y)

    def click_mouse(self, x, y):
        pyautogui.click(x, y)




        
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
        # self.process_state(prompt, previous_discussion_text, callback, context_details, client)
        if self.personality_config.clean_images_between_sessions:
            self.personality.image_files.clear()
        # TODO: add more functions to call
        if self.personality_config.activate_function_call:
            self.function_definitions = [
                build_image_function(self, client),
            ]
            if self.personality_config.make_song_in_udio:
                self.function_definitions.append(open_and_fill_udio_function())
            if self.personality_config.make_song_in_suno_ai:
                self.function_definitions.append(open_and_fill_suno_function())

            out = self.interact_with_function_call(context_details, self.function_definitions,hide_function_call=self.personality_config.hide_function_call, separate_output=True)
            self.set_message_content(out)
        else:
            if len(self.personality.image_files)>0:
                self.fast_gen_with_images(previous_discussion_text, self.personality.image_files)
            else:
                self.fast_gen(previous_discussion_text)



