#!/bin/bash

# Update and upgrade packages
sudo apt update
sudo apt upgrade -y
# Add a repository for Python 3.10
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.10 and pip
sudo apt install python3.10 python3-pip -y
# Create symlinks for python and pip
sudo ln -s /usr/bin/python3.10 /usr/local/bin/python
sudo ln -s /usr/bin/pip3 /usr/local/bin/pip

# Install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p ~/miniconda
rm ~/miniconda.sh

# Clone the git repository
git clone https://github.com/ParisNeo/lollms-webui.git ~/lollms-webui
cd ~/lollms-webui

# Create and activate conda environment
conda create --prefix ./env python=3.10 pip -y
conda activate env

# Install requirements
pip install -r requirements.txt

# Exit WSL
exit
