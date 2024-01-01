from fastapi import APIRouter
from lollms_webui import LoLLMSWebUI

router = APIRouter()
lollmsWebUI = LoLLMSWebUI.get_instance()

@router.get("/users")
def get_users():
    # Your code here
    pass

@router.post("/users")
def create_user():
    # Your code here
    pass
