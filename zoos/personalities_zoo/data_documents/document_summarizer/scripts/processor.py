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
from lollms.prompting import LollmsContextDetails
import subprocess
from typing import Callable, Any
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
        # Example entries
        #       {"name":"make_scripted","type":"bool","value":False, "help":"Makes a scriptred AI that can perform operations using python script"},
        #       {"name":"make_scripted","type":"bool","value":False, "help":"Makes a scriptred AI that can perform operations using python script"},
        # Supported types:
        # str, int, float, bool, list
        # options can be added using : "options":["option1","option2"...]        
        personality_config_template = ConfigTemplate(
            [
                {"name":"global_context","type":"str","value":"", "help":"The context information that will be used all over the discussion. Provide useful information about the document that can help enhance the quality of the analysis"},
                {"name":"use_whole_conversation","type":"bool","value":True, "help":"If true, the personality will use the whole previous discussion messages to answer you.\nSome times it is better to activate this to avoid task contamination between questions."},
                {"name":"analysis_type","type":"str","value":"automatic", "options":["automatic","Always read and summarize","RAG","Just Answer"], "help":"sets the algorithm used to solve the task"},
                {"name":"zip_size","type":"int","value":512, "help":"the maximum size of the summary in tokens"},
                {"name":"chunk_size","type":"int","value":0, "help":"the size of each chunk to summarize in tokens. If 0, then the context size will be used as reference."},
                {"name":"output_path","type":"str","value":"", "help":"The path to a folder where to put the summary file."},
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

    def bulletpoints(self, chunks, summary_instruction="", chunk_name="chunk", answer_start="", max_generation_size=3000):
        summeries = []
        for i, chunk in enumerate(chunks):
            self.step_start(f"Processing chunk : {i+1}/{len(chunks)}")
            txt= "\n".join([
                            f"{self.config.start_header_id_template}{chunk_name}:",
                            f"{chunk}",
                            f"{self.config.start_header_id_template}{self.config.system_message_template}{self.config.end_header_id_template}{summary_instruction}",
                            f"{self.config.start_header_id_template}information in bullet points:",
                            f"```markdown\n{answer_start}"
                            ])
            ASCIIColors.magenta(txt)
            summary = f"```markdown\n{answer_start}"+ self.fast_gen(
                        txt,
                            max_generation_size=max_generation_size).replace("```markdown\n```markdown","```markdown").replace("```\n```","```")
            summary = self.extract_code_blocks(summary)
            if len(summary)>0:
                summeries.append(summary[0]["content"].replace("```",""))
                self.step_end(f"Processing chunk : {i+1}/{len(chunks)}")
            else:
                raise Exception("The model returned an empty or corrupted text")
        return "\n".join(summeries)
    
    def analyze_doc(self, prompt, context_details, document_path:Path,  output =""):
        document_text = GenericDataLoader.read_file(document_path)
        tk = self.personality.model.tokenize(document_text)
        self.step_start(f"summerizing {document_path.stem}")
        if len(tk)<int(self.personality_config.zip_size):
                document_text = self.summarize_text(document_text,"summarize this document chunk and do not add any comments after the summary.\nOnly extract the information from the provided chunk.\nDo not invent anything outside the provided text.","document chunk")
        else:
            depth=0
            while len(tk)>int(self.personality_config.zip_size):
                self.step_start(f"Comprerssing.. [depth {depth}]")
                chunk_size = int(self.personality.config.ctx_size*0.6) if self.personality_config.chunk_size==0 else self.personality_config.chunk_size
                document_chunks = DocumentDecomposer.decompose_document(document_text, chunk_size, 0, self.personality.model.tokenize, self.personality.model.detokenize, True)
                document_text = self.bulletpoints(document_chunks,"\n".join([
                        f"{self.config.start_header_id_template}global context: {self.personality_config.global_context}",
                        f"Extract the informations needed to fullfill the document anlysis from the current chunk in form of bullet points.",
                        "Do not answer the user question, just perform information scraping.",
                        "If you detect the document title in this chunks do not strip it aout and just keep it as a separate bullet point.",
                        "The ouput should contain exclusively information from the document chunk.",
                        "Do not provide opinions nor extra information that is not in the document chunk",
                        f"{self.config.start_header_id_template}discussion:",
                        context_details.discussion_messages if self.personality_config.global_context else prompt
                    ]),
                    "Document chunk"
                    )
                tk = self.personality.model.tokenize(document_text)
                self.step_end(f"Comprerssing.. [depth {depth}]")
                self.set_message_content(output+f"\n\n## Information extracted from chunk :\n{document_text}")
                depth += 1
                self.step_start(f"Last composition")
                document_text = self.fast_gen("\n".join([
                f"{self.config.start_header_id_template}global context: {self.personality_config.global_context}",
                f"{self.config.start_header_id_template}{self.config.system_message_template}{self.config.end_header_id_template}Use the bulletpoint information to analyze the document and answer the user request.",
                f"Analyze the document taking into consideration the context information from the discussion.",
                f"{self.config.start_header_id_template}discussion:",
                context_details.discussion_messages if self.personality_config.global_context else prompt,
                f"{self.config.start_header_id_template}information extracted from document:",
                document_text,
                f"{self.config.start_header_id_template}Response:\n"
                ""
            ]))
        self.step_end(f"Last composition")
        self.step_end(f"summerizing {document_path.stem}")
        if self.personality_config.output_path:
            self.save_text(document_text, Path(self.personality_config.output_path)/(document_path.stem+"_analysis.txt"))
        return document_text, output
                    
    def zip_document(self, previous_discussion, document_path:Path,  output =""):
        document_text = GenericDataLoader.read_file(document_path)
        tk = self.personality.model.tokenize(document_text)
        self.step_start(f"summerizing {document_path.stem}")
        document_text = self.summarize_text(document_text,"summarize this document chunk and do not add any comments after the summary.\nOnly extract the information from the provided chunk.\nDo not invent anything outside the provided text.","document chunk")
        self.step_end(f"summerizing {document_path.stem}")
        self.step_start(f"Last composition")
        document_text = self.fast_gen("\n".join([
                f"Rewrite this document in a better way while respecting the following guidelines:",
                f"Analyze the document taking into consideration the context information from the discussion",
                f"{self.config.start_header_id_template}discussion:",
                previous_discussion
            ]))
        self.step_end(f"Last composition")
        self.step_end(f"summerizing {document_path.stem}")
        if self.personality_config.output_path:
            self.save_text(document_text, Path(self.personality_config.output_path)/(document_path.stem+"_analysis.txt"))
        return document_text, output

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
            if self.personality_config.analysis_type=="Always read and summarize":
                index = 1
            elif self.personality_config.analysis_type=="RAG":
                index = 2
            else:
                self.step_start("Analyzing request")
                index = self.multichoice_question("classify this prompt:\n",
                                                        [
                                                            f"{self.personality.config.user_name} is asking a question about the document",
                                                            f"{self.personality.config.user_name} is asking to analyze the document", 
                                                            f"{self.personality.config.user_name} is just asking for information or chatting",
                                                        ],
                                                        f"{self.config.start_header_id_template}{self.personality.config.user_name}: "+prompt)
            if index==1:
                self.step_end("Analyzing request")
                self.personality.step_start("Analyzing the document ...")
                summary, output = self.analyze_doc(prompt, context_details,self.personality.text_files[0])
                out = summary
                self.set_message_content(out)
                self.personality.step_end("Generating ...")
            else:
                self.step_end("Analyzing request")
                self.personality.step_start("Generating a response ...")
                out = self.fast_gen(f"{self.config.start_header_id_template}global context: {self.personality_config.global_context}\n"+previous_discussion_text)
                self.set_message_content(out)
                self.personality.step_end("Generating ...")
                
        else:
            self.personality.step_start("Generating ...")
            out = self.fast_gen(f"{self.config.start_header_id_template}global context: {self.personality_config.global_context}\n"+previous_discussion_text)
            self.set_message_content(out)
        return out

