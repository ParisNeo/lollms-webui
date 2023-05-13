import json
import yaml
from pathlib import Path
import argparse

def json_to_yaml(json_file):
    # Read JSON file
    with open(json_file, 'r') as file:
        json_data = json.load(file)

    # Create YAML file path
    yaml_file = Path(json_file).with_suffix('.yaml')

    # Convert JSON to YAML
    with open(yaml_file, 'w') as file:
        yaml.dump(json_data, file)

    print(f"Conversion complete. YAML file saved as: {yaml_file}")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Convert JSON file to YAML.')
    parser.add_argument('json_file', help='Path to the JSON file')
    args = parser.parse_args()

    # Convert JSON to YAML
    json_to_yaml(args.json_file)
