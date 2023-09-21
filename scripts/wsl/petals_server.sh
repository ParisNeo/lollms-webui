#!/bin/bash
cd ~/lollms-webui
# activate conda environment
source ~/miniconda/etc/profile.d/conda.sh
conda activate ./env

# Run petals server
python3 -m petals.cli.run_server petals-team/StableBeluga2
