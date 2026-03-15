"""
project: lollms
personality: # Code guard
Author: # Place holder: creator name 
description: # Place holder: personality description
"""
from lollms.types import MSG_OPERATION_TYPE
from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality
from lollms.utilities import show_yes_no_dialog
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails

from pathlib import Path
from typing import Callable, Any
import subprocess
import ast

class FunctionAndMethodExtractor(ast.NodeVisitor):
    def __init__(self, tokens):
        self.tokens = tokens
        self.definitions = []
        self.current_index = 0

    def visit_FunctionDef(self, node):
        definition_tokens = self.tokens[self.current_index:node.end_lineno]
        self.definitions.append(('Function', node.name, definition_tokens))
        self.current_index = node.end_lineno
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_name = f'{node.name}.{item.name}'
                definition_tokens = self.tokens[self.current_index:item.end_lineno]
                self.definitions.append(('Method', method_name, definition_tokens))
                self.current_index = item.end_lineno
        self.generic_visit(node)

def parse_query(query):
    """
    
    """

    lq = len(query)
    parts = query.split("@@")
    if len(parts)>1:
        query_ = parts[1].split("@@")
        query_=query_[0]
        parts = query_.split("|")
        fn = parts[0]
        if len(parts)>1:
            params = parts[1:]
        else:
            params=[]
        try:
            end_pos = query.index("@@")
        except:
            end_pos = lq
        return fn, params, end_pos

    else:
        return None, None


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
                {"name":"code_folder_path","type":"str","value":"", "help":"Folder containing code to check"},
                {"name":"docs_folder_path","type":"str","value":"", "help":"Folder to put the documentation to"},
                {"name":"tests_folder_path","type":"str","value":"", "help":"Folder to put the tests in (not implemented yet)"},
                {"name":"reprocess_processed_files","type":"bool","value":False, "help":"If true reprocess unprocessed files"},
                {"name":"context","type":"text","value":"", "help":"More information about the code"},
                {"name":"files_to_parse","type":"str","value":".py", "help":"File types to be scanned comma separated"},
                {"name":"process_subfolders","type":"bool","value":True, "help":"If true then process files from the subdirectories"},
                {"name":"output_format","type":"str","value":"markdown", "options":["markdown","html","latex"], "help":"Output format"},
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
                                        "start_detection": self.start_detection,
                                        "help":self.help,
                                    },
                                    "default": None
                                },                           
                            ],
                            callback=callback
                        )
    def install(self):
        super().install()
        requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Install dependencies using pip from requirements.txt
        subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])      
        ASCIIColors.success("Installed successfully")        

    def help(self, prompt="", full_context=""):
        self.set_message_content(self.personality.help)

    def build_vulenerabilities_report(self, code, fn):
        analysis = self.fast_gen(f"{self.config.start_header_id_template}{self.config.system_message_template}{self.config.end_header_id_template}Analyze this code and try to detect any security vulenerabilities.\nCreate a report about any detected vulenerability.\nPoint out the vulenerabilities by showing code snippets. Give the report a title and split it into sections. Show the vulenerabilities potential flaws and especially propose fixes to the code using some code tags. The output format is {self.personality_config.output_format}.{self.config.start_header_id_template}file name:{fn}{self.config.start_header_id_template}code:\n```python\n{code}\n```{self.config.separator_template}{self.config.start_header_id_template}additional context:{self.personality_config.context}{self.config.separator_template}{self.config.start_header_id_template}report:\n")
        self.set_message_content(analysis)
        return analysis

    def continue_vulenerabilities_report(self, code):
        analysis = self.fast_gen(f"{self.config.start_header_id_template}{self.config.system_message_template}{self.config.end_header_id_template}Analyze this code chunk and try to detect any security vulenerabilities.\nCreate a report about any detected vulenerability.\nPoint out the vulenerabilities by showing code snippets. This is the continuation of a report started earlyer and we are analysing another chunk if the code. Show the vulenerabilities potential flaws and especially propose fixes to the code using some code tags. The output format is {self.personality_config.output_format}.{self.config.start_header_id_template}code:\n```python\n{code}\n```{self.config.separator_template}{self.config.start_header_id_template}additional context:{self.personality_config.context}{self.config.separator_template}{self.config.start_header_id_template}report:\n")
        self.set_message_content(analysis)
        return analysis



    def process_folder(
                            self, 
                            code_folder_path:Path, 
                            docs_folder_path:Path, 
                            max_nb_tokens_in_file:int, 
                            tokenize:Callable, 
                            detokenize:Callable,
                            accepted_file_types:list
                        ):
         
        for file in code_folder_path.iterdir():
            if file.name.startswith(".") or str(file)==self.personality_config.docs_folder_path:
                continue
            if file.is_dir():
                if self.personality_config.process_subfolders:
                    docs_subfolder = docs_folder_path/file.stem
                    docs_subfolder.mkdir(exist_ok=True, parents=True)
                    self.process_folder(file, docs_subfolder, max_nb_tokens_in_file, tokenize, detokenize, accepted_file_types)
            else:
                if file.suffix.lower() in accepted_file_types:
                    output_documentation_file_path = docs_folder_path/f"{file.stem}.md"
                    if self.personality_config.reprocess_processed_files or not output_documentation_file_path.exists():
                        self.new_message("")
                        self.add_chunk_to_message_content("")
                        self.step_start(f"Processing file {file}")
                        with open(file, "r", encoding="utf-8") as f:
                            code = f.read()
                            tk = self.personality.model.tokenize(code)
                            nb_tk = len(tk)
                            if nb_tk<max_nb_tokens_in_file:
                                analysis = self.build_vulenerabilities_report(code, file.name)
                                with open(output_documentation_file_path,"w", encoding="utf-8") as df:
                                    df.write(analysis)
                            else:
                                tokens = tokenize(code)
                                extractor = FunctionAndMethodExtractor(tokens)
                                tree = ast.parse(code)
                                extractor.visit(tree)

                                chunk = []
                                nb_processed = 0
                                for definition_type, definition_name, definition_tokens in extractor.definitions:
                                    if len(chunk) + len(definition_tokens) <= max_nb_tokens_in_file:
                                        chunk.extend(definition_tokens)
                                    else:
                                        # Process the current chunk
                                        definition_code = detokenize(chunk)
                                        if nb_processed==0:
                                            analysis = self.build_vulenerabilities_report(definition_code, file.name)
                                            with open(output_documentation_file_path,"a", encoding="utf-8") as df:
                                                df.write(analysis)
                                        else:
                                            analysis = self.continue_vulenerabilities_report(definition_code)
                                            with open(output_documentation_file_path,"a", encoding="utf-8") as df:
                                                df.write("\n"+analysis)
                                        nb_processed +=1
                                        chunk = definition_tokens  # Start a new chunk with the current definition

                                # Process the last chunk if there are any tokens left
                                if chunk:
                                    definition_code = detokenize(chunk)
                                    if nb_processed>0:
                                        analysis = self.continue_vulenerabilities_report(definition_code)
                                        with open(output_documentation_file_path,"a", encoding="utf-8") as df:
                                            df.write(analysis)
                                    else:
                                        analysis = self.build_vulenerabilities_report(definition_code, file)
                                        with open(output_documentation_file_path,"w", encoding="utf-8") as df:
                                            df.write(analysis)

                            self.step_end(f"Processing file {file}")

    def start_detection(self, prompt="", full_context="", client:Client=None):
        if show_yes_no_dialog("File processing request","Hi! I just received a request to start reading and documenting files on your PC.If this operation was not triggered by you, please press No and investigate your security.\nIf this is requested by you then pres yes to start.\nDo you want to continue?"):
            if self.personality_config.code_folder_path=="" or self.personality_config.docs_folder_path=="":
                self.set_message_content("Please setup a code folder path, a docs folder path and optionally a tests folder path before trying to use this functionality")
        
            code_folder_path = Path(self.personality_config.code_folder_path)
            tests_folder_path = Path(self.personality_config.tests_folder_path)
            docs_folder_path = Path(self.personality_config.docs_folder_path)
            tokenize = self.personality.model.tokenize
            detokenize = self.personality.model.detokenize
            max_nb_tokens_in_file = 3*self.personality.config.ctx_size/4
            accepted_file_types = ["." + extension.strip() if not extension.startswith(".") else extension.strip() for extension in self.personality_config.files_to_parse.split(",")] 
            self.process_folder(code_folder_path, docs_folder_path, max_nb_tokens_in_file, tokenize, detokenize, accepted_file_types)

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
        output = self.fast_gen(previous_discussion_text)
        self.set_message_content(output)

        return output

