# Lollms function call definition file
# File Name: git_commit.py
# Author: ParisNeo
# Description: This function commits changes to a Git repository with a specified commit message.

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

def git_commit(commit_message: str, repo_path: Union[str, Path]) -> str:
    """
    Commits changes to a Git repository with a specified commit message.

    Args:
        repo_path (Union[str, Path]): The path to the Git repository.
        commit_message (str): The commit message.

    Returns:
        str: Success or error message.
    """
    try:
        repo_path = Path(repo_path)
        if not repo_path.exists():
            return "Repository path does not exist."

        repo = git.Repo(repo_path)

        # Stage all changes
        repo.git.add(A=True)

        # Commit changes
        repo.index.commit(commit_message)

        return "Changes committed successfully."

    except Exception as e:
        return trace_exception(e)

def git_commit_function(repo_path:Path|str):
    return {
        "function_name": "git_commit",
        "function": partial(git_commit, repo_path=repo_path),
        "function_description": "Commits changes to a Git repository with a specified commit message.",
        "function_parameters": [
            {"name": "commit_message", "type": "str"}
        ]
    }

if __name__ == "__main__":
    # Example usage
    repo_path = "path/to/repo"
    commit_message = "Your commit message"
    print(git_commit(repo_path, commit_message))
