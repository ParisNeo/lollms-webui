
echo \u001b[34m
echo HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHH     .HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHH.     ,HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHH.##  HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHHH#.HHHHH/*,*,*,*,*,*,*,*,***,*,**#HHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHHHHH.*,,***,***,***,***,***,***,*******HHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHHH*,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,*,,,,,HHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHH.,,,***,***,***,***,***,***,***,***,***,***/HHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHH*,,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*HHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHH#,***,***,***,***,***,***,***,***,***,***,***,**HHHHHHHHHHHHHHHHH
echo HHHHHHHHHH..HHH,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,*#HHHHHHHHHHHHHHHH
echo HHHHHHH,,,**,/H*,***,***,***,,,*,***,***,***,**,,,**,***,***,***H,,*,***HHHHHHHH
echo HHHHHH.*,,,*,,,,,*,*,*,***#HHHHH.,,*,*,*,*,**/HHHHH.,*,*,*,*,*,*,*,*****HHHHHHHH
echo HHHHHH.*,***,*,*,***,***,.HHHHHHH/**,***,****HHHHHHH.***,***,***,*******HHHHHHHH
echo HHHHHH.,,,,,,,,,,,,,,,,,,,.HHHHH.,,,,,,,,,,,,.HHHHHH,,,,,,,,,,,,,,,,,***HHHHHHHH
echo HHHHHH.,,,,,,/H,,,**,***,***,,,*,***,***,***,**,,,,*,***,***,***H***,***HHHHHHHH
echo HHHHHHH.,,,,*.H,,,,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,***H*,,,,/HHHHHHHHH
echo HHHHHHHHHHHHHHH*,***,***,**,,***,***,***,***,***,***,***,***,**.HHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHH,,,,,,,,*,,#H#,,,,,*,,,*,,,,,,,,*#H*,,,,,,,,,**HHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHH,,*,***,***,**/.HHHHHHHHHHHHH#*,,,*,***,***,*HHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHH,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*HHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHH**,***,***,***,***,***,***,***,***,***,***,*.HHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHH*,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,*HHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHH**,***,***,*******/..HHHHHHHHH.#/*,*,,,***,***HHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHH*,*,*,******#HHHHHHHHHHHHHHHHHHHHHHHHHHHH./**,,,.HHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHH.,,*,***.HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH.*#HHHHHHHHHHHH
echo HHHHHHHHHHHHHHH/,,,*.HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHH,,#HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHH.HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
echo \u001b[0m
echo Checking internet connection

ping google.com -n 1 >nul 2>&1
if errorlevel 1 (
    echo Internet connection not available
    goto NO_INTERNET
) else (
    goto INTERNET_OK
)
:NO_INTERNET

if exist lollms-webui (
    echo lollms-webui folder found
    cd lollms-webui
    set /p="Activating Conda environment ..." <nul
    call activate <conda_environment_name>
)
goto END

:INTERNET_OK
echo \e[32mInternet connection working fine

REM Check if Git is installed
echo "Checking for git..."
where git >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    goto GIT_CHECKED
) else (
    goto GIT_INSTALL
)
:GIT_FINISH

REM Check if Git is installed
:GIT_CHECKED
echo "Git is installed."
goto GIT_SKIP

:GIT_INSTALL
echo.
choice /C YN /M "Do you want to download and install Git?"
if errorlevel 2 goto GIT_CANCEL
if errorlevel 1 goto GIT_INSTALL_2

:GIT_INSTALL_2
echo "Git is not installed. Installing Git..."
powershell.exe -Command "Start-Process https://git-scm.com/download/win -Wait"
goto GIT_SKIP

:GIT_CANCEL
echo.
echo Git download cancelled.
echo Please install Git and try again.
pause
exit /b 1

:GIT_SKIP

REM Check if repository exists 
echo checking git repository
if exist ".git" (
    goto :PULL_CHANGES
) else (
    goto :CLONE_REPO
)

:PULL_CHANGES
echo Pulling latest changes 
git pull origin main
goto :CHECK_CONDA_INSTALL

:CLONE_REPO
REM Check if repository exists 
if exist lollms-webui (
    echo lollms-webui folder found
    cd lollms-webui
    echo Pulling latest changes 
    git pull
) else (
    echo Cloning repository...
    rem Clone the Git repository into a temporary directory
    git clone https://github.com/ParisNeo/lollms-webui.git ./lollms-webui
    cd lollms-webui
    echo Pulling latest changes 
    git pull
)

:CHECK_CONDA_INSTALL
REM Check if Conda is installed
set /p="Checking for Conda..." <nul
where conda >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    goto CONDA_CHECKED
) else (
    goto CONDA_INSTALL
)
:CONDA_CHECKED
echo "Conda is installed."
goto CONDA_SKIP

:CONDA_INSTALL
echo.
choice /C YN /M "Do you want to download and install Conda?"
if errorlevel 2 goto CONDA_CANCEL
if errorlevel 1 goto CONDA_INSTALL_2

:CONDA_INSTALL_2
REM Download Conda installer
if not exist "./tmp" mkdir "./tmp"
echo Downloading Conda installer...
powershell -Command "Invoke-WebRequest -Uri 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe' -OutFile 'tmp/conda.exe'"
REM Install Conda
echo Installing Conda...
tmp/conda.exe /InstallationType=JustMe /AddToPath=0 /RegisterPython=0 /S

:CONDA_CANCEL
echo Please install Conda and try again.
pause
exit /b 1

:CONDA_SKIP

REM Activate Conda environment
set /p="Activating Conda environment ..." <nul
conda activate <conda_environment_name>
echo OK

REM Install the required packages
echo Installing requirements ...
conda install --file requirements.txt

if %ERRORLEVEL% neq 0 (
    echo Failed to install required packages. Please check your internet connection and try again.
    pause
    exit /b 1
)

echo Checking models...
if not exist \models (
    md \models
)

:END
if exist "./tmp"  (
echo Cleaning tmp folder
rd /s /q "./tmp"
)

echo Conda environment activated and packages installed successfully.
echo Launching application...

REM Run the Python app
python app.py %*
set app_result=%errorlevel%

pause >nul
exit /b 0
