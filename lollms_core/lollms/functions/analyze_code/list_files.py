# Lollms function call definition file
# File Name: list_project_structure.py
# Author: ParisNeo
# Description: This function lists and displays the structure of the project directory.

from functools import partial
from pathlib import Path
from typing import Union, List
from ascii_colors import trace_exception

def list_project_structure(project_path: Union[str, Path]) -> str:
    """
    Lists and displays the structure of the project directory, excluding certain directories.

    Args:
        project_path (Union[str, Path]): The path to the project directory.

    Returns:
        str: A string representation of the project directory structure.
    """
    try:
        project_path = Path(project_path)
        
        # Validate the project path
        if not project_path.exists() or not project_path.is_dir():
            return "Invalid project path."
        
        # Directories to exclude
        exclude_dirs = {'.git', '.vscode', '__pycache__'}
        
        structure = []
        for file in project_path.rglob("*"):
            # Skip excluded directories
            if any(part in exclude_dirs or part.endswith('.egg-info') for part in file.parts):
                continue
            
            indent_level = len(file.relative_to(project_path).parts) - 1
            structure.append(f"{'    ' * indent_level}{file.name}")
        
        return "\n".join(structure)
        
    except Exception as e:
        return trace_exception(e)

def list_project_structure_function(project_path: Union[str, Path]):
    return {
        "function_name": "list_project_structure",
        "function": partial(list_project_structure, project_path=project_path),
        "function_description": "Lists and displays the structure of the project directory.",
        "function_parameters": []
    }
