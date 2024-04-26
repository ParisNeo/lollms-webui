#!/bin/bash
#
# This script will install Miniconda and git with all dependencies for this project.
# This enables a user to install this project without manually installing Conda and git.

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


export PACKAGES_TO_INSTALL=python=3.11 git pip


# This will test if homebrew is installed on the mac.
# If not installed it will install homebrew. 

echo "*****************************************************"
echo "*** Homebriew is required for LoLLMs Install      ***"
echo "*** Checking if Homebrew is installed             ***"
echo "***                                               ***"
which -s brew
if [[ $? != 0 ]] ; then
    # Install Homebrew
   echo "*** Please Install Homebrew - See https://brew.sh ***"
   echo "*****************************************************"
   exit 1
else
   echo "*** Homebrew is installed - Continuing            ***"
   echo "***                                               ***"
fi

# This will test if GCC is installed.
# If GCC is installed it will attempt an upgrade
# if it is not installed it will install gcc using homebrew
echo "*** Checking if GCC is installed                  ***"
echo "***                                               ***"
if brew list gcc &>/dev/null; then
	echo "*** GCC is already installed - Upgrading          ***"
	echo "*****************************************************"
else
	echo "*** GCC Not Installed - Installing                ***"
	echo "*****************************************************"
	brew install gcc
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
ENV_NAME="lollms"
INSTALL_DIR="$PWD"

arch=$(uname -m)
if [ "$arch" == "arm64" ]; then
    MINICONDA_DOWNLOAD_URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh"
else
    MINICONDA_DOWNLOAD_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
fi

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

  if [ "$arch" == "arm64" ]; then
    bash "Miniforge3-MacOSX-arm64.sh" -b -p "$MINICONDA_DIR" || ( echo && echo "Miniconda installer not found." && exit 1 )
    rm -f "Miniforge3-MacOSX-arm64.sh"
    if [ ! -f "$MINICONDA_DIR/bin/activate" ]; then
      echo && echo "Miniconda install failed." && exit 1
    fi
  
  else
    bash "Miniconda3-latest-MacOSX-x86_64.sh" -b -p "$MINICONDA_DIR" || ( echo && echo "Miniconda installer not found." && exit 1 )
    rm -f "Miniconda3-latest-MacOSX-x86_64.sh"
    if [ ! -f "$MINICONDA_DIR/bin/activate" ]; then
      echo && echo "Miniconda install failed." && exit 1
    fi
  
  fi
fi

# Activate Miniconda
source "$MINICONDA_DIR/bin/activate" || ( echo "Miniconda hook not found." && exit 1 )

# Create the installer environment
if [ ! -d "$INSTALL_ENV_DIR" ]; then
  echo "Packages to install: $PACKAGES_TO_INSTALL"
  conda create -y -k -n "$ENV_NAME" $CHANNEL $PACKAGES_TO_INSTALL || ( echo && echo "Conda environment creation failed." && exit 1 )
  echo "Conda created and using packages: $PACKAGES_TO_INSTALL"
fi

# Activate installer environment
source activate "$ENV_NAME" || ( echo && echo "Conda environment activation failed." && exit 1 )

# install conda
conda install conda -y

echo "$ENV_NAME Activated"
# Set default CUDA toolkit to the one in the environment
export CUDA_PATH="$INSTALL_ENV_DIR"

# Clone the repository
cd $INSTALL_DIR
if [ -d "lollms-webui" ]; then
  cd $INSTALL_DIR/lollms-webui || exit 1
  git pull
  git submodule update --init --recursive
  cd $INSTALL_DIR/lollms-webui/lollms_core 
  pip install -e .
  cd $INSTALL_DIR/lollms-webuil/utilities/safe_store
  pip install -e .

else
  git clone --depth 1  --recurse-submodules "$REPO_URL"
  git submodule update --init --recursive
  cd $INSTALL_DIR/lollms-webui/lollms_core
  pip install -e .
  cd $INSTALL_DIR/lollms-webui/utilities/safe_store
  pip install -e .

  cd $INSTALL_DIR/lollms-webui || exit 1
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

if [[ -e "../macos_run.sh" ]]; then
    echo "Macos run found"
else
    cp scripts/macos/macos_run.sh $INSTALL_DIR/ 
fi

if [[ -e "../macos_update.sh" ]]; then
    echo "Macos update found"
else
    cp scripts/macos/macos_update.sh $INSTALL_DIR/ 
fi

if [[ -e "../macos_conda_session.sh" ]]; then
    echo "Macos conda session found"
else
    cp scripts/macos/macos_conda_session.sh $INSTALL_DIR/ 
fi


# cd scripts/python/lollms_installer
# python main.py
# cd ..

echo "Creating a bin dir (required for llamacpp binding)"
mkdir -p $INSTALL_DIR/installer_files/lollms_env/bin


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


