######
# Project       : GPT4ALL-UI
# File          : binding.py
# Author        : ParisNeo with the help of the community
# Supported by Nomic-AI
# license       : Apache 2.0
# Description   : 
# This is an interface class for GPT4All-ui bindings.
######
from pathlib import Path
from typing import Callable
from transformers import AutoTokenizer, TextGenerationPipeline
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
from api.binding import LLMBinding
import torch
import yaml
import requests
from tqdm import tqdm
import os
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
import concurrent.futures
import wget


__author__ = "parisneo"
__github__ = "https://github.com/ParisNeo/GPTQ_binding"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

binding_name = "GPTQ"

class GPTQ(LLMBinding):
    file_extension='*'
    def __init__(self, config:dict) -> None:
        """Builds a GPTQ binding

        Args:
            config (dict): The configuration file
        """
        super().__init__(config, False)
        
        self.model_dir = f'{config["model"]}'
        pretrained_model_dir = "facebook/opt-125m"
        quantized_model_dir = "opt-125m-4bit"


        self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_dir, use_fast=True)
        # load quantized model to the first GPU
        self.model = AutoGPTQForCausalLM.from_quantized(self.model_dir)

    def tokenize(self, prompt):
        """
        Tokenizes the given prompt using the model's tokenizer.

        Args:
            prompt (str): The input prompt to be tokenized.

        Returns:
            list: A list of tokens representing the tokenized prompt.
        """
        return self.tokenizer.tokenize(prompt)

    def detokenize(self, tokens_list):
        """
        Detokenizes the given list of tokens using the model's tokenizer.

        Args:
            tokens_list (list): A list of tokens to be detokenized.

        Returns:
            str: The detokenized text as a string.
        """
        return self.tokenizer.decode(tokens_list)
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
            tok = self.tokenizer.decode(self.model.generate(**self.tokenizer(prompt, return_tensors="pt").to("cuda:0"))[0])
            if new_text_callback is not None:
                new_text_callback(tok)
            output = tok
            """
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
            """
        except Exception as ex:
            print(ex)
        return output

    def download_model(self, repo, base_folder, callback=None):
        """
        Downloads a folder from a Hugging Face repository URL, reports the download progress using a callback function,
        and displays a progress bar.

        Args:
            repo (str): The name of the Hugging Face repository.
            base_folder (str): The base folder where the repository should be saved.
            installation_path (str): The path where the folder should be saved.
            callback (function, optional): A callback function to be called during the download
                with the progress percentage as an argument. Defaults to None.
        """
        dont_download = [".gitattributes"]

        url = f"https://huggingface.co/{repo}/tree/main"
        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        file_names = []

        for a_tag in soup.find_all('a', {'class': 'group'}):
            span_tag = a_tag.find('span', {'class': 'truncate'})
            if span_tag:
                file_name = span_tag.text
                if file_name not in dont_download:
                    file_names.append(file_name)

        print(f"Repo: {repo}")
        print("Found files:")
        for file in file_names:
            print(" ", file)

        dest_dir = Path(base_folder) / repo.replace("/", "_")
        dest_dir.mkdir(parents=True, exist_ok=True)
        os.chdir(dest_dir)

        def download_file(get_file):
            filename = f"https://huggingface.co/{repo}/resolve/main/{get_file}"
            print(f"\nDownloading {filename}")
            wget.download(filename, out=str(dest_dir), bar=callback)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(download_file, file_names)

        os.chdir(base_folder)

        installation_path = Path(installation_path)
        installation_path.parent.mkdir(parents=True, exist_ok=True)
        dest_dir.rename(installation_path)

        print("Done")
    @staticmethod
    def list_models(config:dict):
        """Lists the models for this binding
        """
        
        return [
            "EleutherAI/gpt-j-6b",
            "opt-125m-4bit"  
            "TheBloke/medalpaca-13B-GPTQ-4bit",
            "TheBloke/stable-vicuna-13B-GPTQ",
        ]
    @staticmethod
    def get_available_models():
        # Create the file path relative to the child class's directory
        binding_path = Path(__file__).parent
        file_path = binding_path/"models.yaml"

        with open(file_path, 'r') as file:
            yaml_data = yaml.safe_load(file)
        
        return yaml_data