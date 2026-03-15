# Title LollmsSD
# Licence: MIT
# Author : Paris Neo
# Adapted from the work of mix1009's sdwebuiapi
# check it out : https://github.com/mix1009/sdwebuiapi/tree/main
# Here is a copy of the LICENCE https://github.com/mix1009/sdwebuiapi/blob/main/LICENSE
# All rights are reserved

from pathlib import Path
import sys
from lollms.app import LollmsApplication
from lollms.paths import LollmsPaths
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
from lollms.utilities import PackageManager, find_next_available_filename
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
from lollms.utilities import git_pull, show_yes_no_dialog, EnvironmentManager
import subprocess
import shutil
from tqdm import tqdm
import threading

em = EnvironmentManager()


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
    sd_folder = shared_folder / "auto_sd"
    download_file(model_url, sd_folder/"models/Stable-diffusion","Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors")

def install_sd(lollms_app:LollmsApplication):
    root_dir = lollms_app.lollms_paths.personal_path
    shared_folder = root_dir/"shared"
    sd_folder = shared_folder / "auto_sd"
    ASCIIColors.cyan("Installing autosd conda environment with python 3.10")
    em.create_env("autosd","3.10")
    ASCIIColors.cyan("Done")
    if os.path.exists(str(sd_folder)):
        print("Repository already exists. Pulling latest changes...")
        try:
            subprocess.run(["git", "-C", str(sd_folder), "pull"], check=True)
            subprocess.run(["git", "-C", str(sd_folder/"extensions/SD-CN-Animation"), "pull"])
        except:
            subprocess.run(["git", "clone", "https://github.com/ParisNeo/stable-diffusion-webui.git", str(sd_folder)])
    else:
        print("Cloning repository...")
        subprocess.run(["git", "clone", "https://github.com/ParisNeo/stable-diffusion-webui.git", str(sd_folder)])
        subprocess.run(["git", "clone", "https://github.com/Mikubill/sd-webui-controlnet", str(sd_folder/"extensions/sd-webui-controlnet")])        
        subprocess.run(["git", "clone", "https://github.com/deforum-art/sd-webui-deforum.git", str(sd_folder/"extensions/sd-webui-deforum")])
        subprocess.run(["git", "clone", "https://github.com/ParisNeo/SD-CN-Animation.git", str(sd_folder/"extensions/SD-CN-Animation")])

    if show_yes_no_dialog("warning!","Do you want to install a model?\nI suggest Juggernaut-XL_v9.\nYou can install models manually by putting them inside your persona folder/auto_sd/models/stable_diffusion"):
        download_file("https://huggingface.co/RunDiffusion/Juggernaut-XL-v9/resolve/main/Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors", sd_folder/"models/Stable-diffusion","Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors")
    
    lollms_app.sd = LollmsSD(lollms_app)
    ASCIIColors.green("Stable diffusion installed successfully")


def upgrade_sd(lollms_app:LollmsApplication):
    root_dir = lollms_app.lollms_paths.personal_path
    shared_folder = root_dir/"shared"
    sd_folder = shared_folder / "auto_sd"
    if os.path.exists(str(sd_folder)):
        print("Repository already exists. Pulling latest changes...")
        try:
            subprocess.run(["git", "-C", str(sd_folder), "pull"], check=True)
        except:
            subprocess.run(["git", "clone", "https://github.com/ParisNeo/stable-diffusion-webui.git", str(sd_folder)])

        try:
            subprocess.run(["git", "-C", str(sd_folder/"extensions/sd-webui-deforum"), "pull"])
        except:
            subprocess.run(["git", "clone", "https://github.com/deforum-art/sd-webui-deforum.git", str(sd_folder/"extensions/sd-webui-deforum")])

        try:
            subprocess.run(["git", "-C", str(sd_folder/"extensions/sd-webui-controlnet"), "pull"])
        except:
            subprocess.run(["git", "clone", "https://github.com/Mikubill/sd-webui-controlnet", str(sd_folder/"extensions/sd-webui-controlnet")])        

        try:
            subprocess.run(["git", "-C", str(sd_folder/"extensions/SD-CN-Animation"), "pull"])
        except:
            subprocess.run(["git", "clone", "https://github.com/ParisNeo/SD-CN-Animation.git", str(sd_folder/"extensions/SD-CN-Animation")])
    else:
        print("Cloning repository...")
        subprocess.run(["git", "clone", "https://github.com/ParisNeo/stable-diffusion-webui.git", str(sd_folder)])
        subprocess.run(["git", "clone", "https://github.com/deforum-art/sd-webui-deforum.git", str(sd_folder/"extensions/sd-webui-deforum")])
        subprocess.run(["git", "clone", "https://github.com/ParisNeo/SD-CN-Animation.git", str(sd_folder/"extensions/SD-CN-Animation")])


def raw_b64_img(image: Image) -> str:
    # XXX controlnet only accepts RAW base64 without headers
    with io.BytesIO() as output_bytes:
        metadata = None
        for key, value in image.info.items():
            if isinstance(key, str) and isinstance(value, str):
                if metadata is None:
                    metadata = PngImagePlugin.PngInfo()
                metadata.add_text(key, value)
        image.save(output_bytes, format="PNG", pnginfo=metadata)

        bytes_data = output_bytes.getvalue()

    return str(base64.b64encode(bytes_data), "utf-8")


def b64_img(image: Image) -> str:
    return "data:image/png;base64," + raw_b64_img(image)


class Upscaler(str, Enum):
    none = "None"
    Lanczos = "Lanczos"
    Nearest = "Nearest"
    LDSR = "LDSR"
    BSRGAN = "BSRGAN"
    ESRGAN_4x = "ESRGAN_4x"
    R_ESRGAN_General_4xV3 = "R-ESRGAN General 4xV3"
    ScuNET_GAN = "ScuNET GAN"
    ScuNET_PSNR = "ScuNET PSNR"
    SwinIR_4x = "SwinIR 4x"


class HiResUpscaler(str, Enum):
    none = "None"
    Latent = "Latent"
    LatentAntialiased = "Latent (antialiased)"
    LatentBicubic = "Latent (bicubic)"
    LatentBicubicAntialiased = "Latent (bicubic antialiased)"
    LatentNearest = "Latent (nearist)"
    LatentNearestExact = "Latent (nearist-exact)"
    Lanczos = "Lanczos"
    Nearest = "Nearest"
    ESRGAN_4x = "ESRGAN_4x"
    LDSR = "LDSR"
    ScuNET_GAN = "ScuNET GAN"
    ScuNET_PSNR = "ScuNET PSNR"
    SwinIR_4x = "SwinIR 4x"

