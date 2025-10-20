
######
# Project       : lollms
# File          : utilities.py
# Author        : ParisNeo with the help of the community
# license       : Apache 2.0
# Description   : 
# This file contains utilities functions that can be used by any
# module.
######
from ascii_colors import ASCIIColors, trace_exception
import numpy as np
from pathlib import Path
import json
import re
import subprocess
import gc
import shutil

from typing import List, Optional

import requests
from io import BytesIO
import base64
import importlib
import yaml

import asyncio

import ctypes
import io
import urllib
import os
import sys
import git

import mimetypes
import sys
import platform
import subprocess
import pkg_resources
from functools import partial
import sys
import pipmaster as pm

pm.install_if_missing("PyQt5")

from PyQt5.QtWidgets import QApplication, QButtonGroup, QRadioButton, QVBoxLayout, QWidget, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

import os
import subprocess
import sys
import platform
from enum import Enum
from pathlib import Path
import shutil

from pathlib import Path
import sys
import subprocess
from typing import Union, List

# Pre-compile regex for efficiency
# Characters typically invalid in filenames across OSes + ASCII control characters
_INVALID_FILENAME_CHARS_RE = re.compile(r'[<>:"/\\|?*\x00-\x1F]')
# Reserved filenames in Windows (case-insensitive)
_WINDOWS_RESERVED_NAMES_RE = re.compile(
    r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$", re.IGNORECASE
)
# Matches one or more dots or spaces at the beginning or end of a string
_LEADING_TRAILING_DOTS_SPACES_RE = re.compile(r"^[. ]+|[. ]+$")

def safe_filename(
    filename: str,
    replacement: str = '_',
    max_len: int = 200,
    default_name: str = "unnamed_file"
) -> str:
    """
    Sanitizes a string to create a safe filename for most operating systems.

    This function performs several steps:
    1. Converts input to string.
    2. Replaces characters invalid in Windows/Linux/macOS filenames with `replacement`.
    3. Removes leading and trailing periods and spaces (problematic on Windows).
    4. Truncates the filename to `max_len`.
    5. Checks if the result is empty or consists only of periods, returning `default_name` if so.
    6. Prepends `replacement` if the name matches a reserved Windows filename (e.g., CON, PRN).

    Args:
        filename: The original string to sanitize.
        replacement: Character(s) to substitute for invalid characters. Defaults to '_'.
        max_len: The maximum allowed length for the final filename. Defaults to 200.
        default_name: The name returned if sanitization results in an empty or invalid string.
                      Defaults to "unnamed_file".

    Returns:
        A sanitized string suitable for use as a filename component.
    """
    if not isinstance(filename, str):
        filename = str(filename) # Ensure we're working with a string

    # 1. Replace invalid characters using pre-compiled regex
    sanitized = _INVALID_FILENAME_CHARS_RE.sub(replacement, filename)

    # 2. Remove leading/trailing dots and spaces
    sanitized = _LEADING_TRAILING_DOTS_SPACES_RE.sub('', sanitized)

    # 3. Truncate to maximum length
    if len(sanitized) > max_len:
        sanitized = sanitized[:max_len]
        # Re-apply step 2 in case truncation created trailing dots/spaces
        sanitized = _LEADING_TRAILING_DOTS_SPACES_RE.sub('', sanitized)

    # 4. Check if the result is empty or only periods (edge case)
    if not sanitized or all(c == '.' for c in sanitized):
        return default_name

    # 5. Check against reserved Windows names (case-insensitive)
    if _WINDOWS_RESERVED_NAMES_RE.match(sanitized):
        sanitized = replacement + sanitized
        # Re-truncate if the prefix made it too long
        if len(sanitized) > max_len:
            sanitized = sanitized[:max_len]
            # Re-apply step 2 again after potential truncation
            sanitized = _LEADING_TRAILING_DOTS_SPACES_RE.sub('', sanitized)


    # Final check for empty string after all modifications
    if not sanitized:
        return default_name

    return sanitized


import requests
from pathlib import Path
from typing import Union, Optional, Callable
import tqdm # Use tqdm for progress bar if available

# ... (other utility functions like get_torch_device, etc.)

def download_file(url: str, destination_path: Union[str, Path], progress_callback: Optional[Callable[[str], None]] = None, chunk_size=8192) -> bool:
    """
    Downloads a file from a URL to a destination path with progress reporting.

    Args:
        url: The URL of the file to download.
        destination_path: The local path (string or Path object) where the file should be saved.
        progress_callback: An optional function to call with progress messages (e.g., percentage).
                           Takes a single string argument.
        chunk_size: The chunk size for downloading data.

    Returns:
        True if the download was successful, False otherwise.
    """
    dest_path = Path(destination_path)
    # Ensure the destination directory exists
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        if progress_callback:
            progress_callback(f"Error creating directory {dest_path.parent}: {e}")
        print(f"Error creating directory {dest_path.parent}: {e}") # Also print to console
        return False

    try:
        # Use a session for potential connection pooling benefits
        with requests.Session() as session:
            response = session.get(url, stream=True, timeout=30) # Add timeout
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            total_size_in_bytes = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            if progress_callback:
                progress_callback(f"Starting download of {dest_path.name} from {url}")

            # Use tqdm for a visual progress bar if available and no callback is provided
            progress_bar = None
            if not progress_callback and PackageManager.check_package_installed("tqdm"):
                 try:
                     progress_bar = tqdm.tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=f"Downloading {dest_path.name}")
                 except Exception:
                     progress_bar = None # Fallback if tqdm fails


            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:  # filter out keep-alive new chunks
                        chunk_len = len(chunk)
                        f.write(chunk)
                        downloaded_size += chunk_len

                        if progress_bar:
                             progress_bar.update(chunk_len)
                        elif progress_callback:
                            if total_size_in_bytes > 0:
                                progress = (downloaded_size / total_size_in_bytes) * 100
                                # Report progress less frequently to avoid flooding logs/UI
                                if downloaded_size % (chunk_size * 10) == 0 or downloaded_size == total_size_in_bytes:
                                    progress_callback(f"Downloading {dest_path.name}: {progress:.1f}% ({downloaded_size/1024/1024:.2f}MB / {total_size_in_bytes/1024/1024:.2f}MB)")
                            else:
                                # Report progress based on downloaded size if total unknown
                                if downloaded_size % (chunk_size * 50) == 0: # Report every ~400KB
                                     progress_callback(f"Downloading {dest_path.name}: {downloaded_size/1024/1024:.2f}MB downloaded (total size unknown)")

            if progress_bar:
                 progress_bar.close()

            if total_size_in_bytes != 0 and downloaded_size != total_size_in_bytes:
                if progress_callback:
                    progress_callback(f"Error: Download finished, but size mismatch! Expected {total_size_in_bytes}, got {downloaded_size}")
                print(f"Error: Download size mismatch for {dest_path.name}")
                # Optional: Delete incomplete file?
                # dest_path.unlink(missing_ok=True)
                # return False # Consider this a failure
                return True # Or consider it success but log warning

            if progress_callback:
                progress_callback(f"Successfully downloaded {dest_path.name}")
            return True

    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP Error during download: {http_err}"
        if progress_callback: progress_callback(error_msg)
        print(error_msg) # Also print
        return False
    except requests.exceptions.ConnectionError as conn_err:
        error_msg = f"Connection Error during download: {conn_err}"
        if progress_callback: progress_callback(error_msg)
        print(error_msg)
        return False
    except requests.exceptions.Timeout as timeout_err:
        error_msg = f"Timeout Error during download: {timeout_err}"
        if progress_callback: progress_callback(error_msg)
        print(error_msg)
        return False
    except requests.exceptions.RequestException as req_err:
        error_msg = f"Error during download request: {req_err}"
        if progress_callback: progress_callback(error_msg)
        print(error_msg)
        return False
    except Exception as e:
        error_msg = f"An unexpected error occurred during download: {e}"
        if progress_callback: progress_callback(error_msg)
        print(error_msg)
        # You might want to re-import trace_exception here if needed
        # from lollms.helpers import trace_exception
        # trace_exception(e)
        return False


