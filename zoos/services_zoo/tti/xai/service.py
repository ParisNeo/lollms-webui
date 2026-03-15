# Title LollmsXAI
# Licence: Apache 2.0
# Author : Paris Neo
# Adapted from LollmsNovitaAi

from pathlib import Path
import sys
from lollms.app import LollmsApplication
from lollms.paths import LollmsPaths
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
import time
import io
import sys
import requests
import os
import base64
import subprocess
import time
import json
import platform
from dataclasses import dataclass
from PIL import Image, PngImagePlugin
from enum import Enum
from typing import List, Dict, Tuple
import random
from ascii_colors import ASCIIColors, trace_exception
from lollms.paths import LollmsPaths
from lollms.utilities import PackageManager, find_next_available_filename
from lollms.tti import LollmsTTI
import subprocess
import shutil
from tqdm import tqdm
import threading
from io import BytesIO
import os
import pipmaster as pm
pm.install_if_missing("openai")
import openai

class LollmsXAI(LollmsTTI):
    def __init__(self, app: LollmsApplication, output_folder: str | Path = None, api_key: str = None):
        """
        Initializes the LollmsXAI binding.

        Args:
            app (LollmsApplication): The LollmsApplication instance.
            output_folder (Path|str):  The output folder where to put the generated data. Defaults to LollmsPaths.outputs_path / "xai".
            api_key (str, optional): The xAI API key. If None, tries to read from XAI_API_KEY environment variable.
        """
        # Try to get the API key from environment variable if not provided
        if api_key is None:
            api_key = os.getenv("XAI_API_KEY", "")

        # Define the configuration template
        service_config = TypedConfig(
            ConfigTemplate([
                {"name": "api_key", "type": "str", "value": api_key, "help": "A valid xAI API key."},
                {"name": "n", "type": "int", "value": 1, "min": 1, "max": 10, "help": "Number of images to generate (1-10). Note: The paint function currently saves only the first image."},
                {"name": "response_format", "type": "str", "value": "url", "options": ["url", "b64_json"], "help": "Format in which the image is returned ('url' or 'b64_json')."},
                # Note: xAI API does not support size, style, quality, steps, guidance, seed, negative prompt etc. at the moment.
                # The model is fixed to 'grok-2-image'.
            ]),
            BaseConfig(config={
                "api_key": api_key,
            })
        )

        output_folder_path = app.lollms_paths.personal_outputs_path / "xai" if output_folder is None else Path(output_folder)
        output_folder_path.mkdir(parents=True, exist_ok=True)

        super().__init__("xai", app, service_config, output_folder_path)
        self.api_key = self.service_config.api_key
        self.client = None # Client will be initialized when needed


    def settings_updated(self):
        """Called when the configuration is updated."""
        self.api_key = self.service_config.api_key
        self.client = None # Reset client so it's recreated with the new key if needed


    def _initialize_client(self):
        """Initializes the OpenAI client for xAI API."""
        if not self.api_key:
            raise ValueError("xAI API key is not set. Please configure it in the binding settings or set the XAI_API_KEY environment variable.")
        if self.client is None:
            try:
                self.client = openai.OpenAI(base_url="https://api.x.ai/v1", api_key=self.api_key)
            except Exception as e:
                trace_exception(e)
                raise Exception(f"Failed to initialize xAI client. Error: {e}")


    def download_image(self, image_url: str, save_path: Path) -> None:
        """
        Downloads the generated image from the provided URL and saves it to the specified path.

        Args:
            image_url (str): The URL of the image to download.
            save_path (Path): The path where the image will be saved (including filename and extension).
        """
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors

            with open(save_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            ASCIIColors.green(f"Image downloaded successfully to: {save_path}")
        except requests.exceptions.RequestException as e:
            trace_exception(e)
            raise Exception(f"Failed to download image from URL: {image_url}. Error: {e}")
        except Exception as e:
            trace_exception(e)
            raise Exception(f"An unexpected error occurred while downloading the image: {e}")

    def save_base64_image(self, b64_json: str, save_path: Path) -> None:
        """
        Decodes a base64 encoded image string and saves it to the specified path.

        Args:
            b64_json (str): The base64 encoded image string.
            save_path (Path): The path where the image will be saved (including filename and extension).
        """
        try:
            # Ensure the path has the correct extension (jpg for xAI)
            if save_path.suffix.lower() != ".jpg":
                ASCIIColors.warning(f"Forcing .jpg extension for xAI output: {save_path.stem}.jpg")
                save_path = save_path.with_suffix(".jpg")

            # Assume format is 'data:image/jpeg;base64,...' or just the base64 part
            if ',' in b64_json:
                header, encoded_data = b64_json.split(',', 1)
            else:
                encoded_data = b64_json # Assume it's just the data if no header

            image_data = base64.b64decode(encoded_data)
            with open(save_path, "wb") as file:
                file.write(image_data)
            ASCIIColors.green(f"Image saved successfully from base64 data to: {save_path}")
        except base64.binascii.Error as e:
            trace_exception(e)
            raise Exception(f"Failed to decode base64 string. Error: {e}")
        except Exception as e:
            trace_exception(e)
            raise Exception(f"An unexpected error occurred while saving the base64 image: {e}")

    def paint(
        self,
        positive_prompt: str,
        negative_prompt: str = "", # xAI API does not support negative prompts, ignored.
        sampler_name: str = None, # Ignored
        seed: int = None,         # Ignored
        scale: float = None,      # Ignored
        steps: int = None,        # Ignored
        width: int = 512,         # Ignored (xAI does not support size customization)
        height: int = 512,        # Ignored
        output_folder: str | Path = None,
        output_file_name: str = None
    ) -> Tuple[Path | None, Dict | None]:
        """
        Generates an image using the xAI API based on a textual prompt.

        Args:
            positive_prompt (str): The description of the image to generate.
            negative_prompt (str): Ignored by xAI API.
            sampler_name (str, optional): Ignored.
            seed (int, optional): Ignored.
            scale (float, optional): Ignored.
            steps (int, optional): Ignored.
            width (int, optional): Ignored.
            height (int, optional): Ignored.
            output_folder (str | Path, optional): The folder to save the output image. Defaults to the binding's output folder.
            output_file_name (str, optional): The desired filename for the output image (without extension).

        Returns:
            Tuple[Path | None, Dict | None]: A tuple containing the path to the generated image (or None if failed)
                                            and a dictionary containing metadata (including the revised prompt) or an error message.
        """
        if not positive_prompt:
            return None, {"error": "Positive prompt cannot be empty."}

        if negative_prompt:
             ASCIIColors.warning("xAI binding does not support negative prompts. The negative prompt will be ignored.")
        if width != 512 or height != 512:
             ASCIIColors.warning("xAI binding does not support custom image dimensions. The default size will be used.")
        if sampler_name or seed or scale or steps:
             ASCIIColors.warning("xAI binding does not support sampler, seed, scale, or steps parameters. They will be ignored.")


        try:
            self._initialize_client() # Ensure client is ready

            num_images = self.service_config.n
            response_format = self.service_config.response_format

            if num_images > 1:
                 ASCIIColors.info(f"Requesting {num_images} images from xAI, but only the first one will be saved by this function.")


            # Make the API call
            
            ASCIIColors.info(f"Generating image with prompt: {positive_prompt}")
            start_time = time.time()
            response = self.client.images.generate(
                model="grok-2-image",  # Fixed model for xAI image generation
                prompt=positive_prompt[:1024],
                n=num_images,
                response_format=response_format
            )
            end_time = time.time()
            ASCIIColors.info(f"xAI image generation took {end_time - start_time:.2f} seconds.")

            # Process the response
            if not response.data:
                return None, {"error": "xAI API returned no image data."}

            # --- Handle output path ---
            output_path = Path(output_folder) if output_folder else self.output_folder
            output_path.mkdir(parents=True, exist_ok=True)

            # Define filename (use .jpg as xAI generates JPGs)
            if output_file_name:
                # Ensure it has .jpg extension
                base_name = Path(output_file_name).stem
                file_path = output_path / f"{base_name}.jpg"
            else:
                file_path = find_next_available_filename(output_path, "img_xai_", "jpg")

            # --- Save the first image ---
            first_image_data = response.data[0]
            saved_path = None
            metadata = {
                "positive_prompt": positive_prompt,
                "revised_prompt": getattr(first_image_data, 'revised_prompt', 'N/A'),
                "model": "grok-2-image",
                "response_format": response_format,
                "requested_n": num_images,
                "saved_image_index": 0 # We are saving the first image
            }

            if response_format == "url":
                image_url = getattr(first_image_data, 'url', None)
                if image_url:
                    self.download_image(image_url, file_path)
                    saved_path = file_path
                else:
                    return None, {"error": "xAI API returned response format 'url' but no URL was found."}
            elif response_format == "b64_json":
                b64_data = getattr(first_image_data, 'b64_json', None)
                if b64_data:
                    self.save_base64_image(b64_data, file_path)
                    saved_path = file_path # Use the potentially corrected path from save_base64_image
                else:
                    return None, {"error": "xAI API returned response format 'b64_json' but no base64 data was found."}
            else:
                 return None, {"error": f"Unsupported response format received: {response_format}"}

            return saved_path, metadata

        except openai.APIConnectionError as e:
            trace_exception(e)
            return None, {"error": f"xAI API Connection Error: {e}"}
        except openai.AuthenticationError as e:
            trace_exception(e)
            return None, {"error": f"xAI API Authentication Error: Invalid API Key? {e}"}
        except openai.RateLimitError as e:
            trace_exception(e)
            return None, {"error": f"xAI API Rate Limit Error: {e}"}
        except openai.BadRequestError as e:
            trace_exception(e)
            # Try to parse more detailed error if available
            error_details = str(e)
            try:
                 # Attempt to parse the response body if it's JSON-like
                 import json
                 body = getattr(e, 'response', None)
                 if body and hasattr(body, 'text'):
                      err_json = json.loads(body.text)
                      if 'error' in err_json and 'message' in err_json['error']:
                           error_details = err_json['error']['message']
            except Exception:
                 pass # Keep original error if parsing fails
            return None, {"error": f"xAI API Bad Request Error: {error_details}"}
        except openai.APIError as e:
            trace_exception(e)
            return None, {"error": f"xAI API Error: {e}"}
        except Exception as e:
            trace_exception(e)
            return None, {"error": f"An unexpected error occurred: {e}"}


    def paint_from_images(self, positive_prompt: str, images: List[str], negative_prompt: str = "") -> Tuple[Path | None, Dict | None]:
        """
        Image-to-image generation is not supported by the xAI /v1/images/generations endpoint.
        """
        ASCIIColors.warning("xAI binding does not support image-to-image generation via this endpoint.")
        # Or raise NotImplementedError("xAI binding does not support image-to-image generation")
        pass # Or return an empty list or raise an error


    @staticmethod
    def get(app: LollmsApplication):
        # This static method is used by Lollms to get the binding class
        return LollmsXAI