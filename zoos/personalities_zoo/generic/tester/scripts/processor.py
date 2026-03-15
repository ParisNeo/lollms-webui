from fastapi import APIRouter, Request
from typing import Dict, Any
import subprocess
from pathlib import Path
from lollms.helpers import ASCIIColors, trace_exception
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate, InstallOption
from lollms.types import MSG_OPERATION_TYPE
from lollms.personality import APScript, AIPersonality
from lollms.prompting import LollmsContextDetails
import json
from typing import Callable, Any
import shutil
import yaml



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

        personality_config_template = ConfigTemplate(
            [
                {"name":"test_boolean","type":"bool","value":True,"help":"Test a boolean checkbox"},
                {"name":"test_multichoices","type":"str","value":"Euler a", "options":["Choice 1","Choice 2","Choice 3"], "help":"Tests multichoices select"},                
                {"name":"test_float","type":"float","value":7.5, "min":0.01, "max":1.0, "help":"tests float"},
                {"name":"test_int","type":"int","value":50, "min":10, "max":1024, "help":"tests int"},
                {"name":"test_str","type":"str","value":"test", "help":"tests string"},
                
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
                                        "test_new_message":self.test_new_message,
                                        "test_goto_state1":self.test_goto_state1,
                                    },
                                    "default": self.idle
                                }, 
                                {
                                    "name": "state1",
                                    "commands": { # list of commands
                                        "help":self.help,
                                        "test_goto_idle":self.test_goto_idle,
                                    },
                                    "default": self.state1
                                },                                                           
                            ],
                            callback=callback
                        )
        
    def install(self):
        super().install()
        
        requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Install dependencies using pip from requirements.txt
        subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])      

        ASCIIColors.success("Installed successfully")



    def help(self, prompt, full_context):
        self.set_message_content(self.personality.help)
    
    def test_new_message(self, prompt, full_context):
        self.new_message("Starting fresh :)", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT)
        
    def test_goto_state1(self, prompt, full_context):
        self.goto_state("state1")
        
    def test_goto_idle(self, prompt, full_context):
        self.goto_state("idle")
        
        
        
    def add_file(self, path, client, callback=None):
        if callback is None and self.callback is not None:
            callback = self.callback
        ASCIIColors.yellow("Testing add file")
        super().add_file(path, client, callback)


    async def handle_request(self, data: dict, client:Client=None) -> Dict[str, Any]:
        """
        Handle client requests.

        Args:
            data (dict): A dictionary containing the request data.
            client (Client): A refertence to the client asking for this request.

        Returns:
            dict: A dictionary containing the response, including at least a "status" key.

        This method should be implemented by a class that inherits from this one.

        Example usage:
        ```
        handler = YourHandlerClass()
        client = checkaccess(lollmsServer, client_id)
        request_data = {"command": "some_command", "parameters": {...}}
        response = handler.handle_request(request_data, client)
        ```
        """        
        personality_subpath = data['personality_subpath']
        logo_path = data['logo_path']
        assets_path:Path = self.personality.lollms_paths.personalities_zoo_path / "personal" / personality_subpath / "assets"

        shutil.copy(logo_path, assets_path/"logo.png")
        return {"status":True}


    def make_selectable_photo(self, image_id, image_source, params=""):
        return f"""
        <div class="flex items-center cursor-pointer justify-content: space-around">
            <img id="{image_id}" src="{image_source}" alt="Artbot generated image" class="object-cover cursor-pointer" style="width:300px;height:300px" onclick="console.log('Selected');"""+"""
            fetch('/post_to_personality', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({"""+f"""
                {params}"""+"""})
            })">
        </div>
        """
    # States ================================================
    def idle(self, prompt, full_context):    
         self.set_message_content("testing responses and creating new json message")
         self.new_message("json data", MSG_OPERATION_TYPE.MSG_TYPE_JSON_INFOS,{'test':{'value':1,'value2':2},'test2':['v1','v2']})
         file_id = 721
         personality_path:Path = self.personality.lollms_paths.personal_outputs_path / self.personality.personality_folder_name
         personality_path="/".join(str(personality_path).replace('\\','/').split('/')[-2:])
         pth = "outputs/sd/Artbot_721.png"
         self.set_message_html('<img src="outputs/sd/Artbot_721.png">')
         self.new_message(self.make_selectable_photo("721", "outputs/sd/Artbot_721.png", params="param1:0"), MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI)
         self.new_message("Testing generation", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT)
         out = self.generate("explain what is to be human",50,callback = self.callback)
         self.set_message_content(out)
        
    def state1(self, prompt, full_context):    
         self.set_message_content("testing responses from state 1", callback=self.callback)
    

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

