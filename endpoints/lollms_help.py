"""
project: lollms_user
file: lollms_user.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes allow users to do advanced stuff like executing code.

"""

import os
import platform
import re
import shutil
import string
import subprocess
from pathlib import Path
from typing import Optional

import tqdm
from ascii_colors import ASCIIColors
from fastapi import (APIRouter, FastAPI, File, HTTPException, Request,
                     UploadFile)
from fastapi.responses import FileResponse
from lollms.client_session import Client
from lollms.databases.discussions_database import DiscussionsDB
from lollms.main_config import BaseConfig
from lollms.security import (check_access, forbid_remote_access, sanitize_path,
                             sanitize_path_from_endpoint, sanitize_svg)
from lollms.types import MSG_OPERATION_TYPE
from lollms.utilities import (add_period, detect_antiprompt,
                              remove_text_from_string, show_yes_no_dialog,
                              trace_exception)
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse

from lollms_webui import LOLLMSWebUI


def validate_file_path(path):
    try:
        sanitized_path = sanitize_path(path, allow_absolute_path=False)
        return sanitized_path is not None
    except Exception as e:
        print(f"Path validation error: {str(e)}")
        return False


# ----------------------- Defining router and main class ------------------------------

router = APIRouter()
lollmsElfServer: LOLLMSWebUI = LOLLMSWebUI.get_instance()
