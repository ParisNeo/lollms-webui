#!/usr/bin/env bash
echo "\u001b[34m"
echo "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHH     .HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHH.     ,HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHH.##  HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHHH#.HHHHH_*,*,*,*,*,*,*,*,***,*,**#HHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHHHHH.*,,***,***,***,***,***,***,*******HHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHHH*,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,*,,,,,HHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHH.,,,***,***,***,***,***,***,***,***,***,***_HHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHH*,,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*HHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHH#,***,***,***,***,***,***,***,***,***,***,***,**HHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHH..HHH,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,*#HHHHHHHHHHHHHHHH"
echo "HHHHHHH,,,**,_H*,***,***,***,,,*,***,***,***,**,,,**,***,***,***H,,*,***HHHHHHHH"
echo "HHHHHH.*,,,*,,,,,*,*,*,***#HHHHH.,,*,*,*,*,**_HHHHH.,*,*,*,*,*,*,*,*****HHHHHHHH"
echo "HHHHHH.*,***,*,*,***,***,.HHHHHHH_**,***,****HHHHHHH.***,***,***,*******HHHHHHHH"
echo "HHHHHH.,,,,,,,,,,,,,,,,,,,.HHHHH.,,,,,,,,,,,,.HHHHHH,,,,,,,,,,,,,,,,,***HHHHHHHH"
echo "HHHHHH.,,,,,,_H,,,**,***,***,,,*,***,***,***,**,,,,*,***,***,***H***,***HHHHHHHH"
echo "HHHHHHH.,,,,*.H,,,,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,***H*,,,,_HHHHHHHHH"
echo "HHHHHHHHHHHHHHH*,***,***,**,,***,***,***,***,***,***,***,***,**.HHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHH,,,,,,,,*,,#H#,,,,,*,,,*,,,,,,,,*#H*,,,,,,,,,**HHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHH,,*,***,***,**_.HHHHHHHHHHHHH#*,,,*,***,***,*HHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHH,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*HHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHH**,***,***,***,***,***,***,***,***,***,***,*.HHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHH*,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,*HHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHH**,***,***,*******_..HHHHHHHHH.#_*,*,,,***,***HHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHH*,*,*,******#HHHHHHHHHHHHHHHHHHHHHHHHHHHH._**,,,.HHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHH.,,*,***.HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH.*#HHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHH_,,,*.HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHH,,#HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHH.HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "\u001b[0m"

if ping -q -c 1 google.com >/dev/null 2>&1; then
    echo -e "\e[32mInternet Connection working fine\e[0m"
    
    # Install Git
    echo -n "Checking for Git..."
    if command -v git > /dev/null 2>&1; then
      echo "is installed"
    else
      read -p "Git is not installed. Would you like to install Git? [Y/N] " choice
      if [ "$choice" = "Y" ] || [ "$choice" = "y" ]; then
        echo "Installing Git..."
        sudo apt update
        sudo apt install -y git
      else
        echo "Please install Git and try again."
        exit 1
      fi
    fi

    # Check if repository exists
    if [[ -d .git ]] ;then
      echo "Pulling latest changes"
      git pull 
    else
      if [[ -d lollms-webui ]] ;then
        cd lollms-webui
      else
        echo "Cloning repository..."
        git clone https://github.com/ParisNeo/lollms-webui.git ./lollms-webui
        cd lollms-webui
      fi
    fi
    echo "Pulling latest version..."
    git pull

    # Install Conda
    echo -n "Checking for Conda..."
    if command -v conda > /dev/null 2>&1; then
      echo "is installed"
    else
      read -p "Conda is not installed. Would you like to install Conda? [Y/N] " choice
      if [ "$choice" = "Y" ] || [ "$choice" = "y" ]; then
        echo "Installing Conda..."
        curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
        bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda
        source $HOME/miniconda/bin/activate
        conda init bash
        conda update -n base -c defaults conda
      else
        echo "Please install Conda and try again."
        exit 1
      fi
    fi

    # Create a new Conda environment
    echo -n "Creating Conda environment..."
    conda create --prefix ./env python=3.10
    conda activate ./env
    echo "is created"

    # Install the required packages
    echo "Installing requirements..."
    conda install -c gcc
    conda install -c conda-forge cudatoolkit-dev
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt

    if [ $? -ne 0 ]; then
      echo "Failed to install required packages. Please check your internet connection and try again."
      exit 1
    fi

    # Cleanup
    if [ -d "./tmp" ]; then
      rm -rf "./tmp"
      echo "Cleaning tmp folder"
    fi
    # Launch the Python application
    python app.py
else
    # go to the ui folder
    cd lollms-webui
    conda activate ./env
    # Launch the Python application
    python app.py
fi
