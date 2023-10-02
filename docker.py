import os
import yaml


def read_yaml(yaml_file_path, key, value):
    with open(yaml_file_path, 'r') as file:
        return yaml.safe_load(file)

# set GPU env var

# Example usage
check_key_value('your_file.yaml', 'your_key', 'your_value')