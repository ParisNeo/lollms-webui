#!/bin/bash

echo "L🌟LLMS: Lord of Large Language and Multimodal Systems"
echo "V14 SaÏf"
echo "-----------------"
echo "By ParisNeo"
echo "-----------------"

# Store the current path
ORIGINAL_PATH=$(pwd)

cd "$(dirname "$0")"

echo $(pwd)

# Check if Git is installed
if ! command -v git &> /dev/null
then
    echo "Git is not installed. Please install Git using your distribution's package manager."
    exit 1
else
    echo "Git is already installed."
fi

LOLLMSENV_DIR="$PWD/lollmsenv"
REPO_URL="https://github.com/ParisNeo/lollms-webui.git"

USE_MASTER=0
if [ "$1" == "--use-master" ]; then
    USE_MASTER=1
fi

if [ $USE_MASTER -eq 1 ]; then
    echo "--- Using current master repo for LollmsEnv..."
    git clone https://github.com/ParisNeo/LollmsEnv.git "$LOLLMSENV_DIR"
    cd "$LOLLMSENV_DIR"
    bash install.sh --dir "$LOLLMSENV_DIR" -y
    cd ..
else
    # Download LollmsEnv installer
    echo "Downloading LollmsEnv installer..."
    wget https://github.com/ParisNeo/LollmsEnv/releases/download/V1.4.2/lollmsenv_installer.sh
    # Install LollmsEnv
    echo "--- Installing lollmsenv"
    bash lollmsenv_installer.sh --dir "$LOLLMSENV_DIR" -y
fi

# Check for NVIDIA GPU and CUDA
echo "--- Checking for NVIDIA GPU and CUDA..."
if command -v nvidia-smi &> /dev/null
then
    echo "NVIDIA GPU detected."
    echo "Querying GPU information..."
    
    GPU_INFO=$(nvidia-smi --query-gpu=name,driver_version,memory.total,utilization.gpu,temperature.gpu --format=csv,noheader,nounits)
    
    IFS=',' read -r GPU_NAME DRIVER_VERSION TOTAL_MEMORY GPU_UTILIZATION GPU_TEMPERATURE <<< "$GPU_INFO"
    
    echo "GPU Name: $GPU_NAME"
    echo "Driver Version: $DRIVER_VERSION"
    echo "Total Memory: $TOTAL_MEMORY MiB"
    echo "GPU Utilization: $GPU_UTILIZATION %"
    echo "GPU Temperature: $GPU_TEMPERATURE C"
    
    echo "Extracting CUDA version..."
    CUDA_VERSION=$(nvidia-smi | grep "CUDA Version" | sed 's/.*CUDA Version: \([0-9.]*\).*/\1/')
    echo "CUDA Version: $CUDA_VERSION"

    echo "For optimal performance, ensure you have CUDA version 12.1 or higher."
    echo "If you need to update, visit https://developer.nvidia.com/cuda-downloads"
else 
    echo "No NVIDIA GPU detected or nvidia-smi is not available."
fi

# Ask user about CUDA installation
read -p "Do you want to install CUDA? (Only for NVIDIA GPUs if your version is lower than 12.1 or if it wasn't already installed, recommended for local AI) [Y/N]: " INSTALL_CUDA
if [[ $INSTALL_CUDA =~ ^[Yy]$ ]]
then
    echo "Please visit https://developer.nvidia.com/cuda-downloads to download and install CUDA."
    read -p "Press enter to continue"
fi

# Check for gcc installation
if ! command -v gcc &> /dev/null
then
    echo "gcc is not installed. Attempting to install..."
    
    # Detect the Linux distribution
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        OS=$DISTRIB_ID
    else
        OS=$(uname -s)
    fi

    # Install gcc based on the detected distribution
    case $OS in
        "Ubuntu"|"Debian")
            sudo apt-get update
            sudo apt-get install -y build-essential
            ;;
        "Fedora"|"CentOS"|"Red Hat Enterprise Linux")
            sudo dnf groupinstall "Development Tools"
            ;;
        "Arch Linux")
            sudo pacman -S base-devel
            ;;
        "openSUSE")
            sudo zypper install -t pattern devel_basis
            ;;
        *)
            echo "Unsupported distribution. Please install gcc manually."
            ;;
    esac

    # Check if gcc was successfully installed
    if command -v gcc &> /dev/null
    then
        echo "gcc has been successfully installed."
    else
        echo "Failed to install gcc. Please install it manually."
    fi
