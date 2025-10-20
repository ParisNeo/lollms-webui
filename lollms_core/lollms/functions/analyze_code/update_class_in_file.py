# Lollms function call definition file
from functools import partial
from lollms.utilities import PackageManager
from ascii_colors import trace_exception
from typing import List, Union
from pathlib import Path
import ast
def update_class_in_file(class_name: str, new_content: str, method_name: Union[str, None] = None, project_path: Union[str, Path] = "") -> str:
    """
    Updates the specified class or method with new content in the given project path.

    Args:
        class_name (str): The name of the class to update.
        new_content (str): The new content to replace the class or method with.
        method_name (Union[str, None]): The name of the method to update. If None, updates the entire class.
        project_path (Union[str, Path]): The path to the Python project directory.

    Returns:
        str: Success message or error message.
    """
    try:
        project_path = Path(project_path)
        
        # Validate the project path
        if not project_path.exists() or not project_path.is_dir():
            return "Invalid project path."
        
        # Traverse the project directory and update class or method content
        for py_file in project_path.rglob("*.py"):
            with open(py_file, "r", encoding="utf-8") as file:
                content = file.read()
                tree = ast.parse(content)
                
                class_found = False
                method_found = False
                updated_content = []
                lines = content.split("\n")
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == class_name:
                        class_found = True
                        if method_name is None:
                            # Update entire class content
                            updated_content.extend(lines[:node.lineno-1])
                            updated_content.append(new_content)
                            updated_content.extend(lines[node.end_lineno:])
                        else:
                            # Update specific method content
                            for class_node in node.body:
                                if isinstance(class_node, ast.FunctionDef) and class_node.name == method_name:
                                    method_found = True
                                    # Calculate the indentation level
                                    indent_level = len(lines[class_node.lineno-1]) - len(lines[class_node.lineno-1].lstrip())
                                    indented_new_content = "\n".join(" " * indent_level + line for line in new_content.split("\n"))
                                    updated_content.extend(lines[:class_node.lineno-1])
                                    updated_content.append(indented_new_content)
                                    updated_content.extend(lines[class_node.end_lineno:])
                                    break
                            if not method_found:
                                return f"Method {method_name} not found in class {class_name}."
                        break
                
                if class_found:
                    with open(py_file, "w", encoding="utf-8") as file:
                        file.write("\n".join(updated_content))
                    return f"{'Method ' + method_name if method_name else 'Class ' + class_name} updated successfully in file {py_file.relative_to(project_path)}."
        
        return "Class not found in the specified project."
        
    except Exception as e:
        return trace_exception(e)
    

# Metadata function 
def update_class_in_file_function(project_path:str ):
    return {
        "function_name": "update_class_in_file", # The function name in string
        "function": partial(update_class_in_file,project_path = project_path), # The function to be called
        "function_description": "Updates the specified class with new content in the given project path.", # Description of the function
        "function_parameters": [ # The set of parameters
            {"name": "class_name", "type": "str"},
            {"name": "new_content", "type": "str"},
            {"name": "method_name", "type": "str", "description":"An optional method name, required only if you need to change a single method content. If you need to change the whole class, do not set this element"},
        ]
    }