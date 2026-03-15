# Title tgi service
# Licence: MIT
# Author : Paris Neo
# This is a service launcher for the tgi server by Jeffrey Morgan (jmorganca)
# check it out : https://github.com/jmorganca/tgi
# Here is a copy of the LICENCE https://github.com/jmorganca/tgi/blob/main/LICENSE
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

from ascii_colors import ASCIIColors, trace_exception
from lollms.paths import LollmsPaths
from lollms.utilities import git_pull
import subprocess
import platform
import shutil

def verify_tgi(lollms_paths:LollmsPaths):
    # Clone repository

    root_dir = lollms_paths.personal_path
    shared_folder = root_dir/"shared"
    tgi_folder = shared_folder / "tgi"
    return tgi_folder.exists()
    

def install_tgi(lollms_app:LollmsApplication):
    root_dir = lollms_app.lollms_paths.personal_path
    shared_folder = root_dir/"shared"
    tgi_folder = shared_folder / "tgi"
    subprocess.run(["", "https://github.com/ParisNeo/stable-diffusion-webui.git", str(tgi_folder)])
    subprocess.run(["git", "clone", "https://github.com/ParisNeo/stable-diffusion-webui.git", str(tgi_folder)])


    return True
class Service:
    def __init__(
                    self, 
                    app:LollmsApplication,
                    base_url="http://127.0.0.1:11434",
                    wait_max_retries = 5
                ):
        self.base_url = base_url
        # Get the current directory
        lollms_paths = app.lollms_paths
        self.app = app
        root_dir = lollms_paths.personal_path

        ASCIIColors.red("  _           _      _      __  __  _____ _______ _____ _____ ")
        ASCIIColors.red(" | |         | |    | |    |  \/  |/ ____|__   __/ ____|_   _|")
        ASCIIColors.red(" | |     ___ | |    | |    | \  / | (___    | | | |  __  | |  ")
        ASCIIColors.red(" | |    / _ \| |    | |    | |\/| |\___ \   | | | | |_ | | |  ")
        ASCIIColors.red(" | |___| (_) | |____| |____| |  | |____) |  | | | |__| |_| |_ ")
        ASCIIColors.red(" |______\___/|______|______|_|  |_|_____/   |_|  \_____|_____|")
        ASCIIColors.red("                                      ______                  ")
        ASCIIColors.red("                                     |______|                 ")
      
        ASCIIColors.red(" Launching tgi service by Hugging face")
        ASCIIColors.red(" Integration in lollms by ParisNeo")

        if not self.wait_for_service(1,False) and base_url is None:
            ASCIIColors.info("Loading tgi service")

        # run tgi
        if platform.system() == 'Windows':
            subprocess.Popen(['wsl', 'bash', '~/run_tgi.sh'])
        else:
            subprocess.Popen(['bash', f'{Path.home()}/run_tgi.sh'])

        # Wait until the service is available at http://127.0.0.1:7860/
        self.wait_for_service(max_retries=wait_max_retries)

    def wait_for_service(self, max_retries = 150, show_warning=True):
        url = f"{self.base_url}"
        # Adjust this value as needed
        retries = 0

        while retries < max_retries or max_retries<0:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    print("Service is available.")
                    if self.app is not None:
                        self.app.success("tgi Service is now available.")
                    return True
            except requests.exceptions.RequestException:
                pass

            retries += 1
            time.sleep(1)
        if show_warning:
            print("Service did not become available within the given time.")
            if self.app is not None:
                self.app.error("tgi Service did not become available within the given time.")
        return False
