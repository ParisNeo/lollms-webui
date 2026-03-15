# Title LollmsNovitaAi
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


class LollmsNovitaAi(LollmsTTI):
    def __init__(self, app, output_folder:str|Path=None):
        """
        Initializes the LollmsNovitaAi binding.

        Args:
            api_key (str): The API key for authentication.
            output_folder (Path|str):  The output folder where to put the generated data
        """
        # Check for the OPENAI_KEY environment variable if no API key is provided
        api_key = os.getenv("OPENAI_KEY","")
        service_config = TypedConfig(
            ConfigTemplate([
                {"name":"engine","type":"str","value":"stable-diffusion","options":["stable-diffusion", "flux-1-schnell"]},
                {"name":"api_key", "type":"str", "value":api_key, "help":"A valid Novita AI key to generate text using anthropic api"},
                {"name":"model_name","type":"str","value":"darkSushiMixMix_225D_64380.safetensors", "options": ["darkSushiMixMix_225D_64380.safetensors"], "help":"The model name"},
                {"name":"n_frames","type":"int","value":85, "help":"The number of frames in the video"},
                {"name":"seed", "type":"int", "value":-1, "help":"The diffusion number of steps"},
                {"name":"steps", "type":"int", "value":20, "help":"The diffusion number of steps"},
                {"name":"guidance_scale", "type":"float", "value":7.5, "help":"The guidance scale for the generation"},
                {"name":"sampler", "type":"str", "value":"DPM++ SDE", "options":["Euler a","Euler","LMS","Heun","DPM2","DPM2 a","DPM++ 2S a","DPM++ 2M","DPM++ SDE","DPM fast","DPM adaptive","LMS Karras","DPM2 Karras","DPM2 a Karras","DPM++ 2S a Karras","DPM++ 2M Karras","DPM++ SDE Karras","DDIM","PLMS","UniPC"], "help":"The guidance scale for the generation"},
                {"name":"loras", "type":"str", "value":None, "help":"List of LoRA configurations"},
                {"name":"embeddings", "type":"str", "value":None, "help":"List of embedding configurations"},
                {"name":"closed_loop", "type":"bool", "value":False, "help":"Whether to use closed loop generation"},
                {"name":"clip_skip", "type":"int", "value":0, "help":"Number of layers to skip in CLIP"},
                {"name":"enable_transparent_background", "type":"bool", "value":False, "help":"Enable transparent background"}
                
            ]),
            BaseConfig(config={
                "api_key": "",     # use avx2
            })
        )

        super().__init__("novita_ai", app, service_config, output_folder)
        models = self.getModels()
        # if model["base_model_type"]==""
        service_config.config_template["model_name"]["options"] = ["arcaneDiffusion_v3_1016.ckpt"] + [model["model_name"] for model in models]

    def getModels(self):
        """
        Gets the list of models
        """
        url = "https://api.novita.ai/v3/model?filter.types=checkpoint"
        headers = {
            "Authorization": f"Bearer {self.service_config.api_key}"
        }

        response = requests.request("GET", url, headers=headers)
        js = response.json()
        return js["models"]
    

    def settings_updated(self):
        pass
    def pinn_width_height(self, width: int, height: int) -> Tuple[int, int]:
        """
        Pins the width and height to the valid range [128, 2048].

        Args:
            width (int): The desired width of the image.
            height (int): The desired height of the image.

        Returns:
            Tuple[int, int]: A tuple containing the pinned width and height.
        """
        # Define the valid range for width and height
        MIN_SIZE = 128
        MAX_SIZE = 2048

        # Pin the width to the valid range
        pinned_width = max(MIN_SIZE, min(width, MAX_SIZE))

        # Pin the height to the valid range
        pinned_height = max(MIN_SIZE, min(height, MAX_SIZE))

        return pinned_width, pinned_height
    def download_image(self, image_url: str, save_path: Path) -> None:
        """
        Downloads the generated video from the provided URL and saves it to the specified path.

        Args:
            image_url (str): The URL of the video to download.
            save_path (Path): The path where the video will be saved.
        """
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        with open(save_path, "wb") as file:
            file.write(response.content)
    def paint(
                self,
                positive_prompt,
                negative_prompt,
                sampler_name=None,
                seed=None,
                scale=None,
                steps=None,
                width=512,
                height=512,
                output_folder=None,
                output_file_name=None
                ):
            width, height = self.pinn_width_height(width, height)
            sampler_name = sampler_name if sampler_name else self.service_config.sampler
            scale = scale if scale else self.service_config.guidance_scale
            steps = steps if steps else self.service_config.steps
            seed = seed if seed else self.service_config.seed
            output_folder = output_folder if output_folder else self.output_folder
            if self.service_config.engine=="stable-diffusion":
                url = "https://api.novita.ai/v3/async/txt2img"

                payload = {
                    "extra": {
                        "response_image_type": "png",
                    },
                    "request": {
                        "model_name": self.service_config.model_name,
                        "prompt": positive_prompt,
                        "width": width,
                        "height": height,
                        "image_num": 1,
                        "steps": steps,
                        "guidance_scale": scale,
                        "sampler_name": sampler_name,
                        "negative_prompt": negative_prompt,
                        #"sd_vae": ,
                        "seed": seed,
                        #"loras": [
                        #    {
                        #        "model_name": "<string>",
                        #        "strength": {}
                        #    }
                        #],
                        #"embeddings": [{"model_name": "<string>"}],
                        #"hires_fix": {
                        #    "target_width": 123,
                        #    "target_height": 123,
                        #    "strength": {},
                        #    "upscaler": "<string>"
                        #},
                        #"refiner": {"switch_at": {}},
                        "enable_transparent_background": self.service_config.enable_transparent_background,
                        "restore_faces": True
                    }
                }
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.service_config.api_key}"
                }

                response = requests.request("POST", url, json=payload, headers=headers)
                try:
                    response.raise_for_status()  # Raise an exception for HTTP errors
                except Exception as ex:
                    trace_exception(ex)
                    infos = response.json()
                    try:
                        raise Exception(infos["message"]+"\nDetails:\n"+infos["metadata"]["details"])
                    except:
                        raise Exception(infos["message"]+"\nDetails:\n")
                    
                infos = response.json()
                task_id = infos.get("task_id")
                url = f"https://api.novita.ai/v3/async/task-result?task_id={task_id}"

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.service_config.api_key}",
                }
                done = False
                pbar = tqdm(total=100, desc="Generating image")
                while not done:
                    response = requests.request("GET", url, headers=headers)
                    infos = response.json()
                    pbar.n = infos["task"]["progress_percent"]
                    pbar.refresh()
                    if infos["task"]["status"]=="TASK_STATUS_SUCCEED" or infos["task"]["status"]=="TASK_STATUS_FAILED":
                        done = True
                    time.sleep(1)
                if infos["task"]["status"]=="TASK_STATUS_SUCCEED":
                    if output_folder:
                        output_folder = Path(output_folder)
                        if output_file_name:
                            file_name = output_folder/output_file_name # You can change the filename if needed
                        else:
                            file_name = output_folder/find_next_available_filename(output_folder, "img_novita_","png")  # You can change the filename if needed
                        self.download_image(infos["images"][0]["image_url"], file_name )
                        return file_name, {"positive_prompt":positive_prompt}
                    else:
                        return None, {"error":"Failed to generate the image. No output folder set!"}

                return None, {"error":"Failed to generate the image"}
            elif self.service_config.engine=="flux-1-schnell":
                url = "https://api.novita.ai/v3beta/flux-1-schnell"

                payload = {
                    "response_image_type": "png",
                    "prompt": positive_prompt,
                    "seed": seed if seed>=0 else random.randint(0,4294967295),
                    "steps": steps,
                    "width": width,
                    "height": height,
                    "image_num": 1
                }
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.service_config.api_key}"
                }

                response = requests.request("POST", url, json=payload, headers=headers)
                try:
                    response.raise_for_status()  # Raise an exception for HTTP errors
                    infos = response.json()
                except Exception as ex:
                    trace_exception(ex)
                    infos = response.json()
                    try:
                        raise Exception(infos["message"]+"\nDetails:\n"+infos["metadata"]["details"])
                    except:
                        raise Exception(infos["message"])
                if output_folder:
                    output_folder = Path(output_folder)
                    if output_file_name:
                        file_name = output_folder/output_file_name # You can change the filename if needed
                    else:
                        file_name = output_folder/find_next_available_filename(output_folder, "img_novita_","png")  # You can change the filename if needed
                    self.download_image(infos["images"][0]["image_url"], file_name )    
                    return file_name, {"positive_prompt":positive_prompt}

    
    def paint_from_images(self, positive_prompt: str, images: List[str], negative_prompt: str = "") -> List[Dict[str, str]]:
        pass
            

    @staticmethod
    def get(app:LollmsApplication):
        return LollmsNovitaAi