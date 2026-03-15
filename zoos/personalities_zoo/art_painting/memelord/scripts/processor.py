import subprocess
import sys
from pathlib import Path
from typing import Callable, Dict, Any, List

from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.types import MSG_OPERATION_TYPE
from lollms.personality import APScript, AIPersonality
from lollms.utilities import PromptReshaper, discussion_path_to_url, find_first_available_file_path, File_Path_Generator
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails

# Helper function to create unique filenames
def get_unique_filename(folder: Path, base_name: str, extension: str) -> Path:
    i = 1
    output_file_name = f"{base_name}_{i}.{extension}"
    while (folder / output_file_name).exists():
        i += 1
        output_file_name = f"{base_name}_{i}.{extension}"
    return folder / output_file_name

class Processor(APScript):
    """
    Meme Builder Personality Processor.
    Guides the user through creating a meme by:
    1. Getting an image description.
    2. Generating the image using a TTI service.
    3. Getting top and bottom text.
    4. Displaying the results.
    """

    def __init__(
                 self,
                 personality: AIPersonality,
                 callback: Callable | None = None,
                ) -> None:
        """
        Initializes the Processor instance.
        """
        personality_config_template = ConfigTemplate(
            [
                # TTI settings - users can configure these in personality settings
                {"name":"tti_negative_prompt", "type":"str", "value":"ugly, blurry, deformed, watermark, text, signature, bad anatomy, worst quality, low quality", "help":"Default negative prompt for image generation"},
                {"name":"tti_sampler_name", "type":"str", "value":"Euler", "help":"Sampler to use for TTI (if TTI service supports it)"},
                {"name":"tti_seed", "type":"int", "value":-1, "help":"Seed for TTI (-1 for random)"},
                {"name":"tti_scale", "type":"float", "value":7.5, "min":0.0, "max":100.0, "help":"CFG Scale for TTI"},
                {"name":"tti_steps", "type":"int", "value":30, "min":1, "max":200, "help":"Number of steps for TTI"},
                {"name":"tti_width", "type":"int", "value":512, "min":64, "max":2048, "help":"Image width for TTI"},
                {"name":"tti_height", "type":"int", "value":512, "min":64, "max":2048, "help":"Image height for TTI"},
                {"name":"refine_image_prompt_with_llm", "type":"bool", "value":True, "help":"If true, use the LLM to refine the user's image description into a better TTI prompt."},
                {"name":"max_discussion_history_for_refinement", "type":"int", "value":3, "min":1, "max":10, "help":"Max number of previous user messages to consider for prompt refinement."},

                # Internal state tracking (not directly user-configurable but part of the dynamic config concept)
                # We'll manage state more directly in instance variables for this simple case
            ]
        )
        personality_config_vals = BaseConfig.from_template(personality_config_template)

        personality_config = TypedConfig(
            personality_config_template,
            personality_config_vals
        )

        super().__init__(
                            personality,
                            personality_config,
                            states_list={}, # Using custom flow, not command-based state machine here
                            callback=callback
                        )
        
        # Initialize meme creation state
        self.reset_meme_creation_state()

    def reset_meme_creation_state(self):
        """Resets the internal state for creating a new meme."""
        self.log_message("Resetting meme creation state.")
        self._image_description_user: str | None = None
        self._image_prompt_final: str | None = None
        self._image_path: Path | None = None
        self._image_url: str | None = None
        self._top_text: str | None = None
        self._bottom_text: str | None = None
        self._current_step: str = "get_image_description" # "get_image_description", "get_top_text", "get_bottom_text", "display_meme"

    def install(self):
        super().install()
        self.info("Meme Builder Personality installed.")
        # Check if TTI service is available, though it's better handled in run_workflow
        if not self.personality.app.tti:
            self.warning("No Text-to-Image (TTI) service seems to be configured in LoLLMs. Meme Builder needs a TTI service to generate images.")
        # You could add any other one-time setup here.
        # For example, creating a subfolder in outputs for memes:
        (self.personality.lollms_paths.personal_outputs_path / "meme_builder_images").mkdir(parents=True, exist_ok=True)


    def get_welcome(self, welcome_message:str, client:Client):
        self.reset_meme_creation_state() # Ensure clean state on new discussion
        return super().get_welcome(welcome_message, client)

    def _refine_image_prompt(self, user_description: str, context_details: LollmsContextDetails) -> str:
        """Uses the LLM to refine a user's image description into a TTI prompt."""
        self.step_start("Refining image description with LLM...")
        
        # Build a limited context for refinement
        history = context_details.discussion_messages
        
        refinement_prompt_parts = [
            "You are an AI assistant helping to create an effective positive prompt for an image generation model (like Stable Diffusion or DALL-E).",
            "The user wants an image for a meme.",
            f"Here's the relevant recent discussion and their latest description:\n{history}",
            f"User's latest image description: '{user_description}'",
            "Based on this, formulate a concise and descriptive positive prompt for the image generation model. Focus on visual details, style (e.g., photo, cartoon, abstract), and key elements.",
            "Output ONLY the refined prompt, with no other text, explanation, or conversational fluff. For example: 'photo of a confused orange cat wearing glasses, looking at a complex mathematical equation on a chalkboard, humorous style'",
            "Refined Prompt:"
        ]
        # We use a simpler build_prompt here as we don't need to sacrifice context in the same way.
        # We want the LLM to see all the instructions.
        set_message_content_refinement_prompt = "\n".join(refinement_prompt_parts)

        refined_prompt = self.personality.model.generate(
            set_message_content_refinement_prompt,
            max_size=150, # Keep prompt relatively short
            temperature=0.5, # More deterministic for prompt generation
            top_k=30,
            top_p=0.8,
            callback=self.sink # Show thinking dots
        )
        refined_prompt = self.remove_backticks(refined_prompt).strip()
        self.step_end("Refining image description with LLM...")
        self.info(f"Refined prompt: {refined_prompt}")
        return refined_prompt

    def run_workflow(self, context_details: LollmsContextDetails, client: Client, callback: Callable):
        self.callback = callback  # Ensure callback is set for self.set_message_content etc.
        prompt = context_details.prompt.strip()

        # Check for TTI service
        if not self.personality.app.tti:
            self.error("No Text-to-Image (TTI) service is configured in LoLLMs. I can't generate images without it. Please configure one in Settings -> Services Zoo -> Text to image.")
            self.reset_meme_creation_state()
            return "TTI service not available."

        # Handle "new meme" command or reset keywords
        if prompt.lower() in ["new meme", "start over", "reset meme", "new_meme_concept"]:
            self.reset_meme_creation_state()
            self.set_message_content("Alright, let's start a fresh meme! What image are you thinking of this time?")
            return "" # Handled

        # Main state machine logic
        if self._current_step == "get_image_description":
            self._image_description_user = prompt
            if self.personality_config.refine_image_prompt_with_llm:
                self._image_prompt_final = self._refine_image_prompt(prompt, context_details)
            else:
                self._image_prompt_final = prompt
            
            self.set_message_content(f"Okay, I'll try to generate an image based on: \"{self._image_prompt_final}\".\nNow, what should the **TOP text** of the meme be? (Type 'none' if you don't want top text)")
            self._current_step = "get_top_text"

        elif self._current_step == "get_top_text":
            self._top_text = prompt if prompt.lower() != "none" else ""
            self.set_message_content(f"Got it. Top text: \"{self._top_text if self._top_text else '(none)'}\".\nAnd what about the **BOTTOM text**? (Type 'none' if you don't want bottom text)")
            self._current_step = "get_bottom_text"

        elif self._current_step == "get_bottom_text":
            self._bottom_text = prompt if prompt.lower() != "none" else ""
            self.set_message_content(f"Perfect. Bottom text: \"{self._bottom_text if self._bottom_text else '(none)'}\".\n\nLet me try to generate the image for: \"{self._image_prompt_final}\". This might take a moment...")
            
            self.step_start("Generating meme image...")
            try:
                # Define output path for the image
                output_dir = self.personality.lollms_paths.personal_outputs_path / "meme_builder_images"
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate a filename (can use File_Path_Generator for more complex scenarios)
                base_name = self._image_prompt_final.replace(" ","_").replace(",","").replace("'","").replace("\"","")[:30] # basic sanitize
                # Use the helper for unique filename
                output_path = find_first_available_file_path(output_dir, base_name, "png")


                generated_image_path, metadata = self.personality.app.tti.paint(
                    positive_prompt=self._image_prompt_final,
                    negative_prompt=self.personality_config.tti_negative_prompt,
                    sampler_name=self.personality_config.tti_sampler_name,
                    seed=self.personality_config.tti_seed,
                    scale=self.personality_config.tti_scale,
                    steps=self.personality_config.tti_steps,
                    width=self.personality_config.tti_width,    
                    height=self.personality_config.tti_height,
                    output_file_name=output_path.name # Just the filename, service handles path
                )

                if generated_image_path and Path(generated_image_path).exists():
                    self._image_path = Path(generated_image_path)
                    self._image_url = self.path2url(str(self._image_path))
                    self.step_end("Image generated successset_message_contenty!", status=True)
                    
                    # Display the meme
                    meme_output = "### Your Meme Is Ready!\n\n"
                    meme_output += f"**Image Prompt:** *{self._image_prompt_final}*\n"
                    meme_output += f"![Generated Meme Image]({self._image_url})\n({self._image_url})\n\n" # Display image and its local URL
                    if self._top_text:
                        meme_output += f"**Top Text:** `{self._top_text}`\n"
                    if self._bottom_text:
                        meme_output += f"**Bottom Text:** `{self._bottom_text}`\n"
                    meme_output += "\nRemember, you'll need to use an image editor to add the text to the image. You can download the image from the link above or find it in your LoLLMs outputs folder."
                    meme_output += "\n\nWant to make another one? Just tell me what image you're thinking of!"
                    self.set_message_content(meme_output)
                    self.reset_meme_creation_state() # Ready for next meme
                else:
                    self.step_end("Image generation failed or TTI service didn't return a valid path.", status=False)
                    self.error(f"Failed to generate image. The TTI service returned: {generated_image_path}. Metadata: {metadata}")
                    self.set_message_content("Oops! Something went wrong while generating the image. The TTI service might not be working correctly, or the prompt was too wild! \nMaybe try a different image description? Or check your TTI service settings.")
                    # Partially reset, keep image description if user wants to retry with different texts or minor prompt tweaks
                    self._current_step = "get_image_description" 
                    self._image_path = None # Clear path as it failed

            except Exception as e:
                self.step_end("Image generation encountered an error.", status=False)
                self.exception(f"An error occurred during image generation: {e}")
                self.set_message_content("Yikes! A technical glitch happened while trying to make the image. Please try again with a new description or check the LoLLMs logs for more details.")
                self.reset_meme_creation_state()
        
        else: # Should not happen if logic is correct
            self.warning(f"Reached an unknown state: {self._current_step}. Resetting.")
            self.reset_meme_creation_state()
            self.set_message_content("Hmm, I got a bit lost. Let's start over. What image are you thinking of for your meme?")

        return "" # Return empty string as we've handled output with self.set_message_content()

    def log_message(self, message:str):
        """Helper to add a prefix for easy log searching."""
        ASCIIColors.cyan(f"MemeBuilder: {message}")

    # You could add execute_command if you defined commands in config.yaml
    # Example:
    # def execute_command(self, command: str, parameters:list=[], client:Client=None):
    #     if command == "new_meme_concept":
    #         self.reset_meme_creation_state()
    #         self.set_message_content("Alright, new meme! What image are you picturing?")
    #         return True
    #     return False # Command not handled by this personality directly

    # Override other APScript methods if needed, e.g., settings_updated
    def settings_updated(self):
        self.info("Meme Builder settings updated.")
        # You might reload or re-initialize something if a setting change requires it.
        # For example, if you had a default style setting.