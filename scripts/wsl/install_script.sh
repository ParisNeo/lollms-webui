#!/bin/bash
echo "      ___       ___           ___       ___       ___           ___      "
echo "     /\__\     /\  \         /\__\     /\__\     /\__\         /\  \     "
echo "    /:/  /    /::\  \       /:/  /    /:/  /    /::|  |       /::\  \    "
echo "   /:/  /    /:/\:\  \     /:/  /    /:/  /    /:|:|  |      /:/\ \  \   "
echo "  /:/  /    /:/  \:\  \   /:/  /    /:/  /    /:/|:|__|__   _\:\~\ \  \  "
echo " /:/__/    /:/__/ \:\__\ /:/__/    /:/__/    /:/ |::::\__\ /\ \:\ \ \__\ "
echo " \:\  \    \:\  \ /:/  / \:\  \    \:\  \    \/__/~~/:/  / \:\ \:\ \/__/ "
echo "  \:\  \    \:\  /:/  /   \:\  \    \:\  \         /:/  /   \:\ \:\__\   "
echo "   \:\  \    \:\/:/  /     \:\  \    \:\  \       /:/  /     \:\/:/  /   "
echo "    \:\__\    \::/  /       \:\__\    \:\__\     /:/  /       \::/  /    "
echo "     \/__/     \/__/         \/__/     \/__/     \/__/         \/__/     "
echo "V9.5"
echo "-----------------"
echo "By ParisNeo"
echo "-----------------"

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
#make it permanant
echo 'source ~/miniconda/etc/profile.d/conda.sh' >> ~/.bashrc

# Clone the git repository
git clone https://github.com/ParisNeo/lollms-webui.git ~/lollms-webui
cd ~/lollms-webui

# Create and activate conda environment
conda create --prefix ./env python=3.11 git pip -y
conda activate ./env



# Initilize all submodules and set them to main branch
echo "Initializing submodules"
git submodule update --init --recursive
cd lollms-webui\lollms_core
pip install -e .
cd ..\..

# Install requirements
pip install -r requirements.txt

# by default ubuntu will start in lollms-webui path
echo 'cd ~/lollms-webui' >> ~/.bashrc
# Add automatic conda activate
echo 'conda activate ./env' >> ~/.bashrc


cd scripts/python/lollms_installer
python main.py
cd ..

# Exit WSL
exit
