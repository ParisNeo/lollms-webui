#!/bin/bash
cd ~/lollms-webui
ls
# activate conda environment
source ~/miniconda/etc/profile.d/conda.sh
conda info --envs
conda activate ./env

# Run lollms webui
python3 app.py

# Exit WSL
exit
