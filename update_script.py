
import os
import sys
import git
import subprocess
import argparse
from pathlib import Path

def run_git_pull():
    try:
        print("----------------> Updating the code <-----------------------")
        repo = git.Repo(Path(__file__).parent)
        origin = repo.remotes.origin
        origin.pull()
        print("Updating submodules")
        try:
            repo.git.submodule('update', '--init')
            # Checkout the main branch on each submodule
            for submodule in repo.submodules:
                try:
                    submodule_repo = submodule.module()
                    submodule_repo.git.checkout('main')
                except Exception as ex:
                    print(f"Couldn't checkout module {submodule}")
        except Exception as ex:
            print("Couldn't update submodules")
            print(ex)
        return True
    except git.GitCommandError as e:
        print(f"Error during git pull: {e}")
        return False

def install_requirements():
    try:
        subprocess.check_call(["pip", "install", "--upgrade", "-r", "requirements.txt"])
    except subprocess.CalledProcessError as e:
        print(f"Error during pip install: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=str, default="https://github.com/ParisNeo/lollms-webui.git", help="Path to the Git repository")
    args = parser.parse_args()

    repo_path = args.repo

    # Perform git pull to update the repository
    run_git_pull()

    # Install the new requirements
    install_requirements()

    # Reload the main script with the original arguments
    temp_file = "temp_args.txt"
    if os.path.exists(temp_file):
        with open(temp_file, "r") as file:
            args = file.read().split()
        main_script = "app.py"  # Replace with the actual name of your main script
        os.system(f"python {main_script} {' '.join(args)}")
        os.remove(temp_file)
    else:
        print("Error: Temporary arguments file not found.")
        sys.exit(1)

if __name__ == "__main__":
    main()