@dataclass
class WebUIApiResult:
    images: list
    parameters: dict
    info: dict

    @property
    def image(self):
        return self.images[0]



class ControlNetUnit:
    def __init__(
        self,
        input_image: Image = None,
        mask: Image = None,
        module: str = "none",
        model: str = "None",
        weight: float = 1.0,
        resize_mode: str = "Resize and Fill",
        lowvram: bool = False,
        processor_res: int = 512,
        threshold_a: float = 64,
        threshold_b: float = 64,
        guidance: float = 1.0,
        guidance_start: float = 0.0,
        guidance_end: float = 1.0,
        control_mode: int = 0,
        pixel_perfect: bool = False,
        guessmode: int = None,  # deprecated: use control_mode
    ):
        self.input_image = input_image
        self.mask = mask
        self.module = module
        self.model = model
        self.weight = weight
        self.resize_mode = resize_mode
        self.lowvram = lowvram
        self.processor_res = processor_res
        self.threshold_a = threshold_a
        self.threshold_b = threshold_b
        self.guidance = guidance
        self.guidance_start = guidance_start
        self.guidance_end = guidance_end
        if guessmode:
            print(
                "ControlNetUnit guessmode is deprecated. Please use control_mode instead."
            )
            control_mode = guessmode
        self.control_mode = control_mode
        self.pixel_perfect = pixel_perfect

    def to_dict(self):
        return {
            "input_image": raw_b64_img(self.input_image) if self.input_image else "",
            "mask": raw_b64_img(self.mask) if self.mask is not None else None,
            "module": self.module,
            "model": self.model,
            "weight": self.weight,
            "resize_mode": self.resize_mode,
            "lowvram": self.lowvram,
            "processor_res": self.processor_res,
            "threshold_a": self.threshold_a,
            "threshold_b": self.threshold_b,
            "guidance": self.guidance,
            "guidance_start": self.guidance_start,
            "guidance_end": self.guidance_end,
            "control_mode": self.control_mode,
            "pixel_perfect": self.pixel_perfect,
        }

