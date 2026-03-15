from typing import Callable
from lollms.config import BaseConfig, ConfigTemplate, TypedConfig
from lollms.personality import APScript, AIPersonality
from lollms.types import MSG_OPERATION_TYPE
from lollms.client_session import Client

class Processor(APScript):
    def __init__(self, personality: AIPersonality, callback: Callable = None) -> None:
        # Initialize configuration
        personality_config_template = ConfigTemplate([
            {"name": "prompt_style", "type": "str", "value": "detailed", "options":["detailed", "concise"], "help": "Style of prompt suggestions"},
            {"name": "include_examples", "type": "bool", "value": True, "help": "Include example responses in suggestions"},
            {"name": "max_examples", "type": "int", "value": 3, "help": "Maximum number of examples to generate"},
        ])
        personality_config_vals = BaseConfig.from_template(personality_config_template)
        personality_config = TypedConfig(personality_config_template, personality_config_vals)
        
        super().__init__(
            personality,
            personality_config,
            states_list=[
                {
                    "name": "idle",
                    "commands": {
                        "help": self.help,
                        "analyze": self.analyze_prompt,
                        "improve": self.improve_prompt,
                        "examples": self.generate_examples,
                    },
                    "default": self.run_workflow
                },
            ],
            callback=callback
        )
        
    def help(self, prompt="", full_context=""):
        """Provides help information about the Prompt Expert personality."""
        return """🤖 Prompt Expert - Your AI Prompt Crafting Assistant

Commands:
- analyze [prompt]: Analyzes the effectiveness of your prompt
- improve [prompt]: Suggests improvements for your prompt
- examples [prompt]: Generates example responses for your prompt

General Usage:
Simply type your prompt, and I'll help you make it more effective!

Tips:
- Be specific about your requirements
- Include context when necessary
- Specify the desired format or style
- Use clear and unambiguous language"""

    def analyze_prompt(self, prompt: str, full_context: str = "") -> str:
        """Analyzes the given prompt for effectiveness."""
        if not prompt:
            return "Please provide a prompt to analyze."

        analysis_prompt = f"""Analyze this AI prompt for effectiveness:
{prompt}

Consider:
1. Clarity
2. Specificity
3. Context
4. Potential ambiguities
5. Structure

Provide a detailed analysis."""

        try:
            self.step_start("Analyzing prompt")
            analysis = self.generate(analysis_prompt)
            self.step_end("Analysis complete")
            return analysis
        except Exception as e:
            return f"Error analyzing prompt: {str(e)}"

    def improve_prompt(self, prompt: str, full_context: str = "") -> str:
        """Suggests improvements for the given prompt."""
        if not prompt:
            return "Please provide a prompt to improve."

        improvement_prompt = f"""Improve this AI prompt:
{prompt}


Provide:
1. Enhanced version in {self.personality_config.prompt_style} mode
2. Explanation of improvements
3. Additional suggestions
"""

        try:
            self.step_start("Generating improvements")
            improvements = self.generate(improvement_prompt)
            self.step_end("Improvements generated")
            return improvements
        except Exception as e:
            return f"Error improving prompt: {str(e)}"

    def generate_examples(self, prompt: str, full_context: str = "") -> str:
        """Generates example responses for the given prompt."""
        if not prompt:
            return "Please provide a prompt to generate examples for."

        max_examples = self.personality_config.max_examples
        example_prompt = f"""Generate {max_examples} diverse example responses for this prompt:
{prompt}

Each example should be different in style and content while remaining relevant."""

        try:
            self.step_start("Generating examples")
            examples = self.generate(example_prompt)
            self.step_end("Examples generated")
            return examples
        except Exception as e:
            return f"Error generating examples: {str(e)}"

    def run_workflow(self, prompt: str, previous_discussion_text: str = "", callback: Callable = None, context_details: dict = None, client: Client = None) -> str:
        """Main workflow for processing user input."""
        try:
            self.callback = callback

            # Check if prompt is empty
            if not prompt.strip():
                return self.help()

            # Determine user intent
            intent_prompt = f"""Determine the user's primary intent from this prompt:
{prompt}
"""

            self.step_start("Determining user intent")
            intent = self.multichoice_question(
                intent_prompt,
                ["Analyze existing prompt", "Improve prompt", "Get examples", "General help"],
                context=prompt
            )
            self.step_end("Determining user intent")

            # Process based on intent
            if intent == 0:  # analyze
                return self.analyze_prompt(prompt)
            elif intent == 1:  # improve
                return self.improve_prompt(prompt)
            elif intent == 2:  # examples
                return self.generate_examples(prompt)
            else:  # help
                return self.help()

        except Exception as e:
            return f"""An error occurred while processing your request: {str(e)}

Please try again or type 'help' for assistance."""

    def validate_prompt(self, prompt: str) -> bool:
        """Validates if the prompt is suitable for processing."""
        if not prompt:
            return False
        
        validation_prompt = f"""Is this a valid and processable prompt?
{prompt}

Consider:
1. Length (not too short or too long)
2. Basic coherence
3. Presence of actual request/question
4. Appropriate content

Answer with yes or no."""

        return self.yes_no(validation_prompt, context=prompt)

