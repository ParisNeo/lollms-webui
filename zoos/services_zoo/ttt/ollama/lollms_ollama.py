# Title Ollama service
# Licence: MIT
# Author : Paris Neo
# This is a service launcher for the ollama server by Jeffrey Morgan (jmorganca)
# check it out : https://github.com/jmorganca/ollama
# Here is a copy of the LICENCE https://github.com/jmorganca/ollama/blob/main/LICENSE
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
from lollms.utilities import git_pull, show_yes_no_dialog
import subprocess
import platform


def verify_ollama(lollms_paths:LollmsPaths):
    # Clone repository

    root_dir = lollms_paths.personal_path
    shared_folder = root_dir/"shared"
    sd_folder = shared_folder / "auto_sd"
    return sd_folder.exists()
    

def install_ollama(lollms_app:LollmsApplication):
    import platform
    import os
    import shutil
    import urllib.request
    import subprocess
    from pathlib import Path

    if show_yes_no_dialog("Info","You have asked to download and install ollama on your system.\nOllama is a separate tool that servs a variaty of llms and lollms can use it as one of its bindings.\nIf you already have it installed, you can press No.\nYou can install it manually from their webite ollama.com.\nPress yes If you want to install it automatically now.\n"):
        system = platform.system()
        download_folder = Path.home() / "Downloads"

        if system == "Windows":
            url = "https://ollama.com/download/OllamaSetup.exe"
            filename = "OllamaSetup.exe"
            urllib.request.urlretrieve(url, download_folder / filename)
            install_process = subprocess.Popen([str(download_folder / filename)])
            install_process.wait()

        elif system == "Linux":
            url = "https://ollama.com/install.sh"
            filename = "install.sh"
            urllib.request.urlretrieve(url, download_folder / filename)
            os.chmod(download_folder / filename, 0o755)
            install_process = subprocess.Popen([str(download_folder / filename)])
            install_process.wait()

        elif system == "Darwin":
            url = "https://ollama.com/download/Ollama-darwin.zip"
            filename = "Ollama-darwin.zip"
            urllib.request.urlretrieve(url, download_folder / filename)
            shutil.unpack_archive(download_folder / filename, extract_dir=download_folder)
            install_process = subprocess.Popen([str(download_folder / "Ollama-darwin" / "install.sh")])
            install_process.wait()

        else:
            print("Unsupported operating system.")

class Service:
    def __init__(
                    self, 
                    app:LollmsApplication,
                    base_url="http://127.0.0.1:11434",
                    wait_max_retries = 5,
                    wait_for_service=True
                ):
        self.base_url = base_url
        # Get the current directory
        lollms_paths = app.lollms_paths
        self.app = app
        root_dir = lollms_paths.personal_path
      
        ASCIIColors.red(" __    _____ __    __    _____ _____       _____ __    __    _____ _____ _____ ")
        ASCIIColors.red("|  |  |     |  |  |  |  |     |   __|     |     |  |  |  |  |  _  |     |  _  |")
        ASCIIColors.red("|  |__|  |  |  |__|  |__| | | |__   |     |  |  |  |__|  |__|     | | | |     |")
        ASCIIColors.red("|_____|_____|_____|_____|_|_|_|_____|_____|_____|_____|_____|__|__|_|_|_|__|__|")
        ASCIIColors.red("                                    |_____|                                    ")

        ASCIIColors.red(" Launching ollama service by Jeffrey Morgan (jmorganca)")
        ASCIIColors.red(" Integration in lollms by ParisNeo")

        if not self.wait_for_service(1,False) and base_url is None:
            ASCIIColors.info("Loading ollama service")

        # Wait until the service is available at http://127.0.0.1:7860/
        if wait_for_service:
            self.wait_for_service(max_retries=wait_max_retries)
        else:
            ASCIIColors.warning("We are not waiting for the OLLAMA service to be up.\nThis means that you may need to wait a bit before you can use it.")

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
                        self.app.success("Ollama Service is now available.")
                    return True
            except requests.exceptions.RequestException:
                pass

            retries += 1
            time.sleep(1)
        if show_warning:
            print("Service did not become available within the given time.\nThis may be a normal behavior as it depends on your system performance. Maybe you should wait a little more before using the ollama client as it is not ready yet\n")
            if self.app is not None:
                self.app.error("Ollama Service did not become available within the given time.")
        return False
