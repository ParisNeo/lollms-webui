# File : extension.py
# Author : ParisNeo
# Description :
# This is the main class to be imported by the extension
# it gives your code access to the model, the callback functions, the model conditionning etc
from config import load_config, save_config

class Extension():
    def __init__(self, metadata_file_path:str) -> None:
        self.config = load_config()