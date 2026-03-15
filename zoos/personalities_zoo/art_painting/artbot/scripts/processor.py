# -*- coding: utf-8 -*-
"""
Personality: ArtBot
Author: ParisNeo
Description:
ArtBot is a LoLLMs personality designed to interact with users about art and generate images
using a configured Text-to-Image (TTI) backend service.
It can discuss ideas, refine prompts, select styles and resolutions (optionally automatically),
and then generate the final artwork. It supports text-to-image and image-to-image workflows.
"""
import subprocess
import re
import webbrowser
from pathlib import Path
from typing import Dict, Any, Callable, List, Tuple, Optional

from PIL import Image

# Lollms imports
from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.types import MSG_OPERATION_TYPE
from lollms.personality import APScript, AIPersonality
from lollms.utilities import PromptReshaper, discussion_path_to_url, safe_filename
from lollms.functions.prompting.image_gen_prompts import get_image_gen_prompt, get_random_image_gen_prompt
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails


# Constants for configuration keys
CONFIG_KEYS = {
    "ACTIVATE_DISCUSSION": "activate_discussion_mode",
    "EXAMPLES_METHOD": "examples_extraction_mathod",
    "NUM_EXAMPLES": "number_of_examples_to_recover",
    "PRODUCTION_TYPE": "production_type",
    # TTI specific params (some might be ignored by non-SD backends)
    "SAMPLER": "sampler_name",
    "STEPS": "steps",
    "SCALE": "scale",
    "WIDTH": "width",
    "HEIGHT": "height",
    "SEED": "seed",
    # ArtBot features
    "IMAGINE": "imagine", # Overall toggle for LLM-based prompt generation
    "BUILD_TITLE": "build_title",
    "PAINT": "paint", # Overall toggle for calling the TTI service
    "USE_FIXED_NEG": "use_fixed_negative_prompts",
    "FIXED_NEG": "fixed_negative_prompts",
    "SHOW_INFOS": "show_infos",
    "CONTINUOUS_DISCUSSION": "continuous_discussion",
    "AUTO_RESOLUTION": "automatic_resolution_selection",
    "ADD_STYLE": "add_style",
    "CONTINUE_FROM_LAST": "continue_from_last_image",
    "IMG2IMG_STRENGTH": "img2img_denoising_strength", # Note: Often called 'strength' or similar in APIs
    "RESTORE_FACES": "restore_faces", # Note: Very backend specific (e.g., A1111)
    "CAPTION_FILES": "caption_received_files",
    "THUMBNAIL_RATIO": "thumbnail_ratio", # Corrected typo
    "SKIP_GRID": "skip_grid", # Note: Grid generation is usually backend specific
    "BATCH_SIZE": "batch_size", # Note: Often handled by TTI backend config, not direct param
    "NUM_IMAGES": "num_images", # Number of sequential generations
    "MAX_PROMPT_SIZE": "max_generation_prompt_size",
    # SD Specific (kept for compatibility but should be less prominent)
    "SD_MODEL": "sd_model_name",
    "SD_ADDRESS": "sd_address"
}

