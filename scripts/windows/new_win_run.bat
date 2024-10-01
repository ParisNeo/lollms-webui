@echo off
@echo Starting LOLLMS Web UI...
echo "Lollms feather"
echo By ParisNeo

cd /D "%~dp0"

@rem better isolation for virtual environment
SET PYTHONNOUSERSITE=1
SET "PYTHONPATH="
SET "PYTHONHOME="
SET "TEMP=%cd%\installer_files\temp"
SET "TMP=%cd%\installer_files\temp"

@rem workaround for broken Windows installs
set PATH=%PATH%;%SystemRoot%\system32

set INSTALL_ENV_DIR=%cd%\installer_files\lollms_env
set LOLLMSENV_DIR=%cd%\installer_files\lollmsenv

if not exist "%LOLLMSENV_DIR%\bin\lollmsenv.bat" (
    echo LollmsEnv not found. Installing LollmsEnv...
    call lollmsenv_install.bat --dir "%LOLLMSENV_DIR%"
)

call "%LOLLMSENV_DIR%\bin\lollmsenv.bat" install-python 3.10.11
call "%LOLLMSENV_DIR%\bin\lollmsenv.bat" create-env lollms_env 3.10.11

@rem Install CUDA 12.4
if not exist "%INSTALL_ENV_DIR%\cuda" (
    echo Installing CUDA 12.4...
    powershell -Command "Invoke-WebRequest -Uri 'https://developer.download.nvidia.com/compute/cuda/12.4.0/local_installers/cuda_12.4.0_windows.exe' -OutFile 'cuda_installer.exe'"
    cuda_installer.exe -s
    move C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4 "%INSTALL_ENV_DIR%\cuda"
    del cuda_installer.exe
)

@rem set CUDA path
set "CUDA_PATH=%INSTALL_ENV_DIR%\cuda"
set "PATH=%CUDA_PATH%\bin;%PATH%"

call "%LOLLMSENV_DIR%\bin\lollmsenv.bat" activate lollms_env
cd lollms-webui

call python app.py %*

:end
pause