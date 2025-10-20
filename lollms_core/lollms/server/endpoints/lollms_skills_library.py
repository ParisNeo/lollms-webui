"""
project: lollms_webui
file: lollms_skills_library.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that allow user to interact with the skills library.

"""
from fastapi import APIRouter, Request
from lollms_webui import LOLLMSWebUI
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from lollms.types import MSG_OPERATION_TYPE
from lollms.utilities import detect_antiprompt, remove_text_from_string, trace_exception
from lollms.security import sanitize_path
from ascii_colors import ASCIIColors
from lollms.databases.discussions_database import DiscussionsDB, Discussion
from lollms.security import check_access
from typing import List

import tqdm
from pathlib import Path
# ----------------------- Defining router and main class ------------------------------

router = APIRouter()
lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()

class ClientInfos(BaseModel):
    client_id: str

class SkillInfos(BaseModel):
    client_id: str
    skill_id: int

class SkillUpdateInfos(BaseModel):
    client_id: str
    skill_id: int
    category: str
    title: str
    content: str

class DeleteSkillInfos(BaseModel):
    client_id: str
    skill_id: int

class CategoryData(BaseModel):
    client_id: str
    category: str


@router.post("/get_skills_library")
def get_skills_library_categories(discussionInfos:ClientInfos):
    return {"status":True, "entries":lollmsElfServer.skills_library.dump()}

@router.post("/get_skills_library_categories")
def get_skills_library_categories(discussionInfos:ClientInfos):
    # get_categories returns a list of strings, each entry is a category
    return {"status":True, "categories":lollmsElfServer.skills_library.get_categories()}

@router.post("/get_skills_library_titles_by_category")
def get_skills_library_titles(categoryData:CategoryData):
    check_access(lollmsElfServer, categoryData.client_id)
    # Get titles returns a list of dict each entry has id and title
    return {"status":True, "titles":lollmsElfServer.skills_library.get_titles_by_category(categoryData.category)}

@router.post("/get_skills_library_titles")
def get_skills_library_titles(clientInfos:ClientInfos):
    check_access(lollmsElfServer, clientInfos.client_id)
    # Get titles returns a list of dict each entry has id and title
    return {"status":True, "titles":lollmsElfServer.skills_library.get_titles()}

@router.post("/get_skills_library_content")
def get_skills_library_content(skillInfos:SkillInfos):
    check_access(lollmsElfServer, skillInfos.client_id)
    # Get the content of the skill from the id, the output is a list of dicts each entry has id, category, title and content
    return {"status":True, "contents":lollmsElfServer.skills_library.get_skill(skillInfos.skill_id)}

@router.post("/delete_skill")
def delete_skill(delSkillInfos:DeleteSkillInfos):
    check_access(lollmsElfServer, delSkillInfos.client_id)
    lollmsElfServer.skills_library.remove_entry(delSkillInfos.skill_id)
    return {"status":True}

@router.post("/edit_skill")
async def edit_skill(skillInfos:SkillUpdateInfos):
    lollmsElfServer.skills_library.update_skill(skillInfos.skill_id, skillInfos.category, skillInfos.title, skillInfos.content)
    return {"status":True}

@router.post("/add_discussion_to_skills_library")
async def add_discussion_to_skills_library(discussionInfos:ClientInfos):
    lollmsElfServer.ShowBlockingMessage("Learning...")
    try:
        client = check_access(lollmsElfServer, discussionInfos.client_id)
        category, title, content = lollmsElfServer.add_discussion_to_skills_library(client)    
        lollmsElfServer.InfoMessage(f"Discussion skill added to skills library:\nTitle: {title}\nCategory: {category}")
    except Exception as ex:
        trace_exception(ex)
        ASCIIColors.error(ex)
        lollmsElfServer.InfoMessage(f"Failed to learn from this discussion because of the follwoing error:\n{ex}")
        return {"status":False,"error":f"{ex}"}
    return {"status":True}
