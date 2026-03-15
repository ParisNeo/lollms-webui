# personal_data/custom_function_calls/git_tools/git_commit_summarizer/function.py

import os
import sys
from pathlib import Path # Use pathlib for more robust path handling
from typing import List, Dict, Any, Optional

# Lollms specific imports
from lollms.function_call import FunctionCall, FunctionType # Base class and enum
from lollms.app import LollmsApplication # Main application instance
from lollms.client_session import Client # User session
from lollms.prompting import LollmsContextDetails # Context details object
# No config classes needed as there are no static params
# from lollms.config import TypedConfig, ConfigTemplate, BaseConfig

# Logging and Dependencies
import ascii_colors as logging # Use alias for the logging API
from ascii_colors import trace_exception # Specific import for exceptions
import pipmaster as pm

# --- Dependency Check ---
GITPYTHON_PACKAGE = "GitPython"
git = None # Initialize git to None
try:
    # Use ensure_packages for potentially clearer intent, though install works too
    pm.ensure_packages({GITPYTHON_PACKAGE:""})
    import git # Now safe to import
except ImportError:
    # Log the error using ascii_colors directly if logger isn't available yet
    logging.error(f"ERROR: {GITPYTHON_PACKAGE} is required but could not be imported after attempting installation.")
    # git remains None, checked later in execute
except Exception as e:
    logging.error(f"ERROR: Failed during {GITPYTHON_PACKAGE} dependency check/installation.")
    trace_exception(e)
    # git remains None

