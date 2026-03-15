"""
project: lollms
file: lollms_generator.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes are specific to the generation process

"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from lollms.server.elf_server import LOLLMSElfServer
from pydantic import BaseModel, ConfigDict
from starlette.responses import StreamingResponse
from lollms.types import MSG_OPERATION_TYPE
from lollms.utilities import detect_antiprompt, remove_text_from_string, trace_exception
from lollms.generation import RECEPTION_MANAGER, ROLE_CHANGE_DECISION, ROLE_CHANGE_OURTPUT
from ascii_colors import ASCIIColors
import time
import re
import threading
from typing import List, Optional, Union
import random
import string
import json
from enum import Enum
import base64
from datetime import datetime
import pipmaster as pm

def _generate_id(length=10):
    letters_and_digits = string.ascii_letters + string.digits
    random_id = ''.join(random.choice(letters_and_digits) for _ in range(length))
    return random_id

# ----------------------- Defining router and main class ------------------------------

router = APIRouter()
elf_server = LOLLMSElfServer.get_instance()


# ----------------------------------- Generation status -----------------------------------------

@router.get("/get_generation_status")
def get_generation_status():
    return {"status":elf_server.busy}


# ----------------------------------- Generation -----------------------------------------
class LollmsTokenizeRequest(BaseModel):
    prompt: str
    return_named: bool = False
class LollmsDeTokenizeRequest(BaseModel):
    tokens: List[int]
    return_named: bool = False

@router.post("/lollms_tokenize")
async def lollms_tokenize(request: LollmsTokenizeRequest):
    try:
        tokens = elf_server.model.tokenize(request.prompt)
        if request.return_named:
            named_tokens=[]
            for token in tokens:
                detoken = elf_server.model.detokenize([token])
                named_tokens.append([detoken,token])
            return named_tokens
        else:
            return tokens
    except Exception as ex:
        return {"status":False,"error":str(ex)}

@router.post("/lollms_detokenize")
async def lollms_detokenize(request: LollmsDeTokenizeRequest):
    text = elf_server.model.detokenize(request.tokens)
    if request.return_named:
        named_tokens=[]
        for token in request.tokens:
            detoken = elf_server.model.detokenize([token])
            named_tokens.append([detoken,token])
        return named_tokens
    else:
        return text

class LollmsGenerateRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    prompt: str
    model_name: Optional[str] = None
    personality: Optional[int] = -1
    n_predict: Optional[int] = None
    stream: bool = False
    temperature: float = 0.7
    top_k: Optional[int] = 40
    top_p: Optional[float] = 0.9
    repeat_penalty: Optional[float] = 1.1
    repeat_last_n: Optional[int] = 40
    seed: Optional[int] = None
    n_threads: Optional[int] = 8

@router.post("/lollms_generate")
async def lollms_generate(request: LollmsGenerateRequest):
    """ Endpoint for generating text from prompts using the LoLLMs fastAPI server.

    Args:
    Data model for the Generate Request.
    Attributes:
    - prompt: str : representing the input text prompt for text generation.
    - model_name: Optional[str] = None : The name of the model to be used (it should be one of the current models)
    - personality : Optional[int] = None : The name of the mounted personality to be used (if a personality is None, the endpoint will just return a completion text). To get the list of mounted personalities, just use /list_mounted_personalities
    - n_predict: int representing the number of predictions to generate.
    - stream: bool indicating whether to stream the generated text or not.
    - temperature: float representing the temperature parameter for text generation.
    - top_k: int representing the top_k parameter for text generation.
    - top_p: float representing the top_p parameter for text generation.
    - repeat_penalty: float representing the repeat_penalty parameter for text generation.
    - repeat_last_n: int representing the repeat_last_n parameter for text generation.
    - seed: int representing the seed for text generation.
    - n_threads: int representing the number of threads for text generation.

    Returns:
    - If the elf_server binding is not None:
    - If stream is True, returns a StreamingResponse of generated text chunks.
    - If stream is False, returns the generated text as a string.
    - If the elf_server binding is None, returns None.
    """

    try:
        headers = { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive',}
        reception_manager=RECEPTION_MANAGER()
        prompt = request.prompt
        if elf_server.config.debug:
            ASCIIColors.yellow(prompt)
        tokens = elf_server.model.tokenize(prompt)
        n_tokens = len(tokens)
        ASCIIColors.info(f"Prompt input size {n_tokens}")        
        if request.n_predict is None:
            n_predict = min(elf_server.config.ctx_size-n_tokens-1,elf_server.config.max_n_predict if elf_server.config.max_n_predict else elf_server.config.ctx_size)
        else:
            n_predict = min(min(elf_server.config.ctx_size-n_tokens-1,elf_server.config.max_n_predict if elf_server.config.max_n_predict else elf_server.config.ctx_size), request.n_predict) if request.n_predict>0 else min(elf_server.config.ctx_size-n_tokens-1,elf_server.config.max_n_predict if elf_server.config.max_n_predict else elf_server.config.ctx_size)
        stream = request.stream
        if elf_server.binding is not None:
            if stream:
                new_output={"new_values":[]}
                async def generate_chunks():
                    lk = threading.Lock()

                    def callback(chunk, chunk_type:MSG_OPERATION_TYPE=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK):
                        if elf_server.cancel_gen:
                            return False
                        
                        if chunk is None:
                            return

                        rx = reception_manager.new_chunk(chunk)
                        if rx.status!=ROLE_CHANGE_DECISION.MOVE_ON:
                            if rx.status==ROLE_CHANGE_DECISION.PROGRESSING:
                                return True
                            elif rx.status==ROLE_CHANGE_DECISION.ROLE_CHANGED:
                                return False
                            else:
                                chunk = chunk + rx.value

                        # Yield each chunk of data
                        lk.acquire()
                        try:
                            new_output["new_values"].append(reception_manager.chunk)
                            lk.release()
                            return True
                        except Exception as ex:
                            trace_exception(ex)
                            lk.release()
                            return False
                        
                    def chunks_builder():
                        if request.model_name in elf_server.binding.list_models() and elf_server.binding.model_name!=request.model_name:
                            elf_server.binding.build_model(request.model_name)    

                        elf_server.binding.generate(
                                                prompt, 
                                                n_predict, 
                                                callback=callback, 
                                                temperature=request.temperature or elf_server.config.temperature,
                                                top_k=request.top_k or elf_server.config.top_k,
                                                top_p=request.top_p or elf_server.config.top_p,
                                                repeat_penalty=request.repeat_penalty or elf_server.config.repeat_penalty,
                                                repeat_last_n=request.repeat_last_n or elf_server.config.repeat_last_n,
                                            )
                        reception_manager.done = True
                    thread = threading.Thread(target=chunks_builder)
                    thread.start()
                    current_index = 0
                    while (not reception_manager.done and elf_server.cancel_gen == False):
                        while (not reception_manager.done and len(new_output["new_values"])==0):
                            time.sleep(0.001)
                        lk.acquire()
                        for i in range(len(new_output["new_values"])):
                            current_index += 1                        
                            yield (new_output["new_values"][i])
                        new_output["new_values"]=[]
                        lk.release()
                    elf_server.cancel_gen = False         
                return StreamingResponse(generate_chunks(), media_type="text/plain", headers=headers)
            else:
                def callback(chunk, chunk_type:MSG_OPERATION_TYPE=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK):
                    # Yield each chunk of data
                    if chunk is None:
                        return True
                    reception_manager.reception_buffer += chunk
                    antiprompt = elf_server.personality.detect_antiprompt(reception_manager.reception_buffer)
                    if antiprompt:
                        ASCIIColors.warning(f"\n{antiprompt} detected. Stopping generation")
                        reception_manager.reception_buffer = elf_server.remove_text_from_string(reception_manager.reception_buffer,antiprompt)
                        return False


                    return True
                
                elf_server.binding.generate(
                                                prompt, 
                                                n_predict, 
                                                callback=callback,
                                                temperature=request.temperature or elf_server.config.temperature
                                            )
                completion_tokens = len(elf_server.binding.tokenize(reception_manager.reception_buffer))
                ASCIIColors.yellow(f"Generated: {completion_tokens} tokens")
                if elf_server.config.debug:
                    ASCIIColors.yellow("Output")        
                    ASCIIColors.yellow(reception_manager.reception_buffer)        

                return PlainTextResponse(reception_manager.reception_buffer)
        else:
            return None
    except Exception as ex:
        trace_exception(ex)
        elf_server.error(ex)
        return {"status":False,"error":str(ex)}

class LollmsEmbed(BaseModel):
    text:str

@router.post("/lollms_embed")
async def lollms_embed(request: LollmsEmbed):
    if not pm.is_installed ("safe_store"):
        pm.install("safe_store")
    from safe_store import SafeStore


    vdb = SafeStore("")       

    vector = vdb.vectorizer.vectorize([request.text])
    return {"vector":vector[0].tolist()}

class LollmsGenerateRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())    
    prompt: str
    images: List[str]
    model_name: Optional[str] = None
    personality: Optional[int] = -1
    n_predict: Optional[int] = 1024
    stream: bool = False
    temperature: float = 0.7
    top_k: Optional[int] = 40
    top_p: Optional[float] = 0.9
    repeat_penalty: Optional[float] = 1.1
    repeat_last_n: Optional[int] = 40
    seed: Optional[int] = None
    n_threads: Optional[int] = 8

@router.post("/lollms_generate_with_images")
async def lollms_generate_with_images(request: LollmsGenerateRequest):
    """ Endpoint for generating text from prompts using the LoLLMs fastAPI server.

    Args:
    Data model for the Generate with images Request.
    Attributes:
    - prompt: str : representing the input text prompt for text generation.
    - images: str : a list of 64 bits encoded images
    - model_name: Optional[str] = None : The name of the model to be used (it should be one of the current models)
    - personality : Optional[int] = None : The name of the mounted personality to be used (if a personality is None, the endpoint will just return a completion text). To get the list of mounted personalities, just use /list_mounted_personalities
    - n_predict: int representing the number of predictions to generate.
    - stream: bool indicating whether to stream the generated text or not.
    - temperature: float representing the temperature parameter for text generation.
    - top_k: int representing the top_k parameter for text generation.
    - top_p: float representing the top_p parameter for text generation.
    - repeat_penalty: float representing the repeat_penalty parameter for text generation.
    - repeat_last_n: int representing the repeat_last_n parameter for text generation.
    - seed: int representing the seed for text generation.
    - n_threads: int representing the number of threads for text generation.

    Returns:
    - If the elf_server binding is not None:
    - If stream is True, returns a StreamingResponse of generated text chunks.
    - If stream is False, returns the generated text as a string.
    - If the elf_server binding is None, returns None.
    """

    try:
        headers = { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive',}
        reception_manager=RECEPTION_MANAGER()
        prompt = request.prompt
        encoded_images = request.images
        tokens = elf_server.model.tokenize(prompt)
        n_tokens = len(tokens)
        ASCIIColors.yellow(f"Prompt input size {n_tokens}")        
        n_predict = min(min(elf_server.config.ctx_size-n_tokens-1,elf_server.config.max_n_predict), request.n_predict) if request.n_predict>0 else min(elf_server.config.ctx_size-n_tokens-1,elf_server.config.max_n_predict)
        stream = request.stream
        prompt_tokens = len(elf_server.binding.tokenize(prompt))
        if elf_server.binding is not None:
            def add_padding(encoded_image):
                missing_padding = len(encoded_image) % 4
                if missing_padding:
                    encoded_image += '=' * (4 - missing_padding)
                return encoded_image
            def sanitize_base64(encoded_image):
                # Remove any characters that are not valid base64 characters
                return re.sub(r'[^A-Za-z0-9+/=]', '', encoded_image)
            image_files = []
            images_path = elf_server.lollms_paths.personal_outputs_path / "tmp_images"
            images_path.mkdir(parents=True, exist_ok=True)
            for i, encoded_image in enumerate(encoded_images):
                # Remove the data URL prefix
                if encoded_image.startswith('data:image/png;base64,'):
                    encoded_image = encoded_image.split(',')[1]  # Get the base64 part only

                sanitized_image = sanitize_base64(encoded_image)
                padded_image = add_padding(sanitized_image)

                image_path = images_path/ f'image_{i}.png'
                with open(image_path, 'wb') as image_file:
                    image_file.write(base64.b64decode(padded_image))
                image_files.append(image_path)            
            if stream:
                new_output={"new_values":[]}
                async def generate_chunks():
                    lk = threading.Lock()

                    def callback(chunk, chunk_type:MSG_OPERATION_TYPE=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK):
                        if elf_server.cancel_gen:
                            return False
                        
                        if chunk is None:
                            return

                        rx = reception_manager.new_chunk(chunk)
                        if rx.status!=ROLE_CHANGE_DECISION.MOVE_ON:
                            if rx.status==ROLE_CHANGE_DECISION.PROGRESSING:
                                return True
                            elif rx.status==ROLE_CHANGE_DECISION.ROLE_CHANGED:
                                return False
                            else:
                                chunk = chunk + rx.value

                        # Yield each chunk of data
                        lk.acquire()
                        try:
                            new_output["new_values"].append(reception_manager.chunk)
                            lk.release()
                            return True
                        except Exception as ex:
                            trace_exception(ex)
                            lk.release()
                            return False
                        
                    def chunks_builder():
                        if request.model_name in elf_server.binding.list_models() and elf_server.binding.model_name!=request.model_name:
                            elf_server.binding.build_model(request.model_name)    

                        elf_server.binding.generate_with_images(
                                                prompt,
                                                image_files,
                                                n_predict, 
                                                callback=callback, 
                                                temperature=request.temperature or elf_server.config.temperature
                                            )
                        reception_manager.done = True
                    thread = threading.Thread(target=chunks_builder)
                    thread.start()
                    current_index = 0
                    while (not reception_manager.done and elf_server.cancel_gen == False):
                        while (not reception_manager.done and len(new_output["new_values"])==0):
                            time.sleep(0.001)
                        lk.acquire()
                        for i in range(len(new_output["new_values"])):
                            current_index += 1                        
                            yield (new_output["new_values"][i])
                        new_output["new_values"]=[]
                        lk.release()
                    elf_server.cancel_gen = False         
                return StreamingResponse(generate_chunks(), media_type="text/plain", headers=headers)
            else:
                def callback(chunk, chunk_type:MSG_OPERATION_TYPE=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK):
                    # Yield each chunk of data
                    if chunk is None:
                        return True

                    rx = reception_manager.new_chunk(chunk)
                    if rx.status!=ROLE_CHANGE_DECISION.MOVE_ON:
                        if rx.status==ROLE_CHANGE_DECISION.PROGRESSING:
                            return True
                        elif rx.status==ROLE_CHANGE_DECISION.ROLE_CHANGED:
                            return False
                        else:
                            chunk = chunk + rx.value


                    return True
                elf_server.binding.generate_with_images(
                                                prompt,
                                                image_files,
                                                n_predict, 
                                                callback=callback,
                                                temperature=request.temperature or elf_server.config.temperature
                                            )
                completion_tokens = len(elf_server.binding.tokenize(reception_manager.reception_buffer))
                return PlainTextResponse(reception_manager.reception_buffer)
        else:
            return None
    except Exception as ex:
        trace_exception(ex)
        elf_server.error(ex)
        raise HTTPException(400, f"Error : {ex}")


# ----------------------- Open AI ----------------------------------------
class Message(BaseModel):
    role: str
    content: str

class Delta(BaseModel):
    content : str = ""
    role : str = "assistant"


class Choices(BaseModel):
    finish_reason: Optional[str] = None,
    index: Optional[int] = 0,
    message: Optional[Message] = None,
    logprobs: Optional[float] = None



class Usage(BaseModel):
    prompt_tokens: Optional[int]=0,
    completion_tokens : Optional[int]=0,
    completion_tokens : Optional[int]=0,


class StreamingChoices(BaseModel):
    finish_reason : Optional[str] = "stop"
    index : Optional[int] = 0
    delta : Optional[Delta] = None
    logprobs : Optional[List[float]|None] = None

class StreamingModelResponse(BaseModel):
    id: str
    """A unique identifier for the completion."""

    choices: List[StreamingChoices]
    """The list of completion choices the model generated for the input prompt."""

    created: int
    """The Unix timestamp (in seconds) of when the completion was created."""

    model: Optional[str] = None
    """The model used for completion."""

    object: Optional[str] = "text_completion"
    """The object type, which is always "text_completion" """

    system_fingerprint: Optional[str] = None
    """This fingerprint represents the backend configuration that the model runs with.

    Can be used in conjunction with the `seed` request parameter to understand when
    backend changes have been made that might impact determinism.
    """

    usage: Optional[Usage] = None
    """Usage statistics for the completion request."""

class ModelResponse(BaseModel):
    id: str
    """A unique identifier for the completion."""

    choices: List[Choices]
    """The list of completion choices the model generated for the input prompt."""

    created: int
    """The Unix timestamp (in seconds) of when the completion was created."""

    model: Optional[str] = None
    """The model used for completion."""

    object: Optional[str] = "text_completion"
    """The object type, which is always "text_completion" """

    system_fingerprint: Optional[str] = None
    """This fingerprint represents the backend configuration that the model runs with.

    Can be used in conjunction with the `seed` request parameter to understand when
    backend changes have been made that might impact determinism.
    """

    usage: Optional[Usage] = None
    """Usage statistics for the completion request."""


class ChatGenerationRequest(BaseModel):
    model: str = ""
    messages: List[Message]
    max_tokens: Optional[int] = -1
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.1


@router.post("/v1/chat/completions")
async def v1_chat_completions(request: ChatGenerationRequest):
    try:
        reception_manager=RECEPTION_MANAGER()
        messages = request.messages
        max_tokens = request.max_tokens if request.max_tokens>0 else elf_server.config.max_n_predict if elf_server.config.max_n_predict else elf_server.config.ctx_size
        temperature = request.temperature if  elf_server.config.temperature else elf_server.config.temperature
        prompt = ""
        roles= False
        for message in messages:
            if message.role!="":
                prompt += f"{elf_server.config.discussion_prompt_separator}{message.role}: {message.content}\n"
                roles = True
            else:
                prompt += f"{message.content}\n"
        if roles:
            prompt += f"{elf_server.config.discussion_prompt_separator}assistant:"
        n_predict = max_tokens if max_tokens>0 else 1024
        stream = request.stream
        prompt_tokens = len(elf_server.binding.tokenize(prompt))
        if elf_server.binding is not None:
            if stream:
                new_output={"new_values":[]}
                async def generate_chunks():
                    lk = threading.Lock()

                    def callback(chunk, chunk_type:MSG_OPERATION_TYPE=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK):
                        if elf_server.cancel_gen:
                            return False
                        
                        if chunk is None:
                            return

                        rx = reception_manager.new_chunk(chunk)
                        if rx.status!=ROLE_CHANGE_DECISION.MOVE_ON:
                            if rx.status==ROLE_CHANGE_DECISION.PROGRESSING:
                                return True
                            elif rx.status==ROLE_CHANGE_DECISION.ROLE_CHANGED:
                                return False
                            else:
                                chunk = chunk + rx.value

                        # Yield each chunk of data
                        lk.acquire()
                        try:
                            new_output["new_values"].append(reception_manager.chunk)
                            lk.release()
                            return True
                        except Exception as ex:
                            trace_exception(ex)
                            lk.release()
                            return False
                        
                    def chunks_builder():
                        elf_server.binding.generate(
                                                prompt, 
                                                n_predict, 
                                                callback=callback, 
                                                temperature=temperature
                                            )
                        reception_manager.done = True
                    thread = threading.Thread(target=chunks_builder)
                    thread.start()
                    current_index = 0
                    while (not reception_manager.done and elf_server.cancel_gen == False):
                        while (not reception_manager.done and len(new_output["new_values"])==0):
                            time.sleep(0.001)
                        lk.acquire()
                        for i in range(len(new_output["new_values"])):
                            output_val = StreamingModelResponse(
                                id = _generate_id(), 
                                choices = [StreamingChoices(index= current_index, delta=Delta(content=new_output["new_values"][i]))], 
                                created=int(time.time()),
                                model=elf_server.config.model_name,
                                object="chat.completion.chunk",
                                usage=Usage(prompt_tokens= prompt_tokens, completion_tokens= 1)
                                )
                            current_index += 1                        
                            yield (output_val.json() + '\n')
                        new_output["new_values"]=[]
                        lk.release()
                    elf_server.cancel_gen = False         
                return StreamingResponse(generate_chunks(), media_type="application/json")
            else:
                def callback(chunk, chunk_type:MSG_OPERATION_TYPE=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK):
                    # Yield each chunk of data
                    if chunk is None:
                        return True

                    rx = reception_manager.new_chunk(chunk)
                    if rx.status!=ROLE_CHANGE_DECISION.MOVE_ON:
                        if rx.status==ROLE_CHANGE_DECISION.PROGRESSING:
                            return True
                        elif rx.status==ROLE_CHANGE_DECISION.ROLE_CHANGED:
                            return False
                        else:
                            chunk = chunk + rx.value


                    return True
                elf_server.binding.generate(
                                                prompt, 
                                                n_predict, 
                                                callback=callback,
                                                temperature=temperature
                                            )
                completion_tokens = len(elf_server.binding.tokenize(reception_manager.reception_buffer))
                return ModelResponse(id = _generate_id(), choices = [Choices(message=Message(role="assistant", content=reception_manager.reception_buffer), finish_reason="stop", index=0)], created=int(time.time()), model=request.model,usage=Usage(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens))
        else:
            return None
    except Exception as ex:
        trace_exception(ex)
        elf_server.error(ex)
        raise HTTPException(400, f"Error : {ex}")

class OllamaModelResponse(BaseModel):
    id: str
    """A unique identifier for the completion."""

    choices: List[Choices]
    """The list of completion choices the model generated for the input prompt."""

    created: int
    """The Unix timestamp (in seconds) of when the completion was created."""

    model: Optional[str] = None
    """The model used for completion."""

    object: Optional[str] = "text_completion"
    """The object type, which is always "text_completion" """

    system_fingerprint: Optional[str] = None
    """This fingerprint represents the backend configuration that the model runs with.

    Can be used in conjunction with the `seed` request parameter to understand when
    backend changes have been made that might impact determinism.
    """

    usage: Optional[Usage] = None
    """Usage statistics for the completion request."""


@router.post("/api/chat")
async def ollama_chat_completion(request: ChatGenerationRequest):
    try:
        reception_manager=RECEPTION_MANAGER()
        messages = request.messages
        max_tokens = request.max_tokens if request.max_tokens>0 else elf_server.config.max_n_predict if elf_server.config.max_n_predict else elf_server.config.ctx_size
        temperature = request.temperature if  elf_server.config.temperature else elf_server.config.temperature
        prompt = ""
        roles= False
        for message in messages:
            if message.role!="":
                prompt += f"{elf_server.config.discussion_prompt_separator}{message.role}: {message.content}\n"
                roles = True
            else:
                prompt += f"{message.content}\n"
        if roles:
            prompt += f"{elf_server.config.discussion_prompt_separator}assistant:"
        n_predict = max_tokens if max_tokens>0 else 1024
        stream = request.stream
        prompt_tokens = len(elf_server.binding.tokenize(prompt))
        if elf_server.binding is not None:
            if stream:
                new_output={"new_values":[]}
                async def generate_chunks():
                    lk = threading.Lock()

                    def callback(chunk, chunk_type:MSG_OPERATION_TYPE=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK):
                        if elf_server.cancel_gen:
                            return False
                        
                        if chunk is None:
                            return

                        rx = reception_manager.new_chunk(chunk)
                        if rx.status!=ROLE_CHANGE_DECISION.MOVE_ON:
                            if rx.status==ROLE_CHANGE_DECISION.PROGRESSING:
                                return True
                            elif rx.status==ROLE_CHANGE_DECISION.ROLE_CHANGED:
                                return False
                            else:
                                chunk = chunk + rx.value

                        # Yield each chunk of data
                        lk.acquire()
                        try:
                            new_output["new_values"].append(reception_manager.chunk)
                            lk.release()
                            return True
                        except Exception as ex:
                            trace_exception(ex)
                            lk.release()
                            return False
                        
                    def chunks_builder():
                        elf_server.binding.generate(
                                                prompt, 
                                                n_predict, 
                                                callback=callback, 
                                                temperature=temperature
                                            )
                        reception_manager.done = True
                    thread = threading.Thread(target=chunks_builder)
                    thread.start()
                    current_index = 0
                    while (not reception_manager.done and elf_server.cancel_gen == False):
                        while (not reception_manager.done and len(new_output["new_values"])==0):
                            time.sleep(0.001)
                        lk.acquire()
                        for i in range(len(new_output["new_values"])):
                            output_val = StreamingModelResponse(
                                id = _generate_id(), 
                                choices = [StreamingChoices(index= current_index, delta=Delta(content=new_output["new_values"][i]))], 
                                created=int(time.time()),
                                model=elf_server.config.model_name,
                                object="chat.completion.chunk",
                                usage=Usage(prompt_tokens= prompt_tokens, completion_tokens= 1)
                                )
                            current_index += 1                        
                            yield (output_val.json() + '\n')
                        new_output["new_values"]=[]
                        lk.release()
                    elf_server.cancel_gen = False         
                return StreamingResponse(generate_chunks(), media_type="application/json")
            else:
                def callback(chunk, chunk_type:MSG_OPERATION_TYPE=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK):
                    # Yield each chunk of data
                    if chunk is None:
                        return True

                    rx = reception_manager.new_chunk(chunk)
                    if rx.status!=ROLE_CHANGE_DECISION.MOVE_ON:
                        if rx.status==ROLE_CHANGE_DECISION.PROGRESSING:
                            return True
                        elif rx.status==ROLE_CHANGE_DECISION.ROLE_CHANGED:
                            return False
                        else:
                            chunk = chunk + rx.value


                    return True
                elf_server.binding.generate(
                                                prompt, 
                                                n_predict, 
                                                callback=callback,
                                                temperature=temperature
                                            )
                completion_tokens = len(elf_server.binding.tokenize(reception_manager.reception_buffer))
                return OllamaModelResponse(id = _generate_id(), choices = [Choices(message=Message(role="assistant", content=reception_manager.reception_buffer), finish_reason="stop", index=0)], created=int(time.time()), model=request.model,usage=Usage(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens))
        else:
            return None
    except Exception as ex:
        trace_exception(ex)
        elf_server.error(ex)
        return {"status":False,"error":str(ex)}

class CompletionGenerationRequest(BaseModel):
    model: Optional[str] = None
    prompt: str
    max_tokens: Optional[int] = -1
    stream: Optional[bool] = False
    temperature: Optional[float] = -1
    mirostat: Optional[int] = None
    mirostat_eta: Optional[float] = None
    mirostat_tau: Optional[float] = None
    num_ctx: Optional[int] = None
    repeat_last_n: Optional[int] = -1
    repeat_penalty: Optional[float] = -1
    seed: Optional[int] = None
    stop: Optional[str] = None
    tfs_z: Optional[float] = None
    num_predict: Optional[int] = None
    top_k: Optional[int] = -1
    top_p: Optional[float] = -1
    format: Optional[str] = None  # Added as per new request
    system: Optional[str] = None  # Added as per new request
    template: Optional[str] = None  # Added as per new request
    context: Optional[str] = None  # Added as per new request
    raw: Optional[bool] = None  # Added as per new request
    keep_alive: Optional[str] = None  # Added as per new request


@router.options("/api/generate")
@router.post("/api/generate")
async def ollama_generate(request: CompletionGenerationRequest):
    """
    Executes Python code and returns the output.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """
    start_header_id_template    = elf_server.config.start_header_id_template
    end_header_id_template      = elf_server.config.end_header_id_template
    separator_template          = elf_server.config.separator_template

    try:
        start_time = time.perf_counter_ns()
        ASCIIColors.cyan("> Ollama Server emulator: Received request")
        text = request.prompt
        request.max_tokens = request.max_tokens if request.max_tokens>0 else elf_server.config.ctx_size
        n_predict = request.max_tokens if request.max_tokens>0 else elf_server.config.max_n_predict
        temperature = request.temperature if request.temperature>0 else elf_server.config.temperature
        top_k = request.top_k if request.top_k>0 else elf_server.config.top_k
        top_p = request.top_p if request.top_p>0 else elf_server.config.top_p
        repeat_last_n = request.repeat_last_n if request.repeat_last_n>0 else elf_server.config.repeat_last_n
        repeat_penalty = request.repeat_penalty if request.repeat_penalty>0 else elf_server.config.repeat_penalty
        stream = request.stream
        created_at = datetime.now().isoformat()
        response_data = {
            "model": request.model if request.model is not None else "llama3",
            "created_at": created_at,
            "response": "",
            "done": False,
            "context": [1, 2, 3],  # Placeholder for actual context
        }
        
        ASCIIColors.cyan("> Processing ...")
        if elf_server.binding is not None:
            if stream:
                output = {"text":""}
                def generate_chunks():
                    def callback(chunk, chunk_type:MSG_OPERATION_TYPE=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK):
                        # Yield each chunk of data
                        output["text"] += chunk
                        antiprompt = detect_antiprompt(output["text"], [start_header_id_template, end_header_id_template])
                        if antiprompt:
                            ASCIIColors.warning(f"\n{antiprompt} detected. Stopping generation")
                            output["text"] = remove_text_from_string(output["text"],antiprompt)
                            return False
                        else:
                            yield chunk
                            return True
                    return iter(elf_server.binding.generate(
                                                text, 
                                                n_predict, 
                                                callback=callback, 
                                                temperature=temperature,
                            ))
                ASCIIColors.success("> Streaming ...")                
                return StreamingResponse(generate_chunks())
            else:
                output = {"text":""}
                def callback(chunk, chunk_type:MSG_OPERATION_TYPE=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK):
                    if chunk is None:
                        return
                    # Yield each chunk of data
                    output["text"] += chunk
                    antiprompt = detect_antiprompt(output["text"])
                    if antiprompt:
                        ASCIIColors.warning(f"\n{antiprompt} detected. Stopping generation")
                        output["text"] = remove_text_from_string(output["text"],antiprompt)
                        ASCIIColors.success("Done")                
                        return False
                    else:
                        return True
                elf_server.binding.generate(
                                                text, 
                                                n_predict, 
                                                callback=callback,
                                                temperature=request.temperature if request.temperature>=0 else elf_server.config.temperature
                                            )
                ASCIIColors.success("> Done")
                response_data["total_duration"] = time.perf_counter_ns() - start_time
                response_data["load_duration"] = 0
                response_data["prompt_eval_count"] = len(request.prompt.split())
                response_data["prompt_eval_duration"] = time.perf_counter_ns() - start_time
                response_data["eval_count"] = len(elf_server.binding.tokenize(output["text"]))  # Simulated number of tokens in the response
                response_data["eval_duration"] = time.perf_counter_ns() - start_time
                response_data["response"] = output["text"]
                response_data["done"] = True
                return response_data
        else:
            ASCIIColors.error("> Failed")
            return None
    except Exception as ex:
        trace_exception(ex)
        elf_server.error(ex)
        return {"status":False,"error":str(ex)}




@router.post("/instruct/generate")
async def ollama_completion(request: CompletionGenerationRequest):
    """
    Executes Python code and returns the output.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """
    try:
        reception_manager=RECEPTION_MANAGER()
        prompt = request.prompt
        n_predict = request.max_tokens if request.max_tokens>=0 else elf_server.config.max_n_predict
        temperature = request.temperature if request.temperature>=0 else elf_server.config.temperature
        # top_k = request.top_k if request.top_k>=0 else elf_server.config.top_k
        # top_p = request.top_p if request.top_p>=0 else elf_server.config.top_p
        # repeat_last_n = request.repeat_last_n if request.repeat_last_n>=0 else elf_server.config.repeat_last_n
        # repeat_penalty = request.repeat_penalty if request.repeat_penalty>=0 else elf_server.config.repeat_penalty
        stream = request.stream
        
        if elf_server.binding is not None:
            if stream:
                new_output={"new_values":[]}
                async def generate_chunks():
                    lk = threading.Lock()

                    def callback(chunk, chunk_type:MSG_OPERATION_TYPE=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK):
                        if elf_server.cancel_gen:
                            return False
                        
                        if chunk is None:
                            return

                        rx = reception_manager.new_chunk(chunk)
                        if rx.status!=ROLE_CHANGE_DECISION.MOVE_ON:
                            if rx.status==ROLE_CHANGE_DECISION.PROGRESSING:
                                return True
                            elif rx.status==ROLE_CHANGE_DECISION.ROLE_CHANGED:
                                return False
                            else:
                                chunk = chunk + rx.value

                        # Yield each chunk of data
                        lk.acquire()
                        try:
                            new_output["new_values"].append(reception_manager.chunk)
                            lk.release()
                            return True
                        except Exception as ex:
                            trace_exception(ex)
                            lk.release()
                            return False
                        
                    def chunks_builder():
                        if request.model in elf_server.binding.list_models() and elf_server.binding.model_name!=request.model:
                            elf_server.binding.build_model(request.model)    

                        elf_server.binding.generate(
                                                prompt, 
                                                n_predict, 
                                                callback=callback, 
                                                temperature=temperature or elf_server.config.temperature
                                            )
                        reception_manager.done = True
                    thread = threading.Thread(target=chunks_builder)
                    thread.start()
                    current_index = 0
                    while (not reception_manager.done and elf_server.cancel_gen == False):
                        while (not reception_manager.done and len(new_output["new_values"])==0):
                            time.sleep(0.001)
                        lk.acquire()
                        for i in range(len(new_output["new_values"])):
                            current_index += 1                        
                            yield {"response":new_output["new_values"][i]}
                        new_output["new_values"]=[]
                        lk.release()
                    elf_server.cancel_gen = False         
                return StreamingResponse(generate_chunks(), media_type="text/plain")
            else:
                def callback(chunk, chunk_type:MSG_OPERATION_TYPE=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK):
                    # Yield each chunk of data
                    if chunk is None:
                        return True

                    rx = reception_manager.new_chunk(chunk)
                    if rx.status!=ROLE_CHANGE_DECISION.MOVE_ON:
                        if rx.status==ROLE_CHANGE_DECISION.PROGRESSING:
                            return True
                        elif rx.status==ROLE_CHANGE_DECISION.ROLE_CHANGED:
                            return False
                        else:
                            chunk = chunk + rx.value


                    return True
                elf_server.binding.generate(
                                                prompt, 
                                                n_predict, 
                                                callback=callback,
                                                temperature=request.temperature or elf_server.config.temperature
                                            )
                return {"response":reception_manager.reception_buffer}
    except Exception as ex:
        trace_exception(ex)
        elf_server.error(ex)
        return {"status":False,"error":str(ex)}


@router.post("/v1/completions")
async def v1_completion(request: CompletionGenerationRequest):
    """
    Executes Python code and returns the output.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """
    try:
        text = request.prompt
        n_predict = request.max_tokens if request.max_tokens>=0 else elf_server.config.max_n_predict if elf_server.config.max_n_predict else elf_server.config.ctx_size
        temperature = request.temperature if request.temperature>=0 else elf_server.config.temperature
        # top_k = request.top_k if request.top_k>=0 else elf_server.config.top_k
        # top_p = request.top_p if request.top_p>=0 else elf_server.config.top_p
        # repeat_last_n = request.repeat_last_n if request.repeat_last_n>=0 else elf_server.config.repeat_last_n
        # repeat_penalty = request.repeat_penalty if request.repeat_penalty>=0 else elf_server.config.repeat_penalty
        stream = request.stream
        
        if elf_server.binding is not None:
            if stream:
                output = {"text":""}
                def generate_chunks():
                    def callback(chunk, chunk_type:MSG_OPERATION_TYPE=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK):
                        # Yield each chunk of data
                        output["text"] += chunk
                        antiprompt = detect_antiprompt(output["text"])
                        if antiprompt:
                            ASCIIColors.warning(f"\n{antiprompt} detected. Stopping generation")
                            output["text"] = remove_text_from_string(output["text"],antiprompt)
                            return False
                        else:
                            yield chunk
                            return True
                    return iter(elf_server.binding.generate(
                                                text, 
                                                n_predict, 
                                                callback=callback, 
                                                temperature=temperature,
                            ))
                
                return StreamingResponse(generate_chunks())
            else:
                output = {"text":""}
                def callback(chunk, chunk_type:MSG_OPERATION_TYPE=MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK):
                    # Yield each chunk of data
                    output["text"] += chunk
                    antiprompt = detect_antiprompt(output["text"])
                    if antiprompt:
                        ASCIIColors.warning(f"\n{antiprompt} detected. Stopping generation")
                        output["text"] = remove_text_from_string(output["text"],antiprompt)
                        return False
                    else:
                        return True
                elf_server.binding.generate(
                                                text, 
                                                n_predict, 
                                                callback=callback,
                                                temperature=request.temperature if request.temperature>=0 else elf_server.config.temperature
                                            )
                return output["text"]
        else:
            return None
    except Exception as ex:
        trace_exception(ex)
        elf_server.error(ex)
        return {"status":False,"error":str(ex)}


@router.post("/stop_gen")
def stop_gen():
    elf_server.cancel_gen = True
    return {"status": True} 
