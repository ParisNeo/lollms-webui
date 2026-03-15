# Title LollmsOpenAIWhisper
# Licence: MIT
# Author : Paris Neo
# 

from pathlib import Path
import sys
from lollms.app import LollmsApplication
from lollms.paths import LollmsPaths
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
import time
import io
import sys
import requests
import os
import base64
import subprocess
import time
import json
import platform
from dataclasses import dataclass
from PIL import Image, PngImagePlugin
from enum import Enum
from typing import List, Dict, Any

from ascii_colors import ASCIIColors, trace_exception
from lollms.paths import LollmsPaths
from lollms.utilities import PackageManager, find_next_available_filename
from lollms.stt import LollmsSTT
import subprocess
import shutil
from tqdm import tqdm
import threading
from io import BytesIO
from openai import OpenAI


class LollmsOpenAIWhisper(LollmsSTT):
    def __init__(
                    self, 
                    app:LollmsApplication, 
                    output_folder:str|Path=None
                    ):
        """
        Initializes the LollmsDalle binding.

        Args:
            api_key (str): The API key for authentication.
            output_folder (Path|str):  The output folder where to put the generated data
        """          
        api_key = os.getenv("OPENAI_KEY","")
        service_config = TypedConfig(
            ConfigTemplate([
                {"name":"api_key", "type":"str", "value":api_key, "help":"A valid Open AI key to generate text using anthropic api"},
                {
                    "name": "model",
                    "type": "str",
                    "value": "whisper-1",
                    "options": ["whisper-1"],
                    "help": "The model to be used"
                },                
            ]),
            BaseConfig(config={
                "api_key": "",     # use avx2
            })
        )


        super().__init__("openai_whisper",app, service_config, output_folder)    
        self.client = OpenAI(api_key=self.service_config.api_key)
        self.ready = True
    def settings_updated(self):
        self.client = OpenAI(api_key=self.service_config.api_key)
        self.ready = True
        
    def transcribe(
                self,
                wav_path: str|Path,
                model:str="",
                output_path:str|Path=None
                ):
        if model=="" or model is None:
            model = self.model
        if output_path is None:
            output_path = self.output_path
        audio_file= open(str(wav_path), "rb")
        transcription = self.client.audio.transcriptions.create(
            model=model, 
            file=audio_file,
            response_format="text"
        )        
        return transcription
