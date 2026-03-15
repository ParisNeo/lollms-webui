"""
project: lollms_tts
file: lollms_tts.py 
author: ParisNeo
description: 
    This file hosts the LollmsXTTS service which provides text-to-speech functionalities using the TTS library.
"""

from pathlib import Path
from lollms.app import LollmsApplication
from lollms.paths import LollmsPaths
from lollms.utilities import PackageManager, find_first_available_file_index, add_period
from ascii_colors import ASCIIColors, trace_exception
from lollms.tts import LollmsTTS
from typing import List
import threading
from packaging import version
import pipmaster as pm
if version.parse(str(pm.get_installed_version("numpy"))) > version.parse(str("1.26.9")):
    pm.install_version("numpy", "1.26.4")

if not pm.is_installed("pydub"):
    pm.install("pydub")

import numpy as np


# Ensure required packages are installed
if not pm.is_installed("TTS"):
    pm.install("TTS")

if not pm.is_installed("simpleaudio"):
    pm.install("simpleaudio")

if not pm.is_installed("wave"):
    pm.install("wave")

import re
from pathlib import Path
from pydub import AudioSegment


import wave
from TTS.api import TTS
import simpleaudio as sa
import time
from queue import Queue
import re
import pipmaster as pm
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig

# List of common sampling rates
common_sampling_rates = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 96000, 192000]

# Function to find the closest sampling rate
def closest_sampling_rate(freq, common_rates):
    return min(common_rates, key=lambda x: abs(x - freq))

def xtts_install():
    pm.install_or_update("tts", force_reinstall=True)

