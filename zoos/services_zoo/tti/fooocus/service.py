# Title LollmsFooocus
# Licence: MIT
# Author : Paris Neo
    # All rights are reserved

from pathlib import Path
import sys
from lollms.app import LollmsApplication
from lollms.paths import LollmsPaths
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
from lollms.utilities import PackageManager, check_and_install_torch, find_next_available_filename
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
from lollms.tti import LollmsTTI
from lollms.utilities import git_pull, show_yes_no_dialog, run_script_in_env, create_conda_env
import subprocess
import shutil
from tqdm import tqdm
import threading


from lollms.config import TypedConfig, ConfigTemplate, BaseConfig

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


def install_fooocus(lollms_app:LollmsApplication):
    root_dir = lollms_app.lollms_paths.personal_path
    shared_folder = root_dir/"shared"
    fooocus_folder = shared_folder / "fooocus"
    fooocus_folder.mkdir(exist_ok=True, parents=True)
    if not PackageManager.check_package_installed("fooocus"):
        PackageManager.install_or_update("gradio_client")
        

def upgrade_fooocus(lollms_app:LollmsApplication):
    PackageManager.install_or_update("fooocus")
    PackageManager.install_or_update("xformers")


class LollmsFooocus(LollmsTTI):
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
                    "value": "localhost:1024",
                    "help": "The base URL for the service. This is the address where the service is hosted (e.g., http://127.0.0.1:8188/)."
                },
                {
                    "name": "wm",
                    "type": "str",
                    "value": "lollms",
                    "help": "Watermarking text or identifier to be used in the service."
                },
                {"name":"model", "type":"str", "value":"v2ray/stable-diffusion-3-medium-diffusers", "help":"The model to be used"},
                {"name":"wm", "type":"str", "value":"lollms", "help":"The water marking"},
            ]),
            BaseConfig(config={
                "api_key": "",     # use avx2
            })
        )

        super().__init__("fooocus", app, service_config)     
        self.ready = False
        # Get the current directory
        lollms_paths = app.lollms_paths
        root_dir = lollms_paths.personal_path
        
        shared_folder = root_dir/"shared"
        self.fooocus_folder = shared_folder / "fooocus"
        self.output_dir = root_dir / "outputs/fooocus"
        self.models_dir = self.fooocus_folder / "models"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        ASCIIColors.red(" _           _ _                ______                               ")
        ASCIIColors.red("| |         | | |               |  ___|                              ")
        ASCIIColors.red("| |     ___ | | |_ __ ___  ___  | |_ ___   ___   ___   ___ _   _ ___ ")
        ASCIIColors.red("| |    / _ \| | | '_ ` _ \/ __| |  _/ _ \ / _ \ / _ \ / __| | | / __|")
        ASCIIColors.red("| |___| (_) | | | | | | | \__ \ | || (_) | (_) | (_) | (__| |_| \__ \ ")
        ASCIIColors.red("\_____/\___/|_|_|_| |_| |_|___/ \_| \___/ \___/ \___/ \___|\__,_|___/")
        ASCIIColors.red("                            ______                                   ")
        ASCIIColors.red("                           |______|                                  ")
        if not PackageManager.check_package_installed("gradio_client"):
            PackageManager.install_or_update("gradio_client")
        from gradio_client import Client
        self.client = Client(base_url)
        

    @staticmethod
    def verify(app:LollmsApplication):
        # Clone repository
        root_dir = app.lollms_paths.personal_path
        shared_folder = root_dir/"shared"
        fooocus_folder = shared_folder / "fooocus"
        return fooocus_folder.exists()
    
    def get(app:LollmsApplication):
        root_dir = app.lollms_paths.personal_path
        shared_folder = root_dir/"shared"
        fooocus_folder = shared_folder / "fooocus"
        fooocus_script_path = fooocus_folder / "lollms_fooocus.py"
        git_pull(fooocus_folder)
        
        if fooocus_script_path.exists():
            ASCIIColors.success("lollms_fooocus found.")
            ASCIIColors.success("Loading source file...",end="")
            # use importlib to load the module from the file path
            from lollms.services.fooocus.lollms_fooocus import LollmsFooocus
            ASCIIColors.success("ok")
            return LollmsFooocus


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
            output_path = self.output_dir
        
        self.client.predict()
        image = self.model(positive_prompt, negative_prompt=negative_prompt, guidance_scale=scale, num_inference_steps=steps,).images[0]
        output_path = Path(output_path)
        fn = find_next_available_filename(output_path,"diff_img_")
        # Save the image
        image.save(fn)
        return fn, {"prompt":positive_prompt, "negative_prompt":negative_prompt}
    


