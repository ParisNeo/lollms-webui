"""
project: lollms_webui
file: lollms_discussion.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes allow users to manipulate the discussion elements.

"""
from fastapi import APIRouter, Request
from lollms.server.elf_server import LOLLMSElfServer
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from lollms.types import MSG_OPERATION_TYPE
from lollms.utilities import detect_antiprompt, remove_text_from_string, trace_exception
from lollms.security import sanitize_path, check_access
from ascii_colors import ASCIIColors
from lollms.databases.discussions_database import DiscussionsDB, Discussion
from typing import List
import shutil
import tqdm
from pathlib import Path
class GenerateRequest(BaseModel):
    text: str

class DatabaseSelectionParameters(BaseModel):
    client_id: str
    name: str

class EditTitleParameters(BaseModel):
    client_id: str
    title: str
    id: int

class MakeTitleParameters(BaseModel):
    id: int

class DeleteDiscussionParameters(BaseModel):
    client_id: str
    id: int

# ----------------------- Defining router and main class ------------------------------

router = APIRouter()
lollmsElfServer:LOLLMSElfServer = LOLLMSElfServer.get_instance()


@router.get("/list_discussions")
def list_discussions():
    discussions = lollmsElfServer.db.get_discussions()
    return discussions


@router.get("/list_databases")
async def list_databases():
   """List all the personal databases in the LoLLMs server."""
   # Retrieve the list of database names
   databases = [f.name for f in lollmsElfServer.lollms_paths.personal_discussions_path.iterdir() if f.is_dir() and (f/"database.db").exists()]
   # Return the list of database names
   return databases


@router.post("/select_database")
def select_database(data:DatabaseSelectionParameters):
    sanitize_path(data.name)
    client = lollmsElfServer.session.get_client(data.client_id)
    

    print(f'Selecting database {data.name}')
    # Create database object
    lollmsElfServer.db = DiscussionsDB(lollmsElfServer, lollmsElfServer.lollms_paths, data.name)
    ASCIIColors.info("Checking discussions database... ",end="")
    lollmsElfServer.db.create_tables()
    lollmsElfServer.db.add_missing_columns()
    lollmsElfServer.config.discussion_db_name = data.name
    ASCIIColors.success("ok")

    if lollmsElfServer.config.auto_save:
        lollmsElfServer.config.save_config()
    
    return {"status":True}


@router.post("/export_discussion")
def export_discussion():
    return {"discussion_text":lollmsElfServer.get_discussion_to()}


class DiscussionEditTitle(BaseModel):
    client_id: str
    title: str
    id: int

@router.post("/edit_title")
async def edit_title(discussion_edit_title: DiscussionEditTitle):
    try:
        client_id = discussion_edit_title.client_id
        title = discussion_edit_title.title
        discussion_id = discussion_edit_title.id
        lollmsElfServer.session.get_client(client_id).discussion = Discussion(lollmsElfServer, discussion_id, lollmsElfServer.db)
        lollmsElfServer.session.get_client(client_id).discussion.rename(title)
        return {'status':True}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}

class DiscussionTitle(BaseModel):
    client_id: str
    id: int
    
@router.post("/make_title")
async def make_title(discussion_title: DiscussionTitle):
    try:
        ASCIIColors.info("Making title")
        discussion_id = discussion_title.id
        discussion = Discussion(lollmsElfServer, discussion_id, lollmsElfServer.db)
        title = lollmsElfServer.make_discussion_title(discussion, discussion_title.client_id)
        discussion.rename(title)
        return {'status':True, 'title':title}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}
    
class DatabaseExport(BaseModel):
    client_id: str


@router.post("/export")
def export(databaseExport:DatabaseExport):
    check_access(lollmsElfServer, databaseExport.client_id)
    return lollmsElfServer.db.export_to_json()



class DiscussionDelete(BaseModel):
    client_id: str
    id: int

@router.post("/delete_discussion")
async def delete_discussion(discussion: DiscussionDelete):
    """
    Executes Python code and returns the output.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """
    check_access(lollmsElfServer, discussion.client_id)

    try:

        client_id           = discussion.client_id
        discussion_id       = discussion.id
        discussion_path = lollmsElfServer.lollms_paths.personal_discussions_path/lollmsElfServer.config.discussion_db_name/f"{discussion_id}"


        lollmsElfServer.session.get_client(client_id).discussion = Discussion(lollmsElfServer, discussion_id, lollmsElfServer.db)
        lollmsElfServer.session.get_client(client_id).discussion.delete_discussion()
        lollmsElfServer.session.get_client(client_id).discussion = None

        shutil.rmtree(discussion_path)
        return {'status':True}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}
    
    
# ----------------------------- import/export --------------------
class DiscussionExport(BaseModel):
    client_id: str
    discussion_ids: List[int]
    export_format: str

@router.post("/export_multiple_discussions")
async def export_multiple_discussions(discussion_export: DiscussionExport):
    check_access(lollmsElfServer, discussion_export.client_id)
    try:
        discussion_ids = discussion_export.discussion_ids
        export_format = discussion_export.export_format

        if export_format=="json":
            discussions = lollmsElfServer.db.export_discussions_to_json(discussion_ids)
        elif export_format=="markdown":
            discussions = lollmsElfServer.db.export_discussions_to_markdown(discussion_ids)
        else:
            discussions = lollmsElfServer.db.export_discussions_to_markdown(discussion_ids)
        return discussions
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}


class DiscussionInfo(BaseModel):
    id: int
    title: str
    messages: List[dict]

class DiscussionImport(BaseModel):
    client_id: str
    jArray: List[DiscussionInfo]

@router.post("/import_multiple_discussions")
async def import_multiple_discussions(discussion_import: DiscussionImport):
    check_access(lollmsElfServer, discussion_import.client_id)
    try:
        discussions = discussion_import.jArray
        lollmsElfServer.db.import_from_json(discussions)
        return discussions
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}



# ------------------------------------------- Files manipulation -----------------------------------------------------
class Identification(BaseModel):
    client_id:str

@router.post("/get_discussion_files_list")
def get_discussion_files_list(data:Identification):
    client = check_access(lollmsElfServer, data.client_id)
    return {"state":True, "files":[{"name":Path(f).name, "size":Path(f).stat().st_size} for f in client.discussion.text_files]+[{"name":Path(f).name, "size":Path(f).stat().st_size} for f in client.discussion.image_files]}

@router.post("/clear_discussion_files_list")
def clear_discussion_files_list(data:Identification):
    client = check_access(lollmsElfServer, data.client_id)
    if lollmsElfServer.personality is None:
        return {"state":False, "error":"No personality selected"}
    client.discussion.remove_all_files()
    return {"state":True}

class RemoveFileData(BaseModel):
    client_id:str
    name:str
    
@router.post("/remove_discussion_file")
def remove_discussion_file(data:RemoveFileData):
    """
    Removes a file form the personality files
    """
    client = check_access(lollmsElfServer, data.client_id)
    
    if lollmsElfServer.personality is None:
        return {"state":False, "error":"No personality selected"}
    try:
        client.discussion.remove_file(data.name)
    except Exception as ex:
        trace_exception(ex)
        return {"state":False, "error": ex}
    return {"state":True}