def run_with_current_interpreter(
    script_path: Union[str, Path], 
    args: List[str] = None
) -> subprocess.CompletedProcess:
    """
    Runs a Python script using the current interpreter.
    
    Args:
        script_path: Path to the Python script to execute
        args: Optional list of arguments to pass to the script
        
    Returns:
        subprocess.CompletedProcess object containing the execution result
        
    Example:
        result = run_with_current_interpreter(Path("my_script.py"), ["arg1", "arg2"])
    """
        
    # Get current Python interpreter path
    interpreter_path = sys.executable
    
    # Prepare command
    command = [interpreter_path, str(script_path)]
    if args:
        command.extend(args)
        
    # Run the script and return the result
    return subprocess.run(
        command,
        text=True,
        check=True,  # Raises CalledProcessError if return code != 0
        stdout=None, # This will make the output go directly to console
        stderr=None  # This will make the errors go directly to console
    )

from pathlib import Path
import sys
import subprocess
from typing import Union, List, Optional

def run_module(
    module_name: str,
    args: Optional[List[str]] = None,
) -> subprocess.CompletedProcess:
    """
    Runs a Python module using the current interpreter with the -m flag and outputs to console.
    
    Args:
        module_name: Name of the module to run (e.g. 'pip', 'http.server')
        args: Optional list of arguments to pass to the module
        
    Returns:
        subprocess.CompletedProcess object containing the execution result
        
    Example:
        # Run pip list
        result = run_module("pip", ["list"])
        # Run http.server on port 8000
        result = run_module("http.server", ["8000"])
    """
    # Get current Python interpreter path
    interpreter_path = sys.executable
    
    # Prepare command
    command = [interpreter_path, "-m", module_name]
    if args:
        command.extend(args)
        
    try:
        # Run the module with direct console output
        return subprocess.run(
            command,
            text=True,
            check=True,  # Raises CalledProcessError if return code != 0
            stdout=None, # This will make the output go directly to console
            stderr=None  # This will make the errors go directly to console
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running module {module_name}")
        raise



class EnvManager(Enum):
    CONDA = 'conda'
    VENV = 'venv'
    PYENV = 'pyenv'
    PIP = 'pip'

class EnvironmentManager:
    def __init__(self, preferred_manager=None):
        """
        Initialize environment manager with optional preferred manager.
        Args:
            preferred_manager (str, optional): 'conda', 'venv', 'pyenv', or 'pip'
        """
        self.preferred_manager = EnvManager(preferred_manager) if preferred_manager else None
        self.manager = self._detect_env_manager()
        self.manager_path = self._get_env_manager_path()

    def _get_env_manager_path(self):
        """Get the path of the environment manager executable"""
        if platform.system() == 'Windows':
            ext = '.exe'
        else:
            ext = ''
        
        if self.manager == EnvManager.CONDA:
            # Check for portable conda
            portable_conda = os.getenv('PORTABLE_CONDA_PATH')
            if portable_conda:
                return os.path.join(portable_conda, 'condabin', f'conda{ext}')
            
            # Check standard conda locations
            possible_paths = [
                os.path.join(sys.prefix, 'condabin', f'conda{ext}'),
                os.path.join(os.path.expanduser('~'), 'miniconda3', 'condabin', f'conda{ext}'),
                os.path.join(os.path.expanduser('~'), 'anaconda3', 'condabin', f'conda{ext}')
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    return path
        
        # Use which/where to find the executable
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(['where', self.manager.value], capture_output=True, text=True)
            else:
                result = subprocess.run(['which', self.manager.value], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        return None

    def _detect_env_manager(self):
        """Detect which environment manager to use based on context and preference"""
        # If preferred manager is specified and available, use it
        if self.preferred_manager:
            if self._check_manager_available(self.preferred_manager):
                return self.preferred_manager
        
        # Check if we're in a venv
        if sys.prefix != sys.base_prefix:
            return EnvManager.VENV
            
        # Check for conda (both portable and installed)
        if self._check_manager_available(EnvManager.CONDA):
            return EnvManager.CONDA
            
        # Check for pyenv
        if self._check_manager_available(EnvManager.PYENV):
            return EnvManager.PYENV
            
        # Default to pip
        return EnvManager.PIP

    def _check_manager_available(self, manager):
        """Check if a specific environment manager is available"""
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(['where', manager.value], capture_output=True)
            else:
                result = subprocess.run(['which', manager.value], capture_output=True)
            return result.returncode == 0
        except:
            return False

    def _get_env_python_path(self, env_name):
        """Get the Python executable path for the environment"""
        if platform.system() == 'Windows':
            return os.path.join(env_name, 'Scripts', 'python.exe')
        return os.path.join(env_name, 'bin', 'python')

    def create_env(self, env_name, python_version):
        """
        Create a new environment with specified Python version
        Args:
            env_name (str): Name of the environment
            python_version (str): Python version to install (e.g., '3.8')
        """
        try:
            if self.manager == EnvManager.CONDA:
                subprocess.run([self.manager_path, 'create', '-n', env_name, 
                              f'python={python_version}', '-y'], check=True)
            elif self.manager == EnvManager.VENV:
                subprocess.run([f'python{python_version}', '-m', 'venv', env_name], check=True)
            elif self.manager == EnvManager.PYENV:
                subprocess.run([self.manager_path, 'install', python_version], check=True)
                subprocess.run([self.manager_path, 'virtualenv', python_version, env_name], check=True)
            else:
                subprocess.run([sys.executable, '-m', 'venv', env_name], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to create environment: {str(e)}")

    def run_pip_in_env(self, env_name, pip_args, cwd=None):
        """
        Run pip commands in the specified environment
        Args:
            env_name (str): Name of the environment
            pip_args (str): Arguments to pass to pip
            cwd (str, optional): Working directory
        """
        try:
            if self.manager == EnvManager.CONDA:
                cmd = f'"{self.manager_path}" run -n {env_name} pip {pip_args}'
            else:
                if platform.system() == 'Windows':
                    pip_path = os.path.join(env_name, 'Scripts', 'pip')
                else:
                    pip_path = os.path.join(env_name, 'bin', 'pip')
                cmd = f'"{pip_path}" {pip_args}'
            
            subprocess.run(cmd, shell=True, cwd=cwd, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to run pip: {str(e)}")

    def run_python_script_in_env(self, env_name, script_path, cwd=None, wait=True):
        """
        Run a Python script in the specified environment
        Args:
            env_name (str): Name of the environment
            script_path (str): Path to the Python script
            cwd (str, optional): Working directory
            wait (bool): Whether to wait for the script to complete
        """
        try:
            if self.manager == EnvManager.CONDA:
                cmd = f'"{self.manager_path}" run -n {env_name} python "{script_path}"'
            else:
                python_path = self._get_env_python_path(env_name)
                cmd = f'"{python_path}" "{script_path}"'
            
            if wait:
                subprocess.run(cmd, shell=True, cwd=cwd, check=True)
            else:
                subprocess.Popen(cmd, shell=True, cwd=cwd)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to run script: {str(e)}")

    def run_script_in_env(self, env_name, script_path, cwd=None):
        """
        Run any script in the specified environment
        Args:
            env_name (str): Name of the environment
            script_path (str): Path to the script
            cwd (str, optional): Working directory
        """
        try:
            if self.manager == EnvManager.CONDA:
                cmd = f'"{self.manager_path}" run -n {env_name} "{script_path}"'
            else:
                cmd = os.path.join(env_name, 'bin', script_path)
            
            subprocess.run(cmd, shell=True, cwd=cwd, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to run script: {str(e)}")

    def environment_exists(self, env_name):
        """
        Check if the specified environment exists
        Args:
            env_name (str): Name of the environment
        Returns:
            bool: True if environment exists, False otherwise
        """
        if self.manager == EnvManager.CONDA:
            result = subprocess.run([self.manager_path, 'env', 'list'], 
                                 capture_output=True, text=True)
            return env_name in result.stdout
        else:
            return os.path.exists(env_name) and os.path.isdir(env_name)

    def get_python_version(self, env_name):
        """
        Get Python version of the specified environment
        Args:
            env_name (str): Name of the environment
        Returns:
            str: Python version
        """
        try:
            if self.manager == EnvManager.CONDA:
                cmd = f'"{self.manager_path}" run -n {env_name} python --version'
            else:
                python_path = self._get_env_python_path(env_name)
                cmd = f'"{python_path}" --version'
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get Python version: {str(e)}")

    def remove_environment(self, env_name):
        """
        Remove the specified environment
        Args:
            env_name (str): Name of the environment
        """
        try:
            if self.manager == EnvManager.CONDA:
                subprocess.run([self.manager_path, 'env', 'remove', '-n', env_name, '-y'], 
                             check=True)
            elif self.manager == EnvManager.PYENV:
                subprocess.run([self.manager_path, 'virtualenv-delete', env_name], check=True)
            else:
                if os.path.exists(env_name):
                    shutil.rmtree(env_name)
        except (subprocess.CalledProcessError, OSError) as e:
            raise RuntimeError(f"Failed to remove environment: {str(e)}")

def process_ai_output(output, images, output_folder):
    if not PackageManager.check_package_installed("cv2"):
        PackageManager.install_package("opencv-python")
    import cv2
    images = [cv2.imread(str(img)) for img in images]
    # Find all bounding box entries in the output
    bounding_boxes = re.findall(r'boundingbox\((\d+), ([^,]+), ([^,]+), ([^,]+), ([^,]+), ([^,]+)\)', output)

    # Group bounding boxes by image index
    image_boxes = {}
    for box in bounding_boxes:
        image_index = int(box[0])
        if image_index not in image_boxes:
            image_boxes[image_index] = []
        image_boxes[image_index].append(box[1:])

    # Process each image and its bounding boxes
    for image_index, boxes in image_boxes.items():
        # Get the corresponding image
        image = images[image_index]

        # Draw bounding boxes on the image
        for box in boxes:
            label, left, top, width, height = box
            left, top, width, height = float(left), float(top), float(width), float(height)
            x, y, w, h = int(left * image.shape[1]), int(top * image.shape[0]), int(width * image.shape[1]), int(height * image.shape[0])
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Save the modified image
        random_stuff = np.random
        output_path = Path(output_folder)/f"image_{image_index}_{random_stuff}.jpg"
        cv2.imwrite(str(output_path), image)

    # Remove bounding box text from the output
    output = re.sub(r'boundingbox\([^)]+\)', '', output)

    # Append img tags for the generated images
    for image_index in image_boxes.keys():
        url = discussion_path_to_url(Path(output_folder)/f"image_{image_index}.jpg")
        output += f'\n<img src="{url}">'

    return output

def get_media_type(file_path):
    """
    Determines the media type of a file based on its file extension.

    Args:
        file_path (str): The path to the media file.

    Returns:
        str: The media type of the file in the format "type/subtype".
             Returns "Unknown" if the media type cannot be determined.
    """
    media_type, _ = mimetypes.guess_type(file_path)
    
    if media_type is None:
        return "Unknown"
    else:
        return media_type


def app_path_to_url(file_path:str|Path)->str:
    """
    This function takes a file path as an argument and converts it into a URL format. It first removes the initial part of the file path until the "outputs" string is reached, then replaces backslashes with forward slashes and quotes each segment with urllib.parse.quote() before joining them with forward slashes to form the final URL.

    :param file_path: str, the file path in the format of a Windows system
    :return: str, the converted URL format of the given file path
    """
    file_path = str(file_path)
    url = "/"+file_path[file_path.index("apps_zoo"):].replace("\\","/").replace("apps_zoo","apps")
    return "/".join([urllib.parse.quote(p, safe="") for p in url.split("/")])

def discussion_path_to_url(file_path:str|Path)->str:
    """
    This function takes a file path as an argument and converts it into a URL format. It first removes the initial part of the file path until the "outputs" string is reached, then replaces backslashes with forward slashes and quotes each segment with urllib.parse.quote() before joining them with forward slashes to form the final URL.

    :param file_path: str, the file path in the format of a Windows system
    :return: str, the converted URL format of the given file path
    """
    file_path = str(file_path)
    url = "/"+file_path[file_path.index("discussion_databases"):].replace("\\","/").replace("discussion_databases","discussions")
    return "/".join([urllib.parse.quote(p, safe="") for p in url.split("/")])

def outputs_path_to_url(file_path:str|Path)->str:
    """
    This function takes a file path as an argument and converts it into a URL format. It first removes the initial part of the file path until the "outputs" string is reached, then replaces backslashes with forward slashes and quotes each segment with urllib.parse.quote() before joining them with forward slashes to form the final URL.

    :param file_path: str, the file path in the format of a Windows system
    :return: str, the converted URL format of the given file path
    """
    file_path = str(file_path)
    url = "/"+file_path[file_path.index("outputs"):].replace("\\","/").replace("outputs","outputs")
    return "/".join([urllib.parse.quote(p, safe="") for p in url.split("/")])


def always_get_an_event_loop() -> asyncio.AbstractEventLoop:
    """
    Ensure that there is always an event loop available.

    This function tries to get the current event loop. If the current event loop is closed or does not exist,
    it creates a new event loop and sets it as the current event loop.

    Returns:
        asyncio.AbstractEventLoop: The current or newly created event loop.
    """
    try:
        # Try to get the current event loop
        current_loop = asyncio.get_event_loop()
        if current_loop.is_closed():
            raise RuntimeError("Event loop is closed.")
        return current_loop

    except RuntimeError:
        # If no event loop exists or it is closed, create a new one
        ASCIIColors.info("Creating a new event loop in main thread.")
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        return new_loop

def yes_or_no_input(prompt):
    while True:
        user_input = input(prompt + " (yes/no): ").lower()
        if user_input == 'yes':
            return True
        elif user_input == 'no':
            return False
        else:
            print("Please enter 'yes' or 'no'.")

def show_console_custom_dialog(title, text, options):
    print(title)
    print(text)
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def show_custom_dialog(title, text, options):
    try:
        app = QApplication(sys.argv)
        window = QWidget()
        layout = QVBoxLayout()
        window.setLayout(layout)
        
        label = QLabel(text)
        layout.addWidget(label)
        
        button_group = QButtonGroup()
        for i, option in enumerate(options):
            button = QRadioButton(option)
            button_group.addButton(button)
            layout.addWidget(button)
        
        def on_ok():
            nonlocal result
            result = [button.text() for button in button_group.buttons() if button.isChecked()]
            window.close()
        
        button = QPushButton("OK")
        button.clicked.connect(on_ok)
        layout.addWidget(button)
        
        window.show()
        result = None
        sys.exit(app.exec_())
        
        return result
    except:
        print(title)


def show_yes_no_dialog(title, text):
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Create a message box with Yes/No buttons
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # Ensure the dialog comes to the foreground
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
        msg.raise_()
        msg.activateWindow()

        # Execute the dialog and return True if 'Yes' was clicked, False otherwise
        return msg.exec_() == QMessageBox.Yes        
    except Exception as ex:
        print(f"Error: {ex}")
        return console_dialog(title, text)


def console_dialog(title, text):
    print(f"{title}\n{text}")
    while True:
        response = input("Enter 'yes' or 'no': ").lower()
        if response in ['yes', 'no']:
            return response == 'yes'
        print("Invalid input. Please enter 'yes' or 'no'.")
        
def show_message_dialog(title, text):
    try:
        app = QApplication(sys.argv)
        msg = QMessageBox()
        msg.setOption(QMessageBox.DontUseNativeDialog, True)
        msg.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(title)
        result = msg.question(None, title, text, QMessageBox.Yes | QMessageBox.No)
        return result == QMessageBox.Yes
    except:
        print(title)


def is_linux():
    return sys.platform.startswith("linux")


def is_windows():
    return sys.platform.startswith("win")


def is_macos():
    return sys.platform.startswith("darwin")

def run_cmd(cmd, assert_success=False, environment=False, capture_output=False, env=None):
    script_dir = os.getcwd()
    conda_env_path = os.path.join(script_dir, "installer_files", "env")
    # Use the conda environment
    if environment:
        if is_windows():
            conda_bat_path = os.path.join(script_dir, "installer_files", "conda", "condabin", "conda.bat")
            cmd = "\"" + conda_bat_path + "\" activate \"" + conda_env_path + "\" >nul && " + cmd
        else:
            conda_sh_path = os.path.join(script_dir, "installer_files", "conda", "etc", "profile.d", "conda.sh")
            cmd = ". \"" + conda_sh_path + "\" && conda activate \"" + conda_env_path + "\" && " + cmd

    # Run shell commands
    result = subprocess.run(cmd, shell=True, capture_output=capture_output, env=env)

    # Assert the command ran successfully
    if assert_success and result.returncode != 0:
        print("Command '" + cmd + "' failed with exit status code '" + str(result.returncode) + "'.\n\nExiting now.\nTry running the start/update script again.")
        sys.exit(1)

    return result
def output_file_path_to_url(file_path:str|Path):
    """
    This function takes a file path as an argument and converts it into a URL format. It first removes the initial part of the file path until the "outputs" string is reached, then replaces backslashes with forward slashes and quotes each segment with urllib.parse.quote() before joining them with forward slashes to form the final URL.

    :param file_path: str, the file path in the format of a Windows system
    :return: str, the converted URL format of the given file path
    """
    file_path = str(file_path)
    url = "/"+file_path[file_path.index("outputs"):].replace("\\","/")
    return "/".join([urllib.parse.quote(p, safe="") for p in url.split("/")])


def personality_path_to_url(file_path:str|Path)->str:
    """
    This function takes a file path as an argument and converts it into a URL format. It first removes the initial part of the file path until the "outputs" string is reached, then replaces backslashes with forward slashes and quotes each segment with urllib.parse.quote() before joining them with forward slashes to form the final URL.

    :param file_path: str, the file path in the format of a Windows system
    :return: str, the converted URL format of the given file path
    """
    file_path = str(file_path)
    url = "/"+file_path[file_path.index("personalities_zoo"):].replace("\\","/").replace("personalities_zoo","personalities")
    return "/".join([urllib.parse.quote(p, safe="") for p in url.split("/")])


def url2host_port(url, default_port =8000):
    if "http" in url:
        parts = url.split(":")
        host = ":".join(parts[:2])
        host_no_http = parts[1].replace("//","")
        port = url.split(":")[2] if len(parts)==3 else default_port
        return host, host_no_http, port
    else:
        parts = url.split(":")
        host = parts[0]
        port = url.split(":")[1] if len(parts)==2 else default_port
        return host, host, port

def is_asyncio_loop_running():
    """
    # This function checks if an AsyncIO event loop is currently running. If an event loop is running, it returns True. If not, it returns False.
    :return: bool, indicating whether or not an AsyncIO event loop is currently running
    """
    try:
        return asyncio.get_event_loop().is_running()
    except RuntimeError:  # This gets raised if there's no running event loop
        return False

import asyncio
from typing import Callable, Coroutine, Any
from typing import Callable, Coroutine, Any

def run_async(func: Callable[[], Coroutine[Any, Any, None]]) -> None:
    """
    run_async(func) -> None

    Utility function to run async functions in either a synchronous or asynchronous environment.
    Takes an async function as input and runs it appropriately based on the context.

    Parameters:
    func (Callable[[], Coroutine[Any, Any, None]]): The async function to run.

    Returns:
    None: Nothing is returned since the function is meant to perform side effects.
    """
    try:
        # Try to get the currently running loop (works in async context)
        loop = asyncio.get_running_loop()
        # If we're here, a loop is already running, so schedule the coroutine
        asyncio.ensure_future(func())
    except RuntimeError:
        # No running loop; we're in a synchronous context
        # Get or create an event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Edge case: loop exists and is running but get_running_loop() failed
                asyncio.ensure_future(func())
            else:
                # No running loop; run the coroutine synchronously
                loop.run_until_complete(func())
        except RuntimeError:
            # No existing loop at all; create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(func())
            finally:
                loop.close()

# Example usage
async def my_async_function():
    await asyncio.sleep(1)
    print("Async function executed!")

# From a synchronous context
def sync_caller():
    print("Calling from sync context")
    run_async(my_async_function)

# From an asynchronous context
async def async_caller():
    print("Calling from async context")
    run_async(my_async_function)
    await asyncio.sleep(2)  # Give time for the async function to complete


def terminate_thread(thread):
    """ 
    This function is used to terminate a given thread if it's currently running. If the thread is not alive, an informational message will be displayed and the function will return without raising any error. Otherwise, it sets the thread's exception to `SystemExit` using `ctypes`, which causes the thread to exit. The function collects the garbage after terminating the thread, and raises a `SystemError` if it fails to do so.
    :param thread: thread object to be terminated
    :return: None if the thread was successfully terminated or an error is raised
    :raises SystemError: if the thread could not be terminated 
    """    
    if thread:
        if not thread.is_alive():
            ASCIIColors.yellow("Thread not alive")
            return

        thread_id = thread.ident
        exc = ctypes.py_object(SystemExit)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, exc)
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, None)
            del thread
            gc.collect()
            raise SystemError("Failed to terminate the thread.")
        else:
            ASCIIColors.yellow("Canceled successfully")

def convert_language_name(language_name):
    """
    Convert a language name string to its corresponding ISO 639-1 code.
    If the given language name is not supported, returns "unsupported".

    Parameters:
    - language_name (str): A lowercase and dot-free string representing the name of a language.

    Returns:
    - str: The corresponding ISO 639-1 code for the given language name or "unsupported" if it's not supported.
    """    
    # Remove leading and trailing spaces
    language_name = language_name.strip()
    
    # Convert to lowercase
    language_name = language_name.lower().replace(".","")
    
    # Define a dictionary mapping language names to their codes
    language_codes = { 
                      "english": "en", "spanish": "es", "french": "fr", "german": "de",
                      "italian": "it", "portuguese": "pt", "russian": "ru", "mandarin": "zh-CN",
                      "korean": "ko", "japanese": "ja", "dutch": "nl", "polish": "pl",
                      "hindi": "hi", "arabic": "ar", "bengali": "bn", "swedish": "sv", "thai": "th", "vietnamese": "vi"
                    }
    
    # Return the corresponding language code if found, or None otherwise
    return language_codes.get(language_name,"en")


# Function to encode the image
def encode_image(image_path, max_image_width=-1):
    image = Image.open(image_path)
    width, height = image.size

    # Check and convert image format if needed
    if image.format not in ['PNG', 'JPEG', 'GIF', 'WEBP']:
        image = image.convert('JPEG')


    if max_image_width != -1 and width > max_image_width:
        ratio = max_image_width / width
        new_width = max_image_width
        new_height = int(height * ratio)
        f = image.format
        image = image.resize((new_width, new_height))
        image.format = f


    # Save the image to a BytesIO object
    byte_arr = io.BytesIO()
    image.save(byte_arr, format=image.format)
    byte_arr = byte_arr.getvalue()

    return base64.b64encode(byte_arr).decode('utf-8')

def load_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as stream:
        config = yaml.safe_load(stream)

    return config


def save_config(config, filepath):
    with open(filepath, "w") as f:
        yaml.dump(config, f)


def load_image(image_file):
    s_image_file = str(image_file)
    if s_image_file.startswith('http://') or s_image_file.startswith('https://'):
        response = requests.get(s_image_file)
        image = Image.open(BytesIO(response.content)).convert('RGB')
    else:
        image = Image.open(s_image_file).convert('RGB')
    return image

def load_image_from_base64(image):
    return Image.open(BytesIO(base64.b64decode(image)))


def expand2square(pil_img, background_color):
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result


def add_period(text):
    """
    Adds a period at the end of each line in the given text, except for empty lines.

    Args:
        text (str): The input text.

    Returns:
        str: The preprocessed text with a period added at the end of each line that doesn't already have one.
    """
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        if line.strip():  # Check if line is not empty
            if line[-1] != '.':
                line += '.'
        processed_lines.append(line)
    
    processed_text = '\n'.join(processed_lines)
    return processed_text

def find_next_available_filename(folder_path, prefix, extension="png"):
    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"The folder '{folder}' does not exist.")

    index = 1
    while True:
        next_filename = f"{prefix}_{index}.{extension}"
        potential_file = folder / next_filename
        if not potential_file.exists():
            return potential_file
        index += 1


def find_first_available_file_index(folder_path, prefix, extension=""):
    """
    Finds the first available file index in a folder with files that have a prefix and an optional extension.
    
    Args:
        folder_path (str): The path to the folder.
        prefix (str): The file prefix.
        extension (str, optional): The file extension (including the dot). Defaults to "".
    
    Returns:
        int: The first available file index.
    """
    # Create a Path object for the folder
    folder = Path(folder_path)
    
    # Get a list of all files in the folder
    files = folder.glob(f'{prefix}*'+extension)
    
    # Initialize the first available number
    available_number = 1
    
    # Iterate through the files
    while True:
        f = folder/f"{prefix}{available_number}{extension}"
        if f.exists():
            available_number += 1
        # If the file number is greater than the available number, break the loop
        else:
            return available_number


def find_first_available_file_path(folder_path, prefix, extension=""):
    """
    Finds the full path for the first available filename in a folder,
    based on a prefix and an optional extension.

    The numbering starts from 1 (e.g., prefix1.ext, prefix2.ext, ...).

    Args:
        folder_path (str or Path): The path to the folder.
                                   The folder will be created if it doesn't exist.
        prefix (str): The desired file prefix.
        extension (str, optional): The desired file extension (including the dot, e.g., ".txt").
                                   Defaults to "".

    Returns:
        Path: A Path object representing the first available file path
              (e.g., /path/to/folder/prefix1.txt if it doesn't exist).
              Returns None if the folder cannot be created or accessed.
    """
    try:
        # Ensure folder_path is a Path object
        folder = Path(folder_path)

        # Create the folder if it doesn't exist
        # os.makedirs(folder, exist_ok=True) # Using exist_ok=True prevents errors if it already exists
        # Using Pathlib's equivalent:
        folder.mkdir(parents=True, exist_ok=True)


        available_number = 1
        while True:
            # Construct the potential file path using an f-string
            potential_path = folder / f"{prefix}{available_number}{extension}"

            # Check if this path already exists (works for files and directories)
            if not potential_path.exists():
                # If it doesn't exist, this is the first available path
                return potential_path
            else:
                # If it exists, increment the number and try the next one
                available_number += 1
    except OSError as e:
        print(f"Error accessing or creating folder {folder_path}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred in find_first_available_file_path: {e}")
        return None

def is_file_path(path_string: Union[str, Path, None]) -> bool:
    """
    Checks if a given string or Path object structurally resembles a file path.

    This function performs basic checks:
    1. Is the input a non-empty string or Path?
    2. Does it contain path separators ('/' or '\\')?
    3. Does it likely have a filename component (doesn't end with a separator)?
    4. Does it potentially have an extension (contains a '.')?

    It does NOT check if the path actually exists on the filesystem.
    It aims to distinguish plausible file paths from simple strings, URLs (basic check),
    or paths explicitly ending like directories.

    Args:
        path_string: The string or Path object to check.

    Returns:
        True if the string looks like a file path, False otherwise.
    """
    # --- Basic Input Validation ---
    if path_string is None:
        return False

    # Convert Path object to string for consistent processing
    if isinstance(path_string, Path):
        path_string = str(path_string)

    if not isinstance(path_string, str):
        # If it's not None, not a Path, and not a string, it's invalid input
        return False

    # Remove leading/trailing whitespace
    path_string = path_string.strip()

    # Empty string is not a valid file path
    if not path_string:
        return False

    # --- Structural Checks ---

    # Very basic check to filter out obvious URLs (can be expanded if needed)
    if path_string.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
        return False

    # Check if it ends with a path separator (more likely a directory)
    # os.path.sep is the primary separator ('/' on Unix, '\' on Windows)
    # os.path.altsep is the alternative ('/' on Windows)
    ends_with_separator = path_string.endswith(os.path.sep)
    if os.path.altsep: # Check altsep only if it exists (it's None on Unix)
        ends_with_separator = ends_with_separator or path_string.endswith(os.path.altsep)

    if ends_with_separator:
        return False # Paths ending in separators usually denote directories

    # Check for the presence of path separators within the string
    has_separator = os.path.sep in path_string
    if os.path.altsep:
        has_separator = has_separator or os.path.altsep in path_string

    # Use os.path.splitext to check for an extension
    # It splits "path/to/file.txt" into ("path/to/file", ".txt")
    # It splits "path/to/file" into ("path/to/file", "")
    # It splits "path/.bashrc" into ("path/.bashrc", "") - important edge case!
    # It splits "path/archive.tar.gz" into ("path/archive.tar", ".gz")
    base, extension = os.path.splitext(path_string)

    # A simple filename like "file.txt" is a valid relative path
    # It won't have separators but will likely have an extension
    has_extension = bool(extension) and extension != '.' # Ensure extension is not just a single dot

    # Check if the part *before* the extension (or the whole string if no extension)
    # contains a '.' which might indicate a hidden file like '.bashrc' when
    # there are no separators. We need the base name for this.
    filename = os.path.basename(path_string)
    is_likely_hidden_file = filename.startswith('.') and '.' not in filename[1:] and not has_separator


    # --- Decision Logic ---
    # It looks like a file path if:
    # 1. It contains separators (e.g., "folder/file", "folder/file.txt") OR
    # 2. It has a valid extension (e.g., "file.txt") OR
    # 3. It looks like a "hidden" file in the current directory (e.g., ".bashrc")
    # AND it doesn't end with a separator (checked earlier).
    if has_separator or has_extension or is_likely_hidden_file:
        # Further refinement: Avoid matching just "." or ".."
        if path_string == '.' or path_string == '..':
            return False
        return True
    else:
        # If it has no separators and no extension (e.g., "myfile"),
        # it's ambiguous - could be a directory name or a file without extension.
        # Let's default to False for this ambiguity unless separators are present.
        return False

# Prompting tools
def detect_antiprompt(text:str, anti_prompts=["!@>"]) -> bool:
    """
    Detects if any of the antiprompts in self.anti_prompts are present in the given text.
    Used for the Hallucination suppression system

    Args:
        text (str): The text to check for antiprompts.

    Returns:
        bool: True if any antiprompt is found in the text (ignoring case), False otherwise.
    """
    for prompt in anti_prompts:
        if prompt.lower() in text.lower():
            return prompt.lower()
    return None


def remove_text_from_string(string, text_to_find):
    """
    Removes everything from the first occurrence of the specified text in the string (case-insensitive).

    Parameters:
    string (str): The original string.
    text_to_find (str): The text to find in the string.

    Returns:
    str: The updated string.
    """
    index = string.lower().find(text_to_find.lower())

    if index != -1:
        string = string[:index]

    return string


import sys
import platform
import subprocess

def check_torch_version(min_version="2.0.0", min_cuda_version=12):
    try:
        import torch
        current_version = torch.__version__
        
        if pkg_resources.parse_version(current_version) < pkg_resources.parse_version(min_version):
            print(f"PyTorch version {current_version} is lower than minimum required version {min_version}")
            return False
            
        if torch.cuda.is_available():
            cuda_version = torch.version.cuda
            if int(cuda_version.split('.')[0]) < min_cuda_version:
                print(f"CUDA version {cuda_version} is lower than minimum required version {min_cuda_version}")
                return False
            print(f"PyTorch {current_version} with CUDA {cuda_version} is properly installed")
        else:
            print("CUDA is not available")
            
        return True
        
    except ImportError:
        print("PyTorch is not installed")
        return False

def reinstall_pytorch_with_cuda():
    """
    Reinstall PyTorch with CUDA support using pip
    Platform-aware: Windows and Linux will use CUDA, Mac will use default
    """
    try:
        system = platform.system().lower()
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "torch", "torchvision", "torchaudio", "-y"])
        
        if system in ['windows', 'linux']:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "torch", "torchvision", "torchaudio",
                "--index-url", "https://download.pytorch.org/whl/cu121"
            ])
        elif system == 'darwin':
            print("Note: Installing default MacOS version as CUDA is not supported on MacOS")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "torch", "torchvision", "torchaudio"
            ])
        print("PyTorch reinstalled with CUDA support (where applicable)")
    except subprocess.CalledProcessError as e:
        print(f"Error reinstalling PyTorch: {e}")

