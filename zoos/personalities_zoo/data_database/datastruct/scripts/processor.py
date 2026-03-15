"""
project: lollms
personality: # Place holder: Personality name 
Author: # Place holder: creator name 
description: # Place holder: personality description
"""
from lollms.types import MSG_OPERATION_TYPE
from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality
from lollms.utilities import PackageManager
import subprocess
from typing import Callable, Any
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails

try:
    if not PackageManager.check_package_installed("sqlite3"):
        PackageManager.install_package("sqlite3")
    import sqlite3
except Exception as ex:
    pass


import sqlite3

class DBToText:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def get_tables(self):
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        self.cursor.execute(query)
        return [i[0] for i in self.cursor.fetchall()]

    def get_table_structure(self, table_name):
        query = f"PRAGMA table_info({table_name})"
        self.cursor.execute(query)
        return [dict(zip(["name", "type", "notnull", "default_value", "pk"], i)) for i in self.cursor.fetchall()]

    def get_table_content(self, table_name):
        query = f"SELECT * FROM {table_name}"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def convert_to_text(self):
        full_report = ""
        self.cursor.execute("PRAGMA database_list")
        db_name = self.cursor.fetchone()[1]
        full_report += "Database report for: " + db_name + "\n"
        full_report += "\n"

        tables = self.get_tables()
        for table in tables:
            full_report += "Table: " + table + "\n"
            structure = self.get_table_structure(table)
            full_report += "Columns:\n"
            for col in structure:
                col_str = str(col).replace("'", "").replace(",", "=")
                full_report += "- " + col_str + "\n"
            full_report += "Data:\n"
            content = self.get_table_content(table)
            for row in content:
                content_str = ", ".join([str(cell) for cell in row])
                full_report += "  - " + content_str + "\n"
            full_report += "\n"
        
        return full_report


