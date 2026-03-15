# Title LollmsWhisper
# Licence: MIT
# Author : Paris Neo
# 

from pathlib import Path
from lollms.app import LollmsApplication
from lollms.stt import LollmsSTT
from dataclasses import dataclass
from PIL import Image, PngImagePlugin
from enum import Enum
from typing import List, Dict, Any

from ascii_colors import ASCIIColors, trace_exception
from lollms.paths import LollmsPaths
import subprocess
import pipmaster as pm
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
try:
    if not pm.is_installed("openai-whisper"):
        pm.install("openai-whisper")
        try:
            pass#install_conda_package("conda-forge::ffmpeg")
        except Exception as ex:
            trace_exception(ex)
            ASCIIColors.red("Couldn't install ffmpeg")
except:
        try:
            pass#install_conda_package("conda-forge::ffmpeg")
        except Exception as ex:
            trace_exception(ex)
            ASCIIColors.red("Couldn't install ffmpeg")
        pm.install("git+https://github.com/openai/whisper.git")

try:
    import whisper
except:
    pm.install("openai-whisper")

class LollmsWhisper(LollmsSTT):
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
        service_config = TypedConfig(
            ConfigTemplate([
                {
                    "name": "model_name",
                    "type": "str",
                    "value": "base",
                    "options": ["tiny", "tiny.en", "base", "base.en", "small", "small.en", "medium", "medium.en", "large", "large-v2", "large-v3", "turbo"],
                    "help": "The engine to be used"
                },
                
            ]),
            BaseConfig(config={
                "api_key": "",     # use avx2
            })
        )


        super().__init__("whisper",app, service_config, output_folder)
        try:
            self.whisper = whisper.load_model(service_config.model_name)
        except:
            ASCIIColors.red("Couldn't load whisper model!\nWhisper will be disabled")
            self.whisper = None
        self.ready = True
    def settings_updated(self):
        pass
    def transcribe(
                self,
                wave_path: str|Path
                )->str:
        if self.whisper:
            result = self.whisper.transcribe(str(wave_path))
            return result["text"]
        else:
            ASCIIColors.error("Whisper is broken")
            return ""