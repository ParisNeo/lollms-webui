# Lollms function call definition file
from ascii_colors import trace_exception
from typing import List, Union
from pathlib import Path
import ast

def add_function_to_file(file_path: Union[str, Path], function_name: str, function_content: str) -> str:
    """
    Adds a new function to the specified file.

    Args:
        file_path (Union[str, Path]): The path to the Python file.
        function_name (str): The name of the function to add.
        function_content (str): The content of the function to add.

    Returns:
        str: Success message or error message.
    """
    try:
        file_path = Path(file_path)
        
        # Validate the file path
        if not file_path.exists() or not file_path.is_file():
            return "Invalid file path."
        
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            tree = ast.parse(content)
            
            # Check if function already exists
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    return f"Function {function_name} already exists in the file."
            
            # Add the new function content at the end of the file
            with open(file_path, "a", encoding="utf-8") as file:
                file.write("\n\n" + function_content)
            
            return f"Function {function_name} added successfully to file {file_path}."
        
    except Exception as e:
        return trace_exception(e)
    

# Metadata function 
def add_function_to_file_function():
    return {
        "function_name": "add_function_to_file", # The function name in string
        "function": add_function_to_file, # The function to be called
        "function_description": "Adds a new function to the specified file.", # Description of the function
        "function_parameters": [ # The set of parameters
            {"name": "file_path", "type": "str"},
            {"name": "function_name", "type": "str"},
            {"name": "function_content", "type": "str"},
        ]
    }