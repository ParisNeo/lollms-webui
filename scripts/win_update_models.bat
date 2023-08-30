@echo off
@echo Starting LOLLMS Web UI...
echo "     ___       ___           ___       ___       ___           ___      "
echo "    /\__\     /\  \         /\__\     /\__\     /\__\         /\  \     "
echo "   /:/  /    /::\  \       /:/  /    /:/  /    /::|  |       /::\  \    "
echo "  /:/  /    /:/\:\  \     /:/  /    /:/  /    /:|:|  |      /:/\ \  \   "
echo " /:/  /    /:/  \:\  \   /:/  /    /:/  /    /:/|:|__|__   _\:\~\ \  \  "
echo "/:/__/    /:/__/ \:\__\ /:/__/    /:/__/    /:/ |::::\__\ /\ \:\ \ \__\ "
echo "\:\  \    \:\  \ /:/  / \:\  \    \:\  \    \/__/~~/:/  / \:\ \:\ \/__/ "
echo " \:\  \    \:\  /:/  /   \:\  \    \:\  \         /:/  /   \:\ \:\__\   "
echo "  \:\  \    \:\/:/  /     \:\  \    \:\  \       /:/  /     \:\/:/  /   "
echo "   \:\__\    \::/  /       \:\__\    \:\__\     /:/  /       \::/  /    "
echo "    \/__/     \/__/         \/__/     \/__/     \/__/         \/__/     "
echo By ParisNeo

cd /D "%~dp0"

@rem better isolation for virtual environment
SET "CONDA_SHLVL="
SET PYTHONNOUSERSITE=1
SET "PYTHONPATH="
SET "PYTHONHOME="
SET "TEMP=%cd%\installer_files\temp"
SET "TMP=%cd%\installer_files\temp"

@rem workaround for broken Windows installs
set PATH=%PATH%;%SystemRoot%\system32

set INSTALL_ENV_DIR=%cd%\installer_files\lollms_env
set MINICONDA_DIR=%cd%\installer_files\miniconda3

if not exist "%MINICONDA_DIR%\Scripts\activate.bat" ( echo Miniconda not found. Please reinstall lollms using win_install.bat. && goto end )
call "%MINICONDA_DIR%\Scripts\activate.bat" activate "%INSTALL_ENV_DIR%"
cd lollms-webui

@rem set default cuda toolkit to the one in the environment
set "CUDA_PATH=%INSTALL_ENV_DIR%"

@echo off
setlocal

REM Set your repository URL and file path
set repository_url=https://github.com/ParisNeo/lollms_bindings_zoo.git

REM Set the destination folder where the file will be downloaded
set destination_folder=downloaded_files

REM Create the destination folder if it doesn't exist
if not exist "%destination_folder%" mkdir "%destination_folder%"

REM Clone the repository (if not already cloned)
if not exist "%destination_folder%\repository" (
    git clone "%repository_url%" "%destination_folder%\repository"
)

REM Change directory to the repository folder
cd "%destination_folder%\repository"

REM Fetch the latest changes from the remote repository
cp hugging_face/models.yaml ../../personal_data/bindings_zoo/hugging_face/models.yaml
cp c_transformers/models.yaml ../../personal_data/bindings_zoo/c_transformers/models.yaml
cp llama_cpp_official/models.yaml ../../personal_data/bindings_zoo/llama_cpp_official/models.yaml
cp gpt_4all/models.yaml ../../personal_data/bindings_zoo/gpt_4all/models.yaml
cp py_llama_cpp/models.yaml ../../personal_data/bindings_zoo/py_llama_cpp/models.yaml
cp gptq/models.yaml ../../personal_data/bindings_zoo/gptq/models.yaml
cp exllama/models.yaml ../../personal_data/bindings_zoo/exllama/models.yaml

echo removing temporary files
cd ../..
rmdir /s /q "%destination_folder%"
echo done
:end
pause
