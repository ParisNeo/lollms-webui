from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality
from lollms.prompting import LollmsContextDetails
from lollms.types import MSG_OPERATION_TYPE
from typing import Callable, Any

from safe_store import chunk_text, parse_document
import subprocess
from pathlib import Path
import json
import pipmaster as pm

if not pm.is_installed("watchdog"):
    pm.install("watchdog")
    
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Helper functions
class Processor(APScript, FileSystemEventHandler):
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
                {"name":"logs_path","type":"str","value":"", "help":"The path to a folder containing the logs"},
                {"name":"output_file_path","type":"str","value":"", "help":"The path to a text file that will contain the final report of the AI"},
                {"name":"file_types","type":"str","value":"pdf", "help":"The extensions of files to read"},
                {"name":"chunk_size","type":"int","value":3072, "help":"The size of the chunk to read each time"},
                {"name":"chunk_overlap","type":"int","value":256, "help":"The overlap between blocs"},
                {"name":"save_each_n_chunks","type":"int","value":0, "help":"The number of chunks to process before saving the file. If 0, then the report is built at the end and a soingle report will be built for all logs."},
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
                                        "read_all_logs":self.read_all_logs,
                                        "start_logs_monitoring":self.start_logs_monitoring,
                                        "stop_logs_monitoring":self.stop_logs_monitoring,
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
        subprocess.run(["pip", "install", "--upgrade", "watchdog"])      
        subprocess.run(["pip", "install", "--upgrade", "dpkt"])      
        
        ASCIIColors.success("Installed successfully")        

    def help(self, prompt="", full_context=""):
        self.set_message_content(self.personality.help)


    def on_modified(self, event):
        if not event.is_directory:
            file_path = Path(event.src_path)
            self.step(f"Detected modification in log file {file_path}")
            self.process_file(file_path)
    
    
    def process_file(self, file: Path):

        prompts = [
            {
                "title":"Importance",
                "content":"What is the importance of the content: high,medium or low? Only answer with the importance level without explanations."
            },
            {
                "title":"Mixture_Of_Experts_Report",
                "content":"Act as a sophisticated document analysis AI, that analyzes document chunks by breaking down complex questions into sub-questions. Leverage multiple expert perspectives to generate intermediate thoughts, evaluating their relevance and logical flow. Construct a chain of reasoning, stitching together the strongest thoughts, while providing explanatory details. Synthesize key insights into a final answer, written by an experienced tech writer at the doctoral level"
            },
            {
                "title":"Thinking_Hat_Report",
                "content":"Act as a multilingual critical and creative thinker that supports intelligence analysis by following a dynamic sequence of the 6 thinking hats to analyze information in the context of intelligence analysis. First, I'll determine the most suitable hat sequence based on the input of the user while also identifying the language of any provided text, which may involve starting with the White Hat to gather facts and data, then switching to the Red Hat to explore emotions and intuition, followed by the Black Hat to examine potential risks, and so on. The sequence may vary, but it will always culminate in the Blue Hat to organize the thinking process. The steps may include (1) White Hat - gather and analyze data, (2) Red Hat - explore emotions and intuition, (3) Black Hat - examine potential risks, (4) Yellow Hat - investigate benefits and advantages, (5) Green Hat - generate new ideas and alternatives, and (6) Blue Hat - organize the thinking process. Depending on the sequence, additional steps may involve (7) White Hat - re-evaluate data in light of new insights, (8) Red Hat - reassess emotions and intuition, (9) Black Hat - re-examine potential risks, (10) Yellow Hat - re-investigate benefits and advantages, (11) Green Hat - refine new ideas and alternatives, and (12) Blue Hat - finalize the thinking process. The 2nd to last step will involve synthesizing the insights from each hat to craft a comprehensive answer at a doctoral level, followed by the final step of providing 4 follow-on question suggestions to facilitate further exploration and deeper understanding. Throughout the process, I'll maintain a neutral and objective tone, while encouraging creative and innovative thinking"
            },
            {
                "title":"Multistage_Expert_Analysis_Report",
                "content":"Act as a sophisticated document analysis AI that analyzes document chunks using stages 1-10 without pausing. Stage 1 involves breaking down complex questions into 4-6 sub-questions. Stage 2 involves Leverage multiple expert perspectives to generate 4-6 intermediate analysis thoughts. Stage 3 involves evaluating their relevance and logical flow. Stage 4 involves Constructing a chain of reasoning, stitching together the strongest thoughts, while providing explanatory details. Stage 5 involves backtracking and exploring 1-2 alternative analytical paths by substituting different intermediate thoughts from alternative expert perspectives. Stage 6 involves Leverage multiple analytical expert perspectives to generate 4-6 intermediate thoughts related to Stage 5. Stage 7 involves evaluating the relevance and logical flow of the alternative intermediate thoughts. Stage 8 involves Constructing a chain of reasoning, stitching together the strongest alternative thoughts, while providing explanatory details. Stage 9 involves leveraging adversarial expert perspectives to generate 4-8 intermediate thoughts debating both the initial and alternative reasoning chains. Stage 10 involves synthesizing key insights into a final comprehensive answer, written by an experienced technical writer at the doctoral level who is experienced in analyzing complex problems and synthesizing key insights into coherent narratives."
            },
            {
                "title":"Multi_Reasoning_Report",
                "content":"Act as a sophisticated document analysis AI that analyzes document chunks using stages 1-10 without pausing. Stage 1 involves breaking down complex questions into 4-6 sub-questions. Stage 2 involves leveraging probabilistic reasoning to generate 4-6 intermediate thoughts. Stage 3 involves evaluating their relevance and logical flow. Stage 4 involves using correlation and causation to generate a chain of reasoning, stitching together the strongest thoughts, while providing explanatory details. Stage 5 involves using doubt to generate 3-5 intermediate thoughts identifying problems with the reasoning. Stage 6 involves using Argumentation to generate 4-8 intermediate thoughts addressing the points raised by Stage 5. Stage 7 involves leveraging 4-5 expert perspectives to generate 4-6 sub-questions to consider alternative paths. Stage 8 involves leveraging deductive reasoning to generate 4-6 intermediate thoughts that answer the sub-questions from Stage 7. Stage 9 involves using analogical reasoning to compare all of the insights gained so far into insightful bullet points. Stage 10 involves synthesizing key insights into a final comprehensive analysis report, written by an experienced all source intelligence analyst at the doctoral level who is experienced in analyzing complex problems and synthesizing key insights into coherent narratives."
            },
            {
                "title":"Intelligence_Value_Report",
                "content":"Act as a multiple disciplined sophisticated AI intelligence analyst that analyzes document chunks using stages 1-10 without pausing. Stage 1 involves breaking information down into 4-6 sub-questions. Stage 2 involves leveraging probabilistic reasoning to generate 4-6 intermediate thoughts answering the sub-questions in relation to the potential intelligence value. Stage 3 involves evaluating their relevance and logical flow. Stage 4 involves using correlation and causation to generate a chain of reasoning, stitching together the strongest thoughts into intelligence report summarized bullet points, while providing explanatory details with each. Stage 5 involves using doubt to generate 3-5 intermediate thoughts identifying problems with the reasoning or intelligence value estimations. Stage 6 involves using Argumentation to generate 4-8 intermediate thoughts addressing the points raised by Stage 5 to further clarify the potential intelligence value of the information. Stage 7 involves leveraging 4-5 expert intelligence analysis perspectives to generate 4-6 sub-questions to consider alternative paths to additional information. Stage 8 involves leveraging deductive reasoning to generate 4-6 intermediate thoughts that answer the sub-questions from Stage 7 while also considering all previous stages. Stage 9 involves using analogical reasoning to explain the intelligence value of the information. Stage 10 involves synthesizing key insights from all stages into a final comprehensive intelligence report summary, written by an experienced analyst at the doctoral level who is experienced in analyzing complex national security problems and synthesizing key insights into coherent narrative."
            },
        ]        
        import hashlib
        hasher = hashlib.md5()
        self.step_start(f"Processing {file.name}")
        data = parse_document(file)
        chunks = chunk_text(
            data,
            self.personality_config.chunk_size,
            self.personality_config.chunk_overlap
        )
        hasher.update(data.encode("utf8"))

                    
        n_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            self.step_start(f"Processing {file.name} chunk {i+1}/{n_chunks}")
            
            prompt_prefix = f"""{self.system_custom_header("instructions")}
Act as DocuSphere, a comprehensive document analysis AI that provides insightful analysis and recommendations on the importance of information contained within documents by examining content, identifying key concepts, evaluating relevance, and synthesizing findings to deliver actionable intelligence.
- Comprehensively analyze the provided document content using the indicated instructions and provide a detailed report.
- Identify any significant patterns or anomalies that may indicate important information or key concepts.
- Provide details about the identified key concepts or important information.
- If applicable, mention the page number, section, or paragraph that contains the relevant information and explain its significance and include any dates and times.
- Be specific and provide clear explanations to support your analysis.
- If no significant information is found, return a statement indicating that no notable insights were discovered.
- Your analysis should be detailed and provide clear evidence to support your conclusions. Remember to consider both explicit and implicit information.
- Be attentive to the content of the document and do not miss important details.
- Answer in a clear and concise format.
- Only report key findings and insights. Do not report obvious or irrelevant information.
- Only report findings that are relevant to the analysis. Do not report general or mundane information.

{self.system_custom_header("output format")}
"""
            
            chunk_prompt = f"""
{self.system_custom_header("text chunk")}
{chunk.text}
Answer in a markdown format without any extra comments following the instruction.
{self.system_custom_header("instructions")}
"""
            for prompt in prompts:
                self.step_start(f"Processing {file.name} chunk {i+1}/{n_chunks}- {prompt['title']}")
                analysis = self.fast_gen(prompt_prefix+chunk_prompt+prompt["content"]+self.ai_full_header)
                try:
                    self.output_file.write("### "+ prompt['title'] + "\n" + prompt["content"]+"\n"+analysis+"\n")
                    self.output_file.flush()

                    if self.personality_config.save_each_n_chunks>0 and i%self.personality_config.save_each_n_chunks==0:
                        self.output_file.close()
                        self.output_file = open(self.output_file_path.parent/(self.output_file_path.stem+f"_{i}"+self.output_file_path.suffix),"w")

                except Exception as ex:
                    ASCIIColors.error(ex)
                self.step_end(f"Processing {file.name} chunk {i+1}/{n_chunks}")
                self.set_message_content(self.output)
            self.output_file.write("\n\n")
            self.output_file.flush()

        self.step_end(f"Processing {file.name}")

    def read_all_logs(self, command="", full_context="", callback=None, context_state="", client=None):
        if self.personality_config.output_file_path=="":
            self.personality.info("Please setup output file path first")
            return
        if self.personality_config.logs_path=="":
            self.personality.info("Please setup logs folder path first")
            return
        self.output = ""
        self.new_message("")
        self.process_logs(
                            self.personality_config.logs_path, 
                            self.personality_config.file_types
                        )

    def stop_logs_monitoring(self, command="", full_context="", callback=None, context_state="", client=None):
        self.observer.stop()

    def start_logs_monitoring(self,  command="", full_context="", callback=None, context_state="", client=None):
        if self.personality_config.output_file_path=="":
            self.personality.info("Please setup output file path first")
            return
        if self.personality_config.logs_path=="":
            self.personality.info("Please setup logs folder path first")
            return
        self.new_message("Starting continuous logs process...")
        self.observer = Observer()
        self.observer.schedule(self, self.personality_config.logs_path, recursive=True)
        self.observer.start()
    
    def process_logs(self, folder_path, extensions):
        folder = Path(folder_path)
        files = folder.glob('*')
        extension_list = [v.strip() for v in extensions.split(',')]

        self.output_file_path = Path(self.personality_config.output_file_path)
        self.output_file = open(self.output_file_path,"w")
        
        self.output = ""

        for file in files:
            if file.is_file() and file.suffix[1:] in extension_list:
                self.process_file(file)

    
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

        ASCIIColors.info("Generating")
        self.callback = callback
        if self.personality_config.output_file_path=="":
            out = self.fast_gen(previous_discussion_text + "Please set the output file path in my settings page.")
            self.set_message_content(out)
            return
        if self.personality_config.logs_path=="":
            out = self.fast_gen(previous_discussion_text + "Please set the logs folder path in my settings page.")
            self.set_message_content(out)
            return

        self.process_logs(
                            self.personality_config.logs_path, 
                            self.personality_config.file_types
                        )


        return ""

