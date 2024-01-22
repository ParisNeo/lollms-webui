#!/bin/bash
echo Starting LOLLMS Web UI...
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


cd "$(dirname "$0")"

# better isolation for virtual environment
CONDA_SHLVL=""
PYTHONNOUSERSITE=1
PYTHONPATH=""
PYTHONHOME=""
miniconda_folder="./installer_files"
TMP="./installer_files/temp"

if  [ -e "$miniconda_folder" ]; then
    INSTALL_ENV_DIR="lollms"
    MINICONDA_DIR="./installer_files/miniconda3"
    MINICONDA_CMD="$MINICONDA_DIR/bin/activate"
else
    INSTALL_ENV_DIR="lollms"
    MINICONDA_CMD="conda activate"
fi

source "$MINICONDA_CMD" "$INSTALL_ENV_DIR"
cd lollms-webui

# set default cuda toolkit to the one in the environment
CUDA_PATH="$INSTALL_ENV_DIR"

python app.py "$@"

read -rp "Press Enter to exit..."
