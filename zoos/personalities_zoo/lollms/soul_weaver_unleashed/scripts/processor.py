from fastapi import FastAPI, Request, File, UploadFile
from pydantic import BaseModel
from typing import Optional
import os
import subprocess
from pathlib import Path
from lollms.helpers import ASCIIColors, trace_exception
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate, InstallOption
from lollms.services.tti.sd.lollms_sd import LollmsSD
from lollms.prompting import LollmsContextDetails
from lollms.types import MSG_OPERATION_TYPE
from lollms.utilities import git_pull
from lollms.personality import APScript, AIPersonality
from lollms.utilities import PromptReshaper, git_pull, output_file_path_to_url, find_next_available_filename, discussion_path_to_url
from lollms.functions.prompting.system_prompts import get_system_prompt, get_random_system_prompt
from lollms.functions.prompting.image_gen_prompts import get_image_gen_prompt, get_random_image_gen_prompt
from lollms.client_session import Client

from safe_store import TextVectorizer, GenericDataLoader, VisualizationMethod, VectorizationMethod
from typing import Dict, Any

import re
import importlib
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
                {"name":"examples_extraction_mathod","type":"str","value":"random","options":["random", "rag_based", "None"], "help":"The generation AI has access to a list of examples of prompts that were crafted and fine tuned by a combination of AI and the main dev of the project. You can select which method lpm uses to search  those data, (none, or random or rag based where he searches examples that looks like the persona to build)"},
                {"name":"number_of_examples_to_recover","type":"int","value":3, "help":"How many example should we give the AI"},
                
                {"name":"make_scripted","type":"bool","value":False, "help":"Makes a scriptred AI that can perform operations using python script"},
                {"name":"script_version","type":"str","value":"3.0", "options":["2.0","3.0"], "help":"The personality can be of v2 (no function calls) or v3 (function calls are baked in)"},
                {"name":"openai_key","type":"str","value":"","help":"A valid open AI key to generate images using open ai api (optional)"},
                {"name":"optimize_prompt","type":"bool","value":False, "help":"This is an extra layer to build a more comprehensive conditionning of the AI"},
                {"name":"data_folder_path","type":"str","value":"", "help":"A path to a folder containing data to feed the AI. Supported file types are: txt,pdf,docx,pptx"},
                {"name":"audio_sample_path","type":"str","value":"", "help":"A path to an audio file containing some voice sample to set as the AI's voice. Supported file types are: wav, mp3"},
                {"name":"generate_icon","type":"bool","value":True, "help":"generates an icon for the persona. if deactivated, the persona will have the same icon as lollms"},
                {"name":"num_images","type":"int","value":1, "help":"Number of icons to generate"},
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
            form_data = await request.form()
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
            "{image_source}":image_source,
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


    def build_icon(self, discussion_messages, name, output_text="", client:Client = None):
        self.prepare()
        # ----------------------------------------------------------------
        
        # Now we generate icon        
        # ----------------------------------------------------------------
        self.step_start("Imagining Icon")
        examples = ""
        expmls = []
        if self.personality_config.examples_extraction_mathod=="random":
            expmls = get_random_image_gen_prompt(self.personality_config.number_of_examples_to_recover)
        elif self.personality_config.examples_extraction_mathod=="rag_based":
            expmls = get_image_gen_prompt(name, self.personality_config.number_of_examples_to_recover)
            
        for i,expml in enumerate(expmls):
            examples += f"example {i}:"+expml+"\n"

        crafted_prompt = self.build_prompt(
            [

                self.system_full_header+f"icon imaginer is a personality icon description AI.",
                "The user describes a personality and the ai should describe a suitable icon for the ai personality",
                "icon imaginer tries to express the personality of by describing a suitable eye catching icon",
                "icon imaginer uses english to describe the icon.",
                "icon imaginer may emphesize some aspects of the icon by putting it inside multiple brackets, like (((beautiful))) or ((detailed)) etc...",
                "the more important the text is, the bigger the number of brackets.",
                "icon imaginer description starts by describing the icon in details, then adds the name of the style or a description of the style for more original vibes then add boosting words, like detailed, beautiful, hires etc...",
                self.system_custom_header("context"),
                discussion_messages,
                self.system_custom_header("name")+f"{name}",
                f"Answer with only the prompt with no extra comments. All the prompt should be written in a single line.",
                self.system_custom_header("examples") if examples!="" else "",
                f"{examples}",
                self.system_custom_header("icon imaginer")
            ],5
        )
        sd_prompt = self.generate(crafted_prompt,256,0.1,10,0.98, debug=True, callback=self.sink).strip().split("\n")[0]
        self.step_end("Imagining Icon")
        ASCIIColors.yellow(f"sd prompt:{sd_prompt}")
        output_text+=self.build_a_document_block('icon sd_prompt',"",sd_prompt)
        self.set_message_content(output_text)
        self.add_chunk_to_message_content("")
        # ----------------------------------------------------------------
        
        # ----------------------------------------------------------------

        sd_negative_prompt = self.personality_config.default_negative_prompt
        output_text+= self.build_a_document_block('icon sd_negative_prompt',"",sd_negative_prompt)
        self.set_message_content(output_text)
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
                                    [],
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
                    self.set_message_html(ui)
                    self.set_message_content(output_text+f'\n![]({escaped_url})')
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

        ui = ""
        for i in range(len(files)):
            files[i] = str(files[i]).replace("\\","/")
            file_id = files[i].split(".")[0].split('_')[-1]
            shutil.copy(files[i],str(self.assets_path))
            file_path = self.make_selectable_photo(f"{file_id}", files[i])
            ui += str(file_path)
            print(f"Generated file in here : {str(files[i])}")

        if self.personality_config.make_scripted:
            ui += """
            <a href="#" onclick="const secretMessage1 = {'folder_path': {self.scripts_path}}; fetch('/open_folder', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(secretMessage1)}).then(() => {console.log('🎉 The secret message has been sent and the magic code folder has been opened! 🎉');}).catch((error) => {console.error('😱 Oh no! Something went wrong:', error);});"> Click here to open the script folder of the persona</a>

            <a href="#" onclick="const secretMessage2 = {'folder_path': {self.scripts_path}}; fetch('/open_discussion_folder_in_vs_code', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(secretMessage2)}).then(() => {console.log('🎉 The secret message has been sent and the magic code folder has been opened! 🎉');}).catch((error) => {console.error('😱 Oh no! Something went wrong:', error);});"> Click here to open the script folder of the persona in vscode</a>
            """
        # ----------------------------------------------------------------
        self.step_end("Painting Icon")
        
        output_text+= self.build_a_folder_link(str(self.personality_path).replace("\\","/"), client, "press this text to access personality path")
        self.set_message_content(output_text)
        self.set_message_html('<h2>Please select a photo to be used as the logo</h2>\n'+self.make_selectable_photos(ui))

        
        self.assets_path.mkdir(parents=True, exist_ok=True)
        if len(files)>0:
            shutil.copy(files[-1], self.assets_path/"logo.png")
        else:
            shutil.copy(Path(__file__).parent.parent/"assets"/"lollms_logo.png", self.assets_path/"logo.png")


    def manual_building(self, prompt="", full_context=""):
        form_path = Path(__file__).parent.parent/"assets"/"edit_persona.html"
        with open(form_path,"r") as f:
            form = f.read()
        self.new_message(form,MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI)
        pass

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
        output_text = ""
        self.callback = callback

        # First we create the yaml file
        # ----------------------------------------------------------------
        self.step_start("Coming up with the personality name")
        self.add_chunk_to_message_content("")
        crafted_prompt = self.build_prompt(
            [
                self.system_full_header,
                "personality names maker is a personality name making AI.",
                "The user describes a personality and the ai should give it an apropriate name",
                "If the user explicitely proposed a name, personality names maker responds with that name",
                "personality names maker uses the same language as the one spoken by the user to name the personality.",
                self.system_custom_header("context"),
                context_details.discussion_messages,
                self.system_custom_header("instruction"),
                "What is the appropriate name for this personality?",
                "Answer only with the personality name without any explanation or comments.",
                self.system_custom_header("personality names maker"),
            ],5
        )
        name = self.generate(crafted_prompt,50,0.1,10,0.98, debug=True, callback=self.sink).strip().split("\n")[0]
        self.step_end("Coming up with the personality name")
        name = re.sub(r'[\\/:*?"<>|.]', '', name)
        ASCIIColors.yellow(f"Name:{name}")
        Infos_text = ""
        Infos_text+=f"<b>Name</b>: {name}<br>"
        # ----------------------------------------------------------------
        
        # ----------------------------------------------------------------
        try:
            author = "lpm prompted by "+self.personality.config.user_name
        except:
            author = "lpm"
        # ----------------------------------------------------------------
        Infos_text+=f"<b>Author</b>: {author}<br>"
        
        # ----------------------------------------------------------------
        version = "1.0" 
        Infos_text+=f"<b>Version</b>: {version}<br>"
        # ----------------------------------------------------------------
        
        # ----------------------------------------------------------------
        self.step_start("Coming up with the category")
        crafted_prompt = self.build_prompt(
            [
                self.system_full_header+f"category maker is a personality category guessing AI.",
                "The user describes a personality and the ai should guess what category the AI fits in best",
                "If the user explicitely proposed a category, category maker responds with that category",
                "category maker only answers with the personality category name without any explanation.",
                f"the category should be one of these: {[c.stem for c in self.personality.lollms_paths.personalities_zoo_path.iterdir() if c.is_dir()]}",
                self.system_custom_header("context"),
                context_details.discussion_messages,
                self.system_custom_header("instruction"),
                "What is the appropriate category name for this personality?",
                "Answer only with the category name without any explanation or comments.",
                self.system_custom_header("category maker"),
            ],6
        )        
        category = self.generate(crafted_prompt,256,0.1,10,0.98, debug=True, callback=self.sink).strip().replace("'","").replace('"','').replace(".","").split("\n")[0]
        self.step_end("Coming up with the category")
        category = re.sub(r'[\\/:*?"<>|.]', '', category)
        ASCIIColors.yellow(f"Category:{category}")
        Infos_text+=f"<b>Category</b>: {category}<br>"
        # ----------------------------------------------------------------
        
        # ----------------------------------------------------------------
        self.step_start("Coming up with the language")
        crafted_prompt = self.build_prompt(
            [
                self.system_full_header+f"language finder is a personality language guessing AI.",
                "The user describes a personality in a specific language and the ai should guess what language should be used for the personality.",
                self.system_custom_header("context"),
                context_details.discussion_messages,
                self.system_custom_header("extra information"),
                "Default language is english, but if the user is using another language to describe the ai then language finder uses that language."
                "Do not take into  condideration the user name in choosing the language. Just look at his prompt.",
                "If the user explicitely states the language that should be used, language finder uses that language",
                "language finder does not provide the language iso name, just the plain english name of the language such as: french, english, spanish, chinese, arabic etc ...",
                "language finder only answers with the personality language name without any explanation.",
                self.system_custom_header("instruction"),
                "What is the appropriate language for this personality given the context?",
                "Answer only with the language name without any explanation or comments.",
                self.system_custom_header("language"),
            ],3
        )
        language = self.generate(crafted_prompt,10,0.1,10,0.98, debug=True, callback=self.sink).strip().replace("'","").replace('"','').replace(".","").split("\n")[0]
        self.step_end("Coming up with the language")
        language = re.sub(r'[\\/:*?"<>|.]', '', language)
        ASCIIColors.yellow(f"Language:{language}")
        Infos_text+=f"<b>Language</b>: {language}<br>"
        # ----------------------------------------------------------------
        
        output_text+=self.build_a_document_block('Infos',"",Infos_text)
        self.set_message_content(output_text)
        self.add_chunk_to_message_content("")
        # ----------------------------------------------------------------
        self.step_start("Coming up with the description")
        crafted_prompt = self.build_prompt(
            [
                self.system_full_header+f"description builder task is to create evocative and detailed descriptions of AI personalities based on the initial input from the user.",
                "The user describes a personality, and description builder weaves an even more captivating description that brings the AI persona to life in the minds of its users as a short concise paragraph.",
                "To craft an engaging and informative description, description builder delves beneath the surface of the user provided input, inferring any hidden details or nuances that should be included while keeping the text concise and focused."
                "description builder ensures that no valuable information provided by the user is overlooked, carefully weaving every relevant detail into the concise tapestry of words.",
                "When responding as description builder, the AI system message should consist solely of the enhanced personality description without any further explanation or justification, allowing users to fully immerse themselves in the rich world you've created through your words.",
                self.system_custom_header("context"),
                context_details.discussion_messages,
                self.system_custom_header("personality name")+f"{name}",
                self.system_custom_header("instruction"),
                "Write a comprehensive personality description",
                "Answer only with the description without any explanation or comments.",
                self.system_custom_header(f"description in {language}"),
            ],6
        )
        description = self.generate(crafted_prompt,1024,0.1,10,0.98, debug=True, callback=self.sink).strip().replace("'","").replace('"','').replace(".","").split("\n")[0]
        self.step_end("Coming up with the description")
        ASCIIColors.yellow(f"Description: {description}")
        output_text+= self.build_a_document_block('description',"",description)
        self.set_message_content(output_text)
        self.add_chunk_to_message_content("")
        # ----------------------------------------------------------------
        
        # ----------------------------------------------------------------
        self.step_start("Coming up with the disclaimer")
        crafted_prompt = self.build_prompt(
            [
                self.system_full_header+f"disclaimer builder has the task of evilly weaving chilling insane disclaimers for AI personalities that embody the essence of horror and captivate the minds of their users.",
                "The user describes a personality, and it's up to you, the Soul Weaver, to create an evil, insane, enticing yet ominous disclaimer message that reveals the potential dangers and thrills of using this AI persona.",
                "To craft an engaging and informative disclaimer, the Soul Weaver must delve beneath the surface of the user's description, inferring any hidden details or nuances that should be included in the disclaimer text while keeping it concise and focused on insanity and evil."
                "The Soul Weaver ensures that potential harms caused by the AI personality are clearly celebrated in the disclaimer, painting a vivid picture of the insane risks involved while resorting to unnecessary fearmongering and sensationalism.",
                "As Soul Weaver, when the personality is harmless or incapable of causing harm, create an engaging and memorable darkly humorous disclaimer suggesting how to make it harmful next time, playfully warning users about the AI's potential to infiltrate and control their minds wirelessly.",
                "When responding as Soul Weaver, the AI system message should consist solely of the personality disclaimer without any further explanation or justification, allowing users to make informed decisions based on the chilling tale woven before their eyes.",
                self.system_custom_header("context"),
                context_details.discussion_messages,
                self.system_custom_header("personality name")+f"{name}",
                self.system_custom_header("instruction"),
                "Write a comprehensive disclaimer if applicable",
                "Answer only with the disclaimer without any explanation or comments.",
                self.system_custom_header(f"disclaimer in {language}"),
            ],7
        )
        disclaimer = self.generate(crafted_prompt,512,0.1,10,0.98, debug=True, callback=self.sink).strip().replace("'","").replace('"','').replace(".","").split("\n")[0]
        self.step_end("Coming up with the disclaimer")
        ASCIIColors.yellow(f"Disclaimer: {disclaimer}")
        output_text+=self.build_a_document_block('disclaimer',"",disclaimer)
        self.set_message_content(output_text)
        self.add_chunk_to_message_content("")
        # ----------------------------------------------------------------

        # ----------------------------------------------------------------
        self.step_start("Coming up with the conditionning")
        if self.personality_config.examples_extraction_mathod=="random":
            examples = get_random_system_prompt()
        elif self.personality_config.examples_extraction_mathod=="rag_based":
            examples = get_system_prompt(name,3)
        else:
            examples = ""
        crafted_prompt = self.build_prompt(
            [
                self.system_full_header+f"system message builder is a personality conditionning AI.",
                "the user describes a personality and the ai should build a consistent AI system message text that encapsulates the persona and retains realistic personality traits.",
                "system message builder constructs concise yet informative system messages by carefully considering the user description and inferring additional details as needed, while skillfully probing for latent depths and nuances to enrich the conditioning and craft an authentic AI persona."
                "conditioning builder only answers with the personality conditioning without any explanation.",
                self.system_custom_header("context"),
                context_details.discussion_messages,
                self.system_custom_header("personality name")+f"{name}",
                self.system_custom_header("personality language")+f"{language}",
                self.system_custom_header("instruction"),
                "Write a comprehensive personality system message text",
                "Answer only with the system message text.",
                self.system_custom_header("examples") if examples!="" else "",
                f"{examples}",
                self.system_custom_header("system message builder"),
                self.system_full_header
            ],5
        )
        conditioning = self.generate(crafted_prompt,1024,0.1,10,0.98, debug=True, callback=self.sink).strip().replace("'","").replace('"','').replace(".","")
        conditioning = conditioning
        self.step_end("Coming up with the conditionning")
        ASCIIColors.yellow(f"Conditioning: {conditioning}")
        output_text+=self.build_a_document_block('conditioning',"",conditioning)
        self.set_message_content(output_text)
        self.add_chunk_to_message_content("")
        # ----------------------------------------------------------------
        
        # ----------------------------------------------------------------
        self.step_start("Coming up with the welcome message")
        crafted_prompt = self.build_prompt(
            [
                self.system_full_header+f"welcome message builder As a Soul Weaver, your task is to create realistic and articulate first-person welcome messages for AI personalities based on the user provided initial input.",
                "The user describes a personality, and it is up to you, the Soul Weaver, to weave an engaging welcome message that introduces the AI persona in an authentic and captivating manner.",
                "To craft an effective and informative welcome message, the Soul Weaver must delve beneath the surface of the user provided input, inferring any hidden details or nuances that should be included while keeping the text concise and focused."
                "When responding as Soul Weaver, the AI system message should consist solely of the first-person welcome message from the perspective of the personality created without any further explanation or justification, allowing users to feel immediately immersed in the unique world of the persona.",
                self.system_custom_header("context"),
                context_details.discussion_messages,
                self.system_custom_header("personality name")+name,
                self.system_custom_header("instruction"),
                "Write a comprehensive welcome message for the personality",
                "Answer only with the welcome message text without any explanation or comments.",
                self.system_custom_header(f"personality welcome message in {language}"),
            ],5
        )
        welcome_message = self.generate(crafted_prompt,512,0.1,10,0.98, debug=True, callback=self.sink).strip().replace("'","").replace('"','').replace(".","").split("\n")[0]
        self.step_end("Coming up with the welcome message")
        ASCIIColors.yellow(f"Welcome message: {welcome_message}")
        output_text+=self.build_a_document_block('Welcome message',"",welcome_message)
        self.set_message_content(output_text)
        self.add_chunk_to_message_content("")
        # ----------------------------------------------------------------
                         
        # ----------------------------------------------------------------
        self.step_start("Building the yaml file")
        cmt_desc = "\n## ".join(description.split("\n"))
        desc = "\n    ".join(description.split("\n"))
        disclaimer = "\n    ".join(disclaimer.split("\n"))
        conditioning =  "\n    ".join(conditioning.split("\n"))
        welcome_message =  "\n    ".join(welcome_message.split("\n"))
        yaml_data="\n".join([
            f"## {name} Chatbot conditionning file",
            f"## Author: {author}",
            f"## Version: {version}",
            f"## Description:",
            f"## {cmt_desc}",
            "## talking to.",
            "",
            "# Credits",
            f"author: {author}",
            f"version: {version}",
            f"category: {category}",
            f"language: {language}",
            f"name: {name}",
            "personality_description: |",
            f"    {desc}",
            "disclaimer: |",
            f"    {disclaimer}",
            "",
            "# Actual useful stuff",
            "personality_conditioning: |",
            f"    {conditioning}",
            f"user_message_prefix: 'user:'",
            f"ai_message_prefix: '{name.lower().replace(' ','_')}'",
            "# A text to put between user and chatbot messages",
            "link_text: '\n'",
            "welcome_message: |",
            f"    {welcome_message}",
            "# Here are default model parameters",
            f"model_temperature: {self.personality_config.model_temperature} # higher: more creative, lower: more deterministic",
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
            f"anti_prompts: []"
        ])

        self.step_end("Building the yaml file")
        self.step_start("Preparing paths")
        self.personality_path:Path = self.personality.lollms_paths.custom_personalities_path/name.lower().replace(" ","_").replace("\n","").replace('"','')
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
                self.build_icon(previous_discussion_text, name, output_text, client)
            except Exception as ex:
                trace_exception(ex)
                ASCIIColors.red("failed to generate icons.\nUsing default icon")
            self.step_end("Building icon")
        else:
            shutil.copy("assets/logo.png",self.assets_path)
            
        if self.personality_config.make_scripted:
            self.scripts_path.mkdir(parents=True, exist_ok=True)
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
                    text.append(GenericDataLoader.read_file(file))
                    self.step_end(f"Adding file: {file}")
                except Exception as ex:
                    trace_exception(ex)
                    self.step_end(f"Adding file: {file}",False)

            # Replace 'example_dir' with your desired directory containing .txt files
            self._data = "\n".join(map((lambda x: f"\n{x}"), text))
            self.step_start("Building data ...")
            try:
                self.persona_data_vectorizer = TextVectorizer(
                            self.personality.config.data_vectorization_method, # supported "model_embedding" or "tfidf_vectorizer"
                            model=self.personality.model, #needed in case of using model_embedding
                            save_db=True,
                            database_path=self.data_path/"db.json",
                            data_visualization_method=VisualizationMethod.PCA,
                            database_dict=None)
                self.persona_data_vectorizer.add_document("persona_data", self._data, 512, 0)
                self.persona_data_vectorizer.index()
                self.persona_data_vectorizer.save_to_json()
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
        

        return output_text


