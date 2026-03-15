# Lollms function call definition file
from functools import partial
from lollms.utilities import PackageManager
from ascii_colors import trace_exception
from typing import List, Union
from pathlib import Path
import ast

def update_function_in_file(function_name: str, new_content: str, project_path: Union[str, Path] = "") -> str:
    """
    Updates the specified function with new content in the given project path.

    Args:
        function_name (str): The name of the function to update.
        new_content (str): The new content to replace the function with.
        project_path (Union[str, Path]): The path to the Python project directory.

    Returns:
        str: Success message or error message.
    """
    try:
        project_path = Path(project_path)
        
        # Validate the project path
        if not project_path.exists() or not project_path.is_dir():
            return "Invalid project path."
        
        # Traverse the project directory and update function content
        for py_file in project_path.rglob("*.py"):
            with open(py_file, "r", encoding="utf-8") as file:
                content = file.read()
                tree = ast.parse(content)
                
                function_found = False
                updated_content = []
                lines = content.split("\n")
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == function_name:
                        function_found = True
                        # Calculate the indentation level
                        indent_level = len(lines[node.lineno-1]) - len(lines[node.lineno-1].lstrip())
                        indented_new_content = "\n".join(" " * indent_level + line for line in new_content.split("\n"))
                        updated_content.extend(lines[:node.lineno-1])
                        updated_content.append(indented_new_content)
                        updated_content.extend(lines[node.end_lineno:])
                        break
                
                if function_found:
                    with open(py_file, "w", encoding="utf-8") as file:
                        file.write("\n".join(updated_content))
                    return f"Function {function_name} updated successfully in file {py_file.relative_to(project_path)}."
        
        return "Function not found in the specified project."
        
    except Exception as e:
        return trace_exception(e)
    
    
# Metadata function 
def update_function_in_file_function(project_path:str ):
    return {
        "function_name": "update_function_in_file", # The function name in string
        "function": partial(update_function_in_file, project_path=project_path), # The function to be called
        "function_description": "Updates the specified function with new content in the given project path.", # Description of the function
        "function_parameters": [ # The set of parameters
            {"name": "function_name", "type": "str"},
            {"name": "new_content", "type": "str"},
        ]
    }
