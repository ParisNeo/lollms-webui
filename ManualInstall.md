# LoLLMS WebUI Cross-Platform Installation Guide

## Introduction

LoLLMS (Lord of Large Language and Multimodal Systems) is a powerful tool for working with large language models. This guide will walk you through the installation process for the LoLLMS WebUI on Windows, macOS, and Linux, including the installation of Python 3.11.

## Prerequisites

Before you begin, ensure you have:

- Internet connection
- Administrator/sudo privileges on your system

## Installation Steps

### 1. Install Git

#### Windows
- Download and install Git from https://git-scm.com/download/win

#### macOS
- Install Homebrew if not already installed:
  ```
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```
- Install Git:
  ```
  brew install git
  ```

#### Linux
- Use your distribution's package manager. For example, on Ubuntu:
  ```
  sudo apt-get update
  sudo apt-get install git
  ```

### 2. Install Python 3.11

#### Windows
1. Download the Python 3.11 installer from https://www.python.org/downloads/release/python-3110/
2. Run the installer
3. Check "Add Python 3.11 to PATH"
4. Click "Install Now"

#### macOS
1. Install Homebrew if not already installed (see Git installation step)
2. Install Python 3.11:
   ```
   brew install python@3.11
   ```
3. Add Python 3.11 to your PATH:
   ```
   echo 'export PATH="/usr/local/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

#### Linux (Ubuntu/Debian)
1. Add the deadsnakes PPA:
   ```
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt-get update
   ```
2. Install Python 3.11:
   ```
   sudo apt-get install python3.11 python3.11-venv python3.11-dev
   ```

### 3. Clone the LoLLMS WebUI Repository

Open a terminal (Command Prompt on Windows) and run:

```
git clone --depth 1 --recurse-submodules https://github.com/ParisNeo/lollms-webui.git
cd lollms-webui
git submodule update --init --recursive
```

### 4. Create and Activate a Virtual Environment

#### Windows
```
python -m venv lollms_env
lollms_env\Scripts\activate
```

#### macOS and Linux
```
python -m venv lollms_env
source lollms_env/bin/activate
```

### 5. Install Requirements

With the virtual environment activated, run:

```
pip install --upgrade pip
pip install -r requirements.txt
pip install -e lollms_core
```

### 6. Select and Install a Binding

Choose a binding based on your needs. Here are some options:

- Local bindings: ollama, python_llama_cpp, bs_exllamav2
- Remote bindings: groq, open_router, open_ai, mistral_ai, gemini, vllm, xAI, elf, remote_lollms

To install a binding, run:
```
python zoos/bindings_zoo/<binding_name>/__init__.py
```
Replace `<binding_name>` with your chosen binding.

### 7. Create Launcher Scripts

#### Windows
Create `lollms.bat` in the LoLLMS directory:
```batch
@echo off
call lollms_env\Scripts\activate
cd lollms-webui
python app.py %*
pause
```

#### macOS and Linux
Create `lollms.sh` in the LoLLMS directory:
```bash
#!/bin/bash
source lollms_env/bin/activate
cd lollms-webui
python app.py "$@"
```
Make it executable:
```
chmod +x lollms.sh
```

## Optional Steps

### Install CUDA (for NVIDIA GPUs)

If you have an NVIDIA GPU and want to use it for local AI:

#### Windows
- Download and install CUDA from https://developer.nvidia.com/cuda-downloads

#### macOS
- CUDA is not supported on macOS with recent NVIDIA GPUs.

#### Linux
- Follow the CUDA installation guide for your specific Linux distribution from https://developer.nvidia.com/cuda-downloads

### Install Visual Studio Code

For local AI development, you may want to install Visual Studio Code:

- Download and install from: https://code.visualstudio.com/download

## Running LoLLMS WebUI

To start the LoLLMS WebUI:

#### Windows
Run the `lollms.bat` file.

#### macOS and Linux
Run the `lollms.sh` script:
```
./lollms.sh
```

## Troubleshooting

If you encounter any issues during installation or running the WebUI, please check the following:

1. Ensure Python 3.11 is correctly installed:
   ```
   python3.11 --version
   ```
2. Verify that your Python environment is activated before running any commands.
3. Check that all required packages are installed correctly.
4. Make sure you have selected and installed a compatible binding.
5. For platform-specific issues, consult the documentation for your operating system.

For further assistance, please refer to the official LoLLMS documentation or seek help in the project's support channels.