# from gradio_client import Client

# client = Client("https://fooocus.mydomain.fr/",verify_ssl=False)
# result = client.predict(
# 				True,	# bool in 'Generate Image Grid for Each Batch' Checkbox component
# 				"Howdy!",	# str in 'parameter_11' Textbox component
# 				"Howdy!",	# str in 'Negative Prompt' Textbox component
# 				["Fooocus V2"],	# List[str] in 'Selected Styles' Checkboxgroup component
# 				"Quality",	# str in 'Performance' Radio component
# 				'704×1408 <span style="color: grey;"> ∣ 1:2</span>',	# str in 'Aspect Ratios' Radio component
# 				1,	# int | float (numeric value between 1 and 32) in 'Image Number' Slider component
# 				"png",	# str in 'Output Format' Radio component
# 				"Howdy!",	# str in 'Seed' Textbox component
# 				True,	# bool in 'Read wildcards in order' Checkbox component
# 				0,	# int | float (numeric value between 0.0 and 30.0) in 'Image Sharpness' Slider component
# 				1,	# int | float (numeric value between 1.0 and 30.0) in 'Guidance Scale' Slider component
# 				"animaPencilXL_v100.safetensors",	# str (Option from: ['animaPencilXL_v100.safetensors', 'juggernautXL_v8Rundiffusion.safetensors', 'realisticStockPhoto_v20.safetensors', 'sd_xl_base_1.0_0.9vae.safetensors', 'sd_xl_refiner_1.0_0.9vae.safetensors']) in 'Base Model (SDXL only)' Dropdown component
# 				"None",	# str (Option from: ['None', 'animaPencilXL_v100.safetensors', 'juggernautXL_v8Rundiffusion.safetensors', 'realisticStockPhoto_v20.safetensors', 'sd_xl_base_1.0_0.9vae.safetensors', 'sd_xl_refiner_1.0_0.9vae.safetensors']) in 'Refiner (SDXL or SD 1.5)' Dropdown component
# 				0.1,	# int | float (numeric value between 0.1 and 1.0) in 'Refiner Switch At' Slider component
# 				True,	# bool in 'Enable' Checkbox component
# 				"None",	# str (Option from: ['None', 'sd_xl_offset_example-lora_1.0.safetensors', 'SDXL_FILM_PHOTOGRAPHY_STYLE_BetaV0.4.safetensors', 'sdxl_lcm_lora.safetensors', 'sdxl_lightning_4step_lora.safetensors']) in 'LoRA 1' Dropdown component
# 				-2,	# int | float (numeric value between -2 and 2) in 'Weight' Slider component
# 				True,	# bool in 'Enable' Checkbox component
# 				"None",	# str (Option from: ['None', 'sd_xl_offset_example-lora_1.0.safetensors', 'SDXL_FILM_PHOTOGRAPHY_STYLE_BetaV0.4.safetensors', 'sdxl_lcm_lora.safetensors', 'sdxl_lightning_4step_lora.safetensors']) in 'LoRA 2' Dropdown component
# 				-2,	# int | float (numeric value between -2 and 2) in 'Weight' Slider component
# 				True,	# bool in 'Enable' Checkbox component
# 				"None",	# str (Option from: ['None', 'sd_xl_offset_example-lora_1.0.safetensors', 'SDXL_FILM_PHOTOGRAPHY_STYLE_BetaV0.4.safetensors', 'sdxl_lcm_lora.safetensors', 'sdxl_lightning_4step_lora.safetensors']) in 'LoRA 3' Dropdown component
# 				-2,	# int | float (numeric value between -2 and 2) in 'Weight' Slider component
# 				True,	# bool in 'Enable' Checkbox component
# 				"None",	# str (Option from: ['None', 'sd_xl_offset_example-lora_1.0.safetensors', 'SDXL_FILM_PHOTOGRAPHY_STYLE_BetaV0.4.safetensors', 'sdxl_lcm_lora.safetensors', 'sdxl_lightning_4step_lora.safetensors']) in 'LoRA 4' Dropdown component
# 				-2,	# int | float (numeric value between -2 and 2) in 'Weight' Slider component
# 				True,	# bool in 'Enable' Checkbox component
# 				"None",	# str (Option from: ['None', 'sd_xl_offset_example-lora_1.0.safetensors', 'SDXL_FILM_PHOTOGRAPHY_STYLE_BetaV0.4.safetensors', 'sdxl_lcm_lora.safetensors', 'sdxl_lightning_4step_lora.safetensors']) in 'LoRA 5' Dropdown component
# 				-2,	# int | float (numeric value between -2 and 2) in 'Weight' Slider component
# 				True,	# bool in 'Input Image' Checkbox component
# 				"Howdy!",	# str in 'parameter_91' Textbox component
# 				"Disabled",	# str in 'Upscale or Variation:' Radio component
# 				"https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png",	# str (filepath or URL to image) in 'Drag above image to here' Image component
# 				["Left"],	# List[str] in 'Outpaint Direction' Checkboxgroup component
# 				"https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png",	# str (filepath or URL to image) in 'Drag inpaint or outpaint image to here' Image component
# 				"Howdy!",	# str in 'Inpaint Additional Prompt' Textbox component
# 				"https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png",	# str (filepath or URL to image) in 'Mask Upload' Image component
# 				True,	# bool in 'Disable Preview' Checkbox component
# 				True,	# bool in 'Disable Intermediate Results' Checkbox component
# 				True,	# bool in 'Disable seed increment' Checkbox component
# 				0.1,	# int | float (numeric value between 0.1 and 3.0) in 'Positive ADM Guidance Scaler' Slider component
# 				0.1,	# int | float (numeric value between 0.1 and 3.0) in 'Negative ADM Guidance Scaler' Slider component
# 				0,	# int | float (numeric value between 0.0 and 1.0) in 'ADM Guidance End At Step' Slider component
# 				1,	# int | float (numeric value between 1.0 and 30.0) in 'CFG Mimicking from TSNR' Slider component
# 				"euler",	# str (Option from: ['euler', 'euler_ancestral', 'heun', 'heunpp2', 'dpm_2', 'dpm_2_ancestral', 'lms', 'dpm_fast', 'dpm_adaptive', 'dpmpp_2s_ancestral', 'dpmpp_sde', 'dpmpp_sde_gpu', 'dpmpp_2m', 'dpmpp_2m_sde', 'dpmpp_2m_sde_gpu', 'dpmpp_3m_sde', 'dpmpp_3m_sde_gpu', 'ddpm', 'lcm', 'ddim', 'uni_pc', 'uni_pc_bh2']) in 'Sampler' Dropdown component
# 				"normal",	# str (Option from: ['normal', 'karras', 'exponential', 'sgm_uniform', 'simple', 'ddim_uniform', 'lcm', 'turbo']) in 'Scheduler' Dropdown component
# 				-1,	# int | float (numeric value between -1 and 200) in 'Forced Overwrite of Sampling Step' Slider component
# 				-1,	# int | float (numeric value between -1 and 200) in 'Forced Overwrite of Refiner Switch Step' Slider component
# 				-1,	# int | float (numeric value between -1 and 2048) in 'Forced Overwrite of Generating Width' Slider component
# 				-1,	# int | float (numeric value between -1 and 2048) in 'Forced Overwrite of Generating Height' Slider component
# 				-1,	# int | float (numeric value between -1 and 1.0) in 'Forced Overwrite of Denoising Strength of "Vary"' Slider component
# 				-1,	# int | float (numeric value between -1 and 1.0) in 'Forced Overwrite of Denoising Strength of "Upscale"' Slider component
# 				True,	# bool in 'Mixing Image Prompt and Vary/Upscale' Checkbox component
# 				True,	# bool in 'Mixing Image Prompt and Inpaint' Checkbox component
# 				True,	# bool in 'Debug Preprocessors' Checkbox component
# 				True,	# bool in 'Skip Preprocessors' Checkbox component
# 				1,	# int | float (numeric value between 1 and 255) in 'Canny Low Threshold' Slider component
# 				1,	# int | float (numeric value between 1 and 255) in 'Canny High Threshold' Slider component
# 				"joint",	# str (Option from: ['joint', 'separate', 'vae']) in 'Refiner swap method' Dropdown component
# 				0,	# int | float (numeric value between 0.0 and 1.0) in 'Softness of ControlNet' Slider component
# 				True,	# bool in 'Enabled' Checkbox component
# 				0,	# int | float (numeric value between 0 and 2) in 'B1' Slider component
# 				0,	# int | float (numeric value between 0 and 2) in 'B2' Slider component
# 				0,	# int | float (numeric value between 0 and 4) in 'S1' Slider component
# 				0,	# int | float (numeric value between 0 and 4) in 'S2' Slider component
# 				True,	# bool in 'Debug Inpaint Preprocessing' Checkbox component
# 				True,	# bool in 'Disable initial latent in inpaint' Checkbox component
# 				"None",	# str (Option from: ['None', 'v1', 'v2.5', 'v2.6']) in 'Inpaint Engine' Dropdown component
# 				0,	# int | float (numeric value between 0.0 and 1.0) in 'Inpaint Denoising Strength' Slider component
# 				0,	# int | float (numeric value between 0.0 and 1.0) in 'Inpaint Respective Field' Slider component
# 				True,	# bool in 'Enable Mask Upload' Checkbox component
# 				True,	# bool in 'Invert Mask' Checkbox component
# 				-64,	# int | float (numeric value between -64 and 64) in 'Mask Erode or Dilate' Slider component
# 				True,	# bool in 'Save Metadata to Images' Checkbox component
# 				"fooocus",	# str in 'Metadata Scheme' Radio component
# 				"https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png",	# str (filepath or URL to image) in 'Image' Image component
# 				0,	# int | float (numeric value between 0.0 and 1.0) in 'Stop At' Slider component
# 				0,	# int | float (numeric value between 0.0 and 2.0) in 'Weight' Slider component
# 				"ImagePrompt",	# str in 'Type' Radio component
# 				"https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png",	# str (filepath or URL to image) in 'Image' Image component
# 				0,	# int | float (numeric value between 0.0 and 1.0) in 'Stop At' Slider component
# 				0,	# int | float (numeric value between 0.0 and 2.0) in 'Weight' Slider component
# 				"ImagePrompt",	# str in 'Type' Radio component
# 				"https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png",	# str (filepath or URL to image)in 'Image' Image component
# 				0,	# int | float (numeric value between 0.0 and 1.0) in 'Stop At' Slider component
# 				0,	# int | float (numeric value between 0.0 and 2.0) in 'Weight' Slider component
# 				"ImagePrompt",	# str in 'Type' Radio component
# 				"https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png",	# str (filepath or URL to image) in 'Image' Image component
# 				0,	# int | float (numeric value between 0.0 and 1.0) in 'Stop At' Slider component
# 				0,	# int | float (numeric value between 0.0 and 2.0) in 'Weight' Slider component
# 				"ImagePrompt",	# str in 'Type' Radio component
# 				fn_index=40
# )
# print(result)
