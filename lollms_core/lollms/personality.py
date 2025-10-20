######
# Project       : lollms
# File          : personality.py
# Author        : ParisNeo with the help of the community
# license       : Apache 2.0
# Description   :
# This is an interface class for lollms personalities.
######
from datetime import datetime
from pathlib import Path
from lollms.config import InstallOption, TypedConfig, BaseConfig
from lollms.main_config import LOLLMSConfig
from lollms.paths import LollmsPaths
from lollms.binding import LLMBinding, BindingType
from lollms.utilities import PromptReshaper, discussion_path_to_url, process_ai_output, remove_text_from_string
from lollms.com import NotificationType, NotificationDisplayType
from lollms.client_session import Session, Client
from safe_store import SafeStore, SAFE_STORE_SUPPORTED_FILE_EXTENSIONS
import pkg_resources
from pathlib import Path
from PIL import Image
import re
import shutil
import os
from datetime import datetime
import importlib
import subprocess
import yaml
from ascii_colors import ASCIIColors, trace_exception
import time
from lollms.types import MSG_OPERATION_TYPE, SUMMARY_MODE
import json
from typing import Any, List, Optional, Type, Callable, Dict, Any, Union, Tuple

from functools import partial
import sys
from lollms.com import LoLLMsCom
from lollms.prompting import LollmsContextDetails
import inspect

from lollms.code_parser import compress_js, compress_python, compress_html

import requests
from bs4 import BeautifulSoup
import pipmaster as pm
pm.ensure_packages({"PyQt5":""})
    
import sys
from PyQt5.QtWidgets import QApplication, QLineEdit, QButtonGroup, QRadioButton, QVBoxLayout, QWidget, QMessageBox

def get_element_id(url, text):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    element = soup.find('span', text=text)
    if element:
        return element['id']
    else:
        return None

def craft_a_tag_to_specific_text(url, text, caption):
    # Encode the text to be used in the URL
    encoded_text = text.replace(' ', '%20')

    # Construct the URL with the anchor tag
    anchor_url = f"{url}#{encoded_text}"

    # Return the anchor tag
    return anchor_url

def is_package_installed(package_name):
    try:
        dist = pkg_resources.get_distribution(package_name)
        return True
    except pkg_resources.DistributionNotFound:
        return False


def install_package(package_name):
    try:
        # Check if the package is already installed
        __import__(package_name)
        print(f"{package_name} is already installed.")
    except ImportError:
        print(f"{package_name} is not installed. Installing...")

        # Install the package using pip
        subprocess.check_call(["pip", "install", package_name])

        print(f"{package_name} has been successfully installed.")


def fix_json(json_text):
    try:
        json_text = json_text.replace("}\n{","},\n{")
        # Try to load the JSON string
        json_obj = json.loads(json_text)
        return json_obj
    except json.JSONDecodeError as e:
        trace_exception(e)
class AIPersonality:

    # Extra
    def __init__(
                    self,
                    personality_package_path: str|Path,
                    lollms_paths:LollmsPaths,
                    config:LOLLMSConfig,
                    model:LLMBinding=None,
                    app:LoLLMsCom=None,
                    run_scripts=True,
                    selected_language=None,
                    ignore_discussion_documents_rag=False,
                    is_relative_path=True,
                    installation_option:InstallOption=InstallOption.INSTALL_IF_NECESSARY,
                    callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None
                ):
        """
        Initialize an AIPersonality instance.

        Parameters:
        personality_package_path (str or Path): The path to the folder containing the personality package.

        Raises:
        ValueError: If the provided path is not a folder or does not contain a config.yaml file.
        """
        self.sink_id = 0
        self.config = config

        self.bot_says = ""

        self.lollms_paths = lollms_paths
        self.model = model
        self.callback = callback
        self.app = app

        self.text_files = []
        self.image_files = []
        self.audio_files = []
        self.images_descriptions = []
        self.vectorizer = None

        self.installation_option = installation_option

        # Whisper to transcribe audio
        self.whisper = None

        # First setup a default personality
        # Version
        self._version = pkg_resources.get_distribution('lollms').version

        self.run_scripts = run_scripts

        #General information
        self._author: str = "ParisNeo"
        self._name: str = "lollms"
        self._creation_date = "unknown"
        self._last_update_date = "unknown"

        self._user_name: str = "user"
        self._category: str = "General"
        self._category_desc: str = "General"
        self._language: str = "english"
        self._default_language: str = "english"
        
        self._supported_languages: str = []
        self._selected_language: str = selected_language
        self._ignore_discussion_documents_rag:bool = ignore_discussion_documents_rag

        self._languages: List[dict]=[]




        # Conditionning
        self._personality_description: str = "This personality is a helpful and Kind AI ready to help you solve your problems"
        self._personality_conditioning: str = "\n".join([
            "lollms (Lord of LLMs) is a smart and helpful Assistant built by the computer geek ParisNeo.",
            "It is compatible with many bindings to LLM models such as llama, gpt4all, gptj, autogptq etc.",
            "It can discuss with humans and assist them on many subjects.",
            "It runs locally on your machine. No need to connect to the internet.",
            "It answers the questions with precise details",
            "Its performance depends on the underlying model size and training.",
            "Try to answer with as much details as you can",
            "Date: {{date}}",
        ])
        self._prompts_list: List[str] = []
        self._welcome_message: str = "Welcome! I am lollms (Lord of LLMs) A free and open assistant built by ParisNeo. What can I do for you today?"
        self._include_welcome_message_in_discussion: bool = True
        self._user_message_prefix: str = f"user"
        self._link_text: str = "\n"
        self._ai_message_prefix: str = f"assistant"

        # Extra
        self._dependencies: List[str] = []

        # Disclaimer
        self._disclaimer: str = ""
        self._help: str = ""
        self._commands: list = []

        # Default model parameters
        self._model_temperature: float = 0.7 # higher: more creative, lower more deterministic
        self._model_top_k: int = 50
        self._model_top_p: float = 0.95
        self._model_repeat_penalty: float = 1.3
        self._model_repeat_last_n: int = 40

        self._processor_cfg: dict = {}

        self._logo: Optional[Image.Image] = None
        self._processor = None
        self._data = None



        if personality_package_path is None:
            self.config = {}
            self.assets_list = []
            self.personality_package_path = None
            return
        else:
            parts = str(personality_package_path).split("/")
            self._category = parts[0]
            if parts[0] == "custom_personalities":
                self.personality_package_path = self.lollms_paths.custom_personalities_path/parts[1]
            else:
                if is_relative_path:
                    self.personality_package_path = self.lollms_paths.personalities_zoo_path/personality_package_path
                else:
                    self.personality_package_path = Path(personality_package_path)

            # Validate that the path exists
            if not self.personality_package_path.exists():
                raise ValueError(f"Could not find the personality package:{self.personality_package_path}")

            # Validate that the path format is OK with at least a config.yaml file present in the folder
            if not self.personality_package_path.is_dir():
                raise ValueError(f"Personality package path is not a folder:{self.personality_package_path}")

            self.personality_folder_name = self.personality_package_path.stem


            self.personality_output_folder = lollms_paths.personal_outputs_path/self.name
            self.personality_output_folder.mkdir(parents=True, exist_ok=True)
            # Open and store the personality
            self.load_personality()

    def compute_n_predict(self, tokens):
        return min(self.config.ctx_size-len(tokens)-1,self.config.max_n_predict if self.config.max_n_predict else self.config.ctx_size-len(tokens)-1)      

    def build_context(self, context_details:LollmsContextDetails, is_continue:bool=False, return_tokens:bool=False):
        # Build the final prompt by concatenating the conditionning and discussion messages
        if self.config.use_assistant_name_in_discussion:
            if self.config.use_model_name_in_discussions:
                ai_header = self.ai_custom_header(self.name+f"({self.config.model_name})") 
            else:
                ai_header = self.ai_full_header
        else:
            if self.config.use_model_name_in_discussions:
                ai_header = self.ai_custom_header("assistant"+f"({self.config.model_name})")
            else:
                ai_header = self.ai_custom_header("assistant")

        # Filter out empty elements and join with separator
        prompt_data = context_details.build_prompt(self.app.template, [ai_header] if not is_continue else [] if not self.config.use_continue_message \
            else ["CONTINUE FROM HERE And do not open a new markdown code tag." + self.separator_template + ai_header])
        
        tokens = self.model.tokenize(prompt_data)
        if return_tokens:
            return prompt_data, tokens
        else:
            return prompt_data


    def InfoMessage(self, content, duration:int=4, client_id=None, verbose:bool=True):
        if self.app:
            return self.app.InfoMessage(content=content, client_id=client_id, verbose=verbose)
        ASCIIColors.white(content)

    def ShowBlockingMessage(self, content, client_id=None, verbose:bool=True):
        if self.app:
            return self.app.ShowBlockingMessage(content=content, client_id=client_id, verbose=verbose)
        ASCIIColors.white(content)

    def HideBlockingMessage(self, client_id=None, verbose:bool=True):
        if self.app:
            return self.app.HideBlockingMessage(client_id=client_id, verbose=verbose)


    def info(self, content, duration:int=4, client_id=None, verbose:bool=True):
        if self.app:
            return self.app.info(content=content, duration=duration, client_id=client_id, verbose=verbose)
        ASCIIColors.info(content)

    def warning(self, content, duration:int=4, client_id=None, verbose:bool=True):
        if self.app:
            return self.app.warning(content=content, duration=duration, client_id=client_id, verbose=verbose)
        ASCIIColors.warning(content)

    def success(self, content, duration:int=4, client_id=None, verbose:bool=True):
        if self.app:
            return self.app.success(content=content, duration=duration, client_id=client_id, verbose=verbose)
        ASCIIColors.success(content)

    def error(self, content, duration:int=4, client_id=None, verbose:bool=True):
        if self.app:
            return self.app.error(content=content, duration=duration, client_id=client_id, verbose=verbose)
        ASCIIColors.error(content)

    def notify( self,
                content,
                notification_type:NotificationType=NotificationType.NOTIF_SUCCESS,
                duration:int=4,
                client_id=None,
                display_type:NotificationDisplayType=NotificationDisplayType.TOAST,
                verbose=True
            ):
        if self.app:
            return self.app.error(content=content, notification_type=notification_type, duration=duration, client_id=client_id, display_type=display_type, verbose=verbose)
        ASCIIColors.white(content)


    def new_message(self, message_text:str, message_type:MSG_OPERATION_TYPE= MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT, metadata=[], callback: Callable[[str, int, dict, list, Any], bool]=None):
        """This sends step rogress to front end

        Args:
            step_text (dict): The step progress in %
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the progress to. Defaults to None.
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(message_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_NEW_MESSAGE, personality=self)

    def set_message_content(self, full_text:str, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None):
        """This sends full text to front end

        Args:
            step_text (dict): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the text to. Defaults to None.
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(full_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT)
    def add_chunk_to_message_content(self, full_text:str, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None):
        """This sends full text to front end

        Args:
            step_text (dict): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the text to. Defaults to None.
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(full_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK)

    def set_message_html(self, ui_text:str, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None, client_id= None):
        """This sends ui text to front end

        Args:
            ui_text (dict): The ui code to be sent to the front end
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the text to. Defaults to None.
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(ui_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI)


    def set_message_content_invisible_to_ai(self, full_text:str, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None):
        """This sends full text to front end (INVISIBLE to AI)

        Args:
            step_text (dict): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the text to. Defaults to None.
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(full_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI)

    def set_message_content_invisible_to_user(self, full_text:str, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None):
        """This sends full text to front end (INVISIBLE to user)

        Args:
            step_text (dict): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the text to. Defaults to None.
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(full_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_USER)


    def build_prompt(self, prompt_parts:List[str], sacrifice_id:int=-1, context_size:int=None, minimum_spare_context_size:int=None):
        """
        Builds the prompt for code generation.

        Args:
            prompt_parts (List[str]): A list of strings representing the parts of the prompt.
            sacrifice_id (int, optional): The ID of the part to sacrifice.
            context_size (int, optional): The size of the context.
            minimum_spare_context_size (int, optional): The minimum spare context size.

        Returns:
            str: The built prompt.
        """
        if context_size is None:
            context_size = self.config.ctx_size
        if minimum_spare_context_size is None:
            minimum_spare_context_size = self.config.min_n_predict

        if sacrifice_id == -1 or len(prompt_parts[sacrifice_id])<50:
            return "\n".join([s for s in prompt_parts if s!=""])
        else:
            part_tokens=[]
            nb_tokens=0
            for i,part in enumerate(prompt_parts):
                tk = self.model.tokenize(part)
                part_tokens.append(tk)
                if i != sacrifice_id:
                    nb_tokens += len(tk)
            if len(part_tokens[sacrifice_id])>0:
                sacrifice_tk = part_tokens[sacrifice_id]
                sacrifice_tk= sacrifice_tk[-(context_size-nb_tokens-minimum_spare_context_size):]
                sacrifice_text = self.model.detokenize(sacrifice_tk)
            else:
                sacrifice_text = ""
            prompt_parts[sacrifice_id] = sacrifice_text
            return "\n".join([s for s in prompt_parts if s!=""])


    def internet_search_with_vectorization(self, query, quick_search:bool=False, asses_using_llm=True):
        """
        Do internet search and return the result
        """
        from lollms.internet import internet_search_with_vectorization
        return internet_search_with_vectorization(
                                                    query,
                                                    internet_nb_search_pages=int(self.config.internet_nb_search_pages),
                                                    internet_vectorization_chunk_size=int(self.config.internet_vectorization_chunk_size),
                                                    internet_vectorization_overlap_size=int(self.config.internet_vectorization_overlap_size),
                                                    internet_vectorization_nb_chunks=int(self.config.internet_vectorization_nb_chunks),
                                                    model = self.model,
                                                    quick_search=quick_search,
                                                    asses_using_llm=asses_using_llm,
                                                    yes_no = self.yes_no
                                                    )

    def sink(self, s=None,i=None,d=None):
        if self.config.debug:
            print(s,end="")
        else:
            animation = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
            ASCIIColors.yellow(animation[self.sink_id]+"\r")
            if self.sink_id<9:
                self.sink_id += 1
            else:
                self.sink_id = 0

    def yes_no(
            self,
            question: str,
            context: str = "",
            max_answer_length: int = None,
            conditionning: str = "",
            return_explanation: bool = False,
            callback = None
        ) -> bool | dict:
        """
        Answers a yes/no question.

        Args:
            question (str): The yes/no question to answer.
            context (str, optional): Additional context to provide for the question.
            max_answer_length (int, optional): Maximum string length allowed for the response. Defaults to None.
            conditionning (str, optional): An optional system message to put at the beginning of the prompt.
            return_explanation (bool, optional): If True, returns a dictionary with the answer and explanation. Defaults to False.

        Returns:
            bool or dict: 
                - If return_explanation is False, returns a boolean (True for 'yes', False for 'no').
                - If return_explanation is True, returns a dictionary with the answer and explanation.
        """
        if not callback:
            callback=self.sink

        prompt = f"{conditionning}\nQuestion: {question}\nContext: {context}\n"
        
        template = """
        {
            "answer": true | false,
            "explanation": "Optional explanation if return_explanation is True"
        }
        """
        
        response = self.generate_code(
            prompt=prompt,
            template=template,
            language="json",
            code_tag_format="markdown",
            max_size=max_answer_length,
            include_code_directives=True,
            accept_all_if_no_code_tags_is_present=True,
            callback=callback
        )
        
        try:
            parsed_response = json.loads(response)
            answer = parsed_response.get("answer", False)
            explanation = parsed_response.get("explanation", "")
            
            if return_explanation:
                return {"answer": answer, "explanation": explanation}
            else:
                return answer
        except json.JSONDecodeError:
            return False

    def multichoice_question(
            self, 
            question: str, 
            possible_answers: list, 
            context: str = "", 
            max_answer_length: int = None, 
            conditionning: str = "", 
            return_explanation: bool = False,
            callback = None
        ) -> dict:
        """
        Interprets a multi-choice question from a user's response. This function expects only one choice as true. 
        All other choices are considered false. If none are correct, returns -1.

        Args:
            question (str): The multi-choice question posed by the user.
            possible_answers (List[Any]): A list containing all valid options for the chosen value.
            context (str, optional): Additional context to provide for the question.
            max_answer_length (int, optional): Maximum string length allowed while interpreting the user's responses. Defaults to None.
            conditionning (str, optional): An optional system message to put at the beginning of the prompt.
            return_explanation (bool, optional): If True, returns a dictionary with the choice and explanation. Defaults to False.

        Returns:
            dict: 
                - If return_explanation is False, returns a JSON object with only the selected choice index.
                - If return_explanation is True, returns a JSON object with the selected choice index and an explanation.
                - Returns {"index": -1} if no match is found among the possible answers.
        """
        if not callback:
            callback=self.sink
        
        prompt = f"""
        {conditionning}\n
        QUESTION:\n{question}\n
        POSSIBLE ANSWERS:\n"""
        for i, answer in enumerate(possible_answers):
            prompt += f"{i}. {answer}\n"
        
        if context:
            prompt += f"\nADDITIONAL CONTEXT:\n{context}\n"
        
        prompt += "\nRespond with a JSON object containing:\n"
        if return_explanation:
            prompt += "{\"index\": (the selected answer index), \"explanation\": (reasoning for selection)}"
        else:
            prompt += "{\"index\": (the selected answer index)}"
        
        response = self.generate_code(prompt, language="json", max_size=max_answer_length, 
            accept_all_if_no_code_tags_is_present=True, return_full_generated_code=False, callback=callback)
        
        try:
            result = json.loads(response)
            if return_explanation:
                if "index" in result and isinstance(result["index"], int):
                    return result["index"], result["index"]
            else:
                if "index" in result and isinstance(result["index"], int):
                    return result["index"]
        except json.JSONDecodeError:
            if return_explanation:
                return -1, "failed to decide"
            else:
                return -1
            
    def multichoice_ranking(
            self, 
            question: str, 
            possible_answers: list, 
            context: str = "", 
            max_answer_length: int = 512, 
            conditionning: str = "", 
            return_explanation: bool = False,
            callback = None
        ) -> dict:
        """
        Ranks answers for a question from best to worst. Returns a JSON object containing the ranked order.

        Args:
            question (str): The question for which the answers are being ranked.
            possible_answers (List[Any]): A list of possible answers to rank.
            context (str, optional): Additional context to provide for the question.
            max_answer_length (int, optional): Maximum string length allowed for the response. Defaults to 50.
            conditionning (str, optional): An optional system message to put at the beginning of the prompt.
            return_explanation (bool, optional): If True, returns a dictionary with the ranked order and explanations. Defaults to False.

        Returns:
            dict: 
                - If return_explanation is False, returns a JSON object with only the ranked order.
                - If return_explanation is True, returns a JSON object with the ranked order and explanations.
        """
        if not callback:
            callback=self.sink
        
        prompt = f"""
        {conditionning}\n
        QUESTION:\n{question}\n
        POSSIBLE ANSWERS:\n"""
        for i, answer in enumerate(possible_answers):
            prompt += f"{i}. {answer}\n"
        
        if context:
            prompt += f"\nADDITIONAL CONTEXT:\n{context}\n"
        
        prompt += "\nRespond with a JSON object containing:\n"
        if return_explanation:
            prompt += "{\"ranking\": (list of indices ordered from best to worst), \"explanations\": (list of reasons for each ranking)}"
        else:
            prompt += "{\"ranking\": (list of indices ordered from best to worst)}"
        
        response = self.generate_code(prompt, language="json", return_full_generated_code=False, callback=callback)
        
        try:
            result = json.loads(response)
            if "ranking" in result and isinstance(result["ranking"], list):
                return result
        except json.JSONDecodeError:
            return {"ranking": []}


    def step_start(self, step_text, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None):
        """This triggers a step start

        Args:
            step_text (str): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the step start to. Defaults to None.
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(step_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_START)

    def step_end(self, step_text, success=True, callback: Callable[[str, int, dict, list], bool]=None):
        """This triggers a step end

        Args:
            step_text (str): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the step end to. Defaults to None.
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            if success:
                callback(step_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS)
            else:
                callback(step_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_FAILURE)
                
    def step(self, step_text, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None):
        """This triggers a step information

        Args:
            step_text (str): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE, dict, list) to send the step to. Defaults to None.
            The callback has these fields:
            - chunk
            - Message Type : the type of message
            - Parameters (optional) : a dictionary of parameters
            - Metadata (optional) : a list of metadata
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(step_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP)

    def print_prompt(self, title, prompt):
        ASCIIColors.red("*-*-*-*-*-*-*-* ", end="")
        ASCIIColors.red(title, end="")
        ASCIIColors.red(" *-*-*-*-*-*-*-*")
        ASCIIColors.yellow(prompt)
        ASCIIColors.red(" *-*-*-*-*-*-*-*")
        ASCIIColors.red(f"Weight : {self.model.count_tokens(prompt)} tokens")
        ASCIIColors.red(" *-*-*-*-*-*-*-*")


    def fast_gen_with_images(self, prompt: str, images:list, max_generation_size: int=None, placeholders: dict = {}, sacrifice: list = ["previous_discussion"], debug: bool  = False, callback=None, show_progress=False) -> str:
        """
        Fast way to generate text from text and images

        This method takes in a prompt, maximum generation size, optional placeholders, sacrifice list, and debug flag.
        It reshapes the context before performing text generation by adjusting and cropping the number of tokens.

        Parameters:
        - prompt (str): The input prompt for text generation.
        - max_generation_size (int): The maximum number of tokens to generate.
        - placeholders (dict, optional): A dictionary of placeholders to be replaced in the prompt. Defaults to an empty dictionary.
        - sacrifice (list, optional): A list of placeholders to sacrifice if the window is bigger than the context size minus the number of tokens to generate. Defaults to ["previous_discussion"].
        - debug (bool, optional): Flag to enable/disable debug mode. Defaults to False.

        Returns:
        - str: The generated text after removing special tokens ("<s>" and "</s>") and stripping any leading/trailing whitespace.
        """
        start_header_id_template    = self.config.start_header_id_template
        end_header_id_template      = self.config.end_header_id_template
        system_message_template     = self.config.system_message_template

        prompt = "\n".join([
            self.system_full_header+f"I am an AI assistant that can converse and analyze images. When asked to locate something in an image you send, I will reply with:",
            "boundingbox(image_index, label, left, top, width, height)",
            "Where:",
            "image_index: 0-based index of the image",
            "label: brief description of what is located",
            "left, top: x,y coordinates of top-left box corner (0-1 scale)",
            "width, height: box dimensions as fraction of image size",
            "Coordinates have origin (0,0) at top-left, (1,1) at bottom-right.",
            "For other queries, I will respond conversationally to the best of my abilities.",
            prompt
        ])
        if debug == False:
            debug = self.config.debug

        pr = PromptReshaper(prompt)

        prompt = pr.build(placeholders,
                        self.model.tokenize,
                        self.model.detokenize,
                        self.model.config.ctx_size - max_generation_size if max_generation_size else self.model.config.ctx_size - self.model.config.min_n_predict,
                        sacrifice
                        )
        ntk = self.model.count_tokens(prompt)
        if max_generation_size:
            max_generation_size = min(self.model.config.ctx_size - ntk, max_generation_size)
        else:
            max_generation_size = min(self.model.config.ctx_size - ntk,self.model.config.max_n_predict)
        # TODO : add show progress

        gen = self.generate_with_images(prompt, images, max_generation_size, callback=callback, show_progress=show_progress).strip().replace("</s>", "").replace("<s>", "")
        try:
            gen = process_ai_output(gen, images, "/discussions/")
        except Exception as ex:
            pass
        if debug:
            self.print_prompt("prompt", prompt+gen)

        return gen

    def fast_gen(
                    self, 
                    prompt: str, 
                    max_generation_size: int=None, 
                    placeholders: dict = {}, 
                    sacrifice: list = ["previous_discussion"], 
                    debug: bool  = False, 
                    callback=None, 
                    show_progress=False, 
                    temperature = None, 
                    top_k = None, 
                    top_p=None, 
                    repeat_penalty=None, 
                    repeat_last_n=None
                ) -> str:
        """
        Fast way to generate code

        This method takes in a prompt, maximum generation size, optional placeholders, sacrifice list, and debug flag.
        It reshapes the context before performing text generation by adjusting and cropping the number of tokens.

        Parameters:
        - prompt (str): The input prompt for text generation.
        - max_generation_size (int): The maximum number of tokens to generate.
        - placeholders (dict, optional): A dictionary of placeholders to be replaced in the prompt. Defaults to an empty dictionary.
        - sacrifice (list, optional): A list of placeholders to sacrifice if the window is bigger than the context size minus the number of tokens to generate. Defaults to ["previous_discussion"].
        - debug (bool, optional): Flag to enable/disable debug mode. Defaults to False.

        Returns:
        - str: The generated text after removing special tokens ("<s>" and "</s>") and stripping any leading/trailing whitespace.
        """
        if debug == False:
            debug = self.config.debug

        pr = PromptReshaper(prompt)
        prompt = pr.build(placeholders,
                        self.model.tokenize,
                        self.model.detokenize,
                        (self.model.config.ctx_size - max_generation_size) if max_generation_size is not None else (self.model.config.ctx_size - 1024),
                        sacrifice
                        )
        # TODO : add show progress

        gen = self.generate(prompt, max_generation_size, temperature = temperature, top_k = top_k, top_p=top_p, repeat_penalty=repeat_penalty, repeat_last_n=repeat_last_n, callback=callback, show_progress=show_progress).strip().replace("</s>", "").replace("<s>", "")

        return gen
    

    def generate_text_with_tag(self, prompt, tag_name="SPECIAL_TAG"):
        """
        Generates text using self.fast_gen and wraps it inside a custom tag.
        
        :param prompt: The input prompt for text generation.
        :param tag_name: The name of the tag to wrap the generated text (default is "SPECIAL_TAG").
        :return: The generated text wrapped inside the specified tag.
        """
        # Generate the text using self.fast_gen
        generated_text = self.fast_gen(self.system_full_header+f"you are a helpful assistant that responds to user requests inside a <{tag_name}></{tag_name}> tag.\nExample:\n{self.user_custom_header('user')}What is the result to one plus one?\n{self.user_custom_header('assistant')}Here is the answer to your question:\n<{tag_name}>\nOne plus one equals to two.\n</{tag_name}>\n"+"\n"+self.separator_template+self.user_custom_header("user")+prompt+"\n"+self.separator_template+self.ai_custom_header("assistant"))
        return generated_text

    def extract_text_from_tag(self, tagged_text, tag_name="SPECIAL_TAG"):
        """
        Extracts the text from a custom tag.
        
        :param tagged_text: The text containing the tagged content.
        :param tag_name: The name of the tag to extract text from (default is "SPECIAL_TAG").
        :return: The extracted text from the specified tag.
        """
        # Define the start and end tags based on the provided tag_name
        start_tag = f"<{tag_name}>"
        end_tag = f"</{tag_name}>"
        
        # Find the indices of the start and end tags
        start_index = tagged_text.find(start_tag)
        end_index = tagged_text.find(end_tag)
        
        # If the tags are found, extract the text between them
        if start_index != -1 and end_index != -1:
            start_index += len(start_tag)  # Move index to the start of the actual text
            extracted_text = tagged_text[start_index:end_index]
        else:
            extracted_text = ""  # Return empty string if tags are not found
        
        return extracted_text


    def generate_codes(
                        self, 
                        prompt, 
                        images=[],
                        template=None,
                        language="json",
                        code_tag_format="markdown", # or "html"
                        max_size = None,  
                        temperature = None, 
                        top_k = None, 
                        top_p=None, 
                        repeat_penalty=None, 
                        repeat_last_n=None, 
                        callback=None, 
                        debug=False, 
                        return_full_generated_code=False, 
                    ):
        response_full = ""
        full_prompt = f"""{self.system_full_header}Act as a code generation assistant that generates code from user prompt.    
{self.user_full_header} 
{prompt}
"""
        if template:
            full_prompt += "Here is a template of the answer:\n"
            if code_tag_format=="markdown":
                full_prompt += f"""You must answer with the code placed inside the markdown code tag like this:
