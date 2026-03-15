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

class LollmsStableDiffusion(LollmsTTV):
    """
    LollmsStableDiffusion is an implementation of LollmsTTV using Stable Diffusion API for text-to-video generation.
    """
    
    def __init__(
            self,
            app: LollmsApplication,
            output_folder: str | Path = None
    ):
        # Initialize service_config
        api_key = os.environ.get("STABLEDIFFUSION_API_KEY")
        service_config = TypedConfig(
            ConfigTemplate([
                {"name": "api_key", "type": "str", "value": api_key, "help": "A valid Stable Diffusion API key for text-to-video generation"},
            ]),
            BaseConfig(config={
                "api_key": "",  # Default to empty if not set in env
            })
        )
        super().__init__("stable_diffusion", app, service_config, output_folder)
        self.api_key = self.service_config.config["api_key"]
        if not self.api_key:
            ASCIIColors.error("Stable Diffusion API key not provided. Please set STABLEDIFFUSION_API_KEY in your environment or update the configuration.")

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
        Generates a video from a text prompt using Stable Diffusion API.

        Args:
            prompt (str): The text prompt describing the content.
            negative_prompt (Optional[str]): Text describing elements to avoid.
            model_name (str): Ignored in this implementation.
            height (int): Ignored (API controls resolution).
            width (int): Ignored (API controls resolution).
            steps (int): Ignored (API controls steps).
            seed (int): Ignored (API does not support seed).
            nb_frames (int): Number of frames to determine video length.
            output_dir (str | Path): Optional custom output directory.

        Returns:
            str: Path to the generated video file.
        """
        output_path = Path(output_dir) if output_dir else self.output_folder
        output_path.mkdir(exist_ok=True, parents=True)

        # Warn about unsupported features
        if model_name:
            ASCIIColors.warning("Warning: Stable Diffusion API does not support model selection in this implementation.")
        if height != 512 or width != 512:
            ASCIIColors.warning("Warning: Stable Diffusion API controls resolution internally.")
        if steps != 20:
            ASCIIColors.warning("Warning: Stable Diffusion API controls inference steps internally.")
        if seed != -1:
            ASCIIColors.warning("Warning: Stable Diffusion API does not support seed specification.")

        # Prepare API request
        data = {
            "key": self.api_key,
            "prompt": prompt,
            "negative_prompt": negative_prompt if negative_prompt else "",
            "scheduler": "UniPCMultistepScheduler",
        }
        if nb_frames is not None:
            frame_rate = 8  # Assuming 8 fps as a reasonable default
            seconds = nb_frames / frame_rate
            data["seconds"] = int(seconds)
        else:
            data["seconds"] = 2  # Default to 2 seconds

        # Make API call
        response = requests.post("https://stablediffusionapi.com/api/v5/text2video", json=data)
        if response.status_code == 200:
            video_url = response.json()["output"][0]
            video_content = requests.get(video_url).content
            filename = find_next_available_filename(output_path, f"stable_diffusion_{prompt[:10]}.mp4")
            with open(filename, "wb") as f:
                f.write(video_content)
            return str(filename)
        else:
            raise RuntimeError(f"Failed to generate video: {response.text}")

    def getModels(self):
        """Returns available models (placeholder as API doesn't expose this)."""
        return ["StableDiffusion_Default"]