from lollms.config import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate, InstallOption
from lollms.types import MSG_OPERATION_TYPE
from lollms.personality import APScript, AIPersonality
from lollms.prompting import LollmsContextDetails
import subprocess
from pathlib import Path
import urllib.request
import json
import time

from functools import partial
import sys
import yaml
import re
import random

from typing import Callable, Any


def find_matching_number(numbers, text):
    for index, number in enumerate(numbers):
        number_str = str(number)
        pattern = r"\b" + number_str + r"\b"  # Match the whole word
        match = re.search(pattern, text)
        if match:
            return number, index
    return None, None  # No matching number found
  
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
        personality_config_template = ConfigTemplate([
                {"name":"max_thought_size","type":"int","value":512, "min":10, "max":personality.model.config["ctx_size"]},
                {"name":"max_judgement_size","type":"int","value":512, "min":10, "max":personality.model.config["ctx_size"]},
                {"name":"max_summary_size","type":"int","value":512, "min":10, "max":personality.model.config["ctx_size"]},
                {"name":"nb_samples_per_idea","type":"int","value":3, "min":2, "max":100},
                {"name":"nb_ideas","type":"int","value":3, "min":2, "max":100},
                {"name":"idea_temperature","type":"float","value":0.8, "min":0, "max":2, "help":"The temperature of the idea generation controls the creativily level.\nA higher temperature yields more original ideas and more variety and lower temperatures yield more logical ideas."},
                {"name":"thinking_method","type":"str","value":"synthesize", "options":["synthesize","pick_best","develop"], "min":2, "max":100}
            ])
        personality_config = BaseConfig.from_template(personality_config_template)
        personality_config = TypedConfig(
            personality_config_template,
            personality_config
        )
        super().__init__(
                            personality,
                            personality_config,
                            callback=callback
                        )
        
    def install(self):
        super().install()
        requirements_file = self.personality.personality_package_path / "requirements.txt"
        # install requirements
        subprocess.run(["pip", "install", "--upgrade", "--no-cache-dir", "-r", str(requirements_file)])        
        ASCIIColors.success("Installed successfully")


    def process(self, text, message_type:MSG_OPERATION_TYPE):
        if text is None:
            return
        bot_says = self.bot_says + text
        ASCIIColors.success(f"generated:{len(bot_says)} words", end='\r')
        if self.personality.detect_antiprompt(bot_says):
            print("Detected hallucination")
            return False
        else:
            self.bot_says = bot_says
            return True
        
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
        self.bot_says = ""
        # 1 first ask the model to formulate a query
        final_ideas = []
        summary_prompt = ""
        prev_number = -1
        layers = []
        selections = []
        output = ""
        for j in range(self.personality_config.nb_ideas):
            print(f"============= Starting level {j+1} of the tree =====================")
            output += f"\n-- level {j+1} ---\n"
            self.set_message_content(output)
            self.step_start(f"Processing Level {j+1} of the tree")
            local_ideas=[]
            judgement_prompt = f"{self.config.start_header_id_template}prompt: {prompt}\n"
            for i in range(self.personality_config.nb_samples_per_idea):
                self.step_start(f"Generating idea number {j+1}:{i+1}/{self.personality_config.nb_samples_per_idea}")
                print(f"\nIdea {i+1}")
                if len(final_ideas)>0:
                    final_ideas_text = "\n".join([f'Idea {n}:{i}' for n,i in enumerate(final_ideas)])
                    idea_prompt = f"""{self.config.start_header_id_template}instructions: Given the following discussion and previous ideas, try to give another idea to solve the proposed problem. 
{self.config.start_header_id_template}discussion:
{previous_discussion_text}
{self.config.start_header_id_template}previous ideas: {final_ideas_text}
{self.config.start_header_id_template}idea:"""
                else:
                    idea_prompt = f"""{self.config.start_header_id_template}instructions: Given the following discussion, try to give an original idea to solve the proposed problem. 
{self.config.start_header_id_template}discussion:
{previous_discussion_text}
{self.config.start_header_id_template}idea:"""
                idea = self.generate(idea_prompt,self.personality_config.max_thought_size,temperature=self.personality_config.idea_temperature)
                output += f"\n## Idea {i+1}:\n {idea}\n"
                self.set_message_content(output)
                local_ideas.append(idea.strip())
                judgement_prompt += f"{self.config.separator_template}{self.config.start_header_id_template}Idea {i}:{idea}\n"
                self.step_end(f"Generating idea number {j+1}:{i+1}/{self.personality_config.nb_samples_per_idea}")

            idea_id = self.multichoice_question(f"What is the most adequate idea to the context?\n",[f"{i} - {local_idea}" for local_idea in local_ideas],previous_discussion_text)
            if idea_id>=0 and idea_id<len(local_ideas):
                print(f"Chosen thought n:{idea_id}")
                final_ideas.append(local_ideas[idea_id])
            else:
                self.warning("Warning, the model made a wrong answer, taking random idea as the best")
                idea_id = random.randint(0,self.personality_config["nb_samples_per_idea"])
                print(f"Chosen thought n:{idea_id+1}")
                if idea_id>=0 and idea_id<len(local_ideas):
                    final_ideas.append(local_ideas[idea_id]) 
                else:
                    final_ideas.append(local_ideas[0]) 
            output += f"\n<b>Best level idea:</b>\n{local_ideas[idea_id]}\n"
            self.set_message_content(output)
            layers.append(local_ideas)
            selections.append(idea_id)
            
            self.step_end(f"Processing Level {j+1} of the tree")

        self.step_start(f"Building final summary")
        if self.personality_config.thinking_method=="synthesize":
            summary_prompt += f"{self.config.start_header_id_template}Instructions: Combine these ideas in a comprihensive essai. Give a detailed explanation.\n"
            for idea in final_ideas:
                summary_prompt += f">Idea: {idea}\n"
            summary_prompt += f"{self.config.start_header_id_template}Previous context:\n{previous_discussion_text}\n"
            summary_prompt += f"{self.config.start_header_id_template}Synthesis:"
        if self.personality_config.thinking_method=="pick_best":
            summary_prompt += f"{self.config.start_header_id_template}Instructions: Pick the best idea out of the proposed ones and rewrite it in a comprehensive paragraph. Give a detailed explanation.\nDo not mention its number, just its full description"
            for idea in final_ideas:
                summary_prompt += f">Idea: {idea}\n"
            summary_prompt += f"{self.config.start_header_id_template}Previous context:\n{previous_discussion_text}\n"
            summary_prompt += f"{self.config.start_header_id_template}Best idea :"
        if self.personality_config.thinking_method=="develop":
            summary_prompt += f"{self.config.start_header_id_template}Instructions: Out of the above ideas, write an essai inspired from the ideas in order to answer the user request.\n"
            for idea in final_ideas:
                summary_prompt += f">Idea: {idea}\n"
            summary_prompt += f"{self.config.start_header_id_template}Previous context:\n{previous_discussion_text}\n"
            summary_prompt += f"{self.config.start_header_id_template}Essai:"

        final_summary = self.fast_gen(summary_prompt)

        ASCIIColors.success("Summary built successfully")
        self.step_end(f"Building final summary")
        output += f"## Final summary:\n{final_summary}"
        self.set_message_content(output)
        
        
        tree_full_output = {
            "tree_layers": layers,
            "selections":selections,
            "summary":final_summary
        }
        
        self.json("infos", tree_full_output)

        return final_summary


