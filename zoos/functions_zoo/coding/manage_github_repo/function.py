from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails
from datetime import datetime
import yaml
from typing import List, Dict
from ascii_colors import ASCIIColors, trace_exception
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
import os
import subprocess
from pathlib import Path
import requests

# Use pipmaster to check and install any missing module by its name
import pipmaster as pm
if not pm.is_installed("requests"):
    pm.install("requests")

class GitHubRepoManager(FunctionCall):
    def __init__(self, app: LollmsApplication, client: Client):
        # Static parameters for GitHub token and user profile name
        static_parameters = TypedConfig(
            ConfigTemplate([
                {
                    "name": "github_token",
                    "type": "str",
                    "value": "",
                    "help": "GitHub token for authentication."
                },
                {
                    "name": "github_user",
                    "type": "str",
                    "value": "",
                    "help": "GitHub user profile name."
                }
            ]),
            BaseConfig(config={})
        )
        super().__init__("manage_github_repo", app, FunctionType.CLASSIC, client, static_parameters)
        self.personality = app.personality

    def update_context(self, context: LollmsContextDetails, constructed_context: List[str]):
        # No additional context needed for this function
        return constructed_context

    def execute(self, context: LollmsContextDetails, *args, **kwargs):
        # Recover parameters
        repo_name = kwargs.get("repo_name", "")
        commit_message = kwargs.get("commit_message", "")
        
        # Recover static parameters or environment variables
        github_token = self.static_parameters.github_token or os.getenv("GITHUB_TOKEN", "")
        github_user = self.static_parameters.github_user or os.getenv("GITHUB_USER", "")
        
        if not github_token or not github_user:
            self.personality.set_message_html(self.personality.build_error_message("GitHub token or user profile name is missing. Please set them in the static parameters or environment variables."))
            return "GitHub token or user profile name is missing. Please set them in the static parameters or environment variables."
        
        # Get the discussion folder path
        discussion_folder = Path(self.client.discussion.discussion_folder)
        
        # Check if the folder is already a git repository
        is_repo = (discussion_folder / ".git").exists()
        
        if not is_repo:
            # Initialize a new git repository
            subprocess.run(["git", "init"], cwd=discussion_folder, check=True)
            
            # Create a new GitHub repository
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            data = {
                "name": repo_name,
                "private": False
            }
            response = requests.post(f"https://api.github.com/user/repos", headers=headers, json=data)
            
            if response.status_code != 201:
                return f"Failed to create GitHub repository: {response.json().get('message', 'Unknown error')}"
            
            # Add the remote origin
            subprocess.run(["git", "remote", "add", "origin", f"https://github.com/{github_user}/{repo_name}.git"], cwd=discussion_folder, check=True)
        
        # Stage all changes
        subprocess.run(["git", "add", "."], cwd=discussion_folder, check=True)
        
        # Commit changes
        subprocess.run(["git", "commit", "-m", commit_message], cwd=discussion_folder, check=True)
        
        # Push changes
        subprocess.run(["git", "push", "-u", "origin", "master"], cwd=discussion_folder, check=True)
        self.personality.set_message_html(self.personality.build_message_element(f"Successfully pushed changes to GitHub repository '{repo_name}' with commit message: '{commit_message}'."))
        return f"Successfully pushed changes to GitHub repository '{repo_name}' with commit message: '{commit_message}'."