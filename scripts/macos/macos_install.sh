#!/bin/bash

# This script will install Miniconda and git with all dependencies for this project.
# This enables a user to install this project without manually installing Conda and git.

cd "$(dirname "$0")"

if [[ "$PWD" == *" "* ]]; then
  echo "This script relies on Miniconda, which cannot be silently installed under a path with spaces."
  exit 1
fi

echo "WARNING: This script relies on Miniconda, which will fail to install if the path is too long."

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
echo "A) Enable GPU"
echo "B) Run CPU mode"
echo
read -rp "Input> " gpuchoice
gpuchoice="${gpuchoice:0:1}"
uppercase_gpuchoice=$(echo "$gpuchoice" | tr '[:lower:]' '[:upper:]')
if [[ "$uppercase_gpuchoice" == "A" ]]; then
  PACKAGES_TO_INSTALL="python=3.10 cuda-toolkit ninja git"
  CHANNEL="-c pytorch -c conda-forge"
elif [[ "$uppercase_gpuchoice" == "B" ]]; then
  PACKAGES_TO_INSTALL="python=3.10 ninja git"
  CHANNEL="-c conda-forge"
else
  echo "Invalid choice. Exiting..."
  exit 1
fi

echo "Installing gcc..."
brew install gcc

# Better isolation for virtual environment
unset CONDA_SHLVL
export PYTHONNOUSERSITE=1
unset PYTHONPATH
unset PYTHONHOME
export TEMP="$PWD/installer_files/temp"
export TMP="$PWD/installer_files/temp"

MINICONDA_DIR="$PWD/installer_files/miniconda3"
INSTALL_ENV_DIR="$PWD/installer_files/lollms_env"
ENV_NAME="lollms"
MINICONDA_DOWNLOAD_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
REPO_URL="https://github.com/ParisNeo/lollms-webui.git"

if [ ! -f "$MINICONDA_DIR/Scripts/conda" ]; then
  # Download Miniconda
  echo "Downloading Miniconda installer from $MINICONDA_DOWNLOAD_URL"
  curl -LOk "$MINICONDA_DOWNLOAD_URL"

  # Install Miniconda
  echo
  echo "Installing Miniconda to $MINICONDA_DIR"
  echo "Please wait..."
  echo
  bash "Miniconda3-latest-MacOSX-x86_64.sh" -b -p "$MINICONDA_DIR" || ( echo && echo "Miniconda installer not found." && exit 1 )
  rm -f "Miniconda3-latest-MacOSX-x86_64.sh"
  if [ ! -f "$MINICONDA_DIR/bin/activate" ]; then
    echo && echo "Miniconda install failed." && exit 1
  fi
fi

# Activate Miniconda
source "$MINICONDA_DIR/bin/activate" || ( echo "Miniconda hook not found." && exit 1 )

# Create the installer environment
if [ ! -d "$INSTALL_ENV_DIR" ]; then
  echo "Packages to install: $PACKAGES_TO_INSTALL"
  conda create -y -k -n "$ENV_NAME" $CHANNEL $PACKAGES_TO_INSTALL || ( echo && echo "Conda environment creation failed." && exit 1 )
  echo "Conda created and using packages: $PACKAGES_TO_INSTALL"
  echo "Installing tools"
  if [[ "$(echo $gpuchoice | tr '[:lower:]' '[:upper:]')" == "A" ]]; then
    conda run --live-stream -n "$ENV_NAME" python -m pip install torch torchvision torchaudio --channel pytorch --channel conda-forge || ( echo && echo "Pytorch installation failed." && exit 1 )
  elif [[ "$(echo $gpuchoice | tr '[:lower:]' '[:upper:]')" == "B" ]]; then
    conda run --live-stream -n "$ENV_NAME" python -m pip install torch torchvision torchaudio --channel pytorch --channel conda-forge || ( echo && echo "Pytorch installation failed." && exit 1 )
  fi
fi

# Activate installer environment
source activate "$ENV_NAME" || ( echo && echo "Conda environment activation failed." && exit 1 )

echo "$ENV_NAME Activated"
# Set default CUDA toolkit to the one in the environment
export CUDA_PATH="$INSTALL_ENV_DIR"

# Clone the repository
if [ -d "lollms-webui" ]; then
  cd lollms-webui || exit 1
  git pull
else
  git clone "$REPO_URL"
  cd lollms-webui || exit 1
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


# Loop through each "git+" requirement and uninstall it (workaround for inconsistent git package updating)
while IFS= read -r requirement; do
  if echo "$requirement" | grep -q "git+"; then
    package_name=$(echo "$requirement" | awk -F'/' '{ print $4 }' | awk -F'@' '{ print $1 }')
    python -m pip uninstall -y "$package_name"
  fi
done < requirements.txt

# Install the pip requirements
python -m pip install -r requirements.txt --upgrade

python -m pip install -e lollms_core --upgrade

python -m pip install -e utilities/safe_store --upgrade

if [[ -e "../macos_run.sh" ]]; then
    echo "Macos run found"
else
    cp scripts/macos/macos_run.sh ../
fi

if [[ -e "../macos_update.sh" ]]; then
    echo "Macos update found"
else
    cp scripts/macos/macos_update.sh ../
fi

uppercase_gpuchoice=$(echo "$gpuchoice" | tr '[:lower:]' '[:upper:]')
if [[ "$uppercase_gpuchoice" == "B" ]]; then
    echo "This is a .no_gpu file." > .no_gpu
else
    echo "GPU is enabled, no .no_gpu file will be created."
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
