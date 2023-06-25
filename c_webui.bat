
echo \u001b[34m
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
echo \u001b[0m
@echo off

ping -n 1 google.com >nul
if %errorlevel% equ 0 (
    echo Internet Connection working fine
    
    REM Install Git
    echo Checking for Git...
    where git >nul 2>nul
    if %errorlevel% equ 0 (
        echo Git is installed
    ) else (
        set /p choice=Git is not installed. Would you like to install Git? [Y/N]
        if /i "%choice%"=="Y" (
            echo Installing Git...
            REM Replace the following two lines with appropriate Git installation commands for Windows
            echo Please install Git and try again.
            exit /b 1
        )
    )
    
    REM Check if repository exists
    if exist .git (
        echo Pulling latest changes
        git pull origin main
    ) else (
        if exist lollms-webui (
            cd lollms-webui
        ) else (
            echo Cloning repository...
            git clone https://github.com/ParisNeo/lollms-webui.git ./lollms-webui
            cd lollms-webui
        )
    )
    echo Pulling latest version...
    git pull

    REM Install Conda
    echo Checking for Conda...
    where conda >nul 2>nul
    if %errorlevel% equ 0 (
        echo Conda is installed
    ) else (
        set /p choice=Conda is not installed. Would you like to install Conda? [Y/N]
        if /i "%choice%"=="Y" (
            echo Installing Conda...
            REM Replace the following lines with appropriate Conda installation commands for Windows
            echo Please install Conda and try again.
            exit /b 1
        )
    )

    REM Create a new Conda environment
    echo Creating Conda environment...
    conda create --prefix ./env python=3.10
    conda activate ./env
    echo Conda environment is created

    REM Install the required packages
    echo Installing requirements...
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt

    if %errorlevel% neq 0 (
        echo Failed to install required packages. Please check your internet connection and try again.
        exit /b 1
    )

    REM Cleanup
    if exist "./tmp" (
        rmdir /s /q "./tmp"
        echo Cleaning tmp folder
    )

)
REM Launch the Python application
python app.py