class LollmsSD(LollmsTTI):
    has_controlnet = False
    def __init__(self, app:LollmsApplication, output_folder:str|Path=None):
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
                    "value": "http://127.0.0.1:7860",
                    "help": "Watermarking text or identifier to be used in the generated content."
                },
                {
                    "name": "wm",
                    "type": "str",
                    "value": "Artbot",
                    "help": "Watermarking text or identifier to be used in the generated content."
                },
                {
                    "name": "max_retries",
                    "type": "int",
                    "value": 50,
                    "help": "The maximum number of retries to attempt before determining that the service is unavailable."
                },
                {
                    "name": "guidance_scale",
                    "type": "float",
                    "value": 7.5,
                    "help": "The guidance scale for diffusion process."
                },
                {
                    "name": "sampler",
                    "type": "str",
                    "value": "Euler a",
                    "help": "The sampler algorithm to use for image generation. Example: 'Euler a'."
                },
                {
                    "name": "steps",
                    "type": "int",
                    "value": 20,
                    "help": "The number of steps to use in the generation process. Higher values may improve quality but increase processing time."
                },
                {
                    "name": "seed",
                    "type": "int",
                    "value": -1,
                    "help": "Random numbers generator seed."
                },
                {
                    "name": "use_https",
                    "type": "bool",
                    "value": False,
                    "help": "If set to true, the service will use HTTPS for secure communication."
                },
                {
                    "name": "username",
                    "type": "str",
                    "value": None,
                    "help": "The username for authentication, if required by the service."
                },
                {
                    "name": "password",
                    "type": "str",
                    "value": None,
                    "help": "The password for authentication, if required by the service."
                },
                {
                    "name": "local_service",
                    "type": "bool",
                    "value": False,
                    "help": "If set to true, a local instance of the service will be installed and used."
                },
                {
                    "name": "start_service_at_startup",
                    "type": "bool",
                    "value": False,
                    "help": "If set to true, the service will automatically start at startup. This also enables the local service option."
                },
                {
                    "name": "share",
                    "type": "bool",
                    "value": False,
                    "help": "If set to true, the server will be accessible from outside your local machine (e.g., over the internet)."
                },
                {
                    "name": "restore_faces",
                    "type": "bool",
                    "value": False,
                    "help": "If set to true,faces are going to be restored after generation."
                }
                
            ]),
            BaseConfig(config={
                "api_key": "",     # use avx2
            })
        )

        super().__init__("stable_diffusion", app, service_config, output_folder)

        self.ready = False
        # Get the current directory
        lollms_paths = app.lollms_paths
        root_dir = lollms_paths.personal_path

        # Store the path to the script
        if service_config.base_url is None:
            self.service_config.base_url = "http://127.0.0.1:7860"
        if service_config.local_service and service_config.start_service_at_startup:
            if not LollmsSD.verify(app):
                install_sd(app)


        self.sd_base_url = self.service_config.base_url+"/sdapi/v1"
        shared_folder = root_dir/"shared"
        self.sd_folder = shared_folder / "auto_sd"
        self.output_folder = root_dir / "outputs/sd"
        self.output_folder.mkdir(parents=True, exist_ok=True)

       
        ASCIIColors.red("                                                       ")
        ASCIIColors.red(" __    _____ __    __    _____ _____       _____ ____  ")
        ASCIIColors.red("|  |  |     |  |  |  |  |     |   __|     |   __|    \ ")
        ASCIIColors.red("|  |__|  |  |  |__|  |__| | | |__   |     |__   |  |  |")
        ASCIIColors.red("|_____|_____|_____|_____|_|_|_|_____|_____|_____|____/ ")
        ASCIIColors.red("                                    |_____|            ")

        ASCIIColors.red(" Forked from Auto1111's Stable diffusion api")
        ASCIIColors.red(" Integration in lollms by ParisNeo using mix1009's sdwebuiapi ")

        if not self.wait_for_service(1,False) and service_config.local_service and service_config.start_service_at_startup:
            ASCIIColors.info("Loading lollms_sd")
            os.environ['SD_WEBUI_RESTARTING'] = '1' # To forbid sd webui from showing on the browser automatically
            # Launch the Flask service using the appropriate script for the platform
            if platform.system() == "Windows":
                ASCIIColors.info("Running on windows")
                script_path = self.sd_folder / "lollms_sd.bat"
                if self.service_config.share:
                    pass # TODO : implement
                    # run_script_in_env("autosd", str(script_path) +" --share", cwd=self.sd_folder)
                else:
                    pass # TODO : implement
                    # run_script_in_env("autosd", str(script_path), cwd=self.sd_folder)
            else:
                ASCIIColors.info("Running on linux/MacOs")
                script_path = str(self.sd_folder / "lollms_sd.sh")
                ASCIIColors.info(f"launcher path: {script_path}")
                ASCIIColors.info(f"sd path: {self.sd_folder}")

                if self.service_config.share:
                    pass # TODO: implement
                    # run_script_in_env("autosd","bash " + script_path +" --share", cwd=self.sd_folder)
                else:
                    pass # TODO: implement
                    # run_script_in_env("autosd","bash " + script_path, cwd=self.sd_folder)
                ASCIIColors.info("Process done")
                ASCIIColors.success("Launching Auto1111's SD succeeded")

        # Wait until the service is available at http://127.0.0.1:7860/

        self.default_sampler = self.service_config.sampler
        self.default_steps = self.service_config.steps

        self.session = requests.Session()

        if self.service_config.username and self.service_config.password:
            self.set_auth(self.service_config.username, self.service_config.password)
        else:
            self.check_controlnet()
    def settings_updated(self):
        pass # TODO: implement
    @staticmethod
    def verify(app:LollmsApplication):
        # Clone repository
        root_dir = app.lollms_paths.personal_path
        shared_folder = root_dir/"shared"
        sd_folder = shared_folder / "auto_sd"
        return sd_folder.exists()
    
    def get(app:LollmsApplication):
        root_dir = app.lollms_paths.personal_path
        shared_folder = root_dir/"shared"
        sd_folder = shared_folder / "auto_sd"
        sd_script_path = sd_folder / "lollms_sd.py"
        git_pull(sd_folder)
        
        if sd_script_path.exists():
            ASCIIColors.success("lollms_sd found.")
            ASCIIColors.success("Loading source file...",end="")
            # use importlib to load the module from the file path
            from lollms.services.tti.sd.lollms_sd import LollmsSD
            ASCIIColors.success("ok")
            return LollmsSD


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
        
        scale = scale if scale else self.service_config.guidance_scale
        steps = steps if steps else self.service_config.steps
        seed = seed if seed else self.service_config.seed
        output_folder = output_folder if output_folder else self.output_folder

        infos = {}
        img_paths = []

        try:
            generated = self.txt2img(
                        positive_prompt,
                        negative_prompt=negative_prompt, 
                        sampler_name=sampler_name,
                        seed=seed,
                        cfg_scale=scale,
                        steps=steps,
                        width=width,
                        height=height,
                        tiling=False,
                        restore_faces=self.service_config.restore_faces,
                        styles=None, 
                        script_name="",
                        )
            """
                images: list
                parameters: dict
                info: dict
            """
            for img in generated.images:
                if output_file_name:
                    file_name = output_folder/output_file_name # You can change the filename if needed
                else:
                    file_name = output_folder/find_next_available_filename(output_folder, "img_sd_","png")  # You can change the filename if needed
                img_paths.append(self.saveImage(img, file_name))
            infos = generated.info
        except Exception as ex:
            ASCIIColors.error("Couldn't generate the image")
            trace_exception(ex)  


        return img_paths[0] if len(img_paths)>0 else None, infos

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
                            output_folder=None,
                            output_file_name=None
                            ) -> List[Dict[str, str]]:
        output_folder = output_folder if output_folder else self.output_folder
        infos = {}
        img_paths = []
        try:
            generated = self.img2img(
                        positive_prompt,
                        negative_prompt, 
                        [self.loadImage(images[-1])],
                        sampler_name=sampler_name,
                        seed=seed,
                        cfg_scale=scale,
                        steps=steps,
                        width=int(width),
                        height=int(height),
                        denoising_strength=img2img_denoising_strength,
                        tiling=False,
                        restore_faces=restore_faces,
                        styles=None, 
                        script_name="",
                        )
            """
                images: list
                parameters: dict
                info: dict
            """
            for img in generated.images:
                if output_file_name:
                    file_name = output_folder/output_file_name # You can change the filename if needed
                else:
                    file_name = output_folder/find_next_available_filename(output_folder, "img_sd_","png")  # You can change the filename if needed
                img_paths.append(self.saveImage(img, file_name))
            infos = generated.info
        except Exception as ex:
            ASCIIColors.error("Couldn't generate the image")
            trace_exception(ex)  

        return img_paths[0] if len(img_paths)>0 else None, infos

    def check_controlnet(self):
        try:
            scripts = self.get_scripts()
            self.has_controlnet = "controlnet m2m" in scripts["txt2img"]
        except:
            pass

    def set_auth(self, username, password):
        self.session.auth = (username, password)
        self.check_controlnet()

    def _to_api_result(self, response):
        if response.status_code != 200:
            raise RuntimeError(response.status_code, response.text)

        r = response.json()
        images = []
        if "images" in r.keys():
            images = [Image.open(io.BytesIO(base64.b64decode(i))) for i in r["images"]]
        elif "image" in r.keys():
            images = [Image.open(io.BytesIO(base64.b64decode(r["image"])))]

        info = ""
        if "info" in r.keys():
            try:
                info = json.loads(r["info"])
            except:
                info = r["info"]
        elif "html_info" in r.keys():
            info = r["html_info"]
        elif "caption" in r.keys():
            info = r["caption"]

        parameters = ""
        if "parameters" in r.keys():
            parameters = r["parameters"]

        return WebUIApiResult(images, parameters, info)

    async def _to_api_result_async(self, response):
        if response.status != 200:
            raise RuntimeError(response.status, await response.text())

        r = await response.json()
        images = []
        if "images" in r.keys():
            images = [Image.open(io.BytesIO(base64.b64decode(i))) for i in r["images"]]
        elif "image" in r.keys():
            images = [Image.open(io.BytesIO(base64.b64decode(r["image"])))]

        info = ""
        if "info" in r.keys():
            try:
                info = json.loads(r["info"])
            except:
                info = r["info"]
        elif "html_info" in r.keys():
            info = r["html_info"]
        elif "caption" in r.keys():
            info = r["caption"]

        parameters = ""
        if "parameters" in r.keys():
            parameters = r["parameters"]

        return WebUIApiResult(images, parameters, info)

    def loadImage(self, file_path:str)->Image:
        return Image.open(file_path)

    def saveImage(self, image:Image, save_file_path=None):
        image.save(save_file_path)
        return save_file_path


    def txt2img(
        self,
        prompt="",
        negative_prompt="",
        enable_hr=False,
        denoising_strength=0.7,
        firstphase_width=0,
        firstphase_height=0,
        hr_scale=2,
        hr_upscaler=HiResUpscaler.Latent,
        hr_second_pass_steps=0,
        hr_resize_x=0,
        hr_resize_y=0,
        styles=[],
        seed=-1,
        subseed=-1,
        subseed_strength=0.0,
        seed_resize_from_h=0,
        seed_resize_from_w=0,
        sampler_name=None,  # use this instead of sampler_index
        batch_size=1,
        n_iter=1,
        steps=None,
        cfg_scale=7.0,
        width=512,
        height=512,
        restore_faces=False,
        tiling=False,
        do_not_save_samples=False,
        do_not_save_grid=False,
        eta=1.0,
        s_churn=0,
        s_tmax=0,
        s_tmin=0,
        s_noise=1,
        override_settings={},
        override_settings_restore_afterwards=True,
        script_args=None,  # List of arguments for the script "script_name"
        script_name=None,
        send_images=True,
        save_images=False,
        alwayson_scripts={},
        controlnet_units: List[ControlNetUnit] = [],
        sampler_index=None,  # deprecated: use sampler_name
        use_deprecated_controlnet=False,
        use_async=False,
    ):
        if sampler_index is None:
            sampler_index = self.default_sampler
        if sampler_name is None:
            sampler_name = self.default_sampler
        if steps is None:
            steps = self.default_steps
        if script_args is None:
            script_args = []
        payload = {
            "enable_hr": enable_hr,
            "hr_scale": hr_scale,
            "hr_upscaler": hr_upscaler,
            "hr_second_pass_steps": hr_second_pass_steps,
            "hr_resize_x": hr_resize_x,
            "hr_resize_y": hr_resize_y,
            "denoising_strength": denoising_strength,
            "firstphase_width": firstphase_width,
            "firstphase_height": firstphase_height,
            "prompt": prompt,
            "styles": styles,
            "seed": seed,
            "subseed": subseed,
            "subseed_strength": subseed_strength,
            "seed_resize_from_h": seed_resize_from_h,
            "seed_resize_from_w": seed_resize_from_w,
            "batch_size": batch_size,
            "n_iter": n_iter,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height,
            "restore_faces": restore_faces,
            "tiling": tiling,
            "do_not_save_samples": do_not_save_samples,
            "do_not_save_grid": do_not_save_grid,
            "negative_prompt": negative_prompt,
            "eta": eta,
            "s_churn": s_churn,
            "s_tmax": s_tmax,
            "s_tmin": s_tmin,
            "s_noise": s_noise,
            "override_settings": override_settings,
            "override_settings_restore_afterwards": override_settings_restore_afterwards,
            "sampler_name": sampler_name,
            "sampler_index": sampler_index,
            "script_name": script_name,
            "script_args": script_args,
            "send_images": send_images,
            "save_images": save_images,
            "alwayson_scripts": alwayson_scripts,
        }

        if use_deprecated_controlnet and controlnet_units and len(controlnet_units) > 0:
            payload["controlnet_units"] = [x.to_dict() for x in controlnet_units]
            return self.custom_post(
                "controlnet/txt2img", payload=payload, use_async=use_async
            )

        if controlnet_units and len(controlnet_units) > 0:
            payload["alwayson_scripts"]["ControlNet"] = {
                "args": [x.to_dict() for x in controlnet_units]
            }
        #elif self.has_controlnet:
            # workaround : if not passed, webui will use previous args!
        #    payload["alwayson_scripts"]["ControlNet"] = {"args": []}
        print(self.sd_base_url)
        return self.post_and_get_api_result(
            f"{self.sd_base_url}/txt2img", payload, use_async
        )

    def post_and_get_api_result(self, url, json, use_async):
        if use_async:
            import asyncio

            return asyncio.ensure_future(self.async_post(url=url, json=json))
        else:
            response = self.session.post(url=url, json=json)
            return self._to_api_result(response)

    async def async_post(self, url, json):
        import aiohttp

        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(self.session.auth[0], self.session.auth[1]) if self.session.auth else None
            async with session.post(url, json=json, auth=auth) as response:
                return await self._to_api_result_async(response)

    def img2img(
        self,
        prompt="",
        negative_prompt="",
        images=[],  # list of PIL Image
        resize_mode=0,
        denoising_strength=0.75,
        image_cfg_scale=1.5,
        mask_image=None,  # PIL Image mask
        mask_blur=4,
        inpainting_fill=0,
        inpaint_full_res=True,
        inpaint_full_res_padding=0,
        inpainting_mask_invert=0,
        initial_noise_multiplier=1,
        styles=[],
        seed=-1,
        subseed=-1,
        subseed_strength=0,
        seed_resize_from_h=0,
        seed_resize_from_w=0,
        sampler_name=None,  # use this instead of sampler_index
        batch_size=1,
        n_iter=1,
        steps=None,
        cfg_scale=7.0,
        width=512,
        height=512,
        restore_faces=False,
        tiling=False,
        do_not_save_samples=False,
        do_not_save_grid=False,
        eta=1.0,
        s_churn=0,
        s_tmax=0,
        s_tmin=0,
        s_noise=1,
        override_settings={},
        override_settings_restore_afterwards=True,
        script_args=None,  # List of arguments for the script "script_name"
        sampler_index=None,  # deprecated: use sampler_name
        include_init_images=False,
        script_name=None,
        send_images=True,
        save_images=False,
        alwayson_scripts={},
        controlnet_units: List[ControlNetUnit] = [],
        use_deprecated_controlnet=False,
        use_async=False,
    ):
        if sampler_name is None:
            sampler_name = self.default_sampler
        if sampler_index is None:
            sampler_index = self.default_sampler
        if steps is None:
            steps = self.default_steps
        if script_args is None:
            script_args = []

        payload = {
            "init_images": [b64_img(x) for x in images],
            "resize_mode": resize_mode,
            "denoising_strength": denoising_strength,
            "mask_blur": mask_blur,
            "inpainting_fill": inpainting_fill,
            "inpaint_full_res": inpaint_full_res,
            "inpaint_full_res_padding": inpaint_full_res_padding,
            "inpainting_mask_invert": inpainting_mask_invert,
            "initial_noise_multiplier": initial_noise_multiplier,
            "prompt": prompt,
            "styles": styles,
            "seed": seed,
            "subseed": subseed,
            "subseed_strength": subseed_strength,
            "seed_resize_from_h": seed_resize_from_h,
            "seed_resize_from_w": seed_resize_from_w,
            "batch_size": batch_size,
            "n_iter": n_iter,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "image_cfg_scale": image_cfg_scale,
            "width": width,
            "height": height,
            "restore_faces": restore_faces,
            "tiling": tiling,
            "do_not_save_samples": do_not_save_samples,
            "do_not_save_grid": do_not_save_grid,
            "negative_prompt": negative_prompt,
            "eta": eta,
            "s_churn": s_churn,
            "s_tmax": s_tmax,
            "s_tmin": s_tmin,
            "s_noise": s_noise,
            "override_settings": override_settings,
            "override_settings_restore_afterwards": override_settings_restore_afterwards,
            "sampler_name": sampler_name,
            "sampler_index": sampler_index,
            "include_init_images": include_init_images,
            "script_name": script_name,
            "script_args": script_args,
            "send_images": send_images,
            "save_images": save_images,
            "alwayson_scripts": alwayson_scripts,
        }
        if mask_image is not None:
            payload["mask"] = b64_img(mask_image)

        if use_deprecated_controlnet and controlnet_units and len(controlnet_units) > 0:
            payload["controlnet_units"] = [x.to_dict() for x in controlnet_units]
            return self.custom_post(
                "controlnet/img2img", payload=payload, use_async=use_async
            )

        if controlnet_units and len(controlnet_units) > 0:
            payload["alwayson_scripts"]["ControlNet"] = {
                "args": [x.to_dict() for x in controlnet_units]
            }
        #elif self.has_controlnet:
        #    payload["alwayson_scripts"]["ControlNet"] = {"args": []}

        return self.post_and_get_api_result(
            f"{self.sd_base_url}/img2img", payload, use_async
        )

    def extra_single_image(
        self,
        image,  # PIL Image
        resize_mode=0,
        show_extras_results=True,
        gfpgan_visibility=0,
        codeformer_visibility=0,
        codeformer_weight=0,
        upscaling_resize=2,
        upscaling_resize_w=512,
        upscaling_resize_h=512,
        upscaling_crop=True,
        upscaler_1="None",
        upscaler_2="None",
        extras_upscaler_2_visibility=0,
        upscale_first=False,
        use_async=False,
    ):
        payload = {
            "resize_mode": resize_mode,
            "show_extras_results": show_extras_results,
            "gfpgan_visibility": gfpgan_visibility,
            "codeformer_visibility": codeformer_visibility,
            "codeformer_weight": codeformer_weight,
            "upscaling_resize": upscaling_resize,
            "upscaling_resize_w": upscaling_resize_w,
            "upscaling_resize_h": upscaling_resize_h,
            "upscaling_crop": upscaling_crop,
            "upscaler_1": upscaler_1,
            "upscaler_2": upscaler_2,
            "extras_upscaler_2_visibility": extras_upscaler_2_visibility,
            "upscale_first": upscale_first,
            "image": b64_img(image),
        }

        return self.post_and_get_api_result(
            f"{self.sd_base_url}/extra-single-image", payload, use_async
        )

    def extra_batch_images(
        self,
        images,  # list of PIL images
        name_list=None,  # list of image names
        resize_mode=0,
        show_extras_results=True,
        gfpgan_visibility=0,
        codeformer_visibility=0,
        codeformer_weight=0,
        upscaling_resize=2,
        upscaling_resize_w=512,
        upscaling_resize_h=512,
        upscaling_crop=True,
        upscaler_1="None",
        upscaler_2="None",
        extras_upscaler_2_visibility=0,
        upscale_first=False,
        use_async=False,
    ):
        if name_list is not None:
            if len(name_list) != len(images):
                raise RuntimeError("len(images) != len(name_list)")
        else:
            name_list = [f"image{i + 1:05}" for i in range(len(images))]
        images = [b64_img(x) for x in images]

        image_list = []
        for name, image in zip(name_list, images):
            image_list.append({"data": image, "name": name})

        payload = {
            "resize_mode": resize_mode,
            "show_extras_results": show_extras_results,
            "gfpgan_visibility": gfpgan_visibility,
            "codeformer_visibility": codeformer_visibility,
            "codeformer_weight": codeformer_weight,
            "upscaling_resize": upscaling_resize,
            "upscaling_resize_w": upscaling_resize_w,
            "upscaling_resize_h": upscaling_resize_h,
            "upscaling_crop": upscaling_crop,
            "upscaler_1": upscaler_1,
            "upscaler_2": upscaler_2,
            "extras_upscaler_2_visibility": extras_upscaler_2_visibility,
            "upscale_first": upscale_first,
            "imageList": image_list,
        }

        return self.post_and_get_api_result(
            f"{self.sd_base_url}/extra-batch-images", payload, use_async
        )

    # XXX 500 error (2022/12/26)
    def png_info(self, image):
        payload = {
            "image": b64_img(image),
        }

        response = self.session.post(url=f"{self.sd_base_url}/png-info", json=payload)
        return self._to_api_result(response)

    """
    :param image pass base64 encoded image or PIL Image
    :param model "clip" or "deepdanbooru"
    """
    def interrogate(self, image, model="clip"):
        payload = {
            "image": b64_img(image) if isinstance(image, Image.Image) else b64_img(Image.open(image)),
            "model": model,
        }

        response = self.session.post(url=f"{self.sd_base_url}/interrogate", json=payload)
        return self._to_api_result(response)

    def interrupt(self):
        response = self.session.post(url=f"{self.sd_base_url}/interrupt")
        return response.json()

    def skip(self):
        response = self.session.post(url=f"{self.sd_base_url}/skip")
        return response.json()

    def get_options(self):
        response = self.session.get(url=f"{self.sd_base_url}/options")
        return response.json()

    def set_options(self, options):
        response = self.session.post(url=f"{self.sd_base_url}/options", json=options)
        return response.json()

    def get_cmd_flags(self):
        response = self.session.get(url=f"{self.sd_base_url}/cmd-flags")
        return response.json()

    def get_progress(self):
        response = self.session.get(url=f"{self.sd_base_url}/progress")
        return response.json()

    def get_cmd_flags(self):
        response = self.session.get(url=f"{self.sd_base_url}/cmd-flags")
        return response.json()

    def get_samplers(self):
        response = self.session.get(url=f"{self.sd_base_url}/samplers")
        return response.json()

    def get_sd_vae(self):
        response = self.session.get(url=f"{self.sd_base_url}/sd-vae")
        return response.json()

    def get_upscalers(self):
        response = self.session.get(url=f"{self.sd_base_url}/upscalers")
        return response.json()

    def get_latent_upscale_modes(self):
        response = self.session.get(url=f"{self.sd_base_url}/latent-upscale-modes")
        return response.json()

    def get_loras(self):
        response = self.session.get(url=f"{self.sd_base_url}/loras")
        return response.json()

    def get_sd_models(self):
        response = self.session.get(url=f"{self.sd_base_url}/sd-models")
        return response.json()

    def get_hypernetworks(self):
        response = self.session.get(url=f"{self.sd_base_url}/hypernetworks")
        return response.json()

    def get_face_restorers(self):
        response = self.session.get(url=f"{self.sd_base_url}/face-restorers")
        return response.json()

    def get_realesrgan_models(self):
        response = self.session.get(url=f"{self.sd_base_url}/realesrgan-models")
        return response.json()

    def get_prompt_styles(self):
        response = self.session.get(url=f"{self.sd_base_url}/prompt-styles")
        return response.json()

    def get_artist_categories(self):  # deprecated ?
        response = self.session.get(url=f"{self.sd_base_url}/artist-categories")
        return response.json()

    def get_artists(self):  # deprecated ?
        response = self.session.get(url=f"{self.sd_base_url}/artists")
        return response.json()

    def refresh_checkpoints(self):
        response = self.session.post(url=f"{self.sd_base_url}/refresh-checkpoints")
        return response.json()

    def get_scripts(self):
        response = self.session.get(url=f"{self.sd_base_url}/scripts")
        return response.json()

    def get_embeddings(self):
        response = self.session.get(url=f"{self.sd_base_url}/embeddings")
        return response.json()

    def get_memory(self):
        response = self.session.get(url=f"{self.sd_base_url}/memory")
        return response.json()

    def get_endpoint(self, endpoint, baseurl):
        if baseurl:
            return f"{self.sd_base_url}/{endpoint}"
        else:
            from urllib.parse import urlparse, urlunparse

            parsed_url = urlparse(self.service_config.base_url)
            basehost = parsed_url.netloc
            parsed_url2 = (parsed_url[0], basehost, endpoint, "", "", "")
            return urlunparse(parsed_url2)

    def custom_get(self, endpoint, baseurl=False):
        url = self.get_endpoint(endpoint, baseurl)
        response = self.session.get(url=url)
        return response.json()

    def custom_post(self, endpoint, payload={}, baseurl=False, use_async=False):
        url = self.get_endpoint(endpoint, baseurl)
        if use_async:
            import asyncio

            return asyncio.ensure_future(self.async_post(url=url, json=payload))
        else:
            response = self.session.post(url=url, json=payload)
            return self._to_api_result(response)

    def controlnet_version(self):
        r = self.custom_get("controlnet/version")
        return r["version"]

    def controlnet_model_list(self):
        r = self.custom_get("controlnet/model_list")
        return r["model_list"]

    def controlnet_module_list(self):
        r = self.custom_get("controlnet/module_list")
        return r["module_list"]

    def controlnet_detect(
        self, images, module="none", processor_res=512, threshold_a=64, threshold_b=64
    ):
        input_images = [b64_img(x) for x in images]
        payload = {
            "controlnet_module": module,
            "controlnet_input_images": input_images,
            "controlnet_processor_res": processor_res,
            "controlnet_threshold_a": threshold_a,
            "controlnet_threshold_b": threshold_b,
        }
        r = self.custom_post("controlnet/detect", payload=payload)
        return r

    def util_get_model_names(self):
        return sorted([x["title"] for x in self.get_sd_models()])

    def util_set_model(self, name, find_closest=True):
        if find_closest:
            name = name.lower()
        models = self.util_get_model_names()
        found_model = None
        if name in models:
            found_model = name
        elif find_closest:
            import difflib

            def str_simularity(a, b):
                return difflib.SequenceMatcher(None, a, b).ratio()

            max_sim = 0.0
            max_model = models[0]
            for model in models:
                sim = str_simularity(name, model)
                if sim >= max_sim:
                    max_sim = sim
                    max_model = model
            found_model = max_model
        if found_model:
            print(f"loading {found_model}")
            options = {}
            options["sd_model_checkpoint"] = found_model
            self.set_options(options)
            print(f"model changed to {found_model}")
        else:
            print("model not found")

    def util_get_current_model(self):
        return self.get_options()["sd_model_checkpoint"]

    def util_wait_for_ready(self, check_interval=5.0):
        import time

        while True:
            result = self.get_progress()
            progress = result["progress"]
            job_count = result["state"]["job_count"]
            if progress == 0.0 and job_count == 0:
                break
            else:
                print(f"[WAIT]: progress = {progress:.4f}, job_count = {job_count}")
                time.sleep(check_interval)


    def wait_for_service_in_another_thread(self, max_retries=150, show_warning=True):
        thread = threading.Thread(target=self.wait_for_service, args=(max_retries, show_warning))
        thread.start()
        return thread

    def wait_for_service(self, max_retries = 50, show_warning=True):
        url = f"{self.sd_base_url}/internal/ping"
        # Adjust this value as needed
        retries = 0

        while retries < max_retries or max_retries<0:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    print("Service is available.")
                    if self.app is not None:
                        self.app.success("SD Service is now available.")
                    self.ready = True
                    return True
            except requests.exceptions.RequestException:
                pass

            retries += 1
            time.sleep(1)
        if show_warning:
            print("Service did not become available within the given time.")
            if self.app is not None:
                self.app.error("SD Service did not become available within the given time.")
        return False
    
    def get_available_image_name(self, save_folder, base_name):
        index = 0
        while True:
            image_name = f"{base_name}_{index}.png"
            image_path = os.path.join(save_folder, image_name)
            if not os.path.exists(image_path):
                return image_name
            index += 1        



