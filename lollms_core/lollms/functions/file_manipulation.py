# Lollms function call definition file
# Here you need to import any necessary imports depending on the function requested by the user
from functools import partial
from typing import List
from ascii_colors import trace_exception

# Importing pathlib
from pathlib import Path

# Function to change the file extension
def change_file_extension(file_path: str, new_extension: str) -> str:
    """
    Change the extension of a given file path.

    Parameters:
    file_path (str): The original file path.
    new_extension (str): The new extension, including the leading dot (e.g., '.txt').

    Returns:
    str: The new file path with the changed extension.

    Example:
    >>> change_file_extension("example.docx", ".txt")
    'example.txt'
    """
    try:
        # Create a Path object from the file path
        path = Path(file_path)
        
        # Change the extension
        new_path = path.with_suffix(new_extension)
        
        # Return the new path as a string
        return str(new_path)
    except Exception as e:
        return trace_exception(e)

# Metadata function
def change_file_extension_function():
    return {
        "function_name": "change_file_extension", # The function name in string
        "function": change_file_extension, # The function to be called
        "function_description": "Takes a file path and a new extension, then returns the new path with the changed extension.", # Description of the function
        "function_parameters": [
            {"name": "file_path", "type": "str"},
            {"name": "new_extension", "type": "str"}
        ] # The set of parameters          
    }
