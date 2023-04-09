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

REM Check if Python is installed
set /p="Checking for python..." <nul
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    set /p choice=Python is not installed. Would you like to install Python? [Y/N] 
    if /i ".choice." equ "Y" (
        REM Download Python installer
        echo Downloading Python installer...
        powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe' -OutFile 'tmp/python.exe'"
        REM Install Python
        echo Installing Python...
        tmp/python.exe /quiet /norestart
    ) else (
        echo Please install Python and try again.
        pause
        exit /b 1
    )
) else (
    echo OK
)


REM Check if pip is installed
set /p="Checking for pip..." <nul
python -m pip >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    set /p choice=Pip is not installed. Would you like to install pip? [Y/N]
    if /i ".choice." equ "Y" (
        REM Download get-pip.py
        echo Downloading get-pip.py...
        powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'tmp/get-pip.py'"
        REM Install pip
        echo Installing pip...
        python tmp/get-pip.py
    ) else (
        echo Please install pip and try again.
        pause
        exit /b 1
    )
) else (
    echo OK
)

REM Check if venv module is available
set /p="Checking for venv..." <nul
python -c "import venv" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    set /p choice=venv module is not available. Would you like to upgrade Python to the latest version? [Y/N]
    if /i ".choice." equ "Y" (
        REM Upgrade Python
        echo Upgrading Python...
        python -m pip install --upgrade pip setuptools wheel
        python -m pip install --upgrade --user python
    ) else (
        echo Please upgrade your Python installation and try again.
        pause
        exit /b 1
    )
) else (
    echo OK
)

REM Create a new virtual environment
set /p="Creating virtual environment ..." <nul
python -m venv env
if %errorlevel% neq 0 (
    echo Failed to create virtual environment. Please check your Python installation and try again.
    pause
    exit /b 1
) else (
    echo OK
)

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

REM Install Git
echo.
choice /C YN /M "Do you want to download and install Git?"
if errorlevel 2 goto GIT_CANCEL
if errorlevel 1 goto GIT_CHECK

:GIT_CANCEL
echo Git download cancelled.
goto GIT_FINISH

:GIT_CHECK
REM Install Git
echo "Checking for git..."
where git >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo "Git is installed."
) else (
    echo "Git is not installed. Installing Git..."
    powershell.exe -Command "Start-Process https://git-scm.com/download/win -Wait"
)
:GIT_FINISH

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