def reinstall_pytorch_with_rocm():
    """
    Reinstall PyTorch with ROCm support using pip
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "torch", "torchvision", "torchaudio", "-y"])
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "torch", "torchvision", "torchaudio",
            "--index-url", "https://download.pytorch.org/whl/rocm5.6"
        ])
        print("PyTorch reinstalled with ROCm support")
    except subprocess.CalledProcessError as e:
        print(f"Error reinstalling PyTorch: {e}")

def reinstall_pytorch_with_cpu():
    """
    Reinstall PyTorch CPU-only version using pip
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "torch", "torchvision", "torchaudio", "-y"])
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "torch", "torchvision", "torchaudio"
        ])
        print("PyTorch reinstalled (CPU-only version)")
    except subprocess.CalledProcessError as e:
        print(f"Error reinstalling PyTorch: {e}")



def check_and_install_torch(enable_gpu: bool, version: float = 2.2):
    """
    Check and install PyTorch with specified configuration
    Args:
        enable_gpu (bool): Whether to install GPU version
        version (float): Minimum required PyTorch version
    """
    try:
        import torch
        current_version = torch.__version__
        system = platform.system().lower()
        
        # Check if current installation meets requirements
        if pkg_resources.parse_version(current_version) >= pkg_resources.parse_version(str(version)):
            if enable_gpu:
                if system == 'darwin':
                    # For Mac, MPS is the GPU solution
                    print(f"Current PyTorch installation ({current_version}) is compatible with Mac GPU (MPS)")
                    return True
                elif torch.cuda.is_available():
                    print(f"Current PyTorch installation ({current_version}) has CUDA support")
                    return True
                else:
                    print("GPU version requested but CUDA not available. Reinstalling...")
            else:
                print(f"Current CPU PyTorch installation ({current_version}) meets version requirement")
                return True
    except ImportError:
        print("PyTorch not found. Installing...")
    
    # Perform installation based on requirements
    if enable_gpu:
        if system == 'darwin':
            reinstall_pytorch_with_cpu()  # Mac uses default installation for MPS
        else:
            reinstall_pytorch_with_cuda()
    else:
        reinstall_pytorch_with_cpu()
    
    # Verify installation
    try:
        import torch
        print(f"PyTorch {torch.__version__} installed successfully")
        if enable_gpu:
            if system == 'darwin':
                print("MPS (Mac GPU) support available if hardware supports it")
            elif torch.cuda.is_available():
                print(f"CUDA version: {torch.version.cuda}")
            else:
                print("Warning: GPU version requested but CUDA not available")
    except ImportError:
        print("Installation failed")
        return False
    
    return True
    

class NumpyEncoderDecoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return {'__numpy_array__': True, 'data': obj.tolist()}
        return super(NumpyEncoderDecoder, self).default(obj)

    @staticmethod
    def as_numpy_array(dct):
        if '__numpy_array__' in dct:
            return np.array(dct['data'])
        return dct
    

def clone_repository(repository_url, local_folder:Path|str, exist_ok=False):
    if Path(local_folder).exists():
        if exist_ok:
            shutil.rmtree(str(local_folder))
        else:
            ASCIIColors.success("Repository already exists!")
            return False

    try:
        # Create a new repository object
        repo = git.Repo.clone_from(repository_url, str(local_folder))
        ASCIIColors.success("Repository was cloned successfully")
        return True
    except:
        ASCIIColors.error("Repository cloning failed")
        return False
    
def git_pull(folder_path):
    try:
        # Change the current working directory to the desired folder
        subprocess.run(["git", "checkout", folder_path], check=True, cwd=folder_path)
        # Run 'git pull' in the specified folder
        subprocess.run(["git", "pull"], check=True, cwd=folder_path)
        print("Git pull successful in", folder_path)
    except subprocess.CalledProcessError as e:
        print("Error occurred while executing Git pull:", e)
        # Handle any specific error handling here if required
class AdvancedGarbageCollector:
    @staticmethod
    def hardCollect(obj):
        """
        Remove a reference to the specified object and attempt to collect it.

        Parameters:
        - obj: The object to be collected.

        This method first identifies all the referrers (objects referencing the 'obj')
        using Python's garbage collector (gc.get_referrers). It then iterates through
        the referrers and attempts to break their reference to 'obj' by setting them
        to None. Finally, it deletes the 'obj' reference.

        Note: This method is designed to handle circular references and can be used
        to forcefully collect objects that might not be collected automatically.

        """
        if obj is None:
            return
        all_referrers = gc.get_referrers(obj)
        for referrer in all_referrers:
            try:
                if isinstance(referrer, (list, tuple, dict, set)):
                    if isinstance(referrer, list):
                        if obj in referrer:
                            referrer.remove(obj)
                    elif isinstance(referrer, dict):
                        new_dict = {}
                        for key, value in referrer.items():
                            if value != obj:
                                new_dict[key] = value
                        referrer.clear()
                        referrer.update(new_dict)
                    elif isinstance(referrer, set):
                        if obj in referrer:
                            referrer.remove(obj)
            except:
                ASCIIColors.warning("Couldn't remove object from referrer")
        del obj

    @staticmethod
    def safeHardCollect(variable_name, instance=None):
        """
        Safely remove a reference to a variable and attempt to collect its object.

        Parameters:
        - variable_name: The name of the variable to be collected.
        - instance: An optional instance (object) to search for the variable if it
          belongs to an object.

        This method provides a way to safely break references to a variable by name.
        It first checks if the variable exists either in the local or global namespace
        or within the provided instance. If found, it calls the 'hardCollect' method
        to remove the reference and attempt to collect the associated object.

        """
        if instance is not None:
            if hasattr(instance, variable_name):
                obj = getattr(instance, variable_name)
                AdvancedGarbageCollector.hardCollect(obj)
            else:
                print(f"The variable '{variable_name}' does not exist in the instance.")
        else:
            if variable_name in locals():
                obj = locals()[variable_name]
                AdvancedGarbageCollector.hardCollect(obj)
            elif variable_name in globals():
                obj = globals()[variable_name]
                AdvancedGarbageCollector.hardCollect(obj)
            else:
                print(f"The variable '{variable_name}' does not exist in the local or global namespace.")

    @staticmethod
    def safeHardCollectMultiple(variable_names, instance=None):
        """
        Safely remove references to multiple variables and attempt to collect their objects.

        Parameters:
        - variable_names: A list of variable names to be collected.
        - instance: An optional instance (object) to search for the variables if they
          belong to an object.

        This method iterates through a list of variable names and calls 'safeHardCollect'
        for each variable, effectively removing references and attempting to collect
        their associated objects.

        """
        for variable_name in variable_names:
            AdvancedGarbageCollector.safeHardCollect(variable_name, instance)

    @staticmethod
    def collect():
        """
        Perform a manual garbage collection using Python's built-in 'gc.collect' method.

        This method triggers a manual garbage collection, attempting to clean up
        any unreferenced objects in memory. It can be used to free up memory and
        resources that are no longer in use.

        """
        gc.collect()



