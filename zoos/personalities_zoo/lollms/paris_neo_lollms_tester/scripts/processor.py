"""
Project: LoLLMs
Personality: # Placeholder: Personality name (e.g., "Science Enthusiast")
Author: # Placeholder: Creator name (e.g., "ParisNeo")
Description: # Placeholder: Personality description (e.g., "A personality designed for enthusiasts of science and technology, promoting engaging and informative interactions.")
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

from lollms.utilities import discussion_path_to_url
import subprocess
from typing import Callable, Any
from functools import partial
from ascii_colors import trace_exception

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
                {"name":"test_ui", "type":"bool", "value":False, "help":"Enables testing the ui functionality of lollms."},
                # Boolean configuration for enabling scripted AI
                #{"name":"make_scripted", "type":"bool", "value":False, "help":"Enables a scripted AI that can perform operations using python scripts."},
                
                # String configuration with options
                #{"name":"response_mode", "type":"string", "options":["verbose", "concise"], "value":"concise", "help":"Determines the verbosity of AI responses."},
                
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
        if self.personality_config.test_ui:
            prompt='''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multiple Widgets Interface with Tailwind</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        primary: {
                            light: '#3498db',
                            dark: '#2980b9',
                        },
                        secondary: {
                            light: '#2ecc71',
                            dark: '#27ae60',
                        },
                    },
                },
            },
        }
    </script>
</head>
<body class="bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-white transition-colors duration-200">
    <div class="container mx-auto p-8 max-w-2xl">
        <h1 class="text-3xl font-bold mb-8">Widget Interface with Themes</h1>

        <div class="mb-6">
            <label for="theme" class="block mb-2">Select Theme:</label>
            <select id="theme" class="w-full p-2 border rounded" onchange="toggleTheme(this.value)">
                <option value="light">Light</option>
                <option value="dark">Dark</option>
            </select>
        </div>
        <div class="mb-6">
            <label for="image-select" class="block mb-2">Select Image:</label>
            <select id="image-select" class="w-full p-2 border rounded dark:bg-gray-700" onchange="changeImage(this.value)">
                <option value="">Choose an image</option>
                <option value="https://picsum.photos/300/200?random=1">Random Image 1</option>
                <option value="https://picsum.photos/300/200?random=2">Random Image 2</option>
                <option value="https://picsum.photos/300/200?random=3">Random Image 3</option>
            </select>
        </div>

        <div class="mb-6">
            <img id="display-image" src="" alt="Selected Image" class="w-full h-auto rounded shadow-lg hidden">
        </div>
        <div class="mb-6">
            <label for="text-input" class="block mb-2">Text Input:</label>
            <input type="text" id="text-input" placeholder="Enter some text" class="w-full p-2 border rounded dark:bg-gray-700">
        </div>

        <div class="mb-6">
            <label for="dropdown" class="block mb-2">Dropdown Select:</label>
            <select id="dropdown" class="w-full p-2 border rounded dark:bg-gray-700">
                <option value="">Choose an option</option>
                <option value="1">Option 1</option>
                <option value="2">Option 2</option>
                <option value="3">Option 3</option>
            </select>
        </div>

        <div class="mb-6">
            <label class="block mb-2">Radio Buttons:</label>
            <div class="flex space-x-4">
                <label class="inline-flex items-center">
                    <input type="radio" name="radio-group" value="1" class="form-radio text-primary-light dark:text-primary-dark">
                    <span class="ml-2">Option 1</span>
                </label>
                <label class="inline-flex items-center">
                    <input type="radio" name="radio-group" value="2" class="form-radio text-primary-light dark:text-primary-dark">
                    <span class="ml-2">Option 2</span>
                </label>
                <label class="inline-flex items-center">
                    <input type="radio" name="radio-group" value="3" class="form-radio text-primary-light dark:text-primary-dark">
                    <span class="ml-2">Option 3</span>
                </label>
            </div>
        </div>

        <div class="mb-6">
            <label class="block mb-2">Checkboxes:</label>
            <div class="flex space-x-4">
                <label class="inline-flex items-center">
                    <input type="checkbox" class="form-checkbox text-secondary-light dark:text-secondary-dark">
                    <span class="ml-2">Option 1</span>
                </label>
                <label class="inline-flex items-center">
                    <input type="checkbox" class="form-checkbox text-secondary-light dark:text-secondary-dark">
                    <span class="ml-2">Option 2</span>
                </label>
                <label class="inline-flex items-center">
                    <input type="checkbox" class="form-checkbox text-secondary-light dark:text-secondary-dark">
                    <span class="ml-2">Option 3</span>
                </label>
            </div>
        </div>

        <div class="mb-6">
            <label for="slider" class="block mb-2">Slider:</label>
            <input type="range" id="slider" min="0" max="100" value="50" class="w-full">
        </div>

        <div>
            <button onclick="alert('Button clicked!')" class="bg-primary-light dark:bg-primary-dark text-white font-bold py-2 px-4 rounded hover:bg-opacity-90 transition-colors duration-200">
                Click Me!
            </button>
        </div>
    </div>

    <script>
        function changeImage(src) {
            const img = document.getElementById('display-image');
            if (src) {
                img.src = src;
                img.classList.remove('hidden');
            } else {
                img.classList.add('hidden');
            }
        }
        function toggleTheme(theme) {
            if (theme === 'dark') {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
        }
    </script>
</body>
</html>
'''
            import tracemalloc
            tracemalloc.start()
            self.set_message_content("Testing ui")
            self.set_message_html(prompt)
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')
            print("[ Top 10 ]")
            for stat in top_stats[:10]:
                print(stat)
            tracemalloc.stop()
            self.json("json", {"test":"test"})
        else:
            out = self.generate_structured_content("generate a meal",template={"name":"The meal name","ingredients":"a list of ingrediants","steps":"a list of steps"})#, callback=self.sink)
            self.json("Generated json",out)
            self.new_message("")
            out = self.yes_no("Is Paris in france?","You are smart")#, callback=self.sink)
            self.set_message_content(f"paris in france:{out}")
            self.new_message("")
            # Define the question, possible answers, and context
            question = "What is the capital of France?"
            possible_answers = ["Paris", "London", "Berlin", "Madrid"]
            context = "France is a country in Western Europe."

            # Create the multiple-choice question with a condition
            condition = "The answer is not London."
            question_with_condition = self.multichoice_question(
                question=question,
                possible_answers=possible_answers,
                context=context,
                conditionning=condition,
                return_explanation=True
            )
            self.json(f"question_with_condition", question_with_condition)
