import os # For potential path manipulations if needed later
from typing import Optional, Dict, Any

# Lollms imports
from lollms.app import LollmsApplication
from lollms.personality import AIPersonality
from lollms.function_call import FunctionCall, FunctionType
from lollms.utilities import discussion_path_to_url, safe_filename
from lollms.client_session import Client

# Utility imports
from ascii_colors import trace_exception

class ImageGen(FunctionCall):
    """
    Function call handler for generating images using a configured Text-to-Image service.

    This class integrates the image generation process directly into its execute method.
    It takes prompts and image dimensions, calls the TTI service, generates the image,
    saves it to the discussion folder, and returns an HTML <img> tag string pointing
    to the generated image, formatted for the DynamicUIRenderer's media view.
    If an error occurs, it returns a plain text error message.
    """

    def __init__(self, app: LollmsApplication, client: Client):
        """
        Initializes the ImageGen function call handler.

        Args:
            app: The LollmsApplication instance.
            client: The Client session instance associated with the request.
        """
        super().__init__(
            "image_gen",
            app,
            FunctionType.CLASSIC, # Verify this type is appropriate
            client
        )

    def bind_personality(self, personality: AIPersonality) -> 'ImageGen':
        """
        Binds the specific AIPersonality instance that this function call belongs to.

        Args:
            personality: The AIPersonality instance.

        Returns:
            The ImageGen instance itself for chaining.
        """
        self.personality = personality
        return self

    def execute(self, context: Dict[str, Any], **kwargs: Any) -> str:
        """
        Executes the image generation process based on provided arguments.

        Args:
            context: The execution context dictionary (may contain message history, etc.).
                     Not directly used in this implementation but required by the base class.
            **kwargs: Keyword arguments containing the parameters defined in __init__.
                      Expected keys: 'prompt', 'negative_prompt', 'width', 'height', 'output_file_name'.

        Returns:
            An HTML string '<img src="url" class="media" alt="...">` on success,
            or a plain text error message string on failure.
        """
        # --- Parameter Extraction and Validation ---
        prompt: Optional[str] = kwargs.get("prompt")
        negative_prompt: str = kwargs.get("negative_prompt", "")
        width_arg: Any = kwargs.get("width", 1024)
        height_arg: Any = kwargs.get("height", 1024)
        output_file_name: Optional[str] = kwargs.get("output_file_name", None)

        if not self.personality:
            return "Error: ImageGen function call cannot execute without a bound personality."
        if not self.client:
            return "Error: ImageGen function call cannot execute without a client context."
        if not self.client.discussion or not self.client.discussion.discussion_folder:
             return "Error: Client discussion folder is not available."
        if not prompt:
            return "Error: The 'prompt' parameter is mandatory for image generation."

        try:
            img_width = int(width_arg)
            img_height = int(height_arg)
            if img_width <= 0 or img_height <= 0:
                 raise ValueError("Image dimensions must be positive integers.")
        except (ValueError, TypeError):
            return f"Error: Invalid image dimensions provided. Width ('{width_arg}') and height ('{height_arg}') must be positive integers."

        # --- TTI Service Check ---
        tti_service = self.app.tti
        active_tti_service_name = self.app.config.active_tti_service

        if tti_service is None:
            return f"Error: No Text-to-Image service is configured or available ('{active_tti_service_name}' is inactive or missing)."

        # --- Image Generation ---
        file_path: Optional[str] = None
        infos: Optional[Dict[str, Any]] = None # Placeholder for potential info from paint()

        self.personality.step_start(f"Painting image using {tti_service.name}...")
        try:
            # Generate a safe filename if none is provided
            if output_file_name:
                # Ensure the provided name is safe for the filesystem
                final_output_name = safe_filename(output_file_name)
            else:
                 # Create a default name based on the prompt (or fallback)
                 base_name = safe_filename(prompt[:50]) if prompt else "generated_image"
                 # Consider adding a timestamp or UUID for uniqueness if needed
                 final_output_name = f"{base_name}_{self.client.discussion.current_message.id}" # Example using message ID

            file_path, infos = tti_service.paint(
                prompt,
                negative_prompt,
                width=img_width,
                height=img_height,
                output_folder=self.client.discussion.discussion_folder,
                output_file_name=final_output_name # Pass the determined safe filename
            )

            # --- Result Processing ---
            if file_path:
                # Ensure the file path received is valid and exists (optional sanity check)
                # if not os.path.exists(file_path):
                #    self.personality.step_end("Painting image...", success=False)
                #    return f"Error: TTI service reported success but the file '{file_path}' was not found."

                file_path_str = str(file_path) # Ensure it's a string
                image_url = discussion_path_to_url(file_path_str)

                if not image_url:
                     self.personality.step_end("Painting image...", success=False)
                     return f"Error: Could not convert generated image path '{file_path_str}' to a valid URL."

                # Escape potential HTML special characters in alt text
                safe_alt_prompt = prompt.replace('"', '"').replace('<', '<').replace('>', '>')
                html_output = f'<img src="{image_url}" class="media" alt="Generated image: {safe_alt_prompt[:80]}...">'

                self.personality.step_end("Painting image...", success=True)
                return html_output
            else:
                # Handle case where paint() succeeded but returned no file path
                self.personality.step_end("Painting image...", success=False)
                error_detail = f"Info: {infos}" if infos else "No details provided."
                return f"Error: The Text-to-Image service ('{active_tti_service_name}') did not return a valid file path after generation. {error_detail}"

        except Exception as ex:
            trace_exception(ex)
            self.personality.step_end("Painting image...", success=False)
            return f"Error during image generation with '{active_tti_service_name}': {str(ex)}"

