#!/bin/bash

# Check if miniconda3/bin/conda exists
if [ -e "$HOME/miniconda3/bin/conda" ]; then
    echo "Conda is installed!"
else
    echo "Conda is not installed. Please install it first."
    echo Installing conda
    curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    ./Miniconda3-latest-Linux-x86_64.sh -b
    rm ./Miniconda3-latest-Linux-x86_64.sh
    echo Done
fi
PATH="$HOME/miniconda3/bin:$PATH"
export PATH
echo "Initializing conda"
conda init --all
export PATH
echo "Installing vllm"
conda create -n vllm python=3.9 -y
echo "Activating vllm environment"
source activate vllm 
pip install vllm
echo "Done"
