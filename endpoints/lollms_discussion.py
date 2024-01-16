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
from ascii_colors import ASCIIColors
from api.db import DiscussionsDB, Discussion

from safe_store.text_vectorizer import TextVectorizer, VectorizationMethod, VisualizationMethod
import tqdm

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
   databases = [f.name for f in lollmsElfServer.lollms_paths.personal_databases_path.iterdir() if f.suffix == ".db"]
   # Return the list of database names
   return databases

@router.post("/select_database")
def select_database(data:DatabaseSelectionParameters):
    if not data.name.endswith(".db"):
        data.name += ".db"
    print(f'Selecting database {data.name}')
    # Create database object
    lollmsElfServer.db = DiscussionsDB(lollmsElfServer.lollms_paths.personal_databases_path/data.name)
    ASCIIColors.info("Checking discussions database... ",end="")
    lollmsElfServer.db.create_tables()
    lollmsElfServer.db.add_missing_columns()
    lollmsElfServer.config.db_path = data.name
    ASCIIColors.success("ok")

    if lollmsElfServer.config.auto_save:
        lollmsElfServer.config.save_config()
    
    if lollmsElfServer.config.data_vectorization_activate and lollmsElfServer.config.use_discussions_history:
        try:
            ASCIIColors.yellow("0- Detected discussion vectorization request")
            folder = lollmsElfServer.lollms_paths.personal_databases_path/"vectorized_dbs"
            folder.mkdir(parents=True, exist_ok=True)
            lollmsElfServer.long_term_memory = TextVectorizer(
                vectorization_method=VectorizationMethod.TFIDF_VECTORIZER,#=VectorizationMethod.BM25_VECTORIZER,
                database_path=folder/lollmsElfServer.config.db_path,
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


@router.post("/edit_title")
async def edit_title(request: Request):
    """
    Executes Python code and returns the output.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """

    try:
        data = (await request.json())
        client_id           = data.get("client_id")
        title               = data.get("title")
        discussion_id       = data.get("id")
        lollmsElfServer.connections[client_id]["current_discussion"] = Discussion(discussion_id, lollmsElfServer.db)
        lollmsElfServer.connections[client_id]["current_discussion"].rename(title)
        return {'status':True}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}
        
@router.post("/make_title")
async def make_title(request: Request):
    """
    Executes Python code and returns the output.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """

    try:
        data = (await request.json())

        ASCIIColors.info("Making title")
        discussion_id       = data.get("id")
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


@router.post("/delete_discussion")
async def delete_discussion(request: Request):
    """
    Executes Python code and returns the output.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """

    try:
        data = (await request.json())

        client_id       = data.client_id
        discussion_id   = data.id
        lollmsElfServer.connections[client_id]["current_discussion"] = Discussion(discussion_id, lollmsElfServer.db)
        lollmsElfServer.connections[client_id]["current_discussion"].delete_discussion()
        lollmsElfServer.connections[client_id]["current_discussion"] = None
        return {'status':True}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}
    
    
# ----------------------------- import/export --------------------

@router.post("/export_multiple_discussions")
async def export_multiple_discussions(request: Request):
    """
    Opens code in vs code.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """

    try:
        data = (await request.json())
        discussion_ids = data["discussion_ids"]
        export_format = data["export_format"]

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
    
@router.post("/import_multiple_discussions")
async def import_multiple_discussions(request: Request):
    """
    Opens code in vs code.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """

    try:
        discussions = (await request.json())["jArray"]
        lollmsElfServer.db.import_from_json(discussions)
        return discussions
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}
