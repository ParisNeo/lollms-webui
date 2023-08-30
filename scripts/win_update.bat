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

echo Pulling latest changes
call git pull

echo Reinstalling requirements
pip install --upgrade -r requirements.txt

:end
pause
