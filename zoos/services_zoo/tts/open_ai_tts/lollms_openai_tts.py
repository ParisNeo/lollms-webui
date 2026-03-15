# Title LollmsOpenAITTS
# Licence: MIT
# Author : Paris Neo
# Uses open AI api to perform text to speech
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
from lollms.tts import LollmsTTS
import subprocess
import shutil
from pathlib import Path
from tqdm import tqdm
import threading
from io import BytesIO
import pipmaster as pm
if not pm.is_installed("openai"):
    pm.install("openai")
from openai import OpenAI

if not pm.is_installed("sounddevice"):
    pm.install("sounddevice")
if not pm.is_installed("soundfile"):
    pm.install("soundfile")

import sounddevice as sd
import soundfile as sf

def get_Whisper(lollms_paths:LollmsPaths):
    return LollmsOpenAITTS

class LollmsOpenAITTS(LollmsTTS):
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

        # Check for the OPENAI_KEY environment variable if no API key is provided
        api_key = os.getenv("OPENAI_KEY","")
        service_config = TypedConfig(
            ConfigTemplate([
                {
                    "name": "model",
                    "type": "str",
                    "value": "tts-1",
                    "options": ["alloy", "echo", "fable", "nova", "shimmer"],
                    "help": "The model to use for text-to-speech. Options: 'alloy', 'echo', 'fable', 'nova', 'shimmer'."
                },
                {
                    "name": "voice",
                    "type": "str",
                    "value": "alloy",
                    "help": "The voice to use for text-to-speech. Options: 'alloy', 'echo', 'fable', 'nova', 'shimmer'."
                },
                {
                    "name": "api_key",
                    "type": "str",
                    "value": api_key,
                    "help": "A valid API key for accessing the text-to-speech service."
                },
            ]),
            BaseConfig(config={
                "api_key": "",     # use avx2
            })
        )
        super().__init__("openai_tts", app, service_config, output_folder)

        self.client = OpenAI(api_key=self.service_config.api_key)
        self.output_folder = output_folder
        self.ready = True

    def settings_updated(self):
        self.client = OpenAI(api_key=self.service_config.api_key)

    def tts_file(self, text, speaker, file_name_or_path, language="en"):
        speech_file_path = file_name_or_path
        response = self.client.audio.speech.create(
        model=self.service_config.model,
        voice=self.service_config.voice,
        input=text,
        response_format="wav"
        
        )

        response.write_to_file(speech_file_path)

    def tts_audio(self, text, speaker:str=None, file_name_or_path:Path|str=None, language="en", use_threading=False):
        speech_file_path = file_name_or_path
        response = self.client.audio.speech.create(
        model=self.service_config.model,
        voice=self.service_config.voice if speaker is None else speaker,
        input=text,
        response_format="wav"
        
        )

        response.write_to_file(speech_file_path)
        def play_audio(file_path):
            # Read the audio file
            data, fs = sf.read(file_path, dtype='float32')
            # Play the audio file
            sd.play(data, fs)
            # Wait until the file is done playing
            sd.wait()

        # Example usage
        play_audio(speech_file_path)

    def tts_file(self, text, speaker=None, file_name_or_path:Path|str=None, language="en", use_threading=False):
        speech_file_path = file_name_or_path
        text = self.clean_text(text)
        response = self.client.audio.speech.create(
        model=self.service_config.model,
        voice=self.service_config.voice,
        input=text,
        response_format="wav"
        
        )

        response.write_to_file(speech_file_path)
        return file_name_or_path
