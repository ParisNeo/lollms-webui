######
# Project       : GPT4ALL-UI
# File          : config.py
# Author        : ParisNeo with the help of the community
# Supported by Nomic-AI
# Licence       : Apache 2.0
# Description   : 
# A front end Flask application for llamacpp models.
# The official GPT4All Web ui
# Made by the community for the community
######
import yaml

def load_config(file_path):
    with open(file_path, 'r') as stream:
        config = yaml.safe_load(stream)
    return config


def save_config(config, filepath):
    with open(filepath, "w") as f:
        yaml.dump(config, f)