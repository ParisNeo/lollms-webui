# Title LollmsComfyUI
# Licence: GPL-3.0
# Author : Paris Neo
# Forked from comfyanonymous's Comfyui nodes system
# check it out : https://github.com/comfyanonymous/ComfyUI
# Here is a copy of the LICENCE https://github.com/comfyanonymous/ComfyUI/blob/main/LICENSE
# All rights are reserved

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
import uuid
from ascii_colors import ASCIIColors, trace_exception
from lollms.paths import LollmsPaths
from lollms.utilities import git_pull, show_yes_no_dialog, PackageManager
from lollms.tti import LollmsTTI
import subprocess
import shutil
from tqdm import tqdm
import threading
import pipmaster as pm

if not pm.is_installed("websocket"):
    pm.install("websocket-client")
import websocket
if not pm.is_installed("urllib"):
    pm.install("urllib")
from urllib import request, parse



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




def get_comfyui(lollms_paths:LollmsPaths):
    root_dir = lollms_paths.personal_path
    shared_folder = root_dir/"shared"
    comfyui_folder = shared_folder / "comfyui"
    comfyui_script_path = comfyui_folder / "main.py"
    git_pull(comfyui_folder)
    
    if comfyui_script_path.exists():
        ASCIIColors.success("comfyui found.")
        ASCIIColors.success("Loading source file...",end="")
        # use importlib to load the module from the file path
        from lollms.services.tti.comfyui.lollms_comfyui import LollmsComfyUI
        ASCIIColors.success("ok")
        return LollmsComfyUI