class Processor(APScript):
    """
    ArtBot Personality Script Processor.
    Handles user interaction, prompt generation, and TTI calls.
    """
    def __init__(
                 self,
                 personality: AIPersonality,
                 callback: Callable[[str, int, dict], bool] = None,
                ) -> None:

        personality_config_template = ConfigTemplate(
            [
                {"name": CONFIG_KEYS["ACTIVATE_DISCUSSION"], "type":"bool","value":True,"help":"If active, ArtBot discusses first, generating images only when explicitly asked."},
                {"name": CONFIG_KEYS["EXAMPLES_METHOD"], "type":"str","value":"random","options":["random", "rag_based", "None"], "help":"Method to select prompt examples for the LLM (random, RAG-based, or none)."},
                {"name": CONFIG_KEYS["NUM_EXAMPLES"], "type":"int","value":2, "help":"Number of prompt examples to provide to the LLM."},

                {"name": CONFIG_KEYS["PRODUCTION_TYPE"], "type":"str","value":"an artwork", "options":["a photo","an artwork", "a drawing", "a painting", "a hand drawing", "a design", "a presentation asset", "a presentation background", "a game asset", "a game background", "an icon"],"help":"Target type of graphical output."},

                # Core TTI Params (Standardized where possible)
                {"name": CONFIG_KEYS["SAMPLER"], "type":"str","value":"Default", "options":["Default", "Euler a","Euler","LMS","Heun","DPM2","DPM2 a","DPM++ 2S a","DPM++ 2M","DPM++ SDE","DPM++ 2M SDE", "DPM fast", "DPM adaptive", "DPM Karras", "DPM2 Karras", "DPM2 a Karras","DPM++ 2S a Karras","DPM++ 2M Karras","DPM++ SDE Karras","DPM++ 2M SDE Karras" ,"DDIM", "PLMS", "UniPC", "DPM++ 3M SDE", "DPM++ 3M SDE Karras", "DPM++ 3M SDE Exponential"], "help":"Sampler name (backend support varies). 'Default' lets the backend decide."},
                {"name": CONFIG_KEYS["STEPS"], "type":"int","value":40, "min":1, "max":1024, "help":"Number of diffusion steps (backend support varies)."},
                {"name": CONFIG_KEYS["SCALE"], "type":"float","value":7.0, "min":0.1, "max":100.0, "help":"Guidance scale (CFG) (backend support varies)."},
                {"name": CONFIG_KEYS["WIDTH"], "type":"int","value":1024, "min":64, "max":4096, "help":"Desired image width (backend may override)."},
                {"name": CONFIG_KEYS["HEIGHT"], "type":"int","value":1024, "min":64, "max":4096, "help":"Desired image height (backend may override)."},
                {"name": CONFIG_KEYS["SEED"], "type":"int","value":-1, "help":"Generation seed (-1 for random) (backend support varies)."},

                # ArtBot Features
                {"name": CONFIG_KEYS["IMAGINE"], "type":"bool","value":True,"help":"Use LLM to generate/refine prompts."},
                {"name": CONFIG_KEYS["BUILD_TITLE"], "type":"bool","value":True,"help":"Use LLM to generate a title for the artwork."},
                {"name": CONFIG_KEYS["PAINT"], "type":"bool","value":True,"help":"Actually generate the image using the TTI service."},
                {"name": CONFIG_KEYS["USE_FIXED_NEG"], "type":"bool","value":True,"help":"Use a predefined negative prompt."},
                {"name": CONFIG_KEYS["FIXED_NEG"], "type":"str","value":"(((ugly))), (((duplicate))), ((morbid)), ((mutilated)), out of frame, extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), ((extra arms)), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), ((watermark)), ((text)), ((words)), ((signature)), ((logo)), ((robot eyes))","help":"The fixed negative prompt text."},
                {"name": CONFIG_KEYS["SHOW_INFOS"], "type":"bool","value":True,"help":"Show TTI generation metadata."},
                {"name": CONFIG_KEYS["CONTINUOUS_DISCUSSION"], "type":"bool","value":True,"help":"Include previous discussion context when generating prompts."},
                {"name": CONFIG_KEYS["AUTO_RESOLUTION"], "type":"bool","value":False,"help":"Let ArtBot attempt to choose the image resolution via LLM."},
                {"name": CONFIG_KEYS["ADD_STYLE"], "type":"bool","value":False,"help":"Let ArtBot attempt to choose a style via LLM."},

                # Image-to-Image specific
                {"name": CONFIG_KEYS["CONTINUE_FROM_LAST"], "type":"bool","value":False,"help":"Use the last generated image as input for the next generation (img2img)."},
                {"name": CONFIG_KEYS["IMG2IMG_STRENGTH"], "type":"float","value":0.75, "min":0.01, "max":1.0, "help":"Img2Img denoising strength (backend support varies)."}, # Standardized name
                {"name": CONFIG_KEYS["RESTORE_FACES"], "type":"bool","value":False,"help":"Attempt face restoration (backend specific, e.g., A1111)."},
                {"name": CONFIG_KEYS["CAPTION_FILES"], "type":"bool","value":False,"help":"Attempt to caption uploaded images using the LLM (requires multimodal model)."},

                {"name": CONFIG_KEYS["THUMBNAIL_RATIO"], "type":"int","value":2, "min":1, "max":5, "help":"Ratio for displaying thumbnails."},
                {"name": CONFIG_KEYS["NUM_IMAGES"], "type":"int","value":1, "min":1, "max":10,"help":"Number of images to generate sequentially."},
                {"name": CONFIG_KEYS["MAX_PROMPT_SIZE"], "type":"int","value":1024, "min":64, "max":personality.config["ctx_size"], "help":"Max tokens for LLM generated prompts/titles."},

                # Legacy/Backend Specific (less emphasis)
                # {"name": CONFIG_KEYS["SD_MODEL"], "type":"str","value":"", "help":"(Optional) Specific SD model name if using A1111/ComfyUI backend."},
                # {"name": CONFIG_KEYS["SD_ADDRESS"], "type":"str","value":"http://127.0.0.1:7860","help":"(Optional) Address for A1111/ComfyUI service."},
                # {"name": CONFIG_KEYS["SKIP_GRID"], "type":"bool","value":True,"help":"(Optional) Skip grid generation for backends that support it."},
                # {"name": CONFIG_KEYS["BATCH_SIZE"], "type":"int","value":1, "min":1, "max":16,"help":"(Optional) Batch size for backends that support it."},
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
                            states_list=[ # Simplified state machine for this example
                                {
                                    "name": "idle",
                                    "commands": {
                                        "help": self.help_command,
                                        "new_image": self.new_image_command,
                                        "regenerate": self.regenerate_command,
                                        "show_tti_settings": self.show_tti_settings_command, # More generic name
                                    },
                                    "default": self.handle_default_state # Route to run_workflow
                                }
                            ],
                            callback=callback
                        )
        self.current_image_paths = [] # Store paths of images generated in the current turn

    def install(self):
        super().install()
        self.personality_config.save_config() # Save defaults if installing
        self.info("ArtBot installation finished.")

    # --- State Machine Command Handlers ---
    def help_command(self, prompt: str, client: Client):
        """Provides help information."""
        help_text = """
        **ArtBot Commands:**
        - `/help`: Show this help message.
        - `/new_image`: Clear the context for generating a completely new image (discards previous image inputs).
        - `/regenerate`: Attempt to regenerate the last image(s) using the same prompts and settings.
        - `/show_tti_settings`: (If applicable) Open the settings UI for the configured TTI service (e.g., Automatic1111 web UI).

        **Interaction:**
        - Just describe the image you want!
        - Upload an image to use it as a base for the next generation (enable 'Continue from last image' if needed).
        - If 'Activate Discussion Mode' is on, ArtBot will chat until you explicitly ask it to create/generate/draw/paint.
        """
        self.full(help_text)

    def new_image_command(self, prompt: str, client: Client):
        """Clears the current image context."""
        self.current_image_paths = []
        self.personality.image_files = []
        self.info("Image context cleared. Ready for a fresh start!")

    def regenerate_command(self, prompt: str, client: Client):
        """Regenerates the last image using stored metadata."""
        metadata = client.discussion.get_metadata()
        last_positive = metadata.get("artbot_positive_prompt")
        last_negative = metadata.get("artbot_negative_prompt")
        last_title = metadata.get("artbot_title", "Regenerated Artwork")
        last_input_images = metadata.get("artbot_last_input_images", [])
        last_width = metadata.get("artbot_width", self.personality_config[CONFIG_KEYS["WIDTH"]])
        last_height = metadata.get("artbot_height", self.personality_config[CONFIG_KEYS["HEIGHT"]])

        if not last_positive:
            self.warning("No previous generation data found in this discussion to regenerate.")
            return

        # Start the summary message block
        self.step_start(f"Regenerating artwork...")
        generation_summary = f"### Regenerating: {last_title}\n"
        generation_summary += f"- **Resolution:** {last_width}x{last_height}\n"
        generation_summary += f"- **Positive Prompt:**\n```text\n{last_positive}\n```\n"
        generation_summary += f"- **Negative Prompt:**\n```text\n{last_negative}\n```\n"
        if last_input_images:
             generation_summary += f"- **Input Image(s):** {', '.join(map(Path, last_input_images))}\n"

        self.set_message_content(generation_summary) # Initial summary

        # Call the paint function
        generated_files, final_metadata = self._paint_images(
            positive_prompt=last_positive,
            negative_prompt=last_negative,
            title=last_title,
            width=last_width,
            height=last_height,
            client=client,
            input_image_paths=last_input_images
        )

        if not generated_files:
            generation_summary += "\n---\n**Status:** Regeneration Failed ❌"
            self.set_message_content(generation_summary)
            self.error("Regeneration failed.") # Log error
        else:
            generation_summary += "\n---\n**Status:** Regeneration Complete ✅"
            self.set_message_content(generation_summary) # Final summary update
            self.success("Regeneration complete!") # Log success

            # Display images in a new block
            self._display_images(generated_files, last_title)

            # Show metadata if enabled
            if self.personality_config[CONFIG_KEYS["SHOW_INFOS"]] and final_metadata:
                self.json("Regeneration Metadata", final_metadata)

        self.step_end(f"Regenerating artwork...")


    def show_tti_settings_command(self, prompt: str, client: Client):
        """Opens the TTI service's external settings UI if available."""
        if hasattr(self.personality.app.tti, 'config') and 'address' in self.personality.app.tti.config:
            try:
                tti_address = self.personality.app.tti.config['address']
                if tti_address and tti_address.startswith("http"):
                    webbrowser.open(tti_address)
                    self.info(f"Attempting to open TTI settings at: {tti_address}")
                else:
                    self.warning("TTI service address is not configured or invalid.")
            except Exception as e:
                self.error(f"Could not open TTI settings: {e}")
        else:
            self.warning("The current TTI service does not seem to have a configurable web UI address.")

    def handle_default_state(self, prompt: str, context_details: LollmsContextDetails, client: Client):
        """ Default handler for the 'idle' state, routes to the main workflow. """
        self.run_workflow(context_details=context_details, client=client, callback=self.callback)

    # --- Core Workflow ---
    def run_workflow(self, context_details: LollmsContextDetails, client: Client, callback: Callable = None):
        """
        Main entry point for processing user input.
        Orchestrates discussion, prompt generation, and image generation.
        """
        self.callback = callback
        initial_prompt = context_details.prompt
        full_context = context_details.discussion_messages

        # 1. Check TTI Service
        if not self.personality.app.tti:
            self.error("No Text-to-Image service is configured.", client_id=client.client_id)
            return

        # 2. Discussion Mode Handling
        if self.personality_config[CONFIG_KEYS["ACTIVATE_DISCUSSION"]]:
            self.step_start("Analyzing request...")
            classification = self.multichoice_question(
                question="Is the user explicitly asking to generate, create, make, draw, or paint an image, or are they just discussing ideas or asking questions?",
                possible_answers=[
                    "User is asking a question or discussing ideas.",
                    "User is explicitly requesting image generation."
                ],
                context=f"User message: '{initial_prompt}'"
            )
            self.step_end("Analyzing request...")

            if classification == 0:
                self.step_start("Generating discussion response...")
                discussion_prompt = self.build_prompt(
                    [
                        self.personality.system_full_header, self.personality.personality_conditioning,
                        "You are ArtBot, an AI assistant focused on discussing art and image generation ideas.",
                        "The user is not asking you to generate an image right now, but is discussing ideas or asking questions.",
                        "Respond helpfully and engage in the conversation about art.",
                        self.personality.discussion_header(context_details.discussion_id), full_context,
                        self.personality.user_full_header, initial_prompt,
                        self.personality.ai_full_header
                    ],
                    context_size=self.personality.config.ctx_size // 2
                )
                self.print_prompt("Discussion Prompt", discussion_prompt)
                response = self.fast_gen(discussion_prompt, max_generation_size=self.personality_config[CONFIG_KEYS["MAX_PROMPT_SIZE"]], callback=self.add_chunk_to_message_content)
                self.step_end("Generating discussion response...")
                return

            self.step("Proceeding with image generation request.")

        # 3. Prepare for Generation - Start Summary Message
        self.step_start("Preparing artwork generation...")
        generation_summary = "### Artwork Generation Plan\n"
        self.set_message_content(generation_summary)

        self.current_image_paths = []
        positive_prompt = ""
        negative_prompt = ""
        title = "Artwork by ArtBot"
        current_width = self.personality_config[CONFIG_KEYS["WIDTH"]]
        current_height = self.personality_config[CONFIG_KEYS["HEIGHT"]]
        styles = ""

        # 3.a Determine Input Images
        input_image_paths = []
        if self.personality_config[CONFIG_KEYS["CONTINUE_FROM_LAST"]] and self.personality.image_files:
             input_image_paths = [str(self.personality.image_files[-1])]
             generation_summary += f"- **Input Image:** {Path(input_image_paths[0]).name}\n"
             self.set_message_content(generation_summary)
        last_input_images_for_metadata = input_image_paths.copy()

        # 4. Prompt Generation (if 'imagine' is enabled)
        if self.personality_config[CONFIG_KEYS["IMAGINE"]]:
            self.step_start("Imagining Prompt Details...")
            generation_context = full_context if self.personality_config[CONFIG_KEYS["CONTINUOUS_DISCUSSION"]] else ""
            generation_context = self.remove_image_links(generation_context)

            # Optional: Get Styles
            if self.personality_config[CONFIG_KEYS["ADD_STYLE"]]:
                self.step_start("Selecting Style...")
                styles = self._get_styles(initial_prompt, generation_context)
                self.step_end("Selecting Style...")
                if styles:
                    generation_summary += f"- **Style(s):** {styles}\n"
                    self.set_message_content(generation_summary)

            # Optional: Get Resolution
            if self.personality_config[CONFIG_KEYS["AUTO_RESOLUTION"]]:
                self.step_start("Determining Resolution...")
                res = self._get_resolution(initial_prompt, generation_context, default_resolution=(current_width, current_height))
                current_width, current_height = res
                self.step_end("Determining Resolution...")
                generation_summary += f"- **Resolution:** {current_width}x{current_height}\n"
                self.set_message_content(generation_summary)
            else:
                generation_summary += f"- **Resolution:** {current_width}x{current_height} (Default)\n"
                self.set_message_content(generation_summary)


            # Generate Positive Prompt
            self.step_start("Generating Positive Prompt...")
            positive_prompt = self._generate_positive_prompt(initial_prompt, generation_context, styles)
            if not positive_prompt:
                 self.error("Failed to generate positive prompt.")
                 self.step_end("Generating Positive Prompt...", False)
                 self.step_end("Imagining Prompt Details...", False)
                 generation_summary += "\n---\n**Error:** Failed to generate positive prompt. Cannot proceed. ❌"
                 self.set_message_content(generation_summary)
                 return
            self.step_end("Generating Positive Prompt...")
            generation_summary += f"- **Positive Prompt:**\n```text\n{positive_prompt}\n```\n"
            self.set_message_content(generation_summary)

            # Generate Negative Prompt
            if self.personality_config[CONFIG_KEYS["USE_FIXED_NEG"]]:
                negative_prompt = self.personality_config[CONFIG_KEYS["FIXED_NEG"]]
                generation_summary += f"- **Negative Prompt:** (Fixed)\n```text\n{negative_prompt}\n```\n"
                self.set_message_content(generation_summary)
            else:
                self.step_start("Generating Negative Prompt...")
                negative_prompt = self._generate_negative_prompt(positive_prompt, generation_context, styles)
                if not negative_prompt: negative_prompt = "" # Use empty if failed
                self.step_end("Generating Negative Prompt...")
                generation_summary += f"- **Negative Prompt:**\n```text\n{negative_prompt}\n```\n"
                self.set_message_content(generation_summary)

            # Generate Title
            if self.personality_config[CONFIG_KEYS["BUILD_TITLE"]]:
                self.step_start("Generating Title...")
                title = self._generate_title(positive_prompt, negative_prompt)
                if not title: title = "Artwork by ArtBot" # Default on failure
                self.step_end("Generating Title...")
                generation_summary = generation_summary.replace("### Artwork Generation Plan", f"### {title}") # Update title
                self.set_message_content(generation_summary)

            self.step_end("Imagining Prompt Details...")
        else:
            # Use user prompt directly
            prompt_lines = initial_prompt.strip().split('\n', 1)
            positive_prompt = prompt_lines[0]
            negative_prompt = prompt_lines[1] if len(prompt_lines) > 1 else ""
            if self.personality_config[CONFIG_KEYS["USE_FIXED_NEG"]]:
                 negative_prompt = self.personality_config[CONFIG_KEYS["FIXED_NEG"]]
            title = f"Artwork based on User Prompt"
            generation_summary = generation_summary.replace("### Artwork Generation Plan", f"### {title}") # Update title
            generation_summary += f"- **Resolution:** {current_width}x{current_height} (Default)\n"
            generation_summary += f"- **Positive Prompt:** (User Provided)\n```text\n{positive_prompt}\n```\n"
            generation_summary += f"- **Negative Prompt:**\n```text\n{negative_prompt}\n```\n"
            self.set_message_content(generation_summary)
            self.step("Using user prompt directly.")


        # 5. Store Metadata
        metadata = client.discussion.get_metadata()
        metadata["artbot_positive_prompt"] = positive_prompt
        metadata["artbot_negative_prompt"] = negative_prompt
        metadata["artbot_title"] = title
        metadata["artbot_width"] = current_width
        metadata["artbot_height"] = current_height
        metadata["artbot_last_input_images"] = last_input_images_for_metadata
        client.discussion.set_metadata(metadata)

        # 6. Perform Image Generation
        if self.personality_config[CONFIG_KEYS["PAINT"]]:
            generation_summary += "\n---\n**Status:** Generating images..."
            self.set_message_content(generation_summary) # Update status
            self.step("Starting image generation process...")

            generated_files, final_metadata = self._paint_images(
                positive_prompt=positive_prompt,
                negative_prompt=negative_prompt,
                title=title,
                width=current_width,
                height=current_height,
                client=client,
                input_image_paths=input_image_paths
            )

            if not generated_files:
                generation_summary = generation_summary.replace("Generating images...", "Image Generation Failed ❌")
                self.set_message_content(generation_summary)
                self.error("Image generation failed.")
            else:
                generation_summary = generation_summary.replace("Generating images...", f"Image Generation Complete ({len(generated_files)} image(s)) ✅")
                self.set_message_content(generation_summary) # Final summary update
                self.success("Image generation complete!")
                self.current_image_paths = generated_files
                if generated_files:
                    self.personality.image_files.append(Path(generated_files[-1])) # Add last generated for next potential img2img

                # Display images in a new block
                self._display_images(generated_files, title)

                # Show metadata if enabled
                if self.personality_config[CONFIG_KEYS["SHOW_INFOS"]] and final_metadata:
                    self.json("Generation Metadata", final_metadata)

        else:
            generation_summary += "\n---\n**Status:** Image generation skipped (disabled in settings)."
            self.set_message_content(generation_summary)
            self.warning("Image generation (painting) is disabled in settings.")

        self.step_end("Preparing artwork generation...")

    # --- Helper Methods for LLM Interaction ---

    def _get_styles(self, user_prompt: str, context: str) -> str:
        # ... (no change needed in this helper) ...
        styles_list = [
            "Photorealistic", "Oil painting", "Watercolor", "Sketch", "Illustration", "Cartoon", "Comic Book",
            "Anime", "Manga", "Pixel Art", "Abstract", "Surrealism", "Impressionism", "Expressionism",
            "Art Nouveau", "Art Deco", "Minimalist", "Cyberpunk", "Steampunk", "Fantasy Art", "Sci-Fi Art",
            "Concept Art", "Architectural", "Vintage", "Retro", "3D Render", "Octane Render", "Cinematic",
            "Low Poly", "Claymation", "Graffiti", "Calligraphy", "Vector Art", "Isometric"
        ]
        styles_text = ", ".join(styles_list)

        prompt = self.build_prompt(
            [
                self.personality.system_full_header,
                f"Your task is to select one or more artistic styles from the provided list that best suit the user's request for {self.personality_config[CONFIG_KEYS['PRODUCTION_TYPE']]}.",
                "Consider the user's prompt and any relevant discussion context.",
                "Output only the comma-separated names of the selected styles.",
                
                context,
                self.personality.user_full_header,
                user_prompt,
                self.personality.ai_full_header,
                f"Available Styles: {styles_text}\nSelected Styles:"
            ],
            context_size=self.personality.config.ctx_size // 3
        )
        self.print_prompt("Style Selection Prompt", prompt)
        selected_styles = self.fast_gen(prompt, max_generation_size=100).strip()

        valid_styles = [s for s in styles_list if s.lower() in selected_styles.lower()]
        return ", ".join(valid_styles)

    def _get_resolution(self, user_prompt: str, context: str, default_resolution: Tuple[int, int]) -> Tuple[int, int]:
        # ... (no change needed in this helper) ...
        prompt = self.build_prompt(
            [
                self.personality.system_full_header,
                f"Analyze the user's request for {self.personality_config[CONFIG_KEYS['PRODUCTION_TYPE']]} and suggest an appropriate image resolution (width, height).",
                "Common resolutions are 512x512, 768x768, 1024x1024, 1024x768, 768x1024, 1536x1024, 1024x1536.",
                f"The current default is {default_resolution[0]}x{default_resolution[1]}.",
                "Output ONLY the resolution in the format `width, height` (e.g., `1024, 768`).",
                context,
                self.personality.user_full_header,
                user_prompt,
                self.personality.ai_full_header,
                "Suggested Resolution (width, height):"
            ],
            context_size=self.personality.config.ctx_size // 3
        )
        self.print_prompt("Resolution Selection Prompt", prompt)
        resolution_str = self.fast_gen(prompt, max_generation_size=20).strip()

        match = re.search(r'(\d+)\s*,\s*(\d+)', resolution_str)
        if match:
            try:
                width = int(match.group(1))
                height = int(match.group(2))
                if 64 <= width <= 4096 and 64 <= height <= 4096:
                    return width, height
            except ValueError: pass
        self.warning(f"Could not parse resolution '{resolution_str}', using default {default_resolution}.")
        return default_resolution

    def _generate_positive_prompt(self, user_prompt: str, context: str, styles: str) -> str:
        # ... (no change needed in this helper) ...
        examples_text = ""
        if self.personality_config[CONFIG_KEYS["EXAMPLES_METHOD"]] != "None":
            num_examples = self.personality_config[CONFIG_KEYS["NUM_EXAMPLES"]]
            try:
                if self.personality_config[CONFIG_KEYS["EXAMPLES_METHOD"]] == "random":
                    examples = get_random_image_gen_prompt(num_examples)
                elif self.personality_config[CONFIG_KEYS["EXAMPLES_METHOD"]] == "rag_based":
                    examples = get_image_gen_prompt(user_prompt, num_examples)
                else: examples = []
                if examples:
                    examples_text = "Follow the style of these example prompts:\n" + "\n".join([f"- {ex}" for ex in examples])
            except Exception as e: self.warning(f"Could not load prompt examples: {e}")

        prompt_parts = [
            self.personality.system_full_header,
            "You are ArtBot, an expert prompt generator for text-to-image AI.",
            f"Generate a detailed, high-quality positive prompt for creating {self.personality_config[CONFIG_KEYS['PRODUCTION_TYPE']]} based on the user's request and discussion.",
            "Incorporate descriptive details about the subject, scene, mood, lighting, and composition.",
            "Do NOT add any negative keywords here.", "Do NOT explain the prompt, just output the prompt text itself.",
        ]
        if styles: prompt_parts.append(f"The desired artistic style is: {styles}.")
        if examples_text: prompt_parts.append(examples_text)
        if context: prompt_parts.extend([context])
        prompt_parts.extend([self.personality.user_full_header, user_prompt, self.personality.ai_full_header, "Positive Prompt:"])

        llm_prompt = self.build_prompt(prompt_parts, context_size=self.config.ctx_size // 2)
        self.print_prompt("Positive Prompt Generation", llm_prompt)
        generated_prompt = self.generate(llm_prompt, max_size=self.personality_config[CONFIG_KEYS["MAX_PROMPT_SIZE"]], temperature=0.7, top_k=30, top_p=0.9)
        generated_prompt = self.remove_backticks(generated_prompt.strip())
        return generated_prompt

    def _generate_negative_prompt(self, positive_prompt: str, context: str, styles: str) -> str:
        # ... (no change needed in this helper) ...
        prompt = self.build_prompt(
            [
                self.personality.system_full_header,
                "You are ArtBot, generating negative prompts for text-to-image AI.",
                "Based on the positive prompt, user request, and discussion, list keywords to AVOID in the generated image.",
                "Focus on common issues like deformities (ugly, mutation, extra limbs/fingers), bad quality (blurry, low quality), unwanted elements (text, signature, watermark), and things contradicting the style or request.",
                "Use comma separation. Add emphasis with multiple brackets like (((word))).",
                "Do NOT explain the prompt, just output the negative keywords.",
                context,
                self.personality.user_full_header, f"Positive Prompt: {positive_prompt}",
                f"Style: {styles}" if styles else "", self.personality.ai_full_header, "Negative Prompt Keywords:"
            ],
            context_size=self.personality.config.ctx_size // 3
        )
        self.print_prompt("Negative Prompt Generation", prompt)
        generated_prompt = self.fast_gen(prompt, max_generation_size=self.personality_config[CONFIG_KEYS["MAX_PROMPT_SIZE"]] // 2, temperature=0.6).strip()
        generated_prompt = self.remove_backticks(generated_prompt)
        if "ugly" not in generated_prompt.lower(): generated_prompt += ", ugly"
        if "blurry" not in generated_prompt.lower(): generated_prompt += ", blurry"
        if "deformed" not in generated_prompt.lower(): generated_prompt += ", deformed"
        return generated_prompt.strip(', ')

    def _generate_title(self, positive_prompt: str, negative_prompt: str) -> str:
        # ... (no change needed in this helper) ...
        prompt = self.build_prompt(
            [
                self.personality.system_full_header,
                "Create a short, concise, and descriptive title (max 10 words) for an artwork based on the following prompts.",
                "Do not use quotes or explain.",
                self.personality.system_custom_header("Positive Prompt"), positive_prompt,
                self.personality.system_custom_header("Negative Prompt"), negative_prompt,
                self.personality.ai_full_header, "Artwork Title:"
            ],
             context_size= self.personality.config.ctx_size // 4
        )
        self.print_prompt("Title Generation", prompt)
        title = self.fast_gen(prompt, max_generation_size=30).strip().strip('"')
        return title

    # --- TTI Interaction ---

    def _paint_images(
        self,
        positive_prompt: str,
        negative_prompt: str,
        title: str,
        client: Client,
        input_image_paths: List[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> Tuple[List[str], Optional[Dict]]:
        """
        Calls the configured TTI service to generate images sequentially.
        Now returns generated file paths and the metadata of the *last* successful generation.
        """
        generated_files = []
        last_metadata = None # Store metadata of the last image

        width = width or self.personality_config[CONFIG_KEYS["WIDTH"]]
        height = height or self.personality_config[CONFIG_KEYS["HEIGHT"]]
        num_images = self.personality_config[CONFIG_KEYS["NUM_IMAGES"]]

        # Prepare parameters
        tti_params = {
            "positive_prompt": positive_prompt, "negative_prompt": negative_prompt,
            "sampler_name": self.personality_config[CONFIG_KEYS["SAMPLER"]],
            "seed": self.personality_config[CONFIG_KEYS["SEED"]],
            "scale": self.personality_config[CONFIG_KEYS["SCALE"]],
            "steps": self.personality_config[CONFIG_KEYS["STEPS"]],
            "width": width, "height": height,
            "output_folder": client.discussion.discussion_folder,
        }

        for i in range(num_images):
            self.step_start(f"Generating image {i+1}/{num_images}...")
            base_filename = safe_filename(f"{title}_{i+1}")
            tti_params["output_file_name"] = base_filename

            image_path: Optional[Path] = None
            metadata_or_error: Optional[Dict] = None

            try:
                if input_image_paths:
                    image_path, metadata_or_error = self.personality.app.tti.paint_from_images(
                        images=input_image_paths, **tti_params
                    )
                else:
                    image_path, metadata_or_error = self.personality.app.tti.paint(**tti_params)

                if image_path and image_path.exists():
                    self.step_end(f"Generating image {i+1}/{num_images}...", status=True)
                    generated_files.append(str(image_path))
                    last_metadata = metadata_or_error # Store metadata

                    if self.personality_config[CONFIG_KEYS["CONTINUE_FROM_LAST"]]:
                         input_image_paths = [str(image_path)] # Update for next loop iteration

                    # Update seed for next iteration if needed
                    if tti_params["seed"] == -1: pass # Keep random
                    elif tti_params["seed"] != -1: tti_params["seed"] += 1

                else:
                    error_msg = metadata_or_error.get('error', 'Unknown TTI error.') if metadata_or_error else 'Unknown TTI error.'
                    self.step_end(f"Generating image {i+1}/{num_images}...", status=False)
                    self.error(f"Failed to generate image {i+1}: {error_msg}")
                    # Optionally break on first failure:
                    # break

            except Exception as e:
                self.step_end(f"Generating image {i+1}/{num_images}...", status=False)
                self.exception(f"An unexpected error occurred during TTI call for image {i+1}: {e}")
                # Optionally break on first failure:
                # break

        return generated_files, last_metadata # Return paths and last metadata


    def _display_images(self, generated_files: List[str], title: str):
        """ Displays the generated images in a new UI message block. """
        if not generated_files:
            return

        output_html = ""
        for file_path_str in generated_files:
            try:
                file_path = Path(file_path_str)
                img_url = discussion_path_to_url(str(file_path)) # Assuming discussion_path_to_url handles client/personality context
                # Simple image tag display
                thumb_w = self.personality_config[CONFIG_KEYS["WIDTH"]] / self.personality_config[CONFIG_KEYS["THUMBNAIL_RATIO"]]
                thumb_h = self.personality_config[CONFIG_KEYS["HEIGHT"]] / self.personality_config[CONFIG_KEYS["THUMBNAIL_RATIO"]]
                output_html += f'<img src="{img_url}" alt="{title}" style="max-width: {thumb_w}px; max-height:{thumb_h}px; margin: 5px; border: 1px solid #ccc; display: inline-block;">\n'
            except Exception as e:
                 self.warning(f"Could not generate display for image {file_path_str}: {e}")


        if output_html:
            self.new_message("", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI)
            self.set_message_html(f"<div style='text-align:center;'>{output_html}</div>")

    # --- File Handling ---

    def add_file(self, path: Path, client: Client, callback: Callable = None) -> bool:
        # ... (No changes needed here compared to previous version) ...
        if not path.exists():
            self.error(f"File not found: {path}")
            return False

        file_type = self.get_file_type(path)
        if file_type != "image":
            self.warning(f"ArtBot currently only supports image files. Received: {file_type}")
            return super().add_file(path, client, callback=callback)

        self.new_message("", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI)

        try:
            self.personality.image_files.append(path)
            self.info(f"Image file added: {path.name}")

            file_infos = self.personality.app.get_file_infos(str(path))
            img_url = file_infos.url # Use URL from file infos
            display_html = f'<b>Added Image:</b> {path.name}<br><img src="{img_url}" style="max-width: 256px; max-height: 256px; border: 1px solid #ccc;">'
            self.add_html(display_html)

            if self.personality_config[CONFIG_KEYS["CAPTION_FILES"]]:
                if hasattr(self.personality.model, 'interrogate') and callable(getattr(self.personality.model, 'interrogate')):
                     self.step_start("Captioning image...")
                     try:
                         img = Image.open(path).convert("RGB")
                         captions = self.personality.model.interrogate([img])
                         caption = captions[0] if isinstance(captions, list) and captions else str(captions)
                         self.step_end("Captioning image...")
                         self.info(f"Image Caption: {caption}")
                     except Exception as e:
                         self.step_end("Captioning image...", False)
                         self.error(f"Failed to caption image: {e}")
                else:
                     self.warning("Captioning enabled, but the current LLM binding does not support image interrogation.")

            return True

        except Exception as e:
            self.error(f"Error processing uploaded file {path.name}: {e}")
            return False

    # --- Custom Request Handler ---
    async def handle_request(self, data: dict, client: Client) -> Dict[str, Any]:
        # ... (No changes needed here compared to previous version) ...
        operation = data.get("name")
        image_url_path = data.get("image_url_path") # Expecting URL path like /discussions/.../image.png

        if not operation or not image_url_path:
            return {"status": False, "error": "Missing 'name' or 'image_url_path' in request."}

        # Convert URL path back to system path (needs robust handling)
        try:
            file_infos = self.personality.app.get_file_infos_from_url(image_url_path)
            if not file_infos or not file_infos.exists:
                 raise FileNotFoundError(f"Could not resolve image path from URL: {image_url_path}")
            image_path = Path(file_infos.path)

        except Exception as e:
            self.error(f"Error resolving image path: {e}")
            return {"status": False, "error": f"Could not find image file: {image_url_path}"}

        ASCIIColors.info(f"Handling request '{operation}' for image: {image_path}")

        if operation == "variate":
            metadata = client.discussion.get_metadata()
            positive_prompt = metadata.get("artbot_positive_prompt", "Create a variation.")
            negative_prompt = metadata.get("artbot_negative_prompt", "")
            width = metadata.get("artbot_width", self.personality_config[CONFIG_KEYS["WIDTH"]])
            height = metadata.get("artbot_height", self.personality_config[CONFIG_KEYS["HEIGHT"]])
            title = f"Variation of {image_path.stem}"

            # Start summary message
            self.step_start(f"Generating variation for {image_path.name}...")
            generation_summary = f"### Variation: {title}\n"
            generation_summary += f"- **Resolution:** {width}x{height}\n"
            generation_summary += f"- **Positive Prompt:**\n```text\n{positive_prompt}\n```\n"
            generation_summary += f"- **Negative Prompt:**\n```text\n{negative_prompt}\n```\n"
            generation_summary += f"- **Input Image:** {image_path.name}\n"
            generation_summary += "\n---\n**Status:** Generating variation..."
            self.set_message_content(generation_summary)

            generated_files, final_metadata = self._paint_images(
                positive_prompt=positive_prompt,
                negative_prompt=negative_prompt,
                title=title,
                client=client,
                width=width,
                height=height,
                input_image_paths=[str(image_path)]
            )

            if generated_files:
                generation_summary = generation_summary.replace("Generating variation...", f"Variation Complete ({len(generated_files)} image(s)) ✅")
                self.set_message_content(generation_summary)
                self._display_images(generated_files, title)
                if self.personality_config[CONFIG_KEYS["SHOW_INFOS"]] and final_metadata:
                    self.json("Variation Metadata", final_metadata)
                return {"status": True, "message": "Image variation generated."}
            else:
                generation_summary = generation_summary.replace("Generating variation...", "Variation Failed ❌")
                self.set_message_content(generation_summary)
                return {"status": False, "error": "Variation generation failed."}

        elif operation == "set_as_input":
            self.personality.image_files = [image_path]
            self.info(f"Set {image_path.name} as the input for the next generation. Ensure 'Continue from last image' is enabled if you want img2img.")
            return {"status": True, "message": f"{image_path.name} set as input."}

        else:
            self.warning(f"Unknown operation requested: {operation}")
            return {"status": False, "error": f"Unknown operation: {operation}"}

    # --- Utility Methods ---

    def print_prompt(self, title: str, prompt: str):
        # ... (no change needed) ...
        ASCIIColors.red(f"--- {title} ---", end="")
        print()
        ASCIIColors.yellow(prompt)
        ASCIIColors.red("--- End Prompt ---", end="")
        print()

    def remove_image_links(self, markdown_text: str) -> str:
        # ... (no change needed) ...
        return re.sub(r"!\[.*?\]\(.*?\)", "", markdown_text)

    def remove_backticks(self, text: str) -> str:
        # ... (no change needed) ...
        if text.startswith("```") and text.endswith("```"): return text[3:-3].strip()
        if text.startswith("`") and text.endswith("`"): return text[1:-1].strip()
        return text

    def get_css(self):
        # ... (no change needed) ...
        return '<link rel="stylesheet" href="/personalities/art/artbot/assets/tailwind.css">'