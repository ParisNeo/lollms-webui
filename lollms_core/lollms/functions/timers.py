# Lollms function call definition file
# File Name: set_timer_with_alert.py
# Author: Saif (ParisNeo)
# Description: This function sets a non-blocking timer that shows a PyQt window with a message and makes noise after a specified duration. It works on any operating system by using the pyautogui library for the alert sound.

# Here you need to import any necessary imports depending on the function requested by the user
# example import math

# Partial is useful if we need to preset some parameters
from functools import partial

# It is advised to import typing elements
from typing import Any, Dict

# Import PackageManager if there are potential libraries that need to be installed 
from lollms.utilities import PackageManager

# ascii_colors offers advanced console coloring and bug tracing
from ascii_colors import trace_exception

# Here is an example of how we install a non installed library using PackageManager
import pipmaster as pm
# now we can import the libraries
import threading
import time
import sys

# here is the core of the function to be built
def set_timer_with_alert(duration: int, message: str) -> str:
    """
    Sets a non-blocking timer that shows a PyQt window with a message and makes noise after a specified duration.

    Parameters:
    duration (int): The duration for the timer in seconds.
    message (str): The message to be displayed in the alert window.

    Returns:
    str: A success message indicating the timer has been set.
    """
    if not pm.is_installed("pyautogui"):
        pm.install("pyautogui")
    import pyautogui

    def timer_callback():
        try:
            time.sleep(duration)
            pyautogui.alert(text=message, title="Timer Alert", button='OK')
            pyautogui.beep()
        except Exception as e:
            return trace_exception(e)
        
    try:
        # Start the timer in a new thread to make it non-blocking
        timer_thread = threading.Thread(target=timer_callback)
        timer_thread.start()
        
        # Return a success message
        return f"Timer set for {duration} seconds with message '{message}'."
    except Exception as e:
        return trace_exception(e)

# Here is the metadata function that should have the name in format function_name_function
def set_timer_with_alert_function() -> Dict[str, Any]:
    return {
        "function_name": "set_timer_with_alert", # The function name in string
        "function": set_timer_with_alert, # The function to be called
        "function_description": "Sets a non-blocking timer that shows a PyQt window with a message and makes noise after a specified duration.", # Description of the function
        "function_parameters": [{"name": "duration", "type": "int"}, {"name": "message", "type": "str"}] # The set of parameters
    }
