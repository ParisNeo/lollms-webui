from lollms.config import TypedConfig, BaseConfig, ConfigTemplate, InstallOption
from lollms.types import MSG_OPERATION_TYPE
from lollms.personality import APScript, AIPersonality
from lollms.paths import LollmsPaths
from lollms.types import MSG_OPERATION_TYPE
from typing import Callable, Any

from ascii_colors import ASCIIColors, trace_exception
from safe_store import TextVectorizer, VectorizationMethod, GenericDataLoader

import numpy as np
import json
from pathlib import Path
import numpy as np
import json
import subprocess
from urllib.parse import quote

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
        
        self.word_callback = None    

        personality_config_template = ConfigTemplate(
            [
                {"name":"use_batch_mode","type":"bool","value":False, "help":"if selected, the chatwith docs will takes a list of questions out of a text file and answers them all then writes a final report about the questions"},
                {"name":"batch_mode_questions_file","type":"str","value":"", "help":"A path to a text file containing the list of questions"},
                {"name":"batch_mode_report_file","type":"str","value":"", "help":"A path to a markdown file to be created."},
                {"name":"custom_discussion_db_name","type":"str","value":"", "help":"if not empty, you can change this to the path of the database you want to create or use"},
                {"name":"build_keywords","type":"bool","value":True, "help":"If true, the model will first generate keywords before searching"},
                {"name":"load_db","type":"bool","value":False, "help":"If true, the vectorized database will be loaded at startup"},
                {"name":"save_db","type":"bool","value":False, "help":"If true, the vectorized database will be saved for future use"},
                {"name":"vectorization_method","type":"str","value":f"model_embedding", "options":["model_embedding", "tfidf_vectorizer"], "help":"Vectoriazation method to be used (changing this should reset database)"},
                {"name":"show_interactive_form","type":"bool","value":False, "help":"If true, a window wil be shown with the data plot in an interactive form"},
                
                {"name":"nb_chunks","type":"int","value":2, "min":1, "max":50,"help":"Number of data chunks to use for its vector (at most nb_chunks*max_chunk_size must not exeed two thirds the context size)"},
                {"name":"database_path","type":"str","value":f"{personality.name}_db.json", "help":"Path to the database"},
                {"name":"max_chunk_size","type":"int","value":512, "min":10, "max":personality.config["ctx_size"],"help":"Maximum size of text chunks to vectorize"},
                {"name":"chunk_overlap_sentences","type":"int","value":1, "min":0, "max":personality.config["ctx_size"],"help":"Overlap between chunks"},
                
                {"name":"max_answer_size","type":"int","value":512, "min":10, "max":personality.config["ctx_size"],"help":"Maximum number of tokens to allow the generator to generate as an answer to your question"},
                
                {"name":"data_visualization_method","type":"str","value":f"PCA", "options":["PCA", "TSNE"], "help":"The method to be used to show data"},
                {"name":"interactive_mode_visualization","type":"bool","value":False, "help":"If true, you can get an interactive visualization where you can point on data to get the text"},
                {"name":"visualize_data_at_startup","type":"bool","value":False, "help":"If true, the database will be visualized at startup"},
                {"name":"visualize_data_at_add_file","type":"bool","value":False, "help":"If true, the database will be visualized when a new file is added"},
                {"name":"visualize_data_at_generate","type":"bool","value":False, "help":"If true, the database will be visualized at generation time"},
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
                                        "show_database": self.show_database,
                                        "set_database": self.set_database,
                                        "clear_database": self.clear_database,
                                        "show_files":self.show_files,
                                        "process_batch":self.process_batch,
                                    },
                                    "default": self.chat_with_doc
                                },                           
                            ],
                            callback=callback
                        )
        self.state = 0
        self.ready = False
        self.personality = personality
        self.callback = None
        self.vector_store = None


    def install(self):
        super().install()

        requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Step 2: Install dependencies using pip from requirements.txt
        subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])            

        ASCIIColors.success("Installed successfully")

    

    def help(self, prompt, full_context):
        self.set_message_content(self.personality.help, callback=self.callback)
        
    def process_batch(self, prompt, full_context):
        output = ""
        if self.personality_config.batch_mode_questions_file=="":
            self.new_message("Please set a questions list file to my configuration to start batch qna")
            return
        self.new_message("")
        questions = GenericDataLoader.read_file(self.personality_config.batch_mode_questions_file)
        questions = questions.split("\n")
        for i, question in enumerate(questions):
            if len(question)>5:
                output += "## Question:\n"+question+"\n"
                self.set_message_content(output)
                self.step_start(f"Analyzing request {i+1}/{len(questions)}")
                if self.personality_config.build_keywords:
                    query = self.personality.fast_gen("{self.config.start_header_id_template}prompt:"+question+"{self.config.separator_template}{self.config.start_header_id_template}instruction: Convert the prompt to a web search query."+"\nDo not answer the prompt. Do not add explanations. Use comma separated syntax to make a list of keywords in the same line.\nThe keywords should reflect the ideas written in the prompt so that a seach engine can process them efficiently.{self.config.separator_template}{self.config.start_header_id_template}query: ", max_generation_size=256, show_progress=True)
                    preprocessed_prompt = self.fast_gen(query, int(self.personality_config["max_answer_size"]),show_progress=True).strip()
                    output += "### Query:\n"+preprocessed_prompt+"\n"
                    self.set_message_content(output)
                else:
                    preprocessed_prompt = question
                if preprocessed_prompt=="":
                    preprocessed_prompt = prompt
                docs, sorted_similarities, document_ids = self.vector_store.recover_text(preprocessed_prompt, top_k=int(self.personality_config.nb_chunks))
                docs = '\n'.join([f"{self.config.start_header_id_template}document {s[0]}:\n{v}" for i,(v,s) in enumerate(zip(docs,sorted_similarities))])
                full_text =f"""{docs}
{full_context}"""

                tk = self.personality.model.tokenize(full_text)
                # print(f"total: {len(tk)}")           
                ASCIIColors.blue("-------------- Documentation -----------------------")
                ASCIIColors.blue(full_text)
                ASCIIColors.blue(f"Number of tokens :{len(tk)}")
                ASCIIColors.blue("----------------------------------------------------")
                tk = self.personality.model.tokenize(full_text)
                ASCIIColors.info(f"Documentation size in tokens : {len(tk)}")
                if self.personality.config.debug:
                    ASCIIColors.yellow(full_text)
                answer = self.fast_gen(full_text, self.personality_config["max_answer_size"],show_progress=True).strip()
                output += "## Answer:\n"+answer+"\n"
                self.set_message_content(output)
                docs_sources=[]
                for entry in sorted_similarities:
                    e = "_".join(entry[0].replace("\\","/").split("/")[-1].split('_')[:-2])
                    ci = "_".join(entry[0].replace("\\","/").split("/")[-1].split('_')[-2:])
                    name = "/uploads/" + self.personality.personality_folder_name + "/" + e
                    path = e + f" chunk id : {ci}"
                    docs_sources.append([path, name])

                output += "\n### Used References:\n" + "\n".join([f'[{v[0]}]({quote(v[1])})\n' for v in docs_sources])
                ASCIIColors.yellow(output)

                self.step_end(f"Analyzing request {i+1}/{len(questions)}")
                self.set_message_content(output)                
        self.step_start("Saving report")
        if self.personality_config.batch_mode_report_file!="":
            with open(self.personality_config.batch_mode_report_file, "w") as f:
                f.write(output)
        self.step_end("Saving report")

    def show_database(self, prompt, full_context):
        import random
        if self.ready:
            out_pth = self.personality.lollms_paths.personal_uploads_path/f"{self.personality.personality_folder_name}/"
            out_pth.mkdir(parents=True, exist_ok=True)
            out_path = f"/uploads/{self.personality.personality_folder_name}/"
            end = random.randint(0,99999)
            out_path+=f"db{end}.png"
            self.vector_store.show_document(save_fig_path=out_pth/"db.png",show_interactive_form=self.personality_config.show_interactive_form)
            if self.personality_config.data_visualization_method=="PCA":
                self.set_message_content(f"Database representation (PCA):\n![{out_path}]({out_path})", callback=self.callback)
            else:
                self.set_message_content(f"Database representation (TSNE):\n![{out_path}]({out_path})", callback=self.callback)

    def set_database(self, prompt, full_context):
        self.goto_state("waiting_for_file")

    def clear_database(self,prompt, full_context):
        self.vector_store.clear_database()
        self.set_message_content("Starting fresh")
        
    def show_files(self,prompt, full_context):
        files = "\n".join([f.name for f in self.personality.text_files])
        self.set_message_content(files)
        

    def chat_with_doc(self, prompt, full_context):
        if self.vector_store.ready:
            if prompt == "":
                self.exception("Please send a prompt to process")
            self.step_start("Analyzing request", callback=self.callback)
            if self.personality_config.build_keywords:
                full_text =f"""{self.config.start_header_id_template}instructor:Extract keywords from this prompt. The keywords output format is comma separated values.
{self.config.start_header_id_template}prompt: {prompt}
{self.config.start_header_id_template}assistant: The keywords are """
                preprocessed_prompt = self.generate(full_text, int(self.personality_config["max_answer_size"])).strip()
            else:
                preprocessed_prompt = prompt
            self.step_end("Analyzing request", callback=self.callback)
            if preprocessed_prompt=="":
                preprocessed_prompt = prompt
            self.set_message_content(f"Query : {preprocessed_prompt}")

            docs, sorted_similarities, document_ids = self.vector_store.recover_text(preprocessed_prompt, top_k=int(self.personality_config.nb_chunks))
            # for doc in docs:
            #     tk = self.personality.model.tokenize(doc)
            #     print(len(tk))
            docs = '\n'.join([f"{self.config.start_header_id_template}document chunk {s[0]}:\n{v}" for i,(v,s) in enumerate(zip(docs,sorted_similarities))])
            full_text =f"""{docs}
{full_context}
{self.config.start_header_id_template}chat_with_docs:"""

            tk = self.personality.model.tokenize(full_text)
            # print(f"total: {len(tk)}")           
            ASCIIColors.blue("-------------- Documentation -----------------------")
            ASCIIColors.blue(full_text)
            ASCIIColors.blue(f"Number of tokens :{len(tk)}")
            ASCIIColors.blue("----------------------------------------------------")
            ASCIIColors.blue("Thinking")
            tk = self.personality.model.tokenize(full_text)
            ASCIIColors.info(f"Documentation size in tokens : {len(tk)}")
            if self.personality.config.debug:
                ASCIIColors.yellow(full_text)
            output = self.generate(full_text, self.personality_config["max_answer_size"]).strip()
            docs_sources=[]
            for entry in sorted_similarities:
                e = "_".join(entry[0].replace("\\","/").split("/")[-1].split('_')[:-2])
                ci = "_".join(entry[0].replace("\\","/").split("/")[-1].split('_')[-2:])
                name = "/uploads/" + self.personality.personality_folder_name + "/" + e
                path = e + f" chunk id : {ci}"
                docs_sources.append([path, name])

            output += "\n## Used References:\n" + "\n".join([f'[{v[0]}]({quote(v[1])})\n' for v in docs_sources])

            ASCIIColors.yellow(output)

            self.step_end("Thinking", callback=self.callback)
            self.set_message_content(output, callback=self.callback)
        else:
            self.set_message_content("Vector store is not ready. Please send me a document to use. Use Send file command form your chatbox menu to trigger this.", callback=self.callback)

    def build_db(self):
        if self.vector_store is None:
            root_db_folder = self.personality.lollms_paths.self.personal_discussions_path/self.personality.personality_folder_name
            root_db_folder.mkdir(exist_ok=True, parents=True)
            self.vector_store = TextVectorizer(                     
                    self.personality_config.vectorization_method, # supported "model_embedding" or "tfidf_vectorizer"
                    model=self.personality.model, #needed in case of using model_embedding
                    database_path=root_db_folder/"db.json" if self.personality_config.custom_discussion_db_name=="" else self.personality_config.custom_discussion_db_name,
                    save_db=self.personality_config.save_db,
                    visualize_data_at_startup=self.personality_config.visualize_data_at_startup,
                    visualize_data_at_add_file=self.personality_config.visualize_data_at_add_file,
                    visualize_data_at_generate=self.personality_config.visualize_data_at_generate
                    )        
        if len(self.vector_store.chunks)>0:
            self.ready = True

        ASCIIColors.info("-> Vectorizing the database")
        for file in self.personality.text_files:
            try:
                text =  GenericDataLoader.read_file(file)
                try:
                    chunk_size=int(self.personality_config["max_chunk_size"])
                except:
                    ASCIIColors.warning(f"Couldn't read chunk size. Verify your configuration file")
                    chunk_size=512
                try:
                    overlap_size=int(self.personality_config["chunk_overlap_sentences"])
                except:
                    ASCIIColors.warning(f"Couldn't read chunk size. Verify your configuration file")
                    overlap_size=50

                self.vector_store.add_document(file, text, chunk_size=chunk_size, overlap_size=overlap_size)
                
                ASCIIColors.success(f"File {file} added successfully")
            except Exception as ex:
                ASCIIColors.error(f"Couldn't add {file}: The vectorizer threw this exception:{ex}")
                trace_exception(ex)
                return False
        try:
            self.vector_store.index()
            self.ready = True
            ASCIIColors.success(f"Database indexed successfully")
            return True
        except Exception as ex:
            ASCIIColors.error(f"Couldn't vectorize database The vectorizer threw this exception:{ex}")
            trace_exception(ex)
            return False
            
    def add_file(self, path, client, callback=None):
        if callback is None and self.callback is not None:
            callback = self.callback
        super().add_file(path, client)
        self.prepare()
        try:
            self.new_message("",MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI)
            self.step_start("Vectorizing database", callback = callback)
            if not self.build_db():
                self.step_end("Vectorizing database",status=False, callback = callback)
            else:
                self.step_end("Vectorizing database",status=True, callback = callback)
            self.ready = True
            self.finished_message("File imported successfully")
            return True
        except Exception as ex:
            ASCIIColors.error(f"Couldn't vectorize the database: The vectgorizer threw this exception: {ex}")
            trace_exception(ex)
            self.finished_message("Error importing message")
            return False        

    def prepare(self):
        if self.vector_store is None:
            root_db_folder = self.personality.lollms_paths.personal_discussions_path/self.personality.personality_folder_name
            root_db_folder.mkdir(exist_ok=True, parents=True)
            self.vector_store = TextVectorizer(                     
                    self.personality_config.vectorization_method, # supported "model_embedding" or "tfidf_vectorizer"
                    model=self.personality.model, #needed in case of using model_embedding
                    database_path=root_db_folder/"db.json" if self.personality_config.custom_discussion_db_name=="" else self.personality_config.custom_discussion_db_name,
                    save_db=self.personality_config.save_db
            )        


        if self.vector_store and self.personality_config.vectorization_method==VectorizationMethod.TFIDF_VECTORIZER:
            from safe_store.tf_idf_vectorizer import TfidfVectorizer
            data = list(self.vector_store.texts.values())
            if len(data)>0:
                self.vectorizer = TfidfVectorizer()
                self.vectorizer.fit(data)

        if len(self.vector_store.chunks)>0:
            self.ready = True

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
        # State machine
        self.callback = callback
        self.prepare()

        self.process_state(prompt, full_context, callback)

        return ""



