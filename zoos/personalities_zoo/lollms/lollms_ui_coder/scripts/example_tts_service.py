"""
project: lollms_tts
file: lollms_tts.py 
author: ParisNeo
description: 
    This file hosts the XTTS service which provides text-to-speech functionalities using the TTS library.
"""

from pathlib import Path
from lollms.app import LollmsApplication
from lollms.paths import LollmsPaths
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
from lollms.utilities import PackageManager, find_first_available_file_index, add_period
from ascii_colors import ASCIIColors, trace_exception
from lollms.tts import LollmsTTS
from lollms.utilities import run_pip_in_env

# Ensure required packages are installed
if not PackageManager.check_package_installed("TTS"):
    PackageManager.install_or_update("TTS")

if not PackageManager.check_package_installed("simpleaudio"):
    PackageManager.install_or_update("simpleaudio")

from TTS.api import TTS
import simpleaudio as sa

class XTTS(LollmsTTS):
    def __init__(self, app: LollmsApplication, voices_folder: str):
        super().__init__("xtts", app)
        self.generation_threads = {}
        self.voices_folder = voices_folder
        self.ready = False

        # Show a cool LOGO using ASCIIColors
        ASCIIColors.red("   __    ___  __    __          __     __  ___   _        ")
        ASCIIColors.red("  / /   /___\/ /   / /   /\/\  / _\    \ \/ / |_| |_ ___  ")
        ASCIIColors.red(" / /   //  // /   / /   /    \ \ \ _____\  /| __| __/ __| ")
        ASCIIColors.red("/ /___/ \_// /___/ /___/ /\/\ \_\ \_____/  \| |_| |_\__ \ ")
        ASCIIColors.red("\____/\___/\____/\____/\/    \/\__/    /_/\_\\__|\__|___/ ")
        ASCIIColors.red("Using coqui-ai's XTTS backend")
        # Load the TTS model
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        self.tts.to("cuda")
        self.ready = True

    def install(lollms_app: LollmsApplication):
        ASCIIColors.green("XTTS installation started")
        # Here you can perform installation of needed things, or create configuration files or download needed assets etc.
        run_pip_in_env("TTS")
        run_pip_in_env("simpleaudio")

    @staticmethod
    def verify(lollms_paths: LollmsPaths) -> bool:
        # Verify that the service is installed either by verifying the libraries are installed or that some files or folders exist
        try:
            import TTS
            import simpleaudio
            return True
        except ImportError:
            return False

    @staticmethod
    def get(app: LollmsApplication) -> 'XTTS':
        # Verify if the service is installed and if true then return an instance of XTTS
        if XTTS.verify(app.lollms_paths):
            return XTTS(app, app.lollms_paths.custom_voices_path)
        else:
            raise Exception("XTTS service is not installed properly.")

    def tts_file(self, text, file_name_or_path, speaker=None, language="en") -> str:
        # Speaker must be the name of a file in the voices folder list
        speaker_wav = Path(self.voices_folder) / f"{speaker}.wav" if speaker else None
        self.tts.tts_to_file(text=text, file_path=file_name_or_path, speaker_wav=speaker_wav, language=language)
        return file_name_or_path

    def tts_audio(self, text, speaker=None, file_name_or_path: Path | str | None = None, language="en", use_threading=False):
        # Perform text-to-speech and play the output audio here and return a filename or path
        speaker_wav = Path(self.voices_folder) / f"{speaker}.wav" if speaker else None
        wav = self.tts.tts(text=text, speaker_wav=speaker_wav, language=language)
        
        # Convert numpy float32 array to int16
        wav_int16 = np.int16(wav * 32767)
        
        if use_threading:
            self.stop_event.clear()
            self.thread = threading.Thread(target=self._play_audio, args=(wav_int16,))
            self.thread.start()
        else:
            self._play_audio(wav_int16)

    def stop(self):
        # Stop real-time playing
        pass

    def get_voices(self):
        # List voices from the folder
        ASCIIColors.yellow("Listing voices")
        voices = ["main_voice"]
        voices_dir: Path = Path(self.voices_folder)
        voices += [v.stem for v in voices_dir.iterdir() if v.suffix == ".wav"]
        return voices


if __name__ == "__main__":
    # Here do some example
    app = LollmsApplication()
    xtts_service = XTTS.get(app)
    xtts_service.tts_file("Hello, this is a test.", "output.wav", speaker="ParisNeo_Original_voice", language="en")