class PackageManager:
    @staticmethod
    def install_package(package_name, index_url=None, extra_args=None):
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade"]
        if index_url:
            cmd.extend(["--index-url", index_url])
        if extra_args:
            cmd.extend(extra_args)
        cmd.append(package_name)
        subprocess.check_call(cmd)

    @staticmethod
    def check_package_installed(package_name):
        try:
            importlib.import_module(package_name)
            return True
        except ImportError:
            return False
        except Exception as ex:
            print(f"Error checking package: {ex}")
            return False

    @staticmethod
    def check_package_installed_with_version(package_name: str, min_version: Optional[str] = None) -> bool:
        try:
            import pkg_resources
            package = importlib.import_module(package_name)
            if min_version:
                installed_version = pkg_resources.get_distribution(package_name).version
                if pkg_resources.parse_version(installed_version) < pkg_resources.parse_version(min_version):
                    raise ImportError(f"Version {installed_version} is less than the required {min_version}.")
            return True
        except ImportError as ex:
            ASCIIColors.error(f"\nPackage '{package_name}' is not installed or version requirement not met. Error: {ex}")
            return False
        except Exception as ex:
            ASCIIColors.error(f"\nError checking package: {ex}")
            return False

    @staticmethod
    def safe_import(module_name, library_name=None, index_url=None, extra_args=None):
        if not PackageManager.check_package_installed(module_name):
            print(f"{module_name} module not found. Installing...")
            PackageManager.install_package(library_name or module_name, index_url, extra_args)
        globals()[module_name] = importlib.import_module(module_name)
        print(f"{module_name} module imported successfully.")

    @staticmethod
    def get_installed_version(package):
        try:
            output = subprocess.check_output([sys.executable, "-m", "pip", "show", package], universal_newlines=True)
            for line in output.splitlines():
                if line.startswith("Version:"):
                    version = line.split(":", 1)[1].strip()
                    print(f"The installed version of {package} is {version}.")
                    return version
            return None
        except subprocess.CalledProcessError as e:
            print(f"Error getting version for {package}: {e}")
            return None

    @staticmethod
    def install_or_update(package, index_url=None, extra_args=None):
        if PackageManager.check_package_installed(package):
            print(f"{package} is already installed. Checking for updates...")
            installed_version = PackageManager.get_installed_version(package)
            if installed_version:
                print(f"Updating {package} from version {installed_version}.")
                try:
                    PackageManager.install_package(package, index_url, extra_args)
                    print(f"Successfully updated {package}.")
                    return True
                except subprocess.CalledProcessError as e:
                    print(f"Error updating {package}: {e}")
                    return False
        else:
            print(f"{package} is not installed. Installing...")
            return PackageManager.install_package(package, index_url, extra_args)

    @staticmethod
    def uninstall_package(package):
        try:
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", package], check=True)
            print(f"Successfully uninstalled {package}.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error uninstalling {package}: {e}")
            return False

    @staticmethod
    def reinstall(package, index_url=None, extra_args=None):
        if PackageManager.check_package_installed(package):
            print(f"{package} is already installed. Uninstalling for fresh installation...")
            if PackageManager.uninstall_package(package):
                print(f"{package} uninstalled successfully. Now reinstalling.")
                return PackageManager.install_package(package, index_url, extra_args)
            else:
                print(f"Failed to uninstall {package}. Reinstallation aborted.")
                return False
        else:
            print(f"{package} is not installed. Installing it now.")
            return PackageManager.install_package(package, index_url, extra_args)
