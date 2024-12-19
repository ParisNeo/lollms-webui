######
# Project       : lollms-webui
# File          : config.py
# Author        : ParisNeo with the help of the community
# Supported by Nomic-AI
# license       : Apache 2.0
# Description   :
# Configuration management tool
######
import yaml

__author__ = "parisneo"
__github__ = "https://github.com/ParisNeo/lollms-webui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"


def load_config(file_path):
    with open(file_path, "r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream)

    return config


def save_config(config, filepath):
    with open(filepath, "w") as f:
        yaml.dump(config, f)
