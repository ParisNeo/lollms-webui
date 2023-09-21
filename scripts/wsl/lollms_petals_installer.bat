@echo off
echo Checking if wsl is installed...
wsl --list >nul 2>&1
if %errorlevel% neq 0 (
    echo WSL is not enabled or installed. Enabling and installing...
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
    echo WSL installation complete.
) else (
    echo WSL is enabled and installed.
)

set "distribution=Ubuntu-20.04"
wsl --list | findstr "%distribution%"
if %errorlevel% equ 0 (
    echo %distribution% exists in WSL.
) else (
    echo %distribution% does not exist in WSL.
    echo Installing Ubuntu 20.04...
    wsl --install -d Ubuntu-20.04
    wsl -d Ubuntu-20.04 -- apt upgrade -y
    echo Ubuntu 20.04 installation complete.
)

echo Running the install script...
wsl.exe -d Ubuntu-20.04 ./install_script.sh
echo Script execution complete.

pause
