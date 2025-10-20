# Lollms function call definition file
# File Name: create_file.py
# Author: ParisNeo
# Description: This function creates a text file with specified content in the 'text_data' subfolder.

# Import necessary modules
from functools import partial
from typing import Union
from pathlib import Path
from lollms.utilities import PackageManager
from lollms.client_session import Client
from ascii_colors import trace_exception

# Core function to create a file
def create_file(file_name: str, content: str, client:Client) -> Union[str, None]:
    """
    Creates a text file with the specified content in the 'text_data' subfolder.
    
    Parameters:
    file_name (str): The name of the file to be created.
    content (str): The content to be written into the file.
    
    Returns:
    Union[str, None]: Returns None if successful, otherwise returns the exception message.
    """
    try:
        # Define the path to the 'text_data' subfolder

        # Define the full file path
        file_path = client.discussion_path/ 'text_data' / file_name

        # Write the content to the file
        file_path.write_text(content, encoding='utf-8')

        # Return None if successful
        return None
    except Exception as e:
        return trace_exception(e)

# Metadata function
def create_file_function(client:Client):
    return {
        "function_name": "create_file", # The function name in string
        "function": partial(create_file, client=client), # The function to be called
        "function_description": "Creates a text file with specified content in the 'text_data' subfolder.", # Description of the function
        "function_parameters": [
            {"name": "file_name", "type": "str"}, 
            {"name": "content", "type": "str"}
        ] # The set of parameters
    }
