from typing import Callable
from pathlib import Path
import os
from lollms.config import BaseConfig, ConfigTemplate, TypedConfig
from lollms.personality import APScript, AIPersonality
from lollms.types import MSG_OPERATION_TYPE
from lollms.helpers import ASCIIColors, trace_exception
from lollms.client_session import Client

class Processor(APScript):
    def __init__(self, personality: AIPersonality, callback: Callable = None) -> None:
        # Initialize configuration and states
        personality_config_template = ConfigTemplate([
            {"name": "use_theme_prefix", "type": "bool", "value": True, "help": "Adds a theme prefix to generated CSS files"},
            {"name": "theme_name_prefix", "type": "str", "value": "lollms_theme_", "help": "Prefix for theme files"},
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
                        "generate": self.generate_theme
                    },
                    "default": self.generate_theme
                },
            ],
            callback=callback
        )
        self.css_template = None

    def load_css_template(self):
        """Loads the CSS template from assets folder"""
        try:
            template_path = Path(__file__).parent.parent / "assets" / "css_template.css"
            if template_path.exists():
                with open(template_path, "r", encoding="utf-8") as f:
                    self.css_template = f.read()
                return True
            else:
                self.error("CSS template file not found in assets folder!")
                return False
        except Exception as e:
            self.error(f"Error loading CSS template: {str(e)}")
            return False

    def mounted(self):
        """Called when the personality is mounted"""
        if not self.load_css_template():
            self.error("Failed to load CSS template. Please ensure css_template.css exists in the assets folder.")

    def help(self, prompt="", full_context=""):
        """Provides help information about the personality"""
        return """LoLLMs Theme Generator Personality

This personality helps you create custom CSS themes for LoLLMs based on your descriptions.

Usage:
1. Simply describe the theme you want to create (colors, style, mood, etc.)
2. The personality will generate a complete CSS theme based on your description
3. The generated theme will be saved in the discussion folder

Example prompts:
- Create a dark theme with blue accents
- Generate a light and minimalistic theme
- Make a high contrast theme with neon colors

The generated CSS will follow LoLLMs' styling conventions and structure."""

    def generate_theme_name(self, theme_description: str) -> str:
        """Generates a suitable theme name based on the description"""
        try:
            prompt = f"Generate a short (2-3 words) theme name based on this description: {theme_description}\nMake it suitable for a filename (no spaces, use underscores).\nOnly return the name, nothing else."
            theme_name = self.fast_gen(prompt, callback=self.sink).strip().lower()
            theme_name = theme_name.replace(" ", "_")
            if self.personality_config.use_theme_prefix:
                theme_name = f"{self.personality_config.theme_name_prefix}{theme_name}"
            return theme_name
        except Exception as e:
            self.error(f"Error generating theme name: {str(e)}")
            return "custom_theme"

    def generate_css(self, theme_description: str) -> str:
        """Generates CSS based on the template and user description"""
        try:
            prompt = f"""Based on the following CSS template and theme description, generate a complete CSS theme for LoLLMs.
            
Theme description: {theme_description}

Template structure:
{self.css_template}

Generate a complete CSS file following the same structure but with colors and styles matching the description.
Keep all the selectors and structure, only modify the properties values.
Maintain compatibility with LoLLMs' UI components.
Make sure you build the whole file without shortcuts or comments even if nothing is to be changed. 
"""
            css_content = self.generate_code(
                prompt=prompt,
                callback=self.sink
            )
            self.set_message_content(f"```css\n{css_content}\n```\n")
            return css_content
        except Exception as e:
            self.error(f"Error generating CSS: {str(e)}")
            return None

    def save_theme(self, theme_name: str, css_content: str, client: Client) -> tuple[bool, str]:
        """Saves the generated theme to the discussion folder"""
        try:
            filename = f"{theme_name}.css"
            file_path = Path(client.discussion.discussion_folder) / filename
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(css_content)
            
            return True, str(file_path)
        except Exception as e:
            self.error(f"Error saving theme: {str(e)}")
            return False, ""

    def generate_theme(self, prompt: str, previous_discussion_text: str = "", callback: Callable = None, context_details: dict = None, client: Client = None):
        """Main workflow for generating a theme"""
        try:
            self.callback = callback

            if not self.css_template:
                self.set_message_content("Error: CSS template not loaded. Please check if css_template.css exists in the assets folder.")
                return

            # Generate theme name
            self.step_start("Generating theme name")
            theme_name = self.generate_theme_name(prompt)
            self.step_end(f"Generating theme name")

            # Generate CSS content
            self.step_start("Generating CSS theme")
            css_content = self.generate_css(prompt)
            if not css_content:
                self.set_message_content("Failed to generate CSS content.")
                return
            self.step_end("CSS theme generated")

            # Save the theme
            self.step_start("Saving theme file")
            success, file_path = self.save_theme(theme_name, css_content, client)
            if not success:
                self.set_message_content("Failed to save theme file.")
                return
            self.step_end(f"Theme saved to: {file_path}")
            # Preview the theme
            preview = "\n".join(css_content.split("\n"))
            
            response = f"""Theme generated successfully!
Theme name: {theme_name}
File location: {file_path}

Preview of the generated CSS:
```css
{preview}
"""
            self.set_message_content(response)
        except Exception as e:
            trace_exception(e)
            self.error(f"An error occurred while generating the theme: {str(e)}")
            self.set_message_content("Failed to generate theme due to an error. Please check the logs for details.")
            
    def run_workflow(self, prompt: str, previous_discussion_text: str = "", callback: Callable = None, context_details: dict = None, client: Client = None):
        """Entry point for the personality's workflow"""
        if not self.css_template:
            self.load_css_template()
        self.generate_theme(prompt, previous_discussion_text, callback, context_details, client)