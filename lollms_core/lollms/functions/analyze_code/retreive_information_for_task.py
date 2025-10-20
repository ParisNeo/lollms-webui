# Lollms function call definition file
from functools import partial
from typing import List, Dict, Union
from lollms.utilities import PackageManager
from lollms.personality import APScript
from ascii_colors import trace_exception
from pathlib import Path
import sqlite3
import json 
# Ensure required packages are installed
if not PackageManager.check_package_installed("sqlite3"):
    PackageManager.install_package("sqlite3")

def retrieve_information_for_task(project_path: str, task_description: str, llm: APScript) -> Union[str, Dict[str, str]]:
    """
    Retrieves information from the database to perform a task given by the user.
    
    Args:
        project_path (str): The path to the project directory.
        task_description (str): The description of the task to perform.
        llm (APScript): The language model instance for generating SQL queries.
    
    Returns:
        Union[str, Dict[str, str]]: A string containing relevant information or an error message.
    """
    try:
        db_path = Path(project_path) / "project_info.db"
        
        # Validate the database path
        if not db_path.exists() or not db_path.is_file():
            return "Invalid database path."

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Retrieve the list of classes and their descriptions
        cursor.execute("SELECT name, docstring FROM classes")
        classes = cursor.fetchall()

        # Format the classes into a string
        classes_text = "\n".join([f"Class: {cls[0]}, Description: {cls[1]}" for cls in classes])

        # Ask the LLM which classes are needed for the task
        prompt = f"{llm.personality.config.start_header_id_template}{llm.personality.config.system_message_template}{llm.personality.config.end_header_id_template}" \
                 f"Given the following list of classes and their descriptions:\n" \
                 f"{classes_text}\n\n" \
                 f"Task description: {task_description}\n\n" \
                 f"{llm.personality.config.start_header_id_template}instructions{llm.personality.config.end_header_id_template}" \
                 f"Which classes are needed to perform the task? List the class names.\n" \
                 f"Answer in form of a json list inside a json markdown tag.\n" \
                 f"{llm.personality.config.start_header_id_template}assistant{llm.personality.config.end_header_id_template}"

        needed_classes = llm.fast_gen(prompt, callback=llm.sink).strip()
        needed_classes = llm.extract_code_blocks(needed_classes)
        if len(needed_classes)>0:
            needed_classes = json.loads(needed_classes[0]["content"])
            # Retrieve the relevant information for the needed classes
            class_info = {}
            for class_name in needed_classes:
                cursor.execute("SELECT * FROM classes WHERE name = ?", (class_name,))
                class_info[class_name] = cursor.fetchone()

            # Retrieve the project description and structure
            cursor.execute("SELECT name, description FROM project_info")
            project_info = cursor.fetchone()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            conn.close()

            # Format the results into a string
            result_text = f"Project Name: {project_info[0]}\nProject Description: {project_info[1]}\n\n"
            result_text += "Project Structure:\n" + "\n".join([table[0] for table in tables]) + "\n\n"
            result_text += "Needed Classes Information:\n"
            for class_name, info in class_info.items():
                result_text += f"Class: {class_name}\n"
                result_text += f"Description: {info[2]}\n"
                result_text += f"Methods: {info[4]}\n"
                result_text += f"Static Methods: {info[5]}\n\n"

            return result_text.strip()
        else:
            return "Failed to ask the llm"        
    except Exception as e:
        return str(e)
    
def retrieve_information_for_task_function(project_path, llm):
    return {
        "function_name": "retrieve_information_for_task",
        "function": partial(retrieve_information_for_task, project_path=project_path, llm=llm),
        "function_description": "Retrieves information from the database to perform a task given by the user.",
        "function_parameters": [
            {"name": "task_description", "type": "str", "description":"a description of "}
        ]
    }