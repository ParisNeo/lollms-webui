# Lollms function call definition file
# Here you need to import any necessary imports depending on the function requested by the user
# exemple import math

# ascii_colors offers advanced console coloring and bug tracing
from ascii_colors import trace_exception
import pipmaster as pm
pm.ensure_packages({"pyautogui":""})

# now we can import the library
import pyautogui

# here is the core of the function to be built
def move_mouse_to_position(x: int, y: int) -> str:
    try:
        # Move the mouse to the specified (x, y) position
        pyautogui.moveTo(x, y)
        
        # Return a success message
        return f"Mouse moved to position ({x}, {y}) successfully."
    except Exception as e:
        return trace_exception(e)

# Here is the metadata function that should have the name in format function_name_function
def move_mouse_to_position_function():
    screen_width, screen_height = pyautogui.size()
    return {
        "function_name": "move_mouse_to_position", # The function name in string
        "function": move_mouse_to_position, # The function to be called
        "function_description": f"Moves the mouse to a specific position on the screen. The screen resolution is {screen_width} {screen_height}", # Description of the function
        "function_parameters": [{"name": "x", "type": "int"}, {"name": "y", "type": "int"}] # The set of parameters
    }



# here is the core of the function to be built
def press_mouse_button(button: str) -> str:
    try:
        # Simulate a mouse button press
        pyautogui.mouseDown(button=button)
        pyautogui.mouseUp(button=button)
        
        # Return a success message
        return f"Mouse button '{button}' pressed successfully."
    except Exception as e:
        return trace_exception(e)

# Here is the metadata function that should have the name in format function_name_function
def press_mouse_button_function():
    return {
        "function_name": "press_mouse_button", # The function name in string
        "function": press_mouse_button, # The function to be called
        "function_description": "Simulates a press of a mouse button.", # Description of the function
        "function_parameters": [{"name": "button", "type": "str"}] # The set of parameters
    }

# here is the core of the function to be built
def type_text(text: str) -> str:
    try:
        # Type the specified text
        pyautogui.typewrite(text)
        
        # Return a success message
        return f"Text '{text}' typed successfully."
    except Exception as e:
        return trace_exception(e)

# Here is the metadata function that should have the name in format function_name_function
def type_text_function():
    return {
        "function_name": "type_text", # The function name in string
        "function": type_text, # The function to be called
        "function_description": "Types the specified text.", # Description of the function
        "function_parameters": [{"name": "text", "type": "str"}] # The set of parameters
    }