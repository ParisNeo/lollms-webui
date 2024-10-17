"""
project: lollms_user
file: lollms_user.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes allow users to do advanced stuff like executing code.

"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse
from lollms_webui import LOLLMSWebUI
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse
from lollms.types import MSG_OPERATION_TYPE
from lollms.main_config import BaseConfig
from lollms.utilities import detect_antiprompt, remove_text_from_string, trace_exception, show_yes_no_dialog, add_period
from lollms.security import sanitize_path, forbid_remote_access, check_access, sanitize_svg, sanitize_path_from_endpoint
from ascii_colors import ASCIIColors
from lollms.databases.discussions_database import DiscussionsDB
from lollms.client_session import Client
from pathlib import Path
import tqdm
from fastapi import FastAPI, UploadFile, File
import shutil
import os
import platform
import string
import re
import subprocess   
from typing import Optional

def validate_file_path(path):
    try:
        sanitized_path = sanitize_path(path, allow_absolute_path=False)
        return sanitized_path is not None
    except Exception as e:
        print(f"Path validation error: {str(e)}")
        return False

from utilities.execution_engines.python_execution_engine import execute_python
from utilities.execution_engines.latex_execution_engine import execute_latex
from utilities.execution_engines.shell_execution_engine import execute_bash
from utilities.execution_engines.javascript_execution_engine import execute_javascript
from utilities.execution_engines.html_execution_engine import execute_html

from utilities.execution_engines.mermaid_execution_engine import execute_mermaid
from utilities.execution_engines.graphviz_execution_engine import execute_graphviz
from utilities.execution_engines.svg_execution_engine import execute_svg




# ----------------------- Defining router and main class ------------------------------

router = APIRouter()
lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()
