@echo off

echo HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHH     .HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHH.     ,HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHH.##  HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHHH#.HHHHH/*,*,*,*,*,*,*,*,***,*,**#HHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHHHHH.*,,***,***,***,***,***,***,*******HHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHHH*,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,*,,,,,HHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHH.,,,***,***,***,***,***,***,***,***,***,***/HHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHH*,,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*HHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHH#,***,***,***,***,***,***,***,***,***,***,***,**HHHHHHHHHHHHHHHHH
echo HHHHHHHHHH..HHH,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,*#HHHHHHHHHHHHHHHH
echo HHHHHHH,,,**,/H*,***,***,***,,,*,***,***,***,**,,,**,***,***,***H,,*,***HHHHHHHH
echo HHHHHH.*,,,*,,,,,*,*,*,***#HHHHH.,,*,*,*,*,**/HHHHH.,*,*,*,*,*,*,*,*****HHHHHHHH
echo HHHHHH.*,***,*,*,***,***,.HHHHHHH/**,***,****HHHHHHH.***,***,***,*******HHHHHHHH
echo HHHHHH.,,,,,,,,,,,,,,,,,,,.HHHHH.,,,,,,,,,,,,.HHHHHH,,,,,,,,,,,,,,,,,***HHHHHHHH
echo HHHHHH.,,,,,,/H,,,**,***,***,,,*,***,***,***,**,,,,*,***,***,***H***,***HHHHHHHH
echo HHHHHHH.,,,,*.H,,,,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,***H*,,,,/HHHHHHHHH
echo HHHHHHHHHHHHHHH*,***,***,**,,***,***,***,***,***,***,***,***,**.HHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHH,,,,,,,,*,,#H#,,,,,*,,,*,,,,,,,,*#H*,,,,,,,,,**HHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHH,,*,***,***,**/.HHHHHHHHHHHHH#*,,,*,***,***,*HHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHH,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*HHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHH**,***,***,***,***,***,***,***,***,***,***,*.HHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHH*,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,*HHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHH**,***,***,*******/..HHHHHHHHH.#/*,*,,,***,***HHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHH*,*,*,******#HHHHHHHHHHHHHHHHHHHHHHHHHHHH./**,,,.HHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHH.,,*,***.HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH.*#HHHHHHHHHHHH
echo HHHHHHHHHHHHHHH/,,,*.HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHH,,#HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHH.HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH




REM Check if Git is installed
echo "Checking for git..."
where git >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    goto GIT_CHECKED
) else (
    goto GIT_INSTALL
)
:GIT_FINISH

REM Check if Git is installed
:GIT_CHECKED
echo "Git is installed."
goto GIT_SKIP

:GIT_INSTALL
echo.
choice /C YN /M "Do you want to download and install Git?"
if errorlevel 2 goto GIT_CANCEL
if errorlevel 1 goto GIT_INSTALL_2

:GIT_INSTALL_2
echo "Git is not installed. Installing Git..."
powershell.exe -Command "Start-Process https://git-scm.com/download/win -Wait"
goto GIT_SKIP

:GIT_CANCEL
echo.
echo Git download cancelled.
echo Please install Git and try again.
pause
exit /b 1

:GIT_SKIP

REM Check if repository exists 
git rev-parse --is-inside-work-tree 
if errorlevel 1 goto :CLONE_REPO
if errorlevel = 0 goto :PULL_CHANGES
:PULL_CHANGES
echo Pulling latest changes 
git pull origin main
goto :GET_PERSONALITIES

:CLONE_REPO
echo Cloning repository...
git init
git remote add origin https://github.com/nomic-ai/gpt4all-ui.git
git fetch
git reset origin/main  
git checkout -t origin/main
git pull origin main
goto :GET_PERSONALITIES

:GET_PERSONALITIES
REM Download latest personalities
if not exist tmp\personalities git clone https://github.com/ParisNeo/GPT4All_Personalities.git tmp\personalities
copy tmp\personalities\* personalities
goto :CHECK_PYTHON_INSTALL

:CHECK_PYTHON_INSTALL
REM Check if Python is installed
set /p="Checking for python..." <nul
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    goto PYTHON_CHECKED
) else (
    goto PYTHON_INSTALL
)
:PYTHON_CHECKED
echo "Python is installed."
goto PYTHON_SKIP

:PYTHON_INSTALL
echo.
choice /C YN /M "Do you want to download and install python?"
if errorlevel 2 goto PYTHON_CANCEL
if errorlevel 1 goto PYTHON_INSTALL_2

