#!/usr/bin/bash

# Install Python 3.10 and pip
echo -n "Checking for python3.10..."
if command -v python3.10 > /dev/null 2>&1; then
  echo "OK"
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
  echo "OK"
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
  echo "OK"
fi

# Activate the virtual environment
echo -n "Activating virtual environment..."
source env/bin/activate
echo "OK"

# Install the required packages
echo "Installing requirements..."
export DS_BUILD_OPS=0
export DS_BUILD_AIO=0
python3.10 -m pip install pip --upgrade
python3.10 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
  echo "Failed to install required packages. Please check your internet connection and try again."
  exit 1
fi

echo ""
echo "Downloading latest model..."
curl -o "models/gpt4all-lora-quantized-ggml.bin" "https://the-eye.eu/public/AI/models/nomic-ai/gpt4all/gpt4all-lora-quantized-ggml.bin"
if [ $? -ne 0 ]; then
    echo "Failed to download model. Please check your internet connection."
    read -p "Do you want to try downloading again? Press Y to download." yn
    case $yn in
        [Yy]* ) echo "Downloading latest model..."
                curl -o "models/gpt4all-lora-quantized-ggml.bin" "https://the-eye.eu/public/AI/models/nomic-ai/gpt4all/gpt4all-lora-quantized-ggml.bin";;
        * ) echo "Skipping download of model file...";;
    esac
else
    echo "Model successfully downloaded."
fi

echo ""
echo "In order to make a model work, it needs to go through the LLaMA tokenizer, this will fix errors with the model in run.bat. Do you want to convert the model?"
read -p "Press Y to convert or N to skip: " yn
case $yn in
    [Yy]* )
        echo ""
        echo "Select a model to convert:"
        count=0
        for f in models/*; do
            count=$((count+1))
            file[$count]=$f
            echo "[$count] $f"
        done

        Prompt user to choose a model to convert
        read -p "Enter the number of the model you want to convert: " modelNumber

        if [ -z "${file[modelNumber]}" ]; then
        echo ""
        echo "Invalid option. Restarting..."
        exit 1
        fi

        modelPath="${file[modelNumber]}"

        echo ""
        echo "You selected $modelPath"

        Ask user if they want to convert the model
        echo ""
        read -p "Do you want to convert the selected model to the new format? (Y/N)" choice

        if [ "$choice" == "N" ]; then
        echo ""
        echo "Model conversion cancelled. Skipping..."
        exit 0
        fi

        The output inside a code tag
        echo "The code has been converted successfully."
esac
# Convert the model
echo ""
echo "Converting the model to the new format..."
if [ ! -d "tmp/llama.cpp" ]; then
    git clone https://github.com/ggerganov/llama.cpp.git tmp/llama.cpp
    cd tmp\llama.cpp
    git checkout 0f07cacb05f49704d35a39aa27cfd4b419eb6f8d
    cd ..\..
fi
mv -f "${modelPath}" "${modelPath}.original"
python tmp/llama.cpp/migrate-ggml-2023-03-30-pr613.py "${modelPath}.original" "${modelPath}"
if [ $? -ne 0 ]; then
    echo ""
    echo "Error during model conversion. Restarting..."
    mv -f "${modelPath}.original" "${modelPath}"
    goto CONVERT_RESTART
else
    echo ""
    echo "The model file (${modelPath}) has been converted to the new format."
    goto END
fi

:CANCEL_CONVERSION
echo ""
echo "Conversion cancelled. Skipping..."
goto END

:END
echo ""
echo "Cleaning tmp folder"
rm -rf "./tmp"


echo "Virtual environment created and packages installed successfully."
echo "Every thing is setup. Just run run.sh"
exit 0
