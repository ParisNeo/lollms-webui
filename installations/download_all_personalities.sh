#!/bin/bash

# Set the environment name
environment_name="env"

# Activate the virtual environment
source "$environment_name/scripts/activate"

# Change to the installations subfolder

# Run the Python script
python installations/download_all_personalities.py

# Deactivate the virtual environment
echo "deactivating"
deactivate

# Remove tmp folder
folder="tmp"

if [ -d "$folder" ]; then
    echo "Folder exists. Deleting..."
    rm -r "$folder"
    echo "Folder deleted."
else
    echo "Folder does not exist."
fi