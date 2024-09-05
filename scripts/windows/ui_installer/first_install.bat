@echo off

@rem This script will install miniconda and git with all dependencies for this project
@rem This enables a user to install this project without manually installing conda and git.

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
echo V8.5 (alpha)
echo -----------------
echo By ParisNeo
echo -----------------
cd

@rem workaround for broken Windows installs
set PATH=%PATH%;%SystemRoot%\system32

cd /D "%~dp0"

echo "%cd%"| findstr /C:" " >nul && call :PrintBigMessage "This script relies on Miniconda which can not be silently installed under a path with spaces. Please put it in a path without spaces and try again" && goto failed
call :PrintBigMessage "WARNING: This script relies on Miniconda which will fail to install if the path is too long."
set "SPCHARMESSAGE="WARNING: Special characters were detected in the installation path!" "         This can cause the installation to fail!""
echo "%CD%"| findstr /R /C:"[!#\$%&()\*+,;<=>?@\[\]\^`{|}~]" >nul && (
  call :PrintBigMessage %SPCHARMESSAGE%
)
set SPCHARMESSAGE=

cls

@rem better isolation for virtual environment
SET "CONDA_SHLVL="
SET PYTHONNOUSERSITE=1
SET "PYTHONPATH="
SET "PYTHONHOME="
SET "TEMP=%cd%\installer_files\temp"
SET "TMP=%cd%\installer_files\temp"

IF EXIST "installer_files" (
    echo Removing folder: installer_files. Please wait ...
    RMDIR /S /Q "installer_files"
)

IF EXIST "lollms-webui" (
    echo Removing folder: lollms-webui. Please wait ...
    RMDIR /S /Q "lollms-webui"
)

set MINICONDA_DIR=%cd%\installer_files\miniconda3
set INSTALL_ENV_DIR=%cd%\installer_files\lollms_env
set MINICONDA_DOWNLOAD_URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe
set REPO_URL=https://github.com/ParisNeo/lollms-webui.git

set "PACKAGES_TO_INSTALL=python=3.11 git pip"

if not exist "%MINICONDA_DIR%\Scripts\conda.exe" (
  @rem download miniconda
  echo Downloading Miniconda installer from %MINICONDA_DOWNLOAD_URL%
  call curl -LO "%MINICONDA_DOWNLOAD_URL%"

  @rem install miniconda
  echo. && echo Installing Miniconda To "%MINICONDA_DIR%" && echo Please Wait... && echo.
  start "" /W /D "%cd%" "Miniconda3-latest-Windows-x86_64.exe" /InstallationType=JustMe /NoShortcuts=1 /AddToPath=0 /RegisterPython=0 /NoRegistry=1 /S /D=%MINICONDA_DIR% || ( echo. && echo Miniconda installer not found. && goto failed )
  del /q "Miniconda3-latest-Windows-x86_64.exe"
  if not exist "%MINICONDA_DIR%\Scripts\activate.bat" ( echo. && echo Miniconda install failed. && goto end )
)

echo Activating conda environment

@rem activate miniconda
call "%MINICONDA_DIR%\Scripts\activate.bat" || ( echo Miniconda hook not found. && goto end )

echo Creating new environment

@rem create the installer env
if not exist "%INSTALL_ENV_DIR%" (
  echo Packages to install: %PACKAGES_TO_INSTALL%
  call conda create --no-shortcuts -y -k -p "%INSTALL_ENV_DIR%" %CHANNEL% %PACKAGES_TO_INSTALL% || ( echo. && echo Conda environment creation failed. && goto end )
)

@rem check if conda environment was actually created
if not exist "%INSTALL_ENV_DIR%\python.exe" ( echo. && echo Conda environment is empty. && goto end )

@rem activate installer env
call conda activate "%INSTALL_ENV_DIR%" || ( echo. && echo Conda environment activation failed. && goto end )

echo "Cloning lollms-webui"
git clone --depth 1  --recurse-submodules https://github.com/ParisNeo/lollms-webui.git
git submodule update --init --recursive
cd lollms-webui\lollms_core
pip install -e .
cd ..

pip install -r requirements.txt

@rem create launcher
if exist ..\win_run.bat (
    echo Win run found
) else (
  copy scripts\windows\win_run.bat ..\
)

if exist ..\win_update.bat (
    echo Win update found
) else (
  copy scripts\windows\win_update.bat ..\
)

if exist ..\win_conda_session.bat (
    echo win conda session script found
) else (
  copy scripts\windows\win_conda_session.bat ..\
)

if exist ..\win_update_models.bat (
    echo Win update models found
) else (
  copy scripts\windows\win_update_models.bat ..\
)

setlocal enabledelayedexpansion

endlocal

goto end

:PrintBigMessage
echo. && echo.
echo *******************************************************************
for %%M in (%*) do echo * %%~M
echo *******************************************************************
echo. && echo.
exit /b
goto end

:failed
echo Install failed
goto endend

:end

echo Creating a bin dir (required for llamacpp binding)
md ../installer_files/lollms_env/bin

echo Preparing lollms ...
if exist ..\personal_data (
    echo Personal data found
) else (
  md ..\personal_data
)
echo lollms_path: lollms_core\lollms > global_paths_cfg.yaml
echo lollms_personal_path: ..\personal_data >> global_paths_cfg.yaml

set option=%1

if "%option%"=="--elf" (
    echo Installing elf binding
    call python zoos/bindings_zoo/elf/__init__.py
) else if "%option%"=="--openrouter" (
    echo Installing open router binding
    call python zoos/bindings_zoo/open_router/__init__.py
) else if "%option%"=="--openai" (
    echo Installing open ai binding
    call python zoos/bindings_zoo/open_ai/__init__.py
) else if "%option%"=="--groq" (
    echo Installing groq binding
    call python zoos/bindings_zoo/groq/__init__.py
) else if "%option%"=="--mistralai" (
    echo Installing mistral ai binding
    call python zoos/bindings_zoo/mistral_ai/__init__.py
) else if "%option%"=="--ollama" (
    echo Installing ollama binding
    call python zoos/bindings_zoo/ollama/__init__.py
) else if "%option%"=="--vllm" (
    echo Installing vllm binding
    call python zoos/bindings_zoo/elf/__init__.py
) else if "%option%"=="--litellm" (
    echo Installing litellm binding
    call python zoos/bindings_zoo/litellm/__init__.py
) else if "%option%"=="--exllamav2" (
    echo Installing exllamav2 binding
    call python zoos/bindings_zoo/bs_exllamav2/__init__.py
) else if "%option%"=="--python_llama_cpp" (
    echo Installing python_llama_cpp binding
    call python zoos/bindings_zoo/python_llama_cpp/__init__.py
) else if "%option%"=="--huggingface" (
    echo Installing huggingface binding
    call python zoos/bindings_zoo/huggingface/__init__.py
) else if "%option%"=="--remote_lollms" (
    echo Installing remote_lollms binding
    call python zoos/bindings_zoo/remote_lollms/__init__.py
) else if "%option%"=="--xAI" (
    echo Installing xAI binding
    call python zoos/bindings_zoo/xAI/__init__.py
) else if "%option%"=="--gemini" (
    echo Installing gemini binding
    call python zoos/bindings_zoo/gemini/__init__.py
) else (
    echo No valid option selected
)

@rem cd scripts\python\lollms_installer
@rem call python main.py
@rem cd ..
echo Installation complete.
:endend

