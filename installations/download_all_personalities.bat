@echo off

rem Set the environment name
set environment_name=env

rem Activate the virtual environment
call %environment_name%\Scripts\activate.bat

rem Change to the installations subfolder

rem Run the Python script
python installations/download_all_personalities.py

rem Deactivate the virtual environment
echo deactivating
call %environment_name%\Scripts\deactivate.bat

rem Remove tmp folder
set "folder=tmp"

if exist "%folder%" (
    echo Folder exists. Deleting...
    rd /s /q "%folder%"
    echo Folder deleted.
) else (
    echo Folder does not exist.
)