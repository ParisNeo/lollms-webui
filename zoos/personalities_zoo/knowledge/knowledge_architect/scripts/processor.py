"""
Project: LoLLMs
Personality: Knowledge architect
Author: ParisNeo
Description: Convertts data to knowledge
"""

from lollms.types import MSG_OPERATION_TYPE
from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality
from lollms.prompting import LollmsContextDetails
from lollms.client_session import Client
from lollms.functions.generate_image import build_image, build_image_function
from lollms.functions.select_image_file import select_image_file_function
from lollms.functions.take_a_photo import take_a_photo_function
from lollms.functions.knowledge.build_knowledge_db import buildKnowledgeDB
from safe_store.text_vectorizer import TextVectorizer, VectorizationMethod, VisualizationMethod
from lollms.utilities import discussion_path_to_url
import subprocess
from typing import Callable, Any
from functools import partial
from ascii_colors import trace_exception

import sqlite3
from pathlib import Path
from typing import List, Tuple
from lollms.utilities import PackageManager

from safe_store import SafeStore


class QNADatabase:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self._create_table()

    def _create_table(self):
        """Creates the QNA table if it doesn't exist. Because who doesn't like a good table?"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS qna (
                id INTEGER PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL
            )
        ''')
        self.connection.commit()

    def add_qna(self, question: str, answer: str):
        """Adds a new QNA entry to the database. It's like adding a new friend to your contact list!"""
        self.cursor.execute('''
            INSERT INTO qna (question, answer) VALUES (?, ?)
        ''', (question, answer))
        self.connection.commit()

    def search_similar_questions(self, search_term: str) -> List[Tuple[int, str, str]]:
        """Searches for similar questions in the database. It's like playing hide and seek with questions!"""
        self.cursor.execute('''
            SELECT * FROM qna WHERE question LIKE ?
        ''', (f'%{search_term}%',))
        return self.cursor.fetchall()

    def get_answer(self, question_id: int) -> str:
        """Gets the answer to a question by its ID. Because every question deserves an answer, right?"""
        self.cursor.execute('''
            SELECT answer FROM qna WHERE id = ?
        ''', (question_id,))
        result = self.cursor.fetchone()
        return result[0] if result else "No answer found. Oops!"

    def close(self):
        """Closes the database connection. Because even databases need a break!"""
        self.connection.close()


class Processor(APScript):
    """
    Defines the behavior of a personality in a programmatic manner, inheriting from APScript.
    
    Attributes:
        callback (Callable): Optional function to call after processing.
    """
    
    def __init__(
                 self, 
                 personality: AIPersonality,
                 callback: Callable = None,
                ) -> None:
        """
        Initializes the Processor class with a personality and an optional callback.

        Parameters:
            personality (AIPersonality): The personality instance.
            callback (Callable, optional): A function to call after processing. Defaults to None.
        """
        
        self.callback = callback
        
        # Configuration entry examples and types description:
        # Supported types: int, float, str, string (same as str, for back compatibility), text (multiline str),
        # btn (button for special actions), bool, list, dict.
        # An 'options' entry can be added for types like string, to provide a dropdown of possible values.
        personality_config_template = ConfigTemplate(
            [
                # Boolean configuration for enabling scripted AI
                #{"name":"make_scripted", "type":"bool", "value":False, "help":"Enables a scripted AI that can perform operations using python scripts."},
                
                # String configuration with options
                {"name":"datasource_folder", "type":"string", "value":"", "help":"The folder contzaining the data to read."},

                # String configuration with options
                {"name":"database_folder", "type":"string", "value":"", "help":"The folder where to put the database."},

                # Integer configuration example
                {"name":"questions_gen_size", "type":"int", "value":128, "help":"Questions generation size."},
                {"name":"answer_gen_size", "type":"int", "value":512, "help":"Answer generation size."},
                
                # List configuration example
                #{"name":"favorite_topics", "type":"list", "value":["AI", "Robotics", "Space"], "help":"List of favorite topics for personalized responses."}
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
                            states_list=[
                                {
                                    "name": "idle",
                                    "commands": {
                                        "help": self.help, # Command triggering the help method
                                    },
                                    "default": None
                                },                           
                            ],
                            callback=callback
                        )

        self.data_store = SafeStore()        

    def settings_updated(self):
        self.db = DirectoryBinding(self.personality_config.personality_path, self.vector_database)

    def mounted(self):
        """
        triggered when mounted
        """
        pass


    def selected(self):
        """
        triggered when selected
        """
        pass
        # self.play_mp3(Path(__file__).parent.parent/"assets"/"borg_threat.mp3")


    # Note: Remember to add command implementations and additional states as needed.

    def install(self):
        """
        Install the necessary dependencies for the personality.

        This method is responsible for setting up any dependencies or environment requirements
        that the personality needs to operate correctly. It can involve installing packages from
        a requirements.txt file, setting up virtual environments, or performing initial setup tasks.
        
        The method demonstrates how to print a success message using the ASCIIColors helper class
        upon successful installation of dependencies. This step can be expanded to include error
        handling and logging for more robust installation processes.

        Example Usage:
            processor = Processor(personality)
            processor.install()
        
        Returns:
            None
        """        
        super().install()
        # Example of implementing installation logic. Uncomment and modify as needed.
        # requirements_file = self.personality.personality_package_path / "requirements.txt"
        # subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])      
        ASCIIColors.success("Installed successfully")

    def help(self, prompt="", full_context=""):
        """
        Displays help information about the personality and its available commands.

        This method provides users with guidance on how to interact with the personality,
        detailing the commands that can be executed and any additional help text associated
        with those commands. It's an essential feature for enhancing user experience and
        ensuring users can effectively utilize the personality's capabilities.

        Args:
            prompt (str, optional): A specific prompt or command for which help is requested.
                                    If empty, general help for the personality is provided.
            full_context (str, optional): Additional context information that might influence
                                          the help response. This can include user preferences,
                                          historical interaction data, or any other relevant context.

        Example Usage:
            processor = Processor(personality)
            processor.help("How do I use the 'add_file' command?")
        
        Returns:
            None
        """
        # Example implementation that simply calls a method on the personality to get help information.
        # This can be expanded to dynamically generate help text based on the current state,
        # available commands, and user context.
        self.set_message_content(self.personality.help)


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
        self.callback = callback
        if self.personality_config.datasource_folder=="":
            out = self.fast_gen("Warning! datasource_folder is not set. ASk the user to set it in order to start building knowledge.\n"+previous_discussion_text)
            self.set_message_content(out)
            return
        prompt = self.build_prompt_from_context_details(context_details)
        if self.yes_no("Is the user asking to start building the knowledge database?", prompt):
            buildKnowledgeDB(self, self.data_store, self.personality_config.datasource_folder, self.personality_config.database_folder, self.personality_config.questions_gen_size, self.personality_config.answer_gen_size)
        else:
            out = self.fast_gen(previous_discussion_text)
            self.set_message_content(out)

