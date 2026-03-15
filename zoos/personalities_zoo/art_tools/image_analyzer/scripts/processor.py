import subprocess
from pathlib import Path
import os
import sys
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate, InstallOption
from lollms.types import MSG_OPERATION_TYPE
from typing import Any

from lollms.helpers import ASCIIColors, trace_exception
from lollms.personality import APScript, AIPersonality
import time
from pathlib import Path
from lollms.client_session import Client
from lollms.types import MSG_OPERATION_TYPE

import sys
sys.path.append(str(Path(__file__).parent))
import torch
from torchvision import transforms
from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from lollms.utilities import check_and_install_torch
from typing import Callable, Any
from lollms.prompting import LollmsContextDetails
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
        shared_folder = root_dir/"shared"
        self.sd_folder = shared_folder / "auto_sd"
        
        self.callback = None
        self.sd = None
        self.previous_sd_positive_prompt = None
        self.sd_negative_prompt = None

        personality_config_template = ConfigTemplate(
            [
                {"name":"device","type":"str","value":"cuda" if personality.config.hardware_mode=="nvidia-tensorcores" or personality.config.hardware_mode=="nvidia" else "cpu",'options':['cpu','cuda'],"help":"Imagine the images"},
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
                            callback=callback
                        )
        self.model = None

    def install(self):
        super().install()
        if self.config.hardware_mode=="cpu-noavx":
            check_and_install_torch(False)
        elif self.config.hardware_mode=="cpu":
            check_and_install_torch(False)
        elif self.config.hardware_mode=="amd-noavx":
            check_and_install_torch(False)
        elif self.config.hardware_mode=="amd":
            check_and_install_torch(False)
        elif self.config.hardware_mode=="nvidia":
            check_and_install_torch(True)
        elif self.config.hardware_mode=="nvidia-tensorcores":
            check_and_install_torch(True)
        elif self.config.hardware_mode=="apple-intel":
            check_and_install_torch(False)
        elif self.config.hardware_mode=="apple-silicon":
            check_and_install_torch(False)

        
        requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Install dependencies using pip from requirements.txt
        subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])      
        ASCIIColors.success("Installed successfully")

    def prepare(self):
        if self.model is None:
            self.new_message("",MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI)
            self.step_start("Loading Blip")
            self.model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-2.7b").to(self.personality_config.device)
            self.processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b").to(self.personality_config.device)
            self.step_end("Loading Blip")
            self.finished_message()


    def add_file(self, path, client, callback=None):
        self.prepare()
        if callback is None and self.callback is not None:
            callback = self.callback
        try:
            self.new_message("", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK)
            pth = str(path).replace("\\","/").split('/')
            idx = pth.index("uploads")
            pth = "/".join(pth[idx:])
            file_path = f"![](/{pth})\n"


            # only one path is required
            self.raw_image = Image.open(path).convert('RGB')
            self.personality.image_files = [path]
            inputs = self.processor(self.raw_image, return_tensors="pt").to(self.personality_config.device) #"cuda")
            def local_callback(output):
                token = output.argmax(dim=-1)
                token_str = self.processor.decode(token)
                self.set_message_content(token_str, callback=callback)
                print(token_str, end='')
            print("Processing...")
            output = self.processor.decode(self.model.generate(**inputs, max_new_tokens=self.personality.app.config.max_n_predict)[0], skip_special_tokens=True, callback=local_callback)
            print("Image description: "+output)
            self.set_message_content(f"File added successfully\nImage description :\n{output}\nImage:\n!{file_path}", callback=callback)
            self.finished_message()
            return True
        except Exception as ex:
            trace_exception(ex)
            print("Couldn't load file. PLease check the profided path.")
            return False

    def remove_file(self, path):
        # only one path is required
        self.image_files = []

    def remove_text_from_string(self, string, text_to_find):
        """
        Removes everything from the first occurrence of the specified text in the string (case-insensitive).

        Parameters:
        string (str): The original string.
        text_to_find (str): The text to find in the string.

        Returns:
        str: The updated string.
        """
        index = string.lower().find(text_to_find.lower())

        if index != -1:
            string = string[:index]

        return string
    
    def process(self, text):
        bot_says = self.bot_says + text
        antiprompt = self.personality.detect_antiprompt(bot_says)
        if antiprompt:
            self.bot_says = self.remove_text_from_string(bot_says,antiprompt)
            print("Detected hallucination")
            return False
        else:
            self.bot_says = bot_says
            return True

    def generate(self, prompt, max_size):
        self.bot_says = ""
        return self.personality.model.generate(
                                prompt, 
                                max_size, 
                                self.process,
                                temperature=self.personality.model_temperature,
                                top_k=self.personality.model_top_k,
                                top_p=self.personality.model_top_p,
                                repeat_penalty=self.personality.model_repeat_penalty,
                                ).strip()    
        

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
        try:
            inputs = self.processor(self.raw_image, f"{previous_discussion_text}{self.personality.link_text}{self.personality.ai_message_prefix}", return_tensors="pt").to(self.personality_config.device) #"cuda")
            def local_callback(output):
                token = output.argmax(dim=-1)
                token_str = self.processor.decode(token)
                if callback is not None:
                    callback(token_str, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK)
                else:
                    print(token_str, end='')


            output = self.processor.decode(self.model.generate(**inputs, max_new_tokens=self.personality.app.config.max_n_predict)[0], skip_special_tokens=True, callback=local_callback)
        except Exception as ex:
            print(ex)
            trace_exception(ex)
            output = "There seems to be a problem with your image, please upload a valid image to talk about"
        
        self.set_message_content(output)
        return output


