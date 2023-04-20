#!/usr/bin/bash

echo "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHH     .HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHH.     ,HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHH.##  HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHHH#.HHHHH/*,*,*,*,*,*,*,*,***,*,**#HHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHHHHH.*,,***,***,***,***,***,***,*******HHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHHH*,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,*,,,,,HHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHH.,,,***,***,***,***,***,***,***,***,***,***/HHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHH*,,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*HHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHH#,***,***,***,***,***,***,***,***,***,***,***,**HHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHH..HHH,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,*#HHHHHHHHHHHHHHHH"
echo "HHHHHHH,,,**,/H*,***,***,***,,,*,***,***,***,**,,,**,***,***,***H,,*,***HHHHHHHH"
echo "HHHHHH.*,,,*,,,,,*,*,*,***#HHHHH.,,*,*,*,*,**/HHHHH.,*,*,*,*,*,*,*,*****HHHHHHHH"
echo "HHHHHH.*,***,*,*,***,***,.HHHHHHH/**,***,****HHHHHHH.***,***,***,*******HHHHHHHH"
echo "HHHHHH.,,,,,,,,,,,,,,,,,,,.HHHHH.,,,,,,,,,,,,.HHHHHH,,,,,,,,,,,,,,,,,***HHHHHHHH"
echo "HHHHHH.,,,,,,/H,,,**,***,***,,,*,***,***,***,**,,,,*,***,***,***H***,***HHHHHHHH"
echo "HHHHHHH.,,,,*.H,,,,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,***H*,,,,/HHHHHHHHH"
echo "HHHHHHHHHHHHHHH*,***,***,**,,***,***,***,***,***,***,***,***,**.HHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHH,,,,,,,,*,,#H#,,,,,*,,,*,,,,,,,,*#H*,,,,,,,,,**HHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHH,,*,***,***,**/.HHHHHHHHHHHHH#*,,,*,***,***,*HHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHH,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*HHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHH**,***,***,***,***,***,***,***,***,***,***,*.HHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHH*,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,*HHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHH**,***,***,*******/..HHHHHHHHH.#/*,*,,,***,***HHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHH*,*,*,******#HHHHHHHHHHHHHHHHHHHHHHHHHHHH./**,,,.HHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHH.,,*,***.HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH.*#HHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHH/,,,*.HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHH,,#HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHH.HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
echo "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"


# Install git
echo -n "Checking for Git..."
if command -v git > /dev/null 2>&1; then
  echo "is installed"
else
  read -p "Git is not installed. Would you like to install Git? [Y/N] " choice
  if [ "$choice" = "Y" ] || [ "$choice" = "y" ]; then
    echo "Installing Git..."
    sudo apt update
    sudo apt install -y git
  else
    echo "Please install Git and try again."
    exit 1
  fi
fi

# Check if repository exists 
if [[ -d .git ]] ;then
echo Pulling latest changes 
git pull origin main
else
echo Cloning repository...
git init
git remote add origin https://github.com/nomic-ai/gpt4all-ui.git
git pull origin main

fi

# Download latest personalities
if ! test -d ./tmp/personalities; then
  git clone https://github.com/ParisNeo/GPT4All_Personalities.git ./tmp/personalities
fi
cp ./tmp/personalities/* ./personalities/

# Install Python 3.10 and pip
echo -n "Checking for python3.10..."
if command -v python3.10 > /dev/null 2>&1; then
  echo "is installed"
else
  read -p "Python3.10 is not installed. Would you like to install Python3.10? [Y/N] " choice
  if [ "$choice" = "Y" ] || [ "$choice" = "y" ]; then
    echo "Installing Python3.10..."
    sudo apt update
    sudo apt install -y python3.10 python3.10-venv
  else
    echo "Please install Python3.10 and try again."
    exit 1
  fi
fi

# Install venv module
echo -n "Checking for venv module..."
if python3.10 -m venv env > /dev/null 2>&1; then
  echo "is installed"
else
  read -p "venv module is not available. Would you like to install it? [Y/N] " choice
  if [ "$choice" = "Y" ] || [ "$choice" = "y" ]; then
    echo "Installing venv module..."
    sudo apt update
    sudo apt install -y python3.10-venv
  else
    echo "Please install venv module and try again."
    exit 1
  fi
fi

# Create a new virtual environment
echo -n "Creating virtual environment..."
python3.10 -m venv env
if [ $? -ne 0 ]; then
  echo "Failed to create virtual environment. Please check your Python installation and try again."
  exit 1
else
  echo "is created"
fi

# Activate the virtual environment
echo -n "Activating virtual environment..."
source env/bin/activate
echo "is active"

# Install the required packages
echo "Installing requirements..."
python3.10 -m pip install pip --upgrade
python3.10 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
  echo "Failed to install required packages. Please check your internet connection and try again."
  exit 1
fi

# Checking model

MODEL="./models/llama_cpp/gpt4all-lora-quantized-ggml.bin"
MODEL_URL="https://huggingface.co/ParisNeo/GPT4All/resolve/main/gpt4all-lora-quantized-ggml.bin"

if [ -f "$MODEL" ]; then
  echo "File $MODEL already exists. Skipping download."
  
else
  echo "File $MODEL does not exist."
  echo "What would you like to do?"
  select option in "Download" "Download using browser" "Skip"; do
    case $option in
      Download)
        if [ -x "$(command -v wget)" ]; then
          wget $MODEL_URL -P ./models/
        elif [ -x "$(command -v curl)" ]; then
          curl -O $MODEL_URL -o $MODEL
        else
          echo "Error: neither wget nor curl is installed. Please install one of them and try again."
          exit 1
        fi
        break
        ;;
      "Download using browser")
        if [ -x "$(command -v xdg-open)" ]; then
          xdg-open $MODEL_URL
        elif [ -x "$(command -v gnome-open)" ]; then
          gnome-open $MODEL_URL
        elif [ -x "$(command -v kde-open)" ]; then
          kde-open $MODEL_URL
        elif [ -x "$(command -v open)" ]; then
          open $MODEL_URL
        else
          echo "Error: could not detect a default browser. Please open the link in your web browser manually and press any key to continue."
          read -n 1 -s -r -p "Press any key to continue"
        fi
        break
        ;;
      Skip)
        echo "Skipping downloading $MODEL"
        
        break
        ;;
    esac
  done
fi

# Cleanup

if [ -d "./tmp" ]; then
  rm -rf "./tmp"
  echo "Cleaning tmp folder"
fi

# Launch the Python application
python app.py
