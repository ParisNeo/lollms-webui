@echo off
set environment_path=%cd%/lollms-webui/env

echo \u001b[34m
echo "      ___       ___           ___       ___       ___           ___      "
echo "     /\__\     /\  \         /\__\     /\__\     /\__\         /\  \     "
echo "    /:/  /    /::\  \       /:/  /    /:/  /    /::|  |       /::\  \    "
echo "   /:/  /    /:/\:\  \     /:/  /    /:/  /    /:|:|  |      /:/\ \  \   "
echo "  /:/  /    /:/  \:\  \   /:/  /    /:/  /    /:/|:|__|__   _\:\~\ \  \  "
echo " /:/__/    /:/__/ \:\__\ /:/__/    /:/__/    /:/ |::::\__\ /\ \:\ \ \__\ "
echo " \:\  \    \:\  \ /:/  / \:\  \    \:\  \    \/__/~~/:/  / \:\ \:\ \/__/ "
echo "  \:\  \    \:\  /:/  /   \:\  \    \:\  \         /:/  /   \:\ \:\__\   "
echo "   \:\  \    \:\/:/  /     \:\  \    \:\  \       /:/  /     \:\/:/  /   "
echo "    \:\__\    \::/  /       \:\__\    \:\__\     /:/  /       \::/  /    "
echo "     \/__/     \/__/         \/__/     \/__/     \/__/         \/__/     "
echo By ParisNeo
echo \u001b[0m

echo Testing internet connection
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
        git pull 
    ) else (
        if exist lollms-webui (
            cd ./lollms-webui
        ) else (
            echo Cloning repository...
            git clone https://github.com/ParisNeo/lollms-webui.git ./lollms-webui
            cd ./lollms-webui
            echo Cloned successfully
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
        set /p choice="Conda is not installed. Would you like to install Conda? [Y/N]:"
        if /i "%choice%"=="Y" (
            echo Installing Conda...
            set "miniconda_installer_url=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
            set "miniconda_installer=miniconda_installer_filename.exe"
            rem Download the Miniconda installer using curl.
            curl -o "%miniconda_installer%" "%miniconda_installer_url%"            
            if exist "%miniconda_installer%" (
                echo Miniconda installer downloaded successfully.
                echo Installing Miniconda...
                echo.

                rem Run the Miniconda installer.
                "%miniconda_installer%" /InstallationType=JustMe /AddToPath=yes /RegisterPython=0 /S /D="%USERPROFILE%\Miniconda"

                if %errorlevel% equ 0 (
                    echo Miniconda has been installed successfully in "%USERPROFILE%\Miniconda".
                ) else (
                    echo Failed to install Miniconda.
                )

                rem Clean up the Miniconda installer file.
                del "%miniconda_installer%"

                rem Activate Miniconda.
                call "%USERPROFILE%\Miniconda\Scripts\activate"

            ) else (
                echo Failed to download the Miniconda installer.
                exit /b 1
            )
        )
    )
    echo Deactivating any activated environment
    conda deactivate

    echo checking %environment_path% existance

    rem Check the error level to determine if the file exists
    if not exist "%environment_path%" (
        REM Create a new Conda environment
        echo Creating Conda environment...
        conda create --prefix ./env python=3.10
        conda activate ./env
        pip install --upgrade pip setuptools wheel
        conda install -c conda-forge cudatoolkit-dev
    ) else (
        echo Environment already exists. Skipping environment creation.
        conda activate ./env
    )

    echo Activating environment
    conda activate ./env
    echo Conda environment is created
    REM Install the required packages
    echo Installing requirements using pip...
    pip install -r requirements.txt

    if %errorlevel% neq 0 (
        echo Failed to install required packages. Please check your internet connection and try again.
        exit /b 1
    )

    echo Cleanup
    REM Cleanup
    if exist "./tmp" (
        echo Cleaning tmp folder
        rmdir /s /q "./tmp"
        echo Done
    )
    echo Ready
    echo launching app
    REM Launch the Python application
    python app.py %*
    set app_result=%errorlevel%

    pause >nul
    exit /b 0

) else (
    REM Go to webui folder
    cd lollms-webui

    REM Activate environment
    conda activate ./env

    echo launching app
    REM Launch the Python application
    python app.py %*
    set app_result=%errorlevel%

    pause >nul
    exit /b 0
)


