######
# Project       : GPT4ALL-UI
# File          : backend.py
# Author        : ParisNeo with the help of the community
# Supported by Nomic-AI
# license       : Apache 2.0
# Description   : 
# This is an interface class for GPT4All-ui backends.
######
from pathlib import Path
from typing import Callable
import inspect
import yaml
import sys

__author__ = "parisneo"
__github__ = "https://github.com/nomic-ai/gpt4all-ui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"


class GPTBackend:
    file_extension='*.bin'
    backend_path = Path(__file__).parent
    def __init__(self, config:dict, inline:bool) -> None:
        self.config = config
        self.inline = inline


    def generate(self, 
                 prompt:str,                  
                 n_predict: int = 128,
                 new_text_callback: Callable[[str], None] = None,
                 verbose: bool = False,
                 **gpt_params ):
        """Generates text out of a prompt
        This should ber implemented by child class

        Args:
            prompt (str): The prompt to use for generation
            n_predict (int, optional): Number of tokens to prodict. Defaults to 128.
            new_text_callback (Callable[[str], None], optional): A callback function that is called everytime a new text element is generated. Defaults to None.
            verbose (bool, optional): If true, the code will spit many informations about the generation process. Defaults to False.
        """
        pass
    def tokenize(self, prompt):
        """
        Tokenizes the given prompt using the model's tokenizer.

        Args:
            prompt (str): The input prompt to be tokenized.

        Returns:
            list: A list of tokens representing the tokenized prompt.
        """
        pass

    def detokenize(self, tokens_list):
        """
        Detokenizes the given list of tokens using the model's tokenizer.

        Args:
            tokens_list (list): A list of tokens to be detokenized.

        Returns:
            str: The detokenized text as a string.
        """
        pass

    @staticmethod
    def list_models(config:dict):
        """Lists the models for this backend
        """
        models_dir = Path('./models')/config["backend"]  # replace with the actual path to the models folder
        return [f.name for f in models_dir.glob(GPTBackend.file_extension)]
    @staticmethod
    def get_available_models():
        # Create the file path relative to the child class's directory
        backend_path = Path(__file__).parent
        file_path = backend_path/"models.yaml"

        with open(file_path, 'r') as file:
            yaml_data = yaml.safe_load(file)
        
        return yaml_data