class GitManager:
    @staticmethod
    def git_pull(folder_path):
        try:
            # Change the current working directory to the desired folder
            subprocess.run(["git", "checkout", folder_path], check=True, cwd=folder_path)
            # Run 'git pull' in the specified folder
            subprocess.run(["git", "pull"], check=True, cwd=folder_path)
            print("Git pull successful in", folder_path)
        except subprocess.CalledProcessError as e:
            print("Error occurred while executing Git pull:", e)
            # Handle any specific error handling here if required

class File64BitsManager:

    @staticmethod
    def raw_b64_img(image) -> str:
        try:
            from PIL import Image, PngImagePlugin
            import io
            import base64
        except:
            PackageManager.install_package("Pillow")
            from PIL import Image
            import io
            import base64

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


    @staticmethod
    def img2b64(image) -> str:
        return "data:image/png;base64," + File64BitsManager.raw_b64_img(image)    

    @staticmethod
    def b642img(b64img) -> str:
        try:
            from PIL import Image, PngImagePlugin
            import io
            import base64
        except:
            PackageManager.install_package("Pillow")
            from PIL import Image
            import io
            import base64        
        image_data = re.sub('^data:image/.+;base64,', '', b64img)
        return Image.open(io.BytesIO(base64.b64decode(image_data)))  

    @staticmethod
    def get_supported_file_extensions_from_base64(b64data):
        # Extract the file extension from the base64 data
        data_match = re.match(r'^data:(.*?);base64,', b64data)
        if data_match:
            mime_type = data_match.group(1)
            extension = mime_type.split('/')[-1]
            return extension
        else:
            raise ValueError("Invalid base64 data format.")
        
    @staticmethod
    def extract_content_from_base64(b64data):
        # Split the base64 data at the comma separator
        header, content = b64data.split(',', 1)

        # Extract only the content part and remove any white spaces and newlines
        content = content.strip()

        return content

    @staticmethod
    def b642file(b64data, filename):
        import base64   
        # Extract the file extension from the base64 data
        
        
        # Save the file with the determined extension
        with open(filename, 'wb') as file:
            file.write(base64.b64decode(File64BitsManager.extract_content_from_base64(b64data)))

        return filename
    