else
    echo "gcc is already installed."
fi

cd "$ORIGINAL_PATH"
echo $(pwd)

# Install Python and create environment
echo "---   creating environment"
"$LOLLMSENV_DIR/bin/lollmsenv" create-env lollms_env
echo "---   activating environment"
# Activate environment
source "$LOLLMSENV_DIR/envs/lollms_env/bin/activate"
echo "$ORIGINAL_PATH"
cd "$ORIGINAL_PATH"
echo "---   cloning lollmw_webui"

# Clone or update repository
if [ -d "lollms-webui" ]; then
    cd lollms-webui
    git pull
    git submodule update --init --recursive
    cd ..
else
    git clone --depth 1 --recurse-submodules "$REPO_URL"
    cd lollms-webui
    git submodule update --init --recursive
    cd ..
fi

# Install requirements
echo "--- Install requirements"
cd lollms-webui
"$LOLLMSENV_DIR/envs/lollms_env/bin/python" -m pip install -r requirements.txt
"$LOLLMSENV_DIR/envs/lollms_env/bin/python" -m pip install -e lollms_core
cd ..

# Create launcher scripts
echo '#!/bin/bash' > lollms.sh
echo 'source "$LOLLMSENV_DIR/envs/lollms_env/bin/activate"' >> lollms.sh
echo 'cd lollms-webui' >> lollms.sh
echo 'python app.py "$@"' >> lollms.sh
chmod +x lollms.sh

echo '#!/bin/bash' > lollms_terminal.sh
echo 'source "$LOLLMSENV_DIR/envs/lollms_env/bin/activate"' >> lollms_terminal.sh
echo 'cd lollms-webui' >> lollms_terminal.sh
echo 'bash' >> lollms_terminal.sh
chmod +x lollms_terminal.sh

cd lollms-webui

echo "--- current folder $(pwd)"
# Binding selection menu
echo "Select the default binding to be installed:"
echo "1) None (install the binding later)"
echo "2) Local binding - ollama"
echo "3) Local binding - python_llama_cpp"
echo "4) Local binding - bs_exllamav2"
echo "5) Remote binding - groq"
echo "6) Remote binding - open_router"
echo "7) Remote binding - open_ai"
echo "8) Remote binding - mistral_ai"
echo "9) Remote binding - gemini"
echo "10) Remote binding - vllm"
echo "11) Remote binding - xAI"
echo "12) Remote binding - elf"
echo "13) Remote binding - remote lollms"

read -p "Type the number of your choice and press Enter: " choice

# Binding installation logic
case $choice in
    1) ;;
    2) python zoos/bindings_zoo/ollama/__init__.py ;;
    3) python zoos/bindings_zoo/python_llama_cpp/__init__.py ;;
    4) python zoos/bindings_zoo/bs_exllamav2/__init__.py ;;
    5) python zoos/bindings_zoo/groq/__init__.py ;;
    6) python zoos/bindings_zoo/open_router/__init__.py ;;
    7) python zoos/bindings_zoo/open_ai/__init__.py ;;
    8) python zoos/bindings_zoo/mistral_ai/__init__.py ;;
    9) python zoos/bindings_zoo/gemini/__init__.py ;;
    10) python zoos/bindings_zoo/vllm/__init__.py ;;
    11) python zoos/bindings_zoo/xAI/__init__.py ;;
    12) python zoos/bindings_zoo/elf/__init__.py ;;
    13) python zoos/bindings_zoo/remote_lollms/__init__.py ;;
esac

echo "Installation complete."

# Restore the original path
cd "$ORIGINAL_PATH"
echo "Restored to original path: $(pwd)"

read -p "Press enter to exit"
