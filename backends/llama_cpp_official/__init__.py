######
# Project       : GPT4ALL-UI
# File          : backend.py
# Author        : ParisNeo with the help of the community
# Supported by Nomic-AI
# Licence       : Apache 2.0
# Description   : 
# This is an interface class for GPT4All-ui backends.

# This backend is a wrapper to the official llamacpp python bindings
# Follow him on his github project : https://github.com/abetlen/llama-cpp-python

######
from pathlib import Path
from typing import Callable
from llama_cpp import Llama
from gpt4all_api.backend import GPTBackend
import yaml
import random

__author__ = "parisneo"
__github__ = "https://github.com/nomic-ai/gpt4all-ui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

backend_name = "LLAMACPP"

class LLAMACPP(GPTBackend):
    file_extension='*.bin'
    def __init__(self, config:dict) -> None:
        """Builds a LLAMACPP backend

        Args:
            config (dict): The configuration file
        """
        super().__init__(config, False)
        seed = config["seed"]
        if seed <=0:
            seed = random.randint(1, 2**31)
            
        self.model = Llama(model_path=f"./models/llama_cpp_official/{self.config['model']}", n_gpu_layers=40, seed=seed)

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
            tokens = self.model.tokenize(prompt.encode())
            count = 0
            for tok in self.model.generate(tokens, 
                                            temp=self.config['temperature'],
                                            top_k=self.config['top_k'],
                                            top_p=self.config['top_p'],
                                            repeat_penalty=self.config['repeat_penalty'],
                                           ):
                if count >= n_predict or (tok == self.model.token_eos()):
                    break
                word = self.model.detokenize([tok]).decode()
                if not new_text_callback(word):
                    return
                count += 1
        except Exception as ex:
            print(ex)
            
    @staticmethod
    def get_available_models():
        # Create the file path relative to the child class's directory
        backend_path = Path(__file__).parent
        file_path = backend_path/"models.yaml"

        with open(file_path, 'r') as file:
            yaml_data = yaml.safe_load(file)
        
        return yaml_data