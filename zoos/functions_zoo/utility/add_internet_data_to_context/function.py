from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails
from ascii_colors import ASCIIColors, trace_exception
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List
import json

class InternetContextEnhancer(FunctionCall):
    def __init__(self, app: LollmsApplication, client: Client):
        static_parameters=TypedConfig(
            ConfigTemplate([
                {
                    "name": "search_engine_api_key",
                    "type": "str",
                    "value": "",  # Replace with your actual Google API key
                    "help": "Google API key"
                },
                {
                    "name": "search_engine_cx",
                    "type": "str",
                    "value": "",  # Replace with your actual Search Engine ID (cx)
                    "help": "Google Custom Search Engine ID"
                },
            ]),
            BaseConfig(config={
            })
        )
        super().__init__("build_context_update_function", app, FunctionType.CONTEXT_UPDATE, client, static_parameters)
        self.service = build("customsearch", "v1", developerKey=self.static_parameters.search_engine_api_key)
        
    def settings_updated(self):
        self.service = build("customsearch", "v1", developerKey=self.static_parameters.search_engine_api_key)

    def update_context(self, context: LollmsContextDetails, constructed_context: List[str]):
        # Check if internet search is enabled
        try:
            # Perform the internet search
            res = self.service.cse().list(
                q=context.prompt,
                cx=self.static_parameters.search_engine_cx,
                num=5
            ).execute()

            # Process and add relevant information to the context
            for item in res.get('items', []):
                title = item.get('title', '')
                snippet = item.get('snippet', '')
                constructed_context.append(f"**Internet Data:** {title} - {snippet}")
        except HttpError as error:
            constructed_context.append(f"**Internet Search Error:** {str(error)}")
        return constructed_context

    def process_output(self, context: LollmsContextDetails, llm_output: str):
        # Currently, we don't modify the output, but we can add logic here if needed.
        return llm_output