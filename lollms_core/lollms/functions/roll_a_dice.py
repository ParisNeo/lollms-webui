# Lollms function call definition file
# Here you need to import any necessary imports depending on the function requested by the user
import random

# ascii_colors offers advanced console coloring and bug tracing
from ascii_colors import trace_exception

# here is the core of the function to be built
def roll_a_dice() -> int:
    try:
        # handle exceptions

        # Perform dice roll
        result = random.randint(1, 6)
        
        # Return the dice roll result
        return result
    except Exception as e:
        return trace_exception(e)
    

#Here is the metadata function that should have the name in format function_name_function
def roll_a_dice_function():
    return {
        "function_name": "roll_a_dice", # The function name in string
        "function": roll_a_dice, # The function to be called
        "function_description": "Returns a random dice roll result between 1 and 6.", # Description of the function
        "function_parameters": [] # No parameters needed for this function
    }
