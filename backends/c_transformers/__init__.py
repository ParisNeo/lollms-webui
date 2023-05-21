######
# Project       : GPT4ALL-UI
# File          : backend.py
# Author        : ParisNeo with the help of the community
# Underlying backend : Abdeladim's pygptj backend
# Supported by Nomic-AI
# license       : Apache 2.0
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
        elif 'llama' in self.config['model'] or 'wizardLM' in self.config['model']:
            model_type='llama'
        elif 'mpt' in self.config['model']:
            model_type='mpt'
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
        return self.model.detokenize(tokens_list)
    
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
            self.model.reset()
            tokens = self.model.tokenize(prompt)
            count = 0
            for tok in self.model.generate(
                                            tokens,
                                            top_k=self.config['top_k'],
                                            top_p=self.config['top_p'],
                                            temperature=self.config['temperature'],
                                            repetition_penalty=self.config['repeat_penalty'],
                                            seed=self.config['seed'],
                                            batch_size=1,
                                            threads = self.config['n_threads'],
                                            reset=True,
                                           ):
                

                if count >= n_predict or self.model.is_eos_token(tok):
                    break
                word = self.model.detokenize(tok)
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