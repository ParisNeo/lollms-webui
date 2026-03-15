# Title LollmsDiffusers
# Licence: MIT
# Author : Paris Neo
    # All rights are reserved

from pathlib import Path
import sys
from lollms.app import LollmsApplication
from lollms.utilities import PackageManager, check_and_install_torch, find_next_available_filename

from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
import sys
import requests
from typing import List, Dict, Any

from ascii_colors import ASCIIColors, trace_exception
from lollms.paths import LollmsPaths
from lollms.tti import LollmsTTI
from lollms.utilities import git_pull
from tqdm import tqdm

import pipmaster as pm
# Install required libraries if not already present
if not pm.is_installed("torch"):
    pm.install_multiple(["torch","torchvision"," torchaudio"], "https://download.pytorch.org/whl/cu126")  # Adjust CUDA version as needed
if not pm.is_installed("diffusers"):
    pm.install("diffusers")
if not pm.is_installed("transformers"):
    pm.install("transformers")
if not pm.is_installed("accelerate"):
    pm.install("accelerate")
if not pm.is_installed("imageio-ffmpeg"):
    pm.install("imageio-ffmpeg")

import torch


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

def install_model(lollms_app:LollmsApplication, model_url):
    root_dir = lollms_app.lollms_paths.personal_path
    shared_folder = root_dir/"shared"
    diffusers_folder = shared_folder / "diffusers"



    import torch
    from diffusers import PixArtSigmaPipeline

    # You can replace the checkpoint id with "PixArt-alpha/PixArt-Sigma-XL-2-512-MS" too.
    pipe = PixArtSigmaPipeline.from_pretrained(
        "PixArt-alpha/PixArt-Sigma-XL-2-1024-MS", torch_dtype=torch.float16
    )    


        



def upgrade_diffusers(lollms_app:LollmsApplication):
    PackageManager.install_or_update("diffusers")
    PackageManager.install_or_update("xformers")


