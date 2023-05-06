@echo off
setlocal enabledelayedexpansion

REM Clone the repository to a tmp folder
set "REPO_URL=https://github.com/ParisNeo/PyAIPersonality.git"
set "TMP_FOLDER=%temp%\PyAIPersonality"
git clone %REPO_URL% %TMP_FOLDER%

REM List the available languages and prompt user to select one
set "LANGUAGES_FOLDER=%TMP_FOLDER%\personalities_zoo"
set "LANGUAGE_INDEX=0"
for /d %%d in ("%LANGUAGES_FOLDER%\*") do (
  set /a "LANGUAGE_INDEX+=1"
  set "LANGUAGES[!LANGUAGE_INDEX!]=%%~nxd"
  echo !LANGUAGE_INDEX!. %%~nxd
)
set /p "SELECTED_LANGUAGE=Enter the number of the desired language: "
set "LANGUAGE_FOLDER=%LANGUAGES_FOLDER%\!LANGUAGES[%SELECTED_LANGUAGE%]!"

REM List the available categories and prompt user to select one
set "CATEGORIES_FOLDER=%LANGUAGE_FOLDER%"
set "CATEGORY_INDEX=0"
for /d %%d in ("%CATEGORIES_FOLDER%\*") do (
  set /a "CATEGORY_INDEX+=1"
  set "CATEGORIES[!CATEGORY_INDEX!]=%%~nxd"
  echo !CATEGORY_INDEX!. %%~nxd
)
set /p "SELECTED_CATEGORY=Enter the number of the desired category: "
set "CATEGORY_FOLDER=%CATEGORIES_FOLDER%\!CATEGORIES[%SELECTED_CATEGORY%]!"

REM List the available personalities and prompt user to select one
set "PERSONALITIES_FOLDER=%CATEGORY_FOLDER%"
set "PERSONALITY_INDEX=0"
for /d %%d in ("%PERSONALITIES_FOLDER%\*") do (
  set /a "PERSONALITY_INDEX+=1"
  set "PERSONALITIES[!PERSONALITY_INDEX!]=%%~nxd"
  echo !PERSONALITY_INDEX!. %%~nxd
)
set /p "SELECTED_PERSONALITY=Enter the number of the desired personality: "
set "PERSONALITY_FOLDER=%PERSONALITIES_FOLDER%\!PERSONALITIES[%SELECTED_PERSONALITY%]!"

REM Copy the selected personality folder to personalities/language/category folder
set "OUTPUT_FOLDER=%CD%\personalities\!LANGUAGES[%SELECTED_LANGUAGE%]!\!CATEGORIES[%SELECTED_CATEGORY%]!\!PERSONALITIES[%SELECTED_PERSONALITY%]!"
if not exist "%OUTPUT_FOLDER%" mkdir "%OUTPUT_FOLDER%"
xcopy /e /y "%PERSONALITY_FOLDER%" "%OUTPUT_FOLDER%"

REM cleaning 
if exist "./tmp"  (
echo Cleaning tmp folder
rd /s /q "./tmp"
)
REM Remove the tmp folder
rd /s /q "%TMP_FOLDER%"
echo Done
pause