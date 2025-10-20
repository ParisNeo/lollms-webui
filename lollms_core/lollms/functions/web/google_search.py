# Lollms function call definition file

# Import necessary libraries
from functools import partial
from typing import List
from lollms.utilities import PackageManager
from ascii_colors import trace_exception

# Ensure the webbrowser package is available
if not PackageManager.check_package_installed("webbrowser"):
    PackageManager.install_package("webbrowser")

# Import the webbrowser library
import webbrowser

# Define the function to perform a Google search
def google_search(query: str) -> str:
    """
    Perform a Google search using the default web browser.

    Parameters:
    - query (str): The search query.

    Returns:
    - str: A message indicating the search was performed.
    """
    try:
        # Construct the Google search URL
        search_url = f"https://www.google.com/search?q={query}"
        
        # Open the search URL in the default web browser
        webbrowser.open(search_url)
        
        # Return a success message
        return f"Performed Google search for query: {query}"
    except Exception as e:
        return trace_exception(e)

# Define the metadata function
def google_search_function():
    return {
        "function_name": "google_search",  # The function name in string
        "function": google_search,  # The function to be called
        "function_description": "Performs a Google search using the default web browser.",  # Description of the function
        "function_parameters": [{"name": "query", "type": "str"}]  # The set of parameters
    }
