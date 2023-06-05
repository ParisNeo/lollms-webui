#!/bin/bash
source ../env/bin/activate
python install_binding.py "$@"
read -p "Press any key to continue..." 
