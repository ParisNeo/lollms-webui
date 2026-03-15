"""
project: lollms
personality: # Place holder: Personality name 
Author: # Place holder: creator name 
description: # Place holder: personality description
"""
from lollms.types import MSG_OPERATION_TYPE
from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality
from lollms.prompting import LollmsContextDetails
import subprocess
import json
from typing import Callable, Any

# Helper functions
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
        
        self.callback = None
        # Example entries
        #       {"name":"make_scripted","type":"bool","value":False, "help":"Makes a scriptred AI that can perform operations using python script"},
        #       {"name":"make_scripted","type":"bool","value":False, "help":"Makes a scriptred AI that can perform operations using python script"},
        # Supported types:
        # str, int, float, bool, list
        # options can be added using : "options":["option1","option2"...]        
        personality_config_template = ConfigTemplate(
            [
                {"name":"agents_system_message","type":"text","value":"Try to answer the user request by providing useful thoughts. If there are other model's thoughts try to enhance them, add new ideas and correct any false or misleading ideas", "help":"System message to use for agents."},
                {"name":"master_system_message","type":"text","value":"Build a comprehensive answer to the user. Format it as a markdown text and hilight important information.", "help":"System message to use for all questions"},
                {"name":"models_to_use","type":"str","value":"", "help":"List of coma separated models to test in format binding_name::model_name"},
                {"name":"master_model","type":"str","value":"", "help":"A single powerful model in format binding_name::model_name which is going to judge the other models based on the human test file. This model will just compare the output of the model and the human provided answer."},
                {"name":"n_rounds","type":"int","value":3,"help":"The number of rounds in the mixture of agents process. A round is a full pass through all agents."}                
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
                                    "commands": { # list of commands (don't forget to add these to your config.yaml file)
                                        "help":self.help,
                                    },
                                    "default": None
                                },                           
                            ],
                            callback=callback
                        )
        
    def install(self):
        super().install()
        
        # requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Install dependencies using pip from requirements.txt
        # subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])      
        ASCIIColors.success("Installed successfully")        

    def help(self, prompt="", full_context=""):
        self.set_message_content(self.personality.help)

    def is_ok(self, prompt, true_answer, models_list):
        for model_to_test in models_list:
            model_answer = [f'answer_{model_to_test["binding"]}_{model_to_test["model"]}']
            return self.yes_no("Are these two answers similar?",f"prompt:\n{prompt}\nanswer 1:\n{true_answer}\nanswer 2:\n{model_answer}")
        
    def add_file(self, path, client, callback=None):
        """
        Here we implement the file reception handling
        """
        super().add_file(path, client, callback)

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
        self.personality.info("Generating")
        self.callback = callback
        models_to_use = self.personality_config.models_to_use
        model_outputs = []
        
        context_details.conditionning="As a sophisticated AI, aim to break down complex user requests into sub-questions. Utilize multiple expert perspectives to generate intermediate thoughts, assessing their relevance and logical flow. Enhance other model's ideas by providing explanatory details, correcting any false or misleading information, and adding new insights. Synthesize key findings into a coherent final answer written at the doctoral level by an experienced tech writer."
        rounds = []
        for round in range(self.personality_config.n_rounds):
            self.step_start(f"Processing round {round+1}")
            formatted_models_outputs = ""
            if len(model_outputs)>0:
                formatted_models_outputs=self.system_custom_header("Previous models outputs")
                for output in model_outputs:
                    formatted_models_outputs += self.ai_custom_header(f"{output['model_name']} response")+output['text']
                formatted_models_outputs += self.system_full_header+ f"Based on the models response enhance the answer in a single response."
            prompt = self.build_prompt_from_context_details(context_details, formatted_models_outputs)
            if self.config.debug:
                self.print_prompt("Intermediate prompt",prompt)
            model_outputs = []
            for model_infos in models_to_use.split(","):
                self.step_start(f"using model {model_infos}")
                binding_name, model_name = model_infos.split("::")
                self.select_model(binding_name, model_name)
                out = self.fast_gen(prompt, callback=self.sink)
                model_outputs.append({"model_name":model_name, "text":out})
                self.step_end(f"using model {model_infos}")
            self.step_end(f"Processing round {round+1}")
            rounds.append(model_outputs)
        context_details.conditionning="Act as a sophisticated AI, breaking down complex user inquiries into sub-questions. Leverage multiple expert perspectives to generate intermediate thoughts, evaluating their relevance and logical flow. Construct a chain of reasoning by stitching together the strongest thoughts while providing explanatory details. Synthesize key insights into a comprehensive final answer written in markdown format with important information highlighted as if authored by an experienced tech writer at the doctoral level."
        #Now move to master model
        binding_name, model_name = self.personality_config.master_model.split("::")
        self.select_model(binding_name, model_name)
        formatted_models_outputs=""
        for output in model_outputs:
            formatted_models_outputs += self.ai_custom_header(f"{output['model_name']} response")+output['text']
        prompt = self.build_prompt_from_context_details(context_details, formatted_models_outputs)
        if self.config.debug:
            self.print_prompt("Final prompt",prompt)
        out = self.fast_gen(prompt, callback=self.sink)
        self.set_message_content("## Final answer:\n"+out)
        self.json("Rounds",rounds)
        model_outputs.append(out)

        return out

