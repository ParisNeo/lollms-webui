@echo off

echo "L🌟LLMS: Lord of Large Language and Multimodal Systems"
echo V14 SaÏf
echo -----------------
echo By ParisNeo
echo -----------------

REM Store the current path
set "ORIGINAL_PATH=%CD%"

cd /D "%~dp0"

echo %CD%

REM Check if Git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo Git is not installed. Downloading and installing Git...
    
    REM Download Git for Windows
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.37.1.windows.1/Git-2.37.1-64-bit.exe' -OutFile 'GitInstaller.exe'"
    
    REM Install Git silently
    start /wait GitInstaller.exe /VERYSILENT /NORESTART
    
    REM Clean up the installer
    del GitInstaller.exe
    
    echo Git has been installed.
) else (
    echo Git is already installed.
)

set LOLLMSENV_DIR=%CD%\lollmsenv
set REPO_URL=https://github.com/ParisNeo/lollms-webui.git

set USE_MASTER=0
if "%1"=="--use-master" set USE_MASTER=1

if %USE_MASTER%==1 (
    echo --- Using current master repo for LollmsEnv...
    git clone https://github.com/ParisNeo/LollmsEnv.git "%LOLLMSENV_DIR%"
    cd "%LOLLMSENV_DIR%"
    call install.bat --dir "%LOLLMSENV_DIR%" -y
    cd ..
) else (
    REM Download LollmsEnv installer
    echo Downloading LollmsEnv installer...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/ParisNeo/LollmsEnv/releases/download/V1.4.2/lollmsenv_installer.bat' -OutFile 'lollmsenv_installer.bat'"
    REM Install LollmsEnv
    echo --- Installing lollmsenv
    call lollmsenv_installer.bat --dir "%LOLLMSENV_DIR%" -y
)

REM Check for NVIDIA GPU and CUDA
echo --- Checking for NVIDIA GPU and CUDA...
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

cd %ORIGINAL_PATH%
echo %CD%

REM Install Python and create environment
echo ---   creating environment
call "%LOLLMSENV_DIR%\bin\lollmsenv.bat" create-env lollms_env
echo ---   activating environment
REM Activate environment
call "%LOLLMSENV_DIR%\envs\lollms_env\Scripts\activate.bat" 
echo %ORIGINAL_PATH%
cd "%ORIGINAL_PATH%"
echo ---   cloning lollmw_webui

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
echo --- Install requirements
cd lollms-webui
call "%LOLLMSENV_DIR%\envs\lollms_env\Scripts\python.exe" -m pip install -r requirements.txt
call "%LOLLMSENV_DIR%\envs\lollms_env\Scripts\python.exe" -m pip install -e lollms_core
cd ..

REM Create launcher scripts
echo @echo off > lollms.bat
echo call ".\lollmsenv\envs\lollms_env\Scripts\activate.bat" >> lollms.bat
echo cd lollms-webui >> lollms.bat
echo python app.py %%* >> lollms.bat
echo pause >> lollms.bat

echo @echo off > lollms_cmd.bat
echo call ".\lollmsenv\envs\lollms_env\Scripts\activate.bat" >> lollms_cmd.bat
echo cd lollms-webui >> lollms_cmd.bat
echo cmd /k >> lollms_cmd.bat

cd lollms-webui

echo --- current folder !cd!
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
