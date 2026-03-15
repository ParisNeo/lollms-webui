from lollms.personality import APScript, AIPersonality
from lollms.config import ConfigTemplate, BaseConfig, TypedConfig
from lollms.types import MSG_OPERATION_TYPE
from lollms.client_session import Client
from typing import Callable

class CustomPersonality(APScript):
    def __init__(self, personality: AIPersonality, callback: Callable = None):
        personality_config_template = ConfigTemplate([
            {"name": "example_setting", "type": "string", "value": "default", "help": "Description of the setting"},
            # Add more settings as needed
        ])
        personality_config_vals = BaseConfig.from_template(personality_config_template)
        personality_config = TypedConfig(personality_config_template, personality_config_vals)
        
        super().__init__(personality, personality_config, callback=callback)

    def run_workflow(self, prompt: str, previous_discussion_text: str = "", callback: Callable = None, context_details: dict = None, client: Client = None):
        self.callback = callback
        full_prompt = self.build_prompt_from_context_details(context_details)
        
        # Example of using fast_gen (the generation content will be shown to the user as it is generated)
        response = self.fast_gen(full_prompt)
        self.set_message_content(response)

        # Example of using self.sink for intermediate processing (the generation content will not be shown to the user which is useful for intermediateprocessing)
        intermediate_analysis = self.fast_gen(f"Analyze the following prompt: {prompt}", callback=self.sink)

        # Example of yes/no question
        if self.yes_no("Is this a question about images?", prompt):
            # Handle image-related tasks
            pass
        
        # Example of multichoice question
        task_type = self.multichoice_question(
            "What type of task is this?",
            ["text generation", "image analysis", "code writing"],
            context=prompt
        )
        
        if task_type == 0:  # text generation
            # Handle text generation
            pass
        elif task_type == 1:  # image analysis
            # Handle image analysis
            pass
        elif task_type == 2:  # code writing
            # Handle code writing
            pass

    def install(self):
        super().install()
        # Add any additional installation steps here

