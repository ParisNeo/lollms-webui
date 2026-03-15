"""
Project: LoLLMs
Personality: # Placeholder: Personality name (e.g., "Science Enthusiast")
Author: # Placeholder: Creator name (e.g., "ParisNeo")
Description: # Placeholder: Personality description (e.g., "A personality designed for enthusiasts of science and technology, promoting engaging and informative interactions.")
"""

from lollms.types import MSG_OPERATION_TYPE
from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality
from lollms.prompting import LollmsContextDetails
from lollms.client_session import Client
from lollms.functions.generate_image import build_image_from_simple_prompt
from lollms.functions.select_image_file import select_image_file_function
from lollms.functions.take_a_photo import take_a_photo_function

from lollms.utilities import discussion_path_to_url, app_path_to_url
import subprocess
from typing import Callable, Any
from functools import partial
from ascii_colors import trace_exception
import yaml
from datetime import datetime
from pathlib import Path
import shutil
import os
import shutil
import yaml
import git
import json

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
                {"name":"lollms_theme", "type":"bool", "value":False, "help":"Activate this if you want to use lollms theme"},
                {"name":"use_vue_js", "type":"bool", "value":False, "help":"If active instructs the AI to use vue.js"},
                {"name":"use_tailwind_css", "type":"bool", "value":False, "help":"Use tailwindcss for styling the ui"},

                {"name":"project_path", "type":"str", "value":"", "help":"Path to the current project."},
                {"name":"server_port_number", "type":"int", "value":8000, "help":"If a backend is active, use this port number"},                
                {"name":"update_mode", "type":"str", "value":"rewrite", "options":["rewrite","edit"], "help":"The update mode specifies if the AI needs to rewrite the whole code which is a good idea if the code is not long or just update parts of the code which is more suitable for long codes."},
                {"name":"interactive_mode", "type":"bool", "value":False, "help":"Activate this mode to start talking to the AI about snippets of your code. The AI will generate updates depending on your own requirements in an interactive way."},
                {"name":"build_a_backend", "type":"bool", "value":False, "help":"Builds a backend server.py. Required if a serverside code is required"},
                {"name":"create_a_plan", "type":"bool", "value":False, "help":"Create a plan for the app before starting."},
                {"name":"generate_icon", "type":"bool", "value":False, "help":"Generate an icon for the application (requires tti to be active)."},
                {"name":"use_lollms_library", "type":"bool", "value":False, "help":"Activate this if the application requires interaction with lollms."},
                {"name":"force_lollms_multisupport", "type":"bool", "value":False, "help":"If active, the app created should add a setting panel that allows setting lollms settings like the server to be used etc."},
                {"name":"use_lollms_tasks_library", "type":"bool", "value":False, "help":"Activate this if the application needs to use text code extraction, text summary, yes no question answering, multi choice question answering etc."},
                {"name":"use_lollms_rag_library", "type":"bool", "value":False, "help":"Activate this if the application needs to use text code extraction, text summary, yes no question answering, multi choice question answering etc."},
                {"name":"use_lollms_image_gen_library", "type":"bool", "value":False, "help":"(not ready yet) Activate this if the application requires image generation."},
                {"name":"use_lollms_audio_gen_library", "type":"bool", "value":False, "help":"(not ready yet) Activate this if the application requires audio manipulation."},
                {"name":"use_lollms_speach_library", "type":"bool", "value":False, "help":"Activate this if the application requires audio transdcription."},

                {"name":"use_lollms_localization_library", "type":"bool", "value":False, "help":"Activate this library if you want to automatically localize your application into multiple languages."},
                {"name":"use_lollms_flow_library", "type":"bool", "value":False, "help":"Activate this library if you want to use lollms flow library in your application into multiple languages."},
                {"name":"lollms_anything_to_markdown_library", "type":"bool", "value":False, "help":"Activate this library if you want to use lollms anything to markdown library which allows you to read any text type of files and returns it as markdown (useful for RAG)."},
                {"name":"lollms_markdown_renderer", "type":"bool", "value":False, "help":"Activate this library if you want to use lollms markdown renderer that allows you to render markdown text with support for headers, tables, code as well as converting mermaid code into actual mermaid graphs"},

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
        self.application_categories = [
            "Productivity",
            "Coding",
            "Project Management",
            "Games",
            "Communication",
            "Entertainment",
            "Finance",
            "Health & Fitness",
            "Education",
            "Travel & Navigation",
            "Utilities",
            "Creative",
            "E-commerce"
        ]
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
        
    def get_lollms_infos(self):
        if self.personality_config.use_lollms_library:
            with open(Path(__file__).parent.parent/"assets"/"docs"/"lollms_client_js_info.md","r", errors="ignore") as f:
                lollms_infos = f.read() + "\n"
        else:
            lollms_infos = ""
        
        
        if self.personality_config.force_lollms_multisupport:
            lollms_infos += f"{self.system_custom_header('important instruction')}Make sure to add a settings pannel that allows the user to select the lollms host and the ELF_GENERATION_FORMAT.\n"

        if self.personality_config.use_lollms_rag_library:
            with open(Path(__file__).parent.parent/"assets"/"docs"/"lollms_rag_info.md","r", errors="ignore") as f:
                lollms_infos += f.read() + "\n"

        if self.personality_config.use_lollms_image_gen_library:
            with open(Path(__file__).parent.parent/"assets"/"docs"/"lollms_tti.md","r", errors="ignore") as f:
                lollms_infos += f.read() + "\n"


        if self.personality_config.use_lollms_speach_library:
            with open(Path(__file__).parent.parent/"assets"/"docs"/"lollms_speach.md","r", errors="ignore") as f:
                lollms_infos += f.read() + "\n"


        if self.personality_config.use_lollms_localization_library:
            with open(Path(__file__).parent.parent/"assets"/"docs"/"lollms_auto_localizer.md","r", errors="ignore") as f:
                lollms_infos += f.read() + "\n"

        if self.personality_config.use_lollms_flow_library:
            with open(Path(__file__).parent.parent/"assets"/"docs"/"lollms_flow.md","r", errors="ignore") as f:
                lollms_infos += f.read() + "\n"

        if self.personality_config.lollms_anything_to_markdown_library:
            with open(Path(__file__).parent.parent/"assets"/"docs"/"lollms_anything_to_markdown.md","r", errors="ignore") as f:
                lollms_infos += f.read() + "\n"

        if self.personality_config.lollms_markdown_renderer:
            with open(Path(__file__).parent.parent/"assets"/"docs"/"lollms_markdown_renderer.md","r", errors="ignore") as f:
                lollms_infos += f.read() + "\n"

        if self.personality_config.lollms_theme:
            with open(Path(__file__).parent.parent/"assets"/"docs"/"lollms_theme.md","r", errors="ignore") as f:
                lollms_infos += f.read() + "\n"
        if self.personality_config.use_vue_js:
            lollms_infos += f"{self.system_custom_header('important instruction')}Please use vue3.\n"
        if self.personality_config.use_tailwind_css:
            lollms_infos += f"{self.system_custom_header('important instruction')}Please use tailwindcss for styling.\n"

        

        if self.personality_config.use_lollms_tasks_library:
            with open(Path(__file__).parent.parent/"assets"/"docs"/"lollms_taskslib_js_info.md","r", errors="ignore") as f:
                lollms_infos += f.read()
        
        tk = self.personality.model.tokenize(lollms_infos)
        ltk = len(tk)
        if ltk>self.personality.config.ctx_size:
            ASCIIColors.red("WARNING! The lollms_infos is bigger than the context. The quality will be reduced and the mùodel may fail!!")        
            self.warning("WARNING! The lollms_infos is bigger than the context. The quality will be reduced and the mùodel may fail!!")
        elif ltk>self.personality.config.ctx_size-1024:
            ASCIIColors.red("WARNING! The lollms_infos is filling a huge chunk of the context. You won't have enough space for the generation!!")        
            self.warning("WARNING! The lollms_infos is filling a huge chunk of the context. You won't have enough space for the generation!!")
        
        return lollms_infos        

    def buildPlan(self, context_details, metadata, client:Client):
        self.step_start("Building initial_plan.txt")
        crafted_prompt = self.build_prompt([
            self.system_full_header,
            "You are Lollms Apps Planner, an expert AI assistant designed to create comprehensive plans for Lollms applications.",
            "Your primary objective is to generate a detailed and structured plan for the single file web app based on the user's description of a web application.",
    	    "Announce the name of the web app.",
            "Express the user requirements in a better wording.",
            "Make sure you keep any useful information about libraries to use or code examples.",
            "Plan elements of the user interface.",
            "Plan the use cases",
    	    "Take into consideration that this code is a single html file with css and javascript.",
            "Do not ask the user for any additional information. Respond only with the plan.",
            "Answer with the plan without any extra explanation or comments.",
            "The plan must be a markdown text with headers and organized elements.",
            self.system_custom_header("context"),
            context_details.discussion_messages,
            self.system_custom_header("Lollms Apps Planner")
        ])
        if len(self.personality.image_files)>0:
            app_plan = self.generate_with_images(crafted_prompt, self.personality.image_files,512,0.1,10,0.98, debug=True, callback=self.sink)
        else:
            app_plan = self.generate(crafted_prompt,temperature=0.1, top_k=10, top_p=0.98, debug=True, callback=self.sink)

        # Store plan into context
        metadata["plan"]=app_plan
        client.discussion.set_metadata(metadata)
        self.step_end("Building initial_plan.txt")
        return app_plan

    def buildDescription(self, context_details, metadata, client:Client):
        self.step_start("Building description.yaml")
        crafted_prompt = self.build_prompt(
            [
                self.system_full_header,
                "Your objective is to build the description.yaml file for a specific lollms application.",
                "The user describes a web application and the ai should build the yaml file and return it inside a yaml markdown tag",
                "If the user explicitely proposed a name, use that name",
                "Build the description.yaml file.",
                "Do not ask the user for any extra information and only respond with the yaml content in a yaml markdown tag.",
                self.system_custom_header("context"),
                context_details.discussion_messages,
            ],7
        )
        template =f"""
```yaml
name: [Give a name to the application using the user provided information]
description: [Here you can make a detailed description of the application. do not use : or lists, just plain text in a single paragraph.]
version: 1.0
author: [make the user the author]
category: [give a suitable category name from {self.application_categories}]
model: {self.personality.model.model_name}
disclaimer: [If needed, write a disclaimer. else null]
```
"""
        code = self.generate_code(crafted_prompt, self.personality.image_files, template, "yaml", callback=self.sink)
        if len(code)>0:
            ASCIIColors.info(code)
            infos = yaml.safe_load(code)
            infos["creation_date"]=datetime.now().isoformat()
            infos["last_update_date"]=datetime.now().isoformat()
            if self.config.debug:
                ASCIIColors.yellow("--- Description file ---")
                ASCIIColors.yellow(infos)
            app_path = self.personality.lollms_paths.apps_zoo_path/infos["name"].replace(" ","_").replace("'","_")
            app_path.mkdir(parents=True, exist_ok=True)
            metadata["app_path"]=str(app_path)
            self.personality_config.project_path = str(app_path)
            self.personality_config.save()
            metadata["infos"]=infos
            client.discussion.set_metadata(metadata)
            self.step_end("Building description.yaml")
            out =  """
<div class="max-w-md mx-auto my-2">
    <div class="bg-blue-500 text-white rounded-lg py-2 px-4 inline-block shadow-md">
        Description built successfully.
    </div>
</div>
    """             
            self.set_message_html(out)            
            return infos
        else:
            out =  """
    <div class="max-w-md mx-auto my-2">
        <div class="bg-red-500 text-white rounded-lg py-2 px-4 inline-block shadow-md">
            Couldn't build description
        </div>
    </div>
    """             
            self.set_message_html(out)            
            self.step_end("Building description.yaml", False)
            return None


    def updateDescription(self, context_details, metadata, client:Client):
        if "app_path" in metadata and  metadata["app_path"] and "infos" in metadata:
            old_infos = metadata["infos"]
        elif "app_path" in metadata and  metadata["app_path"] :
            with open(Path(metadata["app_path"])/"description.yaml", "r") as f:
                old_infos = yaml.safe_load(f)

        self.step_start("Building description.yaml")
        crafted_prompt = self.build_prompt(
            [
                self.system_full_header,
                "you are Lollms Apps Maker. Your objective is to build the description.yaml file for a specific lollms application.",
                "The user is acsking to modify the description file of the web application and the ai should build the yaml file and return it inside a yaml markdown tag",
                "If the user explicitely proposed a name, use that name. If not, fill in the blacks and imagine the best possible app from the context.",
                "Your sole objective is to build the description.yaml file. Do not ask the user for any extra information and only respond with the yaml content in a yaml markdown tag.",
                self.system_custom_header("context"),
                context_details.discussion_messages,
            ],6
        )
        template= f"""```yaml
name: {old_infos.get("name", "[the name of the app]")}
description: {old_infos.get("description", "[the description of the app]")}
version: {old_infos.get("version", "[the version of the app (if not specified by the user it should be 1.0)]")}
author: {old_infos.get("author", "[the author of the app (if not specified by the user it should be the user name)]")}
category: {old_infos.get("category", "[the category of the app]")}
model: {self.personality.model.model_name}
disclaimer: {old_infos.get("disclaimer", "[If needed, write a disclaimer. else null]")} 
```
"""
        code = self.generate_code(crafted_prompt, self.personality.image_files, template, "yaml")
        infos = yaml.safe_load(code)
        infos["creation_date"]=old_infos["creation_date"]
        infos["last_update_date"]=datetime.now().isoformat()
        if self.config.debug:
            ASCIIColors.yellow("--- Description file ---")
            ASCIIColors.yellow(infos)
        app_path = self.personality.lollms_paths.apps_zoo_path/infos["name"].replace(" ","_").replace("'","_")
        app_path.mkdir(parents=True, exist_ok=True)
        metadata["app_path"]=str(app_path)
        metadata["infos"]=infos
        self.personality_config.project_path = str(app_path)
        self.personality_config.save()            
        client.discussion.set_metadata(metadata)
        self.step_end("Building description.yaml")
        return infos

    def build_index(self, context_details, infos, metadata, client:Client):
        self.step_start("Building index.html")
        lollms_infos = self.get_lollms_infos()
        if self.personality_config.build_a_backend:
            backend_endpoints = self.system_custom_header("Backend endpoints") + self.extract_endpoints(metadata) + "\nUse axios for endpoint calling."
        else:
            backend_endpoints = ""


        crafted_prompt = self.build_prompt(
            [
                "Your objective is to build the index.html file for a specific lollms application.",
                "The user describes a web application and the ai should build a single html code to fullfill the application requirements.",
                "Make sure the application is visually appealing and try to use reactive design with tailwindcss",
                "The output must be in a html markdown code tag",
                "Your sole objective is to build the index.yaml file that does what the user is asking for.",
                "Do not ask the user for any extra information and only respond with the html content in a html markdown tag.",
                "Do not leave place holders. The code must be complete and works out of the box.",
                self.system_custom_header("description"),
                "\n".join([
                "```yaml",
                str(infos),
                "```"
                ]),
                "Start by building a plan then write the full index.html file without any further explanations."  if self.personality_config.create_a_plan is None else "Write the full index.html file without any further explanations.",                        
                self.system_custom_header("context"),
                context_details.discussion_messages,                     
                lollms_infos,
                backend_endpoints,
            ],6
        )

        code = self.generate_code(crafted_prompt, self.personality.image_files, "[The html code]", language="html", temperature=0.1, top_k=10, top_p=0.98, debug=True)
        if self.config.debug:
            ASCIIColors.yellow("--- Code file ---")
            ASCIIColors.yellow(code)
        app_path = metadata["app_path"]
        if len(code)>0:
            # Backup the existing index.html file
            index_file_path = Path(metadata["app_path"]) / "index.html"
            if index_file_path.exists():
                try:
                    if not (Path(app_path) / ".git").exists():
                        repo = git.Repo.init(app_path)
                    else:
                        repo = git.Repo(app_path)
                    # Stage the current version of index.html
                    repo.index.add([os.path.relpath(index_file_path, app_path)])
                    repo.index.commit(f"Backup before update.")
                except Exception as ex:
                    trace_exception(ex)
            self.step_end("Building index.html")
            return code
        else:
            self.step_end("Building index.html", False)
            self.set_message_content("The model you are using failed to build the index.html file. Change the prompt a bit and try again.")
            return None

    def build_server(self, context_details, infos, metadata, client: Client):
        self.step_start("Building server.py")
        lollms_infos = self.get_lollms_infos()
        lollms_infos += f"""
Infos: The client will be running on an server that is not the same as the one we are building so we need to make sure that the client accept cors from all localhost sources. Also, use localhost as hostname and {self.personality_config.server_port_number} as port number.
        """ 

        crafted_prompt = self.build_prompt(
            [
                self.system_full_header,
                "You are Lollms Apps Maker. Your objective is to build the server.py file for a specific Lollms application.",
                "The user describes a web application, and you should build a FastAPI server code to fulfill the application requirements.",
                "Make sure to include all necessary imports, create the FastAPI app, and implement the required endpoints.",
                "The output must be in a Python markdown code tag",
                "Your sole objective is to build the server.py file that does what the user is asking for.",
                "Do not ask the user for any extra information and only respond with the Python content in a Python markdown tag.",
                "Do not leave placeholders. The code must be complete and work out of the box.",
                self.system_custom_header("description"),
                "\n".join([
                "```yaml",
                str(infos),
                "```"
                ]),
                "Start by building a plan."  if self.personality_config.create_a_plan is None else "",                        
                lollms_infos,
                self.system_custom_header("context"),
                context_details.discussion_messages,
                
                self.system_custom_header("Lollms Apps Maker")
            ],
            6
        )
        
        code = self.generate_code(crafted_prompt, self.personality.image_files, temperature=0.1, top_k=10, top_p=0.98, debug=True, callback=self.sink)
        
        if self.config.debug:
            ASCIIColors.yellow("--- Code file ---")
            ASCIIColors.yellow(code)
        
        app_path = metadata["app_path"]
        if len(code) > 0:
            # Backup the existing server.py file
            server_file_path = Path(metadata["app_path"]) / "server.py"
            if server_file_path.exists():
                try:
                    if not (Path(app_path) / ".git").exists():
                        repo = git.Repo.init(app_path)
                    else:
                        repo = git.Repo(app_path)

                    # Stage the current version of server.py
                    repo.index.add([os.path.relpath(server_file_path, app_path)])
                    repo.index.commit("Backup before update")
                except Exception as ex:
                    trace_exception(ex)
            
            self.step_end("Building server.py")

            return code
        else:
            self.step_end("Building server.py", False)
            self.set_message_content("The model you are using failed to build the server.py file. Change the prompt a bit and try again or use a smarter model.")
            return None


    def update_index(self, prompt, context_details, metadata, out:str):
        if not metadata.get("app_path", None):
            self.set_message_content("""
<div style="background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
    <h3 style="margin-top: 0;">⚠️ No Application Path Found</h3>
    <p>It appears that no application path is present in this discussion. Before attempting to make updates, you need to create a new project first.</p>
    <p>You can also set a manual application path in the settings of the personality to continue working on that application.</p>                                     
    <p>Please ask about creating a new project, and I'll be happy to guide you through the process.</p>
</div>
            """)
            return

        out +=  """
<div class="max-w-md mx-auto my-2">
    <div class="bg-blue-500 text-white rounded-lg py-2 px-4 inline-block shadow-md flex items-center space-x-2">
        <span>You asked me to update the index.html code. Let's go ...</span>
        <div class="flex space-x-1">
            <div class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 0s;"></div>
            <div class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 0.2s;"></div>
            <div class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 0.4s;"></div>
        </div>
    </div>
</div>
"""             
        self.set_message_html(out)    
        
        app_path = Path(metadata["app_path"])
        index_file_path = app_path / "index.html"

        # Initialize Git repository if not already initialized
        self.step_start("Backing up previous version")
        app_path = Path(metadata["app_path"])
        try:
            if not (app_path / ".git").exists():
                repo = git.Repo.init(app_path)
            else:
                repo = git.Repo(app_path)

            # Stage and commit the icon
            try:
                repo.index.add([os.path.relpath(index_file_path, app_path)])
                repo.index.commit("Backing up index.html")        
            except Exception:
                pass        
        except Exception as ex:
            self.warning(str(ex))
        self.step_end("Backing up previous version")



        self.step_start("Updating index.html")
        with open(index_file_path, "r", encoding="utf8") as f:
            original_content = f.read()

        if self.personality_config.build_a_backend:
            backend_endpoints = self.system_custom_header("Backend endpoints") + self.extract_endpoints(metadata) + "\nUse axios for endpoint calling."
        else:
            backend_endpoints = ""

        if self.personality_config.update_mode=="rewrite":
            crafted_prompt = self.build_prompt([
                self.system_custom_header("Documentation"),
                self.get_lollms_infos(),
                self.system_custom_header("Instruction"),
                "Rewrite the code to fit the user prompt.",
                backend_endpoints,
                "ORIGINAL CODE:",
                "```html",
                original_content,
                "```",
                "CRITICAL: ANY SHORTCUTS OR PLACEHOLDERS = INSTANT REJECTION",
                "WRITE EVERY SINGLE LINE OF CODE. NO EXCEPTIONS.",
                "Avoid asking the user to fill in the blancks and make sure the code you provide is complete.",
                self.user_custom_header("user"),
                prompt,
                self.ai_custom_header("assistant"),
            ])
            


            code, full_response = self.generate_code(crafted_prompt, self.personality.image_files, language="html", temperature=0.1, top_k=10, top_p=0.98, debug=True, return_full_generated_code=True)
            self.add_chunk_to_message_content("\n")
            if self.config.debug:
                ASCIIColors.yellow("--- Code file ---")
                ASCIIColors.yellow(code)

            if len(code) > 0:
                self.step_end("Updating index.html")
                self.step_start("Backing up previous version")       
                # Stage the current version of index.html
                repo.index.add([os.path.relpath(index_file_path, app_path)])
                repo.index.commit("Backup before update")
                self.step_end("Backing up previous version")
                # Write the updated content back to index.html
                index_file_path.write_text(code, encoding='utf8')
                
                # Stage and commit the changes
                repo.index.add([os.path.relpath(index_file_path, app_path)])
                repo.index.commit("Update index.html")
                
                out += """
<div class="max-w-md mx-auto my-2">
    <div class="bg-blue-500 text-white rounded-lg py-2 px-4 inline-block shadow-md flex items-center space-x-2">
        <span>I finished coding</span>
        <span class="text-xl">😊</span>
    </div>
</div>
"""
            else:
                self.step_end("Updating index.html", False)
                out += "No sections were updated."

            self.step_end("Updating index.html")

            self.set_message_html(out)            
        else:
            crafted_prompt = self.build_prompt(
                [
                    self.system_full_header,
                    "You are Lollms Apps Maker. Your objective is to update the HTML, JavaScript, and CSS code for a specific lollms application.",
                    "The user gives the code the AI should update the code parts using the following syntax",
                    "To update existing code:",
                    "```python",
                    "# REPLACE",
                    "# ORIGINAL",
                    "<old_code>",
                    "# SET",
                    "<new_code_snippet>",
                    "```",
                    "The ORIGINAL statement (<old_code>) should contain valid code from the orginal code. It should be a full statement and not just a fragment of a statement.",
                    "The SET statement (<new_code_snippet>) is mandatory. You should put the new lines of code just after it.",
                    "Make sure if possible to change full statements or functions. The code to SET must be fully working and without placeholders.",
                    "To add code, use the same REPLACE syntax with the last line before where you must add you new code then in the SET rewrite that line and then the new lines to add.",
                    "The code to SET must be fully working and without placeholders.",
                    "Update the code from the user suggestion",
                    self.system_custom_header("context"),
                    context_details.discussion_messages,
                    self.get_lollms_infos(),
                    self.system_custom_header("Code"),
                    "<file_name>index.html</file_name>",
                    "```html",
                    original_content,
                    "```",
                    self.system_custom_header("Lollms Apps Maker")
                ],24
            )
            if len(self.personality.image_files)>0:
                updated_sections = self.generate_with_images(crafted_prompt, self.personality.image_files, temperature=0.1, top_k=10, top_p=0.98, debug=True, callback=self.sink)
            else:
                updated_sections = self.generate(crafted_prompt, temperature=0.1, top_k=10, top_p=0.98, debug=True, callback=self.sink)


            # Extract code blocks
            codes = self.extract_code_blocks(updated_sections)
            if len(codes) > 0:
                # Stage the current version of index.html
                repo.index.add([os.path.relpath(index_file_path, app_path)])
                repo.index.commit("Backup before update")
                
                for code_block in codes:
                    original_code, new_code = self.parse_code_replacement(code_block["content"])
                    original_content = self.update_code_with_best_match(original_content, original_code, new_code)
                
                # Write the updated content back to index.html
                index_file_path.write_text(original_content, encoding='utf8')
                
                # Stage and commit the changes
                repo.index.add([os.path.relpath(index_file_path, app_path)])
                repo.index.commit("Update index.html")
                
                out += f"Updated index file:\n```html\n{original_content}\n```\n"
            else:
                out += "No sections were updated."

            self.step_end("Updating index.html")


    def update_server(self, prompt, context_details, metadata, out: str):
        if not metadata.get("app_path", None):
            self.set_message_content("""
<div style="background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
    <h3 style="margin-top: 0;">⚠️ No Application Path Found</h3>
    <p>It appears that no application path is present in this discussion. Before attempting to make updates, you need to create a new project first.</p>
    <p>You can also set a manual application path in the settings of the personality to continue working on that application.</p>                                     
    <p>Please ask about creating a new project, and I'll be happy to guide you through the process.</p>
</div>
            """)
            return

        out = ""
        
        app_path = Path(metadata["app_path"])
        server_file_path = app_path / "server.py"

        # Initialize Git repository if not already initialized
        self.step_start("Backing up previous version")
        app_path = Path(metadata["app_path"])
        if not (app_path / ".git").exists():
            repo = git.Repo.init(app_path)
        else:
            repo = git.Repo(app_path)

        # Stage and commit the server file
        try:
            repo.index.add([os.path.relpath(server_file_path, app_path)])
            repo.index.commit("Backing up server.py")        
        except Exception:
            pass        
        self.step_end("Backing up previous version")

        self.step_start("Updating server.py")
        with open(server_file_path, "r", encoding="utf8") as f:
            original_content = f.read()

        if self.personality_config.update_mode == "rewrite":
            crafted_prompt = self.build_prompt(
                [
                    self.system_full_header,
                    "You are Lollms Apps Maker best application maker ever.",
                    "Your objective is to update the Python code for a specific lollms FastAPI application.",
                    "The user gives the code and you should rewrite all the code with modifications suggested by the user.",
                    "Your sole objective is to satisfy the user",
                    "Always write the output in a python markdown tag",
                    self.system_custom_header("context"),
                    prompt,
                    self.get_lollms_infos(),
                    self.system_custom_header("Code"),
                    "server.py",
                    "```python",
                    original_content,
                    "```",
                    self.system_custom_header("Very important"),
                    "It is mandatory to rewrite the whole code in a single code tag without any comments.",
                    "Before writing the updates list the upgrades you are going to do.",
                    "The written code must be complete without simplifications or todos.",
                    self.system_custom_header("Lollms Apps Maker")
                ]
            )
            code, full_response = self.generate_code(crafted_prompt, self.personality.image_files, temperature=0.1, top_k=10, top_p=0.98, debug=True, return_full_generated_code=True)
            self.add_chunk_to_message_content("\n")
            if self.config.debug:
                ASCIIColors.yellow("--- Code file ---")
                ASCIIColors.yellow(code)

            if len(code) > 0:
                self.step_end("Updating server.py")
                self.step_start("Backing up previous version")       
                # Stage the current version of server.py
                repo.index.add([os.path.relpath(server_file_path, app_path)])
                repo.index.commit("Backup before update")
                self.step_end("Backing up previous version")
                # Write the updated content back to server.py
                server_file_path.write_text(code, encoding='utf8')
                
                # Stage and commit the changes
                repo.index.add([os.path.relpath(server_file_path, app_path)])
                repo.index.commit("Update server.py")
                
                out += full_response
            else:
                self.step_end("Updating server.py", False)
                out += "No sections were updated."

            self.step_end("Updating server.py")

            self.set_message_html(out)            
        else:
            crafted_prompt = self.build_prompt(
                [
                    self.system_full_header,
                    "You are Lollms Apps Maker. Your objective is to update the Python code for a specific lollms FastAPI application.",
                    "The user gives the code the AI should update the code parts using the following syntax",
                    "To update existing code:",
                    "```python",
                    "# REPLACE",
                    "# ORIGINAL",
                    "<old_code>",
                    "# SET",
                    "<new_code_snippet>",
                    "```",
                    "The ORIGINAL statement (<old_code>) should contain valid code from the orginal code. It should be a full statement and not just a fragment of a statement.",
                    "The SET statement (<new_code_snippet>) is mandatory. You should put the new lines of code just after it.",
                    "Make sure if possible to change full statements or functions. The code to SET must be fully working and without placeholders.",
                    "If there is no ambiguity, just use a single line of code for each (first line to be changed and last line to be changed).",
                    "When providing code changes, make sure to respect the indentation in Python. Only provide the changes, do not repeat unchanged code. Use comments to indicate the type of change.",
                    "If too many changes needs to be done, and you think a full rewrite of the code is much more adequate, use this syntax:",
                    "```python",
                    "# FULL_REWRITE",
                    "<new_full_code>",
                    "```",
                    "Select the best between full rewrite and replace according to the amount of text to update.",
                    "Update the code from the user suggestion",
                    self.system_custom_header("context"),
                    context_details.discussion_messages,
                    self.get_lollms_infos(),
                    self.system_custom_header("Code"),
                    "<file_name>server.py</file_name>",
                    "```python",
                    original_content,
                    "```",
                    self.system_custom_header("Lollms Apps Maker")
                ],24
            )
            if len(self.personality.image_files)>0:
                updated_sections = self.generate_with_images(crafted_prompt, self.personality.image_files, temperature=0.1, top_k=10, top_p=0.98, debug=True, callback=self.sink)
            else:
                updated_sections = self.generate(crafted_prompt, temperature=0.1, top_k=10, top_p=0.98, debug=True, callback=self.sink)
            self.add_chunk_to_message_content("\n")

            # Extract code blocks
            codes = self.extract_code_blocks(updated_sections)
            if len(codes) > 0:
                # Stage the current version of server.py
                repo.index.add([os.path.relpath(server_file_path, app_path)])
                repo.index.commit("Backup before update")

                for code_block in codes:
                    original_code, new_code = self.parse_code_replacement(code_block["content"])
                    out_ = self.update_code_with_best_match(original_content, original_code, new_code)
                    if out_["hasQuery"]:
                        out += f"Updated server file with new code\n"
                    else:
                        print(f"Warning: The AI did not manage to update the code!")
                
                # Write the updated content back to server.py
                server_file_path.write_text(out_["updatedCode"], encoding='utf8')
                
                # Stage and commit the changes
                repo.index.add([os.path.relpath(server_file_path, app_path)])
                repo.index.commit("Update server.py")
                
                out += f"Updated server file:\n```python\n{out_['updatedCode']}\n```\n"
            else:
                out += "No sections were updated."

            self.step_end("Updating server.py")

    def extract_endpoints(self, metadata):
        app_path = Path(metadata["app_path"])
        server_file_path = app_path / "server.py"
        code = server_file_path.read_text("utf-8")
        self.step_end("EXPORTING server endpoints and their input/output format")   
        server_description = self.generate(self.system_full_header+"You are backend summarizer. You extract from the backend code all endpoints and you also return the server address, port number and information about CORS. The endpoints description must contain a representation of all endpoints and their input/output formats. "+self.ai_custom_header("Code")+"\n```python\n"+code+"\n```\n"+self.ai_custom_header("endpoints description"))     
        self.step_end("EXPORTING server endpoints and their input/output format")
        self.add_chunk_to_message_content("\n")
        return server_description

    def build_documentation(self, prompt, context_details, metadata, out:str):
        if not metadata.get("app_path", None):
            self.set_message_content("""
<div style="background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
    <h3 style="margin-top: 0;">⚠️ No Application Path Found</h3>
    <p>It appears that no application path is present in this discussion. Before attempting to make updates, you need to create a new project first.</p>
    <p>You can also set a manual application path in the settings of the personality to continue working on that application.</p>                                     
    <p>Please ask about creating a new project, and I'll be happy to guide you through the process.</p>
</div>
            """)
            return

        out = ""
        
        app_path = Path(metadata["app_path"])
        index_file_path = app_path / "index.html"
        doc_file_path = app_path / "README.md"

        # Initialize Git repository if not already initialized
        self.step_start("Backing up previous version")
        app_path = Path(metadata["app_path"])

        # Stage and commit the icon
        try:
            if not (app_path / ".git").exists():
                repo = git.Repo.init(app_path)
            else:
                repo = git.Repo(app_path)
            repo.index.add([os.path.relpath(doc_file_path, app_path)])
            repo.index.commit("Backing up README.md")        
        except Exception:
            pass        
        self.step_end("Backing up previous version")



        self.step_start("Updating README.md")
        # First read code
        with open(index_file_path, "r", encoding="utf8") as f:
            original_content = f.read()


        crafted_prompt = self.build_prompt(
            [
                self.system_full_header,
                "You are Lollms Apps Documenter best application maker ever.",
                "Your objective is to build a documentation for this webapp.",
                "The user asks for the kind of documentation he wants and you need to write a documentation in markdown format.",
                "Your sole objective is to satisfy the user",
                self.system_custom_header("context"),
                prompt,
                self.get_lollms_infos(),
                self.system_custom_header("code to document"),
                "index.html",
                "```html",
                original_content,
                "```",
                self.system_custom_header("Very important"),
                "Answer with the generated documentation without any comment or explanation.",
                self.system_custom_header("Lollms Apps Documenter")
            ]
        )
        doc = self.generate(crafted_prompt, self.personality.image_files,temperature=0.1, top_k=10, top_p=0.98, debug=True, callback=self.sink)
        if self.config.debug:
            ASCIIColors.yellow("--- Code file ---")
            ASCIIColors.yellow(doc)

        self.step_end("Updating README.md")
        # Write the updated content back to README.md
        doc_file_path.write_text(doc, encoding='utf8')
                
        out += doc

        self.step_end("Updating README.md")

        self.set_message_html(out)      

    def generate_icon(self, metadata, infos, client):
        self.step_start("Backing up previous version")
        app_path = Path(metadata["app_path"])
        if not (app_path / ".git").exists():
            repo = git.Repo.init(app_path)
        else:
            repo = git.Repo(app_path)

        #path to the output icon
        icon_dst = str(app_path/"icon.png")
        # Stage and commit the icon
        try:
            repo.index.add([os.path.relpath(icon_dst, app_path)])
            repo.index.commit("Add icon.png")        
        except Exception:
            pass        
        self.step_end("Backing up previous version")
        out = self.build_message_element_with_thinking_animation("I am generating an icon")
        self.set_message_html(out)        
        if self.personality_config.generate_icon:
            try:
                self.step_start("Generating icon")
                crafted_prompt = self.build_prompt(
                    [
                        "Make an icon for this application:"
                        "```yaml",
                        str(infos),
                        "```",
                        "The icon should depict the essence of the application as described in the description."
                    ]
                )
                icon_infos = build_image_from_simple_prompt(crafted_prompt, self, client, production_type="icon")
                
                icon_src = str(Path(icon_infos["path"]))
                shutil.copy(icon_src, icon_dst)
                self.step_end("Generating icon")

                # Stage and commit the icon
                self.step_start("Commiting to git")
                repo.index.add([os.path.relpath(icon_dst, app_path)])
                repo.index.commit("Add icon.png")
                self.step_end("Commiting to git")
            except:
                self.step_start("Using default icon")
                # Copy icon.png
                icon_src = str(Path(__file__).parent.parent/"assets"/"icon.png")
                icon_dst = str(app_path/"icon.png")
                shutil.copy(icon_src, icon_dst)
                self.step_end("Using default icon")
                
                # Stage and commit the icon
                self.step_start("Commiting to git")
                repo.index.add([os.path.relpath(icon_dst, app_path)])
                repo.index.commit("Add icon.png")        
                self.step_end("Commiting to git")

        else:
            self.step_start("Using default icon")
            # Copy icon.png
            icon_src = str(Path(__file__).parent.parent/"assets"/"icon.png")
            icon_dst = str(app_path/"icon.png")#+"\n<br>\n<p>Warning! We are using default icon beceaus icon generation is deactivated in settings.</p>"
            shutil.copy(icon_src, icon_dst)
            self.step_end("Using default icon")
            
            # Stage and commit the icon
            self.step_start("Commiting to git")
            repo.index.add([os.path.relpath(icon_dst, app_path)])
            repo.index.commit("Add icon.png")        
            self.step_end("Commiting to git")
        return icon_dst

    def create_git_repository(self, infos, metadata):
        self.step_start("Initializing Git repository")
        app_path = metadata["app_path"]
        if not (app_path / ".git").exists():
            repo = git.Repo.init(app_path)
        else:
            repo = git.Repo(app_path)


        # Create .gitignore file
        gitignore_content = """
        # Ignore common Python files
        __pycache__/
        *.py[cod]
        *$py.class

        # Ignore common development files
        .vscode/
        .idea/

        # Ignore OS generated files
        .DS_Store
        Thumbs.db

        # Ignore backup files
        index_v*.html
        """
        with open(Path(metadata["app_path"]) / ".gitignore", "w") as f:
            f.write(gitignore_content)

        # Create README.md file
        readme_content = f"""
        # {infos['name']}

        {infos['description']}

        ## Version
        {infos['version']}

        ## Author
        {infos['author']}

        ## Category
        {infos['category']}

        ## Disclaimer
        {infos.get('disclaimer', 'N/A')}

        ## How to use
        1. Open the `index.html` file in a web browser.
        2. Follow the on-screen instructions to use the application.

        ## Development
        This project was created using the Lollms Apps Maker. To make changes, edit the `index.html` file and commit your changes to the Git repository.
        """
        with open(Path(metadata["app_path"]) / "README.md", "w") as f:
            f.write(readme_content)

        # Add all files to Git
        repo.git.add(all=True)

        # Commit the initial code
        repo.index.commit("Initial commit")

        self.step_end("Initializing Git repository")

    
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
        # Load project
        metadata = client.discussion.get_metadata()
        if "app_path" in metadata and metadata["app_path"] and metadata["app_path"]!="":
            self.personality_config.project_path = metadata["app_path"]
            self.personality_config.save()
        if (not  "app_path" in metadata or not metadata["app_path"] or metadata["app_path"]=="") and self.personality_config.project_path!="":
            metadata["app_path"] = self.personality_config.project_path


        if self.personality_config.interactive_mode:
            extra_infos="""
The Lollms apps maker is a lollms personality built for making lollms specific apps.
Lollms apps are webapps with a possible fastapi backend. These webapps are created in html/css/javascript and can interact with lollms is the option is activated in the settings.
Multiple libraries can be activated in the settings of the personality to instruct the personality to use them.
The lollms libraries suite allows your app to interact with lollms and benefits from its generative capabilities (text to speach, text to image, text to music, text to code etc..)
The code contains description.yaml that describes the application, the author, the creation date and a short description.
"""+self.get_lollms_infos()
            self.answer(context_details, "Extra infos about the process:"+extra_infos)            
        else:
            self.step_start("Analyzing the query")
            out =  self.build_message_element_with_thinking_animation("Let me analyze your query")
            self.set_message_html(out)            
            options=[
                    "The context content is engaging in casual discussion about the webapp or a generic unrelated thought",
                    "asking to build a new webapp",
                    "asking for a modification that requires modifying both backend and frontend" if self.personality_config.build_a_backend else "empty place holder (never select this)",
                    "asking for a modification in the webapp backend or server.py file" if self.personality_config.build_a_backend else "empty place holder (never select this)",
                    "asking for modifications or feature additions to the existing webapp frontend (index.html)",
                    "requesting changes to the app's metadata or configuration file",
                    "asking for design or recreation of the app's icon or logo",
                    "requesting the creation or update of documentation for the app",
                    "asking to implement or modify the backend server functionality for the app"
            ]
            choice = self.multichoice_question("Based on the context content, select the most appropriate affirmation about the context given that you build and edit webapps.", options, prompt)
            if choice>=0 and choice<len(options):
                self.step(options[choice])
            self.step_end("Analyzing the query")
            if choice == 0:
                extra_infos="""
The Lollms apps maker is a lollms personality built for making lollms specific apps.
Lollms apps are webapps with a possible fastapi backend. These webapps are created in html/css/javascript and can interact with lollms is the option is activated in the settings.
Multiple libraries can be activated in the settings of the personality to instruct the personality to use them.
The lollms libraries suite allows your app to interact with lollms and benefits from its generative capabilities (text to speach, text to image, text to music, text to code etc..)
The code contains description.yaml that describes the application, the author, the creation date and a short description.
"""+self.get_lollms_infos()
                self.answer(context_details, "Extra infos about the process:"+extra_infos)            
            elif choice ==1:
                out +=  self.build_info_message("You asked me to build an app. I am building the description file.")
                self.set_message_html(out)

                # ----------------------------------------------------------------
                infos = self.buildDescription(context_details, metadata, client)
                if infos is None:
                    out = "\n<p style='color:red'>It looks like I failed to build the description.<br>That's the easiest part to do!! If the model wasn't able to do this simple task, I think you better change it, or maybe give it another shot.<br>As you know, I depend highly on the model I'm running on. Please give me a better brain and plug me to a good model.</p>"
                    self.set_message_html(out)
                    return
                with open(Path(metadata["app_path"])/"description.yaml","w", encoding="utf8") as f:
                    yaml.dump(infos, f, encoding="utf8")
                out = "\n".join([
                    "# Description :",
                    "Here is the metadata built for this app:",
                    "```yaml",
                    yaml.dump(infos, default_flow_style=False),
                    "```",
                    ""
                ])
                self.set_message_content(out)
                # ----------------------------------------------------------------
                self.new_message("")
                out = self.build_info_message("Building the application. Please wait as this may take a little while.")
                self.set_message_html(out)
                if self.personality_config.build_a_backend:
                    backend_code = self.build_server(context_details, infos, metadata, client)
                    if backend_code:
                        with open(Path(metadata["app_path"])/"server.py","w", encoding="utf8") as f:
                            f.write(backend_code)
                        out +=self.build_info_message("Back end coding done successfully.")
                        self.set_message_html(out)
                    else:
                        out += self.build_error_message("It looks like I failed to build the code. I think the model you are using is not smart enough to do the task. I remind you that the quality of my output depends highly on the model you are using. Give me a better brain if you want me to do better work.")
                        self.set_message_html(out)
                        return
                else:
                    backend_code = None
                code = self.build_index(context_details, infos, metadata, client)
                if code:
                    index_file_path = Path(metadata["app_path"])/"index.html"
                    app_path = metadata["app_path"]
                    with open(index_file_path,"w", encoding="utf8") as f:
                        f.write(code)
                    out +=self.build_info_message("Front end coding done successfully.")
                    if not (Path(app_path) / ".git").exists():
                        repo = git.Repo.init(app_path)
                    else:
                        repo = git.Repo(app_path)
                    repo.index.add([os.path.relpath(index_file_path, app_path)])
                    repo.index.commit(f"Updated index.html by {self.personality.model.model_name}, in answer to prompt: {prompt}")

                    self.set_message_html(out)
                else:
                    out +=self.build_error_message("It looks like I failed to build the code. I think the model you are using is not smart enough to do the task. I remind you that the quality of my output depends highly on the model you are using. Give me a better brain if you want me to do better work.")
                    self.set_message_html(out)
                    return

                # ----------------------------------------------------------------
                self.new_message("")
                if self.personality_config.generate_icon:
                    icon_dst = self.generate_icon(metadata, infos, client)
                    icon_url = app_path_to_url(icon_dst)
                    out += "\n" + f'\n<img src="{icon_url}" style="width: 200px; height: 200px;">'
                else:
                    out +="I'll use the default icon as you did not activate icon generation. You can build new icons whenever you want in the future, just ask me to make a new icon And I'll do (ofcourse, lollms needs to have its TTI active)."
                    icon_url = ""
                out += f"""<a href="/apps/{infos['name'].replace(' ','_')}/index.html">Click here to test the application</a>"""
                self.set_message_html(out)
                # Show the user everything that was created
                out = f"""
<div class="max-w-2xl mx-auto my-8 bg-white p-6 rounded-xl shadow-lg ring-1 ring-gray-100">
    <h2 class="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
        <span class="text-green-500 mr-2">✓</span> Application Created Successfully!
    </h2>
    
    <div class="flex items-center mb-6">
        <a href="/apps/{infos['name'].replace(' ','_')}/index.html" target="_blank" class="mr-4">
            <img src="{icon_url}" class="w-24 h-24 rounded-lg shadow-md object-cover">
        </a>
        <p class="text-gray-700">
            Your application 
            <a href="/apps/{infos['name'].replace(' ','_')}/index.html" target="_blank" 
               class="font-semibold text-blue-600 hover:underline">
                {infos['name']}
            </a> 
            has been created in:
        </p>
    </div>
    
    <pre class="bg-gray-50 text-gray-800 p-3 rounded-lg font-mono text-sm mb-6">{metadata['app_path']}</pre>
    
    <h3 class="text-xl font-semibold text-gray-800 mb-3">Files Created:</h3>
    <ul class="list-disc list-inside text-gray-700 mb-6 space-y-1">
        <li>description.yaml</li>
        <li>index.html</li>
        <li>icon.png</li>
        <li>.gitignore</li>
        <li>README.md</li>
    </ul>
    
    <h3 class="text-xl font-semibold text-gray-800 mb-3">Git Repository:</h3>
    <p class="text-gray-700 mb-6">A Git repository has been initialized with an initial commit.</p>
    
    <h3 class="text-xl font-semibold text-gray-800 mb-3">Next Steps:</h3>
    <ol class="list-decimal list-inside text-gray-700 space-y-2">
        <li>Refresh the apps zoo to find this app in category 
            <span class="font-medium text-blue-600">{infos['category']}</span>
        </li>
        <li>Review the created files and make any necessary adjustments.</li>
        <li>Test the application by opening index.html in a browser.</li>
        <li>Continue development by making changes and committing to Git.</li>
    </ol>
</div>
"""
                self.set_message_html(out)
                client.discussion.set_metadata(metadata)
            elif choice == 2:
                out = ""
                self.update_server(prompt, context_details, metadata, out)
                
                self.update_index(prompt, context_details, metadata, out)
            elif choice == 3:
                out = ""
                self.update_server(prompt, context_details, metadata, out)
            elif choice == 4:
                out = ""
                self.update_index(prompt, context_details, metadata, out)
            elif choice == 5:
                out = ""
                infos = self.updateDescription(context_details, metadata, client)
                if infos is None:
                    out += "\n<p style='color:red'>It looks like I failed to build the description. That's the easiest part to do. As you know, I depend highly on the model I'm running on. Please give me a better brain and plug me to a good model.</p>"
                    self.set_message_html(out)
                    return
                with open(Path(metadata["app_path"])/"description.yaml","w", encoding="utf8") as f:
                    yaml.dump(infos, f, encoding="utf8")
                out += "\n".join([
                    "\nDescription built successfully !",
                    "Here is the metadata built for this app:",
                    "```yaml",
                    yaml.dump(infos, default_flow_style=False),
                    "```",
                    ""
                ])
                self.set_message_html(out)

            elif choice ==6:
                out = self.build_message_element_with_thinking_animation("I'm generating a new icon based on your request.")
                self.set_message_html(out)
                out += self.generate_icon(metadata, metadata["infos"], client)
                self.set_message_html(out)
            elif choice ==7:
                out = self.build_message_element_with_thinking_animation("I'm generating a documentation for the app.")
                self.set_message_html(out)
                self.build_documentation(prompt, context_details, metadata, out)
            elif choice ==8:
                out = self.build_message_element_with_thinking_animation("I'm generating a server for the app.")
                self.set_message_html(out)
                self.update_server(prompt, context_details, metadata, out)
    