```{language}
{template}
```
{"Make sure you fill all fields and to use the exact same keys as the template." if language in ["json","yaml","xml"] else ""}
The code tag is mandatory.
Don't forget encapsulate the code inside a markdown code tag. This is mandatory.
"""
            elif code_tag_format=="html":
                full_prompt +=f"""You must answer with the code placed inside the html code tag like this:
<code language="{language}">
{template}
</code>
{"Make sure you fill all fields and to use the exact same keys as the template." if language in ["json","yaml","xml"] else ""}
The code tag is mandatory.
Don't forget encapsulate the code inside a html code tag. This is mandatory.
"""
        full_prompt += f"""Do not split the code in multiple tags.
{self.ai_full_header}"""

        if len(self.image_files)>0:
            response = self.generate_with_images(full_prompt, self.image_files, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug)
        elif  len(images)>0:
            response = self.generate_with_images(full_prompt, images, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug)
        else:
            response = self.generate(full_prompt, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug)
        response_full += response
        codes = self.extract_code_blocks(response)
        if return_full_generated_code:
            return codes, response_full
        else:
            return codes
        
    def generate_custom_code(   self,
                                full_prompt,
                                images=[],
                                max_size = None,  
                                temperature = None, 
                                top_k = None, 
                                top_p=None, 
                                repeat_penalty=None, 
                                repeat_last_n=None, 
                                callback=None, 
                                debug=None, 
                                return_full_generated_code=False, 
                                accept_all_if_no_code_tags_is_present=False, 
                                max_continues=5                             
                             ):
        self.print_prompt("custom code generation", full_prompt)
        response_full=""
        if len(self.image_files)>0:
            response = self.generate_with_images(full_prompt, self.image_files, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug,callback=self.sink)
        elif  len(images)>0:
            response = self.generate_with_images(full_prompt, images, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug,callback=self.sink)
        else:
            response = self.generate(full_prompt, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug,callback=self.sink)
        response_full += response
        if debug:
            ASCIIColors.green("Response")
            ASCIIColors.green(response_full)
        codes = self.extract_code_blocks(response)
        if len(codes)==0 and accept_all_if_no_code_tags_is_present:
            if return_full_generated_code:
                return response, response_full
            else:
                return response
        if len(codes)>0:
            if not codes[-1]["is_complete"]:
                code = "\n".join(codes[-1]["content"].split("\n")[:-1])
                nb_continues = 0
                while not codes[-1]["is_complete"] and nb_continues<max_continues:
                    response = self.generate(full_prompt+code+self.user_full_header+"continue the code. Start from last line and continue the code. Put the code inside a markdown code tag."+self.separator_template+self.ai_full_header, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug)
                    response_full += response
                    codes = self.extract_code_blocks(response)
                    if len(codes)==0:
                        break
                    else:
                        if not codes[-1]["is_complete"]:
                            code +="\n"+ "\n".join(codes[-1]["content"].split("\n")[:-1])
                        else:
                            code +="\n"+ "\n".join(codes[-1]["content"].split("\n"))
                    nb_continues += 1
            else:
                code = codes[-1]["content"]
            
            if return_full_generated_code:
                return code, response_full
            else:
                return code
        else:
            if return_full_generated_code:
                return None, None
            else:
                return None
        
    def generate_code(
        self, 
        prompt, 
        images=[],
        template=None,
        language="json",
        code_tag_format="markdown",  # or "html"
        max_size=None,  
        temperature=None, 
        top_k=None, 
        top_p=None, 
        repeat_penalty=None, 
        repeat_last_n=None, 
        callback=None, 
        debug=None, 
        return_full_generated_code=False, 
        accept_all_if_no_code_tags_is_present=False, 
        max_continues=3,
        include_code_directives=True  # Make code directives optional
    ):
        if debug is None:
            debug = self.config.debug
            
        response_full = ""
        
        # Determine if structured format
        structured = language.lower() in {'json', 'yaml', 'xml'}
        lang = language.lower()

        # Build core directives (optional)
        code_directives = []
        if include_code_directives:
            code_directives.extend([
                "STRICT REQUIREMENTS:",
                "1. Respond ONLY with a SINGLE code block containing the complete implementation",
                "2. ABSOLUTELY NO explanatory text, comments, or text outside code blocks",
                "3. Code MUST be syntactically correct and properly formatted",
            ])

            # Add structured format rules if applicable
            if structured:
                code_directives.extend([
                    f"4. For {language.upper()} format:",
                    "   a. Maintain EXACT key names and hierarchy from template",
                    "   b. Preserve all required fields even if empty",
                ])
                next_num = 5
            else:
                next_num = 4

            # Add remaining core directives
            code_directives.extend([
                f"{next_num}. If unsure about values, use appropriate placeholders",
                f"{next_num+1}. NEVER split code across multiple blocks",
                f"{next_num+2}. ALWAYS close code blocks properly"
            ])

            # Add language-specific best practices
            if lang == 'python':
                code_directives.extend([
                    "\nPYTHON-SPECIFIC RULES:",
                    "- Follow PEP8 style guidelines",
                    "- Use type hints for function signatures",
                    "- Include docstrings for public functions/classes/modules",
                    "- Prefer f-strings over format() or % formatting",
                    "- Handle exceptions properly with try/except blocks",
                    "- Avoid global variables where possible",
                    "- Use list comprehensions where appropriate"
                ])
            elif lang == 'c':
                code_directives.extend([
                    "\nC-SPECIFIC RULES:",
                    "- Use standard C library functions where possible",
                    "- Check for NULL pointers after allocation",
                    "- Free dynamically allocated memory appropriately",
                    "- Use const qualifiers for constants",
                    "- Include necessary header guards (#ifndef/#define)",
                    "- Document function purposes using comments",
                    "- Validate all input parameters"
                ])
            elif lang == 'cpp':
                code_directives.extend([
                    "\nC++-SPECIFIC RULES:",
                    "- Follow RAII (Resource Acquisition Is Initialization) principles",
                    "- Use smart pointers (unique_ptr, shared_ptr) instead of raw pointers",
                    "- Prefer standard library containers (vector, map) over raw arrays",
                    "- Use const references for large object parameters",
                    "- Mark functions as noexcept where appropriate",
                    "- Use namespaces appropriately",
                    "- Follow the rule of five/zero for class design"
                ])

        # Construct the full prompt
        full_prompt_parts = [self.system_full_header]
        if include_code_directives:
            full_prompt_parts.extend([
                "You are a PRECISION code generation system.",
                "Your responses MUST follow these rules:",
                "\n".join(code_directives),
                ""
            ])
        
        full_prompt_parts.extend([
            prompt,
            ""
        ])

        if template:
            full_prompt_parts.extend([
                "TEMPLATE STRUCTURE (FOLLOW EXACTLY):",
                f"```{language}\n{template}\n```" if code_tag_format == "markdown" else f"<code language='{language}'>\n{template}\n</code>",
                ""
            ])

            if structured:
                full_prompt_parts.append(f"IMPERATIVE: Match {language.upper()} structure PRECISELY. Use EXACT keys/attributes from template.")
            else:
                full_prompt_parts.append("IMPERATIVE: Follow code structure patterns from template.")

        # Add code wrapper based on the specified format
        if code_tag_format == "markdown":
            code_wrapper = f"Respond STRICTLY in this format:\n```{language}\n{{write the code here}}\n```\n"
        elif code_tag_format == "html":
            code_wrapper = f"Respond STRICTLY in this format:\n<code language='{language}'>\n{{write the code here}}\n</code>\n"
        
        full_prompt_parts.extend([
            code_wrapper,
            self.ai_custom_header("assistant")
        ])

        full_prompt = "\n".join(full_prompt_parts)
        full_prompt = full_prompt.strip()
        if debug:
            ASCIIColors.yellow("Prompt")
            ASCIIColors.yellow(full_prompt)

        # Generate initial response
        if len(self.image_files) > 0:
            response = self.generate_with_images(full_prompt, self.image_files, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug)
        elif len(images) > 0:
            response = self.generate_with_images(full_prompt, images, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug)
        else:
            response = self.generate(full_prompt, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug)
        
        response_full += response

        if debug:
            ASCIIColors.green("Initial Response")
            ASCIIColors.green(response_full)
            
        codes = self.extract_code_blocks(response)
        if len(codes) == 0 and accept_all_if_no_code_tags_is_present:
            if return_full_generated_code:
                return response, response_full
            else:
                return response

        code = None
        is_complete = False
        if len(codes) > 0:
            code_info = codes[-1]
            code = code_info["content"]
            is_complete = code_info["is_complete"]
            current_code = code
        else:
            code = None
            current_code = ""

        # Continuation loop for incomplete code
        continues = 0
        while not is_complete and continues < max_continues and code is not None:
            continues += 1
            if debug:
                ASCIIColors.yellow(f"Attempting continuation {continues}/{max_continues}")

            # Prepare continuation prompt
            continuation_prompt = (
                f"The previous {language} code generation was interrupted. Continue EXACTLY from the last line below.\n"
                f"Follow all original directives. Respond ONLY with a SINGLE code block continuing from this point:\n"
                f"```{language}\n"
                f"{current_code.strip()}\n"  # Show current code to continue from
                f"```\n"
                f"Important: Do NOT repeat any previous code. Start your response with the code block."
            )

            # Generate continuation
            if len(images) > 0:
                cont_response = self.generate_with_images(continuation_prompt, images, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug)
            else:
                cont_response = self.generate(continuation_prompt, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug)
            
            response_full += cont_response

            # Extract continuation code
            cont_codes = self.extract_code_blocks(cont_response)
            if len(cont_codes) == 0:
                if debug:
                    ASCIIColors.red("No code found in continuation response")
                break

            cont_code_info = cont_codes[-1]
            cont_code = cont_code_info["content"]
            cont_is_complete = cont_code_info["is_complete"]

            # Remove overlapping lines from continuation
            current_lines = current_code.split('\n')
            cont_lines = cont_code.split('\n')
            
            # Find maximum overlap
            overlap = 0
            max_check = min(len(current_lines), len(cont_lines))
            for i in range(1, max_check + 1):
                if current_lines[-i:] == cont_lines[:i]:
                    overlap = i

            # Merge codes
            if overlap > 0:
                merged_code = '\n'.join(current_lines) + '\n' + '\n'.join(cont_lines[overlap:])
            else:
                merged_code = current_code + '\n' + cont_code

            current_code = merged_code.strip('\n')
            is_complete = cont_is_complete

            if debug:
                ASCIIColors.cyan(f"Continuation {continues} result:")
                ASCIIColors.cyan(current_code)
                ASCIIColors.cyan(f"Code complete: {is_complete}")

        # Final code validation
        if code is not None:
            code = current_code
            if debug:
                ASCIIColors.green("Final generated code:")
                ASCIIColors.green(code)

        if return_full_generated_code:
            return code, response_full
        else:
            return code


    def generate_text(
                        self, 
                        prompt, 
                        images=[],
                        template=None,
                        code_tag_format="markdown", # or "html"
                        max_size = None,  
                        temperature = None, 
                        top_k = None, 
                        top_p=None, 
                        repeat_penalty=None, 
                        repeat_last_n=None, 
                        callback=None, 
                        debug=False, 
                        return_full_generated_code=False, 
                        accept_all_if_no_code_tags_is_present=False, 
                        max_continues=5
                    ):
        response_full = ""
        full_prompt = f"""{self.system_full_header}Act as a code generation assistant who answers with code tags content.    
{self.user_full_header} 
{prompt}
Make sure only a single code tag is generated at each dialogue turn.
"""
        if template:
            full_prompt += "Here is a template of the answer:\n"
            if code_tag_format=="markdown":
                full_prompt += f"""You must answer with the code placed inside the markdown code tag like this:
```plaintext
{template}
```
The code tag is mandatory.
Don't forget encapsulate the code inside a markdown code tag. This is mandatory.
{self.ai_full_header} 
"""
            elif code_tag_format=="html":
                full_prompt +=f"""You must answer with the code placed inside the html code tag like this:
