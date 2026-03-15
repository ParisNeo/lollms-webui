# Title LollmsOpenAITTS
# Licence: MIT
# Author : Paris Neo
# Uses open AI api to perform text to speech
# 

from pathlib import Path
from lollms.app import LollmsApplication
from lollms.paths import LollmsPaths
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
import sys
import requests
from typing import List, Dict, Any

from ascii_colors import ASCIIColors, trace_exception
from lollms.paths import LollmsPaths
from lollms.utilities import PackageManager, find_next_available_filename
from lollms.tts import LollmsTTS
import pipmaster as pm
if not pm.is_installed("sounddevice"):
    pm.install("sounddevice")
if not pm.is_installed("soundfile"):
    pm.install("soundfile")

import sounddevice as sd
import soundfile as sf
import os

def get_Whisper(lollms_paths:LollmsPaths):
    return LollmsElevenLabsTTS

class LollmsElevenLabsTTS(LollmsTTS):
    def __init__(
                    self, 
                    app: LollmsApplication,
                    output_folder: Path | str = None,
                    ):
        """
        Initializes the LollmsDalle binding.

        Args:
            api_key (str): The API key for authentication.
            output_folder (Path|str):  The output folder where to put the generated data
        """
    
        # Check for the ELEVENLABS_KEY environment variable if no API key is provided
        api_key = os.getenv("ELEVENLABS_KEY","")
        service_config = TypedConfig(
            ConfigTemplate(
            [
                {
                    "name": "model_id",
                    "type": "str",
                    "value": "eleven_turbo_v2_5",
                    "options": ["eleven_turbo_v2_5","eleven_flash_v2","eleven_multilingual_v2","eleven_multilingual_v1","eleven_english_sts_v2","eleven_english_sts_v1"],
                    "help": "The ID of the model to use for text-to-speech generation. Example: 'eleven_turbo_v2_5'."
                },
                {
                    "name": "voice_name",
                    "type": "str",
                    "value": "Sarah",
                    "help": "The name of the voice to use for text-to-speech generation. Example: 'Sarah'."
                },
                {
                    "name": "language",
                    "type": "str",
                    "value": "en",
                    "options": ["en", "ja", "zh", "de", "hi", "fr", "ko", "pt", "it", "es", "id", "nl", "tr", "fil", "pl", "sv", "bg", "ro", "ar", "cs", "el", "fi", "hr", "ms", "sk", "da", "ta", "uk", "ru", "hu", "no", "vi"],  # Dynamically populated based on the selected model_id
                    "help": "The language to use for text-to-speech generation. Supported languages depend on the selected model."
                },
                {
                    "name": "api_key",
                    "type": "str",
                    "value": api_key,
                    "help": "A valid API key for accessing the Eleven Labs service."
                },
                {
                    "name": "similarity_boost",
                    "type": "bool",
                    "value": False,
                    "help": "If enabled, increases the similarity of the generated speech to the selected voice."
                },
                {
                    "name": "streaming",
                    "type": "bool",
                    "value": False,
                    "help": "If enabled, the text-to-speech output will be streamed in real-time instead of being generated all at once."
                }
            ]
            ),
            BaseConfig(config={
                "api_key": "",     # use avx2
            })
        )
        super().__init__("elevenlabs_tts", app, service_config, output_folder)
        self.ready = True
        
        self.voices = []
        self.voice_id_map = {}
        try:
            self._fetch_voices()
            self.voice_id = self._get_voice_id(service_config.voice_name)
        except:
            pass
    def settings_updated(self):
        pass


    def _fetch_voices(self):
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {"xi-api-key": self.service_config.api_key}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            for voice in data.get("voices", []):
                name = voice.get("name")
                voice_id = voice.get("voice_id")
                if name and voice_id:
                    self.voices.append(name)
                    self.voice_id_map[name] = voice_id
        except requests.RequestException as e:
            print(f"Error fetching voices: {e}")
            # Fallback to default voice
            self.voices = ["Sarah"]
            self.voice_id_map = {"Sarah": "EXAVITQu4vr4xnSDxMaL"}

    def _get_voice_id(self, voice_name: str) -> str:
        return self.voice_id_map.get(voice_name, "EXAVITQu4vr4xnSDxMaL")  # Default to Sarah if not found

    def set_voice(self, voice_name: str):
        if voice_name in self.voices:
            self.service_config.voice_name = voice_name
            self.voice_id = self._get_voice_id(voice_name)
        else:
            raise ValueError(f"Voice '{voice_name}' not found. Available voices: {', '.join(self.voices)}")



    def tts_file(self, text, file_name_or_path: Path | str = None, speaker=None, language="en", use_threading=False):
        speech_file_path = file_name_or_path
        payload = {
            "text": text,
            "language_code": language,
            "model_id": self.service_config.model_id,
                "voice_settings": {
                "stability": self.service_config.stability,
                "similarity_boost": self.service_config.similarity_boost
            }
        }
        headers = {
            "xi-api-key": self.service_config.api_key,
            "Content-Type": "application/json"
        }
        
        if self.service_config.streaming:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream"
            response = requests.post(url, json=payload, headers=headers)
            # Handle streaming response if needed
        else:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code==400:
                del payload["language_code"]
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
                response = requests.post(url, json=payload, headers=headers)
            with open(speech_file_path, 'wb') as f:
                f.write(response.content)

        return speech_file_path

    def tts_audio(self, text, speaker: str = None, file_name_or_path: Path | str = None, language="en", use_threading=False):
        speech_file_path = file_name_or_path
        payload = {
            "text": text,
            "language_code": language,
            "model_id": self.service_config.model_id,
            "voice_settings": {
                "stability": self.service_config.stability,
                "similarity_boost": self.service_config.similarity_boost
            }
        }
        headers = {
            "xi-api-key": self.service_config.api_key,
            "Content-Type": "application/json"
        }

        if self.service_config.streaming:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream"
            response = requests.post(url, json=payload, headers=headers)
            # Handle streaming response if needed
        else:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                with open(speech_file_path, 'wb') as f:
                    f.write(response.content)
            else:
                self.app.error(f"Couldn't generate speech, {response.reason}")

        def play_audio(file_path):
            # Read the audio file
            data, fs = sf.read(file_path, dtype='float32')
            # Play the audio file
            sd.play(data, fs)
            # Wait until the file is done playing
            sd.wait()

        # Example usage
        play_audio(speech_file_path)
