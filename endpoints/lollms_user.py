"""
project: lollms_user
file: lollms_user.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes allow users to manipulate user information.

"""
from fastapi import APIRouter
from lollms_webui import LOLLMSWebUI
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from lollms.types import MSG_TYPE
from lollms.main_config import BaseConfig
from lollms.utilities import detect_antiprompt, remove_text_from_string
from ascii_colors import ASCIIColors
from api.db import DiscussionsDB
from pathlib import Path
from safe_store.text_vectorizer import TextVectorizer, VectorizationMethod, VisualizationMethod
import tqdm

class PersonalPathParameters(BaseModel):
    path:str

router = APIRouter()
lollmsElfServer = LOLLMSWebUI.get_instance()

@router.get("/switch_personal_path")
def switch_personal_path(data:PersonalPathParameters):
    path = data.path
    global_paths_cfg = Path("./global_paths_cfg.yaml")
    if global_paths_cfg.exists():
        try:
            cfg = BaseConfig()
            cfg.load_config(global_paths_cfg)
            cfg.lollms_personal_path = path
            cfg.save_config(global_paths_cfg)
            return {"status": True}      
        except Exception as ex:
            print(ex)
            return {"status": False, 'error':f"Couldn't switch path: {ex}"}    
        
@router.post("/upload_avatar")
def upload_avatar(data):
    file = data.files['avatar']
    file.save(lollmsElfServer.lollms_paths.personal_user_infos_path/file.filename)
    return {"status": True,"fileName":file.filename}