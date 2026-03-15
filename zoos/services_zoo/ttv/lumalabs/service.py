import os
import time
import requests
from pathlib import Path
from typing import List, Optional
import pipmaster as pm
if not pm.is_installed("lumaai"):
    pm.install("lumaai")
from lumaai import LumaAI
from lollms.app import LollmsApplication
from lollms.main_config import LOLLMSConfig
from lollms.config import TypedConfig
from lollms.utilities import find_next_available_filename
from lollms.service import LollmsSERVICE
from lollms.ttv import LollmsTTV
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
from ascii_colors import ASCIIColors
class LollmsLumaLabs(LollmsTTV):
    """
    LollmsLumaLabs is an implementation of LollmsTTV using LumaAI for text-to-image generation.
    Note: LumaAI currently supports image generation, so video output will be limited to single-frame representations.
    """
    
    def __init__(
            self,
            app: LollmsApplication,
            output_folder: str | Path = None
    ):
        
        # Initialize LumaAI client
        api_key = os.environ.get("LUMAAI_API_KEY")
        service_config = TypedConfig(
            ConfigTemplate([
                {"name":"api_key", "type":"str", "value":api_key, "help":"A valid Novita AI key to generate text using anthropic api"},
            ]),
            BaseConfig(config={
                "api_key": "",     # use avx2
            })
        )
        super().__init__("lumalabs", app, service_config, output_folder)
        try:
            self.client = LumaAI(auth_token=self.service_config.api_key)
        except:
            ASCIIColors.error("Couldn't create a client")
            self.client = None

    def settings_updated(self):
        try:
            self.client = LumaAI(auth_token=self.service_config.api_key)
        except:
            ASCIIColors.error("Couldn't create a client")
            self.client = None


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
        Generates a 'video' from a text prompt using LumaAI. Currently limited to a single image due to API constraints.

        Args:
            prompt (str): The text prompt describing the content.
            negative_prompt (Optional[str]): Text describing elements to avoid (not supported by LumaAI, ignored).
            model_name (str): Model name (not supported by LumaAI, ignored).
            height (int): Desired height of the output image (default 512, LumaAI may override).
            width (int): Desired width of the output image (default 512, LumaAI may override).
            steps (int): Number of inference steps (default 20, ignored by LumaAI).
            seed (int): Random seed for reproducibility (default -1, ignored by LumaAI).
            nb_frames (int): Number of frames (default None, limited to 1 due to LumaAI image-only support).
            output_dir (str | Path): Optional custom output directory.

        Returns:
            str: Path to the generated image file (single-frame 'video').
        """
        output_path = Path(output_dir) if output_dir else self.output_folder
        output_path.mkdir(exist_ok=True, parents=True)

        # Warn about unsupported features
        if negative_prompt:
            ASCIIColors.warning("Warning: LumaAI does not support negative prompts. Ignoring negative_prompt.")
        if model_name:
            ASCIIColors.warning("Warning: LumaAI does not support model selection in this implementation. Ignoring model_name.")
        if steps != 20:
            ASCIIColors.warning("Warning: LumaAI controls inference steps internally. Ignoring steps parameter.")
        if seed != -1:
            ASCIIColors.warning("Warning: LumaAI does not support seed specification. Ignoring seed.")
        if nb_frames and nb_frames > 1:
            ASCIIColors.warning("Warning: LumaAI only supports single-image generation. Generating 1 frame instead of requested nb_frames.")

        # Note: LumaAI's API (as shown) doesn't support width/height directly in the provided example,
        # but we'll include them in case the API supports it in a newer version
        generation_params = {
            "prompt": prompt,
            # Uncomment and use these if LumaAI supports them in the future:
            # "height": height,
            # "width": width,
        }

        # Create generation request
        try:
            generation = self.client.generations.image.create(**generation_params)
        except Exception as e:
            raise RuntimeError(f"Failed to initiate generation: {str(e)}")

        # Poll for completion
        completed = False
        while not completed:
            try:
                generation = self.client.generations.get(id=generation.id)
                if generation.state == "completed":
                    completed = True
                elif generation.state == "failed":
                    raise RuntimeError(f"Generation failed: {generation.failure_reason}")
                print("Dreaming...")
                time.sleep(2)
            except Exception as e:
                raise RuntimeError(f"Error polling generation status: {str(e)}")

        # Download the image
        image_url = generation.assets.image
        output_filename = find_next_available_filename(output_path, f"{generation.id}.jpg")
        
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            with open(output_filename, 'wb') as file:
                file.write(response.content)
            print(f"File downloaded as {output_filename}")
        except Exception as e:
            raise RuntimeError(f"Failed to download image: {str(e)}")

        return str(output_filename)

    def generate_video_by_frames(self, prompts: List[str], frames: List[int], negative_prompt: str, fps: int = 8, 
                                num_inference_steps: int = 50, guidance_scale: float = 6.0, 
                                seed: Optional[int] = None) -> str:
        """
        Generates a 'video' from a list of prompts. Since LumaAI only supports single images,
        this will generate the first prompt's image and return it as a static representation.
        """
        if not prompts:
            raise ValueError("Prompts list cannot be empty.")
        
        return self.generate_video(
            prompt=prompts[0],
            negative_prompt=negative_prompt,
            seed=seed if seed is not None else -1
        )

    def getModels(self):
        """
        Gets the list of models. LumaAI doesn't expose model selection, so returns a placeholder.
        """
        return ["LumaAI_Default"]