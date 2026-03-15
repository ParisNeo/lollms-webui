from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality
from lollms.types import MSG_OPERATION_TYPE
from typing import Any
from lollms.prompting import LollmsContextDetails
import subprocess
from pathlib import Path
from typing import Callable, Any

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
                {"name":"candidate_cv","type":"str","value":"", "help":"Path to the candidate CV"},
                {"name":"subject_text","type":"str","value":"", "help":"Path to the job position description"},
                {"name":"language","type":"str","value":"", "help":"language to rewrite the document in"},

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
                                        "start_processing_cvs":self.start_processing_cvs
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
        self.set_message_content(self.personality.help)
    
    def add_file(self, path, client, callback=None):
        """
        Here we implement the file reception handling
        """
        super().add_file(path, client, callback)

    def save_text(self, text, path:Path):
        with open(path,"w", encoding="utf8") as f:
            f.write(text)
            
                    
    def process_cvs(self):
        try:
            output = ""
            cv_list=[]
            orig_cv_path = Path(self.personality_config.candidate_cv)
            if orig_cv_path.is_dir():
                subject_summary, evaluation_grid, output = self.preprocess_subject(orig_cv_path, output)
                for cv_path in orig_cv_path.glob("*.pdf|*.docx"):
                    output, grade = self.process_cv(cv_path,subject_summary, evaluation_grid, output)
                    cv_list.append([cv_path, grade])
                self.save_text(str(cv_list),orig_cv_path/"grades.md")            
            else:
                subject_summary, evaluation_grid, output = self.preprocess_subject(orig_cv_path.parent, output)
                self.process_cv(orig_cv_path, subject_summary, evaluation_grid, output)
        except Exception as ex:
            self.error(str(ex))

    def preprocess_subject(self, output_path, output =""):
        subject_path = Path(self.personality_config.subject_text)
        subject_text = GenericDataLoader.read_file(subject_path)
        self.step_start(f"summerizing position subject {subject_path.stem}")
        subject_chunks = DocumentDecomposer.decompose_document(subject_text,self.personality.config.ctx_size//2,0, self.personality.model.tokenize, self.personality.model.detokenize, True)
        output += f"- Found `{len(subject_chunks)}` chunks in position description\n"
        
        subject_summary = self.summarize_chunks(subject_chunks,"summarize this position description and do not add any comments after the summary.\nThe objective is to identify the skills required for this position. Only extract the information from the provided chunk.\nDo not invent anything outside the provided text.","position description chunk")
        subject_summary = subject_summary.replace("```","")
        output += f"**Position description summary**\n{subject_summary}\n"
        self.set_message_content(output)
        subject_text_path = Path(subject_path)
        self.save_text(subject_summary, output_path/(subject_text_path.stem+"_summary.md"))
        self.step_end(f"summerizing position subject {subject_path.stem}")
        
        self.step_start(f"building evaluation grid {subject_path.stem}")
        evaluation_grid = self.fast_gen(f"{self.config.start_header_id_template}instructions: Given the following position description, build a list of criteria that should be met for the subject to be fit for this position. Use the following columns: Theme, Criteria, Importance, grade. Leave the grade columns empty. Group the criterias by themes and classify them from important to nice to have. Put this in a table markdown format. Do not add tailing comments.\nPosition description:\n{subject_summary}{self.config.separator_template}{self.config.start_header_id_template}interview ai:Requested description in markdown format\n```markdown\n")
        evaluation_grid = evaluation_grid.replace("```","")
        self.save_text(evaluation_grid, output_path/("evaluation_grid.md"))
        self.step_end(f"building evaluation grid {subject_path.stem}")
        
        return subject_summary, evaluation_grid, output
                    
        
    def process_cv(self, cv_path, subject_summary, evaluation_grid, output = ""):
        output_folder = cv_path.parent
        output_path = output_folder/"interview"/cv_path.stem
        output_path.mkdir(parents=True, exist_ok=True)
        
        output += f"# {cv_path.stem}\n"
        
        self.step_start(f"Reading data {cv_path.stem}")
        cv_data = GenericDataLoader.read_file(cv_path)
        self.step_end(f"Reading data {cv_path.stem}")

        self.step_start(f"chunking documents {cv_path.stem}")
        cv_chunks = DocumentDecomposer.decompose_document(cv_data,self.personality.config.ctx_size//2,0, self.personality.model.tokenize, self.personality.model.detokenize, True)
        output += f"- Found `{len(cv_chunks)}` chunks in cv\n"
        self.set_message_content(output)
        self.step_end(f"chunking documents {cv_path.stem}")
        
        self.step_start(f"summerizing cv {cv_path.stem}")
        cv_summary = self.summarize_chunks(cv_chunks,"summarize this CV chunk in form of bullet points separated by new line and do not add anny comments after the summary.\nUse a new line for each summary entry.\nStart by giving information about the candidate like his name and address and any other available information in the cv, then his academic record if applicable, followed by his professional record if applicable.\nKeep only relevant information about the candidate.\nDo not add information that is not in the cv.", "CV chunk", answer_start="- Name:")
        cv_summary = cv_summary.replace("```","")
        output += f"**CV summary**\n{cv_summary}\n\n"
        self.set_message_content(output)
        self.save_text(cv_summary, output_path/(cv_path.stem+"_summary.md"))
        self.step_end(f"summerizing cv {cv_path.stem}")


        self.step_start(f"building candidate description {cv_path.stem}")
        candidate_description = self.fast_gen(f"{self.config.start_header_id_template}instructions: Given the following position description and candidate cv, build an organized description of the candidate information taking into consideration the position description. Do not add comments after the description.\nPosition description:{subject_summary}\nCandidate cv:\n{cv_summary}{self.config.separator_template}{self.config.start_header_id_template}interview ai:Requested description in markdown format\n```markdown\n")
        candidate_description = candidate_description.replace("```","")
        self.save_text(candidate_description, output_path/("candidate_description.md"))
        self.step_end(f"building candidate description {cv_path.stem}")
        
        self.step_start(f"judging candidate {cv_path.stem}")
        candidate_judgement = self.fast_gen(f"{self.config.start_header_id_template}instructions: Given the following position description and candidate cv, write an objective judgement about the candidate fitness to the position.\nPosition description:{subject_summary}\nCandidate cv:\n{cv_summary}{self.config.separator_template}{self.config.start_header_id_template}interview ai: Ok, here are the requested interview questions in markdown format\n```markdown\n")
        candidate_judgement.replace("```","")
        grade = self.fast_gen(f"{self.config.start_header_id_template}instructions: Given the following candidate judgement, give a mark from 0 to 10.{self.config.separator_template}{self.config.start_header_id_template}judgement: {candidate_judgement}{self.config.separator_template}{self.config.start_header_id_template}grade: ")
        candidate_judgement += "\n\n## grade: "+grade+"\n"
        output += "\n## Candidate judgement:\n"+candidate_judgement        
        self.set_message_content(output)
        try:
            grade = float(grade)
        except:
            output += f"<p style='background-color:red'>{cv_path.stem} had no grade</p>"
            grade = 5
        self.save_text(candidate_judgement, output_path/("candidate_judgement.md"))
        self.step_end(f"judging candidate {cv_path.stem}")
        
        self.step_start(f"building candidate interview questions {cv_path.stem}")
        interview_questions = self.fast_gen(f"{self.config.start_header_id_template}instructions: Given the following position description and candidate cv, build a list of interview questions to test the candidate against the position subject. Try to challenge the candidate about what's mentionned in the CV. Group the questions by theme. Make sure you mension elements from the cv that can be connected to the subject and ask questions about them. Also test social skills and subject ambition. Do not add comments after the description.\nPosition description:{subject_summary}\nCandidate cv:\n{cv_summary}{self.config.separator_template}{self.config.start_header_id_template}interview ai: Ok, here are the requested interview questions in markdown format\n```markdown\n")
        interview_questions.replace("```","")
        self.save_text(interview_questions, output_path/("interview_questions.md"))
        self.step_end("building candidate interview questions")
        

        
        self.step_start(f"building full report {cv_path.stem}")
        full_candidate_file_markdown = "## Candidate description:\n\n"+candidate_description+"\n\n"+"## Interview questions:\n\n"+interview_questions+"\n\n"+"## Evaluation grid:\n\n"+evaluation_grid+"\n"
        self.save_text(full_candidate_file_markdown, output_path/("full_candidate_file_markdown.md"))
        self.step_end(f"building full report {cv_path.stem}")
        
        self.step_start(f"Converting to latex {cv_path.stem}")
        full_candidate_file_latex = self.fast_gen(f"{self.config.start_header_id_template}instructions: Convert the following markdown text to a full latex document using the article format. Format the markdown tables in order to make them fit the page width.\n```markdown\n{full_candidate_file_markdown}\n```{self.config.separator_template}{self.config.start_header_id_template}conversion:\n```latex\n")
        full_candidate_file_latex = full_candidate_file_latex.replace("```","")        
        self.save_text(full_candidate_file_latex, output_path/(cv_path.stem+"_interview.tex"))
        self.step_end("Converting to latex")
        interview_latex_path = output_path/(cv_path.stem+"_interview.tex")
        output += f"**Interview Latex file path**\n[{interview_latex_path}]({interview_latex_path})\n"
        self.set_message_content(output)


        if self.personality_config.language!="":
            self.step_start(f"Translating to:{self.personality_config.language}")
            full_candidate_file_latex_lang = self.fast_gen(f"{self.config.start_header_id_template}instructions: Translate this markdown text to {self.personality_config.language}.\n```markdown\n{full_candidate_file_markdown}\n``{self.config.separator_template}{self.config.start_header_id_template}translation:\n```markdown\n")
            full_candidate_file_latex_lang = full_candidate_file_latex_lang.replace("```","")
            self.save_text(full_candidate_file_latex_lang, output_path/(f"full_candidate_file_latex_{self.personality_config.language}.md"))
            self.step_end(f"Translating to:{self.personality_config.language}")
            self.step_start("Converting to latex")
            full_candidate_file_latex = self.fast_gen(f"{self.config.start_header_id_template}instructions: Convert the following markdown text to a full latex document using the article format. Format the markdown tables in order to make them fit the page width. Keep the same language and do not translate it to english.\n```markdown\n{full_candidate_file_latex_lang}\n```{self.config.separator_template}{self.config.start_header_id_template}conversion:\n```latex\n")
            full_candidate_file_latex = full_candidate_file_latex.replace("```","")
            self.save_text(full_candidate_file_latex, output_path/(cv_path.stem+f"_interview_{self.personality_config.language}.tex"))
            self.step_end("Converting to latex")
            interview_latex_path = output_path/(cv_path.stem+f"_interview_{self.personality_config.language}.tex")
            output += f"**Translated interview Latex file path**\n[Interview Latex file path]({interview_latex_path})\n"
            self.set_message_content(output)
            
        self.set_message_content(output)
        return output, grade


    def start_processing_cvs(self, prompt="", full_context=""):
        self.new_message("")
        self.process_cvs()


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
        if self.personality_config.candidate_cv!="" and self.personality_config.subject_text!="":
            self.step_start("Understanding request")
            if self.yes_no("Is the user asking for starting the process?", previous_discussion_text):
                self.step_end("Understanding request")
                self.process_cvs()
            else:
                self.step_end("Understanding request")
                self.fast_gen(previous_discussion_text, callback=self.callback)
        else:
            self.fast_gen(previous_discussion_text, callback=self.callback)
        return ""


