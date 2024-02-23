"""
project: lollms_webui
file: lollms_discussion.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes allow users to manipulate the discussion elements.

"""
from fastapi import APIRouter, Request
from lollms_webui import LOLLMSWebUI
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from lollms.types import MSG_TYPE
from lollms.utilities import detect_antiprompt, remove_text_from_string, trace_exception
from lollms.security import sanitize_path
from ascii_colors import ASCIIColors
from api.db import DiscussionsDB, Discussion
from typing import List

from safe_store.text_vectorizer import TextVectorizer, VectorizationMethod, VisualizationMethod
import tqdm
from pathlib import Path
class GenerateRequest(BaseModel):
    text: str

class DatabaseSelectionParameters(BaseModel):
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
lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()


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
    print(f'Selecting database {data.name}')
    # Create database object
    lollmsElfServer.db = DiscussionsDB(lollmsElfServer.lollms_paths, data.name)
    ASCIIColors.info("Checking discussions database... ",end="")
    lollmsElfServer.db.create_tables()
    lollmsElfServer.db.add_missing_columns()
    lollmsElfServer.config.discussion_db_name = data.name
    ASCIIColors.success("ok")

    if lollmsElfServer.config.auto_save:
        lollmsElfServer.config.save_config()
    
    if lollmsElfServer.config.data_vectorization_activate and lollmsElfServer.config.activate_ltm:
        try:
            ASCIIColors.yellow("0- Detected discussion vectorization request")
            folder = lollmsElfServer.lollms_paths.personal_discussions_path/"vectorized_dbs"
            folder.mkdir(parents=True, exist_ok=True)
            lollmsElfServer.long_term_memory = TextVectorizer(
                vectorization_method=VectorizationMethod.TFIDF_VECTORIZER,#=VectorizationMethod.BM25_VECTORIZER,
                database_path=folder/lollmsElfServer.config.discussion_db_name,
                data_visualization_method=VisualizationMethod.PCA,#VisualizationMethod.PCA,
                save_db=True
            )
            ASCIIColors.yellow("1- Exporting discussions")
            lollmsElfServer.info("Exporting discussions")
            discussions = lollmsElfServer.db.export_all_as_markdown_list_for_vectorization()
            ASCIIColors.yellow("2- Adding discussions to vectorizer")
            lollmsElfServer.info("Adding discussions to vectorizer")
            index = 0
            nb_discussions = len(discussions)

            for (title,discussion) in tqdm(discussions):
                lollmsElfServer.sio.emit('update_progress',{'value':int(100*(index/nb_discussions))})
                index += 1
                if discussion!='':
                    skill = lollmsElfServer.learn_from_discussion(title, discussion)
                    lollmsElfServer.long_term_memory.add_document(title, skill, chunk_size=lollmsElfServer.config.data_vectorization_chunk_size, overlap_size=lollmsElfServer.config.data_vectorization_overlap_size, force_vectorize=False, add_as_a_bloc=False)
            ASCIIColors.yellow("3- Indexing database")
            lollmsElfServer.info("Indexing database",True, None)
            lollmsElfServer.long_term_memory.index()
            ASCIIColors.yellow("Ready")
        except Exception as ex:
            lollmsElfServer.error(f"Couldn't vectorize the database:{ex}")
            return {"status":False}

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
        lollmsElfServer.connections[client_id]["current_discussion"] = Discussion(discussion_id, lollmsElfServer.db)
        lollmsElfServer.connections[client_id]["current_discussion"].rename(title)
        return {'status':True}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}

class DiscussionTitle(BaseModel):
    id: int
    
@router.post("/make_title")
async def make_title(discussion_title: DiscussionTitle):
    try:
        ASCIIColors.info("Making title")
        discussion_id = discussion_title.id
        discussion = Discussion(discussion_id, lollmsElfServer.db)
        title = lollmsElfServer.make_discussion_title(discussion)
        discussion.rename(title)
        return {'status':True, 'title':title}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}
    
    
@router.get("/export")
def export():
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

    try:

        client_id           = discussion.client_id
        discussion_id       = discussion.id
        lollmsElfServer.connections[client_id]["current_discussion"] = Discussion(discussion_id, lollmsElfServer.db)
        lollmsElfServer.connections[client_id]["current_discussion"].delete_discussion()
        lollmsElfServer.connections[client_id]["current_discussion"] = None
        return {'status':True}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}
    
    
# ----------------------------- import/export --------------------
class DiscussionExport(BaseModel):
    discussion_ids: List[int]
    export_format: str

@router.post("/export_multiple_discussions")
async def export_multiple_discussions(discussion_export: DiscussionExport):
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
    content: str

class DiscussionImport(BaseModel):
    jArray: List[DiscussionInfo]

@router.post("/import_multiple_discussions")
async def import_multiple_discussions(discussion_import: DiscussionImport):
    try:
        discussions = discussion_import.jArray
        lollmsElfServer.db.import_from_json(discussions)
        return discussions
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}
