# Standard library imports
from pathlib import Path
from typing import List, Optional, Dict, Any

# Lollms imports
from lollms.app import LollmsApplication
from lollms.personality import AIPersonality # Required for step feedback
from lollms.function_call import FunctionCall, FunctionType
from lollms.client_session import Client
from lollms.utilities import discussion_path_to_url # To create accessible URLs
from ascii_colors import trace_exception # For detailed error logging

class MusicGen(FunctionCall):
    """
    A Lollms function call class designed to generate music based on a textual prompt.
    It utilizes the currently loaded Text-to-Music (TTM) service within the Lollms application.
    This class follows the structure of other Lollms function calls like VideoGen.
    """
    def __init__(self, app: LollmsApplication, client: Client):
        """
        Initializes the MusicGen function call.

        Args:
            app (LollmsApplication): The main Lollms application instance, providing access
                                     to services like TTM.
            client (Client): The client session associated with this function call,
                             used for context like discussion folders.
        """
        super().__init__(
            "music_gen", # Unique identifier for this function call
            app,
            FunctionType.CLASSIC, # Standard execution type
            client=client,
            description="Generates music from a text prompt using the configured Text-to-Music (TTM) service."
        )
        # Define parameters for documentation and potential UI generation
        self.parameters: List[Dict[str, Any]] = [
            {"name": "prompt", "type": "str", "description": "The positive prompt describing the desired music (e.g., 'Epic cinematic orchestral music for a space battle')."},
            {"name": "negative_prompt", "type": "str", "description": "A prompt describing elements to avoid (e.g., 'vocals, choir, silence, low quality').", "default": ""},
            {"name": "duration_s", "type": "float", "description": "The desired duration of the generated audio in seconds.", "default": 10.0},
            {"name": "seed", "type": "int", "description": "An optional seed for reproducibility. If None, a random seed might be used.", "default": None},
            {"name": "output_file_name", "type": "str", "description": "Optional desired name for the output audio file (without extension). If None, a unique name will be generated.", "default": None}
        ]

    def execute(self, *args, **kwargs) -> str:
        """
        Executes the music generation process by calling the loaded TTM service.

        Retrieves parameters from kwargs, validates them, calls the TTM service's
        generate method, and formats the output as an HTML audio player for the UI.

        Args:
            *args: Variable length argument list (not typically used in classic function calls).
            **kwargs: Keyword arguments containing the parameters for music generation.
                      Expected keys match the 'parameters' definition in __init__.

        Returns:
            str: A message indicating the result. On success, it includes an HTML audio
                 player pointing to the generated file. On failure, it returns an error message.
        """
        # --- Parameter Extraction ---
        prompt: str = kwargs.get("prompt", "")
        negative_prompt: str = kwargs.get("negative_prompt", "")
        duration_s_str: str = str(kwargs.get("duration_s", "10.0")) # Get as string first for validation
        seed_str: Optional[str] = kwargs.get("seed") # Get as string or None
        output_file_name: Optional[str] = kwargs.get("output_file_name", None)

        # --- Input Validation ---
        if not prompt:
            return "Error: The 'prompt' parameter is mandatory for music generation."

        try:
            duration_s: float = float(duration_s_str)
            if duration_s <= 0:
                return "Error: 'duration_s' must be a positive number."
        except ValueError:
            return f"Error: Invalid value '{duration_s_str}' for 'duration_s'. It must be a number (e.g., 10.0)."

        seed: Optional[int] = None
        if seed_str is not None:
            try:
                seed = int(seed_str)
            except ValueError:
                return f"Error: Invalid value '{seed_str}' for 'seed'. It must be an integer if provided."

        # --- Service Availability Check ---
        if self.app.ttm is None:
            return "Error: No Text-to-Music (TTM) service is currently loaded or configured in Lollms."

        # --- Execution ---
        personality = self.personality # Get the personality associated with the function call
        if not personality:
            # This should ideally not happen for classic function calls initiated via UI/API
            self.app.error("MusicGen function call executed without a personality context.", client_id=self.client.client_id)
            return "Error: Internal Lollms error - Personality context not found."

        try:
            personality.step_start("Generating music (this might take a moment)...")

            # Call the generate method of the loaded TTM service
            # The TTM service itself handles the output directory based on its configuration
            # or the optional output_dir parameter if we chose to pass it.
            # We pass output_file_name if the user specified one.
            results: List[Dict[str, Any]] = self.app.ttm.generate(
                prompt=prompt,
                negative_prompt=negative_prompt,
                duration_s=duration_s,
                seed=seed,
                output_dir=self.client.discussion.discussion_folder, # Option: Force output to discussion folder
                output_file_name=output_file_name
            )

            # --- Result Processing ---
            if not results:
                personality.step_end("Generating music (this might take a moment)...", False)
                # Check TTM logs for more specific errors if possible
                return "Failed to generate music. The TTM service returned no results. Please check the Lollms console/logs for details."

            # Assume the first result is the primary one
            first_result = results[0]
            file_path_str = first_result.get("path")

            if not file_path_str:
                 personality.step_end("Generating music (this might take a moment)...", False)
                 return "Failed to generate music. The TTM service did not return a valid file path in its result."

            # Use pathlib for robust path handling
            file_path = Path(file_path_str)

            # Verify the file exists before proceeding
            if not file_path.is_file():
                personality.step_end("Generating music (this might take a moment)...", False)
                self.app.error(f"TTM service reported generating file, but it was not found at: {file_path}", client_id=self.client.client_id)
                return f"Error: Generated music file not found at the expected location ({file_path.name}). Check Lollms logs."

            personality.step_end("Generating music (this might take a moment)...")

            # Generate a web-accessible URL for the file
            url = discussion_path_to_url(file_path)
            # Determine the MIME type (important for the <audio> tag)
            # Common audio formats: audio/mpeg (MP3), audio/wav, audio/ogg, audio/aac
            # The TTM service should ideally return the format/MIME type.
            # Fallback based on extension if not provided.
            file_format = first_result.get("format", "audio/mpeg") # Default to mp3 if not specified
            if 'format' not in first_result:
                ext = file_path.suffix.lower()
                if ext == ".wav":
                    file_format = "audio/wav"
                elif ext == ".ogg":
                    file_format = "audio/ogg"
                elif ext == ".aac":
                    file_format = "audio/aac"
                # Add more mappings as needed

            # Create HTML for the audio player
            html_output = f"""<div style="width: 100%; max-width: 600px; margin: 10px auto; padding: 10px; border: 1px solid #ccc; border-radius: 5px; background-color: #f9f9f9;">
  <p style="font-weight: bold; margin-bottom: 5px;">Generated Music:</p>
  <audio controls style="width: 100%;">
    <source src="{url}" type="{file_format}">
    Your browser does not support the audio element. You can download the file <a href="{url}" download="{file_path.name}">here</a>.
  </audio>
  <p style="font-size: 0.8em; margin-top: 5px;">File: {file_path.name}</p>
</div>
"""
            # Send the HTML to the user interface
            personality.set_message_html(html_output)

            # Return a success message (useful for logging or non-UI contexts)
            return f'<audio class="media" src="{url}" alt="{file_path.stem}">'

        except Exception as ex:
            # Ensure the step indicator is removed even if an error occurs
            if personality:
                 personality.step_end("Generating music (this might take a moment)...", False)
            # Log the full exception traceback for debugging
            trace_exception(ex)
            # Return a user-friendly error message
            return f"An unexpected error occurred during music generation: {str(ex)}"

