# Lollms function call definition file
# File Name: git_pull.py
# Author: ParisNeo
# Description: This function pulls the latest changes from the remote repository to the local Git repository.

# Import necessary libraries
from functools import partial
from typing import Union
from pathlib import Path
import subprocess
from ascii_colors import trace_exception

# Ensure Git is installed
from lollms.utilities import PackageManager

if not PackageManager.check_package_installed("git"):
    PackageManager.install_package("gitpython")

import git

def git_pull(repo_path: Union[str, Path]) -> str:
    """
    Pulls the latest changes from the remote repository to the local Git repository.

    Args:
        repo_path (Union[str, Path]): The path to the Git repository.

    Returns:
        str: Success or error message.
    """
    try:
        repo_path = Path(repo_path)
        if not repo_path.exists():
            return "Repository path does not exist."

        repo = git.Repo(repo_path)

        # Pull latest changes
        repo.remotes.origin.pull()

        return "Latest changes pulled successfully."

    except Exception as e:
        return trace_exception(e)

def git_pull_function(repo_path:Path|str):
    return {
        "function_name": "git_pull",
        "function": partial(git_pull, repo_path=repo_path),
        "function_description": "Pulls the latest changes from the remote repository to the local Git repository.",
        "function_parameters": [
            {"name": "repo_path", "type": "str"}
        ]
    }

if __name__ == "__main__":
    # Example usage
    repo_path = "path/to/repo"
    print(git_pull(repo_path))
