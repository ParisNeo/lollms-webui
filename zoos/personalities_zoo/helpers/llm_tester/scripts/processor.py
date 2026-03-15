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
                {"name":"system_message","type":"text","value":"Act as a helpful AI.", "help":"System message to use for all questions"},
                {"name":"test_file_path","type":"str","value":"", "help":"Path tp the test file to use"},
                {"name":"output_file_path","type":"str","value":"", "help":"Path tp the output file to create"},
                {"name":"models_to_test","type":"str","value":"open_ai::gpt-4o,open_ai::gpt-4-turbo-preview", "help":"List of coma separated models to test in format binding_name::model_name"},
                {"name":"master_model","type":"str","value":"open_ai::gpt-4o", "help":"A single powerful model in format binding_name::model_name which is going to judge the other models based on the human test file. This model will just compare the output of the model and the human provided answer."},
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
                                        "start_testing":self.start_testing
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
    
    def start_testing(self, prompt="", full_context="", client=None):
        self.new_message("")
        msg =[]
        if self.personality_config.test_file_path=="":
            msg.append("Please set the test file path to be used in my settings first then try again. I need that file to test the AIs")
        if self.personality_config.models_to_test=="":
            msg.append("Please set the list of models to be tested first (in form binding_name::model_name) It is case sensitive so be careful.")
        self.set_message_content("\n".join(msg))
        if len(msg)>0:
            return
        model_parts = self.personality_config.master_model.split('::')
        if len(model_parts)==2:
            master_model={
                            "binding":model_parts[0].strip(),
                            "model": model_parts[1].strip()
                        }
        else:
            self.personality.app.error("The master model Name is wrong. Please make sure it has the format : binding_name::model_name")
            self.new_message("<b>The master model Name is wrong. Please make sure it has the format : binding_name::model_name</b>")
            return
        raw_models_list = self.personality_config.models_to_test.split(",")
        models_list = [{"binding": entry.split('::')[0].strip(), "model": entry.split('::')[1].strip()} for entry in raw_models_list]
        with open(self.personality_config.test_file_path,"r",encoding="utf-8", errors="ignore") as f:
            prompts = json.load(f)

        previous_binding = self.personality.config["binding_name"]
        previous_model = self.personality.config["model_name"]
        for model in models_list:
            self.step_start(f'Started testing model {model["binding"]}::{model["model"]}')
            self.select_model(model["binding"], model["model"])
            nb_prompts = len(prompts)
            for prompt_id, prompt in enumerate(prompts):
                self.step_start(f'Testing prompt {prompt_id+1}/{nb_prompts} for model {model["model"]}')
                reworked_prompt = f"{self.system_full_header}{self.ai_custom_header('assistant')}Hi I am assistant and I am here to help you.{self.ai_custom_header('prompt')}{prompt['prompt']}{self.config.separator_template}{self.ai_custom_header('assistant')}"
                answer = self.fast_gen(reworked_prompt, callback=self.sink)
                prompt[f'answer_{model["binding"]}_{model["model"]}']={
                    "answer":answer,
                    "val":0
                }
                self.step_end(f'Testing prompt {prompt_id+1}/{nb_prompts} for model {model["model"]}')
            self.step_end(f'Started testing model {model["binding"]}::{model["model"]}')

        self.step_start(f'Loading master model {master_model["binding"]}::{master_model["model"]}')
        self.select_model(master_model["binding"], master_model["model"])
        self.step_end(f'Loading master model {master_model["binding"]}::{master_model["model"]}')
        self.step_start(f'Judging models')
        for prompt_entry in prompts:
            prompt = prompt_entry["prompt"]
            true_answers=prompt_entry["answers"]
            for model_to_test in models_list:
                for true_answer in true_answers:
                    model_infos = prompt_entry[f'answer_{model_to_test["binding"]}_{model_to_test["model"]}']
                    model_answer = model_infos["answer"]
                    if self.yes_no("Is the second answer giving the same information as the first one?",f"prompt:\n{prompt}\nanswer 1:\n{true_answer['text']}\nanswer 2:\n{model_answer}"):
                        model_infos["val"]=true_answer['value']
                        break
        self.step_end(f'Judging models')

        self.step(f'Back to model {model["binding"]}::{model["model"]}')
        self.select_model(previous_binding, previous_model)
        self.step_start(f'Giving a mark for each AI')
        results={
            "prompts":prompts,
            "results":{}
        }
        for model in models_list:
            results["results"][f'answer_{model["binding"]}_{model["model"]}'] = 0
            for prompt in prompts:
                results["results"][f'answer_{model["binding"]}_{model["model"]}'] += prompt[f'answer_{model["binding"]}_{model["model"]}']["val"]
            results["results"][f'answer_{model["binding"]}_{model["model"]}'] /= len(prompts)
            results["results"][f'answer_{model["binding"]}_{model["model"]}'] *= 100

        self.step_end(f'Giving a mark for each AI')

        self.step_start(f'Saving test results')
        with open(self.personality_config.output_file_path,"w",encoding="utf-8", errors="ignore") as f:
            json.dump(results, f, indent=4)
        
        self.step_end(f'Saving test results')
        self.set_message_content("Done testing.\nFinal results:\n"+"\n".join([f"{k}: {v}% correct answers." for k,v in results["results"].items()])+f"\nThe details can be found in the generated file on your pc at {self.personality_config.output_file_path}")
    
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
        out = self.fast_gen(previous_discussion_text)
        self.set_message_content(out)
        return out

