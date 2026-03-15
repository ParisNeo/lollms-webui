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

class LollmsRunway(LollmsTTV):
    """
    LollmsRunway is an implementation of LollmsTTV using Runway AI for text-to-video generation.
    """
    
    def __init__(
            self,
            app: LollmsApplication,
            output_folder: str | Path = None
    ):
        # Initialize service_config
        api_key = os.environ.get("RUNWAY_API_KEY")
        service_config = TypedConfig(
            ConfigTemplate([
                {"name": "api_key", "type": "str", "value": api_key, "help": "A valid Runway AI API key for text-to-video generation"},
            ]),
            BaseConfig(config={
                "api_key": "",  # Default to empty if not set in env
            })
        )
        super().__init__("runway", app, service_config, output_folder)
        self.api_key = self.service_config.config["api_key"]
        if not self.api_key:
            ASCIIColors.error("Runway AI API key not provided. Please set RUNWAY_API_KEY in your environment or update the configuration.")

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
        Generates a video from a text prompt using Runway AI API.

        Args:
            prompt (str): The text prompt describing the content.
            negative_prompt (Optional[str]): Ignored (not explicitly supported).
            model_name (str): Ignored (API uses default model unless specified otherwise).
            height (int): Desired height (may be overridden by API).
            width (int): Desired width (may be overridden by API).
            steps (int): Ignored (API controls steps).
            seed (int): Ignored (not explicitly supported).
            nb_frames (int): Number of frames to estimate video length.
            output_dir (str | Path): Optional custom output directory.

        Returns:
            str: Path to the generated video file.
        """
        output_path = Path(output_dir) if output_dir else self.output_folder
        output_path.mkdir(exist_ok=True, parents=True)

        # Warn about unsupported features
        if negative_prompt:
            ASCIIColors.warning("Warning: Runway AI does not explicitly support negative prompts.")
        if model_name:
            ASCIIColors.warning("Warning: Model selection not implemented; using Runway default.")
        if steps != 20:
            ASCIIColors.warning("Warning: Runway AI controls inference steps internally.")
        if seed != -1:
            ASCIIColors.warning("Warning: Runway AI does not support seed specification in this implementation.")

        # Prepare API request
        data = {
            "prompt": prompt,
            # Add height/width if supported in future API updates
            # "height": height,
            # "width": width,
        }
        if nb_frames is not None:
            frame_rate = 8  # Assuming 8 fps as a reasonable default
            seconds = nb_frames / frame_rate
            data["duration"] = int(seconds)  # Hypothetical parameter; adjust per actual API

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        # Hypothetical API call (adjust endpoint per Runway's documentation)
        response = requests.post("https://api.runwayml.com/v1/generate_video", json=data, headers=headers)
        if response.status_code == 200:
            video_content = response.content  # Assuming direct content; adjust if URL-based
            filename = find_next_available_filename(output_path, f"runway_{prompt[:10]}.mp4")
            with open(filename, "wb") as f:
                f.write(video_content)
            return str(filename)
        else:
            raise RuntimeError(f"Failed to generate video: {response.text}")

    def getModels(self):
        """Returns available models (placeholder)."""
        return ["Runway_Gen3_Alpha_Turbo"]