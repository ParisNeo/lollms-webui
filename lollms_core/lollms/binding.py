######
# Project       : lollms
# File          : binding.py
# Author        : ParisNeo with the help of the community
# license       : Apache 2.0
# Description   : 
# This is an interface class for lollms bindings.
######
import traceback
import os
import time
import asyncio
from typing import Dict, Any, List
from pathlib import Path
from typing import Callable, Any
from lollms.paths import LollmsPaths
from ascii_colors import ASCIIColors
from urllib import request
import threading
import tempfile
import requests
import shutil
import os
import yaml
import importlib
import subprocess
from lollms.config import TypedConfig, InstallOption
from lollms.main_config import LOLLMSConfig
from lollms.com import NotificationType, NotificationDisplayType, LoLLMsCom
from lollms.utilities import show_message_dialog
from lollms.types import BindingType
from lollms.client_session import Client
import urllib
import inspect
from datetime import datetime
from enum import Enum
from lollms.utilities import trace_exception
import pipmaster as pm
pm.install_if_missing("huggingface_hub")
from huggingface_hub import hf_hub_download, snapshot_download
from huggingface_hub.utils import HfHubHTTPError, RepositoryNotFoundError, RevisionNotFoundError, EntryNotFoundError
from tqdm import tqdm
from lollms.databases.models_database import ModelsDB
import sys
import re
__author__ = "parisneo"
__github__ = "https://github.com/ParisNeo/lollms_bindings_zoo"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"


