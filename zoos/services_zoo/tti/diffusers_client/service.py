# Title LollmsDiffusers
# Licence: MIT
# Author : Paris Neo
    # All rights are reserved

from pathlib import Path
import sys
from lollms.app import LollmsApplication
from lollms.utilities import PackageManager, check_and_install_torch, find_next_available_filename, install_cuda, check_torch_version

from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
import sys
import requests
from typing import List, Dict, Any

from ascii_colors import ASCIIColors, trace_exception
from lollms.paths import LollmsPaths
from lollms.tti import LollmsTTI
from lollms.utilities import git_pull
from tqdm import tqdm
from PIL import Image
import threading
import base64
from PIL import Image
import io
import pipmaster as pm


def adjust_dimensions(value: int) -> int:
    """Adjusts the given value to be divisible by 8."""
    return (value // 8) * 8

def download_file(url, folder_path, local_filename):
    # Make sure 'folder_path' exists
    folder_path.mkdir(parents=True, exist_ok=True)

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True)
        with open(folder_path / local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
                progress_bar.update(len(chunk))
        progress_bar.close()

    return local_filename


def install_diffusers(lollms_app:LollmsApplication):
    root_dir = lollms_app.lollms_paths.personal_path
    shared_folder = root_dir/"shared"
    diffusers_folder = shared_folder / "diffusers"
    diffusers_folder.mkdir(exist_ok=True, parents=True)
    models_dir = diffusers_folder / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    PackageManager.reinstall("diffusers")
    PackageManager.reinstall("xformers")
        



def upgrade_diffusers(lollms_app:LollmsApplication):
    PackageManager.install_or_update("diffusers")
    PackageManager.install_or_update("xformers")


class LollmsDiffusersClient(LollmsTTI):
    has_controlnet = False
    def __init__(self, app, output_folder:str|Path=None):
        """
        Initializes the LollmsDalle binding.

        Args:
            api_key (str): The API key for authentication.
            output_folder (Path|str):  The output folder where to put the generated data
        """
        service_config = TypedConfig(
            ConfigTemplate([
                {
                    "name": "base_url",
                    "type": "str",
                    "value": "http://127.0.0.1:8188/",
                    "help": "The base URL for the service. This is the address where the service is hosted (e.g., http://127.0.0.1:8188/)."
                },
                {
                    "name": "wm",
                    "type": "str",
                    "value": "lollms",
                    "help": "Watermarking text or identifier to be used in the service."
                },
                {
                        "name":"model", 
                        "type":"str", 
                        "value":"v2ray/stable-diffusion-3-medium-diffusers",
                        "options": ["v2ray/stable-diffusion-3-medium-diffusers"]
                        
                        "help":"The model to be used"},
                {"name":"wm", "type":"str", "value":"lollms", "help":"The water marking"},
            ]),
            BaseConfig(config={
                "api_key": "",     # use avx2
            })
        )

        super().__init__("diffusers_client", app,service_config, output_folder)    
        self.ready = False
        # Get the current directory
        lollms_paths = app.lollms_paths
        root_dir = lollms_paths.personal_path


        shared_folder = root_dir/"shared"
        self.diffusers_folder = shared_folder / "diffusers"
        self.output_dir = root_dir / "outputs/diffusers"
        self.models_dir = self.diffusers_folder / "models"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)

       
        ASCIIColors.green("   _           _ _                    _ _  __  __                          ")
        ASCIIColors.green("  | |         | | |                  | (_)/ _|/ _|                         ")
        ASCIIColors.green("  | |     ___ | | |_ __ ___  ___   __| |_| |_| |_ _   _ ___  ___ _ __ ___  ")
        ASCIIColors.green("  | |    / _ \| | | '_ ` _ \/ __| / _` | |  _|  _| | | / __|/ _ \ '__/ __| ")
        ASCIIColors.green("  | |___| (_) | | | | | | | \__ \| (_| | | | | | | |_| \__ \  __/ |  \__ \ ")
        ASCIIColors.green("  |______\___/|_|_|_| |_| |_|___/ \__,_|_|_| |_|  \__,_|___/\___|_|  |___/ ")
        ASCIIColors.green("                              ______                                       ")
        ASCIIColors.green("                             |______|                                      ")

    def settings_updated(self):
        pass

    @staticmethod
    def verify(app:LollmsApplication):
        # Clone repository
        root_dir = app.lollms_paths.personal_path
        shared_folder = root_dir/"shared"
        diffusers_folder = shared_folder / "diffusers"
        return diffusers_folder.exists()
    
    def get(app:LollmsApplication):
        root_dir = app.lollms_paths.personal_path
        shared_folder = root_dir/"shared"
        diffusers_folder = shared_folder / "diffusers"
        diffusers_script_path = diffusers_folder / "lollms_diffusers.py"
        git_pull(diffusers_folder)
        
        if diffusers_script_path.exists():
            ASCIIColors.success("lollms_diffusers found.")
            ASCIIColors.success("Loading source file...",end="")
            # use importlib to load the module from the file path
            from lollms.services.tti.diffusers.lollms_diffusers import LollmsDiffusers
            ASCIIColors.success("ok")
            return LollmsDiffusers
    def paint(
        self,
        positive_prompt,
        negative_prompt="",
        sampler_name="",
        seed=-1,
        scale=7.5,
        steps=20,
        img2img_denoising_strength=0.9,
        width=512,
        height=512,
        restore_faces=True,
        output_path=None
    ):
        url = f"{self.service_config.base_url}/generate-image"
        
        payload = {
            "positive_prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "sampler_name": sampler_name,
            "seed": seed,
            "scale": scale,
            "steps": steps,
            "width": width,
            "height": height,
            "restore_faces": restore_faces
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()

            # Assuming the server returns the image path
            server_image_path = result['image_path']
            
            # If output_path is not provided, use the server's image path
            if output_path is None:
                output_path = server_image_path
            else:
                # Copy the image from server path to output_path
                # This part needs to be implemented based on how you want to handle file transfer
                pass

            return {
                "image_path": output_path,
                "prompt": result['prompt'],
                "negative_prompt": result['negative_prompt']
            }

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def save_image(self, image_data, output_path):
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))
        image.save(output_path)
        print(f"Image saved to {output_path}")
    
    def paint_from_images(self, positive_prompt: str, 
                            images: List[str], 
                            negative_prompt: str = "",
                            sampler_name="",
                            seed=-1,
                            scale=7.5,
                            steps=20,
                            img2img_denoising_strength=0.9,
                            width=512,
                            height=512,
                            restore_faces=True,
                            output_path=None
                            ) -> List[Dict[str, str]]:
        import torch
        if sampler_name!="":
            sc = self.get_scheduler_by_name(sampler_name)
            if sc:
                self.model.scheduler = sc

        if output_path is None:
            output_path = self.output_dir
        if seed!=-1:
            generator = torch.Generator("cuda").manual_seed(seed)
            image = self.model(positive_prompt, negative_prompt=negative_prompt, height=height, width=width, guidance_scale=scale, num_inference_steps=steps, generator=generator).images[0]
        else:
            image = self.model(positive_prompt, negative_prompt=negative_prompt, height=height, width=width, guidance_scale=scale, num_inference_steps=steps).images[0]
        output_path = Path(output_path)
        fn = find_next_available_filename(output_path,"diff_img_")
        # Save the image
        image.save(fn)
        return fn, {"prompt":positive_prompt, "negative_prompt":negative_prompt}
    
