#!/bin/bash
cd ~/lollms-webui
# activate conda environment
source ~/miniconda/etc/profile.d/conda.sh
conda activate ./env

# Run lollms webui
python3 app.py

# Exit WSL
exit
