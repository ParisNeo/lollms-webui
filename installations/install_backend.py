import argparse
import subprocess
import shutil
import yaml
from pathlib import Path


def install_binding(binding_name):
    # Load the list of available bindings from bindinglist.yaml
    with open('bindinglist.yaml', 'r') as f:
        binding_list = yaml.safe_load(f)

    # Get the Github repository URL for the selected binding
    try:
        binding_url = binding_list[binding_name]
    except KeyError:
        print(f"Binding '{binding_name}' not found in bindinglist.yaml")
        return

    # Clone the Github repository to a tmp folder
    tmp_folder = Path('tmp')
    if tmp_folder.exists():
        shutil.rmtree(tmp_folder)
    subprocess.run(['git', 'clone', binding_url, tmp_folder])

    # Install the requirements.txt from the cloned project
    requirements_file = tmp_folder / 'requirements.txt'
    subprocess.run(['pip', 'install', '-r', str(requirements_file)])

    # Copy the folder found inside the binding to ../bindings
    folders = [f for f in tmp_folder.iterdir() if f.is_dir() and not f.stem.startswith(".")]
    src_folder = folders[0]
    dst_folder = Path('../bindings') / src_folder.stem
    print(f"coipying from {src_folder} to {dst_folder}")
    # Delete the destination directory if it already exists
    if dst_folder.exists():
        shutil.rmtree(dst_folder)

    shutil.copytree(src_folder, dst_folder)

    # Create an empty folder in ../models with the same name
    models_folder = Path('../models')
    models_folder.mkdir(exist_ok=True)
    (models_folder / binding_name).mkdir(exist_ok=True, parents=True)
    if tmp_folder.exists():
        shutil.rmtree(tmp_folder)


if __name__ == '__main__':
    # Load the list of available bindings from bindinglist.yaml
    with open('bindinglist.yaml', 'r') as f:
        binding_list = yaml.safe_load(f)

    # Print the list of available bindings and prompt the user to select one
    print("Available bindings:")
    for binding_id, binding_name in enumerate(binding_list):
        print(f" {binding_id} - {binding_name}")
    binding_id = int(input("Select a binding to install: "))

    install_binding(list(binding_list.keys())[binding_id])
