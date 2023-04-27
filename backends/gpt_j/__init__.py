######
# Project       : GPT4ALL-UI
# File          : backend.py
# Author        : ParisNeo with the help of the community
# Supported by Nomic-AI
# Licence       : Apache 2.0
# Description   : 
# This is an interface class for GPT4All-ui backends.
######
from pathlib import Path
from typing import Callable
from gpt4allj import Model
from pyGpt4All.backend import GPTBackend

__author__ = "parisneo"
__github__ = "https://github.com/nomic-ai/gpt4all-ui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

backend_name = "GPT_J"


class GPT_J(GPTBackend):
    file_extension='*'
    def __init__(self, config:dict) -> None:
        """Builds a GPT-J backend

        Args:
            config (dict): The configuration file
        """
        super().__init__(config, True)
        self.config = config
        if "use_avx2" in self.config and not self.config["use_avx2"]:
            self.model = Model(
                    model=f"./models/gpt_j/{self.config['model']}", instructions='avx'
                    )
        else:
            self.model = Model(
                    model=f"./models/gpt_j/{self.config['model']}"
                    )
            
        
            
    def get_num_tokens(self, prompt):
        return self.model.num_tokens(prompt)

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
        num_tokens = self.get_num_tokens(prompt)
        print(f"Prompt has {num_tokens} tokens")
        try:
            self.model.generate(
                prompt,
                callback=new_text_callback,
                n_predict=num_tokens + n_predict,
                seed=self.config['seed'] if self.config['seed']>0 else -1,
                temp=self.config['temp'],
                top_k=self.config['top_k'],
                top_p=self.config['top_p'],
                # repeat_penalty=self.config['repeat_penalty'],
                # repeat_last_n = self.config['repeat_last_n'],
                n_threads=self.config['n_threads'],
                #verbose=verbose
            )
        except Exception as ex:
            print(ex)
        #new_text_callback()
