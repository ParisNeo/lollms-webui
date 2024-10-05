@echo off

echo "L🪶LLMS: Lord of Large Language and Multimodal Systems"
echo V13 Feather
echo -----------------
echo By ParisNeo
echo -----------------

REM Store the current path
set "ORIGINAL_PATH=%CD%"

cd /D "%~dp0"

echo %CD%

set LOLLMSENV_DIR=%CD%\installer_files\lollmsenv
set INSTALL_ENV_DIR=%CD%\installer_files\lollms_env
set REPO_URL=https://github.com/ParisNeo/lollms-webui.git

REM Download LollmsEnv installer
echo Downloading LollmsEnv installer...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/ParisNeo/LollmsEnv/releases/download/V1.2.8/lollmsenv_installer.bat' -OutFile 'lollmsenv_installer.bat'"

REM Install LollmsEnv
call lollmsenv_installer.bat --dir "%LOLLMSENV_DIR%" -y

REM Check for NVIDIA GPU and CUDA
echo Checking for NVIDIA GPU and CUDA...
nvidia-smi >nul 2>&1
if %errorlevel% equ 0 (
    echo NVIDIA GPU detected.
    echo Querying GPU information...
    
    REM Use a temporary file to store nvidia-smi output
    nvidia-smi --query-gpu=name,driver_version,memory.total,utilization.gpu,temperature.gpu --format=csv,noheader,nounits
    nvidia-smi --query-gpu=name,driver_version,memory.total,utilization.gpu,temperature.gpu --format=csv,noheader,nounits > gpu_info.txt
    
    REM Read from the temporary file
    for /f "tokens=1-5 delims=," %%a in (gpu_info.txt) do (
        set "GPU_NAME=%%a"
        set "DRIVER_VERSION=%%b"
        set "TOTAL_MEMORY=%%c"
        set "GPU_UTILIZATION=%%d"
        set "GPU_TEMPERATURE=%%e"
    )
    
    echo GPU Name: %GPU_NAME%
    echo Driver Version: %DRIVER_VERSION%
    echo Total Memory: %TOTAL_MEMORY% MiB
    echo GPU Utilization: %GPU_UTILIZATION% %%
    echo GPU Temperature: %GPU_TEMPERATURE% C
    
    echo Extracting CUDA version...
    for /f "tokens=* delims=" %%a in ('nvidia-smi ^| findstr "CUDA Version"') do (
        set "CUDA_LINE=%%a"
    )
    for /f "tokens=3 delims=:" %%a in ("%CUDA_LINE%") do (
        set "CUDA_VERSION=%%a"
    )
    set "CUDA_VERSION=%CUDA_VERSION:~1%"
    echo CUDA Version:%CUDA_VERSION%

    echo For optimal performance, ensure you have CUDA version 12.1 or higher.
    echo If you need to update, visit https://developer.nvidia.com/cuda-downloads
    
    REM Clean up temporary files
    del gpu_info.txt
    del cuda_version.txt
) else ( 
    echo No NVIDIA GPU detected or nvidia-smi is not available.
)


REM Ask user about CUDA installation
set /p INSTALL_CUDA="Do you want to install CUDA? (Only for NVIDIA GPUs if your version is lower than 12.1 or if it wasn't already installed, recommended for local AI) [Y/N]: "
if /i "%INSTALL_CUDA%"=="Y" (
    echo Please visit https://developer.nvidia.com/cuda-downloads to download and install CUDA.
    pause
)

REM Ask about Visual Studio Code installation
set /p INSTALL_VSCODE="Do you want to install Visual Studio Code? (Recommended for local AI development) [Y/N]: "
if /i "%INSTALL_VSCODE%"=="Y" (
    echo Please visit https://code.visualstudio.com/download to download and install Visual Studio Code.
    pause
)

echo %CD%

REM Install Python and create environment
echo activating lollmsenv
call "%LOLLMSENV_DIR%\activate.bat"
call "%LOLLMSENV_DIR%\bin\lollmsenv.bat" install-python 3.10.11
call "%LOLLMSENV_DIR%\bin\lollmsenv.bat" create-env lollms_env 3.10.11
pause
REM Activate environment
call "%LOLLMSENV_DIR%\bin\lollmsenv.bat" activate lollms_env

REM Clone or update repository
if exist lollms-webui\ (
    cd lollms-webui
    git pull
    git submodule update --init --recursive
    cd ..
) else (
    git clone --depth 1 --recurse-submodules %REPO_URL%
    cd lollms-webui
    git submodule update --init --recursive
    cd ..
)

REM Install requirements
cd lollms-webui
pip install -r requirements.txt
cd ..

REM Create launcher scripts
echo @echo off > ..\win_run.bat
echo call "%LOLLMSENV_DIR%\bin\lollmsenv.bat" activate lollms_env >> ..\lollms.bat
echo cd lollms-webui >> ..\lollms.bat
echo python app.py %%* >> ..\lollms.bat

echo @echo off > ..\win_conda_session.bat
echo call "%LOLLMSENV_DIR%\bin\lollmsenv.bat" activate lollms_env >> ..\lollms_cmd.bat
echo cd lollms-webui >> ..\lollms_cmd.bat
echo cmd /k >> ..\lollms_cmd.bat

REM Binding selection menu
echo Select the default binding to be installed:
echo 1) None (install the binding later)
echo 2) Local binding - ollama
echo 3) Local binding - python_llama_cpp
echo 4) Local binding - bs_exllamav2
echo 5) Remote binding - groq
echo 6) Remote binding - open_router
echo 7) Remote binding - open_ai
echo 8) Remote binding - mistral_ai
echo 9) Remote binding - gemini
echo 10) Remote binding - vllm
echo 11) Remote binding - xAI
echo 12) Remote binding - elf
echo 13) Remote binding - remote lollms

set /p choice="Type the number of your choice and press Enter: "

REM Binding installation logic
if "%choice%"=="1" goto :end
if "%choice%"=="2" call python zoos/bindings_zoo/ollama/__init__.py
if "%choice%"=="3" call python zoos/bindings_zoo/python_llama_cpp/__init__.py
if "%choice%"=="4" call python zoos/bindings_zoo/bs_exllamav2/__init__.py
if "%choice%"=="5" call python zoos/bindings_zoo/groq/__init__.py
if "%choice%"=="6" call python zoos/bindings_zoo/open_router/__init__.py
if "%choice%"=="7" call python zoos/bindings_zoo/open_ai/__init__.py
if "%choice%"=="8" call python zoos/bindings_zoo/mistral_ai/__init__.py
if "%choice%"=="9" call python zoos/bindings_zoo/gemini/__init__.py
if "%choice%"=="10" call python zoos/bindings_zoo/vllm/__init__.py
if "%choice%"=="11" call python zoos/bindings_zoo/xAI/__init__.py
if "%choice%"=="12" call python zoos/bindings_zoo/elf/__init__.py
if "%choice%"=="13" call python zoos/bindings_zoo/remote_lollms/__init__.py

:end
echo Installation complete.

REM Restore the original path
cd /D "%ORIGINAL_PATH%"
echo Restored to original path: %CD%

pause
