#!/bin/bash
echo Starting LOLLMS Web UI...

cd "$(dirname "$0")"

# better isolation for virtual environment
CONDA_SHLVL=""
PYTHONNOUSERSITE=1
PYTHONPATH=""
PYTHONHOME=""
TEMP="$(pwd)/installer_files/temp"
TMP="$(pwd)/installer_files/temp"
INSTALL_ENV_DIR="$(pwd)/installer_files/env"
MINICONDA_DIR="$(pwd)/installer_files/miniconda3"

if [ ! -f "$MINICONDA_DIR/bin/activate.bat" ]; then
    echo "Miniconda not found."
    exit 1
fi

source "$MINICONDA_DIR/bin/activate.bat" activate "$INSTALL_ENV_DIR"
cd lollms-webui

# set default cuda toolkit to the one in the environment
CUDA_PATH="$INSTALL_ENV_DIR"

python app.py "$@"

pause