class LollmsXTTS(LollmsTTS):
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
                    "name": "model",
                    "type": "str",
                    "value": "",
                    "options": [],
                    "help": "The model to use for text-to-speech. Options: 'alloy', 'echo', 'fable', 'nova', 'shimmer'."
                },
                {
                    "name": "voice",
                    "type": "str",
                    "value": "alloy",
                    "help": "The voice to use for text-to-speech. Options: 'alloy', 'echo', 'fable', 'nova', 'shimmer'."
                },
                {
                    "name": "freq",
                    "type": "int",
                    "value": 22050,
                    "help": "The output frequency"
                },
            ]),
            BaseConfig(config={
                "api_key": "",     # use avx2
            })
        )
        super().__init__("lollms_xtts", app, service_config, output_folder)  
        voices_folder = app.lollms_paths.custom_voices_path/"xtts"
        voices_folder.mkdir(exist_ok=True, parents=True)
        self.voices_folders = [voices_folder] + [Path(__file__).parent/"voices"]
        voices = self.get_voices()
        service_config.config_template["model"]["options"]=voices
        self.freq = self.service_config.freq
        self.generation_threads = {}
        self.stop_event = threading.Event()

        # Show a cool LOGO using ASCIIColors
        ASCIIColors.red("")
        ASCIIColors.red("   __    ___  __    __          __     __  ___   _        ")
        ASCIIColors.red("  / /   /___\/ /   / /   /\/\  / _\    \ \/ / |_| |_ ___  ")
        ASCIIColors.red(" / /   //  // /   / /   /    \ \ \ _____\  /| __| __/ __| ")
        ASCIIColors.red("/ /___/ \_// /___/ /___/ /\/\ \_\ \_____/  \| |_| |_\__ \ ")
        ASCIIColors.red("\____/\___/\____/\____/\/    \/\__/    /_/\_\\__|\__|___/ ")

        # Load the TTS model
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        self.tts.to("cuda")
        self.wav_queue = Queue()
        self.play_obj = None
        self.thread = None        
        self.ready = True
        
    def settings_updated(self):
        voices = self.get_voices()
        self.service_config.config_template["model"]["options"]=voices


    @staticmethod
    def get(app: LollmsApplication) -> 'LollmsXTTS':
        # Verify if the service is installed and if true then return an instance of LollmsXTTS
        if LollmsXTTS.verify(app.lollms_paths):
            return LollmsXTTS(app, app.lollms_paths.custom_voices_path, freq=app.config.xtts_freq)
        else:
            raise Exception("LollmsXTTS service is not installed properly.")
    def get_speaker_wav(self, speaker) -> Path:
        """
        Searches for the speaker file in the specified folders.
        
        :param speaker: The name of the speaker file (without extension).
        :return: The path to the speaker file if found.
        :raises FileNotFoundError: If the speaker file is not found in any of the folders.
        """
        for folder in self.voices_folders:
            potential_speaker_wav = Path(folder) / f"{speaker}"
            if potential_speaker_wav.exists():
                return potential_speaker_wav
        
        raise FileNotFoundError(f"Speaker file '{speaker}' not found in any of the specified folders.")

    def tts_file(self, text, file_name_or_path, speaker=None, language="en") -> str:
        speaker_wav = None
        
        if speaker:
            speaker_wav = self.get_speaker_wav(speaker)
        else:
            speaker_wav = self.get_speaker_wav("main_voice")
        
        # Split the text into sentences
        sentences = re.split('(?<=[.!?])\s+', text)
        
        # Initialize an empty list to store audio segments
        audio_segments = []
        
        # Process sentences in chunks of less than 400 tokens
        chunk = []
        chunk_tokens = 0
        output_path = Path(file_name_or_path)
        
        for i, sentence in enumerate(sentences):
            sentence_tokens = len(sentence.split())
            if chunk_tokens + sentence_tokens > 400:
                # Process the current chunk
                chunk_text = " ".join(chunk)
                temp_file = output_path.with_suffix(f".temp{i}.wav")
                self.tts.tts_to_file(text=chunk_text, file_path=str(temp_file), speaker_wav=speaker_wav, language=language)
                audio_segments.append(AudioSegment.from_wav(str(temp_file)))
                
                # Reset the chunk
                chunk = [sentence]
                chunk_tokens = sentence_tokens
            else:
                chunk.append(sentence)
                chunk_tokens += sentence_tokens
        
        # Process the last chunk if it's not empty
        if chunk:
            chunk_text = " ".join(chunk)
            temp_file = output_path.with_suffix(f".temp{len(sentences)}.wav")
            self.tts.tts_to_file(text=chunk_text, file_path=str(temp_file), speaker_wav=speaker_wav, language=language)
            audio_segments.append(AudioSegment.from_wav(str(temp_file)))
        
        # Combine all audio segments
        combined_audio = sum(audio_segments)
        
        # Export the combined audio to the final file
        combined_audio.export(file_name_or_path, format="wav")
        
        # Clean up temporary files
        for temp_file in output_path.parent.glob(f"{output_path.stem}.temp*.wav"):
            temp_file.unlink()
        
        return file_name_or_path

    
    def tts_audio(self, text, speaker=None, file_name_or_path: Path | str | None = None, language="en", use_threading=False):
        # Split text into sentences
        sentences = re.split(r'(?<=[.!?]) +', text)
        
        if speaker:
            speaker_wav = self.get_speaker_wav(speaker)
        else:
            speaker_wav = self.get_speaker_wav("main_voice")

        if use_threading:
            self.stop_event.clear()
            generator_thread = threading.Thread(target=self._generate_audio, args=(sentences, speaker_wav, language, file_name_or_path))
            generator_thread.start()
            self.thread = threading.Thread(target=self._play_audio)
            self.thread.start()
        else:
            self.stop_event.clear()
            generator_thread = threading.Thread(target=self._generate_audio, args=(sentences, speaker_wav, language, file_name_or_path))
            generator_thread.start()
            self._play_audio()

    def _generate_audio(self, sentences, speaker_wav, language, file_name_or_path):
        wav_data = []
        for sentence in sentences:
            if self.stop_event.is_set():
                break
            wav = self.tts.tts(text=sentence, speaker_wav=speaker_wav, language=language)
            wav_array = np.array(wav, dtype=np.float32)
            wav_array = np.int16(wav_array * 32767)
            self.wav_queue.put(wav_array)
            wav_data.append(wav_array)
        self.wav_queue.put(None)  # Signal that generation is done

        if file_name_or_path:
            self._save_wav(wav_data, file_name_or_path)

    def _play_audio(self):
        buffered_sentences = 0
        buffer = []
        while not self.stop_event.is_set():
            wav = self.wav_queue.get()
            if wav is None:
                # Play any remaining buffered sentences
                for buffered_wav in buffer:

                    # Find the closest sampling rate
                    closest_freq = closest_sampling_rate(self.freq, common_sampling_rates)
                    self.play_obj = sa.play_buffer(buffered_wav.tobytes(), 1, 2, closest_freq)
                    self.play_obj.wait_done()
                    time.sleep(0.5)  # Pause between sentences
                ASCIIColors.green("Audio done")
                break
            buffer.append(wav)
            buffered_sentences += 1
            if buffered_sentences >= 2:
                for buffered_wav in buffer:
                    closest_freq = closest_sampling_rate(self.freq, common_sampling_rates)
                    self.play_obj = sa.play_buffer(buffered_wav.tobytes(), 1, 2, closest_freq)
                    self.play_obj.wait_done()
                    time.sleep(0.5)  # Pause between sentences
                buffer = []
                buffered_sentences = 0

    def _save_wav(self, wav_data, file_name_or_path):
        with wave.open(str(file_name_or_path), 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.freq)
            for wav in wav_data:
                wf.writeframes(wav.tobytes())

    def stop(self):
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join()
        if self.play_obj:
            self.play_obj.stop()

    def get_voices(self):
        # List voices from the folder
        ASCIIColors.yellow("Listing voices")
        voices = []
        for voices_folder in self.voices_folders:
            voices += [v.stem for v in voices_folder.iterdir() if v.suffix == ".wav"]
        return voices


if __name__ == "__main__":
    # Here do some example
    app = LollmsApplication()
    lollms_xtts_service = LollmsXTTS.get(app)
    lollms_xtts_service.tts_file("Hello, this is a test.", "output.wav", speaker="ParisNeo_Original_voice", language="en")
