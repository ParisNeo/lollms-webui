"""
Lollms TTI Module
=================

This module is part of the Lollms library, designed to provide Text-to-Image (TTI) functionalities within the LollmsApplication framework. The base class `LollmsTTI` is intended to be inherited and implemented by other classes that provide specific TTI functionalities.

Author: ParisNeo, a computer geek passionate about AI
"""
from abc import ABC, abstractmethod
from lollms.app import LollmsApplication
from pathlib import Path
from typing import List, Dict
from lollms.main_config import LOLLMSConfig
from lollms.config import TypedConfig

class LollmsSERVICE(ABC):
    """
    LollmsSERVICE is a base class for implementing Lollms services.
    
    Attributes:
        name (str): The name if the service.
        app (LollmsApplication): The instance of the main Lollms application.
        service_config (TypedConfig): Specific configurations for the current service
    """
    
    def __init__(
                    self,
                    name:str,
                    app: LollmsApplication,
                    service_config: TypedConfig,
                    ):
        """
        Initializes the LollmsTTI class with the given parameters.

        Args:
            app (LollmsApplication): The instance of the main Lollms application.
            model (str, optional): The TTI model to be used for image generation. Defaults to an empty string.
            api_key (str, optional): API key for accessing external TTI services. Defaults to an empty string.
            output_path (Path or str, optional): Path where the output image files will be saved. Defaults to None.
        """
        self.ready = False
        self.name = name
        self.app = app
        self.service_config = service_config
        self.sync_configuration()
    
    def sync_configuration(self):
        self.configuration_file_path = self.app.lollms_paths.personal_configuration_path/"services"/self.name/f"config.yaml"
        self.configuration_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.service_config.config.file_path = self.configuration_file_path
        try:
            self.service_config.config.load_config()
        except:
            self.service_config.config.save_config()
        self.service_config.sync()
    @abstractmethod
    def settings_updated(self):
        pass
