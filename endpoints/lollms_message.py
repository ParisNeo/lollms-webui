"""
project: lollms_message
file: lollms_discussion.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes allow users to manipulate the message elements.

"""
from fastapi import APIRouter
from pydantic import Field
from lollms_webui import LOLLMSWebUI
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from lollms.types import MSG_TYPE
from lollms.utilities import detect_antiprompt, remove_text_from_string, trace_exception
from ascii_colors import ASCIIColors
from api.db import DiscussionsDB

from safe_store.text_vectorizer import TextVectorizer, VectorizationMethod, VisualizationMethod
import tqdm

# ----------------------- Defining router and main class ------------------------------

router = APIRouter()
lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()

class EditMessageParameters(BaseModel):
    client_id: str = Field(..., min_length=1)
    id: int = Field(..., gt=0)
    message: str = Field(..., min_length=1)
    metadata: dict = Field(default={})

@router.get("/edit_message")
async def edit_message(edit_params: EditMessageParameters):
    client_id = edit_params.client_id
    message_id = edit_params.id
    new_message = edit_params.message
    metadata = edit_params.metadata
    try:
        lollmsElfServer.connections[client_id]["current_discussion"].edit_message(message_id, new_message, new_metadata=metadata)
        return {"status": True}
    except Exception as ex:
        trace_exception(ex)  # Assuming 'trace_exception' function logs the error
        return {"status": False, "error": "There was an error editing the message"}



class MessageRankParameters(BaseModel):
    client_id: str = Field(..., min_length=1)
    id: int = Field(..., gt=0)

@router.get("/message_rank_up")
async def message_rank_up(rank_params: MessageRankParameters):
    client_id = rank_params.client_id
    discussion_id = rank_params.id

    try:
        new_rank = lollmsElfServer.connections[client_id]["current_discussion"].message_rank_up(discussion_id)
        return {"status": True, "new_rank": new_rank}
    except Exception as ex:
        trace_exception(ex)  # Assuming 'trace_exception' function logs the error
        return {"status": False, "error": "There was an error ranking up the message"}


@router.get("/message_rank_down")
def message_rank_down(rank_params: MessageRankParameters):
    client_id = rank_params.client_id
    discussion_id = rank_params.id
    try:
        new_rank = lollmsElfServer.connections[client_id]["current_discussion"].message_rank_down(discussion_id)
        return {"status": True, "new_rank": new_rank}
    except Exception as ex:
        return {"status": False, "error":str(ex)}

class MessageDeleteParameters(BaseModel):
    client_id: str = Field(..., min_length=1)
    id: int = Field(..., gt=0)

@router.get("/delete_message")
async def delete_message(delete_params: MessageDeleteParameters):
    client_id = delete_params.client_id
    discussion_id = delete_params.id

    if lollmsElfServer.connections[client_id]["current_discussion"] is None:
        return {"status": False,"message":"No discussion is selected"}
    else:
        try:
            new_rank = lollmsElfServer.connections[client_id]["current_discussion"].delete_message(discussion_id)
            ASCIIColors.yellow("Message deleted")
            return {"status":True,"new_rank": new_rank}
        except Exception as ex:
            trace_exception(ex)  # Assuming 'trace_exception' function logs the error
            return {"status": False, "error": "There was an error deleting the message"}
