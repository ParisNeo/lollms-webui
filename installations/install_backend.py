import argparse
import subprocess
import shutil
import yaml
from pathlib import Path


def install_backend(backend_name):
    # Load the list of available backends from backendlist.yaml
    with open('backendlist.yaml', 'r') as f:
        backend_list = yaml.safe_load(f)

    # Get the Github repository URL for the selected backend
    try:
        backend_url = backend_list[backend_name]
    except KeyError:
        print(f"Backend '{backend_name}' not found in backendlist.yaml")
        return

    # Clone the Github repository to a tmp folder
    tmp_folder = Path('tmp')
    if tmp_folder.exists():
        shutil.rmtree(tmp_folder)
    subprocess.run(['git', 'clone', backend_url, tmp_folder])

    # Install the requirements.txt from the cloned project
    requirements_file = tmp_folder / 'requirements.txt'
    subprocess.run(['pip', 'install', '-r', str(requirements_file)])

    # Copy the folder found inside the binding to ../backends
    folders = [f for f in tmp_folder.iterdir() if f.is_dir() and not f.stem.startswith(".")]
    src_folder = folders[0]
    dst_folder = Path('../backends') / src_folder.stem
    print(f"coipying from {src_folder} to {dst_folder}")
    # Delete the destination directory if it already exists
    if dst_folder.exists():
        shutil.rmtree(dst_folder)

    shutil.copytree(src_folder, dst_folder)

    # Create an empty folder in ../models with the same name
    models_folder = Path('../models')
    models_folder.mkdir(exist_ok=True)
    (models_folder / backend_name).mkdir(exist_ok=True, parents=True)
    if tmp_folder.exists():
        shutil.rmtree(tmp_folder)


if __name__ == '__main__':
    # Load the list of available backends from backendlist.yaml
    with open('backendlist.yaml', 'r') as f:
        backend_list = yaml.safe_load(f)

    # Print the list of available backends and prompt the user to select one
    print("Available backends:")
    for backend_id, backend_name in enumerate(backend_list):
        print(f" {backend_id} - {backend_name}")
    backend_id = int(input("Select a backend to install: "))

    install_backend(list(backend_list.keys())[backend_id])
