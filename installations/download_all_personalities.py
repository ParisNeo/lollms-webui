import os
import shutil
from pathlib import Path

def copy_files(source_path, destination_path):
    for item in os.listdir(source_path):
        source_item = source_path / item
        destination_item = destination_path / item

        if source_item.is_file():
            # Remove destination file if it already exists
            try:
                if destination_item.exists():
                    destination_item.unlink()
                # Copy file from source to destination
                shutil.copy2(str(source_item), str(destination_item))
            except:
                print(f"Couldn't install personality {item}")

        elif source_item.is_dir():
            # Create destination directory if it does not exist
            destination_item.mkdir(parents=True, exist_ok=True)

            # Recursively copy files in subdirectories
            copy_files(source_item, destination_item)

import subprocess

def clone_and_copy_repository(repo_url):
    tmp_folder = Path("tmp/git_clone")
    personalities_folder = Path("personalities")
    subfolder_name = "personalities_zoo"

    # Clone the repository to a temporary folder
    subprocess.run(["git", "clone", repo_url, str(tmp_folder)])

    # Check if the repository was cloned successfully
    if not tmp_folder.exists():
        print("Failed to clone the repository.")
        return

    # Construct the source and destination paths for copying the subfolder
    subfolder_path = tmp_folder / subfolder_name
    destination_path = Path.cwd() / personalities_folder

    # Copy files and folders recursively
    print(f"copying")
    copy_files(subfolder_path, destination_path)

    # Remove the temporary folder
    shutil.rmtree(str(tmp_folder))

    print("Repository clone and copy completed successfully.")

# Example usage
repo_url = "https://github.com/ParisNeo/PyAIPersonality.git"
clone_and_copy_repository(repo_url)
