#!/bin/bash

# This script will install miniconda and git with all dependencies for this project
# This enables a user to install this project without manually installing conda and git.

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
echo "V14"
echo "-----------------"
echo "By ParisNeo"
echo "-----------------"


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


export PACKAGES_TO_INSTALL=python=3.11 git pip
read -rp "Press Enter to continue..."

clear



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
  curl -LO "$MINICONDA_DOWNLOAD_URL"

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
fi

# Check if conda environment was actually created
if [ ! -x "$INSTALL_ENV_DIR/bin/python" ]; then
  echo && echo "Conda environment is empty." && exit 1
fi

# Activate installer environment
source activate "$INSTALL_ENV_DIR" || ( echo && echo "Conda environment activation failed." && exit 1 )

# install conda
conda install conda -y

echo "Installing pytorch (Required for RAG)"
# Check if CUDA-enabled device is available
if command -v nvidia-smi &> /dev/null && nvidia-smi > /dev/null 2>&1; then
    echo "CUDA-enabled device detected."
    echo "Installing PyTorch with CUDA support..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
else
    echo "No CUDA-enabled device detected."
    echo "Installing PyTorch for CPU only..."
    pip install torch torchvision torchaudio
fi

echo "PyTorch installation complete."

# Set default cuda toolkit to the one in the environment
export CUDA_PATH="$INSTALL_ENV_DIR"


# Clone the repository
if [ -d "lollms-webui" ]; then
  cd lollms-webui || exit 1
  git pull
  git submodule update --init --recursive
  cd lollms_core 
  pip install -e .
  cd ../..

else
  git clone --depth 1  --recurse-submodules "$REPO_URL"
  git submodule update --init --recursive
  cd lollms-webui/lollms_core
  pip install -e .
  cd ../..
fi

cd lollms-webui

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
    cp scripts/linux/linux_run.sh ../
fi


if [[ -e "../linux_conda_session.sh" ]]; then
    echo "Linux update found"
else
    cp scripts/linux/linux_conda_session.sh ../
fi


# cd scripts/python/lollms_installer
# python main.py
# cd ..
echo "Creating a bin dir (required for llamacpp binding)"
mkdir -p $INSTALL_ENV_DIR/bin


echo "Select the default binding to be installed:"
options=("None (install the binding later)" "Local binding - ollama" "Local binding - python_llama_cpp" "Local binding - bs_exllamav2" "Remote binding - open_router" "Remote binding - open_ai" "Remote binding - mistral_ai" "Remote binding - gemini" "Remote binding - xAI" "Remote binding - groq")

select opt in "${options[@]}"
do
    case $opt in
        "None (install the binding later)")
            echo "You selected None. No binding will be installed now."
            break
            ;;
        "Local binding - ollama")
            python zoos/bindings_zoo/ollama/__init__.py
            break
            ;;
        "Local binding - python_llama_cpp")
            python zoos/bindings_zoo/python_llama_cpp/__init__.py
            break
            ;;
        "Local binding - bs_exllamav2")
            python zoos/bindings_zoo/bs_exllamav2/__init__.py
            break
            ;;
        "Remote binding - open_router")
            python zoos/bindings_zoo/open_router/__init__.py
            break
            ;;
        "Remote binding - open_ai")
            python zoos/bindings_zoo/open_ai/__init__.py
            break
            ;;
        "Remote binding - mistral_ai")
            python zoos/bindings_zoo/mistral_ai/__init__.py
            break
            ;;
        "Remote binding - gemini")
            python zoos/bindings_zoo/gemini/__init__.py
            break
            ;;
        "Remote binding - xAI")
            python zoos/bindings_zoo/xAI/__init__.py
            break
            ;;
        "Remote binding - groq")
            python zoos/bindings_zoo/xAI/__init__.py
            break
            ;;
        *) echo "Invalid option $REPLY";;
    esac
done


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
