from fastapi import APIRouter, Request, HTTPException, Depends, Header
import uuid
from fastapi import Request, Response
from lollms_webui import LOLLMSWebUI
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse
from lollms.types import MSG_OPERATION_TYPE
from lollms.utilities import detect_antiprompt, remove_text_from_string, trace_exception
from lollms.security import sanitize_path, check_access
from ascii_colors import ASCIIColors
from lollms.databases.discussions_database import DiscussionsDB, Discussion
from lollms.security import check_access
from typing import List, Optional, Union
from pathlib import Path
from safe_store import SafeStore
import sqlite3
import secrets
import time
import shutil
import os
from datetime import datetime, timedelta
import asyncio
from contextlib import asynccontextmanager
import hashlib
# ----------------------- Defining router and main class ------------------------------

router = APIRouter()
lollmsElfServer: LOLLMSWebUI = LOLLMSWebUI.get_instance()

# ----------------------- RAG System ------------------------------
class RAGQuery(BaseModel):
    query: str = Field(..., description="The query to process using RAG")
    key: str = Field(..., description="The key to identify the user")

class RAGResponse(BaseModel):
    answer: str = Field(..., description="The generated answer")
    sources: List[str] = Field(..., description="List of sources used for the answer")

class IndexDocument(BaseModel):
    title: str = Field(..., description="The title of the document")
    content: str = Field(..., description="The content to be indexed")
    path: str = Field(default="unknown", description="The path of the document")
    key: str = Field(..., description="The key to identify the user")

class IndexResponse(BaseModel):
    success: bool = Field(..., description="Indicates if the indexing was successful")
    message: str = Field(..., description="Additional information about the indexing process")

class DocumentResponse(BaseModel):
    success: bool
    message: str

class RAGChunk(BaseModel):
    id : int
    chunk_id : int
    doc_title : str
    doc_path : str
    text : str
    nb_tokens : int
    distance : float



class AuthenticationModel(BaseModel):
    client_id: str = Field(..., description="The client id to authentify the user")

def get_user_vectorizer(user_key: str):
    small_key = hashlib.md5(user_key.encode()).hexdigest()[:8]
    user_folder = lollmsElfServer.lollms_paths.personal_outputs_path / str(user_key)
    user_folder.mkdir(parents=True, exist_ok=True)

    return SafeStore(
        ""
    )

async def validate_key(key: str):
    if lollmsElfServer.config.lollms_access_keys and key not in lollmsElfServer.config.lollms_access_keys:
        raise HTTPException(status_code=403, detail="Invalid Key")
    return key

@router.post("/add_document", response_model=DocumentResponse)
async def add_document(doc: IndexDocument):
    await validate_key(doc.key)
    vectorizer = get_user_vectorizer(doc.key)
    vectorizer.add_document(title=doc.title, text=doc.content, path=doc.path)
    return DocumentResponse(success=True, message="Document added successfully.")

@router.post("/remove_document/{document_id}", response_model=DocumentResponse)
async def remove_document(document_id: int, key: str):
    await validate_key(key)
    vectorizer = get_user_vectorizer(key)
    doc_hash = vectorizer.get_document_hash(document_id)
    vectorizer.remove_document(doc_hash)
    return DocumentResponse(success=True, message="Document removed successfully.")

class IndexDatabaseRequest(BaseModel):
    key: str

@router.post("/index_database", response_model=DocumentResponse)
async def index_database(request: IndexDatabaseRequest):
    key = request.key
    await validate_key(key)
    vectorizer = get_user_vectorizer(key)
    vectorizer.build_index()
    return DocumentResponse(success=True, message="Database indexed successfully.")

@router.post("/search", response_model=List[RAGChunk])
async def search(query: RAGQuery):
    await validate_key(query.key)
    vectorizer = get_user_vectorizer(query.key)
    chunks = vectorizer.search(query.query)
    return [
    RAGChunk(
        id=c.id,
        chunk_id=c.chunk_id,
        title=c.doc.title,
        path=c.doc.path,
        text=c.text,
        nb_tokens=c.nb_tokens,
        distance=c.distance
    )
    for c in chunks
]

@router.delete("/wipe_database", response_model=DocumentResponse)
async def wipe_database(key: str):
    await validate_key(key)
    key = sanitize_path(key)
    user_folder = lollmsElfServer.lollms_paths / str(key)
    shutil.rmtree(user_folder, ignore_errors=True)
    return DocumentResponse(success=True, message="Database wiped successfully.")


# Note: LightRAG support has been removed from LoLLMs
# The /start_rag_server endpoint previously supported LightRAG but has been deprecated

