import os
from pathlib import Path
import subprocess
import sys
from lollms.utilities import create_conda_env, run_script_in_env

def installAmphion(directory=None):
    # Save the current working directory
    original_cwd = Path.cwd()
    
    try:
        # Set the target directory for installation
        if directory is None:
            directory = original_cwd
        else:
            directory = Path(directory)
            # Create the directory if it does not exist
            directory.mkdir(parents=True, exist_ok=True)
        
        # Change the current working directory to the specified directory
        os.chdir(directory)
        
        # Clone the Amphion repository
        subprocess.run("git clone https://github.com/open-mmlab/Amphion.git", shell=True)
        
        # Change directory into the cloned Amphion directory
        os.chdir("Amphion")
    
        # Create and activate the Conda environment
        create_conda_env("amphion", "3.9.15")
    
        # Assuming env.sh installs Python package dependencies via pip
        # Modify the path to env.sh if it is located in a different directory
        env_sh_path = Path.cwd() / "env.sh"
        run_script_in_env("amphion", str(env_sh_path))
    finally:
        # Restore the original working directory
        os.chdir(original_cwd)

# Example usage: Install Amphion in a specific folder
if __name__ == "__main__":
    target_directory = "/path/to/specific/folder"
    installAmphion(target_directory)
