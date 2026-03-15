from fastapi import APIRouter, Request
import subprocess
from pathlib import Path
from lollms.helpers import ASCIIColors, trace_exception
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate, InstallOption
from lollms.types import MSG_OPERATION_TYPE
from lollms.personality import APScript, AIPersonality
from lollms.utilities import PromptReshaper, git_pull
from lollms.prompting import LollmsContextDetails
import re
import importlib
import requests
from tqdm import tqdm
import webbrowser
from typing import Dict, Any
from pathlib import Path
from typing import Callable, Any


import requests

def download_file(url, local_filename):
  response = requests.get(url, stream=True)
  total_size = int(response.headers['Content-Length'])
  block_size = 1024*8
  num_bars = int((total_size + (block_size - 1)) // block_size)
  
  with open(local_filename, 'wb') as f:
     for chunk in tqdm(response.iter_content(chunk_size=block_size), desc="Downloading", total=num_bars, unit='B',unit_scale=True, unit_divisor=1024):
        if chunk:
           f.write(chunk)
           f.flush()


# Helper functions
def find_next_available_filename(folder_path, prefix):
    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"The folder '{folder}' does not exist.")

    index = 1
    while True:
        next_filename = f"{prefix}_{index}.png"
        potential_file = folder / next_filename
        if not potential_file.exists():
            return potential_file
        index += 1


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
                {"name":"production_type","type":"str","value":"an design", "options":["a photo","a design","an artwork", "a drawing", "a painting", "a hand drawing", "a presentation asset", "a presentation background", "a game asset", "a game background", "an icon"],"help":"This selects what kind of graphics the AI is supposed to produce"},
                {"name":"generation_engine","type":"str","value":"stable_diffusion", "options":["stable_diffusion", "dalle-2"],"help":"Select the engine to be used to generate the images. Notice, dalle2 requires open ai key"},
                {"name":"openai_key","type":"str","value":"","help":"A valid open AI key to generate images using open ai api"},
                {"name":"imagine","type":"bool","value":True,"help":"Imagine the images"},
                {"name":"build_title","type":"bool","value":True,"help":"Build a title for the artwork"},
                {"name":"paint","type":"bool","value":True,"help":"Paint the images"},
                {"name":"use_fixed_negative_prompts","type":"bool","value":True,"help":"Uses parisNeo's preferred negative prompts"},
                {"name":"fixed_negative_prompts","type":"str","value":"((((ugly)))), (((duplicate))), ((morbid)), ((mutilated)), out of frame, extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), ((watermark)), ((robot eyes))","help":"which negative prompt to use in case use_fixed_negative_prompts is checked"},                
                {"name":"show_infos","type":"bool","value":True,"help":"Shows generation informations"},
                {"name":"continuous_discussion","type":"bool","value":True,"help":"If true then previous prompts and infos are taken into acount to generate the next image"},
                {"name":"automatic_resolution_selection","type":"bool","value":False,"help":"If true then architectai chooses the resolution of the image to generate"},
                
                {"name":"activate_discussion_mode","type":"bool","value":True,"help":f"If active, the AI will not generate an image until you ask it to, it will just talk to you until you ask it to make the graphical output requested"},
                
                {"name":"continue_from_last_image","type":"bool","value":False,"help":"Uses last image as input for next generation"},
                {"name":"img2img_denoising_strength","type":"float","value":7.5, "min":0.01, "max":1.0, "help":"The image to image denoising strength"},
                {"name":"restore_faces","type":"bool","value":True,"help":"Restore faces"},
                {"name":"caption_received_files","type":"bool","value":False,"help":"If active, the received file will be captioned"},
                {"name":"sampler_name","type":"str","value":"Euler a", "options":["Euler a","Euler","LMS","Heun","DPM2","DPM2 a","DPM++ 2S a","DPM++ 2M","DPM++ SDE","DPM++ 2M SDE", "DPM fast", "DPM adaptive", "DPM Karras", "DPM2 Karras", "DPM2 a Karras","DPM++ 2S a Karras","DPM++ 2M Karras","DPM++ SDE Karras","DPM++ 2M SDE Karras" ,"DDIM", "PLMS","UniPC"], "help":"Select the sampler to be used for the diffusion operation. Supported samplers ddim, dpms, plms"},                
                {"name":"steps","type":"int","value":50, "min":10, "max":1024},
                {"name":"scale","type":"float","value":7.5, "min":0.1, "max":100.0},

                {"name":"width","type":"int","value":512, "min":10, "max":2048},
                {"name":"height","type":"int","value":512, "min":10, "max":2048},

                {"name":"thumbneil_width","type":"int","value":256, "min":10, "max":2048},
                {"name":"thumbneil_height","type":"int","value":256, "min":10, "max":2048},

                {"name":"automatic_image_size","type":"bool","value":False,"help":"If true, architectai will select the image resolution"},
                {"name":"skip_grid","type":"bool","value":True,"help":"Skip building a grid of generated images"},
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
                            [
                                {
                                    "name": "idle",
                                    "commands": { # list of commands
                                        "help":self.help,
                                        "new_image":self.new_image,
                                        "show_sd":self.show_sd,
                                        "regenerate":self.regenerate,
                                        "show_settings":self.show_settings,
                                    },
                                    "default": self.main_process
                                },                           
                            ],
                            callback=callback
                        )
        self.width=int(self.personality_config.width)
        self.height=int(self.personality_config.height)

    def get_css(self):
        return '<link rel="stylesheet" href="/personalities/art/architectai/assets/tailwind.css">'


    def make_selectable_photo(self, image_id, image_source, image_infos={}):
        with(open(Path(__file__).parent.parent/"assets/photo.html","r") as f):
            str_data = f.read()
        
        reshaper = PromptReshaper(str_data)
        str_data = reshaper.replace({
            "{image_id}":f"{image_id}",
            "{thumbneil_width}":f"{self.personality_config.thumbneil_width}",
            "{thumbneil_height}":f"{self.personality_config.thumbneil_height}",
            "{image_source}":image_source,
            "{__infos__}":str(image_infos).replace("True","true").replace("False","false").replace("None","null")
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
    def print_prompt(self, title, prompt):
        ASCIIColors.red("*-*-*-*-*-*-*-* ", end="")
        ASCIIColors.red(title, end="")
        ASCIIColors.red(" *-*-*-*-*-*-*-*")
        ASCIIColors.yellow(prompt)
        ASCIIColors.red(" *-*-*-*-*-*-*-*")

    def install(self):
        super().install()
        
        requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Install dependencies using pip from requirements.txt
        subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])      

        # Clone repository
        if not self.sd_folder.exists():
            subprocess.run(["git", "clone", "https://github.com/ParisNeo/stable-diffusion-webui.git", str(self.sd_folder)])
        # verify if the models are installed
        
        models =[
            {
                "url": "https://civitai.com/api/download/models/141091?type=Model&format=SafeTensor&size=full&fp=fp16",
                "fn": "architectureExterior_v90.safetensors"
            },
            {
                "url": "https://civitai.com/api/download/models/138737?type=Model&format=SafeTensor&size=full&fp=fp16",
                "fn": "architecture_Interior_SDlife_Chiasedamme_V6.0.safetensors"
            }
        ]
        
        for model in models:
            local_filename = self.personality.lollms_paths.personal_path/"shared"/"auto_sd"/"models"/"Stable-diffusion"/model["fn"]

            if not local_filename.exists():
                print(f"Model {model['fn']} does not exist. Downloading...")
                download_file(model["url"], local_filename)
            else:
                print(f"Model {model['fn']} already exists.")        
        self.prepare()
        ASCIIColors.success("Installed successfully")


    def prepare(self):
        if self.sd is None and self.personality_config.generation_engine=="stable_diffusion":
            self.step_start("Loading ParisNeo's fork of AUTOMATIC1111's stable diffusion service")
            self.sd = self.get_sd().LollmsSD(self.personality.lollms_paths, "ArchitectAI", max_retries=-1)
            self.step_end("Loading ParisNeo's fork of AUTOMATIC1111's stable diffusion service")
        
        
    def get_sd(self):
        sd_script_path = self.sd_folder / "lollms_sd.py"
        git_pull(self.sd_folder)
        
        if sd_script_path.exists():
            ASCIIColors.success("lollms_sd found.")
            ASCIIColors.success("Loading source file...",end="")
            module_name = sd_script_path.stem  # Remove the ".py" extension
            # use importlib to load the module from the file path
            loader = importlib.machinery.SourceFileLoader(module_name, str(sd_script_path))
            ASCIIColors.success("ok")
            ASCIIColors.success("Loading module...",end="")
            sd_module = loader.load_module()
            ASCIIColors.success("ok")
            return sd_module

    def remove_image_links(self, markdown_text):
        # Regular expression pattern to match image links in Markdown
        image_link_pattern = r"!\[.*?\]\((.*?)\)"

        # Remove image links from the Markdown text
        text_without_image_links = re.sub(image_link_pattern, "", markdown_text)

        return text_without_image_links


    def help(self, prompt="", full_context=""):
        self.set_message_content(self.personality.help)
    
    def new_image(self, prompt="", full_context=""):
        self.image_files=[]
        self.personality.info("Starting fresh :)")
        
        
    def show_sd(self, prompt="", full_context=""):
        self.prepare()
        webbrowser.open("http://127.0.0.1:7860/?__theme=dark")        
        self.personality.info("Showing Stable diffusion UI")
        
        
    def show_settings(self, prompt="", full_context=""):
        self.prepare()
        webbrowser.open("http://127.0.0.1:7860/?__theme=dark")        
        self.set_message_content("Showing Stable diffusion settings UI")
        
    def show_last_image(self, prompt="", full_context=""):
        self.prepare()
        if len(self.image_files)>0:
            self.set_message_content(f"![]({self.image_files})")        
        else:
            self.set_message_content("Showing Stable diffusion settings UI")        
        
    def add_file(self, path, client, callback=None):
        self.new_message("")
        if callback is None and self.callback is not None:
            callback = self.callback

        self.prepare()
        super().add_file(path, client, callback)
        if self.personality_config.caption_received_files:
            self.new_message("", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK, callback=callback)
            self.step_start("Understanding the image", callback=callback)
            description = self.sd.interrogate(str(path)).info
            self.print_prompt("Blip description",description)
            self.step_end("Understanding the image", callback=callback)
            pth = str(path).replace("\\","/").split('/')
            idx = pth.index("uploads")
            pth = "/".join(pth[idx:])


            
            file_html = self.make_selectable_photo(path.stem,f"/{pth}",{"name":path.stem,"type":"Imported image", "prompt":description})
            self.set_message_content(f"File added successfully\nImage description :\n{description}\nImage:\n![]({pth})", callback=callback)
            self.set_message_html(self.make_selectable_photos(file_html))
            self.finished_message()
        else:    
            self.set_message_content(f"File added successfully\n", callback=callback)
        
    def regenerate(self, prompt="", full_context=""):
        if self.previous_sd_positive_prompt:
            self.new_message("Regenerating using the previous prompt",MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_START)
            output0 = f"## Positive prompt:\n{self.previous_sd_positive_prompt}\n## negative prompt:\n{self.previous_sd_negative_prompt}"
            output = output0
            self.set_message_content(output)
            files = []
            ui=""
            for img in range(self.personality_config.num_images):
                self.step_start(f"Building image {img+1}/{self.personality_config.num_images}")
                file, infos = self.sd.paint(
                                self.previous_sd_positive_prompt, 
                                self.previous_sd_negative_prompt,
                                self.image_files,
                                sampler_name = self.personality_config.sampler_name,
                                seed = self.personality_config.seed,
                                scale = self.personality_config.scale,
                                steps = self.personality_config.steps,
                                img2img_denoising_strength = self.personality_config.img2img_denoising_strength,
                                width = self.personality_config.width,
                                height = self.personality_config.height,
                                restore_faces = self.personality_config.restore_faces,
                            )
                file = str(file)
                url = "/"+file[file.index("outputs"):].replace("\\","/")
                file_html = self.make_selectable_photo(Path(file).stem,url, infos)
                output += f'\n![]({url})' 
                self.set_message_content(output)
                ui += file_html
                self.step_end(f"Building image {img+1}/{self.personality_config.num_images}")
            self.set_message_content(output0)
            self.step_end("Regenerating using the previous prompt")
            self.new_message(self.make_selectable_photos(ui),MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI)
            if self.personality_config.show_infos:
                self.new_message("infos", MSG_OPERATION_TYPE.MSG_TYPE_JSON_INFOS, infos)
        else:
            self.set_message_content("Please generate an image first then retry")

    
    def get_resolution(self, prompt, full_context, default_resolution=[512,512]):

        def extract_resolution(text, default_resolution=[512, 512]):
            # Define a regular expression pattern to match the (w, h) format
            pattern = r'\((\d+),\s*(\d+)\)'
            
            # Search for the pattern in the text
            match = re.search(pattern, text)
            
            if match:
                width = int(match.group(1))
                height = int(match.group(2))
                return width, height
            else:
                return default_resolution
                    
        self.step_start("Choosing resolution")
        prompt=f"{full_context}{self.config.separator_template}{self.config.start_header_id_template}user:{prompt}\nSelect a suitable image size (width, height).\nThe default resolution uis ({default_resolution[0]},{default_resolution[1]}){self.config.separator_template}{self.config.start_header_id_template}selected_image_size:"
        sz = self.generate(prompt, self.personality_config.max_generation_prompt_size).strip().replace("</s>","").replace("<s>","").split("\n")[0]

        self.step_end("Choosing resolution")

        return extract_resolution(sz, default_resolution)

    def main_process(self, initial_prompt, full_context):
        sd_title = "unnamed"    
        metadata_infos=""
        self.prepare()
        try:
            full_context = full_context[:full_context.index(initial_prompt)]
        except:
            ASCIIColors.warning("Couldn't extract full context portion")    
        if self.personality_config.imagine:
            if self.personality_config.activate_discussion_mode:
                if not self.yes_no(f"Pay attention to the prompt tone and answer this, is the user's message explicitly asking to generate {self.personality_config.production_type}?", initial_prompt, self.personality_config.max_generation_prompt_size):
                    pr  = PromptReshaper("""{self.config.start_header_id_template}instructions>ArchitectAI is an art generation AI that discusses with humains about art.
{self.config.start_header_id_template}discussion:
{{previous_discussion}}{{initial_prompt}}
{self.config.start_header_id_template}architectai:""")
                    prompt = pr.build({
                            "previous_discussion":full_context,
                            "initial_prompt":initial_prompt
                            }, 
                            self.personality.model.tokenize, 
                            self.personality.model.detokenize, 
                            self.personality.model.config.ctx_size,
                            ["previous_discussion"]
                            )
                    self.print_prompt("Discussion",prompt)

                    response = self.generate(prompt, self.personality_config.max_generation_prompt_size).strip().replace("</s>","").replace("<s>","")
                    self.set_message_content(response)
                    return



            if self.personality_config.automatic_resolution_selection:
                res = self.get_resolution(initial_prompt, full_context, [self.personality_config.width,self.personality_config.height])
                self.width=res[0]
                self.height=res[1]
            else:
                self.width=self.personality_config.width
                self.height=self.personality_config.height
            metadata_infos += f"### Chosen resolution:\n{self.width}x{self.height}\n"
            self.set_message_content(f"{metadata_infos}")     
            # ====================================================================================
            self.step_start("Imagining positive prompt")
            # 1 first ask the model to formulate a query
            past = f"{self.config.start_header_id_template}".join(self.remove_image_links(full_context).split("{self.config.start_header_id_template}")[:-2])
            pr  = PromptReshaper(f"""{self.config.start_header_id_template}discussion:                                 
{past if self.personality_config.continuous_discussion else ''}
{self.config.start_header_id_template}instructions:
Act as architectai, the art prompt generation AI. Use the previous discussion to come up with an image generation prompt. Be precise and describe the style as well as the {self.personality_config.production_type.split()[-1]} description details. 
{initial_prompt}
{self.config.start_header_id_template}art_generation_prompt: Create {self.personality_config.production_type}""")
            prompt = pr.build({
                    "previous_discussion":past if self.personality_config.continuous_discussion else '',
                    "initial_prompt":initial_prompt,
                    }, 
                    self.personality.model.tokenize, 
                    self.personality.model.detokenize, 
                    self.personality.model.config.ctx_size,
                    ["previous_discussion"]
                    )
            self.print_prompt("Positive prompt",prompt)

            sd_positive_prompt = f"{self.personality_config.production_type} "+self.generate(prompt, self.personality_config.max_generation_prompt_size).strip().replace("</s>","").replace("<s>","")
            self.step_end("Imagining positive prompt")
            metadata_infos += f"### Positive prompt:\n{sd_positive_prompt}\n"
            self.set_message_content(f"{metadata_infos}")     
            # ====================================================================================
            # ====================================================================================
            if not self.personality_config.use_fixed_negative_prompts:
                self.step_start("Imagining negative prompt")
                # 1 first ask the model to formulate a query
                pr  = PromptReshaper("""{self.config.start_header_id_template}instructions:
    Generate negative prompt based on the discussion with the user.
    The negative prompt is a list of keywords that should not be present in our image.
    Try to force the generator not to generate text or extra fingers or deformed faces.
    Use as many words as you need depending on the context.
    To give more importance to a term put it ibti multiple brackets ().
    example: {{fixed_negative_prompts}}
    {self.config.start_header_id_template}discussion:
    {{previous_discussion}}{{initial_prompt}}
    {self.config.start_header_id_template}architectai:
    prompt:{{sd_positive_prompt}}
    negative_prompt: ((morbid)),""")
                prompt = pr.build({
                        "previous_discussion":self.remove_image_links(full_context),
                        "initial_prompt":initial_prompt,
                        "sd_positive_prompt":sd_positive_prompt,
                        "fixed_negative_prompts": self.personality_config.fixed_negative_prompts
                        }, 
                        self.personality.model.tokenize, 
                        self.personality.model.detokenize, 
                        self.personality.model.config.ctx_size,
                        ["previous_discussion"]
                        )
                self.print_prompt("Generate negative prompt", prompt)
                sd_negative_prompt = "((morbid)),"+self.generate(prompt, self.personality_config.max_generation_prompt_size).strip().replace("</s>","").replace("<s>","")
                self.step_end("Imagining negative prompt")
            else:
                sd_negative_prompt = self.personality_config.fixed_negative_prompts
            metadata_infos += f"### Negative prompt:\n{sd_negative_prompt}\n"
            self.set_message_content(f"{metadata_infos}")     
            # ====================================================================================            
            if self.personality_config.build_title:
                self.step_start("Making up a title")
                # 1 first ask the model to formulate a query
                pr  = PromptReshaper("""{self.config.start_header_id_template}instructions:
Given this image description prompt and negative prompt, make a consize title
{self.config.start_header_id_template}positive_prompt:
{{positive_prompt}}
{self.config.start_header_id_template}negative_prompt:
{{negative_prompt}}
{self.config.start_header_id_template}title:
""")
                prompt = pr.build({
                        "positive_prompt":sd_positive_prompt,
                        "negative_prompt":sd_negative_prompt,
                        }, 
                        self.personality.model.tokenize, 
                        self.personality.model.detokenize, 
                        self.personality.model.config.ctx_size,
                        ["negative_prompt"]
                        )
                self.print_prompt("Make up a title", prompt)
                sd_title = self.generate(prompt, self.personality_config.max_generation_prompt_size).strip().replace("</s>","").replace("<s>","")
                self.step_end("Making up a title")
                metadata_infos += f"### title:\n{sd_title}\n"
                self.set_message_content(f"{metadata_infos}")

        else:
            self.width=self.personality_config.width
            self.height=self.personality_config.height
            prompt = initial_prompt.split("\n")
            if len(prompt)>1:
                sd_positive_prompt = prompt[0]
                sd_negative_prompt = prompt[1]
            else:
                sd_positive_prompt = prompt[0]
                sd_negative_prompt = ""
            
        self.previous_sd_positive_prompt = sd_positive_prompt
        self.previous_sd_negative_prompt = sd_negative_prompt
        self.previous_sd_title = sd_title

        output = metadata_infos

        if self.personality_config.paint:
            files = []
            ui=""
            for img in range(self.personality_config.num_images):
                self.step_start(f"Generating image {img+1}/{self.personality_config.num_images}")
                if self.personality_config.generation_engine=="stable_diffusion":
                    file, infos = self.sd.paint(
                                    sd_positive_prompt, 
                                    sd_negative_prompt,
                                    self.image_files,
                                    sampler_name = self.personality_config.sampler_name,
                                    seed = self.personality_config.seed,
                                    scale = self.personality_config.scale,
                                    steps = self.personality_config.steps,
                                    img2img_denoising_strength = self.personality_config.img2img_denoising_strength,
                                    width = self.personality_config.width,
                                    height = self.personality_config.height,
                                    restore_faces = self.personality_config.restore_faces,
                                )
                    infos["title"]=sd_title
                    file = str(file)

                    url = "/"+file[file.index("outputs"):].replace("\\","/")
                    file_html = self.make_selectable_photo(Path(file).stem, url, infos)
                    files.append("/"+file[file.index("outputs"):].replace("\\","/"))
                    ui += file_html
                    metadata_infos += f'\n![]({url})'
                    self.set_message_content(metadata_infos)
                    
                elif self.personality_config.generation_engine=="dalle-2":
                    import openai
                    openai.api_key = self.personality_config.config["openai_key"]
                    response = openai.Image.create(
                        prompt=sd_positive_prompt,
                        n=1,
                        size=f"{self.personality_config.width}x{self.personality_config.height}"
                        )
                    infos = {}
                    # download image to outputs
                    output_dir = self.personality.lollms_paths.personal_outputs_path/"dalle"
                    output_dir.mkdir(parents=True, exist_ok=True)
                    image_url = response['data'][0]['url']

                    # Get the image data from the URL
                    response = requests.get(image_url)

                    if response.status_code == 200:
                        # Generate the full path for the image file
                        file_name = output_dir/find_next_available_filename(output_dir, "img_dalle_")  # You can change the filename if needed

                        # Save the image to the specified folder
                        with open(file_name, "wb") as file:
                            file.write(response.content)
                        ASCIIColors.yellow(f"Image saved to {file_name}")
                    else:
                        ASCIIColors.red("Failed to download the image")
                    file = str(file_name)

                    url = "/"+file[file.index("outputs"):].replace("\\","/")
                    file_html = self.make_selectable_photo(Path(file).stem, url)
                    files.append("/"+file[file.index("outputs"):].replace("\\","/"))
                    ui += file_html
                    metadata_infos += f'\n![]({url})'
                    self.set_message_content(metadata_infos)

                self.step_end(f"Generating image {img+1}/{self.personality_config.num_images}")

            if self.personality_config.continue_from_last_image:
                self.image_files= [file]            
            self.set_message_content(output.strip())
            self.new_message(self.make_selectable_photos(ui), MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI)
        else:
            infos = None
        if self.personality_config.show_infos and infos:
            self.json("infos", infos)


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
        operation = data.get("name","variate")
        prompt = data.get("prompt","")
        negative_prompt =  data.get("negative_prompt","")
        if operation=="variate":
            imagePath = data.get("imagePath","")
            ASCIIColors.info(f"Regeneration requested for file : {imagePath}")
            self.new_image()
            ASCIIColors.info("Building new image")
            self.image_files.append(self.personality.lollms_paths.personal_outputs_path/"sd"/imagePath.split("/")[-1])
            self.personality.info("Regenerating")
            self.previous_sd_positive_prompt = prompt
            self.previous_sd_negative_prompt = negative_prompt
            self.new_message(f"Generating {self.personality_config.num_images} variations")
            self.prepare()
            self.regenerate()
            
            return {"status":True, "message":"Image is now ready to be used as variation"}
        elif operation=="set_as_current":
            imagePath = data.get("imagePath","")
            ASCIIColors.info(f"Regeneration requested for file : {imagePath}")
            self.new_image()
            ASCIIColors.info("Building new image")
            self.image_files.append(self.personality.lollms_paths.personal_outputs_path/"sd"/imagePath.split("/")[-1])
            ASCIIColors.info("Regenerating")
            return {"status":True, "message":"Image is now set as the current image for image to image operation"}

        return {"status":False, "message":"Unknown operation"}

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
        self.main_process(prompt, previous_discussion_text)

        return ""

