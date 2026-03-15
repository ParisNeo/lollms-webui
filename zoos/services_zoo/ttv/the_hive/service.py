import os
import requests
from pathlib import Path
from typing import List, Optional
from lollms.app import LollmsApplication
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
from lollms.utilities import find_next_available_filename
from lollms.service import LollmsSERVICE
from lollms.ttv import LollmsTTV
from ascii_colors import ASCIIColors

class LollmsTheHive(LollmsTTV):
    """
    LollmsTheHive is an implementation of LollmsTTV using TheHive.ai for text-to-video generation.
    Note: Limited to 2-second videos at 512x512 resolution.
    """
    
    def __init__(
            self,
            app: LollmsApplication,
            output_folder: str | Path = None
    ):
        # Initialize service_config
        api_key = os.environ.get("THEHIVE_API_KEY")
        service_config = TypedConfig(
            ConfigTemplate([
                {"name": "api_key", "type": "str", "value": api_key, "help": "A valid TheHive.ai API key for text-to-video generation"},
            ]),
            BaseConfig(config={
                "api_key": "",  # Default to empty if not set in env
            })
        )
        super().__init__("thehive", app, service_config, output_folder)
        self.api_key = self.service_config.config["api_key"]
        if not self.api_key:
            ASCIIColors.error("TheHive.ai API key not provided. Please set THEHIVE_API_KEY in your environment or update the configuration.")

    def settings_updated(self):
        """Update the API key when settings change."""
        self.api_key = self.service_config.config["api_key"]

    def generate_video(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        model_name: str = "",
        height: int = 512,
        width: int = 512,
        steps: int = 20,
        seed: int = -1,
        nb_frames: int = None,
        output_dir: str | Path = None,
    ) -> str:
        """
        Generates a video from a text prompt using TheHive.ai API.

        Args:
            prompt (str): The text prompt (max 250 characters).
            negative_prompt (Optional[str]): Ignored (not supported).
            model_name (str): Ignored (not supported).
            height (int): Ignored (fixed at 512).
            width (int): Ignored (fixed at 512).
            steps (int): Ignored (API controls steps).
            seed (int): Ignored (not supported).
            nb_frames (int): Ignored (fixed at 16 frames for 2 seconds).
            output_dir (str | Path): Optional custom output directory.

        Returns:
            str: Path to the generated video file.
        """
        output_path = Path(output_dir) if output_dir else self.output_folder
        output_path.mkdir(exist_ok=True, parents=True)

        # Warn about unsupported features
        if negative_prompt:
            ASCIIColors.warning("Warning: TheHive.ai does not support negative prompts.")
        if model_name:
            ASCIIColors.warning("Warning: TheHive.ai does not support model selection.")
        if height != 512 or width != 512:
            ASCIIColors.warning("Warning: TheHive.ai generates videos at fixed 512x512 resolution.")
        if steps != 20:
            ASCIIColors.warning("Warning: TheHive.ai controls inference steps internally.")
        if seed != -1:
            ASCIIColors.warning("Warning: TheHive.ai does not support seed specification.")
        if nb_frames and nb_frames != 16:
            ASCIIColors.warning("Warning: TheHive.ai generates 2-second videos (16 frames at 8 fps). Ignoring nb_frames.")

        # Validate prompt length
        if len(prompt) > 250:
            raise ValueError("Prompt exceeds TheHive.ai's 250-character limit.")

        # Hypothetical API request (endpoint requires enablement from TheHive.ai)
        data = {
            "api_key": self.api_key,
            "prompt": prompt
        }
        response = requests.post("https://api.thehive.ai/v1/generate_video", json=data)
        if response.status_code == 200:
            video_url = response.json()["video_url"]  # Hypothetical response field
            video_content = requests.get(video_url).content
            filename = find_next_available_filename(output_path, f"thehive_{prompt[:10]}.mp4")
            with open(filename, "wb") as f:
                f.write(video_content)
            return str(filename)
        else:
            raise RuntimeError(f"Failed to generate video: {response.text}")

    def getModels(self):
        """Returns available models (placeholder)."""
        return ["TheHive_Default"]