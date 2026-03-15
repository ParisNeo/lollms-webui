# Title LollmsMidjourney
# Licence: Apache 2.0
# Author : Paris Neo


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
from typing import List, Dict, Any

from ascii_colors import ASCIIColors, trace_exception
from lollms.paths import LollmsPaths
from lollms.utilities import PackageManager, find_next_available_filename
from lollms.tti import LollmsTTI
import subprocess
import shutil
from tqdm import tqdm

import os
import requests
from PIL import Image


MIDJOURNEY_API_URL = "https://api.imaginepro.ai/api/v1/nova"



def split_image(file_path, folder_path, i):
    with Image.open(file_path) as img:
        width, height = img.size
        
        # Calculate the size of each quadrant
        quad_width = width // 2
        quad_height = height // 2
        
        quadrants = [
            (0, 0, quad_width, quad_height),
            (quad_width, 0, width, quad_height),
            (0, quad_height, quad_width, height),
            (quad_width, quad_height, width, height)
        ]
        
        split_paths = []
        for index, box in enumerate(quadrants):
            quadrant = img.crop(box)
            split_path = os.path.join(folder_path, f"midjourney_{i}_{index+1}.png")
            quadrant.save(split_path)
            split_paths.append(split_path)
        
        return split_paths

class LollmsMidjourney(LollmsTTI):
    def __init__(self, app, output_folder:str|Path=None):
        """
        Initializes the LollmsDalle binding.

        Args:
            api_key (str): The API key for authentication.
            output_folder (Path|str):  The output folder where to put the generated data
        """
        # Check for the MIDJOURNEY_KEY environment variable if no API key is provided
        api_key = os.getenv("MIDJOURNEY_KEY","")
        service_config = TypedConfig(
            ConfigTemplate([
                {
                    "name": "api_key",
                    "type": "str",
                    "value": api_key,
                    "help": "A valid API key for Midjourney, used to access the text generation service via the Anthropic API."
                },
                {
                    "name": "timeout",
                    "type": "int",
                    "value": 300,
                    "help": "The maximum time (in seconds) to wait for a response from the API before timing out."
                },
                {
                    "name": "retries",
                    "type": "int",
                    "value": 2,
                    "help": "The number of times to retry the request if it fails or times out."
                },
                {
                    "name": "interval",
                    "type": "int",
                    "value": 1,
                    "help": "The time interval (in seconds) between retry attempts."
                }        
            ]),
            BaseConfig(config={
                "api_key": "",     # use avx2
            })
        )

        super().__init__("midjourney", app, service_config)
        self.output_folder = output_folder

        self.settings_updated()
        
    def settings_updated(self):
        self.session = requests.Session()
        self.headers = {
            "Authorization": f"Bearer {self.service_config.api_key}",
            "Content-Type": "application/json"
        }

    def send_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Send a prompt to the MidJourney API to generate an image.

        Args:
            prompt (str): The prompt for image generation.

        Returns:
            Dict[str, Any]: The response from the API.
        """
        url = f"{MIDJOURNEY_API_URL}/imagine"
        payload = {"prompt": prompt}
        response = self.session.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def check_progress(self, message_id: str) -> Dict[str, Any]:
        """
        Check the progress of the image generation.

        Args:
            message_id (str): The message ID from the initial request.

        Returns:
            Dict[str, Any]: The response from the API.
        """
        url = f"{MIDJOURNEY_API_URL}/message/{message_id}"
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def upscale_image(self, message_id: str, button: str) -> Dict[str, Any]:
        """
        Upscale the generated image.

        Args:
            message_id (str): The message ID from the initial request.
            button (str): The button action for upscaling.

        Returns:
            Dict[str, Any]: The response from the API.
        """
        url = f"{MIDJOURNEY_API_URL}/button"
        payload = {"messageId": message_id, "button": button}
        response = self.session.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def send_prompt_with_retry(self, prompt: str, retries: int = 3) -> Dict[str, Any]:
        """
        Send a prompt to the MidJourney API with retry mechanism.

        Args:
            prompt (str): The prompt for image generation.
            retries (int): Number of retry attempts.

        Returns:
            Dict[str, Any]: The response from the API.
        """
        for attempt in range(retries):
            try:
                return self.send_prompt(prompt)
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    ASCIIColors.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(2 ** attempt)
                else:
                    ASCIIColors.error(f"All {retries} attempts failed.")
                    raise e

    def poll_progress(self, message_id: str, timeout: int = 300, interval: int = 5) -> Dict[str, Any]:
        """
        Poll the progress of the image generation until it's done or timeout.

        Args:
            message_id (str): The message ID from the initial request.
            timeout (int): The maximum time to wait for the image generation.
            interval (int): The interval between polling attempts.

        Returns:
            Dict[str, Any]: The response from the API.
        """
        start_time = time.time()
        with tqdm(total=100, desc="Image Generation Progress", unit="%") as pbar:
            while time.time() - start_time < timeout:
                progress_response = self.check_progress(message_id)
                if progress_response.get("status") == "DONE":
                    pbar.update(100 - pbar.n)  # Ensure the progress bar is complete
                    print(progress_response)
                    return progress_response
                elif progress_response.get("status") == "FAIL":
                    ASCIIColors.error("Image generation failed.")
                    return {"error": "Image generation failed"}

                progress = progress_response.get("progress", 0)
                pbar.update(progress - pbar.n)  # Update the progress bar
                time.sleep(interval)
        
        ASCIIColors.error("Timeout while waiting for image generation.")
        return {"error": "Timeout while waiting for image generation"}



    def download_image(self, uri, folder_path, split=False):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        i = 1
        while True:
            file_path = os.path.join(folder_path, f"midjourney_{i}.png")
            if not os.path.exists(file_path):
                break
            i += 1
        
        response = requests.get(uri)
        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"Image downloaded and saved as {file_path}")
            
            if split:
                return split_image(file_path, folder_path, i)
            else:
                return [file_path]
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
            return None

    def get_nearest_aspect_ratio(self, width: int, height: int) -> str:
        # Define the available aspect ratios
        aspect_ratios = {
            "1:2": 0.5,
            "2:3": 0.6667,
            "3:4": 0.75,
            "4:5": 0.8,
            "1:1": 1,
            "5:4": 1.25,
            "4:3": 1.3333,
            "3:2": 1.5,
            "16:9": 1.7778,
            "7:4": 1.75,
            "2:1": 2
        }

        # Calculate the input aspect ratio
        input_ratio = width / height

        # Find the nearest aspect ratio
        nearest_ratio = min(aspect_ratios.items(), key=lambda x: abs(x[1] - input_ratio))

        # Return the formatted string
        return f"--ar {nearest_ratio[0]}"
   
    def paint(
                self,
                positive_prompt,
                negative_prompt,
                sampler_name="Euler",
                seed=-1,
                scale=7.5,
                steps=20,
                img2img_denoising_strength=0.9,
                width=512,
                height=512,
                restore_faces=True,
                output_path=None
                ):
        if output_path is None:
            output_path = self.output_path

        try:
            # Send prompt and get initial response
            positive_prompt += self.get_nearest_aspect_ratio(width, height)
            initial_response = self.send_prompt_with_retry(positive_prompt, self.service_config.retries)
            message_id = initial_response.get("messageId")
            if not message_id:
                raise ValueError("No messageId returned from initial prompt")

            # Poll progress until image generation is done
            progress_response = self.poll_progress(message_id, self.service_config.timeout, self.service_config.interval)
            if "error" in progress_response:
                raise ValueError(progress_response["error"])
            
            if width<=1024:
                file_names = self.download_image(progress_response["uri"], output_path, True)
                
                return file_names[0], {"prompt":positive_prompt, "negative_prompt":negative_prompt}

            # Upscale the generated image
            upscale_response = self.upscale_image(message_id, "U1")
            message_id = upscale_response.get("messageId")
            if not message_id:
                raise ValueError("No messageId returned from initial prompt")

            # Poll progress until image generation is done
            progress_response = self.poll_progress(message_id, self.service_config.timeout, self.service_config.interval)
            if "error" in progress_response:
                raise ValueError(progress_response["error"])
            
            file_name = self.download_image(progress_response["uri"], output_path)
            return file_name, {"prompt":positive_prompt, "negative_prompt":negative_prompt}

        except Exception as e:
            trace_exception(e)
            ASCIIColors.error(f"An error occurred: {e}")
            return "", {"prompt":positive_prompt, "negative_prompt":negative_prompt}
    
    @staticmethod
    def get(app:LollmsApplication):
        return LollmsMidjourney