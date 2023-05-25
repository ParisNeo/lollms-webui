#!/bin/bash

# Set the environment name
environment_name="env"

# Activate the virtual environment
source "$environment_name/Scripts/activate"

# Change to the installations subfolder

# Run the Python script
python installations/download_all_personalities.py

# Deactivate the virtual environment
echo "deactivating"
deactivate
