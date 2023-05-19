import argparse
import yaml
from urllib.parse import urlparse

from pathlib import Path

def process_yaml(input_file):
    # Read YAML file
    with open(input_file, 'r') as file:
        models = yaml.safe_load(file)

    # Process each model entry
    for model in models:
        server_url = model['server']
        parsed_url = urlparse(server_url)
        if not 'owner' in model:
            if 'huggingface.co' in parsed_url.netloc:
                # Hugging Face URL, extract owner from server URL
                model['owner'] = parsed_url.path.split('/')[1]
            else:
                # Non-Hugging Face URL, use domain name as owner
                model['owner'] = parsed_url.netloc

        # Add additional fields
        if not 'link' in model:
            model['link'] = server_url
        if not 'license' in model:
            model['license'] = 'Non commercial'

    # Save processed YAML file
    output_file = input_file.stem + '_processed.yaml'
    with open(output_file, 'w') as file:
        yaml.dump(models, file)

    print(f"Processed YAML file saved as {output_file}")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Process YAML file')
    parser.add_argument('input_file', type=str, help='Input YAML file')

    args = parser.parse_args()

    input_file = Path(args.input_file)

    if not input_file.exists():
        print('Input file does not exist.')
        return

    process_yaml(input_file)

if __name__ == '__main__':
    main()
