@echo off
setlocal EnableDelayedExpansion
echo Starting Lollms WebUI Installation Script
python --version 1>nul 2>&1
if errorlevel 1 (
    echo Python is not found in your PATH. Please install Python https://www.python.org/downloads/.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    goto :eof
) else (
    echo Found python version : 
    python --version
)


:: Get the directory where this script is located
set "SCRIPT_DIR=%cd%"
set "PYTHON_EXECUTABLE=python"

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python Virtual Environment in "%SCRIPT_DIR%\venv"...
    %PYTHON_EXECUTABLE% -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Please check your Python installation.
        pause
        goto :eof
    )
    echo Virtual environment created.
) else (
    echo Virtual environment "venv" already exists.
)

echo Activating virtual environment...
call "%SCRIPT_DIR%\venv\Scripts\activate.bat"
if errorlevel 1 (
    echo Failed to activate virtual environment.
    pause
    goto :eof
)

echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
if errorlevel 1 (
    echo Failed to upgrade pip.
    pip install --upgrade pip
    if errorlevel 1 (
        echo Pip upgrade still failed. Please check your internet connection and pip installation.
        pause
        goto :eof
    )
)

:: Install requirements for lollms_webui (if a root requirements.txt exists)
if exist "requirements.txt" (
    echo Installing Python Dependencies from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies from requirements.txt. Please check the file and your internet connection.
        pause
        goto :eof
    )
) else (
    echo No root requirements.txt found. Skipping this step.
    echo (Dependencies for lollms-core will be handled next if defined in its setup.py)
)

:: Install lollms_core
if exist "lollms_core\setup.py" (
    echo Installing lollms-core package from subfolder...
    pip install -e ./lollms_core
    if errorlevel 1 (
        echo Failed to install lollms-core. Please check the lollms_core subfolder and its setup.py.
        pause
        goto :eof
    )
    echo lollms-core installed successfully.
) else (
    echo Warning: lollms_core\setup.py not found. Cannot install lollms-core.
    echo The application might not work correctly.
    pause
)

echo.
echo Configuring Lollms WebUI Paths...

:: Determine lollms_path (absolute path to lollms_core/lollms)
set "lollms_path_val=%SCRIPT_DIR%\lollms_core\lollms"
:: Normalize path for YAML (replace backslashes with forward slashes)
set "lollms_path_val_yaml=!lollms_path_val:\=/!"

:: Prompt for lollms_personal_path
set "default_personal_path=%SCRIPT_DIR%\personal_data"
set "prompt_text=Enter Lollms personal data path [%default_personal_path%]: "
call set /p personal_data_input=%%prompt_text%%
if "!personal_data_input!"=="" (
    set "lollms_personal_path_val=!default_personal_path!"
) else (
    set "lollms_personal_path_val=!personal_data_input!"
)

:: Normalize path for YAML
set "lollms_personal_path_val_yaml=!lollms_personal_path_val:\=/!"

:: Create personal_data directory if it doesn't exist
if not exist "!lollms_personal_path_val!" (
    echo Creating personal data directory: !lollms_personal_path_val!
    mkdir "!lollms_personal_path_val!"
    if errorlevel 1 (
        echo Failed to create personal data directory. Please check permissions.
        pause
    )
)

:: Create global_paths_cfg.yaml
echo Writing configuration to global_paths_cfg.yaml...
(
    echo lollms_path: "!lollms_path_val_yaml!"
    echo lollms_personal_path: "!lollms_personal_path_val_yaml!"
) > "%SCRIPT_DIR%\global_paths_cfg.yaml"

if exist "%SCRIPT_DIR%\global_paths_cfg.yaml" (
    echo Configuration saved to global_paths_cfg.yaml
) else (
    echo Failed to write global_paths_cfg.yaml.
    pause
)

call python installer.py

echo.
echo Lollms WebUI Installation and Setup Complete.
echo.
echo To launch the application:
echo 1. Ensure you are in the project directory: cd /path/to/lollms-webui
echo 2. Activate the virtual environment (if not already active in your current terminal):
echo    call venv\Scripts\activate.bat
echo 3. Run the application using its main script, for example:
echo    python app.py 
echo    (Or use the provided run.bat if available in the project)
echo.
echo If a run.bat is provided with Lollms WebUI, you can simply execute:
echo    run.bat
echo.

endlocal
pause
goto :eof