class PromptReshaper:
    def __init__(self, template:str):
        self.template = template
    def replace(self, placeholders:dict)->str:
        template = self.template
        # Calculate the number of tokens for each placeholder
        for placeholder, text in placeholders.items():
            template = template.replace(placeholder, text)
        return template
    def build(self, placeholders:dict, tokenize, detokenize, max_nb_tokens:int, place_holders_to_sacrifice:list=[])->str:
        # Tokenize the template without placeholders
        template_text = self.template
        template_tokens = tokenize(template_text)
        
        # Calculate the number of tokens in the template without placeholders
        template_tokens_count = len(template_tokens)
        
        # Calculate the number of tokens for each placeholder
        placeholder_tokens_count = {}
        all_count = template_tokens_count
        for placeholder, text in placeholders.items():
            text_tokens = tokenize(text)
            placeholder_tokens_count[placeholder] = len(text_tokens)
            all_count += placeholder_tokens_count[placeholder]

        def fill_template(template, data):
            for key, value in data.items():
                placeholder = "{{" + key + "}}"
                n_text_tokens = len(tokenize(template))
                if key in place_holders_to_sacrifice:
                    n_remaining = max_nb_tokens - n_text_tokens
                    t_value = tokenize(value)
                    n_value = len(t_value)
                    if n_value<n_remaining:
                        template = template.replace(placeholder, value)
                    else:
                        value = detokenize(t_value[-n_remaining:])
                        template = template.replace(placeholder, value)
                        
                else:
                    template = template.replace(placeholder, value)
            return template
        
        return fill_template(self.template, placeholders)



