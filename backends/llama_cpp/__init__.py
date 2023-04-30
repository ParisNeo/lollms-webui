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
from pyllamacpp.model import Model
from pyGpt4All.backend import GPTBackend

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
        
        self.model = Model(
                ggml_model=f"./models/llama_cpp/{self.config['model']}",
                prompt_context="", prompt_prefix="", prompt_suffix="", anti_prompts= [],
                n_ctx=self.config['ctx_size'], 
                seed=self.config['seed'],
                )

    def stop_generation(self):
        self.model._grab_text_callback()

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
            for tok in self.model.generate(prompt, 
                                           n_predict=n_predict,                                           
                                            temp=self.config['temp'],
                                            top_k=self.config['top_k'],
                                            top_p=self.config['top_p'],
                                            repeat_penalty=self.config['repeat_penalty'],
                                            repeat_last_n = self.config['repeat_last_n'],
                                            n_threads=self.config['n_threads'],
                                           ):
                if not new_text_callback(tok):
                    return
        except Exception as ex:
            print(ex)