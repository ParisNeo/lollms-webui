######
# Project       : GPT4ALL-UI
# File          : backend.py
# Author        : ParisNeo with the help of the community
# Underlying backend : Abdeladim's pygptj backend
# Supported by Nomic-AI
# license       : Apache 2.0
# Description   : 
# This is an interface class for GPT4All-ui backends.

# This backend is a wrapper to abdeladim's backend
# Follow him on his github project : https://github.com/abdeladim-s/pygptj

######
from pathlib import Path
from typing import Callable
from pygptj.model import Model
from gpt4all_api.backend import GPTBackend

__author__ = "parisneo"
__github__ = "https://github.com/nomic-ai/gpt4all-ui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

backend_name = "GptJ"

class GptJ(GPTBackend):
    file_extension='*.bin'
    def __init__(self, config:dict) -> None:
        """Builds a LLAMACPP backend

        Args:
            config (dict): The configuration file
        """
        super().__init__(config, False)
        
        self.model = Model(
                model_path=f"./models/gpt_j/{self.config['model']}",
                prompt_context="", prompt_prefix="", prompt_suffix=""
                )
    def tokenize(self, prompt):
        """
        Tokenizes the given prompt using the model's tokenizer.

        Args:
            prompt (str): The input prompt to be tokenized.

        Returns:
            list: A list of tokens representing the tokenized prompt.
        """
        return None

    def detokenize(self, tokens_list):
        """
        Detokenizes the given list of tokens using the model's tokenizer.

        Args:
            tokens_list (list): A list of tokens to be detokenized.

        Returns:
            str: The detokenized text as a string.
        """
        return None
    def generate(self, 
                 prompt:str,                  
                 n_predict: int = 128,
                 new_text_callback: Callable[[str], None] = bool,
                 verbose: bool = False,
                 **gpt_params ):
        """Generates text out of a prompt

        Args:
            prompt (str): The prompt to use for generation
            n_predict (int, optional): Number of tokens to prodict. Defaults to 128.
            new_text_callback (Callable[[str], None], optional): A callback function that is called everytime a new text element is generated. Defaults to None.
            verbose (bool, optional): If true, the code will spit many informations about the generation process. Defaults to False.
        """
        try:
            self.model.reset()
            output = ""
            for tok in self.model.generate(prompt, 
                                           n_predict=n_predict,                                           
                                            temp=self.config['temperature'],
                                            top_k=self.config['top_k'],
                                            top_p=self.config['top_p'],
                                            #repeat_penalty=self.config['repeat_penalty'],
                                            #repeat_last_n = self.config['repeat_last_n'],
                                            n_threads=self.config['n_threads'],
                                           ):
                output += tok
                if new_text_callback is not None:
                    if not new_text_callback(tok):
                        return output
        except Exception as ex:
            print(ex)
        return output