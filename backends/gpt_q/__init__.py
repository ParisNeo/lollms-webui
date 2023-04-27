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
from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM
from pyGpt4All.backend import GPTBackend
from transformers import AutoTokenizer, pipeline
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
from auto_gptq.eval_tasks import LanguageModelingTask

__author__ = "parisneo"
__github__ = "https://github.com/nomic-ai/gpt4all-ui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

backend_name = "GPT-Q"


class GPT_Q(GPTBackend):
    file_extension='*'
    def __init__(self, config:dict) -> None:
        """Builds a GPT-J backend

        Args:
            config (dict): The configuration file
        """
        super().__init__(config, True)
        self.config = config
        # path = Path("models/hugging_face")/self.config['model']
        path = "TheBloke/vicuna-13B-1.1-GPTQ-4bit-128g"
        AutoGPTQForCausalLM.from_pretrained(path, BaseQuantizeConfig())
        self.model = AutoModelForCausalLM.from_pretrained(path, low_cpu_mem_usage=True)
        self.tokenizer = AutoTokenizer.from_pretrained(path)

        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0,  # Use GPU if available
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

        inputs = self.tokenizer(prompt, return_tensors="pt").input_ids
        while len(inputs<n_predict):
            outputs = self.model.generate(
                inputs,
                max_new_tokens=1,
                #new_text_callback=new_text_callback,
                temp=self.config['temp'],
                top_k=self.config['top_k'],
                top_p=self.config['top_p'],
                repeat_penalty=self.config['repeat_penalty'],
                repeat_last_n = self.config['repeat_last_n'],
                n_threads=self.config['n_threads'],
                verbose=verbose
            )
            inputs += outputs
            new_text_callback(self.tokenizer.batch_decode(outputs, skip_special_tokens=True))
