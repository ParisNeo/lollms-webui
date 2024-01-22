#!/bin/bash

echo "This will uninstall the environment. Are you sure? [Y/N]"
read choice
if [[ "$choice" =~ [yY] ]]; then
    # Download Python installer
    printf "Removing lollms conda environment"
    conda remove --name lollms --all
    echo "OK"
    read -p "Press [Enter] to continue..."
else
    echo "Please install Python and try again."
    read -p "Press [Enter] to continue..."
    exit 1
fi
