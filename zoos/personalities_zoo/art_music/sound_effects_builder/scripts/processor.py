import subprocess
from pathlib import Path
from lollms.helpers import ASCIIColors, trace_exception
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate, InstallOption
from lollms.types import MSG_OPERATION_TYPE
from typing import Any
from lollms.personality import APScript, AIPersonality
from lollms.utilities import PromptReshaper, git_pull, File_Path_Generator
from lollms.client_session import Client
import pipmaster as pm
from lollms.prompting import LollmsContextDetails

if not pm.is_installed("torch"):
    ASCIIColors.yellow("Diffusers: Torch not found. Installing it")
    pm.install_multiple(["torch","torchvision","torchaudio"], "https://download.pytorch.org/whl/cu121", force_reinstall=True)

import torch
if not torch.cuda.is_available():
    ASCIIColors.yellow("Diffusers: Torch not using cuda. Reinstalling it")
    pm.install_multiple(["torch","torchvision","torchaudio"], "https://download.pytorch.org/whl/cu121", force_reinstall=True)

import torchaudio

from typing import Callable, Any
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
        
        self.callback = None
        self.music_model = None
        self.previous_mg_prompt = None

        personality_config_template = ConfigTemplate(
            [
                {"name":"device","type":"str","value":"cuda:0","options":["cuda","cpu","xpu","ipu","hpu","xla","Vulkan"],"help":"Select the model to be used to generate the music. Bigger models provide higher quality but consumes more computing power"},
                {"name":"model_name","type":"str","value":"facebook/audiogen-medium","options":["facebook/audiogen-small","facebook/audiogen-medium","facebook/audiogen-large"],"help":"Select the model to be used to generate the music. Bigger models provide higher quality but consumes more computing power"},
                {"name":"number_of_samples","type":"int","value":1,"help":"The number of samples to generate"},
                {"name":"imagine","type":"bool","value":True,"help":"Imagine the images"},
                {"name":"generate","type":"bool","value":True,"help":"Paint the images"},
                {"name":"show_infos","type":"bool","value":True,"help":"Shows generation informations"},
                {"name":"continuous_discussion","type":"bool","value":True,"help":"If true then previous prompts and infos are taken into acount to generate the next image"},
                {"name":"add_style","type":"bool","value":True,"help":"If true then musicbot will choose and add a specific style to the prompt"},
                
                {"name":"activate_discussion_mode","type":"bool","value":True,"help":"If active, the AI will not generate an image until you ask it to, it will just talk to you until you ask it to make an musicwork"},
                
                {"name":"duration","type":"int","value":8, "min":1, "max":2048},

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
                                        "new_music":self.new_music,
                                        "regenerate":self.regenerate
                                    },
                                    "default": self.main_process
                                },                           
                            ],
                            callback=callback
                        )


    def install(self):
        super().install()
        
        requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Install dependencies using pip from requirements.txt
        subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])      
        try:
            import torchaudio
            ASCIIColors.success("Torch audio OK")
        except:
            ASCIIColors.warning("No torch audio found")
        # Clone repository
        self.prepare()
        ASCIIColors.success("Installed successfully")


    def prepare(self):
        if self.music_model is None:
            from audiocraft.models import audiogen
            import torch
            self.step_start("Loading Meta's musicgen")
            self.music_model = audiogen.AudioGen.get_pretrained(self.personality_config.model_name, device=self.personality_config.device)
            self.step_end("Loading Meta's musicgen")
        

    def help(self, prompt, full_context):
        self.set_message_content(self.personality.help)
    
    def new_music(self, prompt, full_context):
        self.image_files=[]
        self.set_message_content("Starting fresh :)")
        

    def regenerate(self, prompt, full_context):
        if self.previous_mg_prompt:
            self.music_model.set_generation_params(duration=self.personality_config.duration)
            res = self.music_model.generate([prompt], progress=True)
            if self.personality_config.show_infos:
                self.new_message("infos", MSG_OPERATION_TYPE.MSG_TYPE_JSON_INFOS,{"prompt":prompt,"duration":self.personality_config.duration})
        else:
            self.set_message_content("Please generate an image first then retry")

    

    def get_styles(self, prompt, full_context):
        self.step_start("Selecting style")
        styles=[
            "hard rock",
            "pop",
            "hiphop",
            "riggay",
            "techno",
            "classic",
            "epic",
            "fantasy"
        ]
        stl=", ".join(styles)
        prompt= self.build_prompt([
            self.user_full_header,
            f"Select what style(s) among those is more suitable for this musicwork: {stl}",
            "explain your reasoning then put your answer inside a markdown code tag",
            self.ai_full_header
            ])
        stl = self.generate(prompt, self.personality_config.max_generation_prompt_size, callback=self.sink).strip().replace("</s>","").replace("<s>","")
        stl = self.extract_code_blocks(stl)
        if len(stl)>0:
            stl=stl[0]["content"]
        else:
            stl = styles[0]
        self.step_end("Selecting style")

        selected_style = ",".join([s for s in styles if s.lower() in stl])
        return selected_style


    def main_process(self, initial_prompt, full_context, callback, context_state, client):    
        self.prepare()
        full_context = full_context[:full_context.index(initial_prompt)]
        
        if self.personality_config.imagine:
            if self.personality_config.activate_discussion_mode:
                if not self.yes_no("Is the user's message asking to generate a music sequence?",full_context+initial_prompt):
                    current_prompt = self.build_prompt([
                        self.system_full_header + "Lord of Music is a music geneation IA that discusses about making music with the user.",
                        self.system_custom_header("discussion"),
                        full_context,
                        initial_prompt,
                        self.ai_full_header
                    ],2)
                    ASCIIColors.yellow(current_prompt)

                    response = self.generate(current_prompt, self.personality_config.max_generation_prompt_size,callback=self.sink).strip().replace("</s>","").replace("<s>","")
                    self.set_message_content(response)
                    return


      
            # ====================================================================================
            if self.personality_config.add_style:
                styles = self.get_styles(initial_prompt,full_context)
            else:
                styles = "No specific style selected."
            self.set_message_content(f"### Chosen style:\n{styles}")         

            self.step_start("Imagining prompt")
            # 1 first ask the model to formulate a query
            current_prompt = self.build_prompt([
                self.system_full_header + context_state["conditionning"],
                self.system_custom_header("discussion"),
                full_context,
                initial_prompt,
                """
Make a prompt based on the discussion with the user presented below to generate some music in the right style.
Make sure you mention every thing asked by the user's idea.
Do not make a very long text.
Do not use bullet points.
The prompt should be in english.
The generation ai has no access to the previous text so do not do references and just write the prompt.""",
            self.ai_full_header
            ],2)
            ASCIIColors.yellow(current_prompt)
            generation_prompt = self.generate(current_prompt, self.personality_config.max_generation_prompt_size, callback=self.sink).strip().replace("</s>","").replace("<s>","")
            self.step_end("Imagining prompt")
            self.set_message_content(f"### Chosen style:\n{styles}\n### Prompt:\n{generation_prompt}")         
            # ====================================================================================
            self.set_message_content(f"### Chosen style:\n{styles}\n### Prompt:\n{generation_prompt}")         
            # ====================================================================================            
            
        else:
            generation_prompt = initial_prompt
            
        self.previous_mg_prompt = generation_prompt

        self.step_start("Making some music")
        output = f"### Prompt :\n{generation_prompt}"
        self.music_model.set_generation_params(duration=self.personality_config.duration)
        import torch
        torch.cuda.empty_cache()
        for sample in range(self.personality_config.number_of_samples):
            res = self.music_model.generate([generation_prompt])
            output_folder = self.personality.lollms_paths.personal_outputs_path / "lom"
            output_folder.mkdir(parents=True, exist_ok=True)
            output_file = File_Path_Generator.generate_unique_file_path(output_folder, "generation","wav")
            torchaudio.save(output_file, res.reshape(1, -1).cpu(), 32000)
            url = "/outputs"+str(output_file).split("outputs")[1].replace("\\","/")
            output += f"""
<audio controls>
    <source src="{url}" type="audio/wav">
    Your browser does not support the audio element.
</audio>
"""
            self.set_message_content(output.strip())
        self.step_end("Making some music")

        ASCIIColors.success("Generation succeeded")


        
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
        self.process_state(prompt, previous_discussion_text, callback, context_details, client)

        return ""

