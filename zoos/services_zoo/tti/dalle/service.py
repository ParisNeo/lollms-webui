# Title LollmsDalle
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
import threading
from io import BytesIO
import os
import pipmaster as pm
if not pm.is_installed("openai"):
    pm.install("openai")
import openai


class LollmsDalle(LollmsTTI):
    def __init__(self, app, output_folder:str|Path=None):
        """
        Initializes the LollmsDalle binding.

        Args:
            api_key (str): The API key for authentication.
            output_folder (Path|str):  The output folder where to put the generated data
        """
        # Check for the OPENAI_KEY environment variable if no API key is provided
        api_key = os.getenv("OPENAI_KEY","")
        service_config = TypedConfig(
            ConfigTemplate([
                {"name":"api_key", "type":"str", "value":api_key, "help":"A valid Open AI key to generate text using anthropic api"},
                {"name":"generation_engine", "type":"str", "value":"dall-e-3", "options":["dall-e-2","dall-e-3"], "help":"The engine to be used"},
            ]),
            BaseConfig(config={
                "api_key": "",     # use avx2
            })
        )

        super().__init__("dall-e", app, service_config, output_folder)

    def settings_updated(self):
        pass

    def paint(
                self,
                positive_prompt,
                negative_prompt,
                sampler_name="Euler",
                seed=None,
                scale=None,
                steps=None,
                width=None,
                height=None,
                output_folder=None,
                output_file_name=None
                ):
        if output_folder is None:
            output_folder = self.output_folder
        generation_engine = self.service_config.generation_engine
        openai.api_key = self.service_config.api_key
        if generation_engine=="dall-e-2":
            supported_resolutions = [
                [512, 512],
                [1024, 1024],
            ]
            # Find the closest resolution
            closest_resolution = min(supported_resolutions, key=lambda res: abs(res[0] - width) + abs(res[1] - height))
            
        else:
            supported_resolutions = [
                [1024, 1024],
                [1024, 1792],
                [1792, 1024]
            ]
            # Find the closest resolution
            if width>height:
                closest_resolution = [1792, 1024]
            elif width<height: 
                closest_resolution = [1024, 1792]
            else:
                closest_resolution = [1024, 1024]


        # Update the width and height
        width = closest_resolution[0]
        height = closest_resolution[1]                    


        response = openai.images.generate(
            model=generation_engine,
            prompt=positive_prompt.strip(),
            quality="standard",
            size=f"{width}x{height}",
            n=1,
            
            )
        # download image to outputs
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)
        image_url = response.data[0].url

        # Get the image data from the URL
        response = requests.get(image_url)

        if response.status_code == 200:
            # Generate the full path for the image file
            if output_file_name:
                file_name = output_folder/output_file_name  # You can change the filename if needed
            else:
                file_name = output_folder/find_next_available_filename(output_folder, "img_dalle_")  # You can change the filename if needed

            # Save the image to the specified folder
            with open(file_name, "wb") as file:
                file.write(response.content)
                
            ASCIIColors.yellow(f"Image saved to {file_name}")
        else:
            ASCIIColors.red("Failed to download the image")

        return file_name, {"positive_prompt":positive_prompt}
    
    def paint_from_images(self, positive_prompt: str, images: List[str], negative_prompt: str = "") -> List[Dict[str, str]]:
        if output_path is None:
            output_path = self.output_path
        if not PackageManager.check_package_installed("openai"):
            PackageManager.install_package("openai")
        import openai
        openai.api_key = self.service_config.api_key
        generation_engine="dall-e-2"
        supported_resolutions = [
            [512, 512],
            [1024, 1024],
        ]
        # Find the closest resolution
        closest_resolution = min(supported_resolutions, key=lambda res: abs(res[0] - width) + abs(res[1] - height))



        # Update the width and height
        width = closest_resolution[0]
        height = closest_resolution[1]                    

        # Read the image file from disk and resize it
        image = Image.open(images[0])
        width, height = width, height
        image = image.resize((width, height))

        # Convert the image to a BytesIO object
        byte_stream = BytesIO()
        image.save(byte_stream, format='PNG')
        byte_array = byte_stream.getvalue()
        response = openai.images.create_variation(
            image=byte_array,
            n=1,
            model=generation_engine, # for now only dalle 2 supports variations
            size=f"{width}x{height}"
        )
        # download image to outputs
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        image_url = response.data[0].url

        # Get the image data from the URL
        response = requests.get(image_url)

        if response.status_code == 200:
            # Generate the full path for the image file
            file_name = output_dir/find_next_available_filename(output_dir, "img_dalle_")  # You can change the filename if needed

            # Save the image to the specified folder
            with open(file_name, "wb") as file:
                file.write(response.content)
            ASCIIColors.yellow(f"Image saved to {file_name}")
        else:
            ASCIIColors.red("Failed to download the image")

        return file_name
            

    @staticmethod
    def get(app:LollmsApplication):
        return LollmsDalle