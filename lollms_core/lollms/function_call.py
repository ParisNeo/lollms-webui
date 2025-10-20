from functools import partial
from typing import Dict, Any, List
from enum import Enum, auto
from lollms.client_session import Client
from lollms.com import LoLLMsCom
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig

# Step 1: Define the FunctionType enum
class FunctionType(Enum):
    CONTEXT_UPDATE = auto()  # Adds information to the context
    AI_FIRST_CALL = auto()  # Called by the AI first, returns output, AI continues
    CLASSIC = auto()  # A classic function call with prompt

# Step 2: Update the FunctionCall base class
class FunctionCall:
    def __init__(self, function_name:str, app:LoLLMsCom, function_type: FunctionType, client: Client, static_parameters:TypedConfig=None, description=""):
        self.function_name = function_name
        self.app = app
        self.function_type = function_type
        self.client = client
        self.description = description
        if static_parameters is not None:
            self.static_parameters = static_parameters
            self.sync_configuration()
        self.personality = app.personality
    
    def sync_configuration(self):
        self.configuration_file_path = self.app.lollms_paths.personal_configuration_path/"services"/self.function_name/f"config.yaml"
        self.configuration_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.static_parameters.config.file_path = self.configuration_file_path
        try:
            self.static_parameters.config.load_config()
        except:
            self.static_parameters.config.save_config()
        self.static_parameters.sync()

    def settings_updated(self):
        pass

    def execute(self, context,  *args, **kwargs):
        """
        Execute the function based on its type.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement the execute method.")

    def update_context(self, context, constructed_context:List[str]):
        """
        Update the context if needed.
        This method should be overridden by subclasses.
        """
        return constructed_context
        
    def process_output(self, context, llm_output:str):
        return llm_output