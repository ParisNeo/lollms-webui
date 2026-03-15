"""
Project: LoLLMs
Personality: Thankful mind keeper
Author: ParisNeo
Description: This personality can help you keep positive thoughts and access them in the future
"""

from lollms.types import MSG_OPERATION_TYPE
from typing import Any
from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality
from lollms.client_session import Client
from lollms.utilities import output_file_path_to_url
from lollms.functions.generate_image import build_image, build_image_function
from lollms.prompting import LollmsContextDetails
from ascii_colors import trace_exception
import subprocess
from typing import Callable, Any
from functools import partial

import sqlite3
import json
from datetime import datetime
from lollms.utilities import PackageManager, discussion_path_to_url
if not PackageManager.check_package_installed("plotly"):
    PackageManager.install_package("plotly")
if not PackageManager.check_package_installed("matplotlib"):
    PackageManager.install_package("matplotlib")
import plotly.graph_objs as go
from plotly.offline import plot
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from lollms.utilities import PackageManager, discussion_path_to_url
if not PackageManager.check_package_installed("plotly"):
    PackageManager.install_package("plotly")
if not PackageManager.check_package_installed("kaleido"):
    PackageManager.install_package("kaleido")


import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import kaleido

def create_and_save_happiness_index_plot(data, html_file_path, png_file_path):
    """
    Creates a happiness index plot from a list of tuples and saves it as HTML and PNG at specified paths.
    
    Parameters:
    - data: A list of tuples, where each tuple contains (happiness index, timestamp).
    - html_file_path: The file path where the HTML file will be saved.
    - png_file_path: The file path where the PNG file will be saved.
    """

    # Convert list of tuples into a DataFrame
    df = pd.DataFrame(data, columns=['Happiness Index', 'Timestamp'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    # Create a subplot
    fig = make_subplots(rows=1, cols=1)

    # Add a scatter plot to the subplot
    fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['Happiness Index'], mode='lines+markers', name='Happiness Index'))

    # Beautify the plot
    fig.update_layout(title='Happiness Index Over Time', xaxis_title='Time', yaxis_title='Happiness Index (%)',
                      template='plotly_dark', xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))

    # Save the plot as HTML
    fig.write_html(html_file_path)

    # Save the plot as PNG
    fig.write_image(png_file_path)

    return html_file_path, png_file_path