:PYTHON_INSTALL_2
REM Download Python installer
if not exist "./tmp" mkdir "./tmp"
echo Downloading Python installer...
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe' -OutFile 'tmp/python.exe'"
REM Install Python
echo Installing Python...
tmp/python.exe /quiet /norestart

:PYTHON_CANCEL
echo Please install python and try again.
pause
exit /b 1

:PYTHON_SKIP

REM Check if pip is installed
set /p="Checking for pip..." <nul
python -m pip >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    goto PIP_CHECKED
) else (
    goto PIP_INSTALL
)
:PIP_CHECKED
echo "Pip is installed."
goto PIP_SKIP

:PIP_INSTALL
echo.
choice /C YN /M "Do you want to download and install pip?"
if errorlevel 2 goto PIP_CANCEL
if errorlevel 1 goto PIP_INSTALL_2

:PIP_INSTALL_2
REM Download get-pip.py
echo Downloading get-pip.py...
powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'tmp/get-pip.py'"
REM Install pip
echo Installing pip...
python tmp/get-pip.py

:PIP_CANCEL
echo Please install pip and try again.
pause
exit /b 1

:PIP_SKIP

REM Upgrading pip setuptools and wheel
echo Updating pip setuptools and wheel
python -m pip install --upgrade pip setuptools wheel

REM Check if pip is installed
set /p="Checking for virtual environment..." <nul
python -c "import venv" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    goto VENV_CHECKED
) else (
    goto VENV_INSTALL
)
:VENV_CHECKED
echo "Virtual environment is installed."
goto VENV_SKIP

:VENV_INSTALL
echo.
choice /C YN /M "Do you want to download and install venv?"
if errorlevel 2 goto VENV_CANCEL
if errorlevel 1 goto VENV_INSTALL_2

:VENV_INSTALL_2
REM Installinv venv
echo installing venv...
pip install virtualenv

:VENV_CANCEL
echo Please install venv and try again.
pause
exit /b 1

:VENV_SKIP

echo Checking virtual environment.
if exist ./env (
    echo Virtual environment already exists.
    goto VENV_CREATED
)

REM Create a new virtual environment
set /p="Creating virtual environment ..." <nul
python -m venv env >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    goto VENV_CREATED
) else (
    echo Failed to create virtual environment. Please check your Python installation and try again.
    pause
    exit /b 1
)
:VENV_CREATED


REM Activate the virtual environment
set /p="Activating virtual environment ..." <nul
call env\Scripts\activate.bat
echo OK
REM Install the required packages
echo Installing requirements ...
python -m pip install pip --upgrade
python -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Failed to install required packages. Please check your internet connection and try again.
    pause
    exit /b 1
)

echo Checking models...
if not exist \models (
    md \models
)

if not exist ./models/llama_cpp/gpt4all-lora-quantized-ggml.bin (
    echo.
    choice /C YNB /M "The default model file (gpt4all-lora-quantized-ggml.bin) does not exist. Do you want to download it? Press B to download it with a browser (faster)."
    if errorlevel 3 goto DOWNLOAD_WITH_BROWSER
    if errorlevel 2 goto DOWNLOAD_SKIP
    if errorlevel 1 goto MODEL_DOWNLOAD
) ELSE (
    echo Model already installed
    goto CONTINUE
)

:DOWNLOAD_WITH_BROWSER
start https://huggingface.co/ParisNeo/GPT4All/resolve/main/gpt4all-lora-quantized-ggml.bin
echo Link has been opened with the default web browser, make sure to save it into the models/llama_cpp folder before continuing. Press any key to continue...
pause
goto :CONTINUE

:MODEL_DOWNLOAD
echo.
echo Downloading latest model...
powershell -Command "Invoke-WebRequest -Uri 'https://huggingface.co/ParisNeo/GPT4All/resolve/main/gpt4all-lora-quantized-ggml.bin' -OutFile %clone_dir%'/models/llama_cpp/gpt4all-lora-quantized-ggml.bin'"
if errorlevel 1 (
    echo Failed to download model. Please check your internet connection.
    choice /C YN /M "Do you want to try downloading again?"
    if errorlevel 2 goto DOWNLOAD_SKIP
    if errorlevel 1 goto MODEL_DOWNLOAD
) else (
    echo Model successfully downloaded.
)
goto :CONTINUE

:DOWNLOAD_SKIP
echo.
echo Skipping download of model file...
goto :CONTINUE

:CONTINUE

:END
if exist "./tmp"  (
echo Cleaning tmp folder
rd /s /q "./tmp"
)

echo Virtual environment created and packages installed successfully.
echo Launching application...

REM Run the Python app

python app.py %*
set app_result=%errorlevel%

pause >nul
exit /b 0