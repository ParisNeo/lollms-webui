# Lollms function call definition file
# File Name: <add a file name here>.py
# Author: <the author of this code is the user name>
# Description: <describe how this function works>

# Here you need to import any necessary imports depending on the function requested by the user
# exemple import math

# Partial is useful if we need to preset some parameters
from functools import partial

# It is advised to import typing elements
# from typing import List

# Import PackageManager if there are potential libraries that need to be installed 
from lollms.utilities import PackageManager

# ascii_colors offers advanced console coloring and bug tracing
from ascii_colors import trace_exception

# Here is an example of how we install a non installed library using PackageManager
if not PackageManager.check_package_installed("pyautogui"):
    PackageManager.install_package("pyautogui")

# now we can import the library
import pyautogui

# here is the core of the function to be built
# Change the name of this function depending on the user requets
def add_constant(parameter1:str, parameter2:int) -> float: # use typed parameters depending on the requested function, only int, float or text outputs are allowed
    """
    Put a detailed docstring here
    """
    
    try:
        # handle exceptions

        # Here you perform your computation or you execute the function
        result = 5.5+parameter2 if parameter1=="hi" else 5.5-parameter2
        
        
        # Finally we return the output
        return result
    except Exception as e:
        return trace_exception(e)
    

#Here is the metadata function that shoule has the name in format function_name_function for example if the function is add_numbers, this one should be add_numbers_function
#Use only parameters that are needed. You may use fixed parameters if necessary usnig partial
def add_constant_function():
    return {
        "function_name": "add_constant", # The function name in string
        "function": add_constant, # The function to be called
        "function_description": "Returns a constabnt value.", # Change this with the description
        "function_parameters": [{"name": "parameter1", "type": "str"}, {"name": "parameter2", "type": "str"}] # Te set of paraeters          
    }