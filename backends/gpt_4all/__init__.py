######
# Project       : GPT4ALL-UI
# File          : backend.py
# Author        : ParisNeo with the help of the community
# Supported by Nomic-AI
# license       : Apache 2.0
# Description   : 
# This is an interface class for GPT4All-ui backends.


# This backend is a wrapper to gpt4all's official backend
# Follow him on his github project : https://github.com/nomic-ai/gpt4all

######
from pathlib import Path
from typing import Callable
from gpt4all import GPT4All
from gpt4all_api.backend import GPTBackend
import yaml

__author__ = "parisneo"
__github__ = "https://github.com/nomic-ai/gpt4all-ui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

backend_name = "GPT4ALL"

class GPT4ALL(GPTBackend):
    file_extension='*.bin'
    
    def __init__(self, config:dict) -> None:
        """Builds a GPT4ALL backend

        Args:
            config (dict): The configuration file
        """
        super().__init__(config, False)
        self.model = GPT4All.get_model_from_name(self.config['model'])
        self.model.load_model(
                model_path=f"./models/gpt_4all/{self.config['model']}"
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
            output = ""
            for tok in self.model.generate(prompt, 
                                           n_predict=n_predict,                                           
                                            temp=self.config['temperature'],
                                            top_k=self.config['top_k'],
                                            top_p=self.config['top_p'],
                                            repeat_penalty=self.config['repeat_penalty'],
                                            repeat_last_n = self.config['repeat_last_n'],
                                            # n_threads=self.config['n_threads'],
                                            streaming=True,
                                           ):
                output += tok
                if new_text_callback is not None:
                    if not new_text_callback(tok):
                        return output
        except Exception as ex:
            print(ex)
        return output

    @staticmethod
    def get_available_models():
        # Create the file path relative to the child class's directory
        backend_path = Path(__file__).parent
        file_path = backend_path/"models.yaml"

        with open(file_path, 'r') as file:
            yaml_data = yaml.safe_load(file)
        
        return yaml_data