# Helper functions
class Processor(APScript):
    """
    A class that processes model inputs and outputs.

    Inherits from APScript.
    """
    def __init__(
                 self, 
                 personality: AIPersonality,
                 callback = None,
                ) -> None:
        
        self.callback = None
        # Example entries
        #       {"name":"make_scripted","type":"bool","value":False, "help":"Makes a scriptred AI that can perform operations using python script"},
        #       {"name":"make_scripted","type":"bool","value":False, "help":"Makes a scriptred AI that can perform operations using python script"},
        # Supported types:
        # str, int, float, bool, list
        # options can be added using : "options":["option1","option2"...]        
        personality_config_template = ConfigTemplate(
            [
            ]
            )
        personality_config_vals = BaseConfig.from_template(personality_config_template)

        personality_config = TypedConfig(
            personality_config_template,
            personality_config_vals
        )
        super().__init__(
                            personality,
                            personality_config,
                            [
                                {
                                    "name": "idle",
                                    "commands": { # list of commands (don't forget to add these to your config.yaml file)
                                        "build_database":self.build_database,
                                        "populate_database":self.populate_database,
                                        "help":self.help,
                                    },
                                    "default": None
                                },                           
                            ],
                            callback=callback
                        )
        
    def install(self):
        super().install()
        if not PackageManager.check_package_installed("sqlite3"):
            PackageManager.install_package("sqlite3")
        # requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Install dependencies using pip from requirements.txt
        # subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])      
        ASCIIColors.success("Installed successfully")        

    def build_database(self, prompt="", full_context="", client:Client=None):
        if len(self.personality.text_files)==0:
            self.personality.InfoMessage("Please upload some files before starting")
            return
        
        self.new_message("")
        full_text = ""
        for file in self.personality.text_files:
            try:
                full_text += GenericDataLoader.read_file(file)
            except:
                self.error(f"Couldn't load file {file}")
        data_information_hints = self.smart_data_extraction(full_text,
                                                            "\n".join([
                                                            "read the chunk text and use it to build a comprehansive list of relational database tables that can store those information.",
                                                            "Each table should contain fields.",
                                                            "The objective is that those tables can store all relevant data from the chunk.",
                                                            "The output must be a structured text that discribes the tables, their fields and the links."
                                                            "If the chunk contains multiple redundant tables representations of the same thing, then fuse them into a single table.",
                                                            "Make sure to keep all the fields needed to store the data."
                                                            ]),
                                                            "\n".join([
                                                            "read the database description and build a sqlite3 database that holds those fields.",
                                                            "You need to build the tables and make sure the links are consistant with the description",
                                                            "The output must be a python code that uses sqlight3 to build the database.",
                                                            "Make sure your answer is placed inside a python markdown tag.",
                                                            "sqlite is already installed on the hosted PC.",
                                                            "Only answer with the code without explanation.",
                                                            "Only provide a single fully functional python code to build the database.",
                                                            "Do not provide any code for populating the database.",
                                                            "The database should be named data.db"
                                                            ]),                                                            
                                                            "Doc",
                                                            callback=self.sink).replace("\_","_")
        self.set_message_content(data_information_hints)
        codes = self.extract_code_blocks(data_information_hints)
        for code in codes:
            if code["type"].lower()=="python":
                output = self.execute_python(code["content"], client.discussion_path, "database_builder.py")
                self.new_message(output)

    def populate_database(self, prompt="", full_context="", client:Client=None):
        if len(self.personality.text_files)==0:
            self.personality.InfoMessage("Please upload some files before starting")
        self.new_message("")
        #db_file = "data.db"

        db2txt = DBToText(client.discussion_path/"data.db")

        full_text = ""
        for file in self.personality.text_files:
            try:
                full_text += GenericDataLoader.read_file(file)
            except:
                self.error(f"Couldn't load file {file}")

        data_information_hints = self.smart_data_extraction("{self.config.start_header_id_template}Database structure:\n"+db2txt.convert_to_text()+"{self.config.separator_template}{self.config.start_header_id_template}Document data chunk:"+full_text,
                                                            "read the chunk text and depending on the database described earlier, extract data that can be put inside the database. If no data needs to be put in the database, just respond with empty output. If some data needs to be added to the database, then return a description to which table should an entry be added and with which parameters. ",
                                                            "\n".join([
                                                            "Use the data from the chunk to populate the database. The output should be python code",
                                                            "The output must be a python code that uses sqlight3 to build the database.",
                                                            "Make sure your answer is placed inside a python markdown tag.",
                                                            "sqlite is already installed on the hosted PC.",
                                                            "Only answer with the code without explanation.",
                                                            "Only provide a single fully functional python code to build the database.",
                                                            "Do not provide any code for populating the database.",
                                                            "The database should is named data.db"
                                                            ]),"Doc",callback=self.sink).replace("\_","_")
        
        self.set_message_content(data_information_hints)
        codes = self.extract_code_blocks(data_information_hints)
        for code in codes:
            if code["type"].lower()=="python":
                output = self.execute_python(code["content"], client.discussion_path, "database_builder.py")
                self.new_message(output)

    def help(self, prompt="", full_context=""):
        self.set_message_content(self.personality.help)
    
    def add_file(self, path, client, callback=None):
        """
        Here we implement the file reception handling
        """
        super().add_file(path, client, callback)

    def run_workflow(self,  context_details:LollmsContextDetails=None, client:Client=None,  callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, AIPersonality| None], bool]=None):
        """
        This function generates code based on the given parameters.

        Args:
            context_details (dict): A dictionary containing the following context details for code generation:
                - conditionning (str): The conditioning information.
                - documentation (str): The documentation information.
                - knowledge (str): The knowledge information.
                - user_description (str): The user description information.
                - discussion_messages (str): The discussion messages information.
                - positive_boost (str): The positive boost information.
                - negative_boost (str): The negative boost information.
                - current_language (str): The force language information.
                - fun_mode (str): The fun mode conditionning text
                - ai_prefix (str): The AI prefix information.
            client_id: The client ID for code generation.
            callback (function, optional): The callback function for code generation.

        Returns:
            None
        """
        prompt = context_details.prompt
        previous_discussion_text = context_details.discussion_messages
        self.personality.info("Generating")
        self.callback = callback
        out = self.fast_gen(previous_discussion_text)
        self.set_message_content(out)
        return out

