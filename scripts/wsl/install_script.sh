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
echo " By ParisNeo"

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
conda create --prefix ./env python=3.10 pip -y
conda activate ./env



# Prompt the user for CPU or GPU installation
read -p "Do you want to use your CPU or GPU for installation? (CPU/GPU): " choice

if [[ "$choice" == "GPU" ]]; then
    # Install CUDA (only if not already installed)
    if ! dpkg -l | grep cuda; then
        echo "Installing CUDA..."
        # install cuda
        wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu.pin
        sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600
        sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/3bf863cc.pub
        sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/ /"
        sudo apt-get update
        sudo apt-get -y install cuda
        # Add cuda to the path
        export PATH=/usr/local/cuda/bin:$PATH
        #make it permanant
        echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
        export LD_LIBRARY_PATH=/usr/local/cuda-12.2/targets/x86_64-linux/lib/:$LD_LIBRARY_PATH
        #make it permanant
        echo "export LD_LIBRARY_PATH=/usr/local/cuda-12.2/targets/x86_64-linux/lib/:$LD_LIBRARY_PATH" >> ~/.bashrc
    else
        echo "CUDA is already installed."
    fi
else
    # CPU installation
    echo "Using CPU for installation..."
fi

# Initilize all submodules and set them to main branch
echo "Initializing submodules"
git submodule update --init
cd zoos/bindings_zoo
git checkout main
cd ../personalities_zoo
git checkout main
cd ../extensions_zoo
git checkout main
cd ../models_zoo
git checkout main

cd ../..

cd lollms_core
git checkout main

cd ../utilities/safe_store
git checkout main

cd ../..

# Install requirements
pip install -r requirements.txt
python -m pip install -e lollms_core --upgrade
python -m pip install -e utilities/safe_store --upgrade

# by default ubuntu will start in lollms-webui path
echo 'cd ~/lollms-webui' >> ~/.bashrc
# Add automatic conda activate
echo 'conda activate ./env' >> ~/.bashrc


# Exit WSL
exit
