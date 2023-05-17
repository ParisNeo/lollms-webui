######
# Project       : GPT4ALL-UI
# File          : backend.py
# Author        : ParisNeo with the help of the community
# Underlying backend : Abdeladim's pygptj backend
# Supported by Nomic-AI
# Licence       : Apache 2.0
# Description   : 
# This is an interface class for GPT4All-ui backends.

# This backend is a wrapper to marella's backend
# Follow him on his github project : https://github.com/marella/ctransformers

######
from pathlib import Path
from typing import Callable
from gpt4all_api.backend import GPTBackend
import yaml
from ctransformers import AutoModelForCausalLM

__author__ = "parisneo"
__github__ = "https://github.com/nomic-ai/gpt4all-ui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

backend_name = "GPTJ"

class GPTJ(GPTBackend):
    file_extension='*.bin'
    def __init__(self, config:dict) -> None:
        """Builds a LLAMACPP backend

        Args:
            config (dict): The configuration file
        """
        super().__init__(config, False)
        if 'gpt2' in self.config['model']:
            model_type='gpt2'
        elif 'gptj' in self.config['model']:
            model_type='gptj'
        elif 'gpt_neox' in self.config['model']:
            model_type='gpt_neox'
        elif 'dolly-v2' in self.config['model']:
            model_type='dolly-v2'
        elif 'starcoder' in self.config['model']:
            model_type='starcoder'
        else:
            print("The model you are using is not supported by this backend")
            return
        
        
        if self.config["use_avx2"]:
            self.model = AutoModelForCausalLM.from_pretrained(
                    f"./models/c_transformers/{self.config['model']}", model_type=model_type
                    )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                    f"./models/c_transformers/{self.config['model']}", model_type=model_type, lib = "avx"
                    )

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
            for tok in self.model.generate(
                                            tokens, 
                                            seed=self.config['seed'],
                                            n_threads=self.config['n_threads'],
                                            n_predict=n_predict,
                                            top_k=self.config['top_k'],
                                            top_p=self.config['top_p'],
                                            temp=self.config['temperature'],
                                            repeat_penalty=self.config['repeat_penalty'],
                                            repeat_last_n=self.config['repeat_last_n'],
                                            n_batch=8,
                                            reset=True,
                                           ):
                if not new_text_callback(self.model.detokenize(tok)):
                    return
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