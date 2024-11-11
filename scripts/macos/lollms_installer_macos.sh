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

# Check if Homebrew is installed
if ! command -v brew &> /dev/null
then
    echo "Homebrew is not installed. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew is already installed."
fi

# Check if Git is installed
if ! command -v git &> /dev/null
then
    echo "Git is not installed. Installing Git using Homebrew..."
    brew install git
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
    curl -O https://github.com/ParisNeo/LollmsEnv/releases/download/V1.4.2/lollmsenv_installer.sh
    # Install LollmsEnv
    echo "--- Installing lollmsenv"
    bash lollmsenv_installer.sh --dir "$LOLLMSENV_DIR" -y
fi

# Check for Metal support (Apple's GPU framework)
echo "--- Checking for Metal support..."
if system_profiler SPDisplaysDataType | grep -q "Metal: Supported"
then
    echo "Metal is supported on this Mac."
    echo "For optimal performance with Metal, ensure you have the latest version of macOS and Xcode Command Line Tools."
else 
    echo "Metal support not detected. You may experience reduced performance for GPU-accelerated tasks."
fi

# Check for Xcode Command Line Tools (includes Clang)
if ! command -v clang &> /dev/null
then
    echo "Xcode Command Line Tools (including Clang) are not installed. Installing..."
    xcode-select --install
else
    echo "Xcode Command Line Tools (including Clang) are already installed."
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
