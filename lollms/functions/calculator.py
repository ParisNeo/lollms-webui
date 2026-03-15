import sympy as sp
import ast
import math
import operator
import re
import threading
import logging
from typing import Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimeoutException(Exception):
    pass

def is_valid_expression(expression: str) -> bool:
    allowed_chars = r'^[0-9+\-*/^()., a-zA-Z]+$'
    return bool(re.match(allowed_chars, expression))

def is_expression_too_complex(expression: str, max_length: int = 100, max_operations: int = 10) -> bool:
    if len(expression) > max_length:
        return True
    
    operation_count = sum(expression.count(op) for op in '+-*/^')
    return operation_count > max_operations

def calculate(expression: str, timeout: int = 5) -> Union[float, str]:
    logger.info(f"Calculating expression: {expression}")
    
    if not is_valid_expression(expression):
        logger.warning(f"Invalid characters in expression: {expression}")
        return "Invalid characters in expression"
    
    if is_expression_too_complex(expression):
        logger.warning(f"Expression too complex: {expression}")
        return "Expression too complex"

    result = []
    exception = []

    def calculate_with_timeout():
        try:
            # Define allowed operations
            allowed_ops = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.USub: operator.neg,
            }

            # Define allowed functions from math module
            allowed_functions = {
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'sqrt': math.sqrt,
                'log': math.log,
                'exp': math.exp,
                # Add more functions as needed
            }

            def eval_expr(node):
                if isinstance(node, ast.Num):
                    return node.n
                elif isinstance(node, ast.Name):
                    if node.id in allowed_functions:
                        return allowed_functions[node.id]
                    raise ValueError(f"Unknown variable: {node.id}")
                elif isinstance(node, ast.BinOp):
                    op = type(node.op)
                    if op not in allowed_ops:
                        raise ValueError(f"Unsupported operation: {op}")
                    return allowed_ops[op](eval_expr(node.left), eval_expr(node.right))
                elif isinstance(node, ast.UnaryOp):
                    op = type(node.op)
                    if op not in allowed_ops:
                        raise ValueError(f"Unsupported operation: {op}")
                    return allowed_ops[op](eval_expr(node.operand))
                elif isinstance(node, ast.Call):
                    if not isinstance(node.func, ast.Name) or node.func.id not in allowed_functions:
                        raise ValueError(f"Unsupported function: {node.func.id}")
                    return allowed_functions[node.func.id](*[eval_expr(arg) for arg in node.args])
                else:
                    raise ValueError(f"Unsupported node type: {type(node)}")

            tree = ast.parse(expression, mode='eval')
            result.append(eval_expr(tree.body))
        except Exception as e:
            exception.append(str(e))

    calculation_thread = threading.Thread(target=calculate_with_timeout)
    calculation_thread.start()
    calculation_thread.join(timeout)

    if calculation_thread.is_alive():
        logger.warning(f"Calculation timed out: {expression}")
        return "Calculation timed out"

    if exception:
        logger.error(f"Error during calculation: {exception[0]}")
        return exception[0]

    if result:
        logger.info(f"Calculation result: {result[0]}")
        return result[0]

    return "Unexpected error occurred"



    

def calculate_function(processor, client):
    return {
        "function_name": "calculate",
        "function": calculate,
        "function_description": "Whenever you need to perform mathematic computations, you can call this function with the math expression and you will get the answer.",
        "function_parameters": [{"name": "expression", "type": "str"}]                
    }


if __name__ == "__main__":
    # Test cases
    test_cases = [
        ("2 + 2", 4),
        ("cos(0)", 1.0),
        ("sin(pi / 2)", 1.0),
        ("sqrt(4)", 2.0),
        ("degrees(pi)", 180.0),
        ("radians(180)", 3.14159),  # Approximately π
        ("2 + 2 and ().__class__.__base__.__subclasses__()[108].load_module('os').system('echo a > AAA')", "An error occurred while evaluating the expression."),
        ("1 / 0", "An error occurred while evaluating the expression."),  # Division by zero
        ("2 ** 3", 8),  # Exponentiation
        ("log(1)", 0),  # Logarithm base e
        ("exp(0)", 1),  # Exponential function
        ("pi", round(float(sp.pi), 5)),  # Pi constant rounded to 5 decimal places
    ]
    for expression, expected in test_cases:
        print(f"Testing expression: {expression}")
        result = calculate(expression)
        print(f"Result: {result} | Expected: {expected}")
        # Check if both are strings and equal
        if isinstance(result, str) and isinstance(expected, str):
            print("Test Passed!" if result == expected else "Test Failed!")
        # Check if both are floats and compare rounded values
        elif isinstance(result, float) and isinstance(expected, (float, int)):
            print("Test Passed!" if round(result, 5) == round(expected, 5) else "Test Failed!")
        else:
            print("Test Failed!")
        print()