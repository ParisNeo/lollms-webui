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