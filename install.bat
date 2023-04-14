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

if not exist "./tmp" mkdir "./tmp"

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

echo Downloading latest model
if not exist models (
    md models
)

if not exist models/gpt4all-lora-quantized-ggml.bin (
    echo.
    choice /C YNB /M "The default model file (gpt4all-lora-quantized-ggml.bin) does not exist. Do you want to download it? Press B to download it with a browser (faster)."
    if errorlevel 3 goto DOWNLOAD_WITH_BROWSER
    if errorlevel 2 goto DOWNLOAD_SKIP
    if errorlevel 1 goto MODEL_DOWNLOAD
) ELSE (
    echo.
    choice /C YNB /M "The default model file (gpt4all-lora-quantized-ggml.bin) already exists. Do you want to replace it? Press B to download it with a browser (faster)."
    if errorlevel 3 goto DOWNLOAD_WITH_BROWSER
    if errorlevel 2 goto DOWNLOAD_SKIP
    if errorlevel 1 goto MODEL_DOWNLOAD
)

:DOWNLOAD_WITH_BROWSER
start https://the-eye.eu/public/AI/models/nomic-ai/gpt4all/gpt4all-lora-quantized-ggml.bin
echo Link has been opened with the default web browser, make sure to save it into the models folder before continuing. Press any key to continue...
pause
goto :CONTINUE

:MODEL_DOWNLOAD
echo.
echo Downloading latest model...
powershell -Command "Invoke-WebRequest -Uri 'https://the-eye.eu/public/AI/models/nomic-ai/gpt4all/gpt4all-lora-quantized-ggml.bin' -OutFile 'models/gpt4all-lora-quantized-ggml.bin'"
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

REM This code lists all files in the ./models folder and asks the user to choose one to convert.
REM If the user agrees, it converts using Python. If not, it skips. On conversion failure, it reverts to original model.
:CONVERT_RESTART
echo.
choice /C YN /M "In order to make a model work, it needs to go through the LLaMA tokenizer, this will fix errors with the model in run.bat. Do you want to convert the model?"
if errorlevel 2 goto CANCEL_CONVERSION
if errorlevel 1 goto CONVERT_START

:CONVERT_START
REM List all files in the models folder
setlocal EnableDelayedExpansion
set count=0
for %%a in (models\*.*) do (
    set /A count+=1
    set "file[!count!]=%%a"
    echo [!count!] %%a
)

REM Prompt user to choose a model to convert
set /P modelNumber="Enter the number of the model you want to convert: "

if not defined file[%modelNumber%] (
    echo.
    echo Invalid option. Restarting...
    goto CONVERT_RESTART
)

set "modelPath=!file[%modelNumber%]!"

echo.
echo You selected !modelPath!
REM Ask user if they want to convert the model
echo.
choice /C YN /M "Do you want to convert the selected model to the new format?"
if errorlevel 2 (
    echo.
    echo Model conversion cancelled. Skipping...
    goto END
)
REM Convert the model
echo.
echo Converting the model to the new format...
if not exist tmp\llama.cpp git clone https://github.com/ggerganov/llama.cpp.git tmp\llama.cpp
cd tmp\llama.cpp
git checkout 0f07cacb05f49704d35a39aa27cfd4b419eb6f8d
cd ..\..
move /y "!modelPath!" "!modelPath!.original"
python tmp\llama.cpp\migrate-ggml-2023-03-30-pr613.py "!modelPath!.original" "!modelPath!"
if %errorlevel% neq 0 (
    goto ERROR_CONVERSION
) else (
    goto SUCCESSFUL_CONVERSION
)

:ERROR_CONVERSION
echo.
echo Error during model conversion. Restarting...
move /y "!modelPath!.original" "!modelPath!"
goto CONVERT_RESTART

:SUCCESSFUL_CONVERSION
echo.
echo The model file (!modelPath!) has been converted to the new format.
goto END

:CANCEL_CONVERSION
echo.
echo Conversion cancelled. Skipping...
goto END

:END

echo Cleaning tmp folder
rd /s /q "./tmp"

echo Virtual environment created and packages installed successfully.
echo Every thing is setup. Just run run.bat 
pause
exit /b 0
