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
source ~/miniconda/etc/profile.d/conda.sh

# Clone the git repository
git clone https://github.com/ParisNeo/lollms-webui.git ~/lollms-webui
cd ~/lollms-webui

# Create and activate conda environment
conda create --prefix ./env python=3.10 pip -y
conda activate ./env

# install cuda
conda install -c anaconda cudatoolkit==11.7
export LD_LIBRARY_PATH=/path/to/directory:$LD_LIBRARY_PATH
#make it permanant
echo "export LD_LIBRARY_PATH=\"\$LD_LIBRARY_PATH:$new_path\"" >> ~/.bashrc
# Install requirements
pip install -r requirements.txt

# Exit WSL
exit
