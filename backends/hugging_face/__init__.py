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
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from pyGpt4All.backend import GPTBackend
import torch
import time
__author__ = "parisneo"
__github__ = "https://github.com/nomic-ai/gpt4all-ui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

backend_name = "HuggingFace"


class HuggingFace(GPTBackend):
    file_extension='*'
    def __init__(self, config:dict) -> None:
        """Builds a Hugging face backend

        Args:
            config (dict): The configuration file
        """
        super().__init__(config, True)
        self.config = config
        path = self.config['model']

        self.model = AutoModelForCausalLM.from_pretrained(Path("models/hugging_face")/path, low_cpu_mem_usage=True)
        self.tokenizer = AutoTokenizer.from_pretrained(Path("models/hugging_face")/path)

        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0,  # Use GPU if available
        )


    def generate_callback(self, text, new_text_callback):
        def callback(outputs):
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            new_text_callback(generated_text)
            print(text + generated_text, end="\r")
            time.sleep(0.5)
        return callback
    
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
        callback = self.generate_callback(prompt, new_text_callback)
        outputs = self.generator(
            prompt, 
            max_length=100, 
            do_sample=True, 
            num_beams=5, 
            temperature=self.config['temp'], 
            top_k=self.config['top_k'],
            top_p=self.config['top_p'],
            repetition_penalty=self.config['repeat_penalty'],
            repeat_last_n = self.config['repeat_last_n'],
            callback=callback
        )
        print(outputs)