#!/bin/bash
source ../env/Scripts/activate
python install_binding.py "$@"
read -p "Press any key to continue..." 
