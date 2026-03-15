import re
import pipmaster as pm

from bs4 import BeautifulSoup
def compress_js(js_code):
    # Patterns to match function, class, and variable declarations
    function_pattern = r"function\s+(\w+)\s*\(([^)]*)\)"
    class_pattern = r"class\s+(\w+)\s*{([^}]*)}"
    variable_pattern = r"var\s+(\w+)|let\s+(\w+)|const\s+(\w+)"
    
    # Find all matches in the JS code
    functions = re.findall(function_pattern, js_code)
    classes = re.finditer(class_pattern, js_code, re.DOTALL)  # Use finditer for class bodies
    variables = re.findall(variable_pattern, js_code)

    # Compress information
    compressed = []
    
    for func in functions:
        compressed.append(f"Function: {func[0]}({func[1]})")
    
    for cls in classes:
        class_name = cls.group(1)
        class_body = cls.group(2)
        compressed.append(f"Class: {class_name}")
        
        # Attempt to find member functions and properties within class body
        member_functions = re.findall(r"(\w+)\s*\(([^)]*)\)\s*{", class_body)
        for member in member_functions:
            compressed.append(f"  Member Function: {member[0]}({member[1]})")
        
        # Simple attempt to find properties (this is very basic and might not catch all cases)
        properties = re.findall(r"this\.(\w+)\s*=", class_body)
        for prop in properties:
            compressed.append(f"  Property: {prop}")

    for var in variables:
        # Variables can be declared with var, let, or const
        var_name = var[0] or var[1] or var[2]
        compressed.append(f"Variable: {var_name}")
    
    # Return compressed version as a single string
    return '\n'.join(compressed)

def compress_python(py_code):
    # Patterns to match function, class declarations, and possibly variables
    function_pattern = r"def\s+(\w+)\s*\(([^)]*)\):"
    class_pattern = r"class\s+(\w+)\s*:\s*\n((?:\s{4,}.+\n)+)"  # Assuming 4 spaces for indentation
    variable_pattern = r"(\w+)\s*=\s*.+"
    
    # Find all matches in the Python code
    functions = re.findall(function_pattern, py_code)
    classes = re.finditer(class_pattern, py_code, re.DOTALL)
    variables = re.findall(variable_pattern, py_code)

    class_member_functions = set()  # To store class member function names
    compressed = []

    for cls in classes:
        class_name = cls.group(1)
        class_body = cls.group(2)
        compressed.append(f"Class: {class_name}")
        
        # Attempt to find member functions within class body
        member_functions = re.findall(r"def\s+(\w+)\s*\(([^)]*)\):", class_body)
        for member in member_functions:
            class_member_functions.add(member[0])  # Add member function name to the set
            compressed.append(f"  Member Function: {member[0]}({member[1]})")
        
        # Not extracting properties as Python's properties are not as straightforward as JavaScript's
    
    # Filter out functions that are class members before adding them to the compressed output
    for func in functions:
        if func[0] not in class_member_functions:
            compressed.append(f"Function: {func[0]}({func[1]})")

    for var in variables:
        compressed.append(f"Variable: {var[0]}")
    
    # Return compressed version as a single string
    return '\n'.join(compressed)

def compress_html(html_doc):

    # Initialize BeautifulSoup with the provided HTML document
    soup = BeautifulSoup(html_doc, 'html.parser')
    
    # This dictionary will store our findings: tags as keys and lists of ids/classes as values
    elements_summary = {}
    
    # For simplicity, let's focus on a few common tags, but you can expand this list
    tags_of_interest = ['div', 'a', 'button', 'img', 'span']
    
    for tag in tags_of_interest:
        elements = soup.find_all(tag)
        for element in elements:
            # Initialize the entry in the dictionary if it does not exist
            if tag not in elements_summary:
                elements_summary[tag] = {'ids': [], 'classes': []}
            
            # If the element has an id, add it to the list
            if element.get('id'):
                elements_summary[tag]['ids'].append(element.get('id'))
            
            # If the element has classes, extend the list with them
            if element.get('class'):
                elements_summary[tag]['classes'].extend(element.get('class'))
    
    # Remove duplicates by converting lists to sets and back to lists
    for tag, info in elements_summary.items():
        info['ids'] = list(set(info['ids']))
        info['classes'] = list(set(info['classes']))
    
    # Generate a simplified summary or 'compressed' representation of the HTML elements
    compressed_output = []
    for tag, info in elements_summary.items():
        if info['ids']:
            compressed_output.append(f"{tag.upper()} IDs: {', '.join(info['ids'])}")
        if info['classes']:
            compressed_output.append(f"{tag.upper()} Classes: {', '.join(info['classes'])}")
    
    return '\n'.join(compressed_output)

if __name__=="__main__":
    # Example JavaScript code with class members
    js_code = """
    function add(a, b) {
        return a + b;
    }

    class Rectangle {
        constructor(height, width) {
            this.height = height;
            this.width = width;
        }
        area() {
            return this.height * this.width;
        }
    }

    let x = 5;
    const y = "Hello";
    var z = true;
    """

    compressed_js = compress_js(js_code)
    print(compressed_js)

    # Example Python code with class members
    py_code = """
    def add(a, b):
        return a + b

    class Rectangle:
        def __init__(self, height, width):
            self.height = height
            self.width = width
        
        def area(self):
            return self.height * self.width

    x = 5
    y = "Hello"
    z = True
    """

    compressed_py = compress_python(py_code)
    print(compressed_py)