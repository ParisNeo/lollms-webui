from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality
from lollms.utilities import find_first_available_file_index
from lollms.types import MSG_OPERATION_TYPE
from typing import Callable, Any
from lollms.prompting import LollmsContextDetails
import subprocess
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json

def convert_webpage_to_markdown(url):
    # Send a GET request to the webpage
    response = requests.get(url)
    
    # Parse the HTML content of the webpage using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all the paragraph and title elements in the webpage
    paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    # Join the text elements into a single string
    text = '\n'.join([element.get_text() for element in paragraphs])
    
    # Convert the text to markdown format
    markdown_text = f"# {soup.title.string}\n\n{text}"
    
    return markdown_text

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
        # Example entry
        #       {"name":"make_scripted","type":"bool","value":False, "help":"Makes a scriptred AI that can perform operations using python script"},
        # Supported types:
        # str, int, float, bool, list
        # options can be added using : "options":["option1","option2"...]        
        personality_config_template = ConfigTemplate(
            [
                {"name":"url","type":"str","value":"", "help":"A url to a webpage to scrape and convert to text"},
                {"name":"data_folder","type":"str","value":"", "help":"A path to a folder containing text files to be used to build the database"},
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
                                    "commands": { # list of commands
                                        "help":self.help,
                                        "scrape_web":self.scrape_web,
                                        "build_db":self.build_db
                                    },
                                    "default": None
                                },                           
                            ],
                            callback=callback
                        )
        
    def install(self):
        super().install()
        
        # requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Install dependencies using pip from requirements.txt
        # subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])      
        ASCIIColors.success("Installed successfully")        

    def help(self, prompt="", full_context=""):
        self.set_message_content(self.personality.help)
    
    def scrape_web(self, prompt="", full_context=""):
        self.new_message("")
        self.step_start("Scraping data")
        if self.personality_config.url=="":
            self.personality.info("Please set a url into my configuration before asking me to scrape a url!", False)
            return
        if self.personality_config.data_folder=="":
            self.personality.info("Please set a data_folder into my configuration before asking me to scrape a url!", False)
            return
        self.personality.info("Starting data processing", True)
        text = convert_webpage_to_markdown(self.personality_config.url)
        index = find_first_available_file_index(self.personality_config.data_folder,"data_",".txt")
        data_folder = Path(self.personality_config.data_folder)
        with open(data_folder/f"data_{index}.txt","w", encoding="utf8") as f:
            f.write(text)
        self.step_end("Scraping data")
    
            
    def build_db(self, prompt="", full_context=""):
        if self.personality_config.data_folder == "":
            self.personality.info("Please set a data_folder into my configuration before asking me to build the database!")
            return
        self.new_message("")
        self.step_start("Building database")
        # Get the path of the data_folder
        data_folder = Path(self.personality_config.data_folder)

        # Load all text files from data_folder
        files = data_folder.glob("*.txt")

        # Decompose text into sentences
        sentences = []
        for file in files:
            with open(file, "r", encoding="utf8") as f:
                text = f.read()
                paragraphs = text.split("\n")
                for paragraph in paragraphs:
                    if paragraph.strip() != "":
                        sentences.extend(paragraph.strip().split("."))

        # Generate questions and answers
        qa_list = []
        for sentence in sentences:
            sentence = sentence.strip()
            words = sentence.split()
            i = 0 
            for word in words:
                if word in ["-","#","'",'"',"/",",",".",":",";","?","!","§","(",")","[","]","{","}","|","`","_","~","»","»"]:
                    continue
                question = f"Given the following sentence \"{sentence}\", what is the position of the word {word}?"
                answer = f"The position of {word} in the sentence is {i+1}"
                qa_list.append({"question": question, "answer": answer})

                question = f"What is the length of the word {word}?"
                answer = f"The length of the word {word} is {len(word)}"
                qa_list.append({"question": question, "answer": answer})

                i += 1
            question = f"What is the number of words in {sentence}?"
            answer = f"The length of this sentence is {i}"
            qa_list.append({"question": question, "answer": answer})

        # Build JSON file
        output_file = data_folder / "database.json"
        with open(output_file, "w", encoding="utf8") as f:
            json.dump(qa_list,f, indent=4, ensure_ascii=False)


        self.step_end("Building database")
        
    def add_file(self, path, client, callback=None):
        """
        Here we implement the file reception handling
        """
        super().add_file(path, client, callback)

    from lollms.client_session import Client
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

        if self.personality_config.data_folder!="":
            self.build_db()
        else:
            ASCIIColors.info("Generating")
            self.callback = callback
            out = self.fast_gen(previous_discussion_text+"Looking at my configuration, I see that you did not yet give a link to the data file. Please open my settings by pressing my icon on the chatbox and setup the path to the raw data file to process.")
            self.set_message_content(out)
        return ""

