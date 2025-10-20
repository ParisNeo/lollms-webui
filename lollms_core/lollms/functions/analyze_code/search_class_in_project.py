from typing import Optional, Union
from pathlib import Path
import sqlite3
import difflib
import json

from ascii_colors import trace_exception
from functools import partial

def search_class_in_project(class_name: str, db_path: Union[str, Path]) -> Optional[str]:
    """
    Searches for a specific class by name in the project database and returns detailed information.

    Args:
        db_path (Union[str, Path]): The path to the project database file.
        class_name (str): The name of the class to search for.

    Returns:
        Optional[str]: A string with detailed information about the class, or None if not found.
    """
    try:
        db_path = Path(db_path)
        if not db_path.exists():
            return "Database file does not exist."

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch all class names to find the closest match
        cursor.execute("SELECT id, name FROM classes")
        classes = cursor.fetchall()
        class_names = [name for _, name in classes]
        closest_matches = difflib.get_close_matches(class_name, class_names, n=1, cutoff=0.1)

        if not closest_matches:
            return f"No class found with a name similar to '{class_name}'."

        closest_class_name = closest_matches[0]
        cursor.execute("SELECT id, file_id, name, docstring, core FROM classes WHERE name = ?", (closest_class_name,))
        class_info = cursor.fetchone()

        if not class_info:
            return f"No class found with the name '{closest_class_name}'."

        class_id, file_id, name, docstring, core = class_info

        # Fetch the file path
        cursor.execute("SELECT path FROM files WHERE id = ?", (file_id,))
        file_path = cursor.fetchone()[0]

        # Fetch methods of the class
        cursor.execute("SELECT name, docstring, parameters FROM methods WHERE class_id = ?", (class_id,))
        methods = cursor.fetchall()

        # Construct the detailed information string
        details = f"Class: {name}\n"
        details += f"File: {file_path}\n"
        details += f"Description: {docstring}\n\n"
        details += "Methods:\n"
        for method_name, method_docstring, method_parameters in methods:
            details += f"  - {method_name}({', '.join([f'{param[0]}: {param[1]}' for param in json.loads(method_parameters)])})\n"
            details += f"    Description: {method_docstring}\n"

        conn.close()
        return details

    except Exception as e:
        return trace_exception(e)


def search_class_in_project_function(project_path):
    return {
        "function_name": "create_project_database",
        "function": partial(search_class_in_project, project_path=project_path),
        "function_description": "Searches for a specific class by name in the project database and returns detailed information.",
        "function_parameters": [{"name":"class_name", "type":"str", "description":"Name of the class to search"}]
    }


if __name__ == "__main__":
    # Example usage
    db_path = "path/to/project_info.db"
    class_name = "MyClass"
    print(search_class_in_project(db_path, class_name))
