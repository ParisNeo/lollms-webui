"""
Lollms TTI Module
=================

This module is part of the Lollms library, designed to provide Text-to-Image (TTI) functionalities within the LollmsApplication framework. The base class `LollmsTTI` is intended to be inherited and implemented by other classes that provide specific TTI functionalities.

Author: ParisNeo, a computer geek passionate about AI
"""

from lollms.app import LollmsApplication
from pathlib import Path
from typing import List, Dict, Tuple
from lollms.main_config import LOLLMSConfig
from lollms.config import TypedConfig
from lollms.service import LollmsSERVICE

class LollmsTTI(LollmsSERVICE):
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
            
    def paint(self, 
                positive_prompt,
                negative_prompt,
                sampler_name="Euler",
                seed=None,
                scale=None,
                steps=None,
                width=None,
                height=None,
                output_folder=None,
                output_file_name=None) -> Tuple[Path | None, Dict | None]:
        """
        Generates images based on the given positive and negative prompts.

        Args:
            positive_prompt (str): The positive prompt describing the desired image.
            negative_prompt (str, optional): The negative prompt describing what should be avoided in the image. Defaults to an empty string.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing image paths, URLs, and metadata.
        """
        pass

    def paint_from_images(self, positive_prompt: str, images: List[str], negative_prompt: str = "") -> Tuple[Path | None, Dict | None]:
        """
        Generates images based on the given positive prompt and reference images.

        Args:
            positive_prompt (str): The positive prompt describing the desired image.
            images (List[str]): A list of paths to reference images.
            negative_prompt (str, optional): The negative prompt describing what should be avoided in the image. Defaults to an empty string.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing image paths, URLs, and metadata.
        """
        pass

    @staticmethod
    def verify(app: LollmsApplication) -> bool:
        """
        Verifies if the TTI service is available.

        Args:
            app (LollmsApplication): The instance of the main Lollms application.

        Returns:
            bool: True if the service is available, False otherwise.
        """
        return True

    @staticmethod
    def install(app: LollmsApplication) -> bool:
        """
        Installs the necessary components for the TTI service.

        Args:
            app (LollmsApplication): The instance of the main Lollms application.

        Returns:
            bool: True if the installation was successful, False otherwise.
        """
        return True
    
    @staticmethod 
    def get(app: LollmsApplication) -> 'LollmsTTI':
        """
        Returns the LollmsTTI class.

        Args:
            app (LollmsApplication): The instance of the main Lollms application.

        Returns:
            LollmsTTI: The LollmsTTI class.
        """
        return LollmsTTI
