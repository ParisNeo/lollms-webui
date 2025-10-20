"""
Lollms TTM Module
=================

This module is part of the Lollms library, designed to provide Text-to-Music (TTM) functionalities within the LollmsApplication framework. The base class `LollmsTTM` is intended to be inherited and implemented by other classes that provide specific TTM functionalities using various models or APIs.

Author: ParisNeo, a computer geek passionate about AI
Inspired by the LollmsTTI structure.
"""

from lollms.app import LollmsApplication
from pathlib import Path
from typing import List, Dict, Optional
from lollms.main_config import LOLLMSConfig
from lollms.config import TypedConfig
from lollms.service import LollmsSERVICE

class LollmsTTM(LollmsSERVICE):
    """
    LollmsTTM is a base class for implementing Text-to-Music (TTM) functionalities within the LollmsApplication.
    Subclasses should implement the actual music generation logic by overriding the `generate` method.
    """

    def __init__(
                    self,
                    name: str,
                    app: LollmsApplication,
                    service_config: TypedConfig,
                    output_folder: Optional[str | Path] = None
                    ):
        """
        Initializes the LollmsTTM class with the given parameters.

        Args:
            name (str): The unique name of the TTM service.
            app (LollmsApplication): The instance of the main Lollms application.
            service_config (TypedConfig): Configuration specific to this TTM service.
            output_folder (str | Path, optional): Path where the output audio files will be saved.
                                                 If None, defaults to a subfolder named `name` within
                                                 `app.lollms_paths.personal_outputs_path`.
        """
        super().__init__(name, app, service_config)
        if output_folder is not None:
            self.output_folder = Path(output_folder)
        else:
            # Default output path within the standard Lollms outputs structure
            self.output_folder = app.lollms_paths.personal_outputs_path / name
        
        # Ensure the output directory exists
        self.output_folder.mkdir(exist_ok=True, parents=True)

    def generate(self,
                 prompt: str,
                 negative_prompt: str = "",
                 duration_s: float = 10.0,
                 seed: Optional[int] = None,
                 # Add other common TTM parameters as needed by specific models
                 # e.g., model_name: Optional[str] = None,
                 # e.g., tempo_bpm: Optional[int] = None,
                 # e.g., genre: Optional[str] = None,
                 output_dir: Optional[str | Path] = None,
                 output_file_name: Optional[str] = None
                 ) -> List[Dict[str, str]]:
        """
        Generates audio based on the given text prompt.

        This method must be implemented by subclasses to perform the actual text-to-music generation.

        Args:
            prompt (str): The positive prompt describing the desired music.
            negative_prompt (str, optional): A prompt describing elements to avoid in the music. Defaults to "".
            duration_s (float, optional): The desired duration of the generated audio in seconds. Defaults to 10.0.
            seed (int, optional): A seed for reproducibility. If None, a random seed may be used. Defaults to None.
            output_dir (str | Path, optional): Directory to save the output file(s). If None, uses self.output_folder.
            output_file_name (str, optional): Desired name for the output file (without extension). 
                                             If None, a unique name will be generated.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, each containing details about a generated audio file.
                                  Expected keys might include 'path' (local file path), 'url' (if served), 
                                  'prompt', 'duration_s', 'seed', 'format', etc.
        """
        # Base implementation does nothing - subclasses must override this
        raise NotImplementedError("Subclasses must implement the 'generate' method.")

    # Optional: Add methods for other TTM functionalities like music continuation, variation, etc.
    # def generate_continuation(self, audio_path: str | Path, prompt: str, ...):
    #     pass
    #
    # def generate_variation(self, audio_path: str | Path, prompt: str, ...):
    #     pass

    @staticmethod
    def verify(app: LollmsApplication) -> bool:
        """
        Verifies if the TTM service's dependencies are met or if it's ready to use (e.g., API key configured).

        This base implementation returns True. Subclasses should override this
        to perform actual checks (e.g., check for installed libraries, API connectivity).

        Args:
            app (LollmsApplication): The instance of the main Lollms application.

        Returns:
            bool: True if the service is considered available/verified, False otherwise.
        """
        return True

    @staticmethod
    def install(app: LollmsApplication) -> bool:
        """
        Installs the necessary components or dependencies for the TTM service.

        This base implementation returns True. Subclasses should override this
        to perform actual installation steps (e.g., pip install required packages).

        Args:
            app (LollmsApplication): The instance of the main Lollms application.

        Returns:
            bool: True if the installation was successful (or not needed), False otherwise.
        """
        return True

    @staticmethod
    def get(app: LollmsApplication) -> 'LollmsTTM':
        """
        Returns the LollmsTTM class type itself.

        Used for discovery or instantiation purposes within the Lollms framework.

        Args:
            app (LollmsApplication): The instance of the main Lollms application.

        Returns:
            LollmsTTM: The LollmsTTM class type.
        """
        return LollmsTTM

# Example of how a specific TTM implementation might inherit (Conceptual)
# class MySpecificTTM(LollmsTTM):
#     def __init__(self, app: LollmsApplication, service_config: TypedConfig, output_folder: Optional[str | Path] = None):
#         super().__init__("my_specific_ttm", app, service_config, output_folder)
#         # Initialize specific model, API client, etc.
#         # self.model = ... load model based on service_config ...
#
#     def generate(self, prompt: str, negative_prompt: str = "", duration_s: float = 10.0, seed: Optional[int] = None, ...) -> List[Dict[str, str]]:
#         # ... Actual implementation using self.model or an API ...
#         self.app.ShowBlockingMessage(f"Generating music for: {prompt}")
#         try:
#             # 1. Prepare parameters for the specific model/API
#             # 2. Call the generation function
#             # audio_data = self.model.generate(prompt=prompt, neg_prompt=negative_prompt, duration=duration_s, seed=seed, ...)
#             # 3. Determine output path and filename
#             output_path = Path(output_dir or self.output_folder)
#             output_path.mkdir(parents=True, exist_ok=True)
#             if output_file_name:
#                 base_filename = output_file_name
#             else:
#                 # Generate a unique filename (e.g., using timestamp or hash)
#                 import time
#                 base_filename = f"ttm_output_{int(time.time())}"
#             
#             # Assume generated format is WAV for example
#             full_output_path = output_path / f"{base_filename}.wav"
#
#             # 4. Save the generated audio data to the file
#             # save_audio(audio_data, full_output_path) # Replace with actual saving logic
#
#             # 5. Prepare the result dictionary
#             result = {
#                 "path": str(full_output_path),
#                 # "url": Optional URL if served by Lollms web server
#                 "prompt": prompt,
#                 "negative_prompt": negative_prompt,
#                 "duration_s": duration_s, # Actual duration might differ slightly
#                 "seed": seed,
#                 "format": "wav" 
#             }
#             self.app.HideBlockingMessage()
#             return [result]
#         except Exception as e:
#             self.app.HideBlockingMessage()
#             self.app.ShowError(f"Error generating music: {e}")
#             # Log the error properly
#             print(f"Error in MySpecificTTM.generate: {e}") # Use app.error or logging framework
#             return []
#
#     @staticmethod
#     def verify(app: LollmsApplication) -> bool:
#         # Check if 'my_specific_library' is installed
#         try:
#             import my_specific_library 
#             return True
#         except ImportError:
#             return False
#
#     @staticmethod
#     def install(app: LollmsApplication) -> bool:
#         # Install 'my_specific_library'
#         return app.binding_pip_install("my_specific_library")
#
#     @staticmethod
#     def get(app: LollmsApplication) -> 'LollmsTTM':
#         return MySpecificTTM