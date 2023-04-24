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

__author__ = "parisneo"
__github__ = "https://github.com/nomic-ai/gpt4all-ui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

def load_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as stream:
        config = yaml.safe_load(stream)
    return config


def save_config(config, filepath):
    with open(filepath, "w") as f:
        yaml.dump(config, f)