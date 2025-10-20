"""
Lollms STT Module
=================

This module is part of the Lollms library, designed to provide Speech-to-Text (STT) functionalities within the LollmsApplication framework. The base class `LollmsSTT` is intended to be inherited and implemented by other classes that provide specific STT functionalities.

Author: ParisNeo, a computer geek passionate about AI
"""

from lollms.app import LollmsApplication
from pathlib import Path
from ascii_colors import ASCIIColors
from lollms.main_config import LOLLMSConfig
from lollms.config import TypedConfig
from lollms.service import LollmsSERVICE

import pipmaster as pm

pm.ensure_packages({"sounddevice":"","wave":""})
try:
    import sounddevice as sd
    import wave
except:
    ASCIIColors.error("Couldn't load sound tools")

class LollmsSTT(LollmsSERVICE):
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

    def transcribe(
                self,
                wav_path: str | Path,
                prompt:str=""
                )->str:
        """
        Transcribes the given audio file to text.

        Args:
            wav_path (str or Path): The path to the WAV audio file to be transcribed.
            prompt (str, optional): An optional prompt to guide the transcription. Defaults to an empty string.
        """
        pass
    
    def stop(self):
        """
        Stops the current generation
        """
        pass
    

    def get_models(self):
        return self.models
    
    @staticmethod
    def verify(app: LollmsApplication) -> bool:
        """
        Verifies if the STT service is available.

        Args:
            app (LollmsApplication): The instance of the main Lollms application.

        Returns:
            bool: True if the service is available, False otherwise.
        """
        return True

    @staticmethod
    def install(app: LollmsApplication) -> bool:
        """
        Installs the necessary components for the STT service.

        Args:
            app (LollmsApplication): The instance of the main Lollms application.

        Returns:
            bool: True if the installation was successful, False otherwise.
        """
        return True
    
    @staticmethod 
    def get(app: LollmsApplication) -> 'LollmsSTT':
        """
        Returns the LollmsSTT class.

        Args:
            app (LollmsApplication): The instance of the main Lollms application.

        Returns:
            LollmsSTT: The LollmsSTT class.
        """
        return LollmsSTT


    def get_devices(self):
        devices =  sd.query_devices()
        print(devices)
        return {
            "status": True,
            "device_names": [device['name'] for device in devices if device["max_input_channels"]>0],
            "device_indexes": [device['index'] for device in devices if device["max_input_channels"]>0]
        }
