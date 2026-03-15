from fastapi import APIRouter, Request
import subprocess
from pathlib import Path
from lollms.helpers import ASCIIColors, trace_exception
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate, InstallOption
from lollms.types import MSG_OPERATION_TYPE
from lollms.utilities import git_pull
from lollms.personality import APScript, AIPersonality
from lollms.prompting import LollmsContextDetails
from lollms.utilities import PromptReshaper, git_pull
import re
import importlib
import requests
from tqdm import tqdm
import shutil
import yaml
import urllib.parse

from typing import Callable, Any, Dict, Any
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
        personality_config_template = ConfigTemplate(
            [
                {"name":"number_of_personas","type":"int","value":5, "min":1, "help":"Number of personas to be generated"},                
                {"name":"model_name","type":"str","value":"DreamShaper_5_beta2_noVae_half_pruned.ckpt", "help":"Name of the model to be loaded for stable diffusion generation"},
                {"name":"sampler_name","type":"str","value":"Euler a", "options":["Euler a","Euler","LMS","Heun","DPM2","DPM2 a","DPM++ 2S a","DPM++ 2M","DPM++ SDE","DPM++ 2M SDE", "DPM fast", "DPM adaptive", "DPM Karras", "DPM2 Karras", "DPM2 a Karras","DPM++ 2S a Karras","DPM++ 2M Karras","DPM++ SDE Karras","DPM++ 2M SDE Karras" ,"DDIM", "PLMS","UniPC"], "help":"Select the sampler to be used for the diffusion operation. Supported samplers ddim, dpms, plms"},                
                {"name":"ddim_steps","type":"int","value":50, "min":10, "max":1024},
                {"name":"scale","type":"float","value":7.5, "min":0.1, "max":100.0},
                {"name":"steps","type":"int","value":50, "min":10, "max":1024},                
                {"name":"W","type":"int","value":512, "min":10, "max":2048},
                {"name":"H","type":"int","value":512, "min":10, "max":2048},
                {"name":"skip_grid","type":"bool","value":True,"help":"Skip building a grid of generated images"},
                {"name":"img2img_denoising_strength","type":"float","value":7.5, "min":0.01, "max":1.0, "help":"The image to image denoising strength"},
                {"name":"batch_size","type":"int","value":1, "min":1, "max":100,"help":"Number of images per batch (requires more memory)"},
                {"name":"num_images","type":"int","value":1, "min":1, "max":100,"help":"Number of batch of images to generate (to speed up put a batch of n and a single num images, to save vram, put a batch of 1 and num_img of n)"},
                {"name":"seed","type":"int","value":-1},
                {"name":"max_generation_prompt_size","type":"int","value":512, "min":10, "max":personality.config["ctx_size"]},
                
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
        self.sd = None
        self.assets_path = None

    def install(self):
        super().install()
        
        requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Install dependencies using pip from requirements.txt
        subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])      
        ASCIIColors.success("Installed successfully")


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
        imageSource = data['imageSource']
        assets_path= data['assets_path']

        shutil.copy(self.personality.lollms_paths.personal_outputs_path/"sd"/imageSource.split("/")[-1] , Path(assets_path)/"logo.png")
        ASCIIColors.success("image Selected successfully")
        return {"status":True}


    def prepare(self):
        if self.sd is None:
            from lollms.services.tti.sd.lollms_sd import LollmsSD
            self.step_start("Loading ParisNeo's fork of AUTOMATIC1111's stable diffusion service")
            sd = LollmsSD.get(self.personality.app)
            if sd is not None:
                self.sd = sd(self.personality.lollms_paths, "Personality maker", max_retries=-1)
                self.step_end("Loading ParisNeo's fork of AUTOMATIC1111's stable diffusion service")
            else:
                self.step_end("Loading ParisNeo's fork of AUTOMATIC1111's stable diffusion service", False)

    def remove_image_links(self, markdown_text):
        # Regular expression pattern to match image links in Markdown
        image_link_pattern = r"!\[.*?\]\((.*?)\)"

        # Remove image links from the Markdown text
        text_without_image_links = re.sub(image_link_pattern, "", markdown_text)

        return text_without_image_links


    
    def make_selectable_photo(self, image_id, image_source, assets_path=None):
        pth = image_source.split('/')
        idx = pth.index("outputs")
        pth = "/".join(pth[idx:])

        with(open(Path(__file__).parent.parent/"assets/photo.html","r") as f):
            str_data = f.read()
        
        reshaper = PromptReshaper(str_data)
        str_data = reshaper.replace({
            "{image_id}":f"{image_id}",
            "{thumbneil_width}":f"256",
            "{thumbneil_height}":f"256",
            "{image_source}":pth,
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
        self.prepare()
        output_path:Path = self.personality.lollms_paths.personal_outputs_path / self.personality.personality_folder_name
        output_path.mkdir(parents=True, exist_ok=True)
        # First we create the yaml file
        # ----------------------------------------------------------------
        self.step_start("Imagining personas list")
        list_of_personas = "- " + self.generate(f"""{self.personality.personality_conditioning}
{self.config.start_header_id_template}user request:{prompt}
{self.config.start_header_id_template}task: Let's embark on a journey into the enchanting realm of imagination and conjure up the names and descriptions of {self.personality.personality_conditioning} mesmerizing personas. You, as the user, will provide an idea, and I'll present you with a list where each output is formatted as follows:
- Name: A concise and captivating description.
For instance:
- Genius coder: A knowledgeable genius who guides and assists users with coding.
- Humorist: A charismatic personality solely dedicated to entertaining users.
Please ensure that each entry is presented on a separate line.
{self.personality.ai_message_prefix}
Here is the output in the format you have requested:
- """,512,0.1,10,0.98)
        output = f"## Personas to create:\n{list_of_personas}\n"
        self.set_message_content(output)
        self.step_end("Imagining personas list")
        list_of_personas = list_of_personas.split("\n")
        ASCIIColors.yellow(f"list_of_personas:{list_of_personas}")
        # ----------------------------------------------------------------
        for persona in list_of_personas:
            self.new_message('',MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT)
            # ----------------------------------------------------------------
            self.step_start("Coming up with the personality name")
            name = self.generate(f"""{self.personality.personality_conditioning}
{self.config.start_header_id_template}user request:{persona}
{self.config.start_header_id_template}task: What is the name of the personality requested by the user?
If the request contains already the name, then use that.
{self.personality.ai_message_prefix}
name:""",50,0.1,10,0.98).strip().split("\n")[0]
            self.step_end("Coming up with the personality name")
            name = re.sub(r'[\\/:*?"<>|]', '', name)
            ASCIIColors.yellow(f"Name:{name}")
            # ----------------------------------------------------------------
            
            # ----------------------------------------------------------------
            try:
                author = "lollms_personality_maker prompted by "+self.personality.config.user_name
            except:
                author = "lollms_personality_maker"
            # ----------------------------------------------------------------
            
            # ----------------------------------------------------------------
            version = "1.0" 
            # ----------------------------------------------------------------
            
            # ----------------------------------------------------------------
            self.step_start("Coming up with the category")
            category = self.generate(f"""{self.personality.personality_conditioning}
{self.config.start_header_id_template}request:{persona}
{self.config.start_header_id_template}personality name:{name}
{self.config.start_header_id_template}task: Infer the category of the personality
{self.personality.ai_message_prefix}
author name:""",256,0.1,10,0.98).strip().split("\n")[0]
            self.step_end("Coming up with the category")
            ASCIIColors.yellow(f"Category:{category}")
            # ----------------------------------------------------------------
            
            # ----------------------------------------------------------------
            self.step_start("Coming up with the language")
            language = self.generate(f"""{self.personality.personality_conditioning}
{self.config.start_header_id_template}request:{persona}
{self.config.start_header_id_template}task: Infer the language of the request (english, french, chinese etc)
{self.personality.ai_message_prefix}
language:""",256,0.1,10,0.98).strip().split("\n")[0]
            self.step_end("Coming up with the language")
            ASCIIColors.yellow(f"Language:{language}")
            # ----------------------------------------------------------------
            
            # ----------------------------------------------------------------
            self.step_start("Coming up with the description")
            description = self.generate(f"""{self.personality.personality_conditioning}
{self.config.start_header_id_template}request:{persona}
{self.config.start_header_id_template}personality name:{name}
{self.config.start_header_id_template}task: Write a description of the personality
Use detailed description of the most important traits of the personality
{self.personality.ai_message_prefix}
description:""",256,0.1,10,0.98).strip() 
            self.step_end("Coming up with the description")
            ASCIIColors.yellow(f"Description:{description}")
            # ----------------------------------------------------------------
            
            # ----------------------------------------------------------------
            self.step_start("Coming up with the disclaimer")
            disclaimer = self.generate(f"""{self.personality.personality_conditioning}
{self.config.start_header_id_template}request:{persona}
{self.config.start_header_id_template}personality name:{name}
{self.config.start_header_id_template}task: Write a disclaimer about the ai personality infered from the request
{self.personality.ai_message_prefix}
disclaimer:""",256,0.1,10,0.98).strip()  
            self.step_end("Coming up with the disclaimer")
            ASCIIColors.yellow(f"Disclaimer:{disclaimer}")
            # ----------------------------------------------------------------

            # ----------------------------------------------------------------
            self.step_start("Coming up with the conditionning")
            conditioning = self.generate(f"""{self.config.start_header_id_template}request:{persona}
{self.config.start_header_id_template}personality name:{name}
{self.config.start_header_id_template}task: Craft a concise and detailed description of the personality and its key traits to condition a text AI. Use minimal words to simulate the inferred personality from the request.
{self.personality.ai_message_prefix}
{self.config.start_header_id_template}lollms_personality_maker: Here is the conditionning text for the personality {name}:
Act as""",256,0.1,10,0.98).strip()
            conditioning = "Act as "+conditioning
            self.step_end("Coming up with the conditionning")
            ASCIIColors.yellow(f"Conditioning:{conditioning}")
            # ----------------------------------------------------------------
            
            # ----------------------------------------------------------------
            self.step_start("Coming up with the welcome message")
            welcome_message = self.generate(f"""{self.personality.personality_conditioning}
{self.config.start_header_id_template}request:{persona}
{self.config.start_header_id_template}personality name:{name}
{self.config.start_header_id_template}task: Write a welcome message text that {name} sends to the user at startup. Keep it short and sweet.
{self.personality.ai_message_prefix}
welcome message:""",256,0.1,10,0.98).strip()          
            self.step_end("Coming up with the welcome message")
            ASCIIColors.yellow(f"Welcome message:{welcome_message}")
            # ----------------------------------------------------------------
                            
            # ----------------------------------------------------------------
            self.step_start("Building the yaml file")
            cmt_desc = "\n## ".join(description.split("\n"))
            desc = "\n    ".join(description.split("\n"))
            disclaimer = "\n    ".join(disclaimer.split("\n"))
            conditioning =  "\n    ".join(conditioning.split("\n"))
            welcome_message =  "\n    ".join(welcome_message.split("\n"))
            yaml_data=f"""## {name} Chatbot conditionning file
## Author: {author}
## Version: {version}
## Description:
## {cmt_desc}
## talking to.

# Credits
author: {author}
version: {version}
category: {category}
language: {language}
name: {name}
personality_description: |
    {desc}
disclaimer: |
    {disclaimer}

# Actual useful stuff
personality_conditioning: |
    {self.config.start_header_id_template}Instructions: 
    {conditioning}  
user_message_prefix: '{self.config.start_header_id_template}User:'
ai_message_prefix: '{name.lower().replace(' ','_')}'
# A text to put between user and chatbot messages
link_text: '\n'
welcome_message: |
    {welcome_message}
# Here are default model parameters
model_temperature: 0.6 # higher: more creative, lower: more deterministic

model_top_k: 40
model_top_p: 0.90
model_repeat_penalty: 1.1
model_repeat_last_n: 64

# Recommendations
recommended_binding: ''
recommended_model: ''

# Here is the list of extensions this personality requires
dependencies: []

# A list of texts to be used to detect that the model is hallucinating and stop the generation if any one of these is output by the model
anti_prompts: ["{self.config.start_header_id_template}","<|end|>","<|user|>","<|system|>"]
            """
            personality_path:Path = output_path/(name.lower().replace(" ","_").replace("\n","").replace('"',''))
            personality_path.mkdir(parents=True, exist_ok=True)
            with open(personality_path/"config.yaml","w", encoding="utf8") as f:
                f.write(yaml_data)

            self.step_end("Building the yaml file")
            # ----------------------------------------------------------------
            
            # Now we generate icon        
            personality_assets_path = personality_path/"assets"
            personality_assets_path.mkdir(parents=True, exist_ok=True)
            self.personality_assets_path = personality_assets_path
            
            self.word_callback = callback
            
            # ----------------------------------------------------------------
            self.step_start("Imagining Icon")
            # 1 first ask the model to formulate a query
            sd_prompt = self.generate(f"""{self.config.start_header_id_template}request: {persona}
{self.config.start_header_id_template}task: Write a prompt to describe an icon to the personality being built to be generated by a text2image ai. 
The prompt should be descriptive and include stylistic information in a single paragraph.
Try to show the face of the personality in the icon if it is not an abstract concept.
Try to write detailed description of the icon as well as stylistic elements like rounded corners or glossy and try to invoke a particular style or artist to help the generrator ai build an accurate icon.
Avoid text as the generative ai is not good at generating text.
{self.config.start_header_id_template}personality name: {name}
{self.config.start_header_id_template}prompt:""",self.personality_config.max_generation_prompt_size,0.1,10,0.98).strip()
            self.step_end("Imagining Icon")
            ASCIIColors.yellow(f"sd prompt:{sd_prompt}")
            # ----------------------------------------------------------------
            
            # ----------------------------------------------------------------

            path = self.personality.lollms_paths.custom_personalities_path/name.lower().replace(" ","_")
            assets_path= path/"assets"
            self.assets_path = assets_path
            personality_path="/".join(str(personality_path).replace('\\','/').split('/')[-2:])
            self.step_start("Painting Icon")
            try:
                files = []
                ui=""
                for img in range(self.personality_config.num_images):
                    self.step_start(f"Generating image {img+1}/{self.personality_config.num_images}")
                    file, infos = self.sd.paint(
                                    sd_prompt, 
                                    "((((ugly)))), (((duplicate))), ((morbid)), ((mutilated)), out of frame, extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck)))",
                                    [],
                                    sampler_name = self.personality_config.sampler_name,
                                    seed = self.personality_config.seed,
                                    scale = self.personality_config.scale,
                                    steps = self.personality_config.steps,
                                    img2img_denoising_strength = self.personality_config.img2img_denoising_strength,
                                    width = 512,
                                    height = 512,
                                    restore_faces = True,
                                )
                    self.step_end(f"Generating image {img+1}/{self.personality_config.num_images}")
                    file = str(file)

                    url = "/"+file[file.index("outputs"):].replace("\\","/")
                    file_html = self.make_selectable_photo(Path(file).stem, url, assets_path)
                    files.append(file)
                    ui += file_html
                    self.set_message_content(f'\n![]({urllib.parse.quote(url, safe="")})')

            except Exception as ex:
                self.exception("Couldn't generate the personality icon.\nPlease make sure that the personality is well installed and that you have enough memory to run both the model and stable diffusion")
                ASCIIColors.error("Couldn't generate the personality icon.\nPlease make sure that the personality is well installed and that you have enough memory to run both the model and stable diffusion")
                trace_exception(ex)
                files=[]
            self.step_end("Painting Icon")

            output += f"```yaml\n{yaml_data}\n```\n# Icon:\n## Description:\n" + sd_prompt.strip()+"\n"

            ui = ""
            for i in range(len(files)):
                files[i] = str(files[i]).replace("\\","/")
                file_id = files[i].split(".")[0].split('_')[1]
                shutil.copy(files[i],str(personality_assets_path))
                file_path = self.make_selectable_photo(f"Artbot_{file_id}", files[i])
                ui += file_path
                print(f"Generated file in here : {files[i]}")
            server_path = "/outputs/"+personality_path
            output += f"\nYou can find your personality files here : [{personality_path}]({server_path})"
            # ----------------------------------------------------------------
            self.step_end("Painting Icon")
            
            self.set_message_content(output, callback)
            self.new_message('<h2>Please select a photo to be used as the logo</h2>\n'+self.make_selectable_photos(ui),MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI)

            path.mkdir(parents=True, exist_ok=True)
            with open (path/"config.yaml","w") as f:
                config = yaml.safe_load(yaml_data)
                yaml.safe_dump(config,f)
            
            assets_path.mkdir(parents=True, exist_ok=True)
            if len(files)>0:
                shutil.copy(files[-1], assets_path/"logo.png")
        return output


