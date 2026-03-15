from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality
from lollms.prompting import LollmsContextDetails
from lollms.types import MSG_OPERATION_TYPE
from typing import Callable, Any

from lollmsvectordb.text_document_loader import TextDocumentsLoader
from lollmsvectordb.text_chunker import TextChunker
import subprocess
from pathlib import Path

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
                {"name":"output_language","type":"str","value":"French", "help":"The output language to translate to"},
                {"name":"translation_chunk_size","type":"int","value":1024, "help":"The size of the chunks to translate. They shoumld be less than the context size/2"},
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
                                        "start_zipping":self.start_zipping
                                    },
                                    "default": None
                                },                           
                            ],
                            callback=callback
                        )
        self.cv = None
        self.position = None

    def install(self):
        super().install()
        
        # requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Install dependencies using pip from requirements.txt
        # subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])      
        ASCIIColors.success("Installed successfully")        

    def help(self, prompt="", full_context=""):
        self.personality.InfoMessage(self.personality.help)
    
    def add_file(self, path, client, callback=None):
        """
        Here we implement the file reception handling
        """
        super().add_file(path, client, callback)

    def save_text(self, text, path:Path):
        with open(path,"w", encoding="utf8") as f:
            f.write(text)
            
    def translate_document(self, document_path:Path,  output_path:Path=None, output =""):
        document_text = TextDocumentsLoader.read_file(document_path)
        tc = TextChunker(self.personality_config.translation_chunk_size, 0, tokenizer=self.personality.model)
        document_chunks = DocumentDecomposer.decompose_document(document_text, )
        translated = ""
        nb_chunks = len(document_chunks)
        for i,document_chunk in enumerate(document_chunks):
            self.step_start(f"Translating chunk {i+1}/{nb_chunks}")
            txt = "".join(document_chunk)
            translated += self.translate(txt, self.personality_config.output_language, self.personality.config.ctx_size-len(document_chunk)).replace("\\_","_")
            self.step_end(f"Translating chunk {i+1}/{nb_chunks}")
            self.set_message_content(translated)
        if output_path:
            self.save_text(document_text, output_path/(document_path.stem+f"_{self.personality_config.output_language}.txt"))
        return document_text, output
                    
        

    def start_zipping(self, prompt="", full_context=""):
        self.new_message("Warming up")
        for file in self.personality.text_files:
            output=""
            file = Path(file)
            translation, output = self.translate_document(file, file.parent, output)
            output +=f"\n## {file.stem}\n{translation}"
            self.set_message_content(output)


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

        self.callback = callback
        if len(self.personality.text_files)>0:
            self.step_start("Understanding request")
            if self.yes_no("Is the user asking for summarizing the document?", previous_discussion_text):
                self.step_end("Understanding request")
                self.start_zipping()
            else:
                self.step_end("Understanding request")
                self.fast_gen(previous_discussion_text, callback=self.callback)
        else:
            self.fast_gen(previous_discussion_text, callback=self.callback)
        return ""


