from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails
from datetime import datetime
import yaml
from typing import List
from ascii_colors import ASCIIColors, trace_exception
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
import math

# No external modules needed for this function

class Calculator(FunctionCall):
    def __init__(self, app: LollmsApplication, client: Client):
        super().__init__("calculator", app, FunctionType.CLASSIC, client)

    def execute(self, context: LollmsContextDetails, *args, **kwargs):
        expression = kwargs.get("expression", "0")
        try:
            # Define allowed math functions and constants
            safe_dict = {
                'cos': math.cos,
                'sin': math.sin,
                'tan': math.tan,
                'sqrt': math.sqrt,
                'log': math.log,
                'exp': math.exp,
                'pi': math.pi,
                'e': math.e,
                'abs': abs,
                'round': round,
                'floor': math.floor,
                'ceil': math.ceil
            }
            
            # Evaluate the expression with restricted namespace
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            return f"The result of '{expression}' is: {result}"
        except Exception as e:
            return f"An error occurred: {str(e)}"