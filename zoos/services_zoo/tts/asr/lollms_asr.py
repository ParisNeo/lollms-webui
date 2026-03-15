# Title LollmsASR
# Licence: MIT
# Author : Paris Neo
# Adapted from the work of  ahmetoner's whisper-asr-webservice
# check it out : https://github.com/ahmetoner/whisper-asr-webservice
# Here is a copy of the LICENCE https://github.com/ahmetoner/whisper-asr-webservice/blob/main/LICENCE
# All rights are reserved

from pathlib import Path
import sys
from lollms.app import LollmsApplication
from lollms.paths import LollmsPaths
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
from lollms.utilities import PackageManager
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
import threading
from dataclasses import dataclass
from PIL import Image, PngImagePlugin
from enum import Enum
from typing import List, Dict, Any
import uuid

from ascii_colors import ASCIIColors, trace_exception
from lollms.paths import LollmsPaths
from lollms.utilities import git_pull, show_yes_no_dialog, run_python_script_in_env, create_conda_env, run_pip_in_env, environment_exists
import subprocess
import platform

def verify_asr(lollms_paths:LollmsPaths):
    # Clone repository
    root_dir = lollms_paths.personal_path
    shared_folder = root_dir/"shared"
    asr_path = shared_folder / "asr"
    return asr_path.exists()
    
def install_asr(lollms_app:LollmsApplication):
    ASCIIColors.green("asr installation started")
    repo_url = "https://github.com/ParisNeo/whisper-asr-webservice.git"
    root_dir = lollms_app.lollms_paths.personal_path
    shared_folder = root_dir/"shared"
    asr_path = shared_folder / "asr"

    # Step 1: Clone or update the repository
    if os.path.exists(asr_path):
        print("Repository already exists. Pulling latest changes...")
        try:
            subprocess.run(["git", "-C", asr_path, "pull"], check=True)
        except:
            subprocess.run(["git", "clone", repo_url, asr_path], check=True)

    else:
        print("Cloning repository...")
        subprocess.run(["git", "clone", repo_url, asr_path], check=True)

    # Step 2: Create or update the Conda environment
    if environment_exists("asr"):
        print("Conda environment 'asr' already exists. Updating...")
        # Here you might want to update the environment, e.g., update Python or dependencies
        # This step is highly dependent on how you manage your Conda environments and might involve
        # running `conda update` commands or similar.
    else:
        print("Creating Conda environment 'asr'...")
        create_conda_env("asr", "3.10")

    # Step 3: Install or update dependencies using your custom function
    requirements_path = os.path.join(asr_path, "requirements.txt")
    run_pip_in_env("asr", f"install .", cwd=asr_path)

    # Step 4: Launch the server
    # Assuming the server can be started with a Python script in the cloned repository
    print("Launching asr API server...")
    run_python_script_in_env("asr", "asr_api_server", cwd=asr_path)

    print("asr API server setup and launch completed.")
    ASCIIColors.cyan("Done")
    ASCIIColors.cyan("Installing asr-api-server")
    ASCIIColors.green("asr server installed successfully")



def get_asr(lollms_paths:LollmsPaths):
    root_dir = lollms_paths.personal_path
    shared_folder = root_dir/"shared"
    asr_path = shared_folder / "asr"
    asr_script_path = asr_path / "lollms_asr.py"
    git_pull(asr_path)
    
    if asr_script_path.exists():
        ASCIIColors.success("lollms_asr found.")
        ASCIIColors.success("Loading source file...",end="")
        # use importlib to load the module from the file path
        from lollms.services.asr.lollms_asr import LollmsASR
        ASCIIColors.success("ok")
        return LollmsASR

class LollmsASR:
    has_controlnet = False
    def __init__(
                    self, 
                    app:LollmsApplication, 
                    asr_base_url=None,
                    share=False,
                    max_retries=20,
                    wait_for_service=True
                ):
        self.generation_threads = []
        self.ready = False
        if asr_base_url=="" or asr_base_url=="http://127.0.0.1:9000":
            asr_base_url = None
        # Get the current directory
        lollms_paths = app.lollms_paths
        self.app = app
        root_dir = lollms_paths.personal_path
        
        # Store the path to the script
        if asr_base_url is None:
            self.asr_base_url = "http://127.0.0.1:9000"
            if not verify_asr(lollms_paths):
                install_asr(app.lollms_paths)
        else:
            self.asr_base_url = asr_base_url

        self.auto_asr_url = self.asr_base_url+"/asr"
        shared_folder = root_dir/"shared"
        self.asr_path = shared_folder / "asr"
        ASCIIColors.red(" _           _      _     ___  ___       ___   ___________ ")
        ASCIIColors.red("| |         | |    | |    |  \/  |      / _ \ /  ___| ___ \ ")
        ASCIIColors.red("| |     ___ | |    | |    | .  . |___  / /_\ \\ `--.| |_/ /")
        ASCIIColors.red("| |    / _ \| |    | |    | |\/| / __| |  _  | `--. \    / ")
        ASCIIColors.red("| |___| (_) | |____| |____| |  | \__ \ | | | |/\__/ / |\ \ ")
        ASCIIColors.red("\_____/\___/\_____/\_____/\_|  |_/___/ \_| |_/\____/\_| \_|")
        ASCIIColors.red("                                   ______                  ")
        ASCIIColors.red("                                  |______|                 ")
                                                         
        ASCIIColors.red(" Forked from ahmetoner's asr server")
        ASCIIColors.red(" Integration in lollms by ParisNeo using  ahmetoner's webapi")
        ASCIIColors.red(" Address :",end="")
        ASCIIColors.yellow(f"{self.asr_base_url}")

        self.output_folder = app.lollms_paths.personal_outputs_path/"audio_out"
        self.output_folder.mkdir(parents=True, exist_ok=True)

        if not self.wait_for_service(1,False):
            ASCIIColors.info("Loading lollms_asr")
            # Launch the Flask service using the appropriate script for the platform
            self.process = self.run_asr_api_server()

        # Wait until the service is available at http://127.0.0.1:9000/
        if wait_for_service:
            self.wait_for_service()
        else:
            self.wait_for_service_in_another_thread(max_retries=max_retries)


    def run_asr_api_server(self):
        # Get the path to the current Python interpreter
        ASCIIColors.yellow("Loading asr ")
        process = run_python_script_in_env("asr", f"app/webservice.py", wait= False, cwd=self.asr_path)
        return process

    def wait_for_service_in_another_thread(self, max_retries=150, show_warning=True):
        thread = threading.Thread(target=self.wait_for_service, args=(max_retries, show_warning))
        thread.start()
        return thread

    def wait_for_service(self, max_retries = 150, show_warning=True):
        print(f"Waiting for asr service (max_retries={max_retries})")
        url = f"{self.asr_base_url}/languages"
        # Adjust this value as needed
        retries = 0

        while retries < max_retries or max_retries<0:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    print(f"voices_folder is {self.voices_folder}.")
                    if self.voices_folder is not None:
                        print("Generating sample audio.")
                        voice_file =  [v for v in self.voices_folder.iterdir() if v.suffix==".wav"]
                        self.tts_audio("asr is ready",voice_file[0].name)
                    print("Service is available.")
                    if self.app is not None:
                        self.app.success("asr Service is now available.")
                    self.ready = True
                    return True
            except Exception as ex:
                trace_exception(ex)

            retries += 1
            ASCIIColors.yellow("Waiting for asr...")
            time.sleep(5)

        if show_warning:
            print("Service did not become available within the given time.")
            if self.app is not None:
                self.app.error("asr Service did not become available within the given time.")
        return False

