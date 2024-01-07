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
from lollms.utilities import detect_antiprompt, remove_text_from_string
from ascii_colors import ASCIIColors
from api.db import DiscussionsDB

from safe_store.text_vectorizer import TextVectorizer, VectorizationMethod, VisualizationMethod
import tqdm


router = APIRouter()
lollmsElfServer = LOLLMSWebUI.get_instance()