<code language="plaintext">
{template}
</code>
The code tag is mandatory.
Don't forget encapsulate the code inside a html code tag. This is mandatory.
{self.ai_full_header} 
"""

        full_prompt += self.ai_custom_header("assistant")
        if debug:
            ASCIIColors.yellow("Full text generation code:")
            ASCIIColors.yellow(full_prompt)
        if len(self.image_files)>0:
            response = self.generate_with_images(full_prompt, self.image_files, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug)
        elif  len(images)>0:
            response = self.generate_with_images(full_prompt, images, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug)
        else:
            response = self.generate(full_prompt, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug)
        if debug:
            ASCIIColors.green("Response:")
            ASCIIColors.green(response)
        response_full += response
        codes = self.extract_code_blocks(response)
        if len(codes)==0 and accept_all_if_no_code_tags_is_present:
            if return_full_generated_code:
                return response, response_full
            else:
                return response
        if len(codes)>0:
            if not codes[-1]["is_complete"]:
                code = "\n".join(codes[-1]["content"].split("\n")[:-1])
                nb_continues = 0
                while not codes[-1]["is_complete"] and nb_continues<max_continues:
                    response = self.generate(full_prompt+code+self.user_full_header+"continue the code. Start from last line and continue the code. Put the code inside a markdown code tag."+self.separator_template+self.ai_full_header, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug)
                    response_full += response
                    codes = self.extract_code_blocks(response)
                    if len(codes)==0:
                        break
                    else:
                        if not codes[-1]["is_complete"]:
                            code +="\n"+ "\n".join(codes[-1]["content"].split("\n")[:-1])
                        else:
                            code +="\n"+ "\n".join(codes[-1]["content"].split("\n"))
                    nb_continues += 1
            else:
                code = codes[-1]["content"]
            
            if return_full_generated_code:
                return code, response_full
            else:
                return code
        else:
            return None

    def generate_structured_content(
            self, 
            prompt,
            images=[],
            template=None,
            output_format="json",
            callback=None
        ):
            """
            Generates structured content (e.g., JSON, YAML, XML) based on a prompt and template.

            Args:
                prompt (str): The input prompt describing the desired content.
                images (list, optional): List of images to include in the generation process.
                template (dict, optional): A template defining the structure of the output.
                single_shot (bool, optional): If True, generates content in a single attempt without continuations.
                output_format (str, optional): The format of the structured content (e.g., "json", "yaml", "xml").

            Returns:
                dict: A dictionary containing:
                    - "data": The parsed structured content (e.g., dict, list).
                    - "formatted_string": The formatted string representation of the content.
            """
            return    self.generate_code(
                        prompt, 
                        images=images,
                        template=template,
                        language=output_format,
                        code_tag_format="markdown",  # or "html"
                        debug=None,
                        callback=callback
                    )
        
    def extract_thinking_blocks(self, text: str) -> List[str]:
        """
        Extracts content between <thinking> or  tags from a given text.
        If a closing tag is present without an opening tag, the content from the start of the text up to the closing tag is extracted.
        If both opening and closing tags are present, extracts all content between them.

        Parameters:
            text (str): The text containing thinking blocks

        Returns:
            List[str]: List of extracted thinking contents
        """
        # Pattern to match both thinking and think blocks with matching tags
        pattern = r'<(thinking|think)>(.*?)</\1>'
        matches = re.finditer(pattern, text, re.DOTALL)

        # Extract content from the second group and clean
        thinking_blocks = [match.group(2).strip() for match in matches]

        # Check for closing tags without opening tags
        if not thinking_blocks:
            # Look for any closing tag without a matching opening tag
            closing_pattern = r'</(thinking|think)>'
            closing_match = re.search(closing_pattern, text)
            if closing_match:
                # Extract content from start up to the closing tag
                content = text.split('</')[0].strip()
                thinking_blocks.append(content)

        return thinking_blocks

    def remove_thinking_blocks(self, text: str) -> str:
        """
        Removes thinking blocks (either <thinking> or <think>) from text, including the tags.
        If a closing tag is present without a corresponding opening tag, the content from the start of the text up to the closing tag is removed.

        Parameters:
        text (str): The text containing thinking blocks

        Returns:
        str: Text with thinking blocks removed
        """
        import re

        # First, remove blocks with both opening and closing tags
        pattern_with_tags = r'<(thinking|think)>.*?</\1>'
        cleaned_text = re.sub(pattern_with_tags, '', text, flags=re.DOTALL)

        # Then, remove content starting from the beginning up to a closing tag without an opening
        pattern_without_opening = r'^.*?</(thinking|think)>'
        cleaned_text = re.sub(pattern_without_opening, '', cleaned_text, flags=re.DOTALL)

        # Remove extra whitespace and normalize newlines
        cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text.strip())

        return cleaned_text


    def extract_code_blocks(self, text: str, return_remaining_text: bool = False) -> Union[List[dict], Tuple[List[dict], str]]:
        """
        This function extracts code blocks from a given text and optionally returns the text without code blocks.

        Parameters:
        text (str): The text from which to extract code blocks. Code blocks are identified by triple backticks (```).
        return_remaining_text (bool): If True, also returns the text with code blocks removed.

        Returns:
        Union[List[dict], Tuple[List[dict], str]]: 
            - If return_remaining_text is False: Returns only the list of code block dictionaries
            - If return_remaining_text is True: Returns a tuple containing:
                * List of code block dictionaries
                * String containing the text with all code blocks removed
            
        Each code block dictionary contains:
            - 'index' (int): The index of the code block in the text
            - 'file_name' (str): The name of the file extracted from the preceding line, if available
            - 'content' (str): The content of the code block
            - 'type' (str): The type of the code block
            - 'is_complete' (bool): True if the block has a closing tag, False otherwise
        """        
        remaining = text
        bloc_index = 0
        first_index = 0
        indices = []
        text_without_blocks = text
        
        # Find all code block delimiters
        while len(remaining) > 0:
            try:
                index = remaining.index("```")
                indices.append(index + first_index)
                remaining = remaining[index + 3:]
                first_index += index + 3
                bloc_index += 1
            except Exception as ex:
                if bloc_index % 2 == 1:
                    index = len(remaining)
                    indices.append(index)
                remaining = ""

        code_blocks = []
        is_start = True
        
        # Process code blocks and build text without blocks if requested
        if return_remaining_text:
            text_parts = []
            last_end = 0
            
        for index, code_delimiter_position in enumerate(indices):
            if is_start:
                block_infos = {
                    'index': len(code_blocks),
                    'file_name': "",
                    'section': "",
                    'content': "",
                    'type': "",
                    'is_complete': False
                }
                
                # Store text before code block if returning remaining text
                if return_remaining_text:
                    text_parts.append(text[last_end:code_delimiter_position].strip())
                
                # Check the preceding line for file name
                preceding_text = text[:code_delimiter_position].strip().splitlines()
                if preceding_text:
                    last_line = preceding_text[-1].strip()
                    if last_line.startswith("<file_name>") and last_line.endswith("</file_name>"):
                        file_name = last_line[len("<file_name>"):-len("</file_name>")].strip()
                        block_infos['file_name'] = file_name
                    elif last_line.startswith("## filename:"):
                        file_name = last_line[len("## filename:"):].strip()
                        block_infos['file_name'] = file_name
                    if last_line.startswith("<section>") and last_line.endswith("</section>"):
                        section = last_line[len("<section>"):-len("</section>")].strip()
                        block_infos['section'] = section

                sub_text = text[code_delimiter_position + 3:]
                if len(sub_text) > 0:
                    try:
                        find_space = sub_text.index(" ")
                    except:
                        find_space = int(1e10)
                    try:
                        find_return = sub_text.index("\n")
                    except:
                        find_return = int(1e10)
                    next_index = min(find_return, find_space)
                    if '{' in sub_text[:next_index]:
                        next_index = 0
                    start_pos = next_index
                    
                    if code_delimiter_position + 3 < len(text) and text[code_delimiter_position + 3] in ["\n", " ", "\t"]:
                        block_infos["type"] = 'language-specific'
                    else:
                        block_infos["type"] = sub_text[:next_index]

                    if index + 1 < len(indices):
                        next_pos = indices[index + 1] - code_delimiter_position
                        try:
                            if next_pos - 3 < len(sub_text) and sub_text[next_pos - 3] == "`":
                                block_infos["content"] = sub_text[start_pos:next_pos - 3].strip()
                                block_infos["is_complete"] = True
                            else:
                                block_infos["content"] = sub_text[start_pos:next_pos].strip()
                                block_infos["is_complete"] = False
                        except Exception as ex:
                            ASCIIColors.error("Trouble extracting code")
                            ASCIIColors.error(f"next_pos:{next_pos}\nsub_text length:{len(sub_text)}")                        
                            ASCIIColors.error(f"Trying to access:{next_pos-3}")                        
                        if return_remaining_text:
                            last_end = indices[index + 1] + 3
                    else:
                        block_infos["content"] = sub_text[start_pos:].strip()
                        block_infos["is_complete"] = False
                        
                        if return_remaining_text:
                            last_end = len(text)
                    
                    code_blocks.append(block_infos)
                is_start = False
            else:
                is_start = True
                
        if return_remaining_text:
            # Add any remaining text after the last code block
            if last_end < len(text):
                text_parts.append(text[last_end:].strip())
            # Join all non-code parts with newlines
            text_without_blocks = '\n'.join(filter(None, text_parts))
            return code_blocks, text_without_blocks
            
        return code_blocks



    def process(self, text:str, message_type:MSG_OPERATION_TYPE, callback=None, show_progress=False):
        if callback is None:
            callback = self.callback
        if text is None:
            return True
        if message_type==MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK:
            bot_says = self.bot_says + text
        elif  message_type==MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT:
            bot_says = text

        if show_progress:
            if self.nb_received_tokens==0:
                self.start_time = datetime.now()
            dt =(datetime.now() - self.start_time).seconds
            if dt==0:
                dt=1
            spd = self.nb_received_tokens/dt
            ASCIIColors.green(f"Received {self.nb_received_tokens} tokens (speed: {spd:.2f}t/s)              ",end="\r",flush=True)
            sys.stdout = sys.__stdout__
            sys.stdout.flush()
            self.nb_received_tokens+=1


        antiprompt = self.detect_antiprompt(bot_says)
        if antiprompt:
            self.bot_says = remove_text_from_string(bot_says,antiprompt)
            ASCIIColors.warning(f"\n{antiprompt} detected. Stopping generation")
            return False
        else:
            if callback:
                callback(text,message_type)
            self.bot_says = bot_says
            return True

    def generate_with_images(self, prompt, images, max_size=None, temperature = None, top_k = None, top_p=None, repeat_penalty=None, repeat_last_n=None, callback=None, debug=False, show_progress=False ):
        ASCIIColors.info("Text generation started: Warming up")
        self.nb_received_tokens = 0
        self.bot_says = ""
        if debug:
            self.print_prompt("gen",prompt)

        if max_size is None:
            max_size = min(self.config.max_n_predict if self.config.max_n_predict else self.config.ctx_size-self.model.count_tokens(prompt), self.config.ctx_size-self.model.count_tokens(prompt))

        self.model.generate_with_images(
                                prompt,
                                images,
                                max_size,
                                partial(self.process, callback=callback, show_progress=show_progress),
                                temperature=self.model_temperature if temperature is None else temperature,
                                top_k=self.model_top_k if top_k is None else top_k,
                                top_p=self.model_top_p if top_p is None else top_p,
                                repeat_penalty=self.model_repeat_penalty if repeat_penalty is None else repeat_penalty,
                                repeat_last_n = self.model_repeat_last_n if repeat_last_n is None else repeat_last_n
                                )
        return self.bot_says

    def generate(self, prompt, max_size = None, temperature = None, top_k = None, top_p=None, repeat_penalty=None, repeat_last_n=None, callback=None, debug=False, show_progress=False ):
        ASCIIColors.info("Text generation started: Warming up")
        self.nb_received_tokens = 0
        self.bot_says = ""
        if debug:
            self.print_prompt("gen",prompt)
        ntokens = self.model.count_tokens(prompt)
        
        self.model.generate(
                                prompt,
                                max_size if max_size else min(self.config.ctx_size-ntokens,self.config.max_n_predict if self.config.max_n_predict else self.config.ctx_size-ntokens),
                                partial(self.process, callback=callback, show_progress=show_progress),
                                temperature=self.model_temperature if temperature is None else temperature,
                                top_k=self.model_top_k if top_k is None else top_k,
                                top_p=self.model_top_p if top_p is None else top_p,
                                repeat_penalty=self.model_repeat_penalty if repeat_penalty is None else repeat_penalty,
                                repeat_last_n = self.model_repeat_last_n if repeat_last_n is None else repeat_last_n,
                                )
        if debug:
            self.print_prompt("prompt", prompt+self.bot_says)
        
        return self.bot_says

    def setCallback(self, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]):
        self.callback = callback
        if self._processor:
            self._processor.callback = callback


    def __str__(self):
        return f"{self.category}/{self.name}"

    def set_config(self, config, is_default_language= True):
        # Load parameters from the configuration file
        self._version = config.get("version", self._version)
        self._author = config.get("author", self._author)
        self._language = config.get("language", self._language).lower()
        self._name = config.get("name", self._name)
        self._creation_date = config.get("creation_date", self._creation_date)
        self._last_update_date = config.get("last_update_date", self._last_update_date)
        
        self._user_name = config.get("user_name", self._user_name)
        self._category_desc = config.get("category", self._category)
        if is_default_language:
            self._default_language = config.get("language", self._language).lower()

        self._ignore_discussion_documents_rag = config.get("ignore_discussion_documents_rag", self._ignore_discussion_documents_rag)


        self._personality_description = config.get("personality_description", self._personality_description)
        self._personality_conditioning = config.get("personality_conditioning", self._personality_conditioning)
        self._prompts_list = config.get("prompts_list", self._prompts_list)
        try:
            personality_folder = self.lollms_paths.personal_configuration_path/"personalities"/self.personality_folder_name
            personality_folder.mkdir(exist_ok=True, parents=True)
            custom_prompts = personality_folder/"custom_prompts.yaml"
            if custom_prompts.exists():
                with open(custom_prompts,"r") as f:
                    data = yaml.safe_load(f)
                    self._prompts_list.append(data["custom_prompts"])
        except Exception as ex:
            trace_exception(ex)
        self._welcome_message = config.get("welcome_message", self._welcome_message)
        self._include_welcome_message_in_discussion = config.get("include_welcome_message_in_discussion", self._include_welcome_message_in_discussion)

        self._user_message_prefix = config.get("user_message_prefix", self._user_message_prefix)
        self._link_text = config.get("link_text", self._link_text)
        self._ai_message_prefix = config.get("ai_message_prefix", self._ai_message_prefix)
        self._dependencies = config.get("dependencies", self._dependencies)
        self._disclaimer = config.get("disclaimer", self._disclaimer)
        self._help = config.get("help", self._help)
        self._commands = config.get("commands", self._commands)
        self._model_temperature = config.get("model_temperature", self._model_temperature)
        self._model_top_k = config.get("model_top_k", self._model_top_k)
        self._model_top_p = config.get("model_top_p", self._model_top_p)
        self._model_repeat_penalty = config.get("model_repeat_penalty", self._model_repeat_penalty)
        self._model_repeat_last_n = config.get("model_repeat_last_n", self._model_repeat_last_n)

        # Script parameters (for example keys to connect to search engine or any other usage)
        self._processor_cfg = config.get("processor_cfg", self._processor_cfg)

    def add_prompt(self, prompt):
        try:
            personality_folder = self.lollms_paths.personal_configuration_path/"personalities"/self.personality_folder_name
            personality_folder.mkdir(exist_ok=True, parents=True)
            custom_prompts = personality_folder/"custom_prompts.yaml"
            if custom_prompts.exists():
                with open(custom_prompts,"r") as f:
                    data = yaml.safe_load(f)
                    data["custom_prompts"].append(prompt)
            else:
                data = {
                    "custom_prompts":[prompt]
                }                
            with open(custom_prompts,"w") as f:
                yaml.dump(data, f)
        except Exception as ex:
            trace_exception(ex)

    def delete_prompt(self, prompt):
        try:
            personality_folder = self.lollms_paths.personal_configuration_path/"personalities"/self.personality_folder_name
            personality_folder.mkdir(exist_ok=True, parents=True)
            custom_prompts = personality_folder/"custom_prompts.yaml"
            if custom_prompts.exists():
                with open(custom_prompts,"r") as f:
                    data = yaml.safe_load(f)
                    index = data["custom_prompts"].index(prompt)
                    if index>=0:
                        del data["custom_prompts"][index]
                with open(custom_prompts,"w") as f:
                    yaml.dump(data, f)
        except Exception as ex:
            trace_exception(ex)

    def set_language(self, language):
        self.language = language


    def load_personality(self, package_path=None):
        """
        Load personality parameters from a YAML configuration file.

        Args:
            package_path (str or Path): The path to the package directory.

        Raises:
            ValueError: If the configuration file does not exist.
        """
        if package_path is None:
            package_path = self.personality_package_path
        else:
            package_path = Path(package_path)

        # Verify that there is at least a configuration file
        config_file = package_path / "config.yaml"
        if not config_file.exists():
            raise ValueError(f"The provided folder {package_path} does not exist.")

        with open(config_file, "r", encoding='utf-8') as f:
            config = yaml.safe_load(f)

        secret_file = package_path / "secret.yaml"
        if secret_file.exists():
            with open(secret_file, "r", encoding='utf-8') as f:
                self._secret_cfg = yaml.safe_load(f)
        else:
            self._secret_cfg = None

        self.set_config(config, True)

        lang = config.get("language","english").lower()

        #set package path
        self.personality_package_path = package_path

        # Check for a logo file
        self.logo_path = self.personality_package_path / "assets" / "logo.png"
        if self.logo_path.is_file():
            self._logo = Image.open(self.logo_path)

        # Get the assets folder path
        self.assets_path = self.personality_package_path / "assets"
        # Get the scripts folder path
        self.scripts_path = self.personality_package_path / "scripts"
        # Get the languages folder path
        self.languages_path = self.personality_package_path / "languages"
        # Get the data folder path
        self.data_path = self.personality_package_path / "data"
        # Get the data folder path
        self.audio_path = self.personality_package_path / "audio"
        # Get the data folder path
        self.welcome_audio_path = self.personality_package_path / "welcome_audio"


        # If not exist recreate
        self.assets_path.mkdir(parents=True, exist_ok=True)

        # If not exist recreate
        self.scripts_path.mkdir(parents=True, exist_ok=True)

        # If not exist recreate
        self.audio_path.mkdir(parents=True, exist_ok=True)

        # samples
        self.audio_samples = [f for f in self.audio_path.iterdir()]

        # Verify if the persona has a data folder
        if self.data_path.exists():
            self.database_path = self.data_path / "db.db"
            self.persona_data_vectorizer = SafeStore(self.database_path)

            files = [f for f in self.data_path.iterdir() if f.suffix.lower() in ['.asm', '.bat', '.c', '.cpp', '.cs', '.csproj', '.css',
                '.csv', '.docx', '.h', '.hh', '.hpp', '.html', '.inc', '.ini', '.java', '.js', '.json', '.log',
                '.lua', '.map', '.md', '.pas', '.pdf', '.php', '.pptx', '.ps1', '.py', '.rb', '.rtf', '.s', '.se', '.sh', '.sln',
                '.snippet', '.snippets', '.sql', '.sym', '.ts', '.txt', '.xlsx', '.xml', '.yaml', '.yml', '.msg'] ]

            for f in files:
                self.persona_data_vectorizer.add_document(f, self.config.rag_vectorizer)

        else:
            self.persona_data_vectorizer = None
            self._data = None

        self.personality_output_folder = self.lollms_paths.personal_outputs_path/self.name
        self.personality_output_folder.mkdir(parents=True, exist_ok=True)


        if self.run_scripts:
            # Search for any processor code
            processor_file_name = "processor.py"
            self.processor_script_path = self.scripts_path / processor_file_name
            if self.processor_script_path.exists():
                module_name = processor_file_name[:-3]  # Remove the ".py" extension
                module_spec = importlib.util.spec_from_file_location(module_name, str(self.processor_script_path))
                module = importlib.util.module_from_spec(module_spec)
                module_spec.loader.exec_module(module)
                if hasattr(module, "Processor"):
                    self._processor = module.Processor(self, callback=self.callback)
                else:
                    self._processor = None
            else:
                self._processor = None
        # Get a list of all files in the assets folder
        contents = [str(file) for file in self.assets_path.iterdir() if file.is_file()]

        self._assets_list = contents
        return config



    def remove_file(self, file_name, callback=None):
        try:
            if any(file_name == entry.name for entry in self.text_files):
                fn = [entry for entry in self.text_files if entry.name == file_name][0]
                self.text_files = [entry for entry in self.text_files if entry.name != file_name]
                Path(fn).unlink()
                if len(self.text_files)>0:
                    try:
                        self.vectorizer.remove_document(fn)
                        if callback is not None:
                            callback("File removed successfully",MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_INFO)
                        return True
                    except ValueError as ve:
                        ASCIIColors.error(f"Couldn't remove the file")
                        return False
                else:
                    self.vectorizer = None
            elif any(file_name == entry.name for entry in self.image_files):
                fn = [entry for entry in self.image_files if entry.name == file_name][0]
                self.text_files = [entry for entry in self.image_files if entry.name != file_name]
                Path(fn).unlink()

        except Exception as ex:
            ASCIIColors.warning(f"Couldn't remove the file {file_name}")

    def remove_all_files(self, callback=None):
        for file in self.text_files:
            try:
                Path(file).unlink()
            except Exception as ex:
                ASCIIColors.warning(f"Couldn't remove the file {file}")
        for file in self.image_files:
            try:
                Path(file).unlink()
            except Exception as ex:
                ASCIIColors.warning(f"Couldn't remove the file {file}")
        self.text_files=[]
        self.image_files=[]
        self.vectorizer = None
        return True

    def add_file(self, path, client:Client, callback=None, process=True):
        output = ""
        if not self.callback:
            self.callback = callback

        path = Path(path)
        if path.suffix in [".wav",".mp3"]:
            self.audio_files.append(path)
            if process:
                self.new_message("")
                self.ShowBlockingMessage(f"Transcribing ... ")
                if self.app.stt is None:
                    self.InfoMessage("No STT service is up.\nPlease configure your default STT service in the settings page.")
                    return
                text = self.app.stt.transcribe(str(path))
                transcription_fn = str(path)+".txt"
                with open(transcription_fn, "w", encoding="utf-8") as f:
                    f.write(text)

                self.info(f"File saved to {transcription_fn}")
                self.set_message_content(text)
        elif path.suffix in [".png",".jpg",".jpeg",".gif",".bmp",".svg",".webp"]:
            self.image_files.append(path)
            if process:
                if self.callback:
                    try:
                        pth = str(path).replace("\\","/").split('/')
                        if "discussion_databases" in pth:
                            pth = discussion_path_to_url(path)
                            self.new_message("",MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT)
                            output = f'<img src="{pth}" width="800">\n\n'
                            self.set_message_html(output)
                            self.app.close_message(client.client_id if client is not None else 0)

                        if self.model.binding_type not in [BindingType.TEXT_IMAGE, BindingType.TEXT_IMAGE_VIDEO]:
                            # self.ShowBlockingMessage("Understanding image (please wait)")
                            from PIL import Image
                            img = Image.open(str(path))
                            # Convert the image to RGB mode
                            img = img.convert("RGB")
                            output += "## image description :\n"+ self.model.interrogate_blip([img])[0]
                            # output += "## image description :\n"+ self.model.qna_blip([img],"q:Describe this photo with as much details as possible.\na:")[0]
                            self.set_message_content(output)
                            self.app.close_message(client.client_id if client is not None else 0)
                            self.HideBlockingMessage("Understanding image (please wait)")
                            if self.config.debug:
                                ASCIIColors.yellow(output)
                        else:
                            # self.ShowBlockingMessage("Importing image (please wait)")
                            self.HideBlockingMessage("Importing image (please wait)")

                    except Exception as ex:
                        trace_exception(ex)
                        self.HideBlockingMessage("Understanding image (please wait)", False)
                        ASCIIColors.error("Couldn't create new message")
            ASCIIColors.info("Received image file")
            if callback is not None:
                callback("Image file added successfully", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_INFO)
        else:
            try:
                # self.ShowBlockingMessage("Adding file to vector store.\nPlease stand by")
                self.text_files.append(path)
                ASCIIColors.info("Received text compatible file")
                self.ShowBlockingMessage("Processing file\nPlease wait ...")
                if process:
                    if self.vectorizer is None:
                        self.vectorizer = SafeStore(
                                    client.discussion.discussion_rag_folder/"db.sqli")
                    self.vectorizer.add_document(path, self.config.rag_vectorizer, chunk_size=self.config.rag_chunk_size, chunk_overlap=self.config.rag_overlap,metadata={"title":path.stem})
                    if callback is not None:
                        callback("File added successfully",MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_INFO)
                    self.HideBlockingMessage(client.client_id)
                    return True
            except Exception as e:
                trace_exception(e)
                self.InfoMessage(f"Unsupported file format or empty file.\nSupported formats are {SAFE_STORE_SUPPORTED_FILE_EXTENSIONS}",client_id=client.client_id)
                return False
            

    def save_personality(self, package_path=None):
        """
        Save the personality parameters to a YAML configuration file.

        Args:
            package_path (str or Path): The path to the package directory.
        """
        if package_path is None:
            package_path = self.personality_package_path
        else:
            package_path = Path(package_path)

        # Building output path
        config_file = package_path / "config.yaml"
        assets_folder = package_path / "assets"

        # Create assets folder if it doesn't exist
        if not assets_folder.exists():
            assets_folder.mkdir(exist_ok=True, parents=True)

        # Create the configuration dictionary
        config = {
            "author": self._author,
            "version": self._version,
            "name": self._name,
            "creation_date": self._creation_date,
            "last_update_date": self._last_update_date,
            "user_name": self._user_name,
            "category": self._category,
            "language": self._default_language,
            "supported_languages": self._supported_languages,
            "selected_language": self._selected_language,
            "ignore_discussion_documents_rag": self._ignore_discussion_documents_rag,
            "personality_description": self._personality_description,
            "personality_conditioning": self._personality_conditioning,
            "prompts_list": self._prompts_list,
            "welcome_message": self._welcome_message,
            "include_welcome_message_in_discussion": self._include_welcome_message_in_discussion,
            "user_message_prefix": self._user_message_prefix,
            "link_text": self._link_text,
            "ai_message_prefix": self._ai_message_prefix,
            "dependencies": self._dependencies,
            "disclaimer": self._disclaimer,
            "help": self._help,
            "commands": self._commands,
            "model_temperature": self._model_temperature,
            "model_top_k": self._model_top_k,
            "model_top_p": self._model_top_p,
            "model_repeat_penalty": self._model_repeat_penalty,
            "model_repeat_last_n": self._model_repeat_last_n
        }

        # Save the configuration to the YAML file
        with open(config_file, "w") as f:
            yaml.dump(config, f)



    def as_dict(self):
        """
        Convert the personality parameters to a dictionary.

        Returns:
            dict: The personality parameters as a dictionary.
        """
        return {
            "author": self._author,
            "version": self._version,
            "name": self._name,
            "creation_date": self._creation_date,
            "last_update_date": self._last_update_date,
            "user_name": self._user_name,
            "category": self._category,
            "language": self._language,
            "default_language": self._default_language,
            "supported_languages": self._supported_languages,
            "selected_language": self._selected_language,
            "ignore_discussion_documents_rag": self._ignore_discussion_documents_rag,
            "personality_description": self._personality_description,
            "personality_conditioning": self._personality_conditioning,
            "_prompts_list": self._prompts_list,
            "welcome_message": self._welcome_message,
            "include_welcome_message_in_discussion": self._include_welcome_message_in_discussion,
            "user_message_prefix": self._user_message_prefix,
            "link_text": self._link_text,
            "ai_message_prefix": self._ai_message_prefix,
            "dependencies": self._dependencies,
            "disclaimer": self._disclaimer,
            "help": self._help,
            "commands": self._commands,
            "model_temperature": self._model_temperature,
            "model_top_k": self._model_top_k,
            "model_top_p": self._model_top_p,
            "model_repeat_penalty": self._model_repeat_penalty,
            "model_repeat_last_n": self._model_repeat_last_n,
            "assets_list":self._assets_list
        }

    # ========================================== Properties ===========================================

    @property
    def logo(self):
        """
        Get the personality logo.

        Returns:
        PIL.Image.Image: The personality logo as a Pillow Image object.
        """
        if hasattr(self, '_logo'):
            return self._logo
        else:
            return None
    @property
    def version(self):
        """Get the version of the package."""
        return self._version

    @version.setter
    def version(self, value):
        """Set the version of the package."""
        self._version = value

    @property
    def author(self):
        """Get the author of the package."""
        return self._author

    @author.setter
    def author(self, value):
        """Set the author of the package."""
        self._author = value

    @property
    def name(self) -> str:
        """Get the name."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Set the name."""
        self._name = value

    @property
    def creation_date(self) -> str:
        """Get the name."""
        return self._creation_date

    @creation_date.setter
    def creation_date(self, value: str):
        """Set the name."""
        self._creation_date = value        

    @property
    def last_update_date(self) -> str:
        """Get the name."""
        return self._last_update_date

    @last_update_date.setter
    def last_update_date(self, value: str):
        """Set the name."""
        self._last_update_date = value        

    @property
    def user_name(self) -> str:
        """Get the user name."""
        return self._user_name

    @user_name.setter
    def user_name(self, value: str):
        """Set the user name."""
        self._user_name = value


    @property
    def language(self) -> str:
        """Get the language."""
        return self._language


    @property
    def default_language(self) -> str:
        """Get the default language."""
        return self._default_language

    

    @property
    def category(self) -> str:
        """Get the category."""
        return self._category

    @property
    def category_desc(self) -> str:
        """Get the category."""
        return self._category_desc

    @language.setter
    def language(self, value: str):
        """Set the language."""
        self._language = value

    @default_language.setter
    def language(self, value: str):
        """Set the default language."""
        self._default_language = value
        

    @category.setter
    def category(self, value: str):
        """Set the category."""
        self._category = value

    @category_desc.setter
    def category_desc(self, value: str):
        """Set the category."""
        self._category_desc = value


    @property
    def supported_languages(self) -> str:
        """Get the supported_languages."""
        return self._supported_languages

    @supported_languages.setter
    def supported_languages(self, value: str):
        """Set the supported_languages."""
        self._supported_languages = value


    @property
    def selected_language(self) -> str:
        """Get the selected_language."""
        return self._selected_language

    @selected_language.setter
    def selected_language(self, value: str):
        """Set the selected_language."""
        self._selected_language = value

    @property
    def ignore_discussion_documents_rag(self) -> str:
        """Get the ignore_discussion_documents_rag."""
        return self._ignore_discussion_documents_rag

    @ignore_discussion_documents_rag.setter
    def ignore_discussion_documents_rag(self, value: str):
        """Set the ignore_discussion_documents_rag."""
        self._ignore_discussion_documents_rag = value


    @property
    def personality_description(self) -> str:
        """
        Getter for the personality description.

        Returns:
            str: The personality description of the AI assistant.
        """
        return self._personality_description

    @personality_description.setter
    def personality_description(self, description: str):
        """
        Setter for the personality description.

        Args:
            description (str): The new personality description for the AI assistant.
        """
        self._personality_description = description

    @property
    def personality_conditioning(self) -> str:
        """
        Getter for the personality conditioning.

        Returns:
            str: The personality conditioning of the AI assistant.
        """
        return self._personality_conditioning

    @personality_conditioning.setter
    def personality_conditioning(self, conditioning: str):
        """
        Setter for the personality conditioning.

        Args:
            conditioning (str): The new personality conditioning for the AI assistant.
        """
        self._personality_conditioning = conditioning

    @property
    def prompts_list(self) -> str:
        """
        Getter for the personality conditioning.

        Returns:
            str: The personality conditioning of the AI assistant.
        """
        return self._prompts_list

    @prompts_list.setter
    def prompts_list(self, prompts: str):
        """
        Setter for the personality conditioning.

        Args:
            conditioning (str): The new personality conditioning for the AI assistant.
        """
        self._prompts_list = prompts

    @property
    def welcome_message(self) -> str:
        """
        Getter for the welcome message.

        Returns:
            str: The welcome message of the AI assistant.
        """
        return self._welcome_message

    @welcome_message.setter
    def welcome_message(self, message: str):
        """
        Setter for the welcome message.

        Args:
            message (str): The new welcome message for the AI assistant.
        """
        self._welcome_message = message

    @property
    def include_welcome_message_in_discussion(self) -> bool:
        """
        Getter for the include welcome message in disucssion.

        Returns:
            bool: whether to add the welcome message to tje discussion or not.
        """
        return self._include_welcome_message_in_discussion

    @include_welcome_message_in_discussion.setter
    def include_welcome_message_in_discussion(self, message: bool):
        """
        Setter for the welcome message.

        Args:
            message (str): The new welcome message for the AI assistant.
        """
        self._include_welcome_message_in_discussion = message


    @property
    def user_message_prefix(self) -> str:
        """
        Getter for the user message prefix.

        Returns:
            str: The user message prefix of the AI assistant.
        """
        return self._user_message_prefix

    @user_message_prefix.setter
    def user_message_prefix(self, prefix: str):
        """
        Setter for the user message prefix.

        Args:
            prefix (str): The new user message prefix for the AI assistant.
        """
        self._user_message_prefix = prefix

    @property
    def link_text(self) -> str:
        """
        Getter for the link text.

        Returns:
            str: The link text of the AI assistant.
        """
        return self._link_text

    @link_text.setter
    def link_text(self, text: str):
        """
        Setter for the link text.

        Args:
            text (str): The new link text for the AI assistant.
        """
        self._link_text = text
    @property
    def ai_message_prefix(self):
        """
        Get the AI message prefix.

        Returns:
            str: The AI message prefix.
        """
        return self._ai_message_prefix

    @ai_message_prefix.setter
    def ai_message_prefix(self, prefix):
        """
        Set the AI message prefix.

        Args:
            prefix (str): The AI message prefix to set.
        """
        self._ai_message_prefix = prefix

    @property
    def dependencies(self) -> List[str]:
        """Getter method for the dependencies attribute.

        Returns:
            List[str]: The list of dependencies.
        """
        return self._dependencies

    @dependencies.setter
    def dependencies(self, dependencies: List[str]):
        """Setter method for the dependencies attribute.

        Args:
            dependencies (List[str]): The list of dependencies.
        """
        self._dependencies = dependencies

    @property
    def disclaimer(self) -> str:
        """Getter method for the disclaimer attribute.

        Returns:
            str: The disclaimer text.
        """
        return self._disclaimer

    @disclaimer.setter
    def disclaimer(self, disclaimer: str):
        """Setter method for the disclaimer attribute.

        Args:
            disclaimer (str): The disclaimer text.
        """
        self._disclaimer = disclaimer

    @property
    def help(self) -> str:
        """Getter method for the help attribute.

        Returns:
            str: The help text.
        """
        return self._help

    @help.setter
    def help(self, help: str):
        """Setter method for the help attribute.

        Args:
            help (str): The help text.
        """
        self._help = help



    @property
    def commands(self) -> str:
        """Getter method for the commands attribute.

        Returns:
            str: The commands text.
        """
        return self._commands

    @commands.setter
    def commands(self, commands: str):
        """Setter method for the commands attribute.

        Args:
            commands (str): The commands text.
        """
        self._commands = commands


    @property
    def model_temperature(self) -> float:
        """Get the model's temperature."""
        return self._model_temperature

    @model_temperature.setter
    def model_temperature(self, value: float):
        """Set the model's temperature.

        Args:
            value (float): The new temperature value.
        """
        self._model_temperature = value

    @property
    def model_top_k(self) -> int:
        """Get the model's top-k value."""
        return self._model_top_k

    @model_top_k.setter
    def model_top_k(self, value: int):
        """Set the model's top-k value.

        Args:
            value (int): The new top-k value.
        """
        self._model_top_k = value

    @property
    def model_top_p(self) -> float:
        """Get the model's top-p value."""
        return self._model_top_p

    @model_top_p.setter
    def model_top_p(self, value: float):
        """Set the model's top-p value.

        Args:
            value (float): The new top-p value.
        """
        self._model_top_p = value

    @property
    def model_repeat_penalty(self) -> float:
        """Get the model's repeat penalty value."""
        return self._model_repeat_penalty

    @model_repeat_penalty.setter
    def model_repeat_penalty(self, value: float):
        """Set the model's repeat penalty value.

        Args:
            value (float): The new repeat penalty value.
        """
        self._model_repeat_penalty = value

    @property
    def model_repeat_last_n(self) -> int:
        """Get the number of words to consider for repeat penalty."""
        return self._model_repeat_last_n

    @model_repeat_last_n.setter
    def model_repeat_last_n(self, value: int):
        """Set the number of words to consider for repeat penalty.

        Args:
            value (int): The new number of words value.
        """
        self._model_repeat_last_n = value


    @property
    def assets_list(self) -> list:
        """Get the number of words to consider for repeat penalty."""
        return self._assets_list

    @assets_list.setter
    def assets_list(self, value: list):
        """Set the number of words to consider for repeat penalty.

        Args:
            value (int): The new number of words value.
        """
        self._assets_list = value

    @property
    def processor(self) -> 'APScript':
        """Get the number of words to consider for repeat penalty."""
        return self._processor

    @processor.setter
    def processor(self, value: 'APScript'):
        """Set the number of words to consider for repeat penalty.

        Args:
            value (int): The new number of words value.
        """
        self._processor = value


    @property
    def processor_cfg(self) -> list:
        """Get the number of words to consider for repeat penalty."""
        return self._processor_cfg

    @processor_cfg.setter
    def processor_cfg(self, value: dict):
        """Set the number of words to consider for repeat penalty.

        Args:
            value (int): The new number of words value.
        """
        self._processor_cfg = value






    # Properties ===============================================
    @property
    def start_header_id_template(self) -> str:
        """Get the start_header_id_template."""
        return self.config.start_header_id_template

    @property
    def end_header_id_template(self) -> str:
        """Get the end_header_id_template."""
        return self.config.end_header_id_template
    
    @property
    def system_message_template(self) -> str:
        """Get the system_message_template."""
        return self.config.system_message_template


    @property
    def separator_template(self) -> str:
        """Get the separator template."""
        return self.config.separator_template


    @property
    def start_user_header_id_template(self) -> str:
        """Get the start_user_header_id_template."""
        return self.config.start_user_header_id_template
    @property
    def end_user_header_id_template(self) -> str:
        """Get the end_user_header_id_template."""
        return self.config.end_user_header_id_template
    @property
    def end_user_message_id_template(self) -> str:
        """Get the end_user_message_id_template."""
        return self.config.end_user_message_id_template




    @property
    def start_ai_header_id_template(self) -> str:
        """Get the start_ai_header_id_template."""
        return self.config.start_ai_header_id_template
    @property
    def end_ai_header_id_template(self) -> str:
        """Get the end_ai_header_id_template."""
        return self.config.end_ai_header_id_template
    @property
    def end_ai_message_id_template(self) -> str:
        """Get the end_ai_message_id_template."""
        return self.config.end_ai_message_id_template
    @property
    def system_full_header(self) -> str:
        """Get the start_header_id_template."""
        return f"{self.start_header_id_template}{self.system_message_template}{self.end_header_id_template}"
    @property
    def user_full_header(self) -> str:
        """Get the start_header_id_template."""
        return f"{self.start_user_header_id_template}{self.config.user_name}{self.end_user_header_id_template}"
    @property
    def ai_full_header(self) -> str:
        """Get the start_header_id_template."""
        return f"{self.start_ai_header_id_template}{self.name}{self.end_ai_header_id_template}"

    def system_custom_header(self, ai_name) -> str:
        """Get the start_header_id_template."""
        return f"{self.start_user_header_id_template}{ai_name}{self.end_user_header_id_template}"

    def user_custom_header(self, ai_name) -> str:
        """Get the start_header_id_template."""
        return f"{self.start_user_header_id_template}{ai_name}{self.end_user_header_id_template}"

    def ai_custom_header(self, ai_name) -> str:
        """Get the start_header_id_template."""
        return f"{self.start_ai_header_id_template}{ai_name}{self.end_ai_header_id_template}"


    # ========================================== Helper methods ==========================================
    def detect_antiprompt(self, text:str) -> bool:
        """
        Detects if any of the antiprompts in self.anti_prompts are present in the given text.
        Used for the Hallucination suppression system

        Args:
            text (str): The text to check for antiprompts.

        Returns:
            bool: True if any antiprompt is found in the text (ignoring case), False otherwise.
        """
        start_header_id_template        = self.config.start_header_id_template
        start_user_header_id_template   = self.config.start_user_header_id_template
        start_ai_header_id_template     = self.config.start_ai_header_id_template

        anti_prompts = [start_header_id_template, start_user_header_id_template, start_ai_header_id_template]
        if self.app.config.separator_template!="\n":
            anti_prompts.append(self.app.config.separator_template)

        for prompt in anti_prompts:
            if prompt.lower() in text.lower():
                return prompt.lower()
        return None

    def verify_rag_entry(self, query, rag_entry):
        return self.yes_no("Are there any useful information in the document chunk that can be used to answer the query?", self.app.system_custom_header("Query")+query+"\n"+self.app.system_custom_header("document chunk")+"\n"+rag_entry)


    def translate(self, text_chunk, output_language="french", max_generation_size=3000):
        start_header_id_template    = self.config.start_header_id_template
        end_header_id_template      = self.config.end_header_id_template
        system_message_template     = self.config.system_message_template

        translated = self.fast_gen(
                                "\n".join([
                                    f"{start_header_id_template}{system_message_template}{end_header_id_template}",
                                    f"Translate the following text to {output_language}.",
                                    "Be faithful to the original text and do not add or remove any information.",
                                    "Respond only with the translated text.",
                                    "Do not add comments or explanations.",
                                    f"{start_header_id_template}text to translate{end_header_id_template}",
                                    f"{text_chunk}",
                                    f"{start_header_id_template}translation{end_header_id_template}",
                                    ]),
                                    max_generation_size=max_generation_size, callback=self.sink)
        return translated
    
    def sequential_summarize(
                            self, 
                            text:str,
                            chunk_processing_prompt:str="Extract relevant information from the current text chunk and update the memory if needed.",
                            chunk_processing_output_format="markdown",
                            final_memory_processing_prompt="Create final summary using this memory.",
                            final_output_format="markdown",
                            ctx_size:int=None,
                            chunk_size:int=None,
                            bootstrap_chunk_size:int=None,
                            bootstrap_steps:int=None,
                            callback = None,
                            step_callback: Callable[[str, int, int, str], None] = None,
                            debug:bool= False):
        """
            This function processes a given text in chunks and generates a summary for each chunk.
            It then combines the summaries to create a final summary.

            Parameters:
            text (str): The input text to be summarized.
            chunk_processing_prompt (str, optional): The prompt used for processing each chunk. Defaults to "".
            chunk_processing_output_format (str, optional): The format of the output for each chunk. Defaults to "markdown".
            final_memory_processing_prompt (str, optional): The prompt used for processing the final memory. Defaults to "Create final summary using this memory.".
            final_output_format (str, optional): The format of the final output. Defaults to "markdown".
            ctx_size (int, optional): The size of the context. Defaults to None.
            chunk_size (int, optional): The size of each chunk. Defaults to None.
            callback (callable, optional): A function to be called after processing each chunk. Defaults to None.
            debug (bool, optional): A flag to enable debug mode. Defaults to False.

            Returns:
            The final summary in the specified format.
        """
        if ctx_size is None:
            ctx_size = self.app.config.ctx_size

        if chunk_size is None:
            chunk_size = ctx_size // 4

        # Tokenize entire text
        all_tokens = self.model.tokenize(text)
        total_tokens = len(all_tokens)

        # Initialize memory and chunk index
        memory = ""
        start_token_idx = 0

        # Create static prompt template
        example_prompt = f"""
{self.system_full_header}
You are a structured sequential text summary assistant that processes documents chunk by chunk, updating a memory of previously generated information at each step.

Your goal is to extract and combine relevant information from each text chunk with the existing memory, ensuring no key details are omitted or invented.

If requested, infer metadata like titles or authors from the content.

{self.user_full_header}
Update the memory by merging previous information with new details from this text chunk.
Only add information explicitly present in the chunk. Retain all relevant prior memory unless clarified or updated by the current chunk.

----
# Text chunk:
# Chunk number: 0
----
```markdown
```

{chunk_processing_prompt}

Before updating, verify each requested detail:
1. Does the chunk explicitly mention the information?
2. Should prior memory be retained, updated, or clarified?

Include only confirmed details in the output.
Rewrite the full memory including the updates and keeping relevant data.
Do not discuss the information inside the memory, just put the relevant information without comments.

----
# Current document analysis memory:
----
```{chunk_processing_output_format}
```
{self.ai_full_header}
        """ 

        # Calculate static prompt tokens (with empty memory and chunk)
        chunk_id = 0
        static_tokens = self.model.count_tokens(example_prompt)

        # Process text in chunks
        while start_token_idx < total_tokens:
            # Calculate available tokens for chunk
            current_memory_tokens = self.model.count_tokens(memory)
            available_tokens = ctx_size - static_tokens - current_memory_tokens

            if available_tokens <= 0:
                raise ValueError("Memory too large - consider reducing chunk size or increasing context window")

            # Get chunk tokens
            if bootstrap_chunk_size is not None and chunk_id < bootstrap_steps:
                end_token_idx = min(start_token_idx + bootstrap_chunk_size, total_tokens)
            else:                
                end_token_idx = min(start_token_idx + chunk_size, total_tokens)
            chunk_tokens = all_tokens[start_token_idx:end_token_idx]
            chunk = self.model.detokenize(chunk_tokens)
            chunk_id += 1

            # Generate memory update
            prompt =  f"""{self.system_full_header}
You are a structured sequential text summary assistant that processes documents chunk by chunk, updating a memory of previously generated information at each step.

Your goal is to extract and combine relevant information from each text chunk with the existing memory, ensuring no key details are omitted or invented.

If requested, infer metadata like titles or authors from the content.

{self.user_full_header}
Update the memory by merging previous information with new details from this text chunk.
Only add information explicitly present in the chunk. Retain all relevant prior memory unless clarified or updated by the current chunk.

----
# Text chunk:
# Chunk number: {chunk_id}
----
```markdown
{chunk}
```

{chunk_processing_prompt}

Before updating, verify each requested detail:
1. Does the chunk explicitly mention the information?
2. Should prior memory be retained, updated, or clarified?

Include only confirmed details in the output.
Rewrite the full memory including the updates and keeping relevant data.
Do not discuss the information inside the memory, just put the relevant information without comments.

----
# Current document analysis memory:
----
```{chunk_processing_output_format}
{memory}
```
{self.ai_full_header}
        """             
            if debug:
                ASCIIColors.yellow(f" ----- {chunk_id-1} ------")
                ASCIIColors.red(prompt)
            if step_callback:
                step_callback("Memory creation", chunk_id, (total_tokens//chunk_size)+1, "")
            memory = self.generate(prompt, max_size=ctx_size//4, callback=callback).strip()
            code = self.extract_code_blocks(memory)
            if code:
                memory = code[0]["content"]

            if debug:
                ASCIIColors.yellow(f" ----- OUT ------")
                ASCIIColors.yellow(memory)
                ASCIIColors.yellow(" ----- ------")
            # Move to next chunk
            start_token_idx = end_token_idx

        # Prepare final summary prompt
        final_prompt_template = f"""
{self.system_full_header}
You are a memory summarizer assistant that helps users format their memory information into coherent text in a specific style or format.
{final_memory_processing_prompt}.
{self.user_full_header}
Here is my document analysis memory:
```{chunk_processing_output_format}
{memory}
```
The output must be put inside a {final_output_format} markdown tag.
The updated memory must be put in a {chunk_processing_output_format} markdown tag.
{self.ai_full_header}
        """

        # Truncate memory if needed for final prompt
        example_final_prompt = final_prompt_template
        final_static_tokens = self.model.count_tokens(example_final_prompt)
        available_final_tokens = ctx_size - final_static_tokens

        memory_tokens = self.model.tokenize(memory)
        if len(memory_tokens) > available_final_tokens:
            memory = self.model.detokenize(memory_tokens[:available_final_tokens])

        if step_callback:
            step_callback("Final output generation", 1, 1, "")
        # Generate final summary
        final_prompt = final_prompt_template
        memory = self.generate(final_prompt, callback=callback)
        code = self.extract_code_blocks(memory)
        if code:
            memory = code[0]["content"]
        return memory

    
    def summarize_text(
                        self,
                        text,
                        summary_instruction="summarize",
                        doc_name="chunk",
                        answer_start="",
                        max_generation_size=3000,
                        max_summary_size=512,
                        callback=None,
                        chunk_summary_post_processing=None,
                        summary_mode=SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL
                    ):
        tk = self.model.tokenize(text)
        prev_len = len(tk)
        document_chunks=None
        while len(tk)>max_summary_size and (document_chunks is None or len(document_chunks)>1):
            self.step_start(f"Comprerssing {doc_name}...")
            chunk_size = int(self.config.ctx_size*0.6)
            document_chunks =TextChunker.chunk_text(text, self.model, chunk_size, 0, True)
            text = self.summarize_chunks(
                                            document_chunks,
                                            summary_instruction, 
                                            doc_name, 
                                            answer_start, 
                                            max_generation_size, 
                                            callback, 
                                            chunk_summary_post_processing=chunk_summary_post_processing,
                                            summary_mode=summary_mode)
            tk = self.model.tokenize(text)
            dtk_ln=prev_len-len(tk)
            prev_len = len(tk)
            self.step(f"Current text size : {prev_len}, max summary size : {max_summary_size}")
            self.step_end(f"Comprerssing {doc_name}...")
            if dtk_ln<=10: # it is not summarizing
                break
        return text

    def smart_data_extraction(
                                self,
                                text,
                                data_extraction_instruction=f"summarize the current chunk.",
                                final_task_instruction="reformulate with better wording",
                                doc_name="chunk",
                                answer_start="",
                                max_generation_size=3000,
                                max_summary_size=512,
                                callback=None,
                                chunk_summary_post_processing=None,
                                summary_mode=SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL
                            ):
        tk = self.model.tokenize(text)
        prev_len = len(tk)
        while len(tk)>max_summary_size:
            chunk_size = int(self.config.ctx_size*0.6)
            document_chunks = TextChunker.chunk_text(text, self.model, chunk_size, 0, True)
            text = self.summarize_chunks(
                                            document_chunks, 
                                            data_extraction_instruction, 
                                            doc_name, 
                                            answer_start, 
                                            max_generation_size, 
                                            callback, 
                                            chunk_summary_post_processing=chunk_summary_post_processing, 
                                            summary_mode=summary_mode
                                        )
            tk = self.model.tokenize(text)
            dtk_ln=prev_len-len(tk)
            prev_len = len(tk)
            self.step(f"Current text size : {prev_len}, max summary size : {max_summary_size}")
            if dtk_ln<=10: # it is not sumlmarizing
                break
        self.step_start(f"Rewriting ...")
        text = self.summarize_chunks(
                                        [text],
                                        final_task_instruction, 
                                        doc_name, answer_start, 
                                        max_generation_size, 
                                        callback, 
                                        chunk_summary_post_processing=chunk_summary_post_processing
                                    )
        self.step_end(f"Rewriting ...")

        return text

    def summarize_chunks(
                            self,
                            chunks,
                            summary_instruction=f"summarize the current chunk.",
                            doc_name="chunk",
                            answer_start="",
                            max_generation_size=3000,
                            callback=None,
                            chunk_summary_post_processing=None,
                            summary_mode=SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL
                        ):
        start_header_id_template    = self.config.start_header_id_template
        end_header_id_template      = self.config.end_header_id_template
        system_message_template     = self.config.system_message_template

        if summary_mode==SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL:
            summary = ""
            for i, chunk in enumerate(chunks):
                self.step_start(f" Summary of {doc_name} - Processing chunk : {i+1}/{len(chunks)}")
                summary = f"{answer_start}"+ self.fast_gen(
                            "\n".join([
                                self.system_custom_header("previous chunks analysis"),
                                f"{summary}",
                                self.system_custom_header("current chunk"),
                                f"{chunk}",
                                self.system_full_header,
                                summary_instruction,
                                f"Keep only information relevant to the context",
                                f"the output must keep information from the previous chunk analysis and add the current chunk extracted information.",
                                f"Be precise and do not invent information that does not exist in the previous chunks analysis or the current chunk.",
                                f"Do not add any extra comments.",
                                self.system_custom_header("cumulative chunks analysis")+answer_start
                                ]),
                                max_generation_size=max_generation_size,
                                callback=callback)
                if chunk_summary_post_processing:
                    summary = chunk_summary_post_processing(summary)
                self.step_end(f" Summary of {doc_name} - Processing chunk : {i+1}/{len(chunks)}")
            return summary
        else:
            summeries = []
            for i, chunk in enumerate(chunks):
                self.step_start(f" Summary of {doc_name} - Processing chunk : {i+1}/{len(chunks)}")
                summary = f"{answer_start}"+ self.fast_gen(
                            "\n".join([
                                f"{start_header_id_template}Document_chunk [{doc_name}]{end_header_id_template}",
                                f"{chunk}",
                                f"{start_header_id_template}{system_message_template}{end_header_id_template}{summary_instruction}",
                                f"Answer directly with the summary with no extra comments.",
                                f"{start_header_id_template}summary{end_header_id_template}",
                                f"{answer_start}"
                                ]),
                                max_generation_size=max_generation_size,
                                callback=callback)
                if chunk_summary_post_processing:
                    summary = chunk_summary_post_processing(summary)
                summeries.append(summary)
                self.step_end(f" Summary of {doc_name} - Processing chunk : {i+1}/{len(chunks)}")
            return "\n".join(summeries)

    def sequencial_chunks_summary(
                            self,
                            chunks,
                            summary_instruction="summarize",
                            doc_name="chunk",
                            answer_start="",
                            max_generation_size=3000,
                            callback=None,
                            chunk_summary_post_processing=None
                        ):
        start_header_id_template    = self.config.start_header_id_template
        end_header_id_template      = self.config.end_header_id_template
        system_message_template     = self.config.system_message_template
        summeries = []
        for i, chunk in enumerate(chunks):
            if i<len(chunks)-1:
                chunk1 = chunks[i+1]
            else:
                chunk1=""
            if i>0:
                chunk=summary
            self.step_start(f" Summary of {doc_name} - Processing chunk : {i+1}/{len(chunks)}")
            summary = f"{answer_start}"+ self.fast_gen(
                        "\n".join([
                            f"{start_header_id_template}Document_chunk: {doc_name}{end_header_id_template}",
                            f"Block1:",
                            f"{chunk}",
                            f"Block2:",
                            f"{chunk1}",
                            f"{start_header_id_template}{system_message_template}{end_header_id_template}{summary_instruction}",
                            f"Answer directly with the summary with no extra comments.",
                            f"{start_header_id_template}summary{end_header_id_template}",
                            f"{answer_start}"
                            ]),
                            max_generation_size=max_generation_size,
                            callback=callback)
            if chunk_summary_post_processing:
                summary = chunk_summary_post_processing(summary)
            summeries.append(summary)
            self.step_end(f" Summary of {doc_name} - Processing chunk : {i+1}/{len(chunks)}")
        return "\n".join(summeries)
    
# ===========================================================
    # Basic message element (already provided)
    def build_message_element(self, element_text):
        return f"""
<div class="max-w-md mx-auto my-2">
    <div class="bg-red-500 text-white rounded-lg py-2 px-4 inline-block shadow-md">
        {element_text}
    </div>
</div>
"""

    # Message with thinking animation (already updated)
    def build_message_element_with_thinking_animation(self, element_text):
        return f"""
<div class="max-w-md mx-auto my-2">
    <div class="bg-red-500 text-white rounded-lg py-2 px-4 inline-block shadow-md flex items-center space-x-2">
        <span>{element_text}</span>
        <div class="flex space-x-1">
            <div class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 0s;"></div>
            <div class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 0.2s;"></div>
            <div class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 0.4s;"></div>
        </div>
    </div>
</div>
"""

    # Message with emoji (e.g., smiley for completion)
    def build_message_element_with_emoji(self, element_text, emoji="😊"):
        return f"""
<div class="max-w-md mx-auto my-2">
    <div class="bg-red-500 text-white rounded-lg py-2 px-4 inline-block shadow-md flex items-center space-x-2">
        <span>{element_text}</span>
        <span class="text-xl">{emoji}</span>
    </div>
</div>
"""

    # Success message with checkmark
    def build_success_message(self, element_text):
        return f"""
<div class="max-w-md mx-auto my-2">
    <div class="bg-green-500 text-white rounded-lg py-2 px-4 inline-block shadow-md flex items-center space-x-2">
        <span class="text-xl">✓</span>
        <span>{element_text}</span>
    </div>
</div>
"""

    # Warning message with alert icon
    def build_warning_message(self, element_text):
        return f"""
<div class="max-w-md mx-auto my-2">
    <div class="bg-yellow-500 text-white rounded-lg py-2 px-4 inline-block shadow-md flex items-center space-x-2">
        <span class="text-xl">⚠️</span>
        <span>{element_text}</span>
    </div>
</div>
"""

    # Error message with cross
    def build_error_message(self, element_text):
        return f"""
<div class="max-w-md mx-auto my-2">
    <div class="bg-red-600 text-white rounded-lg py-2 px-4 inline-block shadow-md flex items-center space-x-2">
        <span class="text-xl">✗</span>
        <span>{element_text}</span>
    </div>
</div>
"""

    # Progress message with spinning animation
    def build_progress_message(self, element_text):
        return f"""
<div class="max-w-md mx-auto my-2">
    <div class="bg-blue-500 text-white rounded-lg py-2 px-4 inline-block shadow-md flex items-center space-x-2">
        <span>{element_text}</span>
        <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
    </div>
</div>
"""

    # Info message with light bulb
    def build_info_message(self, element_text):
        return f"""
<div class="max-w-md mx-auto my-2">
    <div class="bg-blue-400 text-white rounded-lg py-2 px-4 inline-block shadow-md flex items-center space-x-2">
        <span class="text-xl">💡</span>
        <span>{element_text}</span>
    </div>
</div>
"""
    
    def build_progressbar_message(self, element_text, progress_percentage=50):
        return f"""
<div class="max-w-md mx-auto my-2">
    <div class="bg-blue-500 text-white rounded-lg py-2 px-4 shadow-md">
        <div class="flex items-center space-x-2 mb-2">
            <span>{element_text}</span>
        </div>
        <div class="w-full bg-blue-300 rounded-full h-2.5">
            <div class="bg-white h-2.5 rounded-full transition-all duration-500 ease-in-out" 
                 style="width: {progress_percentage}%"></div>
        </div>
    </div>
</div>
"""

    
class StateMachine:
    def __init__(self, states_list):
        """
        states structure is the following
        [
            {
                "name": the state name,
                "commands": [ # list of commands
                    "command": function
                ],
                "default": default function
            }
        ]
        """
        self.states_list = states_list
        self.current_state_id = 0
        self.callback = None

    def goto_state(self, state:int|str):
        """
        Transition to the state with the given name or index.

        Args:
            state (str or int): The name or index of the state to transition to.

        Raises:
            ValueError: If no state is found with the given name or index.
        """
        if isinstance(state, str):
            for i, state_dict in enumerate(self.states_list):
                if state_dict["name"] == state:
                    self.current_state_id = i
                    return
        elif isinstance(state, int):
            if 0 <= state < len(self.states_list):
                self.current_state_id = state
                return
        raise ValueError(f"No state found with name or index: {state}")



    def process_state(self, command, full_context, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None, context_state:dict=None, client:Client=None):
        """
        Process the given command based on the current state.

        Args:
            command: The command to process.

        Raises:
            ValueError: If the current state doesn't have the command and no default function is defined.
        """
        if callback:
            self.callback=callback

        current_state = self.states_list[self.current_state_id]
        commands = current_state["commands"]
        command = command.strip()

        for cmd, func in commands.items():
            if cmd == command[0:len(cmd)]:
                # Get the number of parameters the function expects
                param_count = len(inspect.signature(func).parameters)

                if param_count == 3:
                    # Old version of the function
                    return func(command, full_context, client)
                elif param_count >= 5:
                    # New version of the function
                    return func(command, full_context, callback, context_state, client)
                else:
                    raise ValueError(f"Unexpected number of parameters for function {func.__name__}. Expected 3 or 5, got {param_count}")


        default_func = current_state.get("default")
        if default_func is not None:
            default_func(command, full_context, callback, context_state, client)
        else:
            raise ValueError(f"Command '{command}' not found in current state and no default function defined.")


class LoLLMsActionParameters:
    def __init__(self, name: str, parameter_type: Type, range: Optional[List] = None, options: Optional[List] = None, value: Any = None) -> None:
        self.name = name
        self.parameter_type = parameter_type
        self.range = range
        self.options = options
        self.value = value

    def __str__(self) -> str:
        parameter_dict = {
            'name': self.name,
            'parameter_type': self.parameter_type.__name__,
            'value': self.value
        }
        if self.range is not None:
            parameter_dict['range'] = self.range
        if self.options is not None:
            parameter_dict['options'] = self.options
        return json.dumps(parameter_dict, indent=4)

    @staticmethod
    def from_str(string: str) -> 'LoLLMsActionParameters':
        parameter_dict = json.loads(string)
        name = parameter_dict['name']
        parameter_type = eval(parameter_dict['parameter_type'])
        range = parameter_dict.get('range', None)
        options = parameter_dict.get('options', None)
        value = parameter_dict['value']
        return LoLLMsActionParameters(name, parameter_type, range, options, value)

    @staticmethod
    def from_dict(parameter_dict: dict) -> 'LoLLMsActionParameters':
        name = parameter_dict['name']
        parameter_type = eval(parameter_dict['parameter_type'])
        range = parameter_dict.get('range', None)
        options = parameter_dict.get('options', None)
        value = parameter_dict['value']
        return LoLLMsActionParameters(name, parameter_type, range, options, value)


class LoLLMsActionParametersEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, LoLLMsActionParameters):
            parameter_dict = {
                'name': obj.name,
                'parameter_type': obj.parameter_type.__name__,
                'value': obj.value
            }
            if obj.range is not None:
                parameter_dict['range'] = obj.range
            if obj.options is not None:
                parameter_dict['options'] = obj.options
            return parameter_dict
        return super().default(obj)

class LoLLMsAction:
    def __init__(self, name, parameters: List[LoLLMsActionParameters], callback: Callable, description:str="") -> None:
        self.name           = name
        self.parameters     = parameters
        self.callback       = callback
        self.description    = description

    def __str__(self) -> str:
        action_dict = {
            'name': self.name,
            'parameters': self.parameters,
            'description': self.description
        }
        return json.dumps(action_dict, indent=4, cls=LoLLMsActionParametersEncoder)

    @staticmethod
    def from_str(string: str) -> 'LoLLMsAction':
        action_dict = json.loads(string)
        name = action_dict['name']
        parameters = [LoLLMsActionParameters.from_dict(param_str) for param_str in action_dict['parameters']]
        return LoLLMsAction(name, parameters, None)

    @staticmethod
    def from_dict(action_dict: dict) -> 'LoLLMsAction':
        name = action_dict['name']
        parameters = [LoLLMsActionParameters.from_dict(param_str) for param_str in action_dict['parameters']]
        return LoLLMsAction(name, parameters, None)


    def run(self) -> None:
        args = {param.name: param.value for param in self.parameters}
        self.callback(**args)

def generate_actions(potential_actions: List[LoLLMsAction], parsed_text: dict) -> List[LoLLMsAction]:
    actions = []
    try:
        for action_data in parsed_text["actions"]:
            name = action_data['name']
            parameters = action_data['parameters']
            matching_action = next((action for action in potential_actions if action.name == name), None)
            if matching_action:
                action = LoLLMsAction.from_str(str(matching_action))
                action.callback = matching_action.callback
                if type(parameters)==dict:
                    for param_name, param_value in parameters.items():
                        matching_param = next((param for param in action.parameters if param.name == param_name), None)
                        if matching_param:
                            matching_param.value = param_value
                else:
                    for param in parameters:
                        if "name" in param:
                            param_name = param["name"]
                            param_value = param["value"]
                        else:
                            param_name = list(param.keys())[0]
                            param_value = param[param_name]
                        matching_param = next((param for param in action.parameters if param.name == param_name), None)
                        if matching_param:
                            matching_param.value = param_value
                actions.append(action)
    except json.JSONDecodeError:
        print("Invalid JSON format.")
    return actions

class APScript(StateMachine):
    """
    Template class for implementing personality processor classes in the APScript framework.

    This class provides a basic structure and placeholder methods for processing model inputs and outputs.
    Personality-specific processor classes should inherit from this class and override the necessary methods.
    """
    def __init__(
                    self,
                    personality         :AIPersonality,
                    personality_config  :TypedConfig,
                    states_list         :dict   = {},
                    callback            = None
                ) -> None:
        super().__init__(states_list)
        self.function_definitions               = [] # New! useful for 3rd gen personalities 
        self.notify                             = personality.app.notify

        self.personality                        = personality
        self.config                             = personality.config
        self.personality_config                 = personality_config
        self.installation_option                = personality.installation_option
        self.configuration_file_path            = self.personality.lollms_paths.personal_configuration_path/"personalities"/self.personality.personality_folder_name/f"config.yaml"
        self.configuration_file_path.parent.mkdir(parents=True, exist_ok=True)

        self.personality_config.config.file_path    = self.configuration_file_path

        self.callback = callback

        # Installation
        if (not self.configuration_file_path.exists() or self.installation_option==InstallOption.FORCE_INSTALL) and self.installation_option!=InstallOption.NEVER_INSTALL:
            self.install()
            self.personality_config.config.save_config()
        else:
            self.load_personality_config()

    def sink(self, s=None,i=None,d=None):
        pass

    def settings_updated(self):
        """
        To be implemented by the processor when the settings have changed
        """
        pass

    def mounted(self):
        """
        triggered when mounted
        """
        pass

    def get_welcome(self, welcome_message:str, client:Client):
        """
        triggered when a new conversation is created
        """
        return welcome_message
        
    def selected(self):
        """
        triggered when mounted
        """
        pass

    def generate_html_from_dict(self, data):
        css_style = """
        <style>
            .container {
                font-family: 'Arial', sans-serif;
                max-width: 1000px;
                margin: 20px auto;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .header {
                background-color: #343a40;
                color: white;
                padding: 20px;
                border-radius: 6px;
                margin-bottom: 20px;
            }
            .section {
                margin-bottom: 20px;
                padding: 15px;
                background-color: white;
                border-radius: 6px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }
            .key {
                font-weight: bold;
                color: #495057;
                margin-bottom: 5px;
            }
            .value {
                color: #212529;
                white-space: pre-wrap;
                line-height: 1.6;
            }
            .list {
                margin: 0;
                padding-left: 20px;
            }
        </style>
        """

        def format_value(value):
            if isinstance(value, list):
                if not value:
                    return "<em>Empty list</em>"
                items = [f"<li>{item}</li>" for item in value]
                return f"<ul class='list'>{''.join(items)}</ul>"
            elif isinstance(value, (str, int, float)):
                # Replace pipe character and preserve formatting for multiline strings
                if isinstance(value, str) and '|' in value:
                    value = value.replace('|', '').strip()
                return f"<div class='value'>{value}</div>"
            else:
                return f"<div class='value'>{str(value)}</div>"

        html = css_style
        html += "<div class='container'>"
        
        # Add header with name if it exists
        if "name" in data:
            html += f"<div class='header'><h1>{data['name']}</h1></div>"

        # Process all key-value pairs
        for key, value in data.items():
            if key != "name":  # Skip name as it's already in header
                html += "<div class='section'>"
                html += f"<div class='key'>{key.replace('_', ' ').title()}:</div>"
                html += format_value(value)
                html += "</div>"

        html += "</div>"
        return html



    def execute_command(self, command: str, parameters:list=[], client:Client=None):
        """
        Recovers user commands and executes them. Each personality can define a set of commands that they can receive and execute
        Args:
            command: The command name
            parameters: A list of the command parameters

        """
        try:
            self.process_state(command, "", self.callback, context_state=None, client= client)
        except Exception as ex:
            trace_exception(ex)
            self.warning(f"Couldn't execute command {command}")

    async def handle_request(self, data: dict, client:Client=None) -> Dict[str, Any]:
        """
        Handle client requests.

        Args:
            data (dict): A dictionary containing the request data.
            client (Client): A refertence to the client asking for this request.

        Returns:
            dict: A dictionary containing the response, including at least a "status" key.

        This method should be implemented by a class that inherits from this one.

        Example usage:
        ```
        handler = YourHandlerClass()
        client = checkaccess(lollmsServer, client_id)
        request_data = {"command": "some_command", "parameters": {...}}
        response = handler.handle_request(request_data, client)
        ```
        """        
        return {"status":True}



    def load_personality_config(self):
        """
        Load the content of local_config.yaml file.

        The function reads the content of the local_config.yaml file and returns it as a Python dictionary.

        Args:
            None

        Returns:
            dict: A dictionary containing the loaded data from the local_config.yaml file.
        """
        try:
            self.personality_config.config.load_config()
        except:
            self.personality_config.config.save_config()
        self.personality_config.sync()

    def install(self):
        """
        Installation procedure (to be implemented)
        """
        ASCIIColors.blue("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
        ASCIIColors.red(f"Installing {self.personality.personality_folder_name}")
        ASCIIColors.blue("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")


    def uninstall(self):
        """
        Installation procedure (to be implemented)
        """
        ASCIIColors.blue("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
        ASCIIColors.red(f"Uninstalling {self.personality.personality_folder_name}")
        ASCIIColors.blue("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")


    def add_file(self, path, client:Client, callback=None, process=True):
        self.personality.add_file(path, client=client,callback=callback, process=process)
        if callback is not None:
            callback("File added successfully",MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_INFO)
        return True

    def remove_file(self, path):
        if path in self.personality.text_files:
            self.personality.text_files.remove(path)
        elif path in self.personality.image_files:
            self.personality.image_files.remove(path)


    def load_config_file(self, path, default_config=None):
        """
        Load the content of local_config.yaml file.

        The function reads the content of the local_config.yaml file and returns it as a Python dictionary.
        If a default_config is provided, it fills any missing entries in the loaded dictionary.
        If at least one field from default configuration was not present in the loaded configuration, the updated
        configuration is saved.

        Args:
            path (str): The path to the local_config.yaml file.
            default_config (dict, optional): A dictionary with default values to fill missing entries.

        Returns:
            dict: A dictionary containing the loaded data from the local_config.yaml file, with missing entries filled
            by default_config if provided.
        """
        with open(path, 'r') as file:
            data = yaml.safe_load(file)

        if default_config:
            updated = False
            for key, value in default_config.items():
                if key not in data:
                    data[key] = value
                    updated = True

            if updated:
                self.save_config_file(path, data)

        return data

    def save_config_file(self, path, data):
        """
        Save the configuration data to a local_config.yaml file.

        Args:
            path (str): The path to save the local_config.yaml file.
            data (dict): The configuration data to be saved.

        Returns:
            None
        """
        with open(path, 'w') as file:
            yaml.dump(data, file)

    def generate_with_images(self, prompt, images, max_size = None, temperature = None, top_k = None, top_p=None, repeat_penalty=None, repeat_last_n=None, callback=None, debug=False ):
        return self.personality.generate_with_images(prompt, images, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug)

    def generate(self, prompt, max_size = None, temperature = None, top_k = None, top_p=None, repeat_penalty=None, repeat_last_n=None, callback=None, debug=False ):
        return self.personality.generate(prompt, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug)


    def generate_codes(self, prompt, max_size = None, temperature = None, top_k = None, top_p=None, repeat_penalty=None, repeat_last_n=None, callback=None, debug=False ):
        if len(self.personality.image_files)>0:
            response = self.personality.generate_with_images(self.system_custom_header("Generation infos")+ "Generated code must be put inside the adequate markdown code tag. Use this template:\n```language name\nCode\n```\n" + self.separator_template + prompt, self.personality.image_files, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug)
        else:
            response = self.personality.generate(self.system_custom_header("Generation infos")+ "Generated code must be put inside the adequate markdown code tag. Use this template:\n```language name\nCode\n```\n" + self.separator_template + prompt, max_size, temperature, top_k, top_p, repeat_penalty, repeat_last_n, callback, debug=debug)
        codes = self.extract_code_blocks(response)
        return codes
    


    def generate_code(
                        self, 
                        prompt, 
                        images=[],
                        template=None,
                        language="json",
                        code_tag_format="markdown", # or "html"
                        max_size = None,  
                        temperature = None, 
                        top_k = None, 
                        top_p=None, 
                        repeat_penalty=None, 
                        repeat_last_n=None, 
                        callback=None, 
                        debug=None, 
                        return_full_generated_code=False, 
                        accept_all_if_no_code_tags_is_present=False, 
                        max_continues=5
                    ):
        return self.personality.generate_code(prompt, 
                        images,
                        template,
                        language,
                        code_tag_format, # or "html"
                        max_size,  
                        temperature, 
                        top_k, 
                        top_p, 
                        repeat_penalty, 
                        repeat_last_n, 
                        callback, 
                        debug, 
                        return_full_generated_code, 
                        accept_all_if_no_code_tags_is_present, 
                        max_continues
                    )

    def generate_text(
                        self, 
                        prompt, 
                        images=[],
                        template=None,
                        code_tag_format="markdown", # or "html"
                        max_size = None,  
                        temperature = None, 
                        top_k = None, 
                        top_p=None, 
                        repeat_penalty=None, 
                        repeat_last_n=None, 
                        callback=None, 
                        debug=False, 
                        return_full_generated_code=False, 
                        accept_all_if_no_code_tags_is_present=False, 
                        max_continues=5
                    ):
        return self.personality.generate_text(prompt, 
                        images,
                        template,
                        code_tag_format, # or "html"
                        max_size,  
                        temperature, 
                        top_k, 
                        top_p, 
                        repeat_penalty, 
                        repeat_last_n, 
                        callback, 
                        debug, 
                        return_full_generated_code, 
                        accept_all_if_no_code_tags_is_present, 
                        max_continues
                    )     

    def generate_structured_content(self, 
                                prompt,
                                images=[],
                                template=None, 
                                output_format="yaml",
                                callback=None):
        """
        Generate structured content (YAML/JSON) either in single-shot or step-by-step mode.
        
        Args:
            prompt (str): The main prompt describing what to generate
            template (dict): Dictionary containing the structure and field-specific prompts
            single_shot (bool): If True, generates all content at once. If False, generates field by field
            output_format (str): "yaml" or "json"
        
        Returns:
            dict: Contains both the structured data and formatted string
        """
        return self.personality.generate_structured_content(prompt, images, template, output_format, callback)

            
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
                - think_first_mode (str(): The think first mode condition
                - ai_prefix (str): The AI prefix information.
            client_id: The client ID for code generation.
            callback (function, optional): The callback function for code generation.

        Returns:
            None
        """
        return None


    # ================================================= Advanced methods ===========================================
    def compile_latex(self, file_path, pdf_latex_path=None):
        try:
            # Determine the pdflatex command based on the provided or default path
            if pdf_latex_path:
                pdflatex_command = pdf_latex_path
            else:
                pdflatex_command = self.personality.config.pdf_latex_path if self.personality.config.pdf_latex_path is not None else 'pdflatex'

            # Set the execution path to the folder containing the tmp_file
            execution_path = file_path.parent
            # Run the pdflatex command with the file path
            result = subprocess.run([pdflatex_command, "-interaction=nonstopmode", file_path], check=True, capture_output=True, text=True, cwd=execution_path)
            # Check the return code of the pdflatex command
            if result.returncode != 0:
                error_message = result.stderr.strip()
                return {"status":False,"error":error_message}

            # If the compilation is successful, you will get a PDF file
            pdf_file = file_path.with_suffix('.pdf')
            print(f"PDF file generated: {pdf_file}")
            return {"status":True,"file_path":pdf_file}

        except subprocess.CalledProcessError as e:
            print(f"Error occurred while compiling LaTeX: {e}")
            return {"status":False,"error":e}

    def find_numeric_value(self, text):
        pattern = r'\d+[.,]?\d*'
        match = re.search(pattern, text)
        if match:
            return float(match.group().replace(',', '.'))
        else:
            return None
    def remove_backticks(self, text):
        if text.startswith("```"):
            split_text = text.split("\n")
            text = "\n".join(split_text[1:])
        if text.endswith("```"):
            text= text[:-3]
        return text

    def search_duckduckgo(self, query: str, max_results: int = 10, instant_answers: bool = True, regular_search_queries: bool = True, get_webpage_content: bool = False) -> List[Dict[str, Union[str, None]]]:
        """
        Perform a search using the DuckDuckGo search engine and return the results as a list of dictionaries.

        Args:
            query (str): The search query to use in the search. This argument is required.
            max_results (int, optional): The maximum number of search results to return. Defaults to 10.
            instant_answers (bool, optional): Whether to include instant answers in the search results. Defaults to True.
            regular_search_queries (bool, optional): Whether to include regular search queries in the search results. Defaults to True.
            get_webpage_content (bool, optional): Whether to retrieve and include the website content for each result. Defaults to False.

        Returns:
            list[dict]: A list of dictionaries containing the search results. Each dictionary will contain 'title', 'body', and 'href' keys.

        Raises:
            ValueError: If neither instant_answers nor regular_search_queries is set to True.
        """
        if not pm.is_installed("duckduckgo_search"):
            pm.install("duckduckgo_search")
        from duckduckgo_search import DDGS
        if not (instant_answers or regular_search_queries):
            raise ValueError("One of ('instant_answers', 'regular_search_queries') must be True")

        query = query.strip("\"'")

        with DDGS() as ddgs:
            if instant_answers:
                answer_list = list(ddgs.answers(query))
                if answer_list:
                    answer_dict = answer_list[0]
                    answer_dict["title"] = query
                    answer_dict["body"] = next((item['Text'] for item in answer_dict['AbstractText']), None)
                    answer_dict["href"] = answer_dict.get('FirstURL', '')
            else:
                answer_list = []

            if regular_search_queries:
                results = ddgs.text(query, safe=False, result_type='link')
                for result in results[:max_results]:
                    title = result['Text'] or query
                    body = None
                    href = result['FirstURL'] or ''
                    answer_dict = {'title': title, 'body': body, 'href': href}
                    answer_list.append(answer_dict)

            if get_webpage_content:
                for i, result in enumerate(answer_list):
                    try:
                        response = requests.get(result['href'])
                        if response.status_code == 200:
                            content = response.text
                            answer_list[i]['body'] = content
                    except Exception as e:
                        print(f"Error retrieving webpage content for {result['href']}: {str(e)}")

            return answer_list


    def translate(self, text_chunk, output_language="french", max_generation_size=3000):
        start_header_id_template    = self.config.start_header_id_template
        end_header_id_template      = self.config.end_header_id_template
        system_message_template     = self.config.system_message_template

        translated = self.fast_gen(
                                "\n".join([
                                    f"{start_header_id_template}{system_message_template}{end_header_id_template}",
                                    f"Translate the following text to {output_language}.",
                                    "Be faithful to the original text and do not add or remove any information.",
                                    "Respond only with the translated text.",
                                    "Do not add comments or explanations.",
                                    f"{start_header_id_template}text to translate{end_header_id_template}",
                                    f"{text_chunk}",
                                    f"{start_header_id_template}translation{end_header_id_template}",
                                    ]),
                                    max_generation_size=max_generation_size, callback=self.sink)
        return translated
    def sequential_summarize(self, text: str, summary_context: str = "", task="Create final summary using this memory.", format: str = "bullet points", tone: str = "neutral", ctx_size: int = 4096, callback = None):
        """
        Summarizes a long text sequentially by processing chunks and maintaining a memory.
        
        Args:
            text (str): The input text to summarize.
            summary_context (str): Optional context to guide the summarization.
            format (str): Desired format for the final summary (e.g., "bullet points").
            tone (str): Desired tone for the final summary (e.g., "neutral").
            ctx_size (int): Total context window size of the model.
        
        Returns:
            str: The final formatted summary.
        """
        return self.personality.sequential_summarize(text, summary_context, format, tone, ctx_size, callback=callback)
    

    def summarize_text(
                        self,
                        text:str,
                        summary_instruction="summarize",
                        doc_name="chunk",
                        answer_start="",
                        max_generation_size=3000,
                        max_summary_size=512,
                        callback=None,
                        chunk_summary_post_processing=None,
                        summary_mode=SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL
                    ):
        tk = self.personality.model.tokenize(text)
        prev_len = len(tk)
        document_chunks=None
        while len(tk)>max_summary_size and (document_chunks is None or len(document_chunks)>1):
            self.step_start(f"Comprerssing {doc_name}...")
            chunk_size = int(self.personality.config.ctx_size*0.6)
            document_chunks = TextChunker.chunk_text(text, self.personality.model, chunk_size, 0, True)
            text = self.summarize_chunks(
                                            document_chunks,
                                            summary_instruction, 
                                            doc_name, 
                                            answer_start, 
                                            max_generation_size, 
                                            callback, 
                                            chunk_summary_post_processing=chunk_summary_post_processing,
                                            summary_mode=summary_mode)
            tk = self.personality.model.tokenize(text)
            dtk_ln=prev_len-len(tk)
            prev_len = len(tk)
            self.step(f"Current text size : {prev_len}, max summary size : {max_summary_size}")
            self.step_end(f"Comprerssing {doc_name}...")
            if dtk_ln<=10: # it is not summarizing
                break
        return text

    def smart_data_extraction(
                                self,
                                text,
                                data_extraction_instruction="summarize",
                                final_task_instruction="reformulate with better wording",
                                doc_name="chunk",
                                answer_start="",
                                max_generation_size=3000,
                                max_summary_size=512,
                                callback=None,
                                chunk_summary_post_processing=None,
                                summary_mode=SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL
                            ):
        tk = self.personality.model.tokenize(text)
        prev_len = len(tk)
        while len(tk)>max_summary_size:
            chunk_size = int(self.personality.config.ctx_size*0.6)
            document_chunks = TextChunker.chunk_text(text, self.personality.model, chunk_size, 0, True)
            text = self.summarize_chunks(
                                            document_chunks, 
                                            data_extraction_instruction, 
                                            doc_name, 
                                            answer_start, 
                                            max_generation_size, 
                                            callback, 
                                            chunk_summary_post_processing=chunk_summary_post_processing, 
                                            summary_mode=summary_mode
                                        )
            tk = self.personality.model.tokenize(text)
            dtk_ln=prev_len-len(tk)
            prev_len = len(tk)
            self.step(f"Current text size : {prev_len}, max summary size : {max_summary_size}")
            if dtk_ln<=10: # it is not sumlmarizing
                break
        self.step_start(f"Rewriting ...")
        text = self.summarize_chunks(
                                        [text],
                                        final_task_instruction, 
                                        doc_name, answer_start, 
                                        max_generation_size, 
                                        callback, 
                                        chunk_summary_post_processing=chunk_summary_post_processing
                                    )
        self.step_end(f"Rewriting ...")

        return text

    def summarize_chunks(
                            self,
                            chunks,
                            summary_instruction="summarize",
                            doc_name="chunk",
                            answer_start="",
                            max_generation_size=3000,
                            callback=None,
                            chunk_summary_post_processing=None,
                            summary_mode=SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL
                        ):
        start_header_id_template    = self.config.start_header_id_template
        end_header_id_template      = self.config.end_header_id_template
        system_message_template     = self.config.system_message_template

        if summary_mode==SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL:
            summary = ""
            for i, chunk in enumerate(chunks):
                self.step_start(f" Summary of {doc_name} - Processing chunk : {i+1}/{len(chunks)}")
                summary = f"{answer_start}"+ self.fast_gen(
                            "\n".join([
                                self.system_custom_header("previous chunks analysis"),
                                f"{summary}",
                                self.system_custom_header("current chunk"),
                                f"{chunk}",
                                self.system_full_header,
                                summary_instruction,
                                f"Keep only information relevant to the context",
                                f"the output must keep information from the previous chunk analysis and add the current chunk extracted information.",
                                f"Be precise and do not invent information that does not exist in the previous chunks analysis or the current chunk.",
                                f"Do not add any extra comments.",
                                self.system_custom_header("cumulative chunks analysis")+answer_start
                                ]),
                                max_generation_size=max_generation_size,
                                callback=callback)
                if chunk_summary_post_processing:
                    summary = chunk_summary_post_processing(summary)
                self.step_end(f" Summary of {doc_name} - Processing chunk : {i+1}/{len(chunks)}")
            return summary
        else:
            summeries = []
            for i, chunk in enumerate(chunks):
                self.step_start(f" Summary of {doc_name} - Processing chunk : {i+1}/{len(chunks)}")
                summary = f"{answer_start}"+ self.fast_gen(
                            "\n".join([
                                f"{start_header_id_template}Document_chunk [{doc_name}]{end_header_id_template}",
                                f"{chunk}",
                                f"{start_header_id_template}{system_message_template}{end_header_id_template}{summary_instruction}",
                                f"Answer directly with the summary with no extra comments.",
                                f"{start_header_id_template}summary{end_header_id_template}",
                                f"{answer_start}"
                                ]),
                                max_generation_size=max_generation_size,
                                callback=callback)
                if chunk_summary_post_processing:
                    summary = chunk_summary_post_processing(summary)
                summeries.append(summary)
                self.step_end(f" Summary of {doc_name} - Processing chunk : {i+1}/{len(chunks)}")
            return "\n".join(summeries)

    def sequencial_chunks_summary(
                            self,
                            chunks,
                            summary_instruction="summarize",
                            doc_name="chunk",
                            answer_start="",
                            max_generation_size=3000,
                            callback=None,
                            chunk_summary_post_processing=None
                        ):
        start_header_id_template    = self.config.start_header_id_template
        end_header_id_template      = self.config.end_header_id_template
        system_message_template     = self.config.system_message_template
        summeries = []
        for i, chunk in enumerate(chunks):
            if i<len(chunks)-1:
                chunk1 = chunks[i+1]
            else:
                chunk1=""
            if i>0:
                chunk=summary
            self.step_start(f" Summary of {doc_name} - Processing chunk : {i+1}/{len(chunks)}")
            summary = f"{answer_start}"+ self.fast_gen(
                        "\n".join([
                            f"{start_header_id_template}Document_chunk: {doc_name}{end_header_id_template}",
                            f"Block1:",
                            f"{chunk}",
                            f"Block2:",
                            f"{chunk1}",
                            f"{start_header_id_template}{system_message_template}{end_header_id_template}{summary_instruction}",
                            f"Answer directly with the summary with no extra comments.",
                            f"{start_header_id_template}summary{end_header_id_template}",
                            f"{answer_start}"
                            ]),
                            max_generation_size=max_generation_size,
                            callback=callback)
            if chunk_summary_post_processing:
                summary = chunk_summary_post_processing(summary)
            summeries.append(summary)
            self.step_end(f" Summary of {doc_name} - Processing chunk : {i+1}/{len(chunks)}")
        return "\n".join(summeries)
    
    def build_prompt(self, prompt_parts:List[str], sacrifice_id:int=-1, context_size:int=None, minimum_spare_context_size:int=None):
        """
        Builds the prompt for code generation.

        Args:
            prompt_parts (List[str]): A list of strings representing the parts of the prompt.
            sacrifice_id (int, optional): The ID of the part to sacrifice.
            context_size (int, optional): The size of the context.
            minimum_spare_context_size (int, optional): The minimum spare context size.

        Returns:
            str: The built prompt.
        """
        if context_size is None:
            context_size = self.personality.config.ctx_size
        if minimum_spare_context_size is None:
            minimum_spare_context_size = self.personality.config.min_n_predict

        if sacrifice_id == -1 or len(prompt_parts[sacrifice_id])<50:
            return self.separator_template.join([s for s in prompt_parts if s!=""])
        else:
            part_tokens=[]
            nb_tokens=0
            for i, part in enumerate(prompt_parts):
                part_s=part.strip()
                tk = self.personality.model.tokenize(part_s)
                part_tokens.append(tk)
                if i != sacrifice_id:
                    nb_tokens += len(tk)
                    
            if len(part_tokens[sacrifice_id])>0:
                sacrifice_tk = part_tokens[sacrifice_id]
                sacrifice_tk= sacrifice_tk[-(context_size-nb_tokens-minimum_spare_context_size):]
                sacrifice_text = self.personality.model.detokenize(sacrifice_tk)
            else:
                sacrifice_text = ""
            prompt_parts[sacrifice_id] = sacrifice_text
            return self.separator_template.join([s for s in prompt_parts if s!=""])
    # ================================================= Sending commands to ui ===========================================
    def add_collapsible_entry(self, title, content, subtitle="", open_by_default=False, icon=None, type="default"):
        """
        Creates a collapsible entry with enhanced styling and animations.
        
        Args:
            title (str): The main title of the collapsible
            content (str): The content to be displayed when expanded
            subtitle (str): Optional subtitle text
            open_by_default (bool): Whether the collapsible should be open by default
            icon (str): Optional custom icon SVG string
            type (str): Type of collapsible ('default', 'success', 'warning', 'error', 'info')
        
        Returns:
            str: HTML string for the collapsible element
        """
        # Color schemes for different types
        color_schemes = {
            "default": "border-gray-200 bg-white hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-750",
            "success": "border-green-200 bg-green-50 hover:bg-green-100 dark:border-green-700 dark:bg-green-900/20 dark:hover:bg-green-900/30",
            "warning": "border-yellow-200 bg-yellow-50 hover:bg-yellow-100 dark:border-yellow-700 dark:bg-yellow-900/20 dark:hover:bg-yellow-900/30",
            "error": "border-red-200 bg-red-50 hover:bg-red-100 dark:border-red-700 dark:bg-red-900/20 dark:hover:bg-red-900/30",
            "info": "border-blue-200 bg-blue-50 hover:bg-blue-100 dark:border-blue-700 dark:bg-blue-900/20 dark:hover:bg-blue-900/30"
        }
        
        # Default arrow icon if no custom icon is provided
        default_icon = '''
<svg class="w-5 h-5 text-gray-500 dark:text-gray-400 transition-transform duration-300 transform group-open:rotate-90" 
xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
<path fill-rule="evenodd" 
d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" 
clip-rule="evenodd" />
</svg>
        '''
        
        icon_html = icon if icon else default_icon
        color_scheme = color_schemes.get(type, color_schemes["default"])
        open_attr = 'open' if open_by_default else ''
        
        return "\n".join([
            f'''
<details 
class="group w-full rounded-xl border {color_scheme} shadow-sm mb-4 
transition-all duration-300 ease-in-out hover:shadow-md 
focus-within:ring-2 focus-within:ring-blue-500 dark:focus-within:ring-blue-400" 
{open_attr}>
<summary 
class="flex items-center justify-between p-4 cursor-pointer select-none 
transition-all duration-300 ease-in-out">
<div class="flex items-center space-x-3 flex-grow">
<div class="flex-shrink-0">
{icon_html}
</div>
<div class="flex-grow">
<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
{title}
</h3>
{f'<p class="text-sm text-gray-500 dark:text-gray-400">{subtitle}</p>' if subtitle else ''}
</div>
</div>
<div class="flex-shrink-0">
<svg class="w-5 h-5 text-gray-500 dark:text-gray-400 transition-transform duration-300 
transform group-open:rotate-180" 
xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
<path fill-rule="evenodd" 
d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" 
clip-rule="evenodd" />
</svg>
</div>
</summary>
<div class="px-4 pb-4 pt-2 text-gray-700 dark:text-gray-300 
transition-all duration-300 ease-in-out">
<div class="prose dark:prose-invert max-w-none">
{content}
</div>
</div>
</details>
'''
])



    def internet_search_with_vectorization(self, query, quick_search:bool=False ):
        """
        Do internet search and return the result
        """
        return self.personality.internet_search_with_vectorization(query, quick_search=quick_search)


    def vectorize_and_query(self, title, url, text, query, max_chunk_size=512, overlap_size=20, internet_vectorization_nb_chunks=3):
        vectorizer = SafeStore("")
        vectorizer.add_document(title, text, url)
        vectorizer.build_index()
        chunks = vectorizer.search(query, internet_vectorization_nb_chunks)
        return chunks


    def step_start(self, step_text, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None):
        """This triggers a step start

        Args:
            step_text (str): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the step start to. Defaults to None.
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(step_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_START)

    def step_end(self, step_text, status=True, callback: Callable[[str, int, dict, list], bool]=None):
        """This triggers a step end

        Args:
            step_text (str): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the step end to. Defaults to None.
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(step_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_SUCCESS if status else MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_END_FAILURE)

    def step(self, step_text, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None):
        """This triggers a step information

        Args:
            step_text (str): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE, dict, list) to send the step to. Defaults to None.
            The callback has these fields:
            - chunk
            - Message Type : the type of message
            - Parameters (optional) : a dictionary of parameters
            - Metadata (optional) : a list of metadata
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(step_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP)

    def exception(self, ex, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None):
        """This sends exception to the client

        Args:
            step_text (str): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE, dict, list) to send the step to. Defaults to None.
            The callback has these fields:
            - chunk
            - Message Type : the type of message
            - Parameters (optional) : a dictionary of parameters
            - Metadata (optional) : a list of metadata
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(str(ex), MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_EXCEPTION)

    def warning(self, warning:str, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None):
        """This sends exception to the client

        Args:
            step_text (str): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE, dict, list) to send the step to. Defaults to None.
            The callback has these fields:
            - chunk
            - Message Type : the type of message
            - Parameters (optional) : a dictionary of parameters
            - Metadata (optional) : a list of metadata
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(warning, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_EXCEPTION)


    def json(self, title:str, json_infos:dict, callback: Callable[[str, int, dict, list], bool]=None, indent=4):
        """This sends json data to front end

        Args:
            step_text (dict): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE, dict, list) to send the step to. Defaults to None.
            The callback has these fields:
            - chunk
            - Message Type : the type of message
            - Parameters (optional) : a dictionary of parameters
            - Metadata (optional) : a list of metadata
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback([{"title":title, "content":json.dumps(json_infos, indent=indent)}], MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_JSON_INFOS)

    def set_message_html(self, html_ui:str, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]|None=None):
        """This sends ui elements to front end

        Args:
            step_text (dict): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE, dict, list) to send the step to. Defaults to None.
            The callback has these fields:
            - chunk
            - Message Type : the type of message
            - Parameters (optional) : a dictionary of parameters
            - Metadata (optional) : a list of metadata
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(html_ui, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI)


    def ui_in_iframe(self, html_ui:str, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None, client_id= None):
        """This sends ui elements to front end inside an iframe

        Args:
            html_ui (str): The HTML content to be displayed inside the iframe
            callback (callable, optional): A callable with this signature (str, MSG_TYPE, dict, list) to send the step to. Defaults to None.
            The callback has these fields:
            - chunk
            - Message Type : the type of message
            - Parameters (optional) : a dictionary of parameters
            - Metadata (optional) : a list of metadata
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            iframe_html = f'<iframe class="w-full" srcdoc="{html_ui}" style="width:100%; height:100%; border:none;"></iframe>'
            callback(iframe_html, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI)





    def code(self, code:str, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None):
        """This sends code to front end

        Args:
            step_text (dict): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE, dict, list) to send the step to. Defaults to None.
            The callback has these fields:
            - chunk
            - Message Type : the type of message
            - Parameters (optional) : a dictionary of parameters
            - Metadata (optional) : a list of metadata
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(code, MSG_OPERATION_TYPE.MSG_TYPE_CODE)

    def add_chunk_to_message_content(self, full_text:str, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None):
        """This sends full text to front end

        Args:
            step_text (dict): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the text to. Defaults to None.
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(full_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK)


    def set_message_content(self, full_text:str, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None, msg_type:MSG_OPERATION_TYPE = MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT):
        """This sends full text to front end

        Args:
            step_text (dict): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the text to. Defaults to None.
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(full_text, msg_type)

    def set_message_content_invisible_to_ai(self, full_text:str, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None):
        """This sends full text to front end (INVISIBLE to AI)

        Args:
            step_text (dict): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the text to. Defaults to None.
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(full_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI)

    def set_message_content_invisible_to_user(self, full_text:str, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None):
        """This sends full text to front end (INVISIBLE to user)

        Args:
            step_text (dict): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the text to. Defaults to None.
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(full_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_USER)




    def execute_python(self, code, code_folder=None, code_file_name=None):
        if code_folder is not None:
            code_folder = Path(code_folder)

        """Executes Python code and returns the output as JSON."""
        # Create a temporary file.
        root_folder = code_folder if code_folder is not None else self.personality.personality_output_folder
        root_folder.mkdir(parents=True,exist_ok=True)
        tmp_file = root_folder/(code_file_name if code_file_name is not None else f"ai_code.py")
        with open(tmp_file,"w") as f:
            f.write(code)

        # Execute the Python code in a temporary file.
        process = subprocess.Popen(
            ["python", str(tmp_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=root_folder
        )

        # Get the output and error from the process.
        output, error = process.communicate()

        # Check if the process was successful.
        if process.returncode != 0:
            # The child process threw an exception.
            error_message = f"Error executing Python code: {error.decode('utf8')}"
            return error_message

        # The child process was successful.
        return output.decode("utf8")

    def build_python_code(self, prompt, max_title_length=4096):
        start_header_id_template    = self.config.start_header_id_template
        end_header_id_template      = self.config.end_header_id_template
        system_message_template     = self.config.system_message_template

        global_prompt = "\n".join([
            f"{prompt}",
            f"{start_header_id_template}Extra conditions{end_header_id_template}",
            "- The code must be complete, not just snippets, and should be put inside a single python markdown code.",
            "- Preceive each python codeblock with a line using this syntax:",
            "```python",
            "# FILENAME: the file path relative to the root folder of the project",
            "# Placeholder. Here you need to put the code for the file",
            "```",
            f"{start_header_id_template}Code Builder{end_header_id_template}"
        ])
        code = self.fast_gen(global_prompt, max_title_length)
        code_blocks = self.extract_code_blocks(code)
        if len(code_blocks)>0:
            return code_blocks[0]["content"]
        else:
            return None


    @staticmethod
    def update_code_with_best_match(original_content: str, original_code: str, new_code: str) -> str:
        """
        Updates the original content by replacing the best-matching code snippet with the new code.
        
        Args:
            original_content (str): The complete source code content
            original_code (str): The code snippet to be replaced
            new_code (str): The new code snippet to insert
        
        Returns:
            str: Updated content with the replacement made
            
        Raises:
            ValueError: If no sufficiently close match is found
        """
        if not pm.is_installed("difflib"):
            pm.install("difflib")

        import difflib
        # Normalize line endings and strip whitespace from inputs
        original_code = original_code.strip()
        new_code = new_code.strip()
        
        # If any of the inputs are empty, raise an error
        if not original_content or not original_code:
            raise ValueError("Original content and code snippet cannot be empty")
        
        # Split content into lines for better matching
        content_lines = original_content.splitlines()
        code_lines = original_code.splitlines()
        
        # Join lines to create a normalized version of the original code
        normalized_code = '\n'.join(code_lines)
        
        # Find the best match using difflib
        best_match = None
        best_match_ratio = 0
        best_match_start = None
        best_match_end = None
        
        for i in range(len(content_lines) - len(code_lines) + 1):
            # Extract a slice of the content to compare
            content_slice = '\n'.join(content_lines[i:i + len(code_lines)])
            
            # Calculate similarity ratio
            match_ratio = difflib.SequenceMatcher(None, content_slice.strip(), normalized_code.strip()).ratio()
            
            # Update the best match if this one is better
            if match_ratio > best_match_ratio:
                best_match = content_slice
                best_match_ratio = match_ratio
                best_match_start = i
                best_match_end = i + len(code_lines)
        
        # Check if a sufficiently close match was found
        if best_match is None or best_match_ratio < 0.8:  # Threshold for similarity
            raise ValueError("No sufficiently close match found for the original code snippet")
        
        # Preserve original indentation
        first_line = content_lines[best_match_start]
        indentation = ''
        for char in first_line:
            if char in (' ', '\t'):
                indentation += char
            else:
                break
        
        # Apply indentation to new code
        new_code_lines = [indentation + line if line.strip() else line 
                        for line in new_code.splitlines()]
        
        # Combine everything together
        updated_lines = (
            content_lines[:best_match_start] +
            new_code_lines +
            content_lines[best_match_end:]
        )
        
        return '\n'.join(updated_lines)



    def make_title(self, prompt, max_title_length: int = 50):
        """
        Generates a title for a given prompt.

        Args:
            prompt (str): The prompt for which a title needs to be generated.
            max_title_length (int, optional): The maximum length of the generated title. Defaults to 50.

        Returns:
            str: The generated title.
        """
        start_header_id_template    = self.config.start_header_id_template
        separator_template          = self.config.separator_template
        end_header_id_template      = self.config.end_header_id_template
        system_message_template     = self.config.system_message_template
        global_prompt = f"{start_header_id_template}{system_message_template}{end_header_id_template}Based on the provided prompt, suggest a concise and relevant title that captures the main topic or theme of the conversation. Only return the suggested title, without any additional text or explanation.{separator_template}{start_header_id_template}prompt{end_header_id_template}{prompt}{separator_template}{start_header_id_template}title{end_header_id_template}"
        title = self.fast_gen(global_prompt,max_title_length)
        return title


    def plan(self, 
                         request: str, 
                         images:list=[], 
                         actions_list:list=[LoLLMsAction], 
                         context:str = "", 
                         max_answer_length: int = 512) -> List[LoLLMsAction]:
        """
        creates a plan out of a request and a context

        Args:
            request (str): The request posed by the user.
            max_answer_length (int, optional): Maximum string length allowed while interpreting the users' responses. Defaults to 50.

        Returns:
            int: Index of the selected option within the possible_ansers list. Or -1 if there was not match found among any of them.
        """
        
        prompt = "\n".join([
            self.system_full_header,
            "Act as plan builder, a tool capable of making plans to perform the user requested operation."
        ])
        
        if len(actions_list)>0:
            prompt += "\n".join([
                "The plan builder is an AI that responds in json format. It should plan a succession of actions in order to reach the objective.",
                self.system_custom_header("list of action types information"),                
                f"{[str(a) for a in actions_list]}",
                "Remember, you can only use one of these actions in the list",
                "The AI should respond in this format using data from actions_list:",
                "```json",
                "{",
                '    "actions": [',
                '    {',
                '        "name": name of the action 1,',
                '        "parameters":[',
                '            parameter name: parameter value',
                '        ]',
                '    },',
                '    {',
                '        "name": name of the action 2,',
                '        "parameters":[',
                '            parameter name: parameter value',
                '        ]',
                '    }',
                '    ...',
                '    ]',
                "}"
                "```",
                ""
            ])
        if context != "":
            
            prompt += "\n".join([
                self.system_custom_header("context"),
                f"{context}"
            ])

        prompt += "\n".join([
            self.system_custom_header("request"),
            f"{request}",
            self.ai_custom_header("plan"),
        ])
        self.print_prompt("prompt",prompt)
        code = self.generate_code(prompt, images, max_answer_length).strip().replace("</s>","").replace("<s>","")
        code = fix_json(code)
        return generate_actions(actions_list, code), code


    def parse_directory_structure(self, structure):
        paths = []
        lines = structure.strip().split('\n')
        stack = []

        for line in lines:
            line = line.rstrip()
            level = (len(line) - len(line.lstrip())) // 4

            if '/' in line or line.endswith(':'):
                directory = line.strip(' ├─└│').rstrip(':').rstrip('/')

                while stack and level < stack[-1][0]:
                    stack.pop()

                stack.append((level, directory))
                path = '/'.join([dir for _, dir in stack]) + '/'
                paths.append(path)
            else:
                file = line.strip(' ├─└│')
                if stack:
                    path = '/'.join([dir for _, dir in stack]) + '/' + file
                    paths.append(path)

        return paths

    def update_section(self, content, section_name, new_code):
        # Define patterns for HTML, JavaScript, and CSS sections
        html_pattern = re.compile(f"<!-- section_start: {section_name} -->.*?<!-- section_end: {section_name} -->", re.DOTALL)
        js_css_pattern = re.compile(f"// section_start: {section_name}.*?// section_end: {section_name}", re.DOTALL)

        # Try to replace HTML section
        updated_content, html_replacements = re.subn(html_pattern, f"<!-- section_start: {section_name} -->\n{new_code}\n<!-- section_end: {section_name} -->", content)

        # If HTML replacement didn't occur, try JavaScript/CSS section
        if html_replacements == 0:
            updated_content, js_css_replacements = re.subn(js_css_pattern, f"// section_start: {section_name}\n{new_code}\n// section_end: {section_name}", content)
            
            if js_css_replacements == 0:
                return content, False  # Section not found
        
        return updated_content, True  # Section updated successfully


    def parse_code_replacement(self, input_text: str) -> tuple[str, str]:
        """
        Parses a code replacement string format and extracts original and new code segments.
        
        Args:
            input_text (str): Input text in the format:
                            # REPLACE
                            # ORIGINAL
                            <old_code>
                            # SET
                            <new_code_snippet>
        
        Returns:
            tuple[str, str]: A tuple containing (original_code, new_code)
                            Both strings are stripped of leading/trailing whitespace
        
        Raises:
            ValueError: If the input format is invalid or markers are missing
        """
        # Split the text into lines
        lines = input_text.strip().split('\n')
        
        try:
            # Find marker positions
            original_marker = next(i for i, line in enumerate(lines) if line.strip() == "# ORIGINAL")
            set_marker = next(i for i, line in enumerate(lines) if line.strip() == "# SET")
            
            # Extract code segments
            original_code = '\n'.join(lines[original_marker + 1:set_marker]).strip()
            new_code = '\n'.join(lines[set_marker + 1:]).strip()
            
            return original_code, new_code
            
        except StopIteration:
            raise ValueError("Invalid format: Missing required markers (# ORIGINAL or # SET)")



    def extract_code_blocks(self, text: str, return_remaining_text: bool = False) -> Union[List[dict], Tuple[List[dict], str]]:
        codes = []
        remaining_text = text
        current_index = 0
        
        while True:
            # Find next code block start
            start_pos = remaining_text.find('```')
            if start_pos == -1:
                break
                
            # Check for file name before code block
            file_name = ''
            file_name_match = remaining_text[:start_pos].rfind('<file_name>')
            if file_name_match != -1:
                file_name_end = remaining_text[:start_pos].rfind('</file_name>')
                if file_name_end != -1 and file_name_match < file_name_end:
                    file_name = remaining_text[file_name_match + 11:file_name_end].strip()
            
            # Get code type if specified
            code_type = ''
            next_newline = remaining_text.find('\n', start_pos + 3)
            if next_newline != -1:
                potential_type = remaining_text[start_pos + 3:next_newline].strip()
                if potential_type:
                    code_type = potential_type
                    start_pos = next_newline + 1
                else:
                    start_pos += 3
            else:
                start_pos += 3
                
            # Find matching end tag
            tag_count = 1
            pos = start_pos
            content_start = start_pos
            is_complete = False
            
            while pos < len(remaining_text):
                if remaining_text[pos:pos + 3] == '```':
                    tag_count -= 1
                    if tag_count == 0:
                        # Found matching end tag
                        content = remaining_text[content_start:pos].strip()
                        is_complete = True
                        codes.append({
                            'index': current_index,
                            'file_name': file_name,
                            'content': content,
                            'type': code_type,
                            'is_complete': True
                        })
                        remaining_text = remaining_text[pos + 3:]
                        break
                elif remaining_text[pos:pos + 3] == '```':
                    tag_count += 1
                pos += 1
                
            if not is_complete:
                # Handle incomplete code block
                content = remaining_text[content_start:].strip()
                codes.append({
                    'index': current_index,
                    'file_name': file_name,
                    'content': content,
                    'type': code_type,
                    'is_complete': False
                })
                remaining_text = ''
                
            current_index += 1
        
        if return_remaining_text:
            return codes, remaining_text
        return codes



    def build_and_execute_python_code(self,context, instructions, execution_function_signature, extra_imports=""):
        start_header_id_template    = self.config.start_header_id_template
        end_header_id_template      = self.config.end_header_id_template

        code =  self.generate_code(self.build_prompt([
            self.system_custom_header('context'),
            context,
            self.system_full_header,
            f"{instructions}",
            "Don't call the function, just write it",
            "Do not provide usage example.",
            "The code must me without comments",
            ],2), self.personality.image_files, execution_function_signature, "python")


        # Perform the search query
        code = code["content"]
        code = "\n".join([
                    extra_imports,
                    code
                ])
        ASCIIColors.magenta(code)
        module_name = 'custom_module'
        spec = importlib.util.spec_from_loader(module_name, loader=None)
        module = importlib.util.module_from_spec(spec)
        exec(code, module.__dict__)
        return module, code


    def yes_no(self, question: str, context:str="", max_answer_length: int = None, conditionning="", return_explanation=False, callback = None) -> bool:
        """
        Analyzes the user prompt and answers whether it is asking to generate an image.

        Args:
            question (str): The user's message.
            max_answer_length (int, optional): The maximum length of the generated answer. Defaults to 50.
            conditionning: An optional system message to put at the beginning of the prompt
        Returns:
            bool: True if the user prompt is asking to generate an image, False otherwise.
        """
        return self.personality.yes_no(question, context, max_answer_length, conditionning=conditionning, return_explanation=return_explanation, callback=callback)

    def multichoice_question(
            self, 
            question: str, 
            possible_answers: list, 
            context: str = "", 
            max_answer_length: int = None, 
            conditionning: str = "", 
            return_explanation: bool = False,
            callback = None
        ) -> dict:
        """
        Interprets a multi-choice question from a users response. This function expects only one choice as true. All other choices are considered false. If none are correct, returns -1.

        Args:
            question (str): The multi-choice question posed by the user.
            possible_ansers (List[Any]): A list containing all valid options for the chosen value. For each item in the list, either 'True', 'False', None or another callable should be passed which will serve as the truth test function when checking against the actual user input.
            max_answer_length (int, optional): Maximum string length allowed while interpreting the users' responses. Defaults to 50.
            conditionning: An optional system message to put at the beginning of the prompt

        Returns:
            int: Index of the selected option within the possible_ansers list. Or -1 if there was not match found among any of them.
        """
        return self.personality.multichoice_question(question, possible_answers, context, max_answer_length, conditionning, return_explanation, callback=callback)

    def multichoice_ranking(
                                self, 
                                question: str, 
                                possible_answers:list, 
                                context:str = "", 
                                max_answer_length: int = 50, 
                                conditionning="", 
                                return_explanation:bool = False,
                                callback=None
                            ) -> int:
        """
        Ranks answers for a question from best to worst. returns a list of integers

        Args:
            question (str): The multi-choice question posed by the user.
            possible_ansers (List[Any]): A list containing all valid options for the chosen value. For each item in the list, either 'True', 'False', None or another callable should be passed which will serve as the truth test function when checking against the actual user input.
            max_answer_length (int, optional): Maximum string length allowed while interpreting the users' responses. Defaults to 50.
            conditionning: An optional system message to put at the beginning of the prompt

        Returns:
            int: Index of the selected option within the possible_ansers list. Or -1 if there was not match found among any of them.
        """
        return self.personality.multichoice_ranking(question, possible_answers, context, max_answer_length, conditionning, return_explanation, callback)


    def build_html5_integration(self, html, ifram_name="unnamed"):
        """
        This function creates an HTML5 iframe with the given HTML content and iframe name.

        Args:
        html (str): The HTML content to be displayed in the iframe.
        ifram_name (str, optional): The name of the iframe. Defaults to "unnamed".

        Returns:
        str: The HTML string for the iframe.
        """
        return "\n".join(
            [
                '<div class="card">',
                f'<iframe id="{ifram_name}" srcdoc="{html}" style="width: 100%; height: 600px; border: none;"></iframe>',
                '</div>'
            ]
        )



    def InfoMessage(self, content, client_id=None, verbose:bool=None):
        self.personality.app.notify(
                content, 
                notification_type=NotificationType.NOTIF_SUCCESS, 
                duration=0, 
                client_id=client_id, 
                display_type=NotificationDisplayType.MESSAGE_BOX,
                verbose=verbose
            )

    def info(self, info_text:str, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None):
        """This sends info text to front end

        Args:
            step_text (dict): The step text
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the info to. Defaults to None.
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(info_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT)


    def error(self, content, duration:int=4, client_id=None, verbose:bool=True):
        self.personality.error(content=content, duration=duration, client_id=client_id, verbose=verbose)
    def success(self, content, duration:int=4, client_id=None, verbose:bool=True):
        self.personality.success(content=content, duration=duration, client_id=client_id, verbose=verbose)


    def step_progress(self, step_text:str, progress:float, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None):
        """This sends step rogress to front end

        Args:
            step_text (dict): The step progress in %
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the progress to. Defaults to None.
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(step_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_PROGRESS, {'progress':progress})


    def ask_user(self, question):
        try:
            app = QApplication(sys.argv)
            input_field = QLineEdit(question)
            input_field.setWindowTitle("Input")
            input_field.exec_()
            answer = input_field.text()
            input_field.deleteLater()
            return answer
        except:
            ASCIIColors.warning(question)

    def ask_user_yes_no(self, question):
        try:
            app = QApplication(sys.argv)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setText(question)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            response = msg.exec_()
            return response == QMessageBox.Yes
        except:
            print(question)



    def ask_user_multichoice_question(self, question, choices, default=None):
        try:
            from PyQt5.QtWidgets import QLabel, QPushButton
            app = QApplication(sys.argv)
            window = QWidget()
            layout = QVBoxLayout()
            window.setLayout(layout)
            
            label = QLabel(question)
            layout.addWidget(label)
            
            button_group = QButtonGroup()
            for i, choice in enumerate(choices):
                button = QRadioButton(choice)
                button_group.addButton(button)
                layout.addWidget(button)
            
            if default is not None:
                for button in button_group.buttons():
                    if button.text() == default:
                        button.setChecked(True)
                        break
            
            def on_ok():
                nonlocal result
                result = [button.text() for button in button_group.buttons() if button.isChecked()]
                window.close()
            
            button = QPushButton("OK")
            button.clicked.connect(on_ok)
            layout.addWidget(button)
            
            window.show()
            result = None
            sys.exit(app.exec_())
            
            return result
        except:
            ASCIIColors.error(question)

    def new_message(self, message_text:str, message_type:MSG_OPERATION_TYPE= MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT, metadata=[], callback: Callable[[str, int, dict, list, AIPersonality], bool]=None):
        """This sends step rogress to front end

        Args:
            step_text (dict): The step progress in %
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the progress to. Defaults to None.
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(message_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_NEW_MESSAGE, personality = self.personality)

    def finished_message(self, message_text:str="", callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None):
        """This sends step rogress to front end

        Args:
            step_text (dict): The step progress in %
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the progress to. Defaults to None.
        """
        if not callback and self.callback:
            callback = self.callback

        if callback:
            callback(message_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_FINISHED_MESSAGE)

    def print_prompt(self, title, prompt):
        ASCIIColors.red("*-*-*-*-*-*-*-* ", end="")
        ASCIIColors.red(title, end="")
        ASCIIColors.red(" *-*-*-*-*-*-*-*")
        ASCIIColors.yellow(prompt)
        ASCIIColors.red(" *-*-*-*-*-*-*-*")


    def fast_gen_with_images(self, prompt: str, images:list, max_generation_size: int= None, placeholders: dict = {}, sacrifice: list = ["previous_discussion"], debug: bool = False, callback=None, show_progress=False) -> str:
        """
        Fast way to generate code

        This method takes in a prompt, maximum generation size, optional placeholders, sacrifice list, and debug flag.
        It reshapes the context before performing text generation by adjusting and cropping the number of tokens.

        Parameters:
        - prompt (str): The input prompt for text generation.
        - max_generation_size (int): The maximum number of tokens to generate.
        - placeholders (dict, optional): A dictionary of placeholders to be replaced in the prompt. Defaults to an empty dictionary.
        - sacrifice (list, optional): A list of placeholders to sacrifice if the window is bigger than the context size minus the number of tokens to generate. Defaults to ["previous_discussion"].
        - debug (bool, optional): Flag to enable/disable debug mode. Defaults to False.

        Returns:
        - str: The generated text after removing special tokens ("<s>" and "</s>") and stripping any leading/trailing whitespace.
        """
        return self.personality.fast_gen_with_images(prompt=prompt, images=images, max_generation_size=max_generation_size,placeholders=placeholders, sacrifice=sacrifice, debug=debug, callback=callback, show_progress=show_progress)

    def fast_gen(self, prompt: str, max_generation_size: int= None, placeholders: dict = {}, sacrifice: list = ["previous_discussion"], debug: bool = False, callback=None, show_progress=False) -> str:
        """
        Fast way to generate text

        This method takes in a prompt, maximum generation size, optional placeholders, sacrifice list, and debug flag.
        It reshapes the context before performing text generation by adjusting and cropping the number of tokens.

        Parameters:
        - prompt (str): The input prompt for text generation.
        - max_generation_size (int): The maximum number of tokens to generate.
        - placeholders (dict, optional): A dictionary of placeholders to be replaced in the prompt. Defaults to an empty dictionary.
        - sacrifice (list, optional): A list of placeholders to sacrifice if the window is bigger than the context size minus the number of tokens to generate. Defaults to ["previous_discussion"].
        - debug (bool, optional): Flag to enable/disable debug mode. Defaults to False.

        Returns:
        - str: The generated text after removing special tokens ("<s>" and "</s>") and stripping any leading/trailing whitespace.
        """
        return self.personality.fast_gen(prompt=prompt,max_generation_size=max_generation_size,placeholders=placeholders, sacrifice=sacrifice, debug=debug, callback=callback, show_progress=show_progress)




    def generate_text_with_tag(self, prompt, tag_name="SPECIAL_TAG"):
        """
        Generates text using self.fast_gen and wraps it inside a custom tag.
        
        :param prompt: The input prompt for text generation.
        :param tag_name: The name of the tag to wrap the generated text (default is "SPECIAL_TAG").
        :return: The generated text wrapped inside the specified tag.
        """
        return self.personality.generate_text_with_tag(prompt, tag_name)

    def extract_text_from_tag(self, tagged_text, tag_name="SPECIAL_TAG"):
        """
        Extracts the text from a custom tag.
        
        :param tagged_text: The text containing the tagged content.
        :param tag_name: The name of the tag to extract text from (default is "SPECIAL_TAG").
        :return: The extracted text from the specified tag.
        """
        return self.personality.extract_text_from_tag(tagged_text, tag_name)

    def mix_it_up(self, prompt: str, models, master_model, nb_rounds=2, max_generation_size: int= None, placeholders: dict = {}, sacrifice: list = ["previous_discussion"], debug: bool = False, callback=None, show_progress=False) -> dict:
        """
        Fast generates text using multiple LLMs with detailed round tracking. Each LLM sees the initial prompt plus the formatted outputs of the previous rounds.
        The master model then completes the job by creating a unique answer inspired by the last round outputs.

        Parameters:
        - prompt (str): The input prompt for text generation.
        - models (list of str): The list of model identifiers in the format "binding_name::model_name".
        - master_model (str): The model identifier for the master model, also in the format "binding_name::model_name".
        - max_generation_size (int): The maximum number of tokens to generate.
        - placeholders (dict, optional): A dictionary of placeholders to be replaced in the prompt. Defaults to an empty dictionary.
        - sacrifice (list, optional): A list of placeholders to sacrifice if the window is bigger than the context size minus the number of tokens to generate. Defaults to ["previous_discussion"].
        - debug (bool, optional): Flag to enable/disable debug mode. Defaults to False.

        Returns:
        - dict: A dictionary with the round information and the final generated text, keys: 'rounds' and 'final_output'.
        """
        context = prompt
        previous_outputs = []

        # Dictionary to store rounds information
        rounds_info = {
            'initial_prompt': prompt,
            'rounds': []
        }
        for round in range(nb_rounds):
            self.step_start(f"Round {round + 1}")
            for idx, model_id in enumerate(models):
                self.step_start(f"Using model {model_id}")
                binding_name, model_name = model_id.split("::")
                self.select_model(binding_name, model_name)
                
                # Concatenate previous outputs with formatting
                formatted_previous_outputs = "\n".join([f"Model {m}: {o}" for m, o in previous_outputs])
                round_prompt = context + "\n" + formatted_previous_outputs
                output = self.fast_gen(prompt=round_prompt, max_generation_size=max_generation_size, placeholders=placeholders, sacrifice=sacrifice, debug=debug, callback=callback, show_progress=show_progress)
                
                rounds_info['rounds'].append({
                    'model': model_id,
                    'round_prompt': round_prompt,
                    'output': output
                })
                previous_outputs.append((model_id, output))  # Update for the next round
                self.step_end(f"Using model {model_id}")
            self.step_end(f"Round {round + 1}")

        # Final round with the master model
        self.select_model(*master_model.split("::"))
        
        # Last round output for the master model
        formatted_previous_outputs = "\n".join([f"Model {m}: {o}" for m, o in previous_outputs])
        final_prompt = context + "\n" + formatted_previous_outputs
        final_output = self.fast_gen(prompt=final_prompt, max_generation_size=max_generation_size, placeholders=placeholders, sacrifice=sacrifice, debug=debug, callback=callback, show_progress=show_progress)

        rounds_info['final_output'] = final_output

        return rounds_info

    def answer(self, context_details:LollmsContextDetails, custom_entries = "", send_full=True, callback=None):
        if context_details.is_continue:
            full_prompt = context_details.build_prompt(self.personality.app.template, custom_entries=custom_entries, suppress= ["ai_prefix"])
        else:
            full_prompt = context_details.build_prompt(self.personality.app.template, custom_entries=custom_entries)

        out = self.fast_gen(full_prompt)
        nb_tokens = len(self.personality.model.tokenize(out))
        if nb_tokens >= (self.config.max_n_predict if self.config.max_n_predict else self.config.ctx_size)-1:
            out = out+self.fast_gen(full_prompt+out, callback=callback)
        if context_details.is_continue:
            out = context_details.previous_chunk + out
        if send_full:
            self.set_message_content(out)
        return out
    
    def generate_with_function_calls(self, context_details: dict, functions: List[Dict[str, Any]], max_answer_length: Optional[int] = None, callback = None) -> List[Dict[str, Any]]:
        """
        Performs text generation with function calls.

        Args:
            context_details (dict): The full prompt (including conditioning, user discussion, extra data, and the user prompt).
            functions (List[Dict[str, Any]]): A list of dictionaries describing functions that can be called.
            max_answer_length (int, optional): Maximum string length allowed for the generated text.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries with the function names and parameters to execute.
        """


        # Upgrade the prompt with information about the function calls.
        upgraded_prompt = self._upgrade_prompt_with_function_info(context_details, functions)

        # Generate the initial text based on the upgraded prompt.
        generated_text = self.fast_gen(upgraded_prompt, max_answer_length, callback=callback)

        if self.config.debug:
            self.print_prompt("Generated", generated_text)

        # Extract the function calls from the generated text.
        function_calls, text_without_code = self.extract_function_calls_as_json(generated_text)

        return generated_text, function_calls, text_without_code


    def generate_with_function_calls_and_images(self, context_details: dict, images:list, functions: List[Dict[str, Any]], max_answer_length: Optional[int] = None, callback = None) -> List[Dict[str, Any]]:
        """
        Performs text generation with function calls.

        Args:
            prompt (str): The full prompt (including conditioning, user discussion, extra data, and the user prompt).
            functions (List[Dict[str, Any]]): A list of dictionaries describing functions that can be called.
            max_answer_length (int, optional): Maximum string length allowed for the generated text.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries with the function names and parameters to execute.
        """
        # Upgrade the prompt with information about the function calls.
        upgraded_prompt = self._upgrade_prompt_with_function_info(context_details, functions)

        # Generate the initial text based on the upgraded prompt.
        generated_text = self.fast_gen_with_images(upgraded_prompt, images, max_answer_length, callback=callback)

        # Extract the function calls from the generated text.
        function_calls, text_without_code = self.extract_function_calls_as_json(generated_text)

        return generated_text, function_calls, text_without_code

    def execute_function(self, code, function_definitions = None):
        function_call = json.loads(code)
        self.execute_function_calls([function_call], function_definitions=function_definitions )

    def execute_function_calls(self, function_calls: List[Dict[str, Any]], function_definitions: List[Dict[str, Any]]) -> List[Any]:
        """
        Executes the function calls with the parameters extracted from the generated text,
        using the original functions list to find the right function to execute.

        Args:
            function_calls (List[Dict[str, Any]]): A list of dictionaries representing the function calls.
            function_definitions (List[Dict[str, Any]]): The original list of functions with their descriptions and callable objects.

        Returns:
            List[Any]: A list of results from executing the function calls.
        """
        if function_definitions is None:
            function_definitions = self.function_definitions
        results = []
        # Convert function_definitions to a dict for easier lookup
        functions_dict = {func['function_name']: func for func in function_definitions}

        for call in function_calls:
            keys = [k for k in call.keys()]
            if not ("function_name" in keys):
                key = keys[0] if len(keys)>0 else None
                d = call[key] if key else None
                function_name = key
                parameters = d
            else:
                function_name = call.get("function_name", None) or call.get("function", None)
                parameters = call.get("function_parameters", None)
            fn =  functions_dict.get(function_name)
            if fn:
                function = fn['function']
                try:
                    # Assuming parameters is a dictionary that maps directly to the function's arguments.
                    if type(parameters)==list:
                        f_parameters ={k:v for k,v in zip([p['name'] for p in fn['function_parameters']],parameters)}
                        result = function(**f_parameters)
                        results.append(result)
                    elif type(parameters)==dict:
                        result = function(**parameters)
                        results.append(result)
                except TypeError as e:
                    trace_exception(e)
                    # Handle cases where the function call fails due to incorrect parameters, etc.
                    results.append(f"Error calling {function_name}: {e}")
            else:
                results.append(f"Function {function_name} not found.")

        return results

    def transform_functions_to_text(self, functions):
        function_texts = []

        for func in functions:
            function_text = f'Function: {func["function_name"]}\nDescription: {func["function_description"]}\nParameters:\n'
            
            for param in func["function_parameters"]:
                param_type = "string" if param["type"] == "str" else param["type"]
                param_description = param.get("description", "")
                function_text += f'  - {param["name"]} ({param_type}): {param_description}\n'
            
            function_texts.append(function_text.strip())
        
        return "\n\n".join(function_texts)
    
    def transform_functions(self, functions):
        tools = []

        for func in functions:
            function_dict = {
                "type": "function",
                "function": {
                    "name": func["function_name"],
                    "description": func["function_description"],
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            }
            
            for param in func["function_parameters"]:
                function_dict["function"]["parameters"]["properties"][param["name"]] = {
                    "type": "string" if param["type"] == "str" else param["type"],
                    "description": param.get("description", ""),
                }
                function_dict["function"]["parameters"]["required"].append(param["name"])
            
            tools.append(function_dict)

        return tools

    def _upgrade_prompt_with_function_info(self, context_details: LollmsContextDetails, functions: List[Dict[str, Any]]) -> str:
        """
        Upgrades the prompt with information about function calls.

        Args:
            context_details (dict): The original prompt.
            functions (List[Dict[str, Any]]): A list of dictionaries describing functions that can be called.

        Returns:
            str: The upgraded prompt that includes information about the function calls.
        """
        tools = self.transform_functions_to_text(functions)
        import copy
        cd = copy.deepcopy(context_details)
        
        function_descriptions = [
                                 self.system_custom_header("Available functions"),
                                 tools,
                                 "",
                                 cd["conditionning"],
                                 "Your objective is interact with the user and if you need to call a function, then use the available functions above and call them using the following json format inside a markdown tag:"
                                 "```function",
                                 "{",
                                 '"function_name":the name of the function to be called,',
                                 '"function_parameters": a list of  parameter values',
                                 "}",
                                 "```",
                                 "It is important to put the function call inside a function markdown tag to be interpreted."
                                 ]


        # Combine the function descriptions with the original prompt.
        function_info = '\n'.join(function_descriptions)

        cd.conditionning=function_info
        upgraded_prompt = cd.build_prompt(self.personality.app.template)

        
        return upgraded_prompt

    def extract_function_calls_as_json(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts function calls formatted as JSON inside markdown code blocks.

        Args:
            text (str): The generated text containing JSON markdown entries for function calls.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the function calls.
        """

        # Extract markdown code blocks that contain JSON.
        code_blocks, text_without_code = self.extract_code_blocks(text, True)

        # Filter out and parse JSON entries.
        function_calls = []
        for block in code_blocks:
            if block["type"]=="function" or block["type"]=="json" or block["type"]=="":
                content = block.get("content", "")
                try:
                    # Attempt to parse the JSON content of the code block.
                    function_call = json.loads(content)
                    if type(function_call)==dict:
                        function_calls.append(function_call)
                    elif type(function_call)==list:
                        function_calls+=function_call
                except json.JSONDecodeError:
                    # If the content is not valid JSON, skip it.
                    continue

        return function_calls, text_without_code


    def interact(
                    self, 
                    context_details:LollmsContextDetails, 
                    callback = None
                    ):
        upgraded_prompt = context_details.build_prompt(self.personality.app.template)
        if len(self.personality.image_files)>0:
            # Generate the initial text based on the upgraded prompt.
            generated_text = self.fast_gen_with_images(upgraded_prompt, self.personality.image_files, callback=callback)
        else:    
            generated_text = self.fast_gen(upgraded_prompt, callback=callback)

        return generated_text

    def interact_with_function_call(
                                        self, 
                                        context_details, 
                                        function_definitions, 
                                        prompt_after_execution=True, 
                                        callback = None, 
                                        hide_function_call=False,
                                        separate_output=False,
                                        max_nested_function_calls=10):

        final_output = ""
        if len(self.personality.image_files)>0:
            out, function_calls, text_without_code = self.generate_with_function_calls_and_images(context_details, self.personality.image_files, function_definitions, callback=callback)
        else:
            out, function_calls, text_without_code = self.generate_with_function_calls(context_details, function_definitions, callback=callback)
        nested_function_calls = 0
        while len(function_calls)>0 and nested_function_calls<max_nested_function_calls:
            nested_function_calls += 1
            self.add_chunk_to_message_content("\n") 
            if hide_function_call:
                self.set_message_content(text_without_code) #Hide function 

            if self.config.debug:
                self.print_prompt("Function calls", json.dumps(function_calls, indent=4))

            outputs = self.execute_function_calls(function_calls,function_definitions)
            final_output = "\n".join([str(o) if type(o)==str else str(o[0]) if (type(o)==tuple or type(0)==list) and len(o)>0 else "" for o in outputs])
            out +=  f"{self.separator_template}"+ self.system_custom_header('function calls results') + final_output + "\n"
            if prompt_after_execution:
                if separate_output:
                    self.set_message_content(final_output)
                    self.new_message("")
                context_details.discussion_messages +=out
                if len(self.personality.image_files)>0:
                    out, function_calls, twc = self.generate_with_function_calls_and_images(context_details, self.personality.image_files, function_definitions, callback=callback)
                else:
                    out, function_calls, twc = self.generate_with_function_calls(context_details, function_definitions, callback=callback)
                final_output += "\n" + out
                text_without_code += twc
        else:
            final_output = out
        return final_output

    #Helper method to convert outputs path to url
    def path2url(self,file):
        file = str(file).replace("\\","/")
        pth = file.split('/')
        idx = pth.index("outputs")
        pth = "/".join(pth[idx:])
        file_path = f"![](/{pth})\n"
        return file_path

    def build_a_document_block(self, title="Title", link="", content="content"):
        if link != "":
            return f'''
<div class="container mx-auto p-4 bg-white rounded-lg shadow-md">
    <h3 class="text-2xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-purple-500">
        <a href="{link}" target="_blank" class="hover:underline">{title}</a>
    </h3>
    <div class="text-sm text-gray-700 whitespace-pre-wrap">{content}</div>
</div>
'''
        else:
            return f'''
<div class="container mx-auto p-4 bg-white rounded-lg shadow-md">
    <h3 class="mb-2">
        <p class="text-xl font-semibold bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-purple-500">{title}</p>
    </h3>
    <div class="text-sm text-gray-700 whitespace-pre-wrap mt-2">{content}</div>
</div>
'''


    def build_a_folder_link(self, folder_path, client: Client, link_text="Open Folder"):
        folder_path = str(folder_path).replace('\\','/')
        return '''
<a href="#" onclick="path=\''''+f'{folder_path}'+'''\';
fetch('/open_folder', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ client_id:''' +f'{client.client_id}'+''', path: path })
    })
    .then(response => response.json())
    .then(data => {
    if (data.status) {
        console.log('Folder opened successfully');
    } else {
        console.error('Error opening folder:', data.error);
    }
    })
    .catch(error => {
    console.error('Error:', error);
    });
">'''+f'''{link_text}</a>'''
    def build_a_file_link(self, file_path, client: Client, link_text="Open Folder"):
        file_path = str(file_path).replace('\\','/')
        return '''
<a href="#" onclick="path=\''''+f'{file_path}'+'''\';
fetch('/open_file', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ client_id:''' +f'{client.client_id}'+''', path: path })
    })
    .then(response => response.json())
    .then(data => {
    if (data.status) {
        console.log('Folder opened successfully');
    } else {
        console.error('Error opening folder:', data.error);
    }
    })
    .catch(error => {
    console.error('Error:', error);
    });
">'''+f'''{link_text}</a>'''
    
# ===========================================================
    # Basic message element (already provided)
    def build_message_element(self, element_text):
        return f"""
<div class="max-w-md mx-auto my-2">
    <div class="bg-red-500 text-white rounded-lg py-2 px-4 inline-block shadow-md">
        {element_text}
    </div>
</div>
"""

    # Message with thinking animation (already updated)
    def build_message_element_with_thinking_animation(self, element_text):
        return f"""
<div class="max-w-md mx-auto my-2">
    <div class="bg-red-500 text-white rounded-lg py-2 px-4 inline-block shadow-md flex items-center space-x-2">
        <span>{element_text}</span>
        <div class="flex space-x-1">
            <div class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 0s;"></div>
            <div class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 0.2s;"></div>
            <div class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 0.4s;"></div>
        </div>
    </div>
</div>
"""

    # Message with emoji (e.g., smiley for completion)
    def build_message_element_with_emoji(self, element_text, emoji="😊"):
        return f"""
<div class="max-w-md mx-auto my-2">
    <div class="bg-red-500 text-white rounded-lg py-2 px-4 inline-block shadow-md flex items-center space-x-2">
        <span>{element_text}</span>
        <span class="text-xl">{emoji}</span>
    </div>
</div>
"""

    # Success message with checkmark
    def build_success_message(self, element_text):
        return f"""
<div class="max-w-md mx-auto my-2">
    <div class="bg-green-500 text-white rounded-lg py-2 px-4 inline-block shadow-md flex items-center space-x-2">
        <span class="text-xl">✓</span>
        <span>{element_text}</span>
    </div>
</div>
"""

    # Warning message with alert icon
    def build_warning_message(self, element_text):
        return f"""
<div class="max-w-md mx-auto my-2">
    <div class="bg-yellow-500 text-white rounded-lg py-2 px-4 inline-block shadow-md flex items-center space-x-2">
        <span class="text-xl">⚠️</span>
        <span>{element_text}</span>
    </div>
</div>
"""

    # Error message with cross
    def build_error_message(self, element_text):
        return f"""
<div class="max-w-md mx-auto my-2">
    <div class="bg-red-600 text-white rounded-lg py-2 px-4 inline-block shadow-md flex items-center space-x-2">
        <span class="text-xl">✗</span>
        <span>{element_text}</span>
    </div>
</div>
"""

    # Progress message with spinning animation
    def build_progress_message(self, element_text):
        return f"""
<div class="max-w-md mx-auto my-2">
    <div class="bg-blue-500 text-white rounded-lg py-2 px-4 inline-block shadow-md flex items-center space-x-2">
        <span>{element_text}</span>
        <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
    </div>
</div>
"""

    # Info message with light bulb
    def build_info_message(self, element_text):
        return f"""
<div class="max-w-md mx-auto my-2">
    <div class="bg-blue-400 text-white rounded-lg py-2 px-4 inline-block shadow-md flex items-center space-x-2">
        <span class="text-xl">💡</span>
        <span>{element_text}</span>
    </div>
</div>
"""
    
    def build_progressbar_message(self, element_text, progress_percentage=50):
        return f"""
<div class="max-w-md mx-auto my-2">
    <div class="bg-blue-500 text-white rounded-lg py-2 px-4 shadow-md">
        <div class="flex items-center space-x-2 mb-2">
            <span>{element_text}</span>
        </div>
        <div class="w-full bg-blue-300 rounded-full h-2.5">
            <div class="bg-white h-2.5 rounded-full transition-all duration-500 ease-in-out" 
                 style="width: {progress_percentage}%"></div>
        </div>
    </div>
</div>
"""
# ===========================================================
    def compress_js(self, code):
        return compress_js(code)
    def compress_python(self, code):
        return compress_python(code)
    def compress_html(self, code):
        return compress_html(code)




# ===========================================================
    def select_model(self, binding_name, model_name):
        self.personality.app.select_model(binding_name, model_name)
    def verify_rag_entry(self, query, rag_entry):
        return self.yes_no("Are there any useful information in the document chunk that can be used to answer the query?", self.app.system_custom_header("Query")+query+"\n"+self.app.system_custom_header("document chunk")+"\n"+rag_entry)
    # Properties ===============================================
    @property
    def start_header_id_template(self) -> str:
        """Get the start_header_id_template."""
        return self.config.start_header_id_template

    @property
    def end_header_id_template(self) -> str:
        """Get the end_header_id_template."""
        return self.config.end_header_id_template
    
    @property
    def system_message_template(self) -> str:
        """Get the system_message_template."""
        return self.config.system_message_template


    @property
    def separator_template(self) -> str:
        """Get the separator template."""
        return self.config.separator_template


    @property
    def start_user_header_id_template(self) -> str:
        """Get the start_user_header_id_template."""
        return self.config.start_user_header_id_template
    @property
    def end_user_header_id_template(self) -> str:
        """Get the end_user_header_id_template."""
        return self.config.end_user_header_id_template
    @property
    def end_user_message_id_template(self) -> str:
        """Get the end_user_message_id_template."""
        return self.config.end_user_message_id_template




    @property
    def start_ai_header_id_template(self) -> str:
        """Get the start_ai_header_id_template."""
        return self.config.start_ai_header_id_template
    @property
    def end_ai_header_id_template(self) -> str:
        """Get the end_ai_header_id_template."""
        return self.config.end_ai_header_id_template
    @property
    def end_ai_message_id_template(self) -> str:
        """Get the end_ai_message_id_template."""
        return self.config.end_ai_message_id_template
    @property
    def system_full_header(self) -> str:
        """Get the start_header_id_template."""
        return f"{self.start_header_id_template}{self.system_message_template}{self.end_header_id_template}"
    @property
    def user_full_header(self) -> str:
        """Get the start_header_id_template."""
        if self.config.use_user_name_in_discussions:
            return f"{self.start_user_header_id_template}{self.config.user_name}{self.end_user_header_id_template}"
        else:
            return f"{self.start_user_header_id_template}user{self.end_user_header_id_template}"
    @property
    def ai_full_header(self) -> str:
        """Get the start_header_id_template."""
        if self.config.use_user_name_in_discussions:
            return f"{self.start_ai_header_id_template}{self.personality.name}{self.end_ai_header_id_template}"
        else:
            return f"{self.start_ai_header_id_template}assistant{self.end_ai_header_id_template}"

    def system_custom_header(self, system_header) -> str:
        """Get the start_header_id_template."""
        return f"{self.start_header_id_template}{system_header}{self.end_user_header_id_template}"

    def user_custom_header(self, ai_name) -> str:
        """Get the start_header_id_template."""
        return f"{self.start_user_header_id_template}{ai_name}{self.end_user_header_id_template}"

    def ai_custom_header(self, ai_name) -> str:
        """Get the start_header_id_template."""
        return f"{self.start_ai_header_id_template}{ai_name}{self.end_ai_header_id_template}"


class AIPersonalityInstaller:
    def __init__(self, personality:AIPersonality) -> None:
        self.personality = personality


class PersonalityBuilder:
    def __init__(
                    self,
                    lollms_paths:LollmsPaths,
                    config:LOLLMSConfig,
                    model:LLMBinding,
                    app=None,
                    installation_option:InstallOption=InstallOption.INSTALL_IF_NECESSARY,
                    callback=None
                ):
        self.config = config
        self.lollms_paths = lollms_paths
        self.model = model
        self.app = app
        self.installation_option = installation_option
        self.callback = callback


    def build_personality(self, id:int=None):
        if id is None:
            id = self.config["active_personality_id"]
            if self.config["active_personality_id"]>=len(self.config["personalities"]):
                ASCIIColors.warning("Personality ID was out of range. Resetting to 0.")
                self.config["active_personality_id"]=0
                id = 0
        else:
            if id>len(self.config["personalities"]):
                id = len(self.config["personalities"])-1

        personality_folder = self.config["personalities"][id]

        if len(self.config["personalities"][id].split("/"))==2:
            self.personality = AIPersonality(
                                            personality_folder,
                                            self.lollms_paths,
                                            self.config,
                                            self.model,
                                            app=self.app,
                                            selected_language=self.config.current_language,
                                            installation_option=self.installation_option,
                                            callback=self.callback
                                        )
        else:
            self.personality = AIPersonality(
                                            personality_folder,
                                            self.lollms_paths,
                                            self.config,
                                            self.model,
                                            app=self.app,
                                            is_relative_path=False,
                                            selected_language=self.config.current_language,
                                            installation_option=self.installation_option,
                                            callback=self.callback
                                        )
        return self.personality

    def get_personality(self):
        return self.personality

    def extract_function_call(self, query):
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