## Interface for extensions


# https://github.com/mix1009/model-keyword
@dataclass
class ModelKeywordResult:
    keywords: list
    model: str
    oldhash: str
    match_source: str


class ModelKeywordInterface:
    def __init__(self, webuiapi):
        self.api = webuiapi

    def get_keywords(self):
        result = self.api.custom_get("model_keyword/get_keywords")
        keywords = result["keywords"]
        model = result["model"]
        oldhash = result["hash"]
        match_source = result["match_source"]
        return ModelKeywordResult(keywords, model, oldhash, match_source)





# https://github.com/Klace/stable-diffusion-webui-instruct-pix2pix
class InstructPix2PixInterface:
    def __init__(self, webuiapi):
        self.api = webuiapi

    def img2img(
        self,
        images=[],
        prompt: str = "",
        negative_prompt: str = "",
        output_batches: int = 1,
        sampler: str = "Euler a",
        steps: int = 20,
        seed: int = 0,
        randomize_seed: bool = True,
        text_cfg: float = 7.5,
        image_cfg: float = 1.5,
        randomize_cfg: bool = False,
        output_image_width: int = 512,
    ):
        init_images = [b64_img(x) for x in images]
        payload = {
            "init_images": init_images,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "output_batches": output_batches,
            "sampler": sampler,
            "steps": steps,
            "seed": seed,
            "randomize_seed": randomize_seed,
            "text_cfg": text_cfg,
            "image_cfg": image_cfg,
            "randomize_cfg": randomize_cfg,
            "output_image_width": output_image_width,
        }
        return self.api.custom_post("instruct-pix2pix/img2img", payload=payload)


