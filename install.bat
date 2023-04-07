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
    set /p choice=Pip is not installed. Would you like to install pip? [Y/N]
    if /i ".choice." equ "Y" (
        REM Download get-pip.py
        echo Downloading get-pip.py...
        powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'tmp/get-pip.py'"
        REM Install pip
        echo Installing pip...
        python tmp/get-pip.py
    ) else .
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
IF NOT EXIST models (
    md models
)

IF NOT EXIST models/gpt4all-lora-quantized-ggml.bin (
    powershell -Command "Invoke-WebRequest -Uri 'https://the-eye.eu/public/AI/models/nomic-ai/gpt4all/gpt4all-lora-quantized-ggml.bin' -OutFile 'models/gpt4all-lora-quantized-ggml.bin'"
) ELSE (
    :PROMPT
    echo.
    set /p choice="The model file already exists. Do you want to override it? (y/n) "
    if /i {%choice%}=={y} (
        powershell -Command "Invoke-WebRequest -Uri 'https://the-eye.eu/public/AI/models/nomic-ai/gpt4all/gpt4all-lora-quantized-ggml.bin' -OutFile 'models/gpt4all-lora-quantized-ggml.bin'" && goto :CONTINUE
    ) else if /i {%choice%}=={n} (
        goto :CONTINUE
    ) else (
        echo.
        echo Invalid input. Please enter 'y' or 'n'.
        goto :PROMPT
    )
)
:CONTINUE

echo Cleaning tmp folder
rd /s /q "./tmp"

echo Virtual environment created and packages installed successfully.
echo Every thing is setup. Just run run.bat 
pause
exit /b 0
