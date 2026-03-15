# Lollms function call definition file
# File Name: runway_ml_gen_2_video_creator.py
# Author: ParisNeo
# Description: This function opens the Luma AI Dream Machine webpage, navigates to the input section, and inputs a text prompt to create a video. If the user is not logged in, it prompts the user to log in.

# Import pathlib for file path operations
from pathlib import Path

# Import necessary libraries
from functools import partial
from typing import Dict, Tuple
from lollms.utilities import PackageManager
from ascii_colors import trace_exception

# Ensure pyautogui is installed
if not PackageManager.check_package_installed("pyautogui"):
    PackageManager.install_package("pyautogui")

# Now we can import the library
import pyautogui
import webbrowser
import time
import numpy as np
from lollms.utilities import PackageManager

if not PackageManager.check_package_installed("cv2"):
    PackageManager.install_package("opencv-python")
import cv2
from ascii_colors import ASCIIColors

def capture_screenshot() -> np.ndarray:
    """Capture a screenshot of the current screen."""
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot

def template_matching(screenshot: np.ndarray, template_path: str, threshold: float = 0.8) -> Tuple[int, int, int, int]:
    """Perform template matching to find the object in the screenshot."""
    template = cv2.imread(str(template_path), cv2.IMREAD_COLOR)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    ASCIIColors.blue(f"Searching results:{max_val}")

    if max_val >= threshold:
        (startX, startY) = max_loc
        endX = startX + template.shape[1]
        endY = startY + template.shape[0]
        return (startX, startY, endX, endY)
    else:
        return None

def runway_ml_gen_2_video_creator(prompt: str) -> str:
    """
    Opens the Luma AI Dream Machine webpage, navigates to the input section, and inputs a text prompt to create a video.
    If the user is not logged in, it prompts the user to log in.
    
    Parameters:
    prompt (str): The text prompt to generate the video.
    
    Returns:
    str: Success message or login prompt.
    """
    try:
        # Open the Luma AI Dream Machine webpage
        webbrowser.open("https://app.runwayml.com/")
        time.sleep(2)  # Wait for the page to load
        # Capture a screenshot of the browser window
        screenshot = capture_screenshot()
        # Locate the input section and type the prompt
        template_path = Path(__file__).parent/"try_gen2.png"  # Replace with the actual path to your image
        if not template_path.exists():
            raise FileNotFoundError("Input section image not found")
        # Perform template matching to find the object
        match = template_matching(screenshot, template_path)
        
        if match:
            startX, startY, endX, endY = match
            print(f"Object found at ({startX}, {startY}) with width {endX - startX} and height {endY - startY}")
            # Move the cursor to the center of the detected object
            pyautogui.moveTo(startX + (endX - startX) // 2, startY + (endY - startY) // 2)
            # Click the detected object
            pyautogui.click()
            # Type the specified text
            pyautogui.typewrite(prompt)
            pyautogui.press('enter')
            return "Video generation process started. This may take some time"
        else:
            template_path = Path(__file__).parent/"try_now.png"  # Replace with the actual path to your image
            if not template_path.exists():
                raise FileNotFoundError("Input section image not found")
            # Perform template matching to find the object
            match = template_matching(screenshot, template_path)
            
            if match:
                startX, startY, endX, endY = match
                print(f"Object found at ({startX}, {startY}) with width {endX - startX} and height {endY - startY}")
                # Move the cursor to the center of the detected object
                pyautogui.moveTo(startX + (endX - startX) // 2, startY + (endY - startY) // 2)
                # Click the detected object
                pyautogui.click()
                time.sleep(2)  # Wait for the page to load
            else:
                not_found=True
        return "Please log in to Luma AI Dream Machine to create a video."
    except Exception as e:
        trace_exception(e)
        return "Please log in to Luma AI Dream Machine to create a video."

def runway_ml_gen_2_video_creator_function() -> Dict:
    return {
        "function_name": "runway_ml_gen_2_video_creator",
        "function": runway_ml_gen_2_video_creator,
        "function_description": "Creates a video from a text prompt using Luma AI Dream Machine.",
        "function_parameters": [{"name": "prompt", "type": "str"}]
    }