class LollmsDiffusers(LollmsTTI):
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
                    "name": "model",
                    "type": "str",
                    "value": "v2ray/stable-diffusion-3-medium-diffusers",
                    "options": [
                        "v2ray/stable-diffusion-3-medium-diffusers",
                        "runwayml/stable-diffusion-v1-5",
                        "stabilityai/stable-diffusion-2-1",
                        "CompVis/stable-diffusion-v1-4",
                        "prompthero/openjourney",
                        "StabilityAI/stable-diffusion-2-base",
                        "dreamlike-art/dreamlike-photoreal-2.0",
                        "stabilityai/stable-diffusion-xl-base-1.0",
                        "stabilityai/stable-diffusion-3-medium",
                        "runwayml/stable-diffusion-v1-4",
                        "hakurei/waifu-diffusion",
                        "Lykon/dreamshaper-8",
                        "stabilityai/stable-diffusion-3.5-large"
                    ],
                    "help": "The model to be used"
                },
                {"name":"wm", "type":"str", "value":"lollms", "help":"The water marking"},
                {"name":"use_gpu", "type":"bool", "value":True, "help":"Activate GPU usage"},
                {"name":"diffusers_offloading_mode", "type":"str", "value":"lollms", "options":["no_offload","sequential_cpu_offload","model_cpu_offload"], "help":"The water marking"},
                
            ]),
            BaseConfig(config={
                "api_key": "",     # use avx2
            })
        )
        # Get the current directory
        lollms_paths = app.lollms_paths
        root_dir = lollms_paths.personal_path
        
        shared_folder = root_dir/"shared"
        self.diffusers_folder = shared_folder / "diffusers"
        self.output_dir = root_dir / "outputs/diffusers"
        self.tti_models_dir = self.diffusers_folder / "models"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.tti_models_dir.mkdir(parents=True, exist_ok=True)

        super().__init__("diffusers", app, service_config)
        self.settings_updated()

    def settings_updated(self):
        ASCIIColors.red("")       
        ASCIIColors.red("   _           _ _                    _ _  __  __                          ")
        ASCIIColors.red("  | |         | | |                  | (_)/ _|/ _|                         ")
        ASCIIColors.red("  | |     ___ | | |_ __ ___  ___   __| |_| |_| |_ _   _ ___  ___ _ __ ___  ")
        ASCIIColors.red("  | |    / _ \| | | '_ ` _ \/ __| / _` | |  _|  _| | | / __|/ _ \ '__/ __| ")
        ASCIIColors.red("  | |___| (_) | | | | | | | \__ \| (_| | | | | | | |_| \__ \  __/ |  \__ \ ")
        ASCIIColors.red("  |______\___/|_|_|_| |_| |_|___/ \__,_|_|_| |_|  \__,_|___/\___|_|  |___/ ")
        ASCIIColors.red("                              ______                                       ")
        ASCIIColors.red("                             |______|                                      ")
        ASCIIColors.red("")       
        ASCIIColors.yellow(f"Using model: {self.service_config.model}")
        import torch 

        try:
            if "stable-diffusion-3" in self.service_config.model:
                from diffusers import StableDiffusion3Pipeline # AutoPipelineForImage2Image#PixArtSigmaPipeline
                self.tti_model = StableDiffusion3Pipeline.from_pretrained(
                    self.service_config.model, torch_dtype=torch.float16, cache_dir=self.tti_models_dir,
                    use_safetensors=True,
                )
                
                self.iti_model = None
            else:
                from diffusers import AutoPipelineForText2Image # AutoPipelineForImage2Image#PixArtSigmaPipeline
                self.tti_model = AutoPipelineForText2Image.from_pretrained(
                    self.service_config.model, torch_dtype=torch.float16, cache_dir=self.tti_models_dir,
                    use_safetensors=True,
                )
                self.iti_model = None
            
            try:
                if self.service_config.use_gpu:
                    self.tti_model.to("cuda")
                if self.service_config.diffusers_offloading_mode=="sequential_cpu_offload":
                    self.tti_model.enable_sequential_cpu_offload()
                elif self.service_config.diffusers_offloading_mode=="model_cpu_offload":
                    self.tti_model.enable_model_cpu_offload()
            except Exception as ex:
                trace_exception(ex)
        except Exception as ex:
            self.tti_model= None
            trace_exception(ex)

    def install_diffusers(self):
        root_dir = self.app.lollms_paths.personal_path
        shared_folder = root_dir/"shared"
        diffusers_folder = shared_folder / "diffusers"
        diffusers_folder.mkdir(exist_ok=True, parents=True)
        models_dir = diffusers_folder / "models"
        models_dir.mkdir(parents=True, exist_ok=True)

        pm.install("diffusers")
        pm.install("xformers")


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

    def get_scheduler_by_name(self, scheduler_name="LMS"):
        if scheduler_name == "LMS":
            from diffusers import LMSDiscreteScheduler
            return LMSDiscreteScheduler(
                beta_start=0.00085, 
                beta_end=0.012, 
                beta_schedule="scaled_linear"
            )
        elif scheduler_name == "Euler":
            from diffusers import EulerDiscreteScheduler
            return LMSDiscreteScheduler()
        elif scheduler_name == "DDPMS":
            from diffusers import DDPMScheduler
            return DDPMScheduler()
        elif scheduler_name == "DDIMS":
            from diffusers import DDIMScheduler
            return DDIMScheduler()
        
        
            
    def paint(
                self,
                positive_prompt,
                negative_prompt,
                width=512,
                height=512,
                sampler_name="",
                seed=-1,
                scale=7.5,
                steps=20,
                img2img_denoising_strength=0.9,
                restore_faces=True,
                output_path=None
                ):
        if sampler_name!="":
            sc = self.get_scheduler_by_name(sampler_name)
            if sc:
                self.tti_model.scheduler = sc
        width = adjust_dimensions(int(width))
        height = adjust_dimensions(int(height))
        
        
        def process_output_path(output_path, self_output_dir):
            if output_path is None:
                output_path = Path(self_output_dir)
                fn = find_next_available_filename(output_path, "diff_img_")
            else:
                output_path = Path(output_path)
                if output_path.is_file():
                    fn = output_path
                elif output_path.is_dir():
                    fn = find_next_available_filename(output_path, "diff_img_")
                else:
                    # If the path doesn't exist, assume it's intended to be a file
                    fn = output_path

            return fn
        
        
        # Usage in the original context
        if output_path is None:
            output_path = self.output_dir

        fn = process_output_path(output_path, self.output_dir)
        
        if seed!=-1:
            generator = torch.Generator("cuda").manual_seed(seed)
            image = self.tti_model(positive_prompt, negative_prompt=negative_prompt, height=height, width=width, guidance_scale=scale, num_inference_steps=steps, generator=generator).images[0]
        else:
            # Define a callback function to update progress
            progress_bar = tqdm(total=steps, desc="Generating Image")
            
            def callback(step: int, timestep: int, tensor):
                progress_bar.update(1)
                
            # Generate image with callback
            image = self.tti_model(
                positive_prompt,
                negative_prompt=negative_prompt,
                height=height,
                width=width,
                guidance_scale=scale,
                num_inference_steps=steps,
                #callback=callback,
                #callback_steps=1
            ).images[0]
            
            progress_bar.close()            
        # Save the image
        image.save(fn)
        return fn, {"prompt":positive_prompt, "negative_prompt":negative_prompt}
    
    def paint_from_images(self, positive_prompt: str, 
                            image: str, 
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
        from diffusers.utils import make_image_grid, load_image

        if not self.iti_model:
            from diffusers import AutoPipelineForImage2Image
            
            self.iti_model = AutoPipelineForImage2Image.from_pretrained(
                self.self.service_config.model, torch_dtype=torch.float16, variant="fp16", use_safetensors=True
            )
        if sampler_name!="":
            sc = self.get_scheduler_by_name(sampler_name)
            if sc:
                self.iti_model.scheduler = sc

        img = load_image(image)
        if output_path is None:
            output_path = self.output_dir
        if seed!=-1:
            generator = torch.Generator("cuda").manual_seed(seed)
            image = self.titi_model(positive_prompt,image=img, negative_prompt=negative_prompt, height=height, width=width, guidance_scale=scale, num_inference_steps=steps, generator=generator).images[0]
        else:
            image = self.iti_model(positive_prompt,image=img, negative_prompt=negative_prompt, height=height, width=width, guidance_scale=scale, num_inference_steps=steps).images[0]
        output_path = Path(output_path)
        fn = find_next_available_filename(output_path,"diff_img_")
        # Save the image
        image.save(fn)
        return fn, {"prompt":positive_prompt, "negative_prompt":negative_prompt}
    
