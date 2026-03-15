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
from lollms.databases.discussions_database import Discussion
import subprocess
from typing import Callable, Any
from lollms.prompting import LollmsContextDetails
import sys
import io
def execute_code(code):
    try:
        captured_stdout = io.StringIO()
        captured_stderr = io.StringIO()
        sys.stdout = captured_stdout
        sys.stderr = captured_stderr

        exec(code, globals())

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        return captured_stdout.getvalue(), captured_stderr.getvalue()

    except Exception as e:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        return str(e), ''
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
                {"name":"server","type":"str","value":"https://localhost:9200", "help":"List of addresses of the server in form of ip or host name: port"},
                {"name":"index_name","type":"str","value":"", "help":"The index to be used for querying"},
                {"name":"mapping","type":"text","value":"", "help":"Mapping of the elastic search index"},
                {"name":"user","type":"str","value":"", "help":"The user name to connect to the database"},
                {"name":"password","type":"str","value":"", "help":"The password to connect to the elastic search database"},
                {"name":"max_execution_depth","type":"int","value":10, "help":"The maximum execution depth"},
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
        self.personality.info("Generating")
        self.callback = callback
        header_text = f"{self.config.start_header_id_template}Extra infos:\n"
        header_text += f"server:{self.personality_config.server}\n"
        if self.personality_config.index_name!="":
            header_text += f"index_name:{self.personality_config.index_name}\n"
        if self.personality_config.mapping!="":
            header_text += f"mapping:\n{self.personality_config.mapping}\n"
        if self.personality_config.user!="" and self.personality_config.password!="":
            header_text += f"user:{self.personality_config.user}\n"
            header_text += f"password:{self.personality_config.password}\n"
            header_text += f'es = Elasticsearch("{self.personality_config.server}", http_auth=("{self.personality_config.user}", "{self.personality_config.password}"), verify_certs=False)'
        else:
            header_text += f'es = Elasticsearch("{self.personality_config.server}", verify_certs=False)'

        execution_output = "\n".join([
                    f"{self.config.start_header_id_template}Requirements:",
                    "Encase full code within one block.",
                    "Import all necessary libraries.",
                    "Submit a single, self-contained code block.",
                    "Reply with code only; no explanations.",
                    "Prefer elasticsearch-dsl when suitable."
        ])
        repeats=0
        out=""
        while repeats<self.personality_config.max_execution_depth:
            repeats += 1
            prompt = self.build_prompt(
                [
                    header_text,
                    context_details.conditionning,
                    context_details.discussion_messages,
                    execution_output,
                    "{self.config.separator_template}{self.config.start_header_id_template}ElasticExplorer:",
                ],
                2
            )
            prev_out = out
            out = self.fast_gen(prompt, callback=self.sink)
            self.set_message_content(out)
            self.add_chunk_to_message_content("")
            context_details.discussion_messages += f"{self.config.start_header_id_template}ElasticExplorer:\n"+ out
            code_blocks = self.extract_code_blocks(out)
            execution_output = ""
            if len(code_blocks)>0:
                self.step_start("Executing code")
                nb_codes = 0
                for i in range(len(code_blocks)):
                    if code_blocks[i]["type"]=="python":
                        nb_codes += 1
                        code = code_blocks[i]["content"].replace("\_","_")
                        discussion:Discussion = self.personality.app.session.get_client(context_details.client_id).discussion 
                        try:
                            stdout, stderr = execute_code(code)

                            execution_output += f"Output of script {i}:\n" + stdout +"\n"+f"\n" + stderr +"\n"+"\n".join([
                                f"{self.config.start_header_id_template}Requirements:",
                                "Disregard any warnings during code execution.",
                                "Upon successful output, respond to user requests directly without incorporating any Python code blocks. If the output includes JSON data, enclose it within JSON code tags.",
                                "In case of errors, rectify the code and provide a complete fixed code block without explanations. Ensure that you use a single code block to maintain readability and organization.",
                            ])
                        except Exception as ex:
                            execution_output += f"Error detected in script {i}:\n" + ex +"\n"+"\n".join([
                                f"{self.config.start_header_id_template}Requirements:",
                                "Utilize the error to correct and improve the code.",
                                "Upon fixing the code, respond to user requests with the complete fixed code.",
                                "Avoid providing any additional explanations or comments within your response.",
                            ])
                if nb_codes == 0:
                    break
                self.step_end("Executing code")
            else:
                break
            self.set_message_content(prev_out+'\n'+out+'\n'+self.build_a_document_block("Script output", "", stdout))

        self.set_message_content(prev_out+'\n'+self.build_a_document_block("Script output", "", stdout)+'\n'+out)

        return out

