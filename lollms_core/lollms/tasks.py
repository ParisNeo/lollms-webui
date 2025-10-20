
import sys
from typing import Callable, Any, List, Dict, Any, Optional
from functools import partial
from datetime import datetime
from ascii_colors import ASCIIColors
from lollms.types import MSG_OPERATION_TYPE, SUMMARY_MODE
from lollms.com import LoLLMsCom
from lollms.utilities import PromptReshaper, remove_text_from_string, process_ai_output

import hashlib
import json
class TasksLibrary:
    def __init__(self, lollms:LoLLMsCom, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None) -> None:
        self.lollms = lollms
        self.config = lollms.config
        self.callback = callback
        self.anti_prompts = [lollms.config.discussion_prompt_separator]
        if lollms.config.separator_template!="\n":
            self.anti_prompts.append(lollms.config.separator_template)

    def print_prompt(self, title, prompt):
        ASCIIColors.red("*-*-*-*-*-*-*-* ", end="")
        ASCIIColors.red(title, end="")
        ASCIIColors.red(" *-*-*-*-*-*-*-*")
        ASCIIColors.yellow(prompt)
        ASCIIColors.red(" *-*-*-*-*-*-*-*")
        
    def sink(self, s=None,i=None,d=None):
        pass
    def detect_antiprompt(self, text:str) -> bool:
        """
        Detects if any of the antiprompts in self.anti_prompts are present in the given text.
        Used for the Hallucination suppression system

        Args:
            text (str): The text to check for antiprompts.

        Returns:
            bool: True if any antiprompt is found in the text (ignoring case), False otherwise.
        """
        for prompt in self.anti_prompts:
            if prompt.lower() in text.lower():
                return prompt.lower()
        return None

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
        
    def generate(self, prompt, max_size= None, temperature = None, top_k = None, top_p=None, repeat_penalty=None, repeat_last_n=None, callback=None, debug=False, show_progress=False ):
        ASCIIColors.info("Text generation started: Warming up")
        self.nb_received_tokens = 0
        self.bot_says = ""
        if debug:
            self.print_prompt("gen",prompt)
        ntokens = len(self.lollms.model.tokenize(prompt))
        self.lollms.model.generate(
                                prompt,
                                max_size if max_size else min(self.lollms.config.ctx_size-ntokens,self.lollms.config.max_n_predict),
                                partial(self.process, callback=callback, show_progress=show_progress),
                                temperature= temperature if temperature is not None else self.lollms.config.temperature if self.lollms.config.override_personality_model_parameters else self.lollms.personality.model_temperature,
                                top_k= top_k if top_k is not None else self.lollms.config.top_k if self.lollms.config.override_personality_model_parameters else self.lollms.personality.model_top_k,
                                top_p= top_p if top_p is not None else self.lollms.config.top_p if self.lollms.config.override_personality_model_parameters else self.lollms.personality.model_top_p,
                                repeat_penalty= repeat_penalty if repeat_penalty is not None else self.lollms.config.repeat_penalty if self.lollms.config.override_personality_model_parameters else self.lollms.personality.model_repeat_penalty,
                                repeat_last_n= repeat_last_n if repeat_last_n is not None else self.lollms.config.repeat_last_n if self.lollms.config.override_personality_model_parameters else self.lollms.personality.model_repeat_last_n,
                                ).strip()
        return self.bot_says

    def generate_with_images(self, prompt, images, max_size, temperature = None, top_k = None, top_p=None, repeat_penalty=None, repeat_last_n=None, callback=None, debug=False, show_progress=False ):
        ASCIIColors.info("Text generation started: Warming up")
        self.nb_received_tokens = 0
        self.bot_says = ""
        if debug:
            self.print_prompt("gen",prompt)

        self.lollms.model.generate_with_images(
                                prompt,
                                images,
                                max_size,
                                partial(self.process, callback=callback, show_progress=show_progress),
                                temperature=self.lollms.config.model_temperature if temperature is None else temperature,
                                top_k=self.lollms.config.model_top_k if top_k is None else top_k,
                                top_p=self.lollms.config.model_top_p if top_p is None else top_p,
                                repeat_penalty=self.lollms.config.model_repeat_penalty if repeat_penalty is None else repeat_penalty,
                                repeat_last_n = self.lollms.config.model_repeat_last_n if repeat_last_n is None else repeat_last_n
                                ).strip()
        return self.bot_says

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
        pr = PromptReshaper(prompt)
        prompt = pr.build(placeholders,
                        self.lollms.model.tokenize,
                        self.lollms.model.detokenize,
                        (self.lollms.model.config.ctx_size - max_generation_size) if max_generation_size is not None else (self.lollms.model.config.ctx_size - 1024),
                        sacrifice
                        )
        # TODO : add show progress
        gen = self.generate(prompt, max_generation_size, temperature = temperature, top_k = top_k, top_p=top_p, repeat_penalty=repeat_penalty, repeat_last_n=repeat_last_n, callback=callback, show_progress=show_progress).strip().replace("</s>", "").replace("<s>", "")
        if debug:
            self.print_prompt("prompt", prompt+gen)

        return gen
    
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
        separator_template          = self.config.separator_template
        prompt = "\n".join([
            f"{start_header_id_template}{system_message_template}{end_header_id_template}I am an AI assistant that can converse and analyze images. When asked to locate something in an image you send, I will reply with:",
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
            debug = self.lollms.config.debug

        if max_generation_size is None:
            prompt_size = self.lollms.model.tokenize(prompt)
            max_generation_size = self.lollms.model.config.ctx_size - len(prompt_size)

        pr = PromptReshaper(prompt)
        prompt = pr.build(placeholders,
                        self.lollms.model.tokenize,
                        self.lollms.model.detokenize,
                        self.lollms.model.config.ctx_size - max_generation_size,
                        sacrifice
                        )
        ntk = len(self.lollms.model.tokenize(prompt))
        max_generation_size = min(self.lollms.model.config.ctx_size - ntk, max_generation_size)
        # TODO : add show progress

        gen = self.generate_with_images(prompt, images, max_generation_size, callback=callback, show_progress=show_progress).strip().replace("</s>", "").replace("<s>", "")
        try:
            gen = process_ai_output(gen, images, "/discussions/")
        except Exception as ex:
            pass
        if debug:
            self.print_prompt("prompt", prompt+gen)

        return gen    
    
    # Communications with the user
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

    def info(self, info:str, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None):
        """This sends exception to the client

        Args:
            inf (str): The information to be sent
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
            callback(info, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_INFO)

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
            callback("", MSG_OPERATION_TYPE.MSG_TYPE_JSON_INFOS, metadata = [{"title":title, "content":json.dumps(json_infos, indent=indent)}])

    def set_message_html(self, html_ui:str, callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool]=None):
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





    def extract_code_blocks(self, text: str) -> List[dict]:
        """
        This function extracts code blocks from a given text.

        Parameters:
        text (str): The text from which to extract code blocks. Code blocks are identified by triple backticks (```).

        Returns:
        List[dict]: A list of dictionaries where each dictionary represents a code block and contains the following keys:
            - 'index' (int): The index of the code block in the text.
            - 'file_name' (str): An empty string. This field is not used in the current implementation.
            - 'content' (str): The content of the code block.
            - 'type' (str): The type of the code block. If the code block starts with a language specifier (like 'python' or 'java'), this field will contain that specifier. Otherwise, it will be set to 'language-specific'.

        Note:
        The function assumes that the number of triple backticks in the text is even.
        If the number of triple backticks is odd, it will consider the rest of the text as the last code block.
        """        
        remaining = text
        bloc_index = 0
        first_index=0
        indices = []
        while len(remaining)>0:
            try:
                index = remaining.index("```")
                indices.append(index+first_index)
                remaining = remaining[index+3:]
                first_index += index+3
                bloc_index +=1
            except Exception as ex:
                if bloc_index%2==1:
                    index=len(remaining)
                    indices.append(index)
                remaining = ""

        code_blocks = []
        is_start = True
        for index, code_delimiter_position in enumerate(indices):
            block_infos = {
                'index':index,
                'file_name': "",
                'content': "",
                'type':""
            }
            if is_start:

                sub_text = text[code_delimiter_position+3:]
                if len(sub_text)>0:
                    try:
                        find_space = sub_text.index(" ")
                    except:
                        find_space = int(1e10)
                    try:
                        find_return = sub_text.index("\n")
                    except:
                        find_return = int(1e10)
                    next_index = min(find_return, find_space)
                    start_pos = next_index
                    if code_delimiter_position+3<len(text) and text[code_delimiter_position+3] in ["\n"," ","\t"] :
                        # No
                        block_infos["type"]='language-specific'
                    else:
                        block_infos["type"]=sub_text[:next_index]

                    next_pos = indices[index+1]-code_delimiter_position
                    if sub_text[next_pos-3]=="`":
                        block_infos["content"]=sub_text[start_pos:next_pos-3].strip()
                    else:
                        block_infos["content"]=sub_text[start_pos:next_pos].strip()
                    code_blocks.append(block_infos)
                is_start = False
            else:
                is_start = True
                continue

        return code_blocks

    def translate_conditionning(self, prompt, original_language, language):
        conditionning_translation_text = f"{self.lollms.system_full_header}Translate the following prompt to {language}.\n{self.lollms.separator_template}{self.lollms.ai_custom_header('prompt')}\n```{original_language}\n{prompt}\n```\nPut the answer inside a {language} markdown tag like this:\n```{language}\nTranslated text\n```\n{self.lollms.ai_custom_header('translation')}"
        cond_translation = self.fast_gen(conditionning_translation_text, temperature=0.1, callback=self.sink)
        response = self.extract_code_blocks(cond_translation)
        if len(response)>0 and len(response[0]["content"])>0:
            conditionning = response[0]["content"]
        else:
            ASCIIColors.print(f"Failed to translate the conditionning message. Reverting to english conditionning with a request to use the lanuage {language}")
            conditionning = prompt + f"\nAlways answer in {language}\n"
        return conditionning

    def translate_message(self, prompt, original_language, language):
        start_header_id_template    = self.config.start_header_id_template
        end_header_id_template      = self.config.end_header_id_template
        system_message_template     = self.config.system_message_template
        separator_template          = self.config.separator_template        
        message_translation_text = f"{start_header_id_template}{system_message_template}{end_header_id_template}Translate the following message to {language}.\nDo not translate any css or code, just the text and strings.{separator_template}{start_header_id_template}prompt:\n```{original_language}\n{prompt.replace(f'{start_header_id_template}','')}\n```{separator_template}{start_header_id_template}translation{end_header_id_template}\n```{language}\n"
        cond_translation = f"```{language}\n"+self.fast_gen(message_translation_text, temperature=0.1, callback=self.sink)
        response = self.extract_code_blocks(cond_translation)
        if len(response)>0 and len(response[0]["content"])>0:
            translated = response[0]["content"]
        else:
            ASCIIColors.print(f"Failed to translate the message. Reverting to english conditionning with a request to use the lanuage {language}")
            message_translation_text = f"{start_header_id_template}{system_message_template}{end_header_id_template}Translate the following message to {language}.\nDo not translate any css or code, just the text and strings.{separator_template}{start_header_id_template}message{end_header_id_template}\n{prompt.replace(f'{start_header_id_template}','')}{separator_template}{start_header_id_template}translation{end_header_id_template}\n"
            translated = self.fast_gen(message_translation_text, temperature=0.1, callback=self.sink)
        return translated

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
        depth=0
        tk = self.lollms.model.tokenize(text)
        prev_len = len(tk)
        document_chunks=None
        while len(tk)>max_summary_size and (document_chunks is None or len(document_chunks)>1):
            self.step_start(f"Comprerssing {doc_name}... [depth {depth+1}]")
            chunk_size = int(self.lollms.config.ctx_size*0.6)
            tc = TextChunker(chunk_size, 0, model= self.lollms.model)
            hasher = hashlib.md5()
            hasher.update(text.encode("utf8"))
            
            document_chunks = tc.get_text_chunks(text, Document(hasher.hexdigest(), doc_name, doc_name ) )
            text = self.summarize_chunks(
                                            document_chunks,
                                            summary_instruction, 
                                            doc_name, 
                                            answer_start, 
                                            max_generation_size, 
                                            callback, 
                                            chunk_summary_post_processing=chunk_summary_post_processing,
                                            summary_mode=summary_mode)
            tk = self.lollms.model.tokenize(text)
            dtk_ln=prev_len-len(tk)
            prev_len = len(tk)
            self.step(f"Current text size : {prev_len}, max summary size : {max_summary_size}")
            self.step_end(f"Comprerssing {doc_name}... [depth {depth+1}]")
            depth += 1
            if dtk_ln<=10: # it is not sumlmarizing
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
        tk = self.lollms.model.tokenize(text)
        prev_len = len(tk)
        while len(tk)>max_summary_size:
            chunk_size = int(self.lollms.config.ctx_size*0.6)
            tc = TextChunker(chunk_size, 0, None, self.lollms.model)
            document_chunks = tc.get_text_chunks(text,Document("","","",0),True)
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
            tk = self.lollms.model.tokenize(text)
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
        separator_template          = self.config.separator_template        
        if summary_mode==SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL:
            summary = ""
            for i, chunk in enumerate(chunks):
                self.step_start(f" Summary of {doc_name} - Processing chunk : {i+1}/{len(chunks)}")
                if summary !="":
                    summary = f"{answer_start}"+ self.fast_gen(
                                "\n".join([
                                    f"{start_header_id_template}Document_chunk: {doc_name}{end_header_id_template}",
                                    f"This is a cumulative summary step. Use the summary of the previous chunks and the current chunk of the document to make a new summary integrating information from both. Make sure not to loose information from previous summaries",
                                    f"Summary of previous chunks",
                                    f"{summary}",
                                    f"current chunk:",
                                    f"{chunk}",
                                    f"{start_header_id_template}{system_message_template}{end_header_id_template}{summary_instruction}",
                                    f"The summary should extract required information from the current chunk to increment the previous summary.",
                                    f"Answer directly with the cumulative summary with no extra comments.",
                                    f"{start_header_id_template}cumulative summary{end_header_id_template}",
                                    f"{answer_start}"
                                    ]),
                                    max_generation_size=max_generation_size,
                                    callback=callback)
                else:
                    summary = f"{answer_start}"+ self.fast_gen(
                                "\n".join([
                                    f"{start_header_id_template}Document_chunk: {doc_name}{end_header_id_template}",
                                    f"current chunk:",
                                    f"{chunk}",
                                    f"{start_header_id_template}{system_message_template}{end_header_id_template}{summary_instruction}",
                                    f"Answer without any extra comments.",
                                    f"{start_header_id_template}chunk summary{end_header_id_template}",
                                    f"{answer_start}"
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
        separator_template          = self.config.separator_template
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
                            f"{start_header_id_template}summary{end_header_id_template}:",
                            f"{answer_start}"
                            ]),
                            max_generation_size=max_generation_size,
                            callback=callback)
            if chunk_summary_post_processing:
                summary = chunk_summary_post_processing(summary)
            summeries.append(summary)
            self.step_end(f" Summary of {doc_name} - Processing chunk : {i+1}/{len(chunks)}")
        return "\n".join(summeries)

    #======================= Function calls
    def _upgrade_prompt_with_function_info(self, prompt: str, functions: List[Dict[str, Any]]) -> str:
        """
        Upgrades the prompt with information about function calls.

        Args:
            prompt (str): The original prompt.
            functions (List[Dict[str, Any]]): A list of dictionaries describing functions that can be called.

        Returns:
            str: The upgraded prompt that includes information about the function calls.
        """
        start_header_id_template    = self.config.start_header_id_template
        end_header_id_template      = self.config.end_header_id_template
        system_message_template     = self.config.system_message_template
        separator_template          = self.config.separator_template
        function_descriptions = [f"{start_header_id_template}information{end_header_id_template}If you need to call a function to fulfill the user request, use a function markdown tag with the function call as the following json format:",
                                 "```function",
                                 "{",
                                 '"function_name":the name of the function to be called,',
                                 '"function_parameters": a list of  parameter values',
                                 "}",
                                 "```",
                                 "You can call multiple functions in one generation.",
                                 "Each function call needs to be in a separate function markdown tag.",
                                 "Do not add status of the execution as it will be added automatically by the system.",
                                 f"{start_header_id_template}List of possible functions to be called{end_header_id_template}\n"]
        for function in functions:
            description = f"{function['function_name']}: {function['function_description']}\nparameters:{function['function_parameters']}"
            function_descriptions.append(description)

        # Combine the function descriptions with the original prompt.
        function_info = ' '.join(function_descriptions)
        upgraded_prompt = f"{function_info}\n{prompt}"

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
        code_blocks = self.extract_code_blocks(text)

        # Filter out and parse JSON entries.
        function_calls = []
        for block in code_blocks:
            if block["type"]=="function":
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

        return function_calls    
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
        results = []
        # Convert function_definitions to a dict for easier lookup
        functions_dict = {func['function_name']: func['function'] for func in function_definitions}

        for call in function_calls:
            function_name = call.get("function_name")
            parameters = call.get("function_parameters", [])
            function = functions_dict.get(function_name)

            if function:
                try:
                    # Assuming parameters is a dictionary that maps directly to the function's arguments.
                    if type(parameters)==list:
                        result = function(*parameters)
                    elif type(parameters)==dict:
                        result = function(**parameters)
                    results.append(result)
                except TypeError as e:
                    # Handle cases where the function call fails due to incorrect parameters, etc.
                    results.append(f"Error calling {function_name}: {e}")
            else:
                results.append(f"Function {function_name} not found.")

        return results
    def generate_with_function_calls(self, prompt: str, functions: List[Dict[str, Any]], max_answer_length: Optional[int] = None) -> List[Dict[str, Any]]:
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
        upgraded_prompt = self._upgrade_prompt_with_function_info(prompt, functions)

        # Generate the initial text based on the upgraded prompt.
        generated_text = self.fast_gen(upgraded_prompt, max_answer_length)

        # Extract the function calls from the generated text.
        function_calls = self.extract_function_calls_as_json(generated_text)

        return generated_text, function_calls

    def generate_with_function_calls_and_images(self, prompt: str, images:list, functions: List[Dict[str, Any]], max_answer_length: Optional[int] = None) -> List[Dict[str, Any]]:
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
        upgraded_prompt = self._upgrade_prompt_with_function_info(prompt, functions)

        # Generate the initial text based on the upgraded prompt.
        generated_text = self.fast_gen_with_images(upgraded_prompt, images, max_answer_length)

        # Extract the function calls from the generated text.
        function_calls = self.extract_function_calls_as_json(generated_text)

        return generated_text, function_calls
