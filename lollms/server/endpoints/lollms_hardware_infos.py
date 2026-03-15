"""
project: lollms
file: lollms_hardware_infos.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes are specific to handling hardware information 

"""

from fastapi import APIRouter, Request
import pkg_resources
from lollms.server.elf_server import LOLLMSElfServer
from ascii_colors import ASCIIColors
from lollms.utilities import load_config
from pathlib import Path
from typing import List
import psutil
import subprocess
from ascii_colors import trace_exception

# ----------------------- Defining router and main class ------------------------------
router = APIRouter()
lollmsElfServer = LOLLMSElfServer.get_instance()

@router.get("/disk_usage")
def disk_usage():
    current_drive = Path.cwd().anchor
    drive_disk_usage = psutil.disk_usage(current_drive)
    try:
        models_folder_disk_usage = psutil.disk_usage(str(lollmsElfServer.lollms_paths.personal_models_path/f'{lollmsElfServer.config["binding_name"]}'))
        return {
            "total_space":drive_disk_usage.total,
            "available_space":drive_disk_usage.free,
            "usage":drive_disk_usage.used,
            "percent_usage":drive_disk_usage.percent,

            "binding_disk_total_space":models_folder_disk_usage.total,
            "binding_disk_available_space":models_folder_disk_usage.free,
            "binding_models_usage": models_folder_disk_usage.used,
            "binding_models_percent_usage": models_folder_disk_usage.percent,
            }
    except Exception as ex:
        return {
            "total_space":drive_disk_usage.total,
            "available_space":drive_disk_usage.free,
            "percent_usage":drive_disk_usage.percent,

            "binding_disk_total_space": None,
            "binding_disk_available_space": None,
            "binding_models_usage": None,
            "binding_models_percent_usage": None,
            }

@router.get("/ram_usage")
def ram_usage():
    """
    Returns the RAM usage in bytes.
    """
    ram = psutil.virtual_memory()
    return {
        "total_space":ram.total,
        "available_space":ram.free,

        "percent_usage":ram.percent,
        "ram_usage": ram.used
        }
@router.get("/vram_usage") # Or @app.route("/vram_usage", methods=['GET']) for Flask
def vram_usage():
    """
    Fetches GPU VRAM usage information using nvidia-smi.

    Returns:
        dict: A dictionary containing a 'gpus' key. The value is a list of
              dictionaries, each representing a GPU with its VRAM details.
              Returns {"gpus": []} if nvidia-smi fails or no GPUs are detected.
    """
    gpus_list = []
    try:
        # Execute nvidia-smi to get total memory, used memory, and GPU name
        # The output is in MiB (Mebibytes)
        output = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=memory.total,memory.used,gpu_name', '--format=csv,nounits,noheader'],
            encoding='utf-8' # Decode the output directly
        )

        # Split the output into lines, one line per GPU
        lines = output.strip().split('\n')

        # Process each line
        for line in lines:
            if not line.strip(): # Skip potential empty lines
                continue

            parts = line.split(',')
            if len(parts) != 3:
                print(f"Warning: Unexpected nvidia-smi output line format: {line}")
                continue # Skip this malformed line

            try:
                # Parse values (nvidia-smi returns MiB)
                total_vram_mib = int(parts[0].strip())
                used_vram_mib = int(parts[1].strip())
                gpu_model = parts[2].strip()

                # Convert MiB to Bytes (as expected by filesize library)
                total_vram_bytes = total_vram_mib * 1024 * 1024
                used_vram_bytes = used_vram_mib * 1024 * 1024

                # Calculate available space and percentage
                available_vram_bytes = total_vram_bytes - used_vram_bytes
                percentage_used = 0.0
                if total_vram_bytes > 0:
                    # Calculate percentage and round to 2 decimal places
                    percentage_used = round((used_vram_bytes / total_vram_bytes) * 100, 2)

                # Create the dictionary structure expected by the frontend
                gpu_info = {
                    "total_vram": total_vram_bytes,
                    "used_vram": used_vram_bytes,
                    "available_space": available_vram_bytes, # Frontend uses this in details
                    "gpu_model": gpu_model,
                    "percentage": percentage_used # Frontend uses this directly
                }
                gpus_list.append(gpu_info)

            except ValueError as ve:
                print(f"Warning: Could not parse VRAM numbers from line: {line}. Error: {ve}")
                continue # Skip this line if parsing fails

    except FileNotFoundError:
        # nvidia-smi command not found (likely no NVIDIA drivers or not in PATH)
        print("nvidia-smi command not found. Assuming no compatible GPU.")
        # Return empty list as expected by frontend when no GPUs detected
        gpus_list = []
    except subprocess.CalledProcessError as e:
        # nvidia-smi command failed to execute properly
        print(f"nvidia-smi failed with error code {e.returncode}: {e.output}")
        # Return empty list
        gpus_list = []
    except Exception as e:
        # Catch any other unexpected errors during processing
        trace_exception(e)
        # Return empty list
        gpus_list = []

    # Always return the structure the frontend expects, even if the list is empty
    # If using Flask, use jsonify: return jsonify({"gpus": gpus_list})
    return {"gpus": gpus_list}