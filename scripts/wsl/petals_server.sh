#!/bin/bash
echo changing dir to lollms-webui
cd ~/lollms-webui
# activate conda environment
echo sourcing miniconda
source ~/miniconda/etc/profile.d/conda.sh
echo activating environment
conda activate ./env
echo running server
# Run petals server
python3 -m petals.cli.run_server petals-team/StableBeluga2
