######
# Project       : GPT4ALL-UI
# File          : backend.py
# Author        : ParisNeo with the help of the community
# Underlying backend : Abdeladim's pygptj backend
# Supported by Nomic-AI
# Licence       : Apache 2.0
# Description   : 
# This is an interface class for GPT4All-ui backends.
######
from pathlib import Path
from typing import Callable
from gpt4allj import Model
from gpt4all_api.backend import GPTBackend
import yaml

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
        
        self.model = Model(
                model=f"./models/llama_cpp/{self.config['model']}", avx2 = self.config["use_avx2"]
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
            for tok in self.model.generate(
                                            prompt, 
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
                if not new_text_callback(tok):
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