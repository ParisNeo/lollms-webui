######
# Project       : GPT4ALL-UI
# File          : backend.py
# Author        : ParisNeo with the help of the community
# Supported by Nomic-AI
# license       : Apache 2.0
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
            
        if not "n_gpu_layers" in self.config:
            self.config["n_gpu_layers"] = 20
        self.model = Llama(model_path=f"./models/llama_cpp_official/{self.config['model']}", n_ctx=self.config["ctx_size"], n_gpu_layers=self.config["n_gpu_layers"], seed=seed)


    def tokenize(self, prompt):
        """
        Tokenizes the given prompt using the model's tokenizer.

        Args:
            prompt (str): The input prompt to be tokenized.

        Returns:
            list: A list of tokens representing the tokenized prompt.
        """
        return self.model.tokenize(prompt.encode())

    def detokenize(self, tokens_list):
        """
        Detokenizes the given list of tokens using the model's tokenizer.

        Args:
            tokens_list (list): A list of tokens to be detokenized.

        Returns:
            str: The detokenized text as a string.
        """
        return self.model.detokenize(tokens_list).decode()

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
                if new_text_callback is not None:
                    if not new_text_callback(word):
                        break
                output += word
                count += 1
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
    

