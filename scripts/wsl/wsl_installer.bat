@echo off
echo Checking if WSL is enabled...
wsl --list >nul 2>&1
if %errorlevel% neq 0 (
    echo WSL is not enabled. Enabling it...
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
    echo WSL is now enabled.
) else (
    echo WSL is enabled and installed.
)

echo Checking if WSL 2 is installed...
wsl --set-default-version 2 >nul 2>&1
if %errorlevel% neq 0 (
    echo WSL 2 is not installed. Installing it...
    wsl --install
    echo WSL 2 installation complete.
) else (
    echo WSL 2 is already installed.
)

pause