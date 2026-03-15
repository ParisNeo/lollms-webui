from functools import partial
from typing import List, Dict, Union, Any
from lollms.utilities import PackageManager
from lollms.personality import APScript
from ascii_colors import trace_exception
from pathlib import Path
import sqlite3
import ast
import json
import pipmaster as pm

pm.ensure_packages({"sqlite3":""})

def create_project_database(project_path: Union[str, Path], max_summary_size: str = 512, llm: APScript = None) -> str:
    """
    Creates a database containing structured information about a Python project.

    Args:
        project_path (Union[str, Path]): The path to the Python project directory.
        llm (Any): The language model instance for text summarization.

    Returns:
        str: Path to the created database file.
    """
    try:
        project_path = Path(project_path)
        
        # Validate the project path
        if not project_path.exists() or not project_path.is_dir():
            return "Invalid project path."

        # Create a SQLite database
        db_path = project_path / "project_info.db"
        if db_path.exists():
            db_path.unlink()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''CREATE TABLE IF NOT EXISTS files (
                            id INTEGER PRIMARY KEY,
                            path TEXT NOT NULL
                          )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS functions (
                            id INTEGER PRIMARY KEY,
                            file_id INTEGER,
                            name TEXT NOT NULL,
                            docstring TEXT,
                            parameters TEXT,
                            core TEXT,
                            FOREIGN KEY (file_id) REFERENCES files (id)
                          )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS classes (
                            id INTEGER PRIMARY KEY,
                            file_id INTEGER,
                            name TEXT NOT NULL,
                            docstring TEXT,
                            core TEXT,
                            FOREIGN KEY (file_id) REFERENCES files (id)
                          )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS methods (
                            id INTEGER PRIMARY KEY,
                            class_id INTEGER,
                            name TEXT NOT NULL,
                            docstring TEXT,
                            parameters TEXT,
                            core TEXT,
                            FOREIGN KEY (class_id) REFERENCES classes (id)
                          )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS project_info (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            description TEXT
                          )''')

        # Extract project name
        project_name = project_path.name

        # Summarize README.md if it exists
        readme_path = project_path / "README.md"
        if readme_path.exists():
            with open(readme_path, "r", encoding="utf-8") as readme_file:
                readme_content = readme_file.read()
                structure = "\n".join([str(p.relative_to(project_path)) for p in project_path.rglob("*")])
                readme_content += f"## Project Structure:\n{structure}"
                project_description = llm.summarize_text(readme_content, "Build a comprehensive description of this project from the available information", max_generation_size=max_summary_size, callback=llm.sink)
        else:
            # Construct a description based on the project structure
            structure = "\n".join([str(p.relative_to(project_path)) for p in project_path.rglob("*")])
            constructed_text = f"Project Name: {project_name}\n\nProject Structure:\n{structure}"
            project_description = llm.summarize_text(constructed_text, "Build a comprehensive description of this project from the available information", max_generation_size=max_summary_size, callback=llm.sink)

        # Insert project information into the database
        cursor.execute("INSERT INTO project_info (name, description) VALUES (?, ?)", (project_name, project_description))

        # Traverse the project directory and extract information
        for py_file in project_path.rglob("*.py"):
            relative_path = py_file.relative_to(project_path)
            with open(py_file, "r", encoding="utf-8") as file:
                content = file.read()
                tree = ast.parse(content)
                file_id = cursor.execute("INSERT INTO files (path) VALUES (?)", (str(relative_path),)).lastrowid

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        parameters = [(arg.arg, arg.annotation.id if arg.annotation else None) for arg in node.args.args]
                        core = ast.get_source_segment(content, node)
                        cursor.execute("INSERT INTO functions (file_id, name, docstring, parameters, core) VALUES (?, ?, ?, ?, ?)",
                                       (file_id, node.name, ast.get_docstring(node), json.dumps(parameters), core))
                    elif isinstance(node, ast.ClassDef):
                        methods = []
                        static_methods = []
                        core = ast.get_source_segment(content, node)
                        class_id = cursor.execute("INSERT INTO classes (file_id, name, docstring, core) VALUES (?, ?, ?, ?)",
                                                  (file_id, node.name, ast.get_docstring(node), core)).lastrowid
                        for class_node in node.body:
                            if isinstance(class_node, ast.FunctionDef):
                                parameters = [(arg.arg, arg.annotation.id if arg.annotation else None) for arg in class_node.args.args]
                                method_core = ast.get_source_segment(content, class_node)
                                cursor.execute("INSERT INTO methods (class_id, name, docstring, parameters, core) VALUES (?, ?, ?, ?, ?)",
                                               (class_id, class_node.name, ast.get_docstring(class_node), json.dumps(parameters), method_core))

        # Commit changes and close the connection
        conn.commit()
        conn.close()
        
        return str(db_path)
        
    except Exception as e:
        return trace_exception(e)

def create_project_database_function(project_path, llm):
    return {
        "function_name": "create_project_database",
        "function": partial(create_project_database, project_path=project_path, llm=llm),
        "function_description": "Creates a database containing structured information about a Python project.",
        "function_parameters": []
    }
