# Lollms function call definition file
# File Name: list_project_classes.py
# Author: Saif
# Description: This script defines a function to list all classes in a given Python project.

# Import necessary libraries
from functools import partial
from pathlib import Path
from typing import Union, List
import ast
import sqlite3

# Import PackageManager if there are potential libraries that need to be installed 
from lollms.utilities import PackageManager

# ascii_colors offers advanced console coloring and bug tracing
from ascii_colors import trace_exception

# Here is the core of the function to be built
def list_project_classes(project_path: Union[str, Path]) -> List[str]:
    """
    Lists all classes in a given Python project.

    Args:
        project_path (Union[str, Path]): The path to the Python project directory.

    Returns:
        List[str]: A list of class names found in the project.
    """
    try:
        project_path = Path(project_path)
        
        # Validate the project path
        if not project_path.exists() or not project_path.is_dir():
            return ["Invalid project path."]
        
        class_names = []

        # Traverse the project directory and extract class names
        for py_file in project_path.rglob("*.py"):
            with open(py_file, "r", encoding="utf-8") as file:
                content = file.read()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_names.append(node.name)

        return class_names
        
    except Exception as e:
        return [trace_exception(e)]

# Metadata function
def list_project_classes_function(project_path):
    return {
        "function_name": "list_project_classes",
        "function": partial(list_project_classes, project_path=project_path),
        "function_description": "Lists all classes in a given Python project.",
        "function_parameters": []
    }
