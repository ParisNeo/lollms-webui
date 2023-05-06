#!/bin/bash
source ../env/Scripts/activate
python install_backend.py "$@"
read -p "Press any key to continue..." 
