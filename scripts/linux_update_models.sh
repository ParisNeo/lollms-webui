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
echo " Models list update script"

cd "$(dirname "$0")"

# better isolation for virtual environment
CONDA_SHLVL=""
PYTHONNOUSERSITE=1
PYTHONPATH=""
PYTHONHOME=""
TEMP="./installer_files/temp"
TMP="./installer_files/temp"
INSTALL_ENV_DIR="./installer_files/lollms_env"
MINICONDA_DIR="./installer_files/miniconda3"

if [ ! -f "$MINICONDA_DIR/bin/activate" ]; then
    echo "Miniconda not found."
    exit 1
fi

source "$MINICONDA_DIR/bin/activate" "$INSTALL_ENV_DIR"


# Set your repository URL and file path
repository_url="https://github.com/ParisNeo/lollms_bindings_zoo.git"

# Set the destination folder where the file will be downloaded
destination_folder="downloaded_files"

# Create the destination folder if it doesn't exist
if [ ! -d "$destination_folder" ]; then
    mkdir "$destination_folder"
fi

# Clone the repository (if not already cloned)
if [ ! -d "$destination_folder/repository" ]; then
    git clone "$repository_url" "$destination_folder/repository"
fi

cd "$destination_folder/repository"

echo "Updating models"
cp hugging_face/models.yaml ../../personal_data/bindings_zoo/hugging_face/models.yaml
cp c_transformers/models.yaml ../../personal_data/bindings_zoo/c_transformers/models.yaml
cp llama_cpp_official/models.yaml ../../personal_data/bindings_zoo/llama_cpp_official/models.yaml
cp gpt_4all/models.yaml ../../personal_data/bindings_zoo/gpt_4all/models.yaml
cp py_llama_cpp/models.yaml ../../personal_data/bindings_zoo/py_llama_cpp/models.yaml
cp gptq/models.yaml ../../personal_data/bindings_zoo/gptq/models.yaml
cp exllama/models.yaml ../../personal_data/bindings_zoo/exllama/models.yaml
echo "Updating models"