class GitCommitSummarizer(FunctionCall): # Must match class_name in config.yaml
    def __init__(self, app: LollmsApplication, client: Client):
        # --- Step 1: Initialize Logger (Recommended) ---
        # Use the __name__ of the module and the class name for a unique logger name
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.debug(f"Initializing {self.__class__.__name__}...")

        # --- Step 2: Define Static Parameters Setup (If Needed) ---
        # No static parameters are defined in config.yaml for this function.
        # If there were, ConfigTemplate and TypedConfig would be defined here.
        # config_template = ConfigTemplate([...])
        # static_params_config = TypedConfig(config_template, BaseConfig(config={}))

        # --- Step 3: Call Parent Class Constructor (MANDATORY) ---
        super().__init__(
            function_name="git_commit_summarizer", # MUST match 'name' in config.yaml
            app=app,                            # Pass the app instance
            function_type=FunctionType.CLASSIC, # Set the function type
            client=client,                      # Pass the client instance
            # static_parameters=static_params_config # Omit if no static params
        )

        # --- Step 4: Access Loaded Static Parameters (AFTER super().__init__()) ---
        # No static parameters to access here.
        # If there were: self.api_key = self.static_parameters.config.get("api_key", "")

        # --- Step 5: Initialize Other Instance Variables ---
        # Any other setup needed for the function can go here.
        # For this function, checking GitPython availability is handled in execute.
        self.logger.info(f"{self.function_name} function initialized successfully.")


    def execute(self, context: LollmsContextDetails, *args, **kwargs) -> str:
        """Analyzes git changes and generates a commit message using the LLM."""
        self.logger.debug(f"Executing {self.function_name}...")

        # --- Dependency Check ---
        if git is None:
            err_msg = f"Error: The required library '{GITPYTHON_PACKAGE}' is not available. Please install it manually (`pip install {GITPYTHON_PACKAGE}`) and restart LoLLMs."
            self.logger.error(err_msg)
            # Provide minimal feedback via UI step if possible, though personality might not be fully ready
            try: self.personality.step_end(err_msg, success=False)
            except: pass
            return err_msg # Return error to LLM

        # --- Parameter Handling ---
        repo_path_param = kwargs.get("repo_path")
        if not repo_path_param:
            self.logger.warning("Parameter 'repo_path' is missing.")
            return "Error: Repository path ('repo_path') parameter is missing."

        self.logger.info(f"Received request to summarize Git repo at: {repo_path_param}")
        self.personality.step_start(f"Analyzing Git repository: {repo_path_param}")

        try:
            # --- Path Validation and Normalization ---
            repo_path = Path(repo_path_param).resolve() # Use pathlib and resolve absolute path
            self.logger.debug(f"Resolved repository path to: {repo_path}")

            if not repo_path.exists():
                err_msg = f"Error: Repository path does not exist: {repo_path}"
                self.logger.error(err_msg)
                self.personality.step_end(f"Path does not exist.", success=False)
                return err_msg
            if not repo_path.is_dir():
                err_msg = f"Error: Provided path is not a directory: {repo_path}"
                self.logger.error(err_msg)
                self.personality.step_end(f"Path is not a directory.", success=False)
                return err_msg

            # --- Git Interaction ---
            try:
                self.logger.debug("Attempting to open Git repository...")
                repo = git.Repo(str(repo_path)) # git.Repo expects string path
                self.logger.debug("Repository opened successfully.")
            except git.InvalidGitRepositoryError:
                err_msg = f"Error: Not a valid Git repository: {repo_path}"
                self.logger.error(err_msg)
                self.personality.step_end(f"Not a valid Git repository.", success=False)
                return err_msg
            except Exception as e:
                 self.logger.error(f"Failed to access Git repository at {repo_path}")
                 trace_exception(e)
                 self.personality.step_end(f"Failed to access Git repository.", success=False)
                 return f"Error accessing Git repository: {type(e).__name__}. Check logs."

            # --- Analyze Changes ---
            self.logger.debug("Checking repository status (is_dirty)...")
            if not repo.is_dirty(untracked_files=True):
                self.logger.info("No changes detected in the repository.")
                self.personality.step_end("No changes detected.", success=True)
                return "No changes detected in the repository. Nothing to summarize for commit."

            self.logger.debug("Fetching staged diff...")
            staged_diff = repo.git.diff('--staged')
            self.logger.debug(f"Staged diff length: {len(staged_diff)}")

            self.logger.debug("Fetching unstaged diff...")
            unstaged_diff = repo.git.diff()
            self.logger.debug(f"Unstaged diff length: {len(unstaged_diff)}")

            self.logger.debug("Fetching untracked files...")
            untracked_files = repo.untracked_files
            untracked_files_str = "\n".join([f"- {f}" for f in untracked_files]) if untracked_files else "None"
            self.logger.debug(f"Untracked files: {len(untracked_files)}")

            change_summary = (
                f"Staged Changes (to be committed):\n```diff\n{staged_diff if staged_diff else 'None'}\n```\n\n"
                f"Unstaged Changes (not staged):\n```diff\n{unstaged_diff if unstaged_diff else 'None'}\n```\n\n"
                f"Untracked Files (new files not tracked):\n```\n{untracked_files_str}\n```"
            )
            self.personality.step("Git changes collected.")

            # --- LLM Interaction for Commit Message ---
            self.personality.step_start("Generating commit message...")
            self.logger.debug("Preparing prompt for LLM commit message generation.")

            # Limit the diff size sent to the LLM
            MAX_DIFF_LENGTH = 4000 # Characters
            if len(change_summary) > MAX_DIFF_LENGTH:
                self.logger.warning(f"Change summary length ({len(change_summary)}) exceeds limit ({MAX_DIFF_LENGTH}). Truncating.")
                change_summary = change_summary[:MAX_DIFF_LENGTH] + "\n\n... (diff truncated due to length)"

            prompt = (
                "Based on the following Git repository changes (staged, unstaged, untracked), generate a concise and informative commit message.\n"
                "IMPORTANT: Follow the Conventional Commits specification (e.g., 'feat: ...', 'fix: ...', 'docs: ...', 'style: ...', 'refactor: ...', 'perf: ...' 'test: ...', 'build: ...', 'ci: ...', 'chore: ...'). The message should start directly with the type and scope (if any), followed by a colon and space, then the description.\n\n"
                f"### Git Changes:\n{change_summary}\n\n"
                "### Suggested Conventional Commit Message:"
            )
            self.logger.debug(f"Prompt for fast_gen:\n{prompt[:200]}...") # Log beginning of prompt

            try:
                commit_message = self.personality.fast_gen(
                    prompt,
                    callback=self.personality.sink # Hide intermediate tokens in UI
                )
                self.logger.info(f"LLM generated commit message draft: {commit_message}")

                # Clean up potential LLM artifacts
                commit_message = commit_message.strip().strip('"`').strip().lstrip('\n')
                # Take the first line as the primary message
                first_line = commit_message.split('\n')[0].strip()

                self.logger.info(f"Final suggested commit message: {first_line}")
                self.personality.step_end("Commit message generated.", success=True)
                # Return just the first line for clarity to the LLM
                return f"Suggested Commit Message: {first_line}"

            except Exception as e:
                self.logger.error("Failed to generate commit message using LLM.")
                trace_exception(e)
                self.personality.step_end("Failed to generate commit message.", success=False)
                return f"Error during commit message generation: {type(e).__name__}. Check logs."

        except Exception as e:
            # Catch-all for unexpected errors during execution
            self.logger.error(f"An unexpected error occurred in {self.function_name}.")
            trace_exception(e)
            # Attempt to signal failure via UI
            try: self.personality.step_end("An unexpected error occurred.", success=False)
            except: pass
            # Notify the user via app console/logs
            self.app.error(f"Error in {self.function_name} function: {e}")
            return f"An unexpected error occurred: {type(e).__name__}. Please check LoLLMs logs."

    # No settings_updated needed as there are no static parameters
    # def settings_updated(self):
    #     self.logger.debug(f"{self.function_name}: Settings updated called, but no static parameters to reload.")
    #     pass