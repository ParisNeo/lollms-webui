"""
project: lollms_{endpoint category name with no spaces}
file: lollms_{endpoint category name with no spaces}.py 
author: ParisNeo
description: 
    {description of the endpoints hosted in this file}

"""
from fastapi import APIRouter, Request
# Use pydentic for validating the endpoint data
from pydantic import BaseModel, Field
from lollms.server.elf_server import LOLLMSElfServer
from lollms.security import check_access

#Use this only if you need to check that some unusual libraries are installed
from lollms.utilities import PackageManager
if not PackageManager.check_package_installed("package name as in the import"):
    PackageManager.install_or_update("package name as in the pip install")
# ----------------------- Defining router and main class ------------------------------

router = APIRouter()
lollmsElfServer:LOLLMSElfServer = LOLLMSElfServer.get_instance()


# ----------------------- types ------------------------------
# THis is the basic simple client authentication endpoint
class ClientAuthentication(BaseModel):
    client_id: str  = Field(...)


# Example post endpoint

@router.post("/example_endpoint") # change that depending on the app
def example_endpoint(request: ClientAuthentication):
    check_access(lollmsElfServer, request.client_id) # THis is mandatory to all post endpoints to protect access to lollms
    # Here you can do the work then return the output