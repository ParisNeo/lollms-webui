# Import necessary libraries
from pathlib import Path
from functools import partial

from typing import List, Union
import ast

# ascii_colors offers advanced console coloring and bug tracing
from ascii_colors import trace_exception

# Function to retrieve classes from the project files
def retrieve_classes_from_project(class_names: List[str], project_path: Union[str, Path]) -> str:
    """
    Retrieves the code of specified classes from the given project path.

    Args:
        project_path (Union[str, Path]): The path to the Python project directory.
        class_names (List[str]): List of class names to retrieve.

    Returns:
        str: The code of the specified classes as a string.
    """
    try:
        project_path = Path(project_path)
        
        # Validate the project path
        if not project_path.exists() or not project_path.is_dir():
            return "Invalid project path."
        
        class_code = "\n"
        
        # Traverse the project directory and extract class code
        for py_file in project_path.rglob("*.py"):
            with open(py_file, "r", encoding="utf-8") as file:
                content = file.read()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name in class_names:
                        class_code += f"\n\n# Class: {node.name} in file: {py_file.relative_to(project_path)}\n"
                        class_code += "```python\n"
                        class_code += "\n".join(content.split("\n")[node.lineno-1:node.end_lineno])
                        class_code += "\n```\n"
        
        return class_code if class_code else "No specified classes found."
        
    except Exception as e:
        return trace_exception(e)

# Metadata function
def retrieve_classes_from_project_function(project_path:str):
    return {
        "function_name": "retrieve_classes_from_project", 
        "function": partial(retrieve_classes_from_project,project_path = project_path),
        "function_description": "Retrieves the code of specified classes from the given project path.",
        "function_parameters": [
            {"name": "class_names", "type": "list", "description": "List of class names to retrieve."}
        ]          
    }