@echo off

echo "LoLLMS: Lord of Large Language and Multimodal Systems"
echo V13 Feather
echo -----------------
echo By ParisNeo
echo -----------------

cd /D "%~dp0"

echo "%cd%"| findstr /C:" " >nul && call :PrintBigMessage "This script cannot be run from a path with spaces. Please move it to a path without spaces and try again." && goto failed

set "SPCHARMESSAGE="WARNING: Special characters were detected in the installation path!" "         This can cause the installation to fail!""
echo "%CD%"| findstr /R /C:"[!#\$%&()\*+,;<=>?@\[\]\^`{|}~]" >nul && (
  call :PrintBigMessage %SPCHARMESSAGE%
)
set SPCHARMESSAGE=

pause
cls

SET "TEMP=%cd%\installer_files\temp"
SET "TMP=%cd%\installer_files\temp"

set LOLLMSENV_DIR=%cd%\installer_files\lollmsenv
set INSTALL_ENV_DIR=%cd%\installer_files\lollms_env
set REPO_URL=https://github.com/ParisNeo/lollms-webui.git

REM Install LollmsEnv if not already installed
if not exist "%LOLLMSENV_DIR%" (
  echo Installing LollmsEnv...
  mkdir "%LOLLMSENV_DIR%"
  cd "%LOLLMSENV_DIR%"
  git clone https://github.com/ParisNeo/LollmsEnv.git .
  call install.bat --local
  cd "%~dp0"
) else (
  echo LollmsEnv already installed.
)

REM Activate LollmsEnv
call "%LOLLMSENV_DIR%\activate.bat"

REM Install Python 3.11
call lollmsenv install-python 3.11.0

REM Create Lollms environment
call lollmsenv create-env lollms_env 3.11.0

REM Activate Lollms environment
call lollmsenv activate lollms_env

REM Install required packages
call lollmsenv install git
call lollmsenv install pip

REM Install PyTorch
echo Installing pytorch (required for RAG)
nvidia-smi >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo CUDA-enabled device detected.
    echo Installing PyTorch with CUDA support...
    call lollmsenv install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu118
) ELSE (
    echo No CUDA-enabled device detected.
    echo Installing PyTorch for CPU only...
    call lollmsenv install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
)

REM Clone or update the repository
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

REM Install lollms_core
cd lollms-webui\lollms_core
call lollmsenv install -e .
cd ..\..

REM Install requirements
call lollmsenv install -r lollms-webui\requirements.txt

REM Create launcher scripts
if not exist ..\win_run.bat (
  copy lollms-webui\scripts\windows\win_run.bat ..\
)

if not exist ..\win_lollmsenv_session.bat (
  echo @echo off > ..\win_lollmsenv_session.bat
  echo call "%LOLLMSENV_DIR%\activate.bat" >> ..\win_lollmsenv_session.bat
  echo call lollmsenv activate lollms_env >> ..\win_lollmsenv_session.bat
  echo cmd /k >> ..\win_lollmsenv_session.bat
)

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
call python lollms-webui\zoos\bindings_zoo\ollama\__init__.py
goto :end

:python_llama_cpp
call python lollms-webui\zoos\bindings_zoo\python_llama_cpp\__init__.py
goto :end

:bs_exllamav2
call python lollms-webui\zoos\bindings_zoo\bs_exllamav2\__init__.py
goto :end

:groq
call python lollms-webui\zoos\bindings_zoo\groq\__init__.py
goto :end

:open_router
call python lollms-webui\zoos\bindings_zoo\open_router\__init__.py
goto :end

:open_ai
call python lollms-webui\zoos\bindings_zoo\open_ai\__init__.py
goto :end

:mistral_ai
call python lollms-webui\zoos\bindings_zoo\mistral_ai\__init__.py
goto :end

:gemini
call python lollms-webui\zoos\bindings_zoo\gemini\__init__.py
goto :end

:vllm
call python lollms-webui\zoos\bindings_zoo\vllm\__init__.py
goto :end

:xAI
call python lollms-webui\zoos\bindings_zoo\xAI\__init__.py
goto :end

:elf
call python lollms-webui\zoos\bindings_zoo\elf\__init__.py
goto :end

:remote_lollms
call python lollms-webui\zoos\bindings_zoo\remote_lollms\__init__.py
goto :end

:PrintBigMessage
echo. && echo.
echo *******************************************************************
for %%M in (%*) do echo * %%~M
echo *******************************************************************
echo. && echo.
exit /b

:failed
echo Install failed
goto endend

:end
echo Installation complete.

:endend
pause
