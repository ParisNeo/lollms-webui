"""
Project: LoLLMs
Personality: # Placeholder: Personality name (e.g., "Science Enthusiast")
Author: # Placeholder: Creator name (e.g., "ParisNeo")
Description: # Placeholder: Personality description (e.g., "A personality designed for enthusiasts of science and technology, promoting engaging and informative interactions.")
"""

from lollms.types import MSG_OPERATION_TYPE
from typing import Any
from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality
from lollms.prompting import LollmsContextDetails
from lollms.client_session import Client
from lollms.utilities import output_file_path_to_url
from lollms.functions.generate_image import build_image, build_image_function
from lollms.functions.take_a_photo import take_photo

from functools import partial
from ascii_colors import trace_exception
import subprocess
from typing import Callable, Any
from pathlib import Path
import sys
import sqlite3
import json
from datetime import datetime
from lollms.utilities import PackageManager, discussion_path_to_url, personality_path_to_url
if not PackageManager.check_package_installed("plotly"):
    PackageManager.install_package("plotly")

import plotly.graph_objs as go
from plotly.offline import plot
import plotly.io as pio  # Import Plotly IO for image saving

class GuitarLearningDB:
    def __init__(self, db_path='guitar_learning.db'):
        self.db_path = db_path
        self.create_tables()

    def create_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # New table CoursePlan
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS UserProfile (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                current_level TEXT NOT NULL,
                current_step INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS CoursePlan (
                step_id INTEGER PRIMARY KEY AUTOINCREMENT,
                step_title TEXT NOT NULL,
                step_type TEXT NOT NULL,
                description TEXT NOT NULL,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES UserProfile (user_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ProgressTrack (
                progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                level TEXT NOT NULL,
                chords TEXT,
                scales TEXT,
                songs TEXT,
                techniques TEXT,
                challenge_completed BOOLEAN,
                FOREIGN KEY (user_id) REFERENCES UserProfile (user_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS AIState (
                state_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                ai_memory TEXT,
                FOREIGN KEY (user_id) REFERENCES UserProfile (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_user_profile(self, name, email, current_level):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO UserProfile (name, email, current_level)
            VALUES (?, ?, ?)
        ''', (name, email, current_level))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id

    def get_user_id_by_name(self, name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id FROM UserProfile
            WHERE name = ?
        ''', (name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def list_all_profiles(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, name, email, current_level FROM UserProfile
        ''')
        results = cursor.fetchall()
        conn.close()
        return results

    def remove_user_profile(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM UserProfile WHERE user_id = ?
        ''', (user_id,))
        cursor.execute('''
            DELETE FROM ProgressTrack WHERE user_id = ?
        ''', (user_id,))
        cursor.execute('''
            DELETE FROM AIState WHERE user_id = ?
        ''', (user_id,))
        conn.commit()
        conn.close()

    def get_user_profile(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name, email, current_level FROM UserProfile
            WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def update_user_profile(self, user_id, name=None, email=None, current_level=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE UserProfile
            SET name = COALESCE(?, name),
                email = COALESCE(?, email),
                current_level = COALESCE(?, current_level)
            WHERE user_id = ?
        ''', (name, email, current_level, user_id))
        conn.commit()
        conn.close()

    # Method to add a new course step and set it as the current step for a user if no steps are associated
    def add_course_step(self, user_id, step_type, step_title, description):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Insert the new step into CoursePlan
        cursor.execute('''
            INSERT INTO CoursePlan (step_type, step_title, description, user_id)
            VALUES (?, ?, ?, ?)
        ''', (step_type, step_title, description, user_id))
        step_id = cursor.lastrowid

        # Check if the user has any associated steps
        cursor.execute('''
            SELECT current_step FROM UserProfile WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()

        # If no steps are associated, set the current_step to the new step
        if result is None or result[0] is None or result[0]==0:
            cursor.execute('''
                UPDATE UserProfile SET current_step = ? WHERE user_id = ?
            ''', (step_id, user_id,))

        conn.commit()
        conn.close()
        return step_id

    def get_current_course_step(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT cp.step_id, cp.step_type, cp.description
            FROM UserProfile up
            JOIN CoursePlan cp ON up.current_step = cp.step_id
            WHERE up.user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return {
            'step_id': result[0],
            'step_type': result[1],
            'code': result[2],
        } if result else None

    def update_course_step(self, step_id, step_type=None, code=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE CoursePlan
            SET step_type = COALESCE(?, step_type),
                code = COALESCE(?, code)
            WHERE step_id = ?
        ''', (step_type, code, step_id))
        conn.commit()
        conn.close()

    def set_user_current_step(self, user_id, step_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE UserProfile
            SET current_step = ?
            WHERE user_id = ?
        ''', (step_id, user_id))
        conn.commit()
        conn.close()


    def log_progress(self, user_id, level, chords, scales, songs, techniques, challenge_completed):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ProgressTrack (user_id, level, chords, scales, songs, techniques, challenge_completed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, level, chords, scales, songs, techniques, challenge_completed))
        conn.commit()
        conn.close()

    def get_last_ai_state(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ai_memory FROM AIState
            WHERE user_id = ?
            ORDER BY state_id DESC
            LIMIT 1
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def set_ai_state(self, user_id, ai_memory):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO AIState (user_id, ai_memory)
            VALUES (?, ?)
        ''', (user_id, ai_memory))
        conn.commit()
        conn.close()

    def get_user_overall_progress(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT level, chords, scales, songs, techniques, challenge_completed FROM ProgressTrack
            WHERE user_id = ?
            ORDER BY progress_id DESC
            LIMIT 1
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return {
            'level': result[0],
            'chords': result[1],
            'scales': result[2],
            'songs': result[3],
            'techniques': result[4],
            'challenge_completed': result[5],
        } if result else {}

    # New method to clear the course for a user
    def clear_course_for_user(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE UserProfile
            SET current_step = 0
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()

        # New method to remove all course steps for a user
        cursor.execute('''
            DELETE FROM CoursePlan
            WHERE step_id IN (
                SELECT current_step FROM UserProfile WHERE user_id = ?
            )
        ''', (user_id,))
        conn.commit()
        conn.close()

    # Method to get all course steps for a user
    def get_course_steps(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT step_id, step_title, step_type, description
            FROM CoursePlan
            WHERE user_id = ?
        ''', (user_id,))
        # Fetch all results
        course_steps = cursor.fetchall()
        conn.close()
        return course_steps

    
    # Method to get the current course step for a user
    def get_current_course_step(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT CP.step_id, CP.step_type, CP.description
            FROM UserProfile UP
            JOIN CoursePlan CP ON UP.current_step = CP.step_id
            WHERE UP.user_id = ?
        ''', (user_id,))
        # Fetch the result
        current_step = cursor.fetchone()
        conn.close()
        return current_step if current_step else None

    # Method to advance to the next course step for a user
    def next_step(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get the current step for the user
        cursor.execute('''
            SELECT current_step FROM UserProfile WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        if result:
            current_step = result[0]
            # Check if there is a next step available
            cursor.execute('''
                SELECT EXISTS(SELECT 1 FROM CoursePlan WHERE step_id = ? + 1)
            ''', (current_step,))
            has_next_step = cursor.fetchone()[0]
            
            if has_next_step:
                # Update the current step to the next step
                cursor.execute('''
                    UPDATE UserProfile SET current_step = current_step + 1 WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
                message = "User has been advanced to the next step."
            else:
                message = "No more steps available. Course completed."
        else:
            message = "User ID does not exist."

        conn.close()
        return message


    def plot_user_progress(self, user_id, image_path, html_path):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT date, level, chords, scales, songs, techniques FROM ProgressTrack
            WHERE user_id = ?
            ORDER BY date
        ''', (user_id,))
        results = cursor.fetchall()
        conn.close()

        if not results:
            print("No progress data to plot.")
            return

        # Extracting data for plotting
        dates = [datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') for row in results]
        levels = [row[1] for row in results]
        chords = [row[2] for row in results]
        scales = [row[3] for row in results]
        songs = [row[4] for row in results]
        techniques = [row[5] for row in results]

        # Convert levels to numeric values if they are not already numeric
        levels_numeric = [float(level) if level.isdigit() else float(index) for index, level in enumerate(levels)]

        # Plotting with Plotly
        trace1 = go.Scatter(x=dates, y=levels_numeric, mode='lines+markers', name='Level', marker=dict(color='RoyalBlue'), line=dict(width=2))
        trace2 = go.Scatter(x=dates, y=chords, mode='lines+markers', name='Chords learned', marker=dict(color='Crimson'), line=dict(width=2, dash='dot'))
        trace3 = go.Scatter(x=dates, y=scales, mode='lines+markers', name='Scales learned', marker=dict(color='GoldenRod'), line=dict(width=2, dash='dash'))
        trace4 = go.Scatter(x=dates, y=songs, mode='lines+markers', name='Songs learned', marker=dict(color='ForestGreen'), line=dict(width=2, dash='dashdot'))
        trace5 = go.Scatter(x=dates, y=techniques, mode='lines+markers', name='Techniques learned', marker=dict(color='DarkViolet'), line=dict(width=2, dash='longdash'))

        data = [trace1, trace2, trace3, trace4, trace5]

        layout = go.Layout(
            title='User Progress Over Time',
            xaxis=dict(title='Date', tickangle=-45),
            yaxis=dict(title='Progress'),
            margin=dict(l=40, r=40, t=40, b=130),
            legend=dict(x=0, y=1.0, bgcolor='rgba(255,255,255,0)'),
            hovermode='closest'
        )

        fig = go.Figure(data=data, layout=layout)
        plot(fig, filename=html_path, auto_open=False)
        
        # Save the plot as a static image
        pio.write_image(fig, image_path)


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
                {"name":"image_generation_engine", "type":"string", "value":"", "options":["autosd","dall-e-2","dall-e-3"], "help":"The image generation engine to be used by the tool for generating images.\nPlease make sure that the service is available and for remote services, verify that you have set the key in the service settings"},
                {"name":"show_screenshot_ui", "type":"bool", "value":True, "help":"When taking a screenshot, if this is true then a ui will be show when the screenshot function is called"},
                {"name":"take_photo_ui", "type":"bool", "value":True, "help":"When taking a screenshot, if this is true then a ui will be show when the take photo function is called"},
                
                # String configuration with options
                {"name":"user_profile_name", "type":"string", "value":"", "help":"The profile name of the user. Used to store progress data."},
                {"name":"user_level", "type":"string", "value":"beginner", "options":["beginner","medium","advanced"], "help":"The profile name of the user. Used to store progress data."},
                 
                
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
        self.user_profile_db = GuitarLearningDB(str(self.evolution_db))

    def get_or_create_user_profile(self):
        if self.personality_config.user_profile_name=="":
            return False
        user_id = self.user_profile_db.get_user_id_by_name(self.personality_config.user_profile_name)
        
        if user_id is None:
            # If the user doesn't exist, create a new profile with the initial level from the configuration
            initial_level = self.personality_config.user_level
            user_id = self.user_profile_db.add_user_profile(self.personality_config.user_profile_name, '', initial_level)
            status_text = f"Created a new user profile for {self.personality_config.user_profile_name} with initial level {initial_level}."
        else:
            # If the user exists, fetch the current status
            user_profile = self.user_profile_db.get_user_profile(user_id)
            status_text = f"User {user_profile[0]} is currently at level {user_profile[2]}."

        # Retrieve the last AI state for the user
        ai_memory = self.user_profile_db.get_last_ai_state(user_id)
        if ai_memory:
            status_text += " Last session data has been retrieved."
        else:
            status_text += " No previous session data found."

        return status_text

    def get_welcome(self, welcome_message:str, client):
        user_level = self.get_or_create_user_profile()
        if user_level:
            return self.fast_gen(f"{self.config.start_header_id_template}{self.config.system_message_template}{self.config.end_header_id_template}Build a better  welcome message for the user.{self.config.separator_template}{self.config.start_header_id_template}current_welcome_message: {welcome_message}{self.config.separator_template}{self.config.start_header_id_template}last session data: {user_level}{self.config.separator_template}{self.config.start_header_id_template}adapted welcome message:")
        else:
            return welcome_message+"\nI see that you did not specify a profile in my settings. Please specify a profile name.\nYou need to press my icon in the chatbar and you'll see my configuration window. Type your profile name and your level, then make a new discussion.\n"

    def help(self):
        """
        Provides help information about the personality and its commands.
        """
        # Implementation of the help method
        pass

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

    def format_course_steps_as_markdown(self, course_steps):
        if not course_steps:
            return "No course steps available for this user."

        markdown_output = "## User's Course Steps\n\n"
        for step in course_steps:
            step_id, step_title, step_type, description = step
            markdown_output += f"### Step {step_id}: {step_title} ({step_type})\n"
            markdown_output += f"{description}\n\n"
        return markdown_output
    # ---------------------- functions ---------------
    def create_a_new_course(self, steps, user_id):
        self.user_profile_db.clear_course_for_user(user_id)
        if type(steps)==dict:
            steps = steps["steps"]
        for step in steps:
            self.user_profile_db.add_course_step(user_id, step.get("step_type","generic"), step.get("step_title","learning step"), step["description"])
        return "### Course created successfuly"
    
    def show_metronome(self):
        # Determine the directory of the current script
        current_script_dir = Path(__file__).parent

        # Construct the path to metronome.py
        metronome_script_path = current_script_dir / 'tools' / 'metronome.py'

        # Use subprocess.Popen to run the script without waiting for it to finish
        subprocess.Popen([sys.executable, str(metronome_script_path)])
        return "Metronome is now running. Adjust the BPM and press start. You can press stop to stop it"

    def show_user_progress(self, user_id, client:Client):
        img_path = client.discussion.discussion_folder/f"current_status_{client.discussion.current_message.id}.png"
        interactive_ui = client.discussion.discussion_folder/f"current_status_{client.discussion.current_message.id}.html"
        self.user_profile_db.plot_user_progress(user_id, str(img_path), str(interactive_ui))
        return f"<img src='{discussion_path_to_url(img_path)}'></img>\n<a href='{discussion_path_to_url(interactive_ui)}' target='_blank'>click here for an interactive version</a>"
        
    def log_progress(self, parameters, user_id):
        if type(parameters)==dict and "parameters" in list(parameters.keys()):
            parameters=parameters["parameters"]
        current_progress = self.user_profile_db.get_user_overall_progress(user_id)
        if not current_progress:
            current_progress = {
                "level":0,
                "chords":0,
                "scales":0,
                "songs":0,
                "techniques":0,
                "challenge_completed":0
            }

        self.user_profile_db.log_progress(
                                            user_id, 
                                            parameters.get('level',current_progress['level']),
                                            parameters.get('chords',current_progress['chords']),
                                            parameters.get('scales',current_progress['scales']),
                                            parameters.get('songs',current_progress['songs']),
                                            parameters.get('techniques',current_progress['techniques']),
                                            parameters.get('challenge_completed',current_progress['challenge_completed']),
                                        )
        return "progress logged successfully"
    
    def get_course_steps(self, user_id):
        course_steps =self.user_profile_db.get_course_steps(user_id)
        out =  "# Course\n"+self.format_course_steps_as_markdown(course_steps)
        return out

    def get_current_course_step(self, user_id):
        course_step =self.user_profile_db.get_current_course_step(user_id)
        if course_step:
            out =  "# Course step\n"
            step_id, step_type, description = course_step
            out += f"### Step {step_id}: {step_type}\n"
            out += f"{description}\n\n"
            return out
        else:
            return "No course step is present since I did not yet build your own course. Please ask me to build a customized course for you. you can also give me more details so that I build a course that fits your needs."

    def next_course(self, user_id):
        course_step =self.user_profile_db.get_current_course_step(user_id)
        if course_step:
            self.user_profile_db.next_step(user_id)
            out =  "# New course step:\n"
            step_id, step_type, description = course_step
            out += f"### Step {step_id}: {step_type}\n"
            out += f"{description}\n\n"
            return out
        else:
            return "No course step is present since I did not yet build your own course. Please ask me to build a customized course for you. you can also give me more details so that I build a course that fits your needs."

    def show_chord(self, chord_name:str):
        path:Path = self.personality.assets_path/"chords"/f"{chord_name}.png"
        if path.exists():
            return f'<img src="{personality_path_to_url(path)}" width="80%"></img>'


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
        self.get_or_create_user_profile()
        user_id = self.user_profile_db.get_user_id_by_name(self.personality_config.user_profile_name)
        if user_id is None:
            self.set_message_content(self.personality.welcome_message+"\nI see that you did not specify a profile in my settings. Please specify a profile name.\nYou need to press my icon in the chatbar and you'll see my configuration window. Type your profile name and your level, then make a new discussion.\n")
            return
        self.personality.info("Generating")
        memory_data = self.user_profile_db.get_last_ai_state(user_id)
        course_step = self.user_profile_db.get_current_course_step(user_id)

        prompt = self.build_prompt([
            context_details.conditionning if context_details.conditionning else "",
            f"{self.config.start_header_id_template}documentation:\n"+context_details.documentation if context_details.documentation else "",
            context_details.user_description if context_details.user_description else "",
            f"{self.config.start_header_id_template}positive_boost:\n"+context_details.positive_boost if context_details.positive_boost else "",
            f"{self.config.start_header_id_template}negative_boost:\n"+context_details.negative_boost if context_details.negative_boost else "",
            f"{self.config.start_header_id_template}current_language:\n"+context_details.current_language if context_details.current_language else "",
            f"{self.config.start_header_id_template}fun_mode:\n"+context_details.fun_mode if context_details.fun_mode else "",
            f"{self.config.start_header_id_template}discussion_window:\n"+context_details.discussion_messages if context_details.discussion_messages else "",
            f"{self.config.start_header_id_template}memory_data:\n"+memory_data if memory_data is not None else "",
            f"{self.config.start_header_id_template}happiness_index:\n"+str(course_step) if course_step is not None else "",
            f"{self.config.start_header_id_template}"+context_details.ai_prefix.replace("{self.config.start_header_id_template}","").replace(":","")+":"
        ], 
        8)

        context_details.extra="\n".join([
            f"{self.config.start_header_id_template}memory_data:\n"+memory_data if memory_data is not None else "",
            f"{self.config.start_header_id_template}happiness_index:\n"+str(course_step) if course_step is not None else "",
        ])
        chords_folder:Path = self.personality.assets_path/"chords"
        self.function_definitions = [
            {
                "function_name": "create_a_new_course",
                "function": partial(self.create_a_new_course, user_id=user_id),
                "function_description": 'Creates a new course from a list of course steps. Each step is a dict in the form:\n{"step_type":"type of the course step (Mastering Chords,Strumming Patterns,Fingerpicking,Scales and Soloing,Music Theory for Guitarists,Ear Training,Guitar Maintenance,Playing Techniques,Learning Songs,Performance Skills)","step_title":"The title of this course step","description":"A detailed description of the course, theory, practice, tests, and evaluation"}',
                "function_parameters": [{"name": "steps", "type": "list of dicts"}]                
            },
            {
                "function_name": "plot_user_progress",
                "function":  partial(self.show_user_progress,user_id=user_id, client=client),
                "function_description": "Plots the user progress over time.",
                "function_parameters": []                
            },
            {
                "function_name": "log_progress",
                "function":  partial(self.log_progress,user_id=user_id),
                "function_description": "Logs the progress of the user. The function_parameters must be a list with a single entry.",
                "function_parameters": [{"name": "parameters", "type": "dict with the following entries (level,chords,scales,songs,techniques,challenge_completed) each entry is an integer"}]                
            },
            {
                "function_name": "get_course_steps",
                "function": partial(self.get_course_steps,user_id=user_id),
                "function_description": "Shows all course steps to the user.",
                "function_parameters": []                
            },
            {
                "function_name": "get_current_course_step",
                "function": partial(self.get_current_course_step,user_id=user_id),
                "function_description": "Shows the current course content.",
                "function_parameters": []                
            },
            {
                "function_name": "next_course",
                "function": partial(self.next_course,user_id=user_id),
                "function_description": "Move to next course step.",
                "function_parameters": []                
            },
            {
                "function_name": "show_metronome",
                "function": self.show_metronome,
                "function_description": "Shows a metronome for the uset to use",
                "function_parameters": []                
            },            
            {
                "function_name": "show_chord",
                "function": self.show_chord,
                "function_description": f"Shows a chord. Currently supported ones are :{[f.stem for f in chords_folder.iterdir()]}",
                "function_parameters": [{"name": "chord_name", "type": "str"}]                
            },            
            build_image_function(self, client),
            {
                "function_name": "take_photo",
                "function": partial(take_photo, use_ui=self.personality_config.take_photo_ui, client=client),
                "function_description": "Takes a photo using the webcam.",
                "function_parameters": []                
            },
            

        ]
        
        if len(self.personality.image_files)>0:
            out, function_calls = self.generate_with_function_calls_and_images(context_details, self.personality.image_files, self.function_definitions)
        else:
            out, function_calls = self.generate_with_function_calls(context_details, self.function_definitions)
        if len(function_calls)>0:
            outputs = self.execute_function_calls(function_calls, self.function_definitions)
            out += "\n" + "\n".join([str(o) for o in outputs])
        self.set_message_content(out)
        return out
