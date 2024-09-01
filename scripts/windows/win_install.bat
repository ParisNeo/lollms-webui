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
echo V12
echo -----------------
echo By ParisNeo
echo -----------------

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

pause
cls

md 

@rem better isolation for virtual environment
SET "CONDA_SHLVL="
SET PYTHONNOUSERSITE=1
SET "PYTHONPATH="
SET "PYTHONHOME="
SET "TEMP=%cd%\installer_files\temp"
SET "TMP=%cd%\installer_files\temp"

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

@rem activate miniconda
call "%MINICONDA_DIR%\Scripts\activate.bat" || ( echo Miniconda hook not found. && goto end )


@rem create the installer env
if not exist "%INSTALL_ENV_DIR%" (
  echo Packages to install: %PACKAGES_TO_INSTALL%
  call conda create --no-shortcuts -y -k -p "%INSTALL_ENV_DIR%" %CHANNEL% %PACKAGES_TO_INSTALL% || ( echo. && echo Conda environment creation failed. && goto end )
)

@rem check if conda environment was actually created
if not exist "%INSTALL_ENV_DIR%\python.exe" ( echo. && echo Conda environment is empty. && goto end )

@rem activate installer env
call conda activate "%INSTALL_ENV_DIR%" || ( echo. && echo Conda environment activation failed. && goto end )

@rem install conda library
call conda install conda -y


@rem clone the repository
if exist lollms-webui\ (
  cd lollms-webui
  git pull
  git submodule update --init --recursive
  cd
  cd lollms_core 
  pip install -e .
  cd ..\..
) else (
  git clone --depth 1  --recurse-submodules https://github.com/ParisNeo/lollms-webui.git
  git submodule update --init --recursive
  cd lollms-webui\lollms_core
  pip install -e .
  cd ..\..
  cd utilities\pipmaster
  pip install -e .
  cd ..\..
)

pip install -r requirements.txt

@rem create launcher
if exist ..\win_run.bat (
    echo Win run found
) else (
  copy scripts\windows\win_run.bat ..\
)


if exist ..\win_conda_session.bat (
    echo win conda session script found
) else (
  copy scripts\windows\win_conda_session.bat ..\
)


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

echo.
set /p choice="Type the number of your choice and press Enter: "

if "%choice%"=="1" goto :none
if "%choice%"=="2" goto :ollama
if "%choice%"=="3" goto :python_llama_cpp
if "%choice%"=="4" goto :bs_exllamav2
if "%choice%"=="5" goto :groq
if "%choice%"=="6" goto :open_router
if "%choice%"=="7" goto :open_ai
if "%choice%"=="8" goto :mistral_ai
if "%choice%"=="9" goto :gemini
if "%choice%"=="10" goto :vllm
if "%choice%"=="11" goto :xAI
if "%choice%"=="12" goto :elf
if "%choice%"=="13" goto :remote_lollms


goto :end

:none
echo You selected None. No binding will be installed now.
goto :end

:ollama
call python zoos/bindings_zoo/ollama/__init__.py
goto :end

:python_llama_cpp
call python zoos/bindings_zoo/python_llama_cpp/__init__.py
goto :end

:bs_exllamav2
call python zoos/bindings_zoo/bs_exllamav2/__init__.py
goto :end

:groq
call python zoos/bindings_zoo/groq/__init__.py
goto :end

:open_router
call python zoos/bindings_zoo/open_router/__init__.py
goto :end

:open_ai
call python zoos/bindings_zoo/open_ai/__init__.py
goto :end

:mistral_ai
call python zoos/bindings_zoo/mistral_ai/__init__.py
goto :end

:gemini
call python zoos/bindings_zoo/gemini/__init__.py
goto :end

:vllm
call python zoos/bindings_zoo/vllm/__init__.py
goto :end

:xAI
call python zoos/bindings_zoo/xAI/__init__.py
goto :end


:elf
call python zoos/bindings_zoo/elf/__init__.py
goto :end

:remote_lollms
call python zoos/bindings_zoo/remote_lollms/__init__.py
goto :end


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

echo Installation complete.
:endend
pause
