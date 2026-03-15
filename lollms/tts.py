"""
Lollms TTS Module
=================

This module is part of the Lollms library, designed to provide Text-to-Speech (TTS) functionalities within the LollmsApplication framework. The base class `LollmsTTS` is intended to be inherited and implemented by other classes that provide specific TTS functionalities.

Author: ParisNeo, a computer geek passionate about AI
"""
from lollms.app import LollmsApplication
from pathlib import Path
from ascii_colors import ASCIIColors
from lollms.main_config import LOLLMSConfig
from lollms.config import TypedConfig
import re
from lollms.service import LollmsSERVICE
import pipmaster as pm

if not pm.is_installed("sounddevice"):
    # os.system("sudo apt-get install portaudio19-dev")
    pm.install("sounddevice")
    pm.install("wave")

try:
    import sounddevice as sd
    import wave
except:
    ASCIIColors.error("Couldn't load sound tools")
class LollmsTTS(LollmsSERVICE):
    """
    LollmsTTI is a base class for implementing Text-to-Image (TTI) functionalities within the LollmsApplication.
    """
    
    def __init__(
                    self,
                    name:str,
                    app: LollmsApplication,
                    service_config: TypedConfig,
                    output_folder: str|Path=None
                    ):
        """
        Initializes the LollmsTTI class with the given parameters.

        Args:
            app (LollmsApplication): The instance of the main Lollms application.
            model (str, optional): The TTI model to be used for image generation. Defaults to an empty string.
            api_key (str, optional): API key for accessing external TTI services. Defaults to an empty string.
            output_path (Path or str, optional): Path where the output image files will be saved. Defaults to None.
        """
        super().__init__(name, app, service_config)
        if output_folder is not None:
            self.output_folder = Path(output_folder)
        else:
            self.output_folder = app.lollms_paths.personal_outputs_path/name
            self.output_folder.mkdir(exist_ok=True, parents=True)



    def tts_file(self, text, file_name_or_path, speaker=None, language="en")->str:
        """
        Converts the given text to speech and saves it to a file.

        Args:
            text (str): The text to be converted to speech.
            speaker (str): The speaker/voice model to be used.
            file_name_or_path (Path or str): The name or path of the output file.
            language (str, optional): The language of the text. Defaults to "en".
        """
        pass

    def tts_audio(self, text, speaker=None, file_name_or_path: Path | str = None, language="en", use_threading=False):
        """
        Converts the given text to speech and returns the audio data.

        Args:
            text (str): The text to be converted to speech.
            speaker (str): The speaker/voice model to be used.
            file_name_or_path (Path or str, optional): The name or path of the output file. Defaults to None.
            language (str, optional): The language of the text. Defaults to "en".
            use_threading (bool, optional): Whether to use threading for the operation. Defaults to False.
        """
        pass

    def stop(self):
        """
        Stops the current generation
        """
        pass

    @staticmethod
    def verify(app: LollmsApplication) -> bool:
        """
        Verifies if the TTS service is available.

        Args:
            app (LollmsApplication): The instance of the main Lollms application.

        Returns:
            bool: True if the service is available, False otherwise.
        """
        return True

    @staticmethod
    def install(app: LollmsApplication) -> bool:
        """
        Installs the necessary components for the TTS service.

        Args:
            app (LollmsApplication): The instance of the main Lollms application.

        Returns:
            bool: True if the installation was successful, False otherwise.
        """
        return True
    
    @staticmethod 
    def get(app: LollmsApplication) -> 'LollmsTTS':
        """
        Returns the LollmsTTS class.

        Args:
            app (LollmsApplication): The instance of the main Lollms application.

        Returns:
            LollmsTTS: The LollmsTTS class.
        """
        return LollmsTTS
    
    def get_voices(self):
        """
        Retrieves the available voices for TTS.

        Returns:
            list: A list of available voices.
        """
        return self.voices

    def get_models(self):
        """
        Retrieves the available models for TTS.

        Returns:
            list: A list of available models.
        """
        return self.models


    def get_devices(self):
        devices =  sd.query_devices()

        return {
            "status": True,
            "device_names": [device['name'] for device in devices if device["max_output_channels"]>0],
            "device_indexes": [device['index'] for device in devices if device["max_output_channels"]>0]
        }
    @staticmethod
    def clean_text(text):
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        # Remove code blocks (assuming they're enclosed in backticks or similar markers)
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`.*?`', '', text)
        # Remove any remaining code-like patterns (this can be adjusted as needed)
        text = re.sub(r'[\{\}\[\]\(\)<>]', '', text)  
        text = text.replace("\\","")      
        return text
