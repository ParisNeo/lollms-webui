"""
project: lollms
file: lollms_rag_events.py 
author: ParisNeo
description: 
    Events related to socket io model events

"""
from fastapi import APIRouter, Request
from fastapi import HTTPException
from pydantic import BaseModel
import pkg_resources
from lollms.server.elf_server import LOLLMSElfServer
from fastapi.responses import FileResponse
from lollms.binding import BindingBuilder, InstallOption
from ascii_colors import ASCIIColors
from lollms.personality import AIPersonality
from lollms.utilities import load_config, trace_exception, gc, terminate_thread, run_async
from pathlib import Path
from typing import List
import socketio
from datetime import datetime
from functools import partial
import shutil
import threading
import os
from tqdm import tqdm

lollmsElfServer = LOLLMSElfServer.get_instance()


# ----------------------------------- events -----------------------------------------