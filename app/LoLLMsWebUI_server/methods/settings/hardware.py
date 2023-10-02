import subprocess
import psutil
from typing import Optional
from lollms.helpers import ASCIIColors
from flask import jsonify
from pathlib import Path


def upgrade_to_gpu(self):
    ASCIIColors.yellow("Received command to upgrade to GPU")
    ASCIIColors.info("Installing cuda toolkit")
    res = subprocess.check_call(["conda", "install", "-c", "nvidia/label/cuda-11.7.0", "-c", "nvidia", "-c", "conda-forge",  "cuda-toolkit", "ninja", "git",  "--force-reinstall", "-y"])
    if res!=0:
        ASCIIColors.red("Couldn't install cuda toolkit")
        return jsonify({'status':False, "error": "Couldn't install cuda toolkit. Make sure you are running from conda environment"})
    ASCIIColors.green("Cuda toolkit installed successfully")
    ASCIIColors.yellow("Removing pytorch")
    try:
        res = subprocess.check_call(["pip","uninstall","torch", "torchvision", "torchaudio", "-y"])
    except :
        pass
    ASCIIColors.green("PyTorch unstalled successfully")
    ASCIIColors.yellow("Installing pytorch with cuda support")
    res = subprocess.check_call(["pip","install","--upgrade","torch==2.0.1+cu117", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cu117","--no-cache"])
    if res==0:
        ASCIIColors.green("PyTorch installed successfully")
        import torch
        if torch.cuda.is_available():
            ASCIIColors.success("CUDA is supported.")
        else:
            ASCIIColors.warning("CUDA is not supported. This may mean that the upgrade didn't succeed. Try rebooting the application")
    else:
        ASCIIColors.green("An error hapened")
    self.config.enable_gpu=True
    return jsonify({'status':res==0})



def ram_usage(self):
    """
    Returns the RAM usage in bytes.
    """
    ram = psutil.virtual_memory()
    return jsonify({
        "total_space":ram.total,
        "available_space":ram.free,

        "percent_usage":ram.percent,
        "ram_usage": ram.used
        })

def vram_usage(self) -> Optional[dict]:
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
    
    return jsonify(ram_usage)

def disk_usage(self):
    current_drive = Path.cwd().anchor
    drive_disk_usage = psutil.disk_usage(current_drive)
    try:
        models_folder_disk_usage = psutil.disk_usage(str(self.lollms_paths.personal_models_path/f'{self.config["binding_name"]}'))
        return jsonify( {
            "total_space":drive_disk_usage.total,
            "available_space":drive_disk_usage.free,
            "usage":drive_disk_usage.used,
            "percent_usage":drive_disk_usage.percent,

            "binding_disk_total_space":models_folder_disk_usage.total,
            "binding_disk_available_space":models_folder_disk_usage.free,
            "binding_models_usage": models_folder_disk_usage.used,
            "binding_models_percent_usage": models_folder_disk_usage.percent,
            })
    except Exception as ex:
        return jsonify({
            "total_space":drive_disk_usage.total,
            "available_space":drive_disk_usage.free,
            "percent_usage":drive_disk_usage.percent,

            "binding_disk_total_space": None,
            "binding_disk_available_space": None,
            "binding_models_usage": None,
            "binding_models_percent_usage": None,
            })