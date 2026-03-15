from fastapi import FastAPI, Request, File, UploadFile
from pydantic import BaseModel
from typing import Optional
import os
import subprocess
from pathlib import Path
from lollms.helpers import ASCIIColors, trace_exception
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate, InstallOption
from lollms.prompting import LollmsContextDetails
from lollms.types import MSG_OPERATION_TYPE
from lollms.personality import APScript, AIPersonality
from lollms.utilities import PromptReshaper, git_pull, output_file_path_to_url, find_next_available_filename, discussion_path_to_url
from lollms.functions.prompting.system_prompts import get_system_prompt, get_random_system_prompt
from lollms.functions.prompting.image_gen_prompts import get_image_gen_prompt, get_random_image_gen_prompt
from lollms.client_session import Client

from lollmsvectordb import VectorDatabase
from lollmsvectordb.text_document_loader import TextDocumentsLoader
from lollmsvectordb.lollms_tokenizers.tiktoken_tokenizer import TikTokenTokenizer
from datetime import datetime
from typing import Dict, Any

import re
import json
import requests
from tqdm import tqdm
import shutil
import yaml
import urllib.parse

from typing import Callable, Any

from PIL import Image
from io import BytesIO


class AIBuildingRequestData(BaseModel):
    ai_name: str
    ai_author: str
    ai_version: str
    ai_category: str
    ai_language: str
    ai_description: str
    ai_conditionning: str
    ai_welcome_message: str
    ai_temperature: float
    ai_disclaimer: str

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
        self.word_callback = None
        self.sd = None
        self.sd_models_folder = self.sd_folder/"models"/"Stable-diffusion"
        if self.sd_models_folder.exists():
            self.sd_models = [f.stem for f in self.sd_models_folder.iterdir()]
        else:
            self.sd_models = ["Not installeed"]
        personality_config_template = ConfigTemplate(
            [
                {"name":"language","type":"str","value":"English", "help":"The personality language"},
                {"name":"single_shot","type":"bool","value":False, "help":"If true, then the AI personality will be built at a single shot (use this if you are using a high end LLM), if not, then deactivate this"},
                {"name":"generate_prompt_examples","type":"bool","value":True, "help":"Generates prompt examples for the personality"},
                {"name":"examples_extraction_method","type":"str","value":"random","options":["random", "rag_based", "None"], "help":"The generation AI has access to a list of examples of prompts that were crafted and fine tuned by a combination of AI and the main dev of the project. You can select which method lpm uses to search  those data, (none, or random or rag based where he searches examples that looks like the persona to build)"},
                {"name":"number_of_examples_to_recover","type":"int","value":3, "help":"How many example should we give the AI"},

                {"name":"data_folder_path","type":"str","value":"", "help":"A path to a folder containing data to feed the AI. Supported file types are: txt,pdf,docx,pptx"},
                {"name":"audio_sample_path","type":"str","value":"", "help":"A path to an audio file containing some voice sample to set as the AI's voice. Supported file types are: wav, mp3"},
                {"name":"generate_icon","type":"bool","value":True, "help":"generates an icon for the persona. if deactivated, the persona will have the same icon as lollms"},
                {"name":"num_images","type":"int","value":1, "help":"Number of icons to generate"},
                
                {"name":"make_scripted","type":"bool","value":False, "help":"Makes a scriptred AI that can perform operations using python script"},                
                {"name":"build_the_scipt","type":"bool","value":True, "help":"Experimental! This requires at least to be using a 128k tokens context LLM"},
                {"name":"script_version","type":"str","value":"3.0", "options":["2.0","3.0"], "help":"The personality can be of v2 (no function calls) or v3 (function calls are baked in)"},
                
                {"name":"model_temperature","type":"float","value":0.1, "help":"The temperature of generation using this personality (lower = more deterministic, higher = more creative, very high may lead to halucinations (make sure to keep it between 0 and 1))"},



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
                                        "regenerate_icons":self.regenerate_icons,
                                        "manual_building":self.manual_building
                                    },
                                    "default": None
                                },                           
                            ],
                            callback=callback
                        )
        self.sd = None
        self.assets_path = None

    def install(self):
        super().install()
        
        requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Install dependencies using pip from requirements.txt
        subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])      
        ASCIIColors.success("Installed successfully")

    def help(self, prompt="", full_context=""):
        self.personality.InfoMessage(self.personality.help)

    def regenerate_icons(self, prompt="", full_context="", client=None):
        try:
            index = full_context.index("name:")
            self.build_icon(full_context,full_context[index:].split("\n")[0].strip(),client=client)
        except:
            self.warning("Couldn't find name")


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
        try:
            imageSource = data['imageSource']
            assets_path= data['assets_path']

            shutil.copy(self.personality.lollms_paths.personal_outputs_path/self.personality.app.tti.name/imageSource.split("/")[-1] , Path(assets_path)/"logo.png")
            ASCIIColors.success("image Selected successfully")
            return {"status":True}
        except Exception as ex:
            trace_exception(ex)
            form_data = data
            ai_icon: Optional[UploadFile] = None
            if 'ai_icon' in form_data:
                ai_icon = form_data['ai_icon'].file

            # Parse the form data using Pydantic
            request_data = AIBuildingRequestData(**form_data)


            yaml_data="\n".join([
                f"## {request_data.ai_name} Chatbot conditionning file",
                f"## Author: {request_data.ai_author}",
                f"## Version: {request_data.ai_version}",
                f"## Description:",
                f"## {request_data.ai_description}",
                "## talking to.",
                "",
                "# Credits",
                f"author: {request_data.ai_author}",
                f"version: {request_data.ai_version}",
                f"category: {request_data.ai_category}",
                f"language: {request_data.ai_language}",
                f"name: {request_data.ai_name}",
                "personality_description: |",
                f"    {request_data.ai_description}",
                "disclaimer: |",
                f"    {request_data.ai_disclaimer}",
                "",
                "# Actual useful stuff",
                "personality_conditioning: |",
                f"    {request_data.ai_conditionning}",
                f"user_message_prefix: 'user'",
                f"ai_message_prefix: '{request_data.ai_name.lower().replace(' ','_')}'",
                "# A text to put between user and chatbot messages",
                "link_text: '\n'",
                "welcome_message: |",
                f"    {request_data.ai_welcome_message}",
                "# Here are default model parameters",
                f"model_temperature: {request_data.ai_temperature} # higher: more creative, lower: more deterministic",
                "",
                "model_top_k: 40",
                "model_top_p: 0.90",
                "model_repeat_penalty: 1.1",
                "model_repeat_last_n: 64",
                "",
                "# Recommendations",
                "recommended_binding: ''",
                "recommended_model: ''",
                "",
                "# Here is the list of extensions this personality requires",
                "dependencies: []",
                "",
                "# A list of texts to be used to detect that the model is hallucinating and stop the generation if any one of these is output by the model",
                "anti_prompts: []"
            ])   
            self.personality_path:Path = self.personality.lollms_paths.custom_personalities_path/request_data.ai_name.lower().replace(" ","_").replace("\n","").replace('"','')
            self.assets_path:Path = self.personality_path/"assets"
            self.personality_path.mkdir(parents=True, exist_ok=True)
            self.assets_path.mkdir(parents=True, exist_ok=True)
         
            with open(self.personality_path/"config.yaml","w", encoding="utf8") as f:
                f.write(yaml_data)

            # Process the file data
            if ai_icon:
                # Save the file to disk or process it as needed
                with open(self.assets_path/'logo.png', 'wb') as f:
                    while chunk := ai_icon.read(8192):
                        f.write(chunk)

            # Return a response indicating success or failure
            return {"status": True}        


    def prepare(self):
        if not self.personality.app.tti and self.personality_config.generate_icon:
            self.info("No tti engine is selected.\nPlease select an engine from the services settings or deactivate icon generation from the personality settings")


    def remove_image_links(self, markdown_text):
        # Regular expression pattern to match image links in Markdown
        image_link_pattern = r"!\[.*?\]\((.*?)\)"

        # Remove image links from the Markdown text
        text_without_image_links = re.sub(image_link_pattern, "", markdown_text)

        return text_without_image_links


    
    def make_selectable_photo(self, image_id, image_source, assets_path=None):

        with(open(Path(__file__).parent.parent/"assets/photo.html","r") as f):
            str_data = f.read()
        
        reshaper = PromptReshaper(str_data)
        str_data = reshaper.replace({
            "{image_id}":f"{image_id}",
            "{thumbneil_width}":f"256",
            "{thumbneil_height}":f"256",
            "{image_source}": image_source,
            "{assets_path}":str(assets_path).replace("\\","/") if assets_path else str(self.assets_path).replace("\\","/")
        })
        return str_data
    
    def make_selectable_photos(self, html:str):
        with(open(Path(__file__).parent.parent/"assets/photos_galery.html","r") as f):
            str_data = f.read()
        
        reshaper = PromptReshaper(str_data)
        str_data = reshaper.replace({
            "{{photos}}":html
        })
        return str_data


    def build_icon(self, discussion_messages, name, ui_code="", client:Client = None):
        self.prepare()
        # ----------------------------------------------------------------
        
        # Now we generate icon        
        # ----------------------------------------------------------------
        self.step_start("Imagining Icon")
        examples = ""
        expmls = []
        if self.personality_config.examples_extraction_method=="random":
            expmls = get_random_image_gen_prompt(self.personality_config.number_of_examples_to_recover)
        elif self.personality_config.examples_extraction_method=="rag_based":
            expmls = get_image_gen_prompt(name, self.personality_config.number_of_examples_to_recover)
            
        for i,expml in enumerate(expmls):
            examples += f"example {i}: "+expml+"\n"

        crafted_prompt = self.build_prompt(
            [
                "The code to generate is a json with two",
                "The user describes a personality and the ai should describe a suitable icon for the ai personality",
                "icon imaginer tries to express the personality of by describing a suitable eye catching icon",
                "icon imaginer uses english to describe the icon.",
                "icon imaginer may emphesize some aspects of the icon by putting it inside multiple brackets, like (((beautiful))) or ((detailed)) etc...",
                "the more important the text is, the bigger the number of brackets.",
                "icon imaginer description starts by describing the icon in details, then adds the name of the style or a description of the style for more original vibes then add boosting words, like detailed, beautiful, hires etc...",
                self.system_custom_header("context"),
                discussion_messages,
                self.system_custom_header("name")+f"{name}",
                self.system_custom_header("examples") if examples!="" else "",
                f"{examples}" if examples!="" else ""
            ],5
        )
        template = """{
"prompt": "[a short image generation prompt to generate the icon with style elements]"
}
        """
        sd_prompt = self.generate_text(crafted_prompt, self.personality.image_files, template, callback=self.sink, accept_all_if_no_code_tags_is_present=True)
        sd_prompt = json.loads(sd_prompt)["prompt"]
        self.step_end("Imagining Icon")
        self.set_message_content("### Image generation prompt:\n"+sd_prompt)
        self.new_message("")
        ASCIIColors.yellow(f"Image generation prompt:\n{sd_prompt}")
        self.add_chunk_to_message_content("")
        # ----------------------------------------------------------------
        
        # ----------------------------------------------------------------

        sd_negative_prompt = self.config.default_negative_prompt
        ui_code+=self.build_a_document_block('icon prompt',"",sd_prompt)
        ui_code+= self.build_a_document_block('icon sd_negative_prompt',"",sd_negative_prompt)
        self.add_chunk_to_message_content("")
        self.step_start("Painting Icon")
        try:
            files = []
            ui=""
            for img in range(self.personality_config.num_images):
                try:
                    self.step_start(f"Generating image {img+1}/{self.personality_config.num_images}")
                    file, infos = self.personality.app.tti.paint(
                                    sd_prompt, 
                                    sd_negative_prompt,
                                    width = 512,
                                    height = 512,
                                    restore_faces = True,
                                    output_path=client.discussion.discussion_folder
                                )
                    if file is None:
                        self.step_end(f"Generating image {img+1}/{self.personality_config.num_images}", False)
                        continue
                    self.step_end(f"Generating image {img+1}/{self.personality_config.num_images}")
                    file = str(file)

                    files.append(file)
                    escaped_url =  discussion_path_to_url(file)
                    file_html = self.make_selectable_photo(Path(file).stem, escaped_url, self.assets_path)
                    ui += file_html
                    ui_code += self.make_selectable_photos(ui)
                    self.set_message_html(ui_code)
                except Exception as ex:
                    ASCIIColors.error("Couldn't generate the personality icon.\nPlease make sure that the personality is well installed and that you have enough memory to run both the model and stable diffusion")
                    shutil.copy("assets/logo.png",self.assets_path)
                    files.append(self.assets_path/"logo.png")
                    trace_exception(ex)

        except Exception as ex:
            try:
                self.exception("Couldn't generate the personality icon.\nPlease make sure that the personality is well installed and that you have enough memory to run both the model and stable diffusion")
                ASCIIColors.error("Couldn't generate the personality icon.\nPlease make sure that the personality is well installed and that you have enough memory to run both the model and stable diffusion")
                shutil.copy("assets/logo.png",self.assets_path)
                files.append(self.assets_path/"logo.png")
                trace_exception(ex)
            except Exception as ex:
                trace_exception(ex)

            files=[]
        self.step_end("Painting Icon")

        header = """
<!DOCTYPE html>
<html>
<head>
    <title>Personality photos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        .flex {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .button-row {
            margin-bottom: 20px;
        }
        .button-link {
            background-color: #4CAF50;
            color: #ffffff;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .button-link:hover {
            background-color: #3e8e41;
        }
    </style>
</head>
<body>
    <h1>Personality icons</h1>
    <h2>Please select a photo to be used as the logo</h2>
        """
        ui=""
        for i in range(len(files)):
            try:
                files[i] = str(files[i]).replace("\\","/")
                file_id = files[i].split(".")[0].split('_')[-1]
                shutil.copy(files[i],str(self.assets_path))
                f=discussion_path_to_url(files[i])
                file_path = self.make_selectable_photo(f"{file_id}", f)
                ui +=  str(file_path)
                print(f"Generated file in here : {str(files[i])}")
            except Exception as ex:
                trace_exception(ex)
        if self.personality_config.make_scripted:
            ui += """
            <div class='flex'>
                <div class='button-row'>
                    <button onclick='open_script_folder(); return false;' class='button-link'>Click here to open the script folder of the persona</button>
                </div>
                <div class='button-row'>
                    <button onclick='open_script_in_vscode(); return false;' class='button-link'>Click here to open the script folder of the persona in vscode</button>
                </div>
            </div>
            <script>
                function open_script_folder(){
                    const secretMessage1 = {'folder_path': """+str(self.scripts_path)+"""};
                    const requestOptions = {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(secretMessage1)
                    };
                    fetch('/open_folder', requestOptions)
                        .then(() => {
                            console.log('The secret message has been sent and the magic code folder has been opened!');
                        })
                        .catch((error) => {
                            console.error('Oh no! Something went wrong:', error);
                        });
                }

                function open_script_in_vscode(){
                    const secretMessage2 = {'folder_path': """+str(self.scripts_path)+"""};
                    const requestOptions = {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(secretMessage2)
                    };
                    fetch('/open_discussion_folder_in_vs_code', requestOptions)
                        .then(() => {
                            console.log('The secret message has been sent and the magic code folder has been opened!');
                        })
                        .catch((error) => {
                            console.error('Oh no! Something went wrong:', error);
                        });
                }
            </script>            
            """
        footer ="""

            </body>
            </html>
        """
        # ----------------------------------------------------------------
        self.step_end("Painting Icon")
        
        ui_code+= self.build_a_folder_link(str(self.personality_path).replace("\\","/"), client,"press this text to access personality path")
        self.set_message_html(ui_code)
        full_page = header+'\n'+ui+"\n"+footer
        print(full_page)
        self.set_message_html(ui)

        
        self.assets_path.mkdir(parents=True, exist_ok=True)
        if len(files)>0:
            if str(files[-1])!=str(self.assets_path/"logo.png"):
                try:
                    shutil.copy(files[-1], self.assets_path/"logo.png")
                except:
                    pass
        else:
            shutil.copy(Path(__file__).parent.parent/"assets"/"lollms_logo.png", self.assets_path/"logo.png")


    def manual_building(self, prompt="", full_context=""):
        form_path = Path(__file__).parent.parent/"assets"/"edit_persona.html"
        with open(form_path,"r") as f:
            form = f.read()
        self.new_message(form,MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI)
        pass



    def generate_personality(self, main_prompt, single_shot=False):
        categories = [c.stem.lower() for c in Path(__file__).parent.parent.parent.parent.iterdir() if c.is_dir()]
        template = {
            "name": f"Based on the prompt, generate a suitable name for the personality.",
            "author": self.personality.config.user_name,
            "creation_date": datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
            "last_update_date": datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
            "category":f"Based on the prompt, choose the most appropriate category from: "+",".join(categories)+". Only write the most appropriate category name in the field category.",
            "language": self.personality_config.language,
            "personality_description": f"Based on the prompt, write a brief description of the personality. Keep it under 3 sentences.",
            "disclaimer": f"Based on the prompt, write a brief disclaimer mentioning any limitations. Keep it under 2 sentences.",
            "personality_conditioning": f"""Based on the prompt, define the personality's system message. The system message describes the personality and how it behaves. The message must be written in """+self.personality_config.language+".",
            "welcome_message": f"Based on the prompt, create a welcome message introducing the personality's capabilities. Keep it friendly and professional, under 3 sentences. The message must be written in "+self.personality_config.language+".",
            "model_temperature": 0.1,
            "model_top_k": 50,
            "model_top_p": 0.90,
            "model_repeat_penalty": 1.0,
            "model_repeat_last_n": 40,
            "dependencies": []
        }
        if self.personality_config.generate_prompt_examples:
            template["prompts_list"]="Based on the prompt, list 5 example user prompts with placeholders for the user to fill placed between []. Each prompt has the following structure @<prompt title>@prompt text with placeholders [placeholder_name::placeholder type (str, float, int, multiline, code)] You can use as many placeholders as needed. The prompts must be disposed one per line inside the markdown tag. The message must be written in "+self.personality_config.language+"."
            
        if self.config.debug and not self.personality.processor:
            ASCIIColors.highlight(self.system_custom_header("prompt")+main_prompt,"source_document_title", ASCIIColors.color_yellow, ASCIIColors.color_red, False)

        
        response = self.generate_structured_content(main_prompt, template = yaml.dump(template), output_format="yaml", callback=self.sink)
        print(response)
        config = yaml.safe_load(response)
        if config["category"].strip().lower() not in categories:
            config["category"]="generic"
        return config


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


        self.word_callback = callback
        self.callback = callback

        # First we create the yaml file
        # ----------------------------------------------------------------
        self.step_start("Building main yaml")

        infos = self.generate_personality(prompt, self.personality_config.single_shot)
        yaml_data = yaml.dump(infos)

        ui_data = self.generate_html_from_dict(infos)
        self.set_message_html(ui_data)
        name = infos["name"]
        self.step_end("Building the yaml file")
        self.new_message("")
        self.step_start("Preparing paths")
        self.personality_path:Path = self.personality.lollms_paths.custom_personalities_path/name.lower().replace(" ","_").replace(",","_").replace("\n","").replace('"','')
        self.personality_path.mkdir(parents=True, exist_ok=True)
        self.assets_path = self.personality_path/"assets"
        self.assets_path.mkdir(parents=True, exist_ok=True)
        self.scripts_path = self.personality_path/"scripts"
        self.audio_path = self.personality_path/"audio"
        self.data_path = self.personality_path/"data"
        self.step_end("Preparing paths")

        self.step_start("Saving configuration file")
        with open(self.personality_path/"config.yaml","w", encoding="utf8") as f:
            f.write(yaml_data)
        self.step_end("Saving configuration file")

        if self.personality_config.generate_icon:
            self.step_start("Building icon")
            try:
                self.build_icon(previous_discussion_text, name, ui_data, client)
                self.step_end("Building icon")
            except Exception as ex:
                trace_exception(ex)
                ASCIIColors.red("failed to generate icons.\nUsing default icon")
                self.step_end("Building icon", False)
                self.personality.error("failed to generate icons.\nUsing default icon")
            self.new_message("")
        else:
            shutil.copy("assets/logo.png",self.assets_path)
            
        if self.personality_config.make_scripted:
            self.scripts_path.mkdir(parents=True, exist_ok=True)
            if self.personality_config.build_the_scipt:
                self.step_start("Creating custom script")
                with open(Path(__file__).parent/"Documentation.md","r") as f:
                    custom_script = f.read()
                code = self.fast_gen(previous_discussion_text+self.system_custom_header("Documentation")+custom_script+"\n"+self.system_custom_header("Instructions")+"Build the script for the personality that satisfies the user request. Build the full file and put its content into a python markdown tag.\nMake sure to use AI querying when needed.\nMake sure the code is complete and handle failure cases\nMake sure you implement all the details and use lollms generative capabilities when needed."+self.ai_full_header)
                codes = self.extract_code_blocks(code)
                if len(codes)>0:
                    code = codes[0]["content"]
                    while not codes[0]["is_complete"]:
                        self.step("Continuing generation")
                        code = self.fast_gen(previous_discussion_text+self.system_custom_header("Documentation")+custom_script+"\n"+self.system_custom_header("Instructions")+"Build the script for the personality that satisfies the user request. Build the full file and put its content into a python markdown tag.\n"+self.ai_full_header+f"""
```python
{code}
```
"""+self.user_full_header+"Continue starting from last line of code"+self.ai_full_header)
                        codes = self.extract_code_blocks(code)
                        if len(codes)>0:
                            code = "\n".join(code.split("\n")[:-1])+codes[0]["content"]

                    with(open(self.scripts_path/"processor.py","w",encoding="utf8", errors='ignore') as f):
                        f.write(codes[0]["content"])
                    self.step_end("Creating custom script")                    
                else:
                    self.step_end("Creating custom script", False)
                    self.step_start("Creating default script")
                    if self.personality_config.script_version=="3.0":
                        template_fn = Path(__file__).parent/"script_template_v3.py"
                    else:
                        template_fn = Path(__file__).parent/"script_template_v2.py"
                    shutil.copy(template_fn, self.scripts_path/"processor.py")
                    self.step_end("Creating default script")
            else:
                self.step_start("Creating default script")
                if self.personality_config.script_version=="3.0":
                    template_fn = Path(__file__).parent/"script_template_v3.py"
                else:
                    template_fn = Path(__file__).parent/"script_template_v2.py"
                shutil.copy(template_fn, self.scripts_path/"processor.py")
                self.step_end("Creating default script")

        if self.personality_config.data_folder_path!="":
            self.data_path.mkdir()
            self.step_start("Creating vector database")
            text = []
            data_path = Path(self.personality_config.data_folder_path)
            text_files = []
            extensions = ["*.txt","*.pdf","*.pptx","*.docx","*.md"]
            for extension in extensions:
                text_files += [file if file.exists() else "" for file in data_path.glob(extension)]
            for file in text_files:
                self.step_start(f"Adding file: {file}")
                try:
                    text.append(TextDocumentsLoader.read_file(file))
                    self.step_end(f"Adding file: {file}")
                except Exception as ex:
                    trace_exception(ex)
                    self.step_end(f"Adding file: {file}",False)

            # Replace 'example_dir' with your desired directory containing .txt files
            self._data = "\n".join(map((lambda x: f"\n{x}"), text))
            self.step_start("Building data ...")
            try:
                if self.personality.config.rag_vectorizer=="semantic":
                    from lollmsvectordb.lollms_vectorizers.semantic_vectorizer import SemanticVectorizer
                    vectorizer = SemanticVectorizer(self.personality.config.rag_vectorizer_model, self.personality.config.rag_vectorizer_execute_remote_code)
                elif self.personality.config.rag_vectorizer=="tfidf":
                    from lollmsvectordb.lollms_vectorizers.tfidf_vectorizer import TFIDFVectorizer
                    vectorizer = TFIDFVectorizer()
                elif self.personality.config.rag_vectorizer=="openai":
                    from lollmsvectordb.lollms_vectorizers.openai_vectorizer import OpenAIVectorizer
                    vectorizer = OpenAIVectorizer(self.personality.config.rag_vectorizer_model, self.personality.config.rag_vectorizer_openai_key)
                elif self.personality.config.rag_vectorizer == "ollama":
                    from lollmsvectordb.lollms_vectorizers.ollama_vectorizer import OllamaVectorizer
                    v = OllamaVectorizer(self.personality.config.rag_vectorizer_model, self.personality.config.rag_service_url)

                self.persona_data_vectorizer = VectorDatabase(self.data_path/"db.sqlite", vectorizer, None if self.lollms.config.rag_vectorizer=="semantic" else self.model if self.model else TikTokenTokenizer(), n_neighbors=self.config.rag_n_chunks)       
                self.persona_data_vectorizer.add_document("persona_data", self._data, 512, 0)
                self.persona_data_vectorizer.build_index()
                self.step_end("Building data ...")
            except Exception as ex:
                trace_exception(ex)
                self.step_end("Building data ...",False)

            self.step_end("Creating vector database")

        if self.personality_config.audio_sample_path!="":
            audio_sample_path=Path(self.personality_config.audio_sample_path)
            self.audio_path.mkdir(exist_ok=True, parents=True)
            self.step_start("Creating a voice for the AI")
            shutil.copy(audio_sample_path, self.audio_path/audio_sample_path.name)
            self.step_end("Creating a voice for the AI")
        

        return ""


