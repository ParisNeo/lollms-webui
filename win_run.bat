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

REM Check for Git updates
git fetch
git status -uno > git_status.txt

REM Read the Git status from the file
set /p git_status=<git_status.txt

REM Prompt the user to update if there are changes
if "%git_status%" == "" (
    echo No updates available.
) else (
    echo Updates are available. Do you want to update? (y/n)
    set /p choice=
    if /i "%choice%"=="y" (
        git pull
        echo Repository has been updated successfully.
    ) else (
        echo Skipping the update.
    )
)

REM Clean up the temporary file
del git_status.txt

REM Check for library upgrades in requirements.txt
pip list --outdated > outdated_libraries.txt

REM Read the outdated library information from the file
setlocal enabledelayedexpansion
set "outdated_libraries="
for /f "skip=2 tokens=1,3" %%a in (outdated_libraries.txt) do (
    set "outdated_libraries=!outdated_libraries!%%a "
)
endlocal & set "outdated_libraries=%outdated_libraries%"

REM Prompt the user to update libraries if there are upgrades available
if "%outdated_libraries%" == "" (
    echo No library upgrades available.
) else (
    echo Upgrades are available for the following libraries: %outdated_libraries%
    echo Do you want to update the libraries? (y/n)
    set /p library_choice=
    if /i "%library_choice%"=="y" (
        pip install --upgrade -r requirements.txt
        echo Libraries have been updated successfully.
    ) else (
        echo Skipping the library updates.
    )
)

REM Clean up the temporary library information file
del outdated_libraries.txt

@rem set default cuda toolkit to the one in the environment
set "CUDA_PATH=%INSTALL_ENV_DIR%"

call python app.py  %*

:end
pause
