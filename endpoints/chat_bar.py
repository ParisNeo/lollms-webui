"""
project: lollms_webui
file: chat_bar.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes are linked to lollms_webui chatbox

"""
from fastapi import APIRouter, Request
from fastapi import HTTPException
from pydantic import BaseModel, Field
from lollms_webui import LOLLMSWebUI
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from lollms.types import MSG_TYPE
from lollms.main_config import BaseConfig
from lollms.utilities import detect_antiprompt, remove_text_from_string, trace_exception, find_first_available_file_index
from ascii_colors import ASCIIColors
from lollms.databases.discussions_database import DiscussionsDB
from lollms.types import SENDER_TYPES
from typing import List
from pathlib import Path
from safe_store.text_vectorizer import TextVectorizer, VectorizationMethod, VisualizationMethod
import tqdm
from fastapi import FastAPI, UploadFile, File
import shutil
import os
import platform
from urllib.parse import urlparse
from functools import partial
from datetime import datetime
from utilities.execution_engines.python_execution_engine import execute_python
from utilities.execution_engines.latex_execution_engine import execute_latex
from utilities.execution_engines.shell_execution_engine import execute_bash
from lollms.security import sanitize_path, forbid_remote_access
from lollms.internet import scrape_and_save
from urllib.parse import urlparse
import threading
# ----------------------- Defining router and main class ------------------------------

router = APIRouter()
lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()

class AddWebPageRequest(BaseModel):
    client_id: str  = Field(...)
    url: str = Field(..., description="Url to be used")

class CmdExecutionRequest(BaseModel):
    client_id: str  = Field(...)
    command: str = Field(..., description="Url to be used")
    parameters: List[str] = Field(..., description="Command parameters")



"""
@router.post("/execute_personality_command")
async def execute_personality_command(request: CmdExecutionRequest):
    client_id = request.client_id
    client = lollmsElfServer.session.get_client(client_id)

    lollmsElfServer.cancel_gen = False
    client.generated_text=""
    client.cancel_generation=False
    client.continuing=False
    client.first_chunk=True
    
    if not lollmsElfServer.model:
        ASCIIColors.error("Model not selected. Please select a model")
        lollmsElfServer.error("Model not selected. Please select a model", client_id=client_id)
        return {'status':False,"error":"Model not selected. Please select a model"}

    if not lollmsElfServer.busy:
        if lollmsElfServer.session.get_client(client_id).discussion is None:
            if lollmsElfServer.db.does_last_discussion_have_messages():
                lollmsElfServer.session.get_client(client_id).discussion = lollmsElfServer.db.create_discussion()
            else:
                lollmsElfServer.session.get_client(client_id).discussion = lollmsElfServer.db.load_last_discussion()

        ump = lollmsElfServer.config.discussion_prompt_separator +lollmsElfServer.config.user_name.strip() if lollmsElfServer.config.use_user_name_in_discussions else lollmsElfServer.personality.user_message_prefix
        message = lollmsElfServer.session.get_client(client_id).discussion.add_message(
            message_type    = MSG_TYPE.MSG_TYPE_FULL.value,
            sender_type     = SENDER_TYPES.SENDER_TYPES_USER.value,
            sender          = ump.replace(lollmsElfServer.config.discussion_prompt_separator,"").replace(":",""),
            content="",
            metadata=None,
            parent_message_id=lollmsElfServer.message_id
        )
        lollmsElfServer.busy=True

        command = request.command
        parameters =  request.parameters
        lollmsElfServer.prepare_reception(client_id)
        if lollmsElfServer.personality.processor is not None:
            lollmsElfServer.start_time = datetime.now()
            lollmsElfServer.personality.processor.callback = partial(lollmsElfServer.process_chunk, client_id=client_id)
            lollmsElfServer.personality.processor.execute_command(command, parameters)
        else:
            lollmsElfServer.warning("Non scripted personalities do not support commands",client_id=client_id)
        lollmsElfServer.close_message(client_id)
        lollmsElfServer.busy=False

        #tpe = threading.Thread(target=lollmsElfServer.start_message_generation, args=(message, message_id, client_id))
        #tpe.start()
    else:
        lollmsElfServer.error("I am busy. Come back later.", client_id=client_id)
        return {'status':False,"error":"I am busy. Come back later."}

    lollmsElfServer.busy=False
    return {'status':True,}
"""
MAX_PAGE_SIZE = 10000000

@router.post("/add_webpage")
async def add_webpage(request: AddWebPageRequest):
    forbid_remote_access(lollmsElfServer)
    client = lollmsElfServer.session.get_client(request.client_id)
    if client is None:
        raise HTTPException(status_code=400, detail="Unknown client. This service only accepts lollms webui requests")
        
    def do_scraping():
        lollmsElfServer.ShowBlockingMessage("Scraping web page\nPlease wait...")
        ASCIIColors.yellow("Scaping web page")
        client = lollmsElfServer.session.get_client(request.client_id)
        url = request.url
        index =  find_first_available_file_index(lollmsElfServer.lollms_paths.personal_uploads_path,"web_",".txt")
        file_path=sanitize_path(lollmsElfServer.lollms_paths.personal_uploads_path/f"web_{index}.txt",True)
        try:
            result = urlparse(url)
            if all([result.scheme, result.netloc]):  # valid URL
                if scrape_and_save(url=url, file_path=file_path,max_size=MAX_PAGE_SIZE):
                    raise HTTPException(status_code=400, detail="Web page too large")
            else:
                raise HTTPException(status_code=400, detail="Invalid URL")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Exception : {e}")
        
        try:
            if not lollmsElfServer.personality.processor is None:
                lollmsElfServer.personality.processor.add_file(file_path, client, partial(lollmsElfServer.process_chunk, client_id = request.client_id))
                # File saved successfully
            else:
                lollmsElfServer.personality.add_file(file_path, client, partial(lollmsElfServer.process_chunk, client_id = request.client_id))
                # File saved successfully
            lollmsElfServer.HideBlockingMessage()
            lollmsElfServer.refresh_files()
        except Exception as e:
            # Error occurred while saving the file
            lollmsElfServer.HideBlockingMessage()
            lollmsElfServer.refresh_files()
            return {'status':False,"error":str(e)}
    client.generation_thread = threading.Thread(target=do_scraping)
    client.generation_thread.start()
        
    return {'status':True}
