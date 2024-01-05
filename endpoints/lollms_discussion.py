from fastapi import APIRouter
from lollms_webui import LOLLMSWebUI
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from lollms.types import MSG_TYPE
from lollms.utilities import detect_antiprompt, remove_text_from_string
from ascii_colors import ASCIIColors

class GenerateRequest(BaseModel):
    text: str


router = APIRouter()
elf_server = LOLLMSWebUI.get_instance()

@router.post("/generate")
def lollms_generate(request_data: GenerateRequest):
    pass

@router.get("/list_discussions")
def list_discussions():
    discussions = elf_server.db.get_discussions()
    return discussions

