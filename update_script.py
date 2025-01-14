import argparse
import os
import subprocess
import sys
from pathlib import Path

import git
import pipmaster as pm
from ascii_colors import ASCIIColors, trace_exception

if not pm.is_installed("PyQt5"):
    pm.install("PyQt5")

import sys

from PyQt5.QtWidgets import QApplication, QMessageBox


def show_error_dialog(message):
    try:
        app = QApplication(sys.argv)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec_()
    except:
        ASCIIColors.error(message)


def run_git_pull():
    try:
        ASCIIColors.info("----------------> Updating the code <-----------------------")

        repo = git.Repo(Path(__file__).parent)
        origin = repo.remotes.origin

        # Fetch the latest changes
        origin.fetch()

        # Check if there are any changes to pull
        if repo.head.commit == origin.refs.main.commit:
            ASCIIColors.success("Already up-to-date.")

        # Discard local changes and force update
        try:
            repo.git.reset("--hard", "origin/main")
            repo.git.clean("-fd")
            origin.pull()
            ASCIIColors.success("Successfully updated the code.")
        except git.GitCommandError as e:
            error_message = f"Failed to update the code: {str(e)}"
            ASCIIColors.error(error_message)
            # show_error_dialog(error_message)

        print("Updating submodules")
        try:
            repo.git.submodule("update", "--init", "--recursive", "--force")
        except Exception as ex:
            error_message = f"Couldn't update submodules: {str(ex)}"
            ASCIIColors.error(error_message)
            # show_error_dialog(error_message)
        try:
            # Checkout the main branch on each submodule
            for submodule in repo.submodules:
                try:
                    submodule_repo = submodule.module()
                    submodule_repo.git.fetch("origin")
                    submodule_repo.git.reset("--hard", "origin/main")
                    submodule_repo.git.clean("-fd")
                    ASCIIColors.success(f"Updated submodule: {submodule}.")
                except Exception as ex:
                    print(
                        f"Couldn't update submodule {submodule}: {str(ex)}\nPlease report the error to ParisNeo either on Discord or on github."
                    )

            execution_path = Path(os.getcwd())
        except Exception as ex:
            error_message = f"Couldn't update submodules: {str(ex)}\nPlease report the error to ParisNeo either on Discord or on github."
            ASCIIColors.error(error_message)
            # show_error_dialog(error_message)
        try:
            # Update lollms_core
            ASCIIColors.info("Updating lollms_core")
            lollms_core_path = execution_path / "lollms_core"
            if lollms_core_path.exists():
                subprocess.run(
                    ["git", "-C", str(lollms_core_path), "fetch", "origin"], check=True
                )
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(lollms_core_path),
                        "reset",
                        "--hard",
                        "origin/main",
                    ],
                    check=True,
                )
                subprocess.run(
                    ["git", "-C", str(lollms_core_path), "clean", "-fd"], check=True
                )
                ASCIIColors.success("Successfully updated lollms_core")
            else:
                ASCIIColors.warning("lollms_core directory not found")

        except Exception as ex:
            error_message = f"Couldn't update submodules: {str(ex)}"
            ASCIIColors.error(error_message)
            # show_error_dialog(error_message)

        return True
    except Exception as e:
        error_message = f"Error during git operations: {str(e)}"
        ASCIIColors.error(error_message)
        # show_error_dialog(error_message)
        return False


def get_valid_input():
    while True:
        update_prompt = (
            "New code is updated. Do you want to update the requirements? (y/n): "
        )
        user_response = input(update_prompt).strip().lower()

        if user_response in ["y", "yes"]:
            return "yes"
        elif user_response in ["n", "no"]:
            return "no"
        else:
            print("Invalid input. Please respond with 'y' or 'n'.")


def install_requirements():
    try:
        # Get valid input from the user
        user_choice = get_valid_input()

        # Enhance the text based on the user's response
        if user_choice == "yes":
            enhanced_text = "Great choice! Updating requirements ensures your project stays up-to-date with the latest changes."
            print(enhanced_text)
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "-r",
                    "requirements.txt",
                ]
            )
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "-e",
                    "lollms_core",
                ]
            )
            ASCIIColors.success("Successfully installed requirements")
        else:  # user_choice == 'no'
            enhanced_text = "Understood. Skipping the requirements update. Make sure to update them later if needed."
            print(enhanced_text)
    except subprocess.CalledProcessError as e:
        error_message = f"Error during pip install: {str(e)}"
        ASCIIColors.error(error_message)
        show_error_dialog(error_message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo",
        type=str,
        default="https://github.com/ParisNeo/lollms-webui.git",
        help="Path to the Git repository",
    )
    args = parser.parse_args()

    repo_path = args.repo

    # Perform git pull to update the repository
    if run_git_pull():
        # Install the new requirements (not needed anymore)
        # install_requirements()

        # Reload the main script with the original arguments
        temp_file = "temp_args.txt"
        if os.path.exists(temp_file):
            with open(temp_file, "r") as file:
                args = file.read().split()
            main_script = "app.py"  # Replace with the actual name of your main script
            os.system(f"{sys.executable} {main_script} {' '.join(args)}")
            try:
                os.remove(temp_file)
            except Exception as e:
                error_message = f"Couldn't remove temp file. Try to remove it manually.\nThe file is located here: {temp_file}\nError: {str(e)}"
                ASCIIColors.warning(error_message)
        else:
            error_message = "Error: Temporary arguments file not found."
            ASCIIColors.error(error_message)
            show_error_dialog(error_message)
            sys.exit(1)
    else:
        error_message = (
            "Update process failed. Please check the console for more details."
        )
        ASCIIColors.error(error_message)
        show_error_dialog(error_message)
        sys.exit(1)


if __name__ == "__main__":
    main()
