# Lollms function call definition file
# File Name: add_code_to_file.py
# Author: ParisNeo
# Description: This function adds given code to a specified Python file in a project directory.

# Import necessary modules
from functools import partial
from ascii_colors import trace_exception
from typing import Union
from pathlib import Path

# Function to add code to a file
def add_code_to_file(file_name: str, code_content: str, project_path: Union[str, Path] = "") -> str:
    """
    Adds the specified code content to the given file in the project path.

    Args:
        file_name (str): The name of the file to add code to.
        code_content (str): The code content to be added.
        project_path (Union[str, Path]): The path to the Python project directory.

    Returns:
        str: Success message or error message.
    """
    try:
        project_path = Path(project_path)
        
        # Validate the project path
        if not project_path.exists() or not project_path.is_dir():
            return "Invalid project path."
        
        file_path = project_path / file_name
        
        # Check if the file exists
        if not file_path.exists():
            return f"File {file_name} does not exist in the specified project."
        
        # Read the current content of the file
        with open(file_path, "r", encoding="utf-8") as file:
            current_content = file.read()
        
        # Add the new code content
        updated_content = current_content + "\n\n" + code_content
        
        # Write the updated content back to the file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(updated_content)
        
        return f"Code added successfully to file {file_name}."
        
    except Exception as e:
        return trace_exception(e)
    

# Metadata function 
def add_code_to_file_function(project_path: str):
    return {
        "function_name": "add_code_to_file", # The function name in string
        "function": partial(add_code_to_file, project_path=project_path), # The function to be called
        "function_description": "Adds the specified code content to the given file in the project path.", # Description of the function
        "function_parameters": [ # The set of parameters
            {"name": "file_name", "type": "str"},
            {"name": "code_content", "type": "str"},
        ]
    }
