from lollms.types import MSG_OPERATION_TYPE
from lollms.helpers import ASCIIColors, trace_exception
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate, InstallOption
from lollms.personality import APScript, AIPersonality
from lollms.prompting import LollmsContextDetails
from pathlib import Path
import json
import re
from typing import Callable, Any
from safe_store import parse_document, SafeStore

def remove_indexing_from_markdown(markdown_text):
    # Define a regular expression pattern to match numbered and hyphenated lists at the beginning of the line
    pattern = r'^(?:\d+\.\s+|\d+-\s+)'
    
    # Use the sub() method to replace the matched pattern with an empty string
    clean_text = re.sub(pattern, '', markdown_text.strip())
    
    return clean_text


def find_last_file(folder_path):
    i = 0
    while True:
        file_name = f"database_{i}.json"
        file_path = Path(folder_path) / file_name
        if not file_path.exists():
            return str(f"database_{i-1}.json")
        i += 1


def find_available_file(folder_path):
    i = 0
    while True:
        file_name = f"database_{i}.json"
        file_path = Path(folder_path) / file_name
        if not file_path.exists():
            return str(file_path)
        i += 1

class Processor(APScript):
    """
    A class that processes model inputs and outputs.
    Inherits from APScript.
    """

    def __init__(
        self,
        personality: AIPersonality,
        callback=None,
    ) -> None:
        # Get the current directory
        root_dir = personality.lollms_paths.personal_path
        # We put this in the shared folder in order as this can be used by other personalities.
        shared_folder = root_dir / "shared"
        self.callback = None
        personality_config_template = ConfigTemplate(
            [
                {
                    "name": "data_folder_path",
                    "type": "str",
                    "value": "",
                    "help": "A path to a local folder containing the original data to be converted to a chat database",
                },
                {
                    "name": "questions_gen_size",
                    "type": "int",
                    "value": 512,
                    "help": "The maximum number of tokens that can be generated for each chunk of text in the questions building phase",
                },
                {
                    "name": "answer_gen_size",
                    "type": "int",
                    "value": 1024,
                    "help": "The maximum number of tokens that can be generated for each chunk of text in the questions building phase",
                },
                {
                    "name": "data_chunk_size",
                    "type": "int",
                    "value": 512,
                    "help": "The maximum number of tokens that for each vectorized data chunks",
                },
                {
                    "name": "data_overlap_size",
                    "type": "int",
                    "value": 128,
                    "help": "The overlap between data chunks in tokens",
                },
                {
                    "name": "data_vectorization_nb_chunks",
                    "type": "int",
                    "value": 2,
                    "help": "The number of chunks to recover from the database",
                },
                {
                    "name": "use_enhanced_mode",
                    "type": "bool",
                    "value": False,
                    "help": "This activates using the keyword building part of the execution diagram. Please read the paper for more details.",
                },
                
                
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
            [],
            callback=callback
        )
        
        self.data_store = SafeStore()

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
        # Preparing callback
        self.callback = callback
        
        # Preparing data
        output_folder = self.personality.lollms_paths.personal_outputs_path/self.personality.name
        output_folder.mkdir(parents=True, exist_ok=True)
        # Verify if the data_folder_path exists
        data_folder_path = Path(self.personality_config.data_folder_path)
        if not Path(data_folder_path).exists():
            self.warning("The specified data_folder_path does not exist.")
        document_files = [v for v in data_folder_path.iterdir()]
        self.step_start(f"Loading files")
        for file_path in document_files:
            document_text = parse_document(file_path)
            self.data_store.add_text(file_path, document_text)
        self.step_end(f"Loading files")
        
        #processing
        if "continue" in prompt.lower():
            try:
                db_name = find_last_file(output_folder)
                with open(output_folder/f"{db_name.split('.')[0]}_q.json", 'r') as file:
                    questions_vector = json.load(file)
            except:
                output = "FAILED to continue from last process: "
                self.set_message_content(output)
                return
            output = "### Loading questions:\n"
            output += "\n".join(questions_vector)
        else:
            db_name = find_available_file(output_folder)
            output = "### Building questions:\n"
            self.set_message_content(output)
            # Iterate over all documents in data_folder_path
            processed_chunks = 0
            # Iterate over all chunks and extract text
            questions_vector = []
            total_chunks = len(self.data_store.chunks.items())
            for chunk_name, chunk in self.data_store.chunks.items():
                chunk_text = chunk["chunk_text"]
                processed_chunks += 1
                self.step_start(f"Processing chunk {chunk_name}: {processed_chunks}/{total_chunks}")
                # Build the prompt text with placeholders
                prompt_text = f"{self.config.start_header_id_template}instruction: Generate questions or tasks that delve into the specific details and information presented in the text chunks. Please do not ask questions about the form of the text, and do not mention the text itself in your questions. Make sure you format the output using Markdown with each question or task placed in a separate paragraph starting with __P__.\n{self.config.separator_template}{self.config.start_header_id_template}chunk {{chunk_name}}: {{chunk}}{self.config.separator_template}{self.config.start_header_id_template}Here are some questions and tasks to further explore the contents of the given text chunks:\n__P__"
                # Ask AI to generate questions
                generated_text = "__P__"+self.fast_gen(prompt_text, max_generation_size=self.personality_config.questions_gen_size, placeholders={"chunk": chunk_text, "chunk_name":chunk_name}, debug=True)
                # Split the generated text into lines and accumulate into questions_vector
                generated_lines = generated_text.strip().split("__P__")
                generated_lines = [q.replace("__P__","") for q in generated_lines]
                generated_lines = [remove_indexing_from_markdown(q) for q in generated_lines]
                questions_vector.extend(generated_lines)
                self.step_end(f"Processing chunk {chunk_name}: {processed_chunks}/{total_chunks}")
                output += "\n<".join(generated_lines) + "\n"
                self.set_message_content(output)
            
            self.step_start(f"Saving questions for future use")
            with open(output_folder/f"{db_name.split('.')[0]}_q.json", 'w') as file:
                json.dump(questions_vector, file)
            self.step_end(f"Saving questions for future use")
        
        output += "### Building answers:\n"
        self.set_message_content(output)
        qna_list=[]
        # Perform further processing with questions_vector
        for index, question in enumerate(questions_vector):
            docs, sorted_similarities, document_ids = self.data_store.recover_text(question, top_k=self.personality_config.data_vectorization_nb_chunks) 
            if self.personality_config.use_enhanced_mode:
                self.step_start(f"Verifying RAG data_{index}")
                prompt_text = """{self.config.start_header_id_template}chunk: {{chunk}}
{self.config.start_header_id_template}instruction: Is the information provided in the above chunk sufficient to answer the following question?
Valid answers:
- Yes
- No
{self.config.start_header_id_template}question: {{question}}
{self.config.start_header_id_template}answer: """
                if "yes" not in prompt_text.lower():
                    self.step_end(f"Verifying RAG data_{index}", False)
                    continue
                self.step_end(f"Verifying RAG data_{index}")

            self.step_start(f"Asking question {index}/{len(questions_vector)}")
            prompt_text = """{self.config.start_header_id_template}chunk: {{chunk}}
{self.config.start_header_id_template}instructions{self.config.end_header_id_template}
Interpret the textual data contained within the chunk thoroughly to answer the corresponding instruction/task presented alongside it.
If the information stored in this chunk does not suffice to provide categorically accurate answers, please answer exactly __UNSUFFICIENT_INFORMATION__.
All statements must be generated solely based on the available input data, discarding any assumptions beyond what has been explicitly stated.
Do not mention the chunks, assume you are generating training data for an AI to learn from without data.
It is crucial to maintain strict adherence to the content delineated in each instance of interaction.
Be precise and helpful.
{self.config.start_header_id_template}question: {{question}}
{self.config.start_header_id_template}answer: """
            # {self.config.start_header_id_template}chunk: {{chunk}}{self.config.separator_template}{self.config.start_header_id_template}instruction: Please use the text chunks to answer the following question:\n{self.config.separator_template}{self.config.start_header_id_template}question: {{question}}\n{self.config.separator_template}{self.config.start_header_id_template}answer: "
            # Ask AI to generate an answer
            answer = self.fast_gen(prompt_text, max_generation_size=self.personality_config.answer_gen_size, placeholders={"chunk": "\nchunk: ".join(docs), "question": question})
            if "UNSUFFICIENT_INFORMATION" in answer:
                continue
            qna_list.append({
                "conditionning":"Act as LoLLMs expert and answer the following questions.",
                "question":question,
                "answer":answer,
                "id":0
            })
            output += f"q:{question}\na:{answer}\n"
            self.set_message_content(output)
            self.step_end(f"Asking question {index}/{len(questions_vector)}")
            with open(output_folder/db_name, 'w') as file:
                json.dump(qna_list, file)
        print("Dictionary saved as JSON successfully!")
        return ""



