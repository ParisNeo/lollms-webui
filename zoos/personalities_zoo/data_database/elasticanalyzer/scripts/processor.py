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
from pathlib import Path
import subprocess
from typing import Callable, Any
from datetime import datetime
from lollms.prompting import LollmsContextDetails
import pandas as pd
import json
import io

import re

def parse_query(query):
    # Match the pattern @@function|param1|param2@@
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
        return None, None, 0

from elasticsearch import Elasticsearch

class ElasticSearchConnector:
    def __init__(self, host='http://localhost:9200', username=None, password=None):
        self.host = host
        self.username = username
        self.password = password
        self.es = self.connect()

    def connect(self):
        if self.username and self.password:
            es = Elasticsearch([self.host], http_auth=(self.username, self.password),verify_certs=False)
        else:
            es = Elasticsearch([self.host])
        return es

    def list_indexes(self):
        return self.es.cat.indices(h='index')

    def view_mapping(self, index):
        return self.es.indices.get_mapping(index=index)

    def query(self, index, body):
        return self.es.search(index=index, body=body)

    def add_entry(self, index, body):
        return self.es.index(index=index, body=body)

    def index_data(self, file_path, index_name):
        try:
            self.create_index(index_name)
            with open(file_path, 'r') as file:
                for line in file:
                    doc = json.loads(line)
                    if 'index' in doc:
                        self.es.index(index=index_name, body=doc['_source'], id=doc['_id'])
                    else:
                        self.es.index(index=index_name, body=doc)
            return True
        except Exception as e:
            print(f"Error indexing data: {e}")
            return False
        

    def ping(self):
        # Ping the Elasticsearch server
        response = self.es.ping()

        # Check if the server is reachable
        if response:
            print("Elasticsearch server is reachable")
            return True
        else:
            print("Elasticsearch server is not reachable")
            return False

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
                {"name":"output_folder_path","type":"str","value":"", "help":"Folder to put the output"},
                {"name":"output_format","type":"str","value":"markdown", "options":["markdown","html","latex"], "help":"Output format"},
                {"name":"max_nb_failures","type":"int","value":3, "help":"Maximum number of failures"},
                {"name":"debug_mode","type":"bool","value":False, "help":"Shows all the process details (useful for debugging)"},
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
        es = ElasticSearchConnector(self.personality_config.server, self.personality_config.user, self.personality_config.password)
        header_text = f"{self.config.start_header_id_template}Extra infos:\n"
        header_text += f"server:{self.personality_config.server}\n"
        if self.personality_config.index_name!="":
            header_text += f"index_name:{self.personality_config.index_name}\n"
        if self.personality_config.mapping!="":
            header_text += f"mapping:\n{self.personality_config.mapping}\n"
        if self.personality_config.user!="":
            header_text += f"user:\n{self.personality_config.user}\n"
        if self.personality_config.password!="":
            header_text += f"password:\n{self.personality_config.user}\n"

        full_prompt = header_text
        full_prompt += context_details.conditionning
        full_prompt += context_details.documentation
        full_prompt += context_details.user_description
        full_prompt += context_details.discussion_messages
        full_prompt += context_details.positive_boost
        full_prompt += context_details.negative_boost
        full_prompt += context_details.current_language
        full_prompt += context_details.fun_mode
        full_prompt += "extra_info:\n"
        full_prompt += "If you need to issue a code to es, please do not respond with any extra text or explanations except the command itself.\n"
        full_prompt += "If you need to explain something to the user, do not issue commands, when a command is detected in your answer, it gets executed and the message is not shown to the user.\n"
        full_prompt += "Either respond with a command with no comments or a comment without any command.\n"

        self.personality.info("Generating")
        self.callback = callback

        max_nb_tokens_in_file = 3*self.personality.config.ctx_size/4

        failed=True
        nb_failures = 0
        while failed  and nb_failures<self.personality_config.max_nb_failures:
            failed=False
            nb_failures += 1
            first_generation = self.fast_gen(full_prompt+context_details.ai_prefix,callback=self.sink).replace("\\_","_")
            fn, params, next = parse_query(first_generation)
            if fn:
                if self.personality_config.debug_mode:
                    self.new_message("## Executing ...", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI)
                if fn=="ping":
                    self.step("The LLM issued a ping command")
                    try:
                        status = es.ping()
                        if self.personality_config.debug_mode:
                            self.set_message_content(self.build_a_document_block(f"Execution result:",None,f"{status}"), msg_type=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI)
                        output = self.fast_gen(full_prompt+first_generation+f"{self.config.start_header_id_template}es: ping response: {'Connection succeeded' if status else 'connection failed'}\n"+context_details.ai_prefix, callback=self.sink).replace("\\_","_")
                    except Exception as ex:
                        self.set_message_content(f"## Execution result:\n{ex}")
                        output = self.fast_gen(full_prompt+first_generation+f"{self.config.start_header_id_template}es: error {ex}\n"+context_details.ai_prefix, callback=self.sink).replace("\\_","_")

                if fn=="list_indexes":
                    self.step("The LLM issued a list_indexes command")
                    try:
                        indexes = es.list_indexes()
                        if self.personality_config.debug_mode:
                            self.set_message_content(self.build_a_document_block(f"Execution result:",None,f"{indexes}"), msg_type=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI)
                        output = self.fast_gen(full_prompt+first_generation+f"{self.config.start_header_id_template}es: indexes {indexes}\n"+context_details.ai_prefix, callback=self.sink).replace("\\_","_")
                    except Exception as ex:
                        self.set_message_content(f"## Execution result:\n{ex}")
                        output = self.fast_gen(full_prompt+first_generation+f"{self.config.start_header_id_template}es: error {ex}\n"+context_details.ai_prefix, callback=self.sink).replace("\\_","_")
                
                if fn=="view_mapping":
                    self.step("The LLM issued a view mapping command")
                    if len(params)>=1:
                        try:
                            mappings = es.view_mapping(params[0])
                            if self.personality_config.debug_mode:
                                self.set_message_content(self.build_a_document_block(f"Execution result:",None,"")+f"\n```json\n{mappings}\n```\n", msg_type=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI)
                            output = self.fast_gen(full_prompt+first_generation+f"{self.config.start_header_id_template}es: mapping\n{mappings}\n"+context_details.ai_prefix, callback=self.sink).replace("\\_","_")
                        except Exception as ex:
                            if self.personality_config.debug_mode:
                                self.set_message_content(f"## Execution result:\n{ex}")
                            output = self.fast_gen(full_prompt+first_generation+f"{self.config.start_header_id_template}es: error {ex}\n"+context_details.ai_prefix).replace("\\_","_")
                    else:
                        ASCIIColors.warning("The AI issued the wrong number of parameters.\nTrying again")
                        self.set_message_content("The AI issued the wrong number of parameters.\nTrying again")
                        failed=True

                if fn=="query":
                    self.step("The LLM issued a query command")
                    if len(params)>=2:
                        try:
                            qoutput = es.query(params[0], params[1])
                            if self.personality_config.debug_mode:
                                self.set_message_content(self.build_a_document_block(f"Execution result:",None,f"")+f"\n```json\n{qoutput}\n```\n", msg_type=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI)
                            if "hits" in qoutput.body and len(qoutput.body["hits"]["hits"])>0:
                                self.step("Found hits")
                                if self.personality_config.output_format=="markdown":
                                    output = "# Output Report"
                                elif self.personality_config.output_format=="html":
                                    reformulation=self.fast_gen(full_prompt+"{self.config.start_header_id_template}Instruction: Reformulate the user request into a paragraph. Make sure you state the objectives clearely.\nRespond with only a clear explanation of the user request without comments.\n"+context_details.ai_prefix, callback=self.sink)
                                    output = "\n".join([
                                        "<h1>Output Report</h1>",
                                        f"<div>{reformulation}</div>",
                                        ""
                                        ])
                                else:
                                    output = "# Output Report"
                                nb_hits = len(qoutput.body["hits"]["hits"])
                                for i,hit in enumerate(qoutput.body["hits"]["hits"]):
                                    ASCIIColors.success(f"HIT:{hit}")
                                    self.step(f"Processing hit {i}/{nb_hits}")
                                    if self.personality_config.output_format=="markdown":
                                        prompt = full_prompt+first_generation+f"\n".join([
                                            f"{self.config.start_header_id_template}response hit entry number {i}/{nb_hits}:\n{hit}",
                                            f"{self.config.start_header_id_template}instructions:",
                                            "Create an informative title and write a concise yet detailed summary of the content of this hit entry in markdown format, while also identifying any relevant information or metadata associated with the entry, reporting any file paths or URLs if they exist in the entry, and avoiding any code or JSON text in your response.",
                                            "If you find any URLs in the entry, build a link and include it in your report.",
                                            context_details.ai_prefix
                                        ])
                                    elif self.personality_config.output_format=="html":
                                        prompt = full_prompt+first_generation+f"\n".join([
                                            f"{self.config.start_header_id_template}response hit entry:\n{hit}",
                                            f"{self.config.start_header_id_template}instructions:",
                                            "Create an informative title and write a concise yet detailed summary of the content of this hit entry in html format, while also identifying any relevant information or metadata associated with the entry, reporting any file paths or URLs if they exist in the entry, and avoiding any code or JSON text in your response.",
                                            "If you find any URLs in the entry, build a link and include it in your report.",
                                            "The html should not contain HTML, head or body tags.",
                                            "The title should be inside a div with class title and without Title: prefix",
                                            "The content should be inside a div with class content",
                                            "The links and references should be put inside a div with class bibliography",
                                            "The bibliography should have a h2 header with the title References.",
                                            context_details.ai_prefix
                                        ])
                                        content = "\n".join([
                                            '<div class="article">',
                                            self.fast_gen(prompt, callback=self.sink).replace("\\_","_"),
                                            '</div>',
                                        ])
                                        output += content
                                    else:
                                        prompt = full_prompt+first_generation+f"\n".join([
                                            f"{self.config.start_header_id_template}response hit entry:\n{hit}",
                                            f"{self.config.start_header_id_template}instructions:",
                                            "Create an informative title and write a concise yet detailed summary of the content of this hit entry in markdown format, while also identifying any relevant information or metadata associated with the entry, reporting any file paths or URLs if they exist in the entry, and avoiding any code or JSON text in your response.",
                                            "If you find any URLs in the entry, build a link and include it in your report.",
                                            context_details.ai_prefix
                                        ])
                                        output += self.fast_gen(prompt, callback=self.sink).replace("\\_","_")+"\n\n"
                                if self.personality_config.output_folder_path!="":
                                    # Get the current date
                                    current_date = datetime.now()

                                    # Format the date as 'year_month_day'
                                    formatted_date = current_date.strftime('%Y_%m_%d_%H_%M_%S')
                                    if self.personality_config.output_format=="markdown":
                                        with open(Path(self.personality_config.output_folder_path)/f"result_{formatted_date}.md","w") as f:
                                            f.write(output)
                                    elif self.personality_config.output_format=="html":
                                        color_scheme = {
                                            'background': '#e6f2ff',
                                            'text': '#333333',
                                            'primary': '#0066cc',
                                            'secondary': '#666666',
                                            'accent': '#ff6600',
                                            'article_bg': '#b3cccc',
                                            'article_shadow': 'rgba(0, 0, 0, 0.1)',
                                        }

                                        styles = "\n".join([
                                            "body {",
                                            f"background-color: {color_scheme['background']};",
                                            f"color: {color_scheme['text']};",
                                            "font-family: Arial, sans-serif;",
                                            "font-size: 16px;",
                                            "line-height: 1.5;",
                                            "}",
                                            "h1 {",
                                            f"color: {color_scheme['primary']};",
                                            "font-size: 36px;",
                                            "text-align: center;",
                                            "text-shadow: 2px 2px 4px {color_scheme['article_shadow']};",
                                            "}",
                                            ".primary {",
                                            f"color: {color_scheme['primary']};",
                                            "}",
                                            ".secondary {",
                                            f"color: {color_scheme['secondary']};",
                                            "}",
                                            ".accent {",
                                            f"color: {color_scheme['accent']};",
                                            "}",
                                            ".article {",
                                            f"background-color: {color_scheme['article_bg']};",
                                            "border-radius: 10px;",
                                            f"box-shadow: 2px 2px 5px {color_scheme['article_shadow']};",
                                            "width: 80%;",
                                            "margin: 0 auto 20px auto;",
                                            "padding: 20px;",
                                            "}",
                                            ".title {",
                                            f"color: {color_scheme['primary']};",
                                            "font-size: 24px;",
                                            "margin-bottom: 12px;",
                                            "text-align: left;",
                                            "}",
                                            ".content {",
                                            f"color: {color_scheme['text']};",
                                            "}",
                                            ".bibliography {",
                                            "    background-color: transparent;",
                                            "    font-style: italic;",
                                            "}"
                                        ])
                                        full_html = "\n".join([
                                            "<html>\n",
                                            "<head>\n",
                                            "<style>\n",
                                            styles,
                                            "</style>\n",
                                            "</head>\n",
                                            "<body>\n",
                                            output,
                                            "\n</body>\n",
                                            "</html>",                                            
                                        ])
                                        self.set_message_content(full_html)
                                        with open(Path(self.personality_config.output_folder_path)/f"result_{formatted_date}.html","w") as f:
                                            f.write(full_html)
                                    else:
                                        with open(Path(self.personality_config.output_folder_path)/f"result_{formatted_date}.md","w") as f:
                                            f.write(output)
                            else:
                                self.step("No Hits found")
                                prompt = full_prompt+first_generation+f"{self.config.start_header_id_template}es: query output:\n{qoutput}\n"+context_details.ai_prefix
                                output = self.fast_gen(prompt, callback=self.sink).replace("\\_","_")
                        except Exception as ex:
                            ASCIIColors.error(ex)
                            failed=True
                            full_prompt += first_generation+f"{self.config.start_header_id_template}es: error {ex}\n"+"The error needs to be fixed. This is very important.\n"+context_details.ai_prefix
                            output = f"The AI issued a wrong command.\nRetrying... {nb_failures}/{self.personality_config.max_nb_failures}"
                    else:
                        ASCIIColors.warning("The AI issued the wrong number of parameters.\nTrying again")
                        output = f"The AI issued the wrong number of parameters.\nRetrying... {nb_failures}/{self.personality_config.max_nb_failures}"
                        failed=True
            else:
                output = first_generation
            self.new_message("")
            self.set_message_content(output)

        return output