class LOLLMSLocalizer:
    def __init__(self, dictionary):
        self.dictionary = dictionary

    def localize(self, input_string):
        def replace(match):
            key = match.group(1)
            return self.dictionary.get(key, match.group(0))
        
        import re
        pattern = r'@<([^>]+)>@'
        localized_string = re.sub(pattern, replace, input_string)
        return localized_string


class File_Path_Generator:
    @staticmethod
    def generate_unique_file_path(folder_path, file_base_name, file_extension):
        folder_path = Path(folder_path)
        index = 0
        while True:
            # Construct the full file path with the current index
            file_name = f"{file_base_name}_{index}.{file_extension}"
            full_file_path = folder_path / file_name
            
            # Check if the file already exists in the folder
            if not full_file_path.exists():
                return full_file_path
            
            # If the file exists, increment the index and try again
            index += 1


def remove_text_from_string(string: str, text_to_find:str):
    """
    Removes everything from the first occurrence of the specified text in the string (case-insensitive).

    Parameters:
    string (str): The original string.
    text_to_find (str): The text to find in the string.

    Returns:
    str: The updated string.
    """
    index = string.lower().find(text_to_find.lower())

    if index != -1:
        string = string[:index]

    return string


def short_desc(text: str, max_length: int = 80) -> str:
    """
    Creates a shortened description of a text string, adding ellipsis if truncated.

    Tries to break at a word boundary (space) if possible within the length limit.

    Args:
        text: The input string. Can be None.
        max_length: The maximum desired length of the output string (including ellipsis).
                    Must be at least 4 to accommodate "...".

    Returns:
        The shortened string, or the original string if it's already short enough.
        Returns an empty string if the input is None or not a string.
    """
    if text is None:
        return ""

    # Ensure input is treated as a string
    if not isinstance(text, str):
        try:
            text = str(text)
        except Exception:
            return "[Invalid Input]" # Or return "" depending on desired behavior

    # If text is already short enough, return it as is.
    if len(text) <= max_length:
        return text

    # Ensure max_length is usable
    if max_length < 4:
        # Cannot add ellipsis, just truncate hard
        return text[:max_length]

    # Calculate the ideal truncation point before adding "..."
    trunc_point = max_length - 3

    # Find the last space character at or before the truncation point
    last_space = text.rfind(' ', 0, trunc_point + 1) # Include trunc_point itself

    if last_space != -1:
        # Found a space, truncate there
        return text[:last_space] + "..."
    else:
        # No space found in the initial part, hard truncate
        return text[:trunc_point] + "..."

def get_torch_device():
    """
    Detects and returns the best available PyTorch device.
    Prioritizes CUDA, then MPS (Apple Silicon), then CPU.

    Returns:
        str: The selected device ("cuda", "mps", or "cpu").
    """
    import torch
    if torch.cuda.is_available():
        device = "cuda"
        try:
            # Optional: Log GPU details if needed
            gpu_name = torch.cuda.get_device_name(0)
            ASCIIColors.info(f"CUDA device detected: {gpu_name}")
        except Exception as e:
            ASCIIColors.warning(f"Could not get CUDA device name: {e}")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available() and torch.backends.mps.is_built():
        # Check if MPS is available and built
        device = "mps"
        ASCIIColors.info("MPS device detected (Apple Silicon).")
    else:
        device = "cpu"
        ASCIIColors.info("No CUDA or MPS detected. Using CPU.")
    return device