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
# Prompt the user for a model name
read -p "Enter the model name (press Enter for default petals-team/StableBeluga2): " modelName

# Use the default model name if no input is provided
if [ -z "$modelName" ]; then
  modelName="petals-team/StableBeluga2"
fi

# Run the Python command with the chosen model name
python3 -m petals.cli.run_server "$modelName" --public_name https://github.com/ParisNeo/lollms-webui