class LLMBinding:
    
    def __init__(
                    self,
                    binding_dir:Path,
                    lollms_paths:LollmsPaths,
                    config:LOLLMSConfig, 
                    binding_config:TypedConfig,
                    installation_option:InstallOption=InstallOption.INSTALL_IF_NECESSARY,
                    SAFE_STORE_SUPPORTED_FILE_EXTENSIONS='*.bin',
                    binding_type:BindingType=BindingType.TEXT_ONLY,
                    models_dir_names:list=None,
                    lollmsCom:LoLLMsCom=None
                ) -> None:
        
        self.binding_type           = binding_type

        self.binding_dir            = binding_dir
        self.binding_folder_name    = binding_dir.stem
        self.lollms_paths           = lollms_paths
        self.config                 = config
        self.binding_config         = binding_config

        self.lollmsCom = lollmsCom

        self.download_infos={}

        self.add_default_configurations(binding_config)

        self.interrogatorStorer = None
        self.SAFE_STORE_SUPPORTED_FILE_EXTENSIONS          = SAFE_STORE_SUPPORTED_FILE_EXTENSIONS
        self.seed                               = config["seed"]

        self.sync_configuration(self.binding_config, lollms_paths)
        # Installation
        if (not self.configuration_file_path.exists() or installation_option==InstallOption.FORCE_INSTALL) and installation_option!=InstallOption.NEVER_INSTALL:
            self.ShowBlockingMessage("Installing Binding")
            self.install()
            self.binding_config.config.save_config()
            self.HideBlockingMessage()
        else:
            self.load_binding_config()

        if models_dir_names is not None:
            config.lollms_paths.binding_models_paths=[config.lollms_paths.personal_models_path / models_dir_name for models_dir_name in models_dir_names]
            self.models_folders = config.lollms_paths.binding_models_paths
            self.models_dir_names = models_dir_names
        else:
            config.lollms_paths.binding_models_paths= [config.lollms_paths.personal_models_path / self.binding_folder_name]
            self.models_folders = config.lollms_paths.binding_models_paths
            self.models_dir_names = [self.binding_folder_name]
        for models_folder in self.models_folders:
            models_folder.mkdir(parents=True, exist_ok=True)

    def stop_generation(self):
        """Requests the generation thread to stop (the model must implement this)."""
        pass


    def parse_lollms_discussion(self, full_prompt: str) -> List[Dict[str, str]]:
        """
        Parses the custom LoLLMs discussion format (!@>system:, !@>discussion:, !@>user_name:, !@>personality_name:)
        into a list of dictionaries compatible with tokenizer.apply_chat_template, preserving
        the actual role names used in the prompt and correctly associating content.

        Args:
            full_prompt: The prompt string containing the custom format.

        Returns:
            A list of message dictionaries, e.g., [{"role": "ParisNeo", "content": "..."}, ...].
            Returns an empty list if parsing fails or format is not detected.
        """
        messages = []
        # Define start/end patterns using config, ensuring they are regex-safe
        start_pattern = re.escape(self.config.start_header_id_template)
        end_pattern = re.escape(self.config.end_header_id_template.strip()) # Strip trailing space if any

        # Regex to find system message and discussion block robustly
        # Look for system block ending either at discussion block or end of string
        system_search_pattern = rf"{start_pattern}system{end_pattern}(.*?)(?={start_pattern}discussion{end_pattern}|$)"
        # Look for discussion block and capture everything after it
        discussion_search_pattern = rf"{start_pattern}discussion{end_pattern}(.*)"

        system_match = re.search(system_search_pattern, full_prompt, re.IGNORECASE | re.DOTALL)
        discussion_match = re.search(discussion_search_pattern, full_prompt, re.IGNORECASE | re.DOTALL)

        # 1. Extract System Prompt
        if system_match:
            system_content = system_match.group(1).strip()
            if system_content:
                # Standardize 'system' role as it's usually special in templates
                messages.append({"role": "system", "content": system_content})

        # 2. Parse Discussion Block if it exists
        if discussion_match:
            discussion_text = discussion_match.group(1) # Don't strip yet, preserve leading/trailing whitespace between turns
            # Pattern to find role markers: captures the role name (e.g., 'lollms', 'ParisNeo')
            role_marker_pattern = re.compile(rf'{start_pattern}(\w+){end_pattern}')

            last_marker_end = 0
            current_role = None # The role governing the content *before* the current marker

            # Iterate through all markers found in the discussion text
            for match in role_marker_pattern.finditer(discussion_text):
                # Content for the *previous* role lies between the end of the previous marker
                # and the start of the current marker.
                content_start = last_marker_end
                content_end = match.start()
                content = discussion_text[content_start:content_end].strip()

                # If we had a role defined from the previous iteration, and there's content, add the message
                if current_role is not None and content:
                    messages.append({"role": current_role, "content": content})
                elif current_role is not None and not content:
                    # Handle case where a marker is immediately followed by another (e.g., !@>user:\n!@>assistant:)
                    # Usually, we want to skip empty messages, but maybe log a warning.
                    # self.warning(f"Empty content found for role: {current_role}")
                    pass


                # The role defined by the *current* marker will govern the *next* segment of content
                current_role = match.group(1) # e.g., 'lollms' or 'ParisNeo'
                last_marker_end = match.end() # Update the end position for the next iteration

            # After the loop, capture the final piece of content following the last marker
            if current_role is not None:
                final_content = discussion_text[last_marker_end:].strip()
                if final_content:
                    messages.append({"role": current_role, "content": final_content})
                # Note: If the discussion ends with just a marker like "!@>lollms:",
                # final_content will be empty. We *do not* add this empty message.
                # The `add_generation_prompt=True` flag in `apply_chat_template` is responsible
                # for adding the necessary tokens to start the assistant's turn based on the
                # *last actual message* in the list (which should be the user's).

        # 3. Handle Fallbacks and Edge Cases (If no valid discussion was parsed)

        # If NO messages were parsed at all (not even system), treat whole prompt as user input
        if not messages and full_prompt:
            user_role_name = self.config.user_name or "user" # Fallback to "user"
            messages.append({"role": user_role_name, "content": full_prompt.strip()})

        # If only a system message was parsed, check if there was content *after* the system block
        # but *before* any potential (malformed or missing) discussion block. Treat that as user input.
        elif len(messages) == 1 and messages[0]["role"] == "system" and system_match:
            # Find where the system message content actually ended in the original prompt
            # system_match.group(1) is the content, system_match.start(1) and end(1) give its span
            end_of_system_message_content = system_match.end(1)
            remaining_prompt_after_system = full_prompt[end_of_system_message_content:].strip()

            # Add remaining content as user input ONLY if no discussion block was detected AT ALL
            if remaining_prompt_after_system and not discussion_match:
                user_role_name = self.config.user_name or "user"
                messages.append({"role": user_role_name, "content": remaining_prompt_after_system})


        return messages
    
    def count_tokens(self, prompt):
        """
        Counts the number of tokens in a prtompt
        """
        return len(self.tokenize(prompt))

    def searchModelFolder(self, model_name:str):
        for mn in self.models_folders:
            if mn.name in model_name.lower():
                return mn
        return self.models_folders[0]
    
    
    def searchModelPath(self, model_name:str):
        model_path=self.searchModelFolder(model_name)
        mp:Path = None
        for f in model_path.iterdir():
            a =  model_name.lower()
            b = f.name.lower()
            if a in b :
                mp = f
                break
        if not mp:
            return None
        
        if model_path.name in ["ggml","gguf"]:
            # model_path/str(model_name).split("/")[-1]
            if mp.is_dir():
                for f in mp.iterdir():
                    if not "mmproj" in f.stem and not f.is_dir():
                        if f.suffix==".reference":
                            with open(f,"r") as f:
                                return Path(f.read())
                        return f
            else:
                show_message_dialog("Warning","I detected that your model was installed with previous format.\nI'll just migrate it to thre new format.\nThe new format allows you to have multiple model variants and also have the possibility to use multimodal models.")
                model_root:Path = model_path.parent/model_path.stem
                model_root.mkdir(exist_ok=True, parents=True)
                shutil.move(model_path, model_root)
                model_path = model_root/model_path.name
                self.config.model_name = model_root.name
                root_path = model_root
                self.config.save_config()
                return model_path
        else:
            return mp
    
    def download_model(self, url, model_name, callback = None):
        folder_path = self.searchModelFolder(model_name)
        model_full_path = (folder_path/model_name)/str(url).split("/")[-1]
        # Check if file already exists in folder
        if model_full_path.exists():
            print("File already exists in folder")
        else:
            # Create folder if it doesn't exist
            folder_path.mkdir(parents=True, exist_ok=True)
            if not callback:
                progress_bar = tqdm(total=100, unit="%", unit_scale=True, desc=f"Downloading {url.split('/')[-1]}")
            # Define callback function for urlretrieve
            downloaded_size = [0]
            def report_progress(block_num, block_size, total_size):
                if callback:
                    downloaded_size[0] += block_size
                    callback(downloaded_size[0], total_size)
                else:
                    progress_bar.update(block_size/total_size)
            # Download file from URL to folder
            try:
                Path(model_full_path).parent.mkdir(parents=True, exist_ok=True)
                request.urlretrieve(url, model_full_path, reporthook=report_progress)
                print("File downloaded successfully!")
            except Exception as e:
                ASCIIColors.error("Error downloading file:", e)
                sys.exit(1)

    def reference_model(self, path):
        path = Path(str(path).replace("\\","/"))
        model_name  = path.stem+".reference"
        folder_path = self.searchModelFolder(model_name)/(path.stem if path.suffix.lower()=="gguf" else path.name)
        model_full_path = (folder_path / model_name)

        # Check if file already exists in folder
        if model_full_path.exists():
            print("File already exists in folder")
            return False
        else:
            # Create folder if it doesn't exist
            folder_path.mkdir(parents=True, exist_ok=True)
            with open(model_full_path,"w") as f:
                f.write(str(path))
            self.InfoMessage("Reference created, please make sure you don't delete or move the referenced file.\nThis can cause the link to be broken.\nNow I'm reloading the zoo.")
            return True


    def sync_configuration(self, binding_config:TypedConfig, lollms_paths:LollmsPaths):
        self.configuration_file_path = lollms_paths.personal_configuration_path/"bindings"/self.binding_folder_name/f"config.yaml"
        self.configuration_file_path.parent.mkdir(parents=True, exist_ok=True)
        binding_config.config.file_path = self.configuration_file_path


    def download_file(self, url, installation_path, callback=None):
        """
        Downloads a file from a URL, reports the download progress using a callback function, and displays a progress bar.

        Args:
            url (str): The URL of the file to download.
            installation_path (str): The path where the file should be saved.
            callback (function, optional): A callback function to be called during the download
                with the progress percentage as an argument. Defaults to None.
        """
        try:
            response = requests.get(url, stream=True)

            # Get the file size from the response headers
            total_size = int(response.headers.get('content-length', 0))

            with open(installation_path, 'wb') as file:
                downloaded_size = 0
                with tqdm(total=total_size, unit='B', unit_scale=True, ncols=80) as progress_bar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                            downloaded_size += len(chunk)
                            if callback is not None:
                                callback(downloaded_size, total_size)
                            progress_bar.update(len(chunk))

            if callback is not None:
                callback(total_size, total_size)

            print("File downloaded successfully")
        except Exception as e:
            print("Couldn't download file:", str(e))

    def _get_folder_size(self, folder_path: Path) -> int:
        """Calculates the total size of all files in a directory."""
        total_size = 0
        for item in folder_path.rglob('*'):
            if item.is_file():
                try:
                    total_size += item.stat().st_size
                except OSError:
                    # Ignore files that might be removed during calculation
                    pass
        return total_size

    def _get_folder_size(self, folder_path: Path) -> int:
        """Calculates the total size of all files in a directory."""
        total_size = 0
        if not folder_path.is_dir():
            return 0
        for item in folder_path.rglob('*'):
            if item.is_file():
                try:
                    # Check if the file still exists before getting its size
                    if item.exists():
                        total_size += item.stat().st_size
                except FileNotFoundError:
                     ASCIIColors.warning(f"File not found during size calculation: {item}. Skipping.")
                except OSError as e:
                    ASCIIColors.warning(f"OS error calculating size for {item}: {e}. Skipping.")
        return total_size

    # ----- ASYNC CORE LOGIC -----
    async def install_model_async(self, variant_id: str, client_id: int = None):
        """
        The core asynchronous logic for downloading and installing a model
        directly into the lollms personal models path.
        """
        ASCIIColors.info(f"Async install task started for: {variant_id} by client: {client_id}")
        start_time = time.time()
        repo_id = ""
        filename = None # Use None to distinguish between single/multi file cases
        model_url = ""
        target_path = None # Path object for the final file or folder
        binding_folder = "" # e.g., gguf, transformers
        model_name = "" # e.g., the GGUF filename or the repo name
        installation_path_str = "" # String version for notification

        try:
            # --- Determine Type and Paths ---
            parts = variant_id.split("::")
            if len(parts)==2 and not (parts[0] in parts[1]):
                # SINGLE FILE (e.g., GGUF, GGML)
                
                if len(parts) != 2 or not parts[0] or not parts[1]:
                    raise ValueError("Invalid variant_id format for single file. Expected 'repo_id::filename'.")
                repo_id = parts[0]
                filename = parts[1] # Store filename explicitly
                model_name = filename
                model_url = f"https://huggingface.co/{repo_id}/resolve/main/{filename}" # Direct file URL
                file_extension = Path(filename).suffix.lower().strip('.')
                binding_folder = file_extension if file_extension in ["gguf", "ggml"] else (file_extension or "misc")

                # Folder name is the repo name part (e.g., "Qwen2.5.1-Coder-7B-Instruct-GGUF")
                model_repo_name_folder = repo_id.split('/')[-1]
                # Target folder structure: personal_models / <type> / <repo_name> /
                target_folder = self.lollms_paths.personal_models_path / binding_folder / model_repo_name_folder
                # Final target path for the file
                target_path = target_folder / filename
                installation_path_str = str(target_path)
                ASCIIColors.info(f"Single file install: Type='{binding_folder}', Target='{target_path}'")

            else:
                if len(parts)==2:
                    variant_id=parts[0]
                # MULTI-FILE REPOSITORY (e.g., Transformers)
                repo_id = variant_id
                binding_folder = "transformers" # Fixed type for multi-file repos
                # Model name and folder name are the repo name part
                provider_name = repo_id.split('/')[0]
                model_name = repo_id.split('/')[-1]
                model_repo_name_folder = model_name
                model_url = f"https://huggingface.co/{repo_id}" # Repo URL

                # Target folder structure: personal_models / transformers / <repo_name> /
                target_folder = self.lollms_paths.personal_models_path / binding_folder / provider_name / model_repo_name_folder
                target_path = target_folder # For repos, the target *is* the folder
                installation_path_str = str(target_path)
                ASCIIColors.info(f"Multi-file repo install: Type='{binding_folder}', Target='{target_path}'")


            # --- Send "Started" notification ---
            # Ensure the specific base binding folder exists (e.g., .../gguf/ or .../transformers/)
            target_path.parent.mkdir(parents=True, exist_ok=True)

            await self.lollmsCom.notify_model_install(
                installation_path=installation_path_str, model_name=model_name, binding_folder=binding_folder,
                model_url=model_url, start_time=start_time, total_size=0, downloaded_size=0, progress=0.0,
                speed=0.0, client_id=client_id, status=True, error="Starting download..."
            )

            # --- Perform Download (using asyncio.to_thread for blocking calls) ---
            actual_size = 0
            if filename:
                # SINGLE FILE DOWNLOAD using hf_hub_download
                ASCIIColors.info(f"Downloading single file: {filename} from {repo_id} to {target_path.parent}")

                # Define the blocking download function
                def _download_file():
                    # Download directly into the target PARENT folder
                    downloaded_path_str = hf_hub_download(
                        repo_id=repo_id,
                        filename=filename,
                        local_dir=str(target_path.parent), # Specify the final directory
                        local_dir_use_symlinks=False, # IMPORTANT: Copy file instead of symlinking from cache
                        resume_download=True,
                        # cache_dir=self.lollms_paths.hf_cache_path # Optional: Still use cache for partial downloads
                        # etag_timeout=10 # Optional: Adjust timeout
                    )
                    return downloaded_path_str

                # Run the download in a thread
                downloaded_path_str = await asyncio.to_thread(_download_file)
                downloaded_path = Path(downloaded_path_str)

                # Ensure the downloaded file is exactly where we want it with the correct name
                # hf_hub_download with local_dir should place it correctly, but sometimes adds hashes if cache involved.
                if downloaded_path.name != target_path.name :
                     ASCIIColors.warning(f"Downloaded file name mismatch: {downloaded_path.name} vs {target_path.name}. Renaming.")
                     # Ensure the final target doesn't exist before renaming
                     if target_path.exists() and target_path.is_file():
                         target_path.unlink()
                     downloaded_path.rename(target_path)
                elif downloaded_path.parent != target_path.parent:
                     ASCIIColors.warning(f"Downloaded file in unexpected parent: {downloaded_path.parent} vs {target_path.parent}. Moving.")
                     if target_path.exists() and target_path.is_file():
                         target_path.unlink()
                     import shutil
                     shutil.move(str(downloaded_path), str(target_path))


                # Verify final path exists before getting size
                if target_path.exists():
                    actual_size = target_path.stat().st_size
                else:
                    raise FileNotFoundError(f"Downloaded file could not be found at expected location: {target_path}")

            else:
                # MULTI-FILE REPOSITORY DOWNLOAD using snapshot_download
                ASCIIColors.info(f"Downloading repository: {repo_id} to {target_path}")

                # Define patterns for essential files (customize as needed)
                allow_patterns = [
                    "*.json",             # Config, tokenizer, generation configs
                    "*.safetensors",      # Weights (preferred)
                    #"*.bin",              # Weights (alternative/older pytorch)
                    "*.py",               # Model code, processing code
                    "tokenizer.model",    # SentencePiece/BPE model files
                    "*.tiktoken",         # Tiktoken files
                    "*.md",               # Readme, etc (often useful)
                    # Add other patterns if models you use require specific file types
                    # "*.txt", ?
                    # "*.vocab"?
                ]
                # Optionally ignore specific large or less common files if allow_patterns is too broad
                # ignore_patterns = ["*.gguf", "*.ggml", "*.onnx", "*.onnx_data", "*.tflite", "pytorch_model*.bin"]

                # Define the blocking snapshot download function
                def _download_repo():
                    # Download directly into the target folder
                    snapshot_download(
                        repo_id=repo_id,
                        local_dir=str(target_path), # Specify the final directory
                        local_dir_use_symlinks=False, # IMPORTANT: Copy files instead of symlinking
                        resume_download=True,
                        allow_patterns=allow_patterns,
                        # ignore_patterns=ignore_patterns, # Uncomment if using ignore patterns
                        # cache_dir=self.lollms_paths.hf_cache_path # Optional: Still use cache
                        # etag_timeout=10 # Optional: Adjust timeout
                    )

                # Run the download in a thread
                await asyncio.to_thread(_download_repo)

                # Calculate total size of downloaded files in the target directory
                actual_size = self._get_folder_size(target_path)
                if actual_size == 0 and not list(target_path.iterdir()):
                     # Check if the folder is truly empty - maybe allow_patterns excluded everything?
                     ASCIIColors.warning(f"Repository download resulted in an empty folder: {target_path}. Check allow_patterns or repo contents.")
                     # Optionally, try again without allow_patterns? Or raise an error?
                     # For now, we'll proceed but ASCIIColors the warning.


            # --- Final Notification (Success) ---
            end_time = time.time()
            duration = end_time - start_time
            average_speed = actual_size / duration if duration > 0 else 0
            ASCIIColors.info(f"Download successful for {variant_id}. Target: {target_path}. Size: {actual_size} bytes. Duration: {duration:.2f}s.")
            await self.lollmsCom.notify_model_install(
                installation_path=installation_path_str, model_name=model_name, binding_folder=binding_folder,
                model_url=model_url, start_time=start_time, total_size=actual_size, downloaded_size=actual_size,
                progress=100.0, speed=average_speed, client_id=client_id, status=True, error=""
            )

        except (HfHubHTTPError, RepositoryNotFoundError, RevisionNotFoundError, EntryNotFoundError, ValueError, OSError, FileNotFoundError) as e:
            error_message = f"Installation failed: {type(e).__name__}: {e}"
            ASCIIColors.error(f"Error installing model {variant_id}: {error_message}\n{traceback.format_exc()}")
            installation_path_str = installation_path_str or variant_id
            model_name = model_name or variant_id.split('/')[-1]
            binding_folder = binding_folder or "unknown"
            await self.lollmsCom.notify_model_install(
                installation_path=installation_path_str, model_name=model_name, binding_folder=binding_folder,
                model_url=model_url or f"https://huggingface.co/{repo_id}", start_time=start_time, total_size=0, downloaded_size=0, progress=0.0,
                speed=0.0, client_id=client_id, status=False, error=error_message
            )
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            ASCIIColors.error(f"Unexpected error during install of {variant_id}: {error_message}\n{traceback.format_exc()}")
            installation_path_str = installation_path_str or variant_id
            model_name = model_name or variant_id.split('/')[-1]
            binding_folder = binding_folder or "unknown"
            await self.lollmsCom.notify_model_install(
                installation_path=installation_path_str, model_name=model_name, binding_folder=binding_folder,
                model_url=model_url or f"https://huggingface.co/{repo_id}", start_time=start_time, total_size=0, downloaded_size=0, progress=0.0,
                speed=0.0, client_id=client_id, status=False, error=error_message
            )

    # ----- SYNCHRONOUS WRAPPER for threading -----
    def install_model_sync_wrapper(self, variant_id: str, client_id: int = None):
        """
        Synchronous wrapper to run the async install logic in a new event loop.
        Target for threading.Thread.
        """
        try:
            ASCIIColors.info(f"Thread {threading.current_thread().name}: Starting asyncio.run for install_model_async({variant_id})")
            asyncio.run(self.install_model_async(variant_id, client_id))
            ASCIIColors.info(f"Thread {threading.current_thread().name}: asyncio.run finished successfully for {variant_id}")
        except Exception as e:
            # This primarily catches errors *during* asyncio.run setup or teardown
            # Most operational errors are caught inside install_model_async and notified from there
            ASCIIColors.error(f"Critical error in sync wrapper task for {variant_id}: {e}\n{traceback.format_exc()}")
            # We might not be able to reliably send an async notification here if the loop failed.


    def add_default_configurations(self, binding_config:TypedConfig):
        binding_config.addConfigs([
            {"name":"model_name","type":"str","value":'', "help":"Last known model for fast model recovery"},
            {"name":"model_template","type":"text","value":'', "help":"The template for the currently used model (optional)"},
            {"name":"clip_model_name","type":"str","value":'ViT-L-14/openai','options':["ViT-L-14/openai","ViT-H-14/laion2b_s32b_b79k"], "help":"Clip model to be used for images understanding"},
            {"name":"caption_model_name","type":"str","value":'blip-large','options':['blip-base', 'git-large-coco', 'blip-large','blip2-2.7b', 'blip2-flan-t5-xl'], "help":"Clip model to be used for images understanding"},
            {"name":"vqa_model_name","type":"str","value":'Salesforce/blip-vqa-capfilt-large','options':['Salesforce/blip-vqa-capfilt-large', 'Salesforce/blip-vqa-base', 'Salesforce/blip-image-captioning-large','Salesforce/blip2-opt-2.7b', 'Salesforce/blip2-flan-t5-xxl'], "help":"Salesforce question/answer model"},
        ])

    def InfoMessage(self, content, client_id=None, verbose:bool=True):
        if self.lollmsCom:
            return self.lollmsCom.InfoMessage(content=content, client_id=client_id, verbose=verbose)
        ASCIIColors.white(content)

    def ShowBlockingMessage(self, content, client_id=None, verbose:bool=True):
        if self.lollmsCom:
            return self.lollmsCom.ShowBlockingMessage(content=content, client_id=client_id, verbose=verbose)
        ASCIIColors.white(content)
        
    def HideBlockingMessage(self, client_id=None, verbose:bool=True):
        if self.lollmsCom:
            return self.lollmsCom.HideBlockingMessage(client_id=client_id, verbose=verbose)

    def info(self, content, duration:int=4, client_id=None, verbose:bool=True):
        if self.lollmsCom:
            return self.lollmsCom.info(content=content, duration=duration, client_id=client_id, verbose=verbose)
        ASCIIColors.info(content)

    def warning(self, content, duration:int=4, client_id=None, verbose:bool=True):
        if self.lollmsCom:
            return self.lollmsCom.warning(content=content, duration=duration, client_id=client_id, verbose=verbose)
        ASCIIColors.warning(content)

    def success(self, content, duration:int=4, client_id=None, verbose:bool=True):
        if self.lollmsCom:
            return self.lollmsCom.success(content=content, duration=duration, client_id=client_id, verbose=verbose)
        ASCIIColors.success(content)
        
    def error(self, content, duration:int=4, client_id=None, verbose:bool=True):
        if self.lollmsCom:
            return self.lollmsCom.error(content=content, duration=duration, client_id=client_id, verbose=verbose)
        ASCIIColors.error(content)
        
    def notify( self,                        
                content, 
                notification_type:NotificationType=NotificationType.NOTIF_SUCCESS, 
                duration:int=4, 
                client_id=None, 
                display_type:NotificationDisplayType=NotificationDisplayType.TOAST,
                verbose=True
            ):
        if self.lollmsCom:
            return self.lollmsCom.sync_notify(content=content, notification_type=notification_type, duration=duration, client_id=client_id, display_type=display_type, verbose=verbose)
        ASCIIColors.white(content)


    def settings_updated(self):
        """
        To be implemented by the bindings
        """
        pass

    async def handle_request(self, data: dict, client:Client=None) -> Dict[str, Any]:
        """
        Handle client requests.

        Args:
            data (dict): A dictionary containing the request data.
            client (Client): A refertence to the client asking for this request.

        Returns:
            dict: A dictionary containing the response, including at least a "status" key.

        This method should be implemented by a class that inherits from this one.

        Example usage:
        ```
        handler = YourHandlerClass()
        client = checkaccess(lollmsServer, client_id)
        request_data = {"command": "some_command", "parameters": {...}}
        response = handler.handle_request(request_data, client)
        ```
        """        
        return {"status":True}

    def print_class_attributes(self, cls, show_layers=False):
        for attr in cls.__dict__:
            if isinstance(attr, property) or isinstance(attr, type):
                continue
            value = getattr(cls, attr)
            if attr!="tensor_file_map": 
                ASCIIColors.red(f"{attr}: ",end="")
                ASCIIColors.yellow(f"{value}")
            elif show_layers:
                ASCIIColors.red(f"{attr}: ")
                for k in value.keys():
                    ASCIIColors.yellow(f"{k}")
                
    def get_parameter_info(self, cls):
        # Get the signature of the class
        sig = inspect.signature(cls)
        
        # Print each parameter name and value
        for name, param in sig.parameters.items():
            if param.default is not None:
                print(f"{name}: {param.default}")
            else:
                print(f"{name}: Not specified")

    def __str__(self) -> str:
        return self.config["binding_name"]+f"({self.config['model_name']})"
    
    def download_and_install_wheel(self, url):
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()

        try:
            # Download the wheel file
            response = requests.get(url)
            if response.status_code == 200:
                # Save the downloaded file to the temporary directory
                wheel_path = os.path.join(temp_dir, 'package.whl')
                with open(wheel_path, 'wb') as file:
                    file.write(response.content)

                # Install the wheel file using pip
                subprocess.check_call(['pip', 'install', wheel_path])

                # Clean up the temporary directory
                shutil.rmtree(temp_dir)
                print('Installation completed successfully.')
            else:
                print('Failed to download the file.')

        except Exception as e:
            print('An error occurred during installation:', str(e))
            shutil.rmtree(temp_dir)

    def get_file_size(self, url):
        # Send a HEAD request to retrieve file metadata
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        # response = urllib.request.urlopen(url, headers=headers)
        
        # Extract the Content-Length header value
        file_size = response.headers.get('Content-Length')
        
        # Convert the file size to integer
        if file_size:
            file_size = int(file_size)
        
        return file_size
    
    def build_model(self, model_name=None):
        """
        Build the model.

        This method is responsible for constructing the model for the LOLLMS class.

        Returns:
            the model
        """        
        if model_name is not None:
            self.model_name = model_name
        else:
            self.model_name = self.config.model_name
    
    def destroy_model(self):
        """
        destroys the current model
        """
        pass

    def install(self):
        """
        Installation procedure (to be implemented)
        """
        ASCIIColors.blue("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
        ASCIIColors.red(f"Installing {self.binding_folder_name}")
        ASCIIColors.blue("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")

    def uninstall(self):
        """
        UnInstallation procedure (to be implemented)
        """
        ASCIIColors.blue("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
        ASCIIColors.red(f"UnInstalling {self.binding_folder_name}")
        ASCIIColors.blue("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")

    def searchModelParentFolder(self, model_name:str, model_type=None):
        model_path=None
        if model_type is not None:
            for mn in self.models_folders:
                if mn.name.lower() == model_type.lower():
                    return mn
        for mn in self.models_folders:
            if mn.name in model_name.lower():
                model_path = mn
                break
        if model_path is None:
            model_path = self.models_folders[0]
        return model_path

    """
    def searchModelPath(self, model_name:str):
        model_path=None
        for mn in self.models_folders:
            for f in mn.iterdir():
                if model_name.lower().replace("-gguf","").replace("-ggml","") in str(f).lower():
                    return f


        model_path = self.models_folders[0]/model_name
        return model_path
    """
    def get_model_path(self):
        """
        Retrieves the path of the model based on the configuration.

        If the model name ends with ".reference", it reads the model path from a file.
        Otherwise, it constructs the model path based on the configuration.

        Returns:
            str: The path of the model.
        """
        if self.config.model_name is None:
            return None
        
 
        model_path = self.searchModelPath(self.config.model_name)

        return model_path

    
    def get_current_seed(self):
        return self.seed
    
    def load_binding_config(self):
        """
        Load the content of local_config.yaml file.

        The function reads the content of the local_config.yaml file and returns it as a Python dictionary.

        Args:
            None

        Returns:
            dict: A dictionary containing the loaded data from the local_config.yaml file.
        """
        try:
            self.binding_config.config.load_config()
        except:
            self.binding_config.config.save_config()
        self.binding_config.sync()

    def save_config_file(self, path):
        """
        Load the content of local_config.yaml file.

        The function reads the content of the local_config.yaml file and returns it as a Python dictionary.

        Args:
            None

        Returns:
            dict: A dictionary containing the loaded data from the local_config.yaml file.
        """     
        self.binding_config.config.save_config(self.configuration_file_path)

    def interrogate_blip(self, images):
        if self.interrogatorStorer is None:
            from lollms.image_gen_modules.clip_interrogator import InterrogatorStorer
            self.interrogatorStorer = InterrogatorStorer(self.binding_config.clip_model_name, self.binding_config.caption_model_name)
        descriptions = []
        for image in images:
            descriptions.append(self.interrogatorStorer.interrogate(image))
        return descriptions

    def qna_blip(self, images, question=""):
        if self.interrogatorStorer is None:
            from lollms.image_gen_modules.blip_vqa import BlipInterrogatorStorer
            self.interrogatorStorer = BlipInterrogatorStorer()
        descriptions = []
        for image in images:
            descriptions.append(self.interrogatorStorer.interrogate(image,question))
        return descriptions

    def generate_with_images(self, 
                 prompt:str,
                 images:list=[],
                 n_predict: int = 128,
                 callback: Callable[[str, int, dict], bool] = None,
                 verbose: bool = False,
                 **gpt_params ):
        """Generates text out of a prompt and a bunch of images
        This should be implemented by child class

        Args:
            prompt (str): The prompt to use for generation
            images(list): A list of images to interpret
            n_predict (int, optional): Number of tokens to prodict. Defaults to 128.
            callback (Callable[[str, int, dict], None], optional): A callback function that is called everytime a new text element is generated. Defaults to None.
            verbose (bool, optional): If true, the code will spit many informations about the generation process. Defaults to False.
        """
        pass
    


    def generate(self, 
                 prompt:str,
                 n_predict: int = 128,
                 callback: Callable[[str, int, dict], bool] = None,
                 verbose: bool = False,
                 **gpt_params ):
        """Generates text out of a prompt
        This should be implemented by child class

        Args:
            prompt (str): The prompt to use for generation
            n_predict (int, optional): Number of tokens to prodict. Defaults to 128.
            callback (Callable[[str, int, dict], None], optional): A callback function that is called everytime a new text element is generated. Defaults to None.
            verbose (bool, optional): If true, the code will spit many informations about the generation process. Defaults to False.
        """
        pass
    
    def tokenize(self, prompt:str):
        """
        Tokenizes the given prompt using the model's tokenizer.

        Args:
            prompt (str): The input prompt to be tokenized.

        Returns:
            list: A list of tokens representing the tokenized prompt.
        """
        return prompt.split(" ")

    def detokenize(self, tokens_list:list):
        """
        Detokenizes the given list of tokens using the model's tokenizer.

        Args:
            tokens_list (list): A list of tokens to be detokenized.

        Returns:
            str: The detokenized text as a string.
        """
        return " ".join(tokens_list)


    def embed(self, text):
        """
        Computes text embedding
        Args:
            text (str): The text to be embedded.
        Returns:
            List[float]
        """
        pass


    def list_models(self):
        """Lists the models for this binding
        """
        models = []
        for models_folder in self.models_folders:
            if models_folder.name in ["ggml","gguf","gpt4all"]:
                models+=[f.name for f in models_folder.iterdir() if f.is_dir() and not f.stem.startswith(".") or f.suffix==".reference"]
            else:
                models+=[f.name for f in models_folder.iterdir() if f.is_dir() and not f.stem.startswith(".") or f.suffix==".reference"]
        return models
    

    def get_available_models(self, app:LoLLMsCom=None):
        # Create the file path relative to the child class's directory
        full_data = []
        for models_dir_name in self.models_dir_names:
            self.models_db = ModelsDB(self.lollms_paths.models_zoo_path/f"{models_dir_name}.db")
            full_data+=self.models_db.query()
        
        return full_data

    def search_models(self, app:LoLLMsCom=None):
        # Create the file path relative to the child class's directory
        full_data = []
        for models_dir_name in self.models_dir_names:
            self.models_db = ModelsDB(self.lollms_paths.models_zoo_path/f"{models_dir_name}.db")
            full_data+=self.models_db.query()
        
        return full_data           

    @staticmethod
    def vram_usage():
        try:
            output = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.total,memory.used,gpu_name', '--format=csv,nounits,noheader'])
            lines = output.decode().strip().split('\n')
            vram_info = [line.split(',') for line in lines]
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {
            "nb_gpus": 0
            }
        
        ram_usage = {
            "nb_gpus": len(vram_info)
        }
        
        if vram_info is not None:
            for i, gpu in enumerate(vram_info):
                ram_usage[f"gpu_{i}_total_vram"] = int(gpu[0])*1024*1024
                ram_usage[f"gpu_{i}_used_vram"] = int(gpu[1])*1024*1024
                ram_usage[f"gpu_{i}_model"] = gpu[2].strip()
        else:
            # Set all VRAM-related entries to None
            ram_usage["gpu_0_total_vram"] = None
            ram_usage["gpu_0_used_vram"] = None
            ram_usage["gpu_0_model"] = None
        
        return ram_usage

    @staticmethod
    def clear_cuda():
        import torch
        ASCIIColors.red("*-*-*-*-*-*-*-*")
        ASCIIColors.red("Cuda VRAM usage")
        ASCIIColors.red("*-*-*-*-*-*-*-*")
        print(LLMBinding.vram_usage())
        try:
            torch.cuda.empty_cache()
            ASCIIColors.green("Cleared cache")
        except Exception as ex:
            ASCIIColors.error("Couldn't clear cuda memory")
        ASCIIColors.red("*-*-*-*-*-*-*-*")
        ASCIIColors.red("Cuda VRAM usage")
        ASCIIColors.red("*-*-*-*-*-*-*-*")
        print(LLMBinding.vram_usage())


# ===============================

class BindingBuilder:
    def build_binding(
                        self, 
                        config: LOLLMSConfig, 
                        lollms_paths:LollmsPaths,
                        installation_option:InstallOption=InstallOption.INSTALL_IF_NECESSARY,
                        lollmsCom=None
                    )->LLMBinding:

        binding:LLMBinding = self.getBinding(config, lollms_paths)
        return binding(
                config,
                lollms_paths=lollms_paths,
                installation_option = installation_option,
                lollmsCom=lollmsCom
                )
    
    def getBinding(
                        self, 
                        config: LOLLMSConfig, 
                        lollms_paths:LollmsPaths,
                    )->LLMBinding:
        
        if len(str(config.binding_name).split("/"))>1:
            binding_path = Path(config.binding_name)
        else:
            binding_path = lollms_paths.bindings_zoo_path / config["binding_name"]

        # define the full absolute path to the module
        absolute_path = binding_path.resolve()
        # infer the module name from the file path
        module_name = binding_path.stem
        # use importlib to load the module from the file path
        loader = importlib.machinery.SourceFileLoader(module_name, str(absolute_path / "__init__.py"))
        binding_module = loader.load_module()
        binding:LLMBinding = getattr(binding_module, binding_module.binding_name)
        return binding
    
class ModelBuilder:
    def __init__(self, binding:LLMBinding):
        self.binding = binding
        self.model = None
        self.build_model() 

    def build_model(self, model_name=None):
        self.model = self.binding.build_model(model_name)

    def get_model(self):
        return self.model

