# Lollms function call definition file

# Partial is useful if we need to preset some parameters
from functools import partial

# It is advised to import typing elements
from typing import List

# Import PackageManager if there are potential libraries that need to be installed 
from lollms.utilities import PackageManager

# ascii_colors offers advanced console coloring and bug tracing
from ascii_colors import trace_exception

# Here is an example of how we install a non installed library using PackageManager
if not PackageManager.check_package_installed("pyautogui"):
    PackageManager.install_package("pyautogui")
if not PackageManager.check_package_installed("webbrowser"):
    PackageManager.install_package("webbrowser")
if not PackageManager.check_package_installed("time"):
    PackageManager.install_package("time")
if not PackageManager.check_package_installed("os"):
    PackageManager.install_package("os")

# now we can import the libraries
import pyautogui
import webbrowser
import time
import os

# Function to open YouTube, search for a specific video, and play the first one
def search_youtube(video_title: str = "lollms paris neo") -> str:
    """
    Opens YouTube, searches for a specific video, and plays the first one in the list.
    
    Parameters:
    video_title (str): The title of the video to search for.
    
    Returns:
    str: Success or error message.
    """
    try:
        # Open YouTube
        webbrowser.open("https://www.youtube.com")
        time.sleep(5)  # Wait for the browser to open YouTube
        
        # Click on the search bar (searching for the element named 'search_query')
        script_dir = os.path.dirname(__file__)
        search_query_path = os.path.join(script_dir, 'search_query.png')
        search_bar_position = pyautogui.locateCenterOnScreen(search_query_path, confidence=0.8)
        if search_bar_position:
            pyautogui.click(search_bar_position)
        else:
            return "Search bar not found on the screen."

        # Type the video title and press Enter
        pyautogui.write(video_title, interval=0.1)
        pyautogui.press('enter')
        time.sleep(5)  # Wait for the search results to load
        
        return "Video is playing."

    except Exception as e:
        return trace_exception(e)
    

# Metadata function
def search_youtube_function():
    return {
        "function_name": "search_youtube", # The function name in string
        "function": search_youtube, # The function to be called
        "function_description": "Opens YouTube, searches for a specific video, and plays the first one in the list.", # Description
        "function_parameters": [{"name": "video_title", "type": "str"}] # Parameters
    }

# Add the if __name__ statement for testing
if __name__ == "__main__":
    video_title = "lollms paris neo"
    result = search_youtube(video_title)
    print(result)
