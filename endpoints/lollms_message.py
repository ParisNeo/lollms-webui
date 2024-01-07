"""
project: lollms_message
file: lollms_discussion.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes allow users to manipulate the message elements.

"""
from fastapi import APIRouter
from lollms_webui import LOLLMSWebUI
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from lollms.types import MSG_TYPE
from lollms.utilities import detect_antiprompt, remove_text_from_string, trace_exception
from ascii_colors import ASCIIColors
from api.db import DiscussionsDB

from safe_store.text_vectorizer import TextVectorizer, VectorizationMethod, VisualizationMethod
import tqdm


router = APIRouter()
lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()

class EditMessageParameters(BaseModel):
    client_id       :str
    id              :int
    message         :str
    metadata        :dict

@router.get("/edit_message")
def edit_message(client_id:str,id:int, message:str,metadata:dict=None):
    message_id      = id
    new_message     = message
    metadata        = metadata
    try:
        lollmsElfServer.connections[client_id]["current_discussion"].edit_message(message_id, new_message,new_metadata=metadata)
        return {"status": True}
    except Exception as ex:
        trace_exception(ex)
        return {"status": False, "error":str(ex)}

class MessageRankParameters(BaseModel):
    client_id       :str
    id              :int

class MessageDeleteParameters(BaseModel):
    client_id       :str
    id              :int

@router.get("/message_rank_up")
def message_rank_up(client_id:str, id:int):
    discussion_id   = id
    try:
        new_rank = lollmsElfServer.connections[client_id]["current_discussion"].message_rank_up(discussion_id)
        return {"status": True, "new_rank": new_rank}
    except Exception as ex:
        return {"status": False, "error":str(ex)}

@router.get("/message_rank_down")
def message_rank_down(client_id:str, id:int):
    discussion_id = id
    try:
        new_rank = lollmsElfServer.connections[client_id]["current_discussion"].message_rank_down(discussion_id)
        return {"status": True, "new_rank": new_rank}
    except Exception as ex:
        return {"status": False, "error":str(ex)}

@router.get("/delete_message")
def delete_message(client_id:str, id:int):
    discussion_id = id
    if lollmsElfServer.connections[client_id]["current_discussion"] is None:
        return {"status": False,"message":"No discussion is selected"}
    else:
        new_rank = lollmsElfServer.connections[client_id]["current_discussion"].delete_message(discussion_id)
        ASCIIColors.yellow("Message deleted")
        return {"status":True,"new_rank": new_rank}