class LollmsComfyUI(LollmsTTI):
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
                    "name": "max_retries",
                    "type": "int",
                    "value": 50,
                    "help": "The maximum number of retries to attempt before determining that the service is unavailable."
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
                }
            ]),
            BaseConfig(config={
            })
        )
        super().__init__("comfyui",app, service_config)
        # Get the current directory
        lollms_paths = app.lollms_paths
        self.app = app
        root_dir = lollms_paths.personal_path
        
        # If this is requiring a local service then verify if it is on
        if self.service_config.local_service:
            if not self.verify_comfyui():
                self.install()

        self.comfyui_url = self.service_config.base_url+"/comfyuiapi/v1"
        shared_folder = root_dir/"shared"
        self.comfyui_folder = shared_folder / "comfyui"
        self.output_dir = root_dir / "outputs/comfyui"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        ASCIIColors.red(" _      ____  _      _      __  __  _____  _____                 __             _ ")
        ASCIIColors.red("| |    / __ \| |    | |    |  \/  |/ ____|/ ____|               / _|           (_)")
        ASCIIColors.red("| |   | |  | | |    | |    | \  / | (___ | |     ___  _ __ ___ | |_ _   _ _   _ _ ")
        ASCIIColors.red("| |   | |  | | |    | |    | |\/| |\___ \| |    / _ \| '_ ` _ \|  _| | | | | | | |")
        ASCIIColors.red("| |___| |__| | |____| |____| |  | |____) | |___| (_) | | | | | | | | |_| | |_| | |")
        ASCIIColors.red("|______\____/|______|______|_|  |_|_____/ \_____\___/|_| |_| |_|_|  \__, |\__,_|_|")
        ASCIIColors.red("                                     ______                         __/ |         ")
        ASCIIColors.red("                                    |______|                       |___/          ")

        ASCIIColors.red(" Forked from comfyanonymous's Comfyui nodes system")
        ASCIIColors.red(" Integration in lollms by ParisNeo")

        if not self.wait_for_service(1,False) and self.service_config.local_service and self.service_config.start_service_at_startup and self.service_config.base_url is None:
            ASCIIColors.info("Loading lollms_comfyui")
            if platform.system() == "Windows":
                ASCIIColors.info("Running on windows")
                script_path = self.comfyui_folder / "main.py"

                if self.service_config.share:
                    pass # TODO: implement
                    #run_python_script_in_env("comfyui", str(script_path), cwd=self.comfyui_folder, wait=False)
                    # subprocess.Popen("conda activate " + str(script_path) +" --share", cwd=self.comfyui_folder)
                else:
                    pass # TODO: implement
                    # run_python_script_in_env("comfyui", str(script_path), cwd=self.comfyui_folder, wait=False)
                    # subprocess.Popen(script_path, cwd=self.comfyui_folder)
            else:
                ASCIIColors.info("Running on linux/MacOs")
                script_path = str(self.comfyui_folder / "lollms_comfyui.sh")
                ASCIIColors.info(f"launcher path: {script_path}")
                ASCIIColors.info(f"comfyui path: {self.comfyui_folder}")

                if self.service_config.share:
                    pass # TODO: implement
                    # run_script_in_env("comfyui","bash " + script_path +" --share", cwd=self.comfyui_folder)
                    # subprocess.Popen("conda activate " + str(script_path) +" --share", cwd=self.comfyui_folder)
                else:
                    pass # TODO: implement
                    # run_script_in_env("comfyui","bash " + script_path, cwd=self.comfyui_folder)
                ASCIIColors.info("Process done")
                ASCIIColors.success("Launching Comfyui succeeded")

        # Wait until the service is available at http://127.0.0.1:8188//

    def verify_comfyui(self):
        # Clone repository
        root_dir = self.app.lollms_paths.personal_path
        shared_folder = root_dir/"shared"
        comfyui_folder = shared_folder / "comfyui"
        return comfyui_folder.exists()
    
    def install(self):
        root_dir = self.app.lollms_paths.personal_path
        shared_folder = root_dir/"shared"
        comfyui_folder = shared_folder / "comfyui"
        if comfyui_folder.exists():
            if show_yes_no_dialog("warning!","I have detected that there is a previous installation of Comfyui.\nShould I remove it and continue installing?"):
                shutil.rmtree(comfyui_folder)
            elif show_yes_no_dialog("warning!","Continue installation?"):
                ASCIIColors.cyan("Installing comfyui conda environment with python 3.10")
                create_conda_env("comfyui","3.10")
                ASCIIColors.cyan("Done")
                return
            else:
                return

        subprocess.run(["git", "clone", "https://github.com/ParisNeo/ComfyUI.git", str(comfyui_folder)])
        subprocess.run(["git", "clone", "https://github.com/ParisNeo/ComfyUI-Manager.git", str(comfyui_folder/"custom_nodes/ComfyUI-Manager")])    
        subprocess.run(["git", "clone", "https://github.com/AlekPet/ComfyUI_Custom_Nodes_AlekPet.git", str(comfyui_folder/"custom_nodes/ComfyUI_Custom_Nodes_AlekPet")])
        subprocess.run(["git", "clone", "https://github.com/ParisNeo/lollms_nodes_suite.git", str(comfyui_folder/"custom_nodes/lollms_nodes_suite")])


        subprocess.run(["git", "clone", "https://github.com/jags111/efficiency-nodes-comfyui.git", str(comfyui_folder/"custom_nodes/efficiency-nodes-comfyui")]) 
        subprocess.run(["git", "clone", "https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet.git", str(comfyui_folder/"custom_nodes/ComfyUI-Advanced-ControlNet")]) 
        subprocess.run(["git", "clone", "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git", str(comfyui_folder/"custom_nodes/ComfyUI-VideoHelperSuite")]) 
        subprocess.run(["git", "clone", "https://github.com/LykosAI/ComfyUI-Inference-Core-Nodes.git", str(comfyui_folder/"custom_nodes/ComfyUI-Inference-Core-Nodes")]) 
        subprocess.run(["git", "clone", "https://github.com/Fannovel16/comfyui_controlnet_aux.git", str(comfyui_folder/"custom_nodes/comfyui_controlnet_aux")]) 
        subprocess.run(["git", "clone", "https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git", str(comfyui_folder/"custom_nodes/ComfyUI-AnimateDiff-Evolved")]) 

        if show_yes_no_dialog("warning!","You will need to install an image generation model.\nDo you want to install an image model from civitai?\nI suggest Juggernaut XL.\nIt is a very good model.\nyou can always install more models afterwards in your comfyui folder/models.checkpoints"):
            download_file("https://civitai.com/api/download/models/357609", comfyui_folder/"models/checkpoints","Juggernaut_XL.safetensors")

        if show_yes_no_dialog("warning!","Do you want to install a video model from hugging face?\nIsuggest SVD XL."):
            download_file("https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt/blob/main/svd_xt.safetensors", comfyui_folder/"models/checkpoints","svd_xt.safetensors")

        if show_yes_no_dialog("warning!","Do you want to install all control net models?"):
            (comfyui_folder/"models/controlnet").mkdir(parents=True, exist_ok=True)        
            download_file("https://huggingface.co/thibaud/controlnet-openpose-sdxl-1.0/resolve/main/OpenPoseXL2.safetensors", comfyui_folder/"models/controlnet","OpenPoseXL2.safetensors")
            download_file("https://huggingface.co/diffusers/controlnet-depth-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors", comfyui_folder/"models/controlnet","DepthMap_XL.safetensors")


        if show_yes_no_dialog("warning!","Do you want to install all animation models?"):
            (comfyui_folder/"models/animatediff_models").mkdir(parents=True, exist_ok=True)
            download_file("https://huggingface.co/guoyww/animatediff/resolve/cd71ae134a27ec6008b968d6419952b0c0494cf2/mm_sdxl_v10_beta.ckpt", comfyui_folder/"models/animatediff_models","mm_sdxl_v10_beta.ckpt")
            
        # TODO: fix
        # create_conda_env("comfyui","3.10")
        # if self.app.config.hardware_mode in ["nvidia", "nvidia-tensorcores"]:
        #     run_python_script_in_env("comfyui", "-m pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121")
        # if self.app.config.hardware_mode in ["amd", "amd-noavx"]:
        #     run_python_script_in_env("comfyui", "-m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7")
        # elif self.app.config.hardware_mode in ["cpu", "cpu-noavx"]:
        #     run_python_script_in_env("comfyui", "-m pip install --pre torch torchvision torchaudio")
        # run_python_script_in_env("comfyui", f"-m pip install -r {comfyui_folder}/requirements.txt")
        
        self.app.comfyui = LollmsComfyUI(self.app)
        ASCIIColors.green("Comfyui installed successfully")
        self.app.HideBlockingMessage()


    def upgrade(self):
        root_dir = self.app.lollms_paths.personal_path
        shared_folder = root_dir/"shared"
        comfyui_folder = shared_folder / "comfyui"
        if not comfyui_folder.exists():
            self.app.InfoMessage("Comfyui is not installed, install it first")
            return

        subprocess.run(["git", "pull", str(comfyui_folder)])
        subprocess.run(["git", "pull", str(comfyui_folder/"custom_nodes/ComfyUI-Manager")])
        subprocess.run(["git",  "pull", str(comfyui_folder/"custom_nodes/efficiency-nodes-comfyui")])
        ASCIIColors.success("DONE")


    def wait_for_service_in_another_thread(self, max_retries=150, show_warning=True):
        thread = threading.Thread(target=self.wait_for_service, args=(max_retries, show_warning))
        thread.start()
        return thread
    
    @staticmethod
    def get_models_list(app):
        return [str(f.name) for f in (app.lollms_paths.personal_path/"shared"/"comfyui"/"models"/"checkpoints").iterdir()]

    def wait_for_service(self, max_retries = 50, show_warning=True):
        url = f"{self.comfyui_base_url}"
        # Adjust this value as needed
        retries = 0

        while retries < max_retries or max_retries<0:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    print("Service is available.")
                    if self.app is not None:
                        self.app.success("Comfyui Service is now available.")
                    return True
            except requests.exceptions.RequestException:
                pass

            retries += 1
            time.sleep(1)
        if show_warning:
            print("Service did not become available within the given time.")
            if self.app is not None:
                self.app.error("Comfyui Service did not become available within the given time.")
        return False
            
    def paint(
                self,
                positive_prompt,
                negative_prompt,
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
        if output_path is None:
            output_path = self.output_dir
        client_id = str(uuid.uuid4())
        url = self.comfyui_base_url[7:-1]

        def queue_prompt(prompt):
            p = {"prompt": prompt, "client_id": client_id}
            data = json.dumps(p).encode('utf-8')
            full_url = "http://{}/prompt".format(url)
            req =  request.Request(full_url, data=data)
            output = request.urlopen(req).read()
            return json.loads(output)

        def get_image(filename, subfolder):
            data = {"filename": filename, "subfolder": subfolder}
            url_values = parse.urlencode(data)
            full_url = "http://{}/view?{}".format(url, url_values)
            with request.urlopen(full_url) as response:
                return response.read()

        def get_history(prompt_id):
            url_values = "http://{}/history/{}".format(url, prompt_id)
            with request.urlopen(url_values) as response:
                return json.loads(response.read())

        def get_images(ws, prompt):
            prompt_id = queue_prompt(prompt)['prompt_id']
            output_images = {}
            while True:
                out = ws.recv()
                if isinstance(out, str):
                    message = json.loads(out)
                    if message['type'] == 'executing':
                        data = message['data']
                        if data['node'] is None and data['prompt_id'] == prompt_id:
                            break #Execution is done
                else:
                    continue #previews are binary data

            history = get_history(prompt_id)[prompt_id]
            for o in history['outputs']:
                for node_id in history['outputs']:
                    node_output = history['outputs'][node_id]
                    if 'images' in node_output:
                        images_output = []
                        for image in node_output['images']:
                            if image["type"]=="output":
                                image_data = get_image(image['filename'], image['subfolder'])
                                images_output.append(image_data)

            return images_output
        
        def save_images(images:dict, folder_path:str|Path):
            # Create the folder if it doesn't exist
            folder = Path(folder_path)
            folder.mkdir(parents=True, exist_ok=True)
            
            # Save each image to the folder
            for i, img_data in enumerate(images):
                img_path = folder / f'image_{i+1}.png'
                with open(img_path, 'wb') as img_file:
                    img_file.write(img_data)
        
            # Return the path to the first image
            return str(folder / 'image_1.png')
        prompt_text = """
        {
        "1": {
            "inputs": {
            "base_ckpt_name": "juggernaut.safetensors",
            "base_clip_skip": -2,
            "refiner_ckpt_name": "None",
            "refiner_clip_skip": -2,
            "positive_ascore": 6,
            "negative_ascore": 2,
            "vae_name": "Baked VAE",
            "positive": "smart robot icon, slick, flat design, high res, W in the center, black background",
            "negative": "ugly, deformed, badly rendered, fuzzy",
            "token_normalization": "none",
            "weight_interpretation": "comfy",
            "empty_latent_width": 1024,
            "empty_latent_height": 1024,
            "batch_size": 1
            },
            "class_type": "Eff. Loader SDXL",
            "_meta": {
            "title": "Eff. Loader SDXL"
            }
        },
        "2": {
            "inputs": {
            "noise_seed": 74738751167752,
            "steps": 20,
            "cfg": 7,
            "sampler_name": "euler",
            "scheduler": "normal",
            "start_at_step": 0,
            "refine_at_step": -1,
            "preview_method": "auto",
            "vae_decode": "true",
            "sdxl_tuple": [
                "1",
                0
            ],
            "latent_image": [
                "1",
                1
            ],
            "optional_vae": [
                "1",
                2
            ]
            },
            "class_type": "KSampler SDXL (Eff.)",
            "_meta": {
            "title": "KSampler SDXL (Eff.)"
            }
        },
        "3": {
            "inputs": {
            "filename_prefix": "ComfyUI",
            "images": [
                "2",
                3
            ]
            },
            "class_type": "SaveImage",
            "_meta": {
            "title": "Save Image"
            }
        }
        }
        """
            

        prompt = json.loads(prompt_text)
        #set the text prompt for our positive CLIPTextEncode
        prompt["1"]["inputs"]["positive"] = prompt_text
        prompt["1"]["inputs"]["negative"] = negative_prompt
        prompt["1"]["inputs"]["empty_latent_width"] = width
        prompt["1"]["inputs"]["empty_latent_height"] = height
        
        prompt["1"]["inputs"]["base_ckpt_name"] = self.app.config.comfyui_model
        
        ws = websocket.WebSocket()
        ws.connect("ws://{}/ws?clientId={}".format(url, client_id))
        images = get_images(ws, prompt)
        
        return save_images(images, output_path), {"prompt":prompt,"negative_prompt":negative_prompt}
        
    
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
        return None
    
