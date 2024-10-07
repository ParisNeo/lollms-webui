@echo off
setlocal enabledelayedexpansion
:: Version number
set VERSION=1.3.2
set USE_MASTER=false

:: Check for --use-master option
for %%a in (%*) do (
    if "%%a"=="--use-master" set USE_MASTER=true
)

:: Temporary directory for downloading and extraction
set TEMP_DIR=.\lollmsenv_install

:: Create temporary directory
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

if "%USE_MASTER%"=="true" (
    echo Cloning LollmsEnv master branch...
    git clone https://github.com/ParisNeo/LollmsEnv.git "%TEMP_DIR%"
    cd /d "%TEMP_DIR%"
) else (
    :: URL of the latest release
    set RELEASE_URL=https://github.com/ParisNeo/LollmsEnv/archive/refs/tags/V%VERSION%.zip

    :: Download the latest release
    echo Downloading LollmsEnv version %VERSION%...
    echo !RELEASE_URL!
    echo '%TEMP_DIR%'
    pause
    powershell -Command "Invoke-WebRequest -Uri '!RELEASE_URL!' -OutFile '%TEMP_DIR%\lollmsenv.zip'"
    if %errorlevel% neq 0 (
        echo Error downloading LollmsEnv: %errorlevel%
        exit /b 1
    )

    :: Extract the archive
    echo Extracting files...
    powershell -Command "Expand-Archive -Path '%TEMP_DIR%\lollmsenv.zip' -DestinationPath '%TEMP_DIR%' -Force"

    :: Change to the extracted directory
    cd /d "%TEMP_DIR%\LollmsEnv-%VERSION%"
)

:: Remove --use-master from arguments
set ARGS=%*
set ARGS=%ARGS:--use-master=%

:: Run the install script with forwarded parameters
echo Running installation...
call install.bat %ARGS%

:: Clean up
echo Cleaning up...
cd /d ..
rmdir /s /q "%TEMP_DIR%"

echo Installation of LollmsEnv complete.

endlocal
