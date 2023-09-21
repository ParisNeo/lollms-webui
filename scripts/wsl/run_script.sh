#!/bin/bash
echo changing dir to lollms-webui
cd ~/lollms-webui
# activate conda environment
echo sourcing miniconda
source ~/miniconda/etc/profile.d/conda.sh
echo activating environment
conda activate ./env
echo running lollmw-webui
# Run lollms webui
python3 app.py

# Exit WSL
exit
