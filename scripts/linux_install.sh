#!/bin/bash

# This script will install miniconda and git with all dependencies for this project
# This enables a user to install this project without manually installing conda and git.


cd "$(dirname "$0")"

if [[ "$PWD" == *" "* ]]; then
  echo "This script relies on Miniconda which cannot be silently installed under a path with spaces."
  exit 1
fi

echo "WARNING: This script relies on Miniconda which will fail to install if the path is too long."

if [[ "$PWD" =~ [^#\$\%\&\(\)\*\+\] ]]; then
  echo "WARNING: Special characters were detected in the installation path!"
  echo "         This can cause the installation to fail!"
fi




read -rp "Press Enter to continue..."

clear

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

echo "Please specify if you want to use a GPU or CPU."
echo "*Note* that only NVidea GPUs (cuda) or AMD GPUs (rocm) are supported."
echo "A) Enable Cuda (for nvidia GPUS)"
echo "B) Enable ROCm (for AMD GPUs)"
echo "C) Run CPU mode"
echo
read -rp "Input> " gpuchoice
gpuchoice="${gpuchoice:0:1}"

if [[ "${gpuchoice^^}" == "A" ]]; then
  PACKAGES_TO_INSTALL="python=3.10 cuda-toolkit ninja git gcc"
  CHANNEL="-c nvidia/label/cuda-11.7.0 -c nvidia -c conda-forge"
elif [[ "${gpuchoice^^}" == "B" ]]; then
  PACKAGES_TO_INSTALL="python=3.10  rocm-comgr rocm-smi ninja git gcc"
  CHANNEL=" -c conda-forge"
elif [[ "${gpuchoice^^}" == "C" ]]; then
  PACKAGES_TO_INSTALL="python=3.10 ninja git gcc"
  CHANNEL="-c conda-forge"
else
  echo "Invalid choice. Exiting..."
  exit 1
fi

# Better isolation for virtual environment
unset CONDA_SHLVL
export PYTHONNOUSERSITE=1
unset PYTHONPATH
unset PYTHONHOME
export TEMP="$PWD/installer_files/temp"
export TMP="$PWD/installer_files/temp"

MINICONDA_DIR="$PWD/installer_files/miniconda3"
INSTALL_ENV_DIR="$PWD/installer_files/lollms_env"
MINICONDA_DOWNLOAD_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
REPO_URL="https://github.com/ParisNeo/lollms-webui.git"

if [ ! -f "$MINICONDA_DIR/Scripts/conda" ]; then
  # Download miniconda
  echo "Downloading Miniconda installer from $MINICONDA_DOWNLOAD_URL"
  curl -LOk "$MINICONDA_DOWNLOAD_URL"

  # Install miniconda
  echo
  echo "Installing Miniconda to $MINICONDA_DIR"
  echo "Please wait..."
  echo
  bash "Miniconda3-latest-Linux-x86_64.sh" -b -p "$MINICONDA_DIR" || ( echo && echo "Miniconda installer not found." && exit 1 )
  rm -f "Miniconda3-latest-Linux-x86_64.sh"
  if [ ! -f "$MINICONDA_DIR/bin/activate" ]; then
    echo && echo "Miniconda install failed." && exit 1
  fi
fi

# Activate miniconda
source "$MINICONDA_DIR/bin/activate" || ( echo "Miniconda hook not found." && exit 1 )

# Create the installer environment
if [ ! -d "$INSTALL_ENV_DIR" ]; then
  echo "Packages to install: $PACKAGES_TO_INSTALL"
  conda create -y -k -p "$INSTALL_ENV_DIR" $CHANNEL $PACKAGES_TO_INSTALL || ( echo && echo "Conda environment creation failed." && exit 1 )
  if [[ "${gpuchoice^^}" == "A" ]]; then
    conda run --live-stream -p "$INSTALL_ENV_DIR" python -m pip install torch==2.0.1+cu117 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117 || ( echo && echo "Pytorch installation failed." && exit 1 )
  elif [[ "${gpuchoice^^}" == "B" ]]; then
    conda run --live-stream -p "$INSTALL_ENV_DIR" python -m pip install torch torchvision torchaudio  --index-url https://download.pytorch.org/whl/rocm5.4.2 || ( echo && echo "Pytorch installation failed." && exit 1 )
  elif [[ "${gpuchoice^^}" == "C" ]]; then
    conda run --live-stream -p "$INSTALL_ENV_DIR" python -m pip install torch torchvision torchaudio || ( echo && echo "Pytorch installation failed." && exit 1 )
  fi
fi

# Check if conda environment was actually created
if [ ! -x "$INSTALL_ENV_DIR/bin/python" ]; then
  echo && echo "Conda environment is empty." && exit 1
fi

# Activate installer environment
source activate "$INSTALL_ENV_DIR" || ( echo && echo "Conda environment activation failed." && exit 1 )

# Set default cuda toolkit to the one in the environment
export CUDA_PATH="$INSTALL_ENV_DIR"

# Clone the repository
if [ -d "lollms-webui" ]; then
  cd lollms-webui || exit 1
  git pull
else
  git clone "$REPO_URL"
  cd lollms-webui || exit 1
fi

# Loop through each "git+" requirement and uninstall it (workaround for inconsistent git package updating)
while IFS= read -r requirement; do
  if echo "$requirement" | grep -q "git+"; then
    package_name=$(echo "$requirement" | awk -F'/' '{ print $4 }' | awk -F'@' '{ print $1 }')
    python -m pip uninstall -y "$package_name"
  fi
done < requirements.txt

# Install the pip requirements
python -m pip install -r requirements.txt --upgrade

if [[ -e "../linux_run.sh" ]]; then
    echo "Linux run found"
else
    cp scripts/linux_run.sh ../
fi

if [[ -e "../linux_update.sh" ]]; then
    echo "Linux update found"
else
    cp scripts/linux_update.sh ../
fi

if [[ -e "../linux_conda_session.sh" ]]; then
    echo "Linux update found"
else
    cp scripts/linux_conda_session.sh ../
fi

if [[ -e "../linux_update_models.sh" ]]; then
    echo "Linux update found"
else
    cp scripts/linux_update_models.sh ../
fi

if [[ "${gpuchoice^^}" == "C" ]]; then
    echo "This is a .no_gpu file." > .no_gpu
    echo "You have chosen to use only CPU on this system."
else
    echo "You have chosen to use GPU on this system."
fi

PrintBigMessage() {
  echo
  echo "*******************************************************************"
  for message in "$@"; do
    echo "* $message"
  done
  echo "*******************************************************************"
  echo
}

PrintBigMessage "$@"

exit 0
