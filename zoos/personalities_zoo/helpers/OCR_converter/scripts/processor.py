import subprocess
from pathlib import Path
from lollms.helpers import ASCIIColors, trace_exception
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate, InstallOption
from lollms.types import MSG_OPERATION_TYPE
from lollms.personality import APScript, AIPersonality
from lollms.utilities import PromptReshaper, git_pull, PackageManager
from lollms.prompting import LollmsContextDetails
import re
import importlib
import requests
from typing import Callable, Any
from tqdm import tqdm
import webbrowser
from functools import partial
try:
    if not PackageManager.check_package_installed("pytesseract"):
        PackageManager.install_package("pytesseract")
    if not PackageManager.check_package_installed("PIL"):
        PackageManager.install_package("Pillow")

    import pytesseract
    from PIL import Image
except:
     pass
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
        # Get the current directory
        root_dir = personality.lollms_paths.personal_path
        # We put this in the shared folder in order as this can be used by other personalities.
        
        
        self.callback = callback

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
                                    "commands": { # list of commands
                                    },
                                    "default": self.main_process
                                },                           
                            ],
                            callback=callback
                        )

    def install(self):
        super().install()
        self.info("Please install [tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and add it to the path.")
        requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Install dependencies using pip from requirements.txt
        subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])      
        try:
            ASCIIColors.info("Loading pytesseract and PIL")
            import pytesseract
            from PIL import Image
        except:
            pass

    def add_file(self, path, client, callback=None):
        if self.callback is None and callback==None:
            self.callback = partial(self.personality.app.process_data, client_id = client.client_id)
        elif self.callback is None:
            self.callback = callback
        # Load an image using PIL (Python Imaging Library)
        if callback is None and self.callback is not None:
            callback = self.callback
        super().add_file(path, client, callback, process=False)
        image = Image.open(self.personality.image_files[-1])
        url = str(self.personality.image_files[-1]).replace("\\","/").split("discussion_databases")[-1]
        self.new_message("",MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT)
        output = f'<img src="/discussions{url}">'
        self.set_message_content(output)
        try:
            # Load an image using PIL (Python Imaging Library)
            image = Image.open(self.personality.image_files[-1])

            # Use pytesseract to extract text from the image
            text = pytesseract.image_to_string(image)
            output += "\n<h3>Extracted text:</h3>\n\n"+text
            self.set_message_content(output)
        except Exception as ex:
            self.set_message_content(f"<h3>Looks like you didn't install tesseract correctly</h3><br>\n\nPlease install [tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and add it to the path.\n\nException:{ex}")
        return True
    
    
    def main_process(self, initial_prompt, full_context):
        if len(self.personality.image_files)==0:
            self.set_message_content("<h3>Please send an image file first</h3>")
        else:
            text = self.generate(full_context+initial_prompt,1024, callback=self.callback)
            self.set_message_content(text)
            
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
        self.process_state(prompt, previous_discussion_text, callback)

        return ""

