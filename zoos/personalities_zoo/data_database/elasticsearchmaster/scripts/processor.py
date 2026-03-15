from lollms.helpers import ASCIIColors, trace_exception
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality
from lollms.prompting import LollmsContextDetails
from lollms.utilities import PackageManager
from lollms.types import MSG_OPERATION_TYPE
from typing import Callable, Any
import importlib.util
import subprocess
import tqdm
import ssl

if not PackageManager.check_package_installed("elasticsearch"):
    PackageManager.install_package("elasticsearch")

from elasticsearch import Elasticsearch

import json
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
        self.es = None
        # Example entry
        #       {"name":"make_scripted","type":"bool","value":False, "help":"Makes a scriptred AI that can perform operations using python script"},
        # Supported types:
        # str, int, float, bool, list
        # options can be added using : "options":["option1","option2"...]        
        personality_config_template = ConfigTemplate(
            [
                {"name":"servers","type":"str","value":"https://localhost:9200", "help":"List of addresses of the server in form of ip or host name: port"},
                {"name":"index_name","type":"str","value":"", "help":"The index to be used for querying"},
                {"name":"output_file_path","type":"str","value":"", "help":"The path to a text file that will contain the final report of the AI"},
                {"name":"chunk_size","type":"int","value":1024, "help":"The size of the chunk to read each time"},
                {"name":"chunk_overlap","type":"int","value":256, "help":"The overlap between blocs"},
                {"name":"save_each_n_chunks","type":"int","value":1, "help":"The number of chunks to process before saving the file. If 0, then the report is built at the end and a single report will be built for all logs."},
                {"name":"user","type":"str","value":"", "help":"The user name to connect to the database"},
                {"name":"password","type":"str","value":"", "help":"The password to connect to the elastic search database"},
                
                # Specify the host and port of the Elasticsearch server
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
                                    },
                                    "default": self.idle
                                },                      
                                {
                                    "name": "waiting_for_index_name",
                                    "commands": { # list of commands
                                    },
                                    "default": self.get_index_name
                                },                            
                                {
                                    "name": "waiting_for_mapping",
                                    "commands": { # list of commands
                                    },
                                    "default": self.get_mapping
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
    
    def add_file(self, path, client, callback=None):
        """
        Here we implement the file reception handling
        """
        super().add_file(path, client, callback)

    # ============================ Elasticsearch stuff
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
        
    def create_index(self, index_name):
        try:
            self.es.indices.create(index=index_name)
            self.personality_config.index_name = index_name
            self.personality_config.save()
            return True
        except Exception as ex:
            self.personality.error(str(ex))
            return False

    def set_index(self, index_name):
        self.personality_config.index_name = index_name
        self.personality_config.save()

    def create_mapping(self, mapping):
        try:
            self.es.indices.put_mapping(index=self.personality_config.index_name, body=mapping)
            return True
        except Exception as ex:
            self.personality.error(str(ex))
            return False
    
    def read_mapping(self):
        try:
            mapping = self.es.indices.get_mapping(index=self.personality_config.index_name)
            return mapping

        except Exception as ex:
            self.personality.error(str(ex))
            return None
    
    def perform_query(self, query):
        results = self.es.search(index=self.personality_config.index_name, body=query)
        return results        

    def prepare(self):
        if self.personality_config.servers=="":
            self.error("Please set a server")
        if self.es is None:
            # Create a default SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            self.es = Elasticsearch(
                self.personality_config.servers.replace(" ", "").replace(".","").split(","), 
                http_auth=(self.personality_config.user, self.personality_config.password),
                verify_certs=False)

    def get_index_name(self, prompt, previous_discussion_text=""):
        self.goto_state("idle")
        index_name=self.fast_gen(f"{self.config.start_header_id_template}instruction: extract the index name from the prompt?{self.config.separator_template}{self.config.start_header_id_template}user prompt: {prompt}{self.config.separator_template}{self.config.start_header_id_template}answer: The requested index name is ").split("\n")[0].strip()
        self.operation(index_name.replace("\"","").replace(".",""))
        self.set_message_content("Index created successfully")

    def get_mapping(self, prompt, previous_discussion_text=""):
        self.goto_state("idle")
        output="```json\n{\n    \"properties\": {"+self.fast_gen(f"{self.config.start_header_id_template}instruction: what is the requested mapping in json format?{self.config.separator_template}{self.config.start_header_id_template}user prompt: {prompt}{self.config.separator_template}{self.config.start_header_id_template}answer: The requested index name is :\n```json\n"+"{\n    \"properties\": {")
        output=self.remove_backticks(output.strip())
        self.create_mapping(json.loads(output))
        self.set_message_content("Mapping created successfully")

    def idle(self, prompt, previous_discussion_text=""):
        self.step_start("Analyzing request")
        index = self.multichoice_question("classify this prompt:\n",
                                                [
                                                    f"{self.personality.config.user_name} is asking for listing indexes",
                                                    f"{self.personality.config.user_name} is asking for creating a new index", 
                                                    f"{self.personality.config.user_name} is asking for changing index",
                                                    f"{self.personality.config.user_name} is asking for creating a mapping",
                                                    f"{self.personality.config.user_name} is asking for reading a mapping",
                                                    f"{self.personality.config.user_name} is asking a question about an entry",
                                                    f"{self.personality.config.user_name} is asking to add an entry to the database",
                                                    f"{self.personality.config.user_name} is asking for querying the database",
                                                    f"{self.personality.config.user_name} is just asking for information or chatting",
                                                ],
                                                f"{self.config.start_header_id_template}{self.personality.config.user_name}: "+prompt)
        self.step_end("Analyzing request")

        if index==0:# "The prompt is asking for creating a new index"
            self.step("Analysis result: The prompt is asking for listing indices")
            try:
                indexes = self.es.indices.get_alias(index="*")
                out = "Here is the list of available indexes:\n"
                for index in indexes:
                    out += f"- {index}\n"
                self.set_message_content(out)
            except Exception as ex:
                trace_exception(ex)
                self.set_message_content(f"I couldn't recover the indexes because of the following error:\n<p>{ex}</p>")

        elif index==1:# "The prompt is asking for creating a new index"
            self.step("Analysis result: The prompt is asking for creating a new index")
            if self.yes_no("does the prompt contain the index name?",prompt):
                index_name=self.fast_gen(f"{self.config.start_header_id_template}instruction: what is the requested index name?{self.config.separator_template}{self.config.start_header_id_template}user prompt: {prompt}{self.config.separator_template}{self.config.start_header_id_template}answer: The requested index name is ").split("\n")[0].strip()
                if self.create_index(index_name.replace("\"","").replace(".","")):
                    self.set_message_content("Index created successfully")
                else:
                    self.set_message_content("Unfortunately an error occured and I couldn't build the index. please check the connection to the database as well as the certificate")

            else:
                self.set_message_content("Please provide the index name")
                self.operation = self.create_index
                self.goto_state("waiting_for_index_name")
                return
        elif index==2:# "The prompt is asking for changing index"
            self.step("Analysis result: The prompt is asking for changing index")
            if self.yes_no("does the prompt contain the index name?",prompt):
                index_name=self.fast_gen(f"{self.config.start_header_id_template}instruction: what is the requested index name?{self.config.separator_template}{self.config.start_header_id_template}user prompt: {prompt}{self.config.separator_template}{self.config.start_header_id_template}answer: The requested index name is ").split("\n")[0].strip()
                self.set_index(index_name)
                self.set_message_content("Index set successfully")
            else:
                self.set_message_content("Please provide the index name")
                self.operation = self.set_index
                self.goto_state("waiting_for_index_name")
                return
        elif index==3:# "creating a mapping"
            self.step("Analysis result: The prompt is asking for creating a mapping")
            if self.yes_no("does the prompt contain the mapping information required to build a mapping json out of it?",prompt):
                output="```json\n{\n    \"properties\": {"+self.fast_gen(f"{self.config.start_header_id_template}instruction: what is the requested mapping in json format?{self.config.separator_template}{self.config.start_header_id_template}user prompt: {prompt}{self.config.separator_template}{self.config.start_header_id_template}answer: The requested index name is :\n```json\n"+"{\n    \"properties\": {")
                output=self.remove_backticks(output.strip())
                self.create_mapping(json.loads(output))
                self.set_message_content("Mapping created successfully")
            else:
                self.set_message_content("Please provide the mapping")
                self.operation = self.set_index
                self.goto_state("waiting_for_mapping")
                return
        elif index==4:# "reading a mapping"            
            self.step("Analysis result: The prompt is asking for reading a mapping")
            mapping = self.read_mapping()
            self.set_message_content("```json\n"+json.dumps(mapping.body,indent=4)+"\n```\n")
        elif index==5:# "a question about an entry"
            self.step("Analysis result: The prompt is asking a question about an entry")
        elif index==6:# "add an entry to the database"
            self.step("Analysis result: The prompt is asking to add an entry to the database")
            mapping = self.read_mapping()
            code = "```python\nfrom elasticsearch import Elasticsearch\n"+self.fast_gen("{self.config.start_header_id_template}context!:\n"+previous_discussion_text+f"{self.config.separator_template}{self.config.start_header_id_template}instructions: Make a python function that takes an ElasticSearch object es and perform the right operations to add an entry to the database as asked by the user. The output should be in form of a boolean.{self.config.separator_template}{self.config.start_header_id_template}mapping:{mapping}\nHere is the signature of the function:\ndef add_entry(es:ElasticSearch, index_name):\nDo not provide explanations or usage example.{self.config.separator_template}{self.config.start_header_id_template}elasticsearch_ai:Here is the query function that you are asking for:\n```python\nfrom elasticsearch import Elasticsearch\n", callback=self.sink)
            code = code.replace("ElasticSearch","Elasticsearch")
            code=self.extract_code_blocks(code)

            if len(code)>0:
                # Perform the search query
                code = code[0]["content"].replace("\_","_")
                ASCIIColors.magenta(code)
                module_name = 'custom_module'
                spec = importlib.util.spec_from_loader(module_name, loader=None)
                module = importlib.util.module_from_spec(spec)
                exec(code, module.__dict__)
                if module.add_entry(self.es, self.personality_config.index_name):
                    self.personality.info("Generating")
                    out = f"<div hidden>\n{code}\n</div>\n" + self.fast_gen(f"{self.config.start_header_id_template}{self.config.system_message_template}{self.config.end_header_id_template}Describe the data being added to the database.{self.config.separator_template}{self.config.start_header_id_template}code: {code}"+"{self.config.start_header_id_template}elesticsearchai: ")
                else:
                    out = f"<div hidden>\n{code}\n</div>\n" + "Couldn't add data to the database"
                self.set_message_content(out)
        elif index==7:# "querying the database"
            self.step("Analysis result: The prompt is asking for querying the database")
            code = "```python\nfrom elasticsearch import Elasticsearch\n"+self.fast_gen("{self.config.start_header_id_template}context!:\n"+previous_discussion_text+"{self.config.separator_template}{self.config.start_header_id_template}instructions: Make a python function that takes an ElasticSearch object es and perform the right operations to query the database in order to answer the question of the user. The output should be a string containing the requested information in markdown format.\nHere is the signature of the function:\ndef query(es:ElasticSearch, index_name:str)->str:\nDo not provide explanations or usage example.{self.config.separator_template}{self.config.start_header_id_template}elasticsearch_ai:Here is the query function that you are asking for:\n```python\n", callback=self.sink)
            code = code.replace("ElasticSearch","Elasticsearch")
            code=self.extract_code_blocks(code)

            if len(code)>0:
                # Perform the search query
                code = code[0]["content"].replace("\_","_")
                if self.personality.config.debug:
                    ASCIIColors.yellow(code)
                ASCIIColors.magenta(code)
                module_name = 'custom_module'
                spec = importlib.util.spec_from_loader(module_name, loader=None)
                module = importlib.util.module_from_spec(spec)
                exec(code, module.__dict__)
                search_result = module.query(self.es, self.personality_config.index_name)
                if search_result:
                    # Process the search results
                    docs= f"{self.config.start_header_id_template}query result:\n{search_result}"
                    self.personality.info("Generating")
                    for document in tqdm.tqdm(docs, desc="Processing documents"):
                        chunks = [document[i:i+self.personality_config.chunk_size] for i in range(0, len(document), self.personality_config.chunk_size)]
                        for i,chunk in enumerate(chunks):
                            str_json = "[" + self.fast_gen("\n".join([
                            f"{self.config.start_header_id_template}log chunk:",
                            f"{chunk}",
                            f"{self.config.start_header_id_template}instructions:",
                            "Act as if you are ElasticSearchMaster a cutting-edge artificial intelligence designed to assist analysts identify information related to their query and provide comprehensive analysis.",
                            "- I will make sure my query formulation is accurate and specific. I will ignore entries that are irrevalent to the query.",
                            "- Summarize documents accurately, ensuring clarity, relevance, and logical flow for efficient analysis.",
                            "- Provide the document ID for every document with each chunk",
                            "- Provide analysis only of the information contained within the chunk.",
                            "- Your analysis should be detailed and provide clear evidence to support your conclusion. ",
                            "- As ElasticSearchMaster, I quickly analyze text chunks, identifying relevant information and assessing risk using only information within the current chunk. My focus on query-related information ensures valuable insights and focused results.",
                            "- You must do everything in your power to provide exquisit analytical support on the chunk only.",
                            "- Answer in valid json format.",


                            f"{self.config.start_header_id_template}JSON format:",
                            "[",
                            "    A list of entries.",
                            "Each entry represents an information response that should only be provided if you understand the query and can qualify it with arguments using only the document chunk, if not then you should leave it blank",
                            "{",
                            "   \"Relevance_Level\": Evaluate the document content's relevance to the query and assign relevance value levels as high (High), moderate (moderate), or low (minor). If no determination can be made based on the document chunk then leave it blank,",
                            "   \"Document_Information\": list all document metadata information from the document chunk and if no information can be extracted based on the document chunk then leave it blank,",
                            "   \"Document_Summary\": Provide a detailed summary of the document based on the document chunk. Summarize documents accurately, ensuring clarity, relevance, and logical flow for efficient analysis. If no summary can be generated based on the document chunk then leave it blank,",
                            "}",
                            "]",
                            f"{self.config.start_header_id_template}ElasticSearchMaster:",
                            "Here is my report as a valid json:",
                            "["
                            ])
                            )
                            try:
                                str_json = str_json.replace('\n', '').replace('\r', '').strip()
                                if not str_json.endswith(']'):
                                    str_json +="]"
                                json_output = json.loads(str_json)
                                for entry in json_output:
                                    Document_Information = entry.get('Document_Information','')
                                    Document_Summary = entry.get('Document_Summary','')

                                    self.output_file.write(f"## A {entry['Relevance_Level']} document chunk {i+1} of file {file}\n")
                                    self.output += f"## A {entry['Relevance_Level']} document chunk {i+1} of file {file}\n"
                                    if Document_Information:
                                        self.output_file.write(f"### Document_Information:\n")
                                        self.output_file.write(f"{Document_Information}\n")
                                        self.output += f"### Document_Information:\n"
                                        self.output += f"{entry.get('Document_Information','')}\n"
                                    if Document_Summary:
                                        self.output_file.write(f"### Document_Summary:\n")
                                        self.output_file.write(f"{Document_Summary}\n")
                                        self.output += f"### Document_Summary:\n"
                                        self.output += f"{Document_Summary}\n"
                                    self.output_file.flush()


                                if self.personality_config.save_each_n_chunks>0 and i%self.personality_config.save_each_n_chunks==0:
                                    self.output_file.close()
                                    self.output_file = open(self.output_file_path.parent/(self.output_file_path.stem+f"_{i}"+self.output_file_path.suffix),"w")

                            except Exception as ex:
                                ASCIIColors.error(ex)
                    self.set_message_content(self.output)
                    
                else:
                    out = "Failed to query the database"
                self.set_message_content(out)
        else:
            self.step("Analysis result: The prompt is asking for something else")
            out = self.fast_gen(previous_discussion_text)
            self.set_message_content(out)        
        


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
        if self.personality_config.user=="" or self.personality_config.servers=="":
            self.set_message_content("Sorry, but before talking, I need to get access to your elasticsearch server.\nTo do this:\n- Got to my settings and set the server(s) names in hte format https://server name or ip address:port number. You can give multiple servers separated by coma.\n- Set your user name and password.\n- come back here and we can start to talk.")
        else:
            self.prepare()
            if self.ping():
                self.process_state(prompt, previous_discussion_text)
            else:
                self.set_message_content("I couldn't connect to the server. Please make sure it is on and reachable and that your user name and password are correct")

        return ""

