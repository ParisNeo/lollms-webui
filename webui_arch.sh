#!/usr/bin/env bash
#
# Adapted for compatabillity wiht Arch-based distributions using pacman package manager
# Adapted by: Pikkiewyn <jacquesjooste@gmail.com>
#
# Some liberties taken with the banner - feel free to revert back to the previous version :)
#
# *Dynamicaly centering banner output (results may vary depending on terminal-type)
# *I spent an inordinate amount of time on this banner...
#
#>measure term width
COLUMNS=$(tput cols)
#>banner
printf "%*s\n" $((""+COLUMNS/2)) "\u001b[0m                                           m0]dl00u/"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHH     .HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHH.     ,HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHH.##  HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHHHHHH#.HHH_*,*,*,*,*,,*,***,*,**#HHHHHHHHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHHHHHHHH.*,**,***,***,,***,***,******HHHHHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHHHHHH*,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,HHHHHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHHHHH.,,**,**,***,***,,***,***,***,**_HHHHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHHHH*,*,*,,,*,*,*,*,*,,*,*,*,*,*,*,,*,*HHHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHHH#,**,**,**,***,***,,***,***,***,**,**HHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHH.HHH,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,*#HHHHHH.HHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHH,,*,_H*,**,**,**,,,*,***,,***,**,,,**,**,***H,,*,**.HHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHH.*,*,,,,,**,*,*#HHHHH.,,*,,*,**_HHHHH.,,*,*,*,*,****.HHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHH.*,*,*,*,**,**,HHHHHHH_**,,****HHHHHHH.**,***,******.HHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHH.,,,,,,,,,,,,,,.HHHHH.,,,,,,,,,.HHHHHH,,,,,,,,,,,,**,HHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHH.,,,,_H,,,*,**,**,,,*,***,,***,**,,,,*,**,***H***,**.HHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHH.,,*.H,,,*,*,,,*,*,*,*,*,,*,*,*,*,*,*,,*,***H*,.,.HHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHHH*,**,**,*,,***,***,,***,***,***,**,**.HHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHHHH,,,,,,*,#H#,,,,,*,,,,,,,,,*#H*,,,,**HHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHHHHH,*,**,**,**HHHHHHHHHHHH#*,,,*,**,*HHHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHHHHHH*,*,,,*,*,*,*,*,,*,*,*,*,*,*,,*,*HHHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHHHHHH*,**,**,***,***,,***,***,***,**,*.HHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHHHHHH,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,*HHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHHHHHH*,**,**,*******_HHHHHHHH.#_*,,,,***HHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHHHHH**,*,****#HHHHHHHHHHHHHHHHHHHHHH**,,,.HHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHHHH.,*,**.HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH.*#HHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHHH_,,*.HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHH,,#HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHH.HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
printf "%*s\n" $((""+COLUMNS/2)) "\u001b[0m                                           m0]dl00u/"
#./shellcheckrc

  printf "Testing internet connectivity"
  ping -c1 -W1 google.com

# Check the exit status of the previous command

  if [ $? -eq 0 ]; then
    printf "Internet connectivity confirmed\n"
  else
    printf "A connection to the internet could not be established,\nplease re-run the script once internet access has been restored.\n"
  exit 1
  fi

#>Git installation

  printf "Confirming Git installation...\n"

  if (git --version) > /dev/null; then
    printf "Git is installed\n"
  else
    printf "Git installation not found. Would you like to install it now? \n"
    until [[ $choice == [Yy] ]]; do
        if [[ $choice == [Nn] ]]; then
          printf "Installation aborted...\n"
          exit 1
        else
          read -r -p "Please confirm (y/n): " choice
          echo
        fi
    done
    printf "Installing Git...\n"
    sudo pacman -S --noconfirm --needed git
      if git --version > /dev/null; then
        printf "Installation successful\n"
      else
        printf "Git installation was unsuccessful. Please install it manually and re-run the scripn\n"
    fi
  fi

#>-Check if repository exists

  printf "Synchronizing repository"

  if [[ -d .git ]] ;then
    printf "Pulling latest changes\n"
    git pull origin main
  elif  [[ -d lollms-webui ]] ;then
    #-error-handling in case folder isn't accessible..avoids a minor mess if cd fails and script keeps going
    cd lollms-webui || { echo "Couldn't access repo folder. Please check folder structure / permissions and run script again"; exit 1; }
  else
    printf "Cloning repository...\n"
    git clone https://github.com/ParisNeo/lollms-webui.git ./lollms-webui 
    if [ $? -ne 0 ]; then
        printf "Downloadin from git failed. Please check your internet connection and permissions and try again.\n"
        exit 1
    fi
    cd lollms-webui || { echo "Couldn't access repo folder. Please check folder structure / permissions and run script again"; exit 1; }
  fi
    printf "Pulling latest version...\n"
    git pull

##>Install Python 3.10 and venv module
#-arch's packages are structured such that the python3 package always installs the latest version,
#-and the venv module is included so we only have to check against the one package

  printf "Checking if Python 3.10+ is installed...\n"

  if (python3 --version) > /dev/null; then
    printf "Python3.10+ is installed.\n"
  else
    read -r -p "Python3 is not installed. Would you like to install it now? (y/n):" choice
    if [ "$choice" == y.Y ]; then
      printf "Installing Python3.10+...\n"
      sudo pacman -Syu
        if $(sudo pacman -S --needed --noconfirm python3) eq 0; then
          printf "Python installed succesfully\n"
        else
          printf "Installation failed. Please install the package manually and run the script again.\n"; exit 1
        fi
    else
    printf "Installation aborted"; exit 1
    fi
  fi

#>Creating a new virtual environment

  printf "Creating virtual environment...\n"

  if [ "$(python3 -m venv env)" ]; then
    printf "Virtual environment installed."
  else
    printf "Failed to install virtual envoronemnt. Please check your Python and ensure the venv module installed correcly."
    exit 1
  fi

#>Activate virtual environment

  printf "Activating virtual environment..."
  source env/bin/activate
  source env/bin/activate 
if [ $? -ne 0 ]; then
    printf "Failed to activate virtual environment. Please check your setup and try again.\n"
    exit 1
else
      printf "Virtrual environment is active"
fi  

#>Install the required packages

  printf "Installing requirements..."
  python3 -m pip install pip --upgrade

  if $( python3 -m pip install --upgrade -r requirements.txt ) -ne 0 ; then
    printf "Failed to install required packages. Please check your internet connection and try again."
    exit 1
  fi

#>Cleanup

  if [ -d "./tmp" ]; then
    printf "Cleaning tmp folder"
    rm -rf "./tmp"
  fi

#>Launch the Python application

printf "Launching application"
python app.py