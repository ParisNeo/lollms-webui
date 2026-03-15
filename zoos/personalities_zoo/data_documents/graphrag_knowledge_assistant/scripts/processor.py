from lollms.personality import APScript, AIPersonality
from lollms.config import ConfigTemplate, BaseConfig, TypedConfig
from lollms.types import MSG_OPERATION_TYPE
from typing import Callable
import os
import graphrag
from graphrag.indexer import Indexer
from graphrag.query_engine import QueryEngine
import tempfile
import shutil

class Processor(APScript):
    def __init__(self, personality: AIPersonality, callback: Callable = None) -> None:
        personality_config_template = ConfigTemplate([
            {"name": "index_chunk_size", "type": "int", "value": 1000, "help": "Size of text chunks for indexing"},
            {"name": "query_method", "type": "string", "options": ["global", "local"], "value": "global", "help": "Query method: global or local"},
        ])
        personality_config_vals = BaseConfig.from_template(personality_config_template)
        personality_config = TypedConfig(personality_config_template, personality_config_vals)
        
        super().__init__(
            personality,
            personality_config,
            states_list=[
                {
                    "name": "idle",
                    "commands": {
                        "help": self.help,
                        "index": self.index_data,
                        "query": self.query_data,
                    },
                    "default": None
                },
            ],
            callback=callback
        )
        self.temp_dir = None
        self.indexer = None
        self.query_engine = None

    def mounted(self):
        self.temp_dir = tempfile.mkdtemp()
        self.indexer = Indexer(self.temp_dir)
        self.query_engine = QueryEngine(self.temp_dir)

    def unmounted(self):
        if self.temp_dir:
            shutil.rmtree(self.temp_dir)

    def install(self):
        super().install()
        # Install graphrag if not already installed
        self.personality.install_package("graphrag")

    def help(self, prompt="", full_context=""):
        return """
        GraphRAG Personality Help:
        
        This personality uses GraphRAG to index and query information to answer questions.
        
        Commands:
        - index: Index new data. Usage: index <path_to_data>
        - query: Query the indexed data. Usage: query <your_question>
        
        Example workflow:
        1. Index your data: index /path/to/your/data
        2. Query the indexed data: query What are the main themes in the document?
        """

    def index_data(self, path):
        if not os.path.exists(path):
            self.set_message_content(f"Error: The path '{path}' does not exist.")
            return

        self.step_start("Indexing data")
        try:
            self.indexer.index(path, chunk_size=self.personality_config.index_chunk_size)
            self.set_message_content(f"Successfully indexed data from '{path}'.")
        except Exception as e:
            self.set_message_content(f"Error indexing data: {str(e)}")
        self.step_end("Indexing complete")

    def query_data(self, query):
        if not self.query_engine:
            self.set_message_content("Error: No data has been indexed yet. Please use the 'index' command first.")
            return

        self.step_start("Querying data")
        try:
            result = self.query_engine.query(query, method=self.personality_config.query_method)
            self.set_message_content(f"Query result: {result}")
        except Exception as e:
            self.set_message_content(f"Error querying data: {str(e)}")
        self.step_end("Query complete")

    def run_workflow(self, prompt: str, previous_discussion_text: str = "", callback: Callable[[str, MSG_OPERATION_TYPE, str, AIPersonality], bool] = None, context_details: dict = None, client=None):
        self.callback = callback
        
        # Check if the prompt is a command
        if prompt.startswith("index "):
            path = prompt.split("index ", 1)[1].strip()
            self.index_data(path)
        elif prompt.startswith("query "):
            query = prompt.split("query ", 1)[1].strip()
            self.query_data(query)
        else:
            # If it's not a command, ask the AI what to do
            decision = self.multichoice_question(
                "What should I do with the user's input?",
                ["Treat it as a query", "Provide help", "Ask for clarification"],
                context=prompt,
                max_answer_length=50
            )
            
            if decision == 0:
                self.query_data(prompt)
            elif decision == 1:
                self.help()
            else:
                clarification = self.generate_code(
                    f"Generate a response asking the user to clarify their request. Context: {prompt}",
                    max_size=100
                )
                self.set_message_content(clarification)

    def fast_gen(self, prompt):
        """Quickly generate a response without going through the full workflow."""
        return self.generate_code(prompt, max_size=100)