class GratitudeDB():
    def __init__(self, db_path):
        self.db_path = db_path
        self.create_tables()

    def _connect(self):
        """Create a new database connection."""
        return sqlite3.connect(self.db_path)

    def create_tables(self):
        """Create the tables needed for the gratitude database with AI enhanced notes and happiness index."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                raw_content TEXT NOT NULL,
                enhanced_content TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS happiness_index (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                index_value REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        conn.close()

    def add_user_profile(self, name):
        """Add a new user profile to the database."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()

    def get_user_id_by_name(self, name):
        """Get a user's ID by their name."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE name = ?', (name,))
        user_id = cursor.fetchone()
        conn.close()
        return user_id[0] if user_id else None

    def list_all_profiles(self):
        """List all user profiles."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        profiles = cursor.fetchall()
        conn.close()
        return profiles

    def remove_user_profile(self, user_id):
        """Remove a user profile by ID."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()

    def add_note(self, user_id, raw_content, enhanced_content=''):
        """Add a gratitude note for a user with an optional AI enhanced note."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notes (user_id, raw_content, enhanced_content)
            VALUES (?, ?, ?)
        ''', (user_id, raw_content, enhanced_content))
        conn.commit()
        conn.close()

    def view_notes(self, user_id):
        """View all notes for a user."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT raw_content, enhanced_content, created_at
            FROM notes
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        notes = cursor.fetchall()
        conn.close()
        return notes

    def view_last_note(self, user_id):
        """View the last note for a user."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT raw_content, enhanced_content
            FROM notes
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (user_id,))
        last_note = cursor.fetchone()
        conn.close()
        return last_note if last_note else (None, None)

    def remove_note(self, note_id):
        """Remove a note by ID."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        conn.commit()
        conn.close()

    def enhance_note(self, note_id, enhanced_content):
        """Update a note with AI enhanced content."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE notes
            SET enhanced_content = ?
            WHERE id = ?
        ''', (enhanced_content, note_id))
        conn.commit()
        conn.close()

    def add_happiness_index(self, user_id, index_value):
        """Add a happiness index entry for a user."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO happiness_index (user_id, index_value)
            VALUES (?, ?)
        ''', (user_id, index_value))
        conn.commit()
        conn.close()

    def view_happiness_index(self, user_id):
        """View happiness index history for a user."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT index_value, recorded_at
            FROM happiness_index
            WHERE user_id = ?
            ORDER BY recorded_at ASC
        ''', (user_id,))
        index_history = cursor.fetchall()
        conn.close()
        return index_history

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
                {"name":"image_generation_engine", "type":"string", "value":"", "options":["autosd","dall-e-2","dall-e-3"], "help":"The profile name of the user. Used to store progress data."},

                # String configuration with options
                {"name":"user_profile_name", "type":"string", "value":"", "help":"The profile name of the user. Used to store progress data."},
                {"name":"happiness_level", "type":"int", "value":0, "help":"Your initial happiness level styarting from 0 to 100."},
                
                # Integer configuration example
                #{"name":"max_attempts", "type":"int", "value":3, "help":"Maximum number of attempts for retryable operations."},
                
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
        self.evolution_db = self.personality.personality_output_folder/"evolution.db"
        self.user_profile_db = GratitudeDB(str(self.evolution_db))

    def get_or_create_user_profile(self):
        if self.personality_config.user_profile_name=="":
            return False
        user_id = self.user_profile_db.get_user_id_by_name(self.personality_config.user_profile_name)
        
        if user_id is None:
            # If the user doesn't exist, create a new profile with the initial level from the configuration
            initial_level = self.personality_config.happiness_level
            user_id = self.user_profile_db.add_user_profile(self.personality_config.user_profile_name)
            self.user_profile_db.add_happiness_index(user_id, self.personality_config.happiness_level)

            status_text = f"Created a new user profile for {self.personality_config.user_profile_name} with initial level {initial_level}."
        else:
            # If the user exists, fetch the current status
            status_text = f"User {self.personality_config.user_profile_name} has a happiness index of {self.personality_config.happiness_level}/100."

        # Retrieve the last AI state for the user
        ai_memory = self.user_profile_db.view_last_note(user_id)
        if ai_memory:
            status_text += " Last gratitude notes has been retrieved."
        else:
            status_text += " No previous gratitude notes found."

        return status_text

    def get_welcome(self, welcome_message:str, client):
        happiness_level = self.get_or_create_user_profile()
        if happiness_level:
            return self.fast_gen(f"{self.config.start_header_id_template}{self.config.system_message_template}{self.config.end_header_id_template}Build a better  welcome message for the user.{self.config.separator_template}{self.config.start_header_id_template}current_welcome_message: {welcome_message}{self.config.separator_template}{self.config.start_header_id_template}last happiness level: {happiness_level}{self.config.separator_template}{self.config.start_header_id_template}adapted welcome message:")
        else:
            return welcome_message+"\nI see that you did not specify a profile in my settings. Please specify a profile name.\nYou need to press my icon in the chatbar and you'll see my configuration window. Type your profile name and your level, then make a new discussion.\n"


    def update_infos(self):
        if not self.get_or_create_user_profile():
            return None, "", 0
        user_id = self.user_profile_db.get_user_id_by_name(self.personality_config.user_profile_name)
        if user_id is None:
            self.set_message_content(self.personality.welcome_message+"\nI see that you did not specify a profile in my settings. Please specify a profile name.\nYou need to press my icon in the chatbar and you'll see my configuration window. Type your profile name and your level, then make a new discussion.\n")
            return None, "", 0
        self.personality.info("Generating")
        memory_data = self.user_profile_db.view_last_note(user_id)
        happiness_index = self.user_profile_db.view_happiness_index(user_id)

        return user_id, memory_data[1], happiness_index
    
    
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
    # ----------------------- Functions to call -------------------------------

    def add_note(self, user_raw_note, ai_enhanced_note, user_id):
        self.user_profile_db.add_note(user_id, user_raw_note, ai_enhanced_note)
        return "### Note added successfully"
    
    def view_last_note(self, user_id):
        last_note = self.user_profile_db.view_last_note(user_id)
        return f"# User note:\n{last_note[0]}\n# Ai enhanced note:\n{last_note[1]}"

    def view_all_notes(self, user_id):
        all_notes = self.user_profile_db.view_notes(user_id)
        return "\n".join([f"# User note created at {last_note[2]}:\n{last_note[0]}\n# Ai enhanced note:\n{last_note[1]}" for last_note in all_notes])
    

    def add_happiness_index(self, happiness_index:int, user_id):
        self.user_profile_db.add_happiness_index(user_id,happiness_index)
        return f"# New happiness entry added to database"

    def plot_happiness_index(self, user_id, client):
        happiness_index = self.user_profile_db.view_happiness_index(user_id)
        img_path = client.discussion.discussion_folder/f"current_status_{client.discussion.current_message.id}.png"
        interactive_ui = client.discussion.discussion_folder/f"current_status_{client.discussion.current_message.id}.html"

        create_and_save_happiness_index_plot(happiness_index, interactive_ui, img_path)

        return f"<img src='{discussion_path_to_url(img_path)}'></img>\n<a href='{discussion_path_to_url(interactive_ui)}' target='_blank'>click here for an interactive version</a>"

    def build_image(self, prompt, width, height, client:Client):
        try:
            if self.personality_config.image_generation_engine=="autosd":
                if not hasattr(self, "sd"):
                    from lollms.services.tti.sd.lollms_sd import LollmsSD
                    self.step_start("Loading ParisNeo's fork of AUTOMATIC1111's stable diffusion service")
                    self.sd = LollmsSD(self.personality.app, self.personality.name, max_retries=-1,auto_sd_base_url=self.personality.config.sd_base_url)
                    self.step_end("Loading ParisNeo's fork of AUTOMATIC1111's stable diffusion service")
                file, infos = self.sd.paint(
                                prompt, 
                                "",
                                self.personality.image_files,
                                width = width,
                                height = height,
                                output_path=client.discussion.discussion_folder
                            )
            elif self.personality_config.image_generation_engine in ["dall-e-2", "dall-e-3"]:
                if not hasattr(self, "dalle"):
                    from lollms.services.tti.dalle.lollms_dalle import LollmsDalle
                    self.step_start("Loading dalle service")
                    self.dalle = LollmsDalle(self.personality.app, self.personality.config.dall_e_key, self.personality_config.image_generation_engine)
                    self.step_end("Loading dalle service")
                self.step_start("Painting")
                file = self.dalle.paint(
                                prompt, 
                                width = width,
                                height = height,
                                output_path=client.discussion.discussion_folder
                            )
                self.step_end("Painting")

            file = str(file)
            escaped_url =  discussion_path_to_url(file)
            return f'\n![]({escaped_url})'
        except Exception as ex:
            trace_exception(ex)
            return "Couldn't generate image. Make sure Auto1111's stable diffusion service is installed"


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
        # self.process_state(prompt, previous_discussion_text, callback, context_details, client)

        user_id, memory_data, happiness_index = self.update_infos()
        if user_id is None:
            self.goto_state("idle")
            self.set_message_content("Please create a profile by providing your name and happiness level in my configuration page. Just press my icon in the chatbar and give fill the form. When this is done, come back to me and we can start.")
            return
        
        context_details.extra="\n".join([
            f"{self.config.start_header_id_template}memory_data:\n"+memory_data if memory_data is not None else "",
            f"{self.config.start_header_id_template}happiness_index:\n"+str(happiness_index) if happiness_index is not None else "",
        ])

        self.function_definitions = [
            {
                "function_name": "add_note",
                "function": partial(self.add_note,user_id=user_id),
                "function_description": "Adds a gratitude note to the database.",
                "function_parameters": [{"name": "user_raw_note", "type": "str"},{"name": "ai_enhanced_note", "type": "str"}]                
            },
            {
                "function_name": "view_last_note",
                "function":  partial(self.view_last_note,user_id=user_id),
                "function_description": "Views the last note in the database.",
                "function_parameters": []                
            },
            {
                "function_name": "view_all_notes",
                "function":  partial(self.view_all_notes,user_id=user_id),
                "function_description": "Views all notes from the database.",
                "function_parameters": []                
            },
            {
                "function_name": "add_happiness_index",
                "function": partial(self.add_happiness_index,user_id=user_id),
                "function_description": "Adds a new happiness value to the happiness_index table (from 0 to 100).",
                "function_parameters": [{"name": "value", "type": "int"}]                
            },
            {
                "function_name": "plot_happiness_index",
                "function": partial(self.plot_happiness_index,user_id=user_id, client=client),
                "function_description": "Plots the happiness value over time.",
                "function_parameters": []                
            },
            build_image_function(self, client),            
        ]
        if len(self.personality.image_files)>0:
            out, function_calls = self.generate_with_function_calls_and_images(context_details, self.personality.image_files, self.function_definitions)
        else:
            out, function_calls = self.generate_with_function_calls(context_details, self.function_definitions)
        if len(function_calls)>0:
            outputs = self.execute_function_calls(function_calls, self.function_definitions)
            out += "\n" + "\n".join([str(o) for o in outputs])
        self.set_message_content(out)