#https://github.com/AUTOMATIC1111/stable-diffusion-webui-rembg
class RemBGInterface:
    def __init__(self, webuiapi):
        self.api = webuiapi

    def rembg(
        self,
        input_image: str = "", #image string (?)
        model: str = 'u2net',  #[None, 'u2net', 'u2netp', 'u2net_human_seg', 'u2net_cloth_seg','silueta','isnet-general-use','isnet-anime']
        return_mask: bool = False,
        alpha_matting: bool = False,
        alpha_matting_foreground_threshold: int = 240,
        alpha_matting_background_threshold: int = 10,
        alpha_matting_erode_size: int = 10
    ):

        payload = {
            "input_image": b64_img(input_image),
            "model": model,
            "return_mask": return_mask,
            "alpha_matting":  alpha_matting,
            "alpha_matting_foreground_threshold": alpha_matting_foreground_threshold,
            "alpha_matting_background_threshold": alpha_matting_background_threshold,
            "alpha_matting_erode_size": alpha_matting_erode_size
        }
        return self.api.custom_post("rembg", payload=payload)


# https://github.com/Mikubill/sd-webui-controlnet
class ControlNetInterface:
    def __init__(self, webuiapi, show_deprecation_warning=True):
        self.api = webuiapi
        self.show_deprecation_warning = show_deprecation_warning

    def print_deprecation_warning(self):
        print(
            "ControlNetInterface txt2img/img2img is deprecated. Please use normal txt2img/img2img with controlnet_units param"
        )

    def txt2img(
        self,
        prompt: str = "",
        negative_prompt: str = "",
        controlnet_input_image: [] = [],
        controlnet_mask: [] = [],
        controlnet_module: str = "",
        controlnet_model: str = "",
        controlnet_weight: float = 0.5,
        controlnet_resize_mode: str = "Scale to Fit (Inner Fit)",
        controlnet_lowvram: bool = False,
        controlnet_processor_res: int = 512,
        controlnet_threshold_a: int = 64,
        controlnet_threshold_b: int = 64,
        controlnet_guidance: float = 1.0,
        enable_hr: bool = False,  # hiresfix
        denoising_strength: float = 0.5,
        hr_scale: float = 1.5,
        hr_upscale: str = "Latent",
        guess_mode: bool = True,
        seed: int = -1,
        subseed: int = -1,
        subseed_strength: int = -1,
        sampler_index: str = "Euler a",
        batch_size: int = 1,
        n_iter: int = 1,  # Iteration
        steps: int = 20,
        cfg_scale: float = 7,
        width: int = 512,
        height: int = 512,
        restore_faces: bool = False,
        override_settings: Dict[str, Any] = None,
        override_settings_restore_afterwards: bool = True,
    ):
        if self.show_deprecation_warning:
            self.print_deprecation_warning()

        controlnet_input_image_b64 = [raw_b64_img(x) for x in controlnet_input_image]
        controlnet_mask_b64 = [raw_b64_img(x) for x in controlnet_mask]

        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "controlnet_input_image": controlnet_input_image_b64,
            "controlnet_mask": controlnet_mask_b64,
            "controlnet_module": controlnet_module,
            "controlnet_model": controlnet_model,
            "controlnet_weight": controlnet_weight,
            "controlnet_resize_mode": controlnet_resize_mode,
            "controlnet_lowvram": controlnet_lowvram,
            "controlnet_processor_res": controlnet_processor_res,
            "controlnet_threshold_a": controlnet_threshold_a,
            "controlnet_threshold_b": controlnet_threshold_b,
            "controlnet_guidance": controlnet_guidance,
            "enable_hr": enable_hr,
            "denoising_strength": denoising_strength,
            "hr_scale": hr_scale,
            "hr_upscale": hr_upscale,
            "guess_mode": guess_mode,
            "seed": seed,
            "subseed": subseed,
            "subseed_strength": subseed_strength,
            "sampler_index": sampler_index,
            "batch_size": batch_size,
            "n_iter": n_iter,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height,
            "restore_faces": restore_faces,
            "override_settings": override_settings,
            "override_settings_restore_afterwards": override_settings_restore_afterwards,
        }
        return self.api.custom_post("controlnet/txt2img", payload=payload)

    def img2img(
        self,
        init_images: [] = [],
        mask: str = None,
        mask_blur: int = 30,
        inpainting_fill: int = 0,
        inpaint_full_res: bool = True,
        inpaint_full_res_padding: int = 1,
        inpainting_mask_invert: int = 1,
        resize_mode: int = 0,
        denoising_strength: float = 0.7,
        prompt: str = "",
        negative_prompt: str = "",
        controlnet_input_image: [] = [],
        controlnet_mask: [] = [],
        controlnet_module: str = "",
        controlnet_model: str = "",
        controlnet_weight: float = 1.0,
        controlnet_resize_mode: str = "Scale to Fit (Inner Fit)",
        controlnet_lowvram: bool = False,
        controlnet_processor_res: int = 512,
        controlnet_threshold_a: int = 64,
        controlnet_threshold_b: int = 64,
        controlnet_guidance: float = 1.0,
        guess_mode: bool = True,
        seed: int = -1,
        subseed: int = -1,
        subseed_strength: int = -1,
        sampler_index: str = "",
        batch_size: int = 1,
        n_iter: int = 1,  # Iteration
        steps: int = 20,
        cfg_scale: float = 7,
        width: int = 512,
        height: int = 512,
        restore_faces: bool = False,
        include_init_images: bool = True,
        override_settings: Dict[str, Any] = None,
        override_settings_restore_afterwards: bool = True,
    ):
        if self.show_deprecation_warning:
            self.print_deprecation_warning()

        init_images_b64 = [raw_b64_img(x) for x in init_images]
        controlnet_input_image_b64 = [raw_b64_img(x) for x in controlnet_input_image]
        controlnet_mask_b64 = [raw_b64_img(x) for x in controlnet_mask]

        payload = {
            "init_images": init_images_b64,
            "mask": raw_b64_img(mask) if mask else None,
            "mask_blur": mask_blur,
            "inpainting_fill": inpainting_fill,
            "inpaint_full_res": inpaint_full_res,
            "inpaint_full_res_padding": inpaint_full_res_padding,
            "inpainting_mask_invert": inpainting_mask_invert,
            "resize_mode": resize_mode,
            "denoising_strength": denoising_strength,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "controlnet_input_image": controlnet_input_image_b64,
            "controlnet_mask": controlnet_mask_b64,
            "controlnet_module": controlnet_module,
            "controlnet_model": controlnet_model,
            "controlnet_weight": controlnet_weight,
            "controlnet_resize_mode": controlnet_resize_mode,
            "controlnet_lowvram": controlnet_lowvram,
            "controlnet_processor_res": controlnet_processor_res,
            "controlnet_threshold_a": controlnet_threshold_a,
            "controlnet_threshold_b": controlnet_threshold_b,
            "controlnet_guidance": controlnet_guidance,
            "guess_mode": guess_mode,
            "seed": seed,
            "subseed": subseed,
            "subseed_strength": subseed_strength,
            "sampler_index": sampler_index,
            "batch_size": batch_size,
            "n_iter": n_iter,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height,
            "restore_faces": restore_faces,
            "include_init_images": include_init_images,
            "override_settings": override_settings,
            "override_settings_restore_afterwards": override_settings_restore_afterwards,
        }
        return self.api.custom_post("controlnet/img2img", payload=payload)

    def model_list(self):
        r = self.api.custom_get("controlnet/model_list")
        return r["model_list"]


    """
    def txt_to_img(
                    self, 
                    positive_prompt,
                    negative_prompt="",
                    denoising_strength=0,
                    seed=-1,
                    cfg_scale=7,
                    steps=50,
                    width=512,
                    height=512,
                    tiling=False,
                    sampler_name="Euler", 
                    upscaler_name="", 
                    styles=None, 
                    restore_faces=False, 
                    save_folder=None, 
                    script_name=""
                    ):
        url = f"{self.sd_base_url}/sdapi/v1/txt2img"
        
        if styles is None:
            styles = []
            
        if save_folder is None:
            save_folder = self.output_folder

        data = {
            "enable_hr": False,
            "denoising_strength": denoising_strength,
            "firstphase_width": 0,
            "firstphase_height": 0,
            "hr_scale": 2,
            "hr_upscaler": upscaler_name,
            "hr_second_pass_steps": 0,
            "hr_resize_x": 0,
            "hr_resize_y": 0,
            "hr_sampler_name": sampler_name,
            "hr_prompt": "",
            "hr_negative_prompt": "",
            "prompt": positive_prompt,
            "styles": styles,
            "seed": seed,
            "subseed": -1,
            "subseed_strength": 0,
            "seed_resize_from_h": -1,
            "seed_resize_from_w": -1,
            "sampler_name": sampler_name,
            "batch_size": 1,
            "n_iter": 1,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height,
            "restore_faces": restore_faces,
            "tiling": tiling,
            "do_not_save_samples": False,
            "do_not_save_grid": True,
            "negative_prompt": negative_prompt,
            "eta": 0,
            "s_min_uncond": 0,
            "s_churn": 0,
            "s_tmax": 0,
            "s_tmin": 0,
            "s_noise": 1,
            "override_settings": {},
            "override_settings_restore_afterwards": True,
            "script_args": [],
            "sampler_index": sampler_name,
            "script_name": script_name,
            "send_images": True,
            "save_images": False,
            "alwayson_scripts": {}
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=data, headers=headers)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                response_data = response.json()
                if save_folder:
                    image_paths = []
                    for i, image_base64 in enumerate(response_data['images']):
                        image_name = self.get_available_image_name(save_folder, self.service_config.wm)
                        image_path = os.path.join(save_folder, image_name)
                        image_data = base64.b64decode(image_base64)
                        with open(image_path, 'wb') as f:
                            f.write(image_data)
                        image_paths.append(image_path)
                    response_data['image_paths'] = image_paths
                return response_data
            else:
                # If the request was not successful, print the status code and response text
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def img_to_img(self, 
                   init_images, 
                   prompt="", 
                   negative_prompt="",
                   sampler_name="Euler",
                   seed=-1,
                   cfg_scale=7,
                   steps=50,
                   width=512,
                   height=512,
                   denoising_strength=0.75,
                   tiling=False,
                   restore_faces=False,
                   styles=None, 
                   save_folder=None, 
                   script_name=""
                ):
        url = f"{self.sd_base_url}/sdapi/v1/img2img"

        if styles is None:
            styles = []

        data = {
            "init_images": init_images,
            "resize_mode": 0,
            "denoising_strength": denoising_strength,
            "image_cfg_scale": 0,
            "mask": "string",
            "mask_blur": 0,
            "mask_blur_x": 4,
            "mask_blur_y": 4,
            "inpainting_fill": 0,
            "inpaint_full_res": True,
            "inpaint_full_res_padding": 0,
            "inpainting_mask_invert": 0,
            "initial_noise_multiplier": 0,
            "prompt": prompt,
            "styles": styles,
            "seed": seed,
            "subseed": -1,
            "subseed_strength": 0,
            "seed_resize_from_h": -1,
            "seed_resize_from_w": -1,
            "sampler_name": sampler_name,
            "batch_size": 1,
            "n_iter": 1,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height,
            "restore_faces": restore_faces,
            "tiling": tiling,
            "do_not_save_samples": False,
            "do_not_save_grid": True,
            "negative_prompt": negative_prompt,
            "eta": 0,
            "s_min_uncond": 0,
            "s_churn": 0,
            "s_tmax": 0,
            "s_tmin": 0,
            "s_noise": 1,
            "override_settings": {},
            "override_settings_restore_afterwards": True,
            "script_args": [],
            "sampler_index": "Euler",
            "include_init_images": False,
            "script_name": script_name,
            "send_images": True,
            "save_images": False,
            "alwayson_scripts": {}
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=data, headers=headers)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                response_data = response.json()
                if save_folder:
                    image_paths = []
                    for i, image_base64 in enumerate(response_data['images']):
                        image_name = self.get_available_image_name(save_folder, self.service_config.wm)
                        image_path = os.path.join(save_folder, image_name)
                        image_data = base64.b64decode(image_base64)
                        with open(image_path, 'wb') as f:
                            f.write(image_data)
                        image_paths.append(image_path)
                    response_data['image_paths'] = image_paths
                return response_data
            else:
                # If the request was not successful, print the status code and response text
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    
    """
