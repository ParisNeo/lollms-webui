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
echo "V8.5 (alpha)"
echo "-----------------"
echo "By ParisNeo"
echo "-----------------"


cd "$(dirname "$0")"
echo "This script is for users who already have conda installed on their system. If you have conda installed on your system then press enter to continue. If you don't have conda, please exit this script, install conda then restart it. You can also use the other linux install script that will install miniconda for you."


export PACKAGES_TO_INSTALL="python=3.11 git pip"
read -rp "Press Enter to continue..."

clear



# Better isolation for virtual environment
unset CONDA_SHLVL
export PYTHONNOUSERSITE=1
unset PYTHONPATH
unset PYTHONHOME

REPO_URL="https://github.com/ParisNeo/lollms-webui.git"

conda create --name lollms $PACKAGES_TO_INSTALL  -y

# Activate installer environment
conda activate lollms || ( echo && echo "Conda environment activation failed." && exit 1 )


# Clone the repository
if [ -d "lollms-webui" ]; then
  cd lollms-webui || exit 1
  git pull
  git submodule update --init --recursive
  cd
  cd lollms-core 
  pip install -e .
  cd ..
  cd utilities/safe_store
  pip install -e .
  cd ../..

else
  git clone --depth 1  --recurse-submodules "$REPO_URL"
  git submodule update --init --recursive
  cd lollms-webui/lollms_core
  pip install -e .
  cd ..
  cd utilities/safe_store
  pip install -e .
  cd ../..

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


# cd scripts/python/lollms_installer
# python main.py
# cd ..
echo "Creating a bin dir (required for llamacpp binding)"
mkdir ../installer_files/lollms_env/bin


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
