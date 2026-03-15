from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional
from base64 import b64encode
import io
from PIL import Image
from fastapi import APIRouter
from lollms_webui import LOLLMSWebUI
from pydantic import BaseModel
from typing import List, Dict
from ascii_colors import trace_exception
from lollms.security import check_access
import yaml

router = APIRouter()
lollmsElfServer = LOLLMSWebUI.get_instance()

class ServiceListingRequest(BaseModel):
    client_id: str



@router.post("/list_ttm_services")
async def list_ttm_services(request: ServiceListingRequest) -> List[Dict[str, str]]:
    """
    Endpoint that returns a list of TTM services by scanning subfolders in services_zoo_path.
    
    Args:
        request (ServiceListingRequest): The request body containing the client_id.
    
    Returns:
        List[Dict[str, str]]: A list of TTM service dictionaries containing name, caption, and help.
    """
    # Validate the client_id
    check_access(lollmsElfServer, request.client_id)
    
    # Get the services directory path
    services_path = lollmsElfServer.lollms_paths.services_zoo_path/"ttm"
    
    # Initialize empty list for services
    ttm_services = []
    
    # Check if the directory exists
    if not services_path.exists() or not services_path.is_dir():
        return ttm_services  # Return empty list if directory doesn't exist
    
    # Iterate through subfolders
    for service_folder in services_path.iterdir():
        if service_folder.is_dir() and service_folder.stem not in [".git", ".vscode"]:
            # Look for config.yaml in each subfolder
            config_file = service_folder / "config.yaml"
            if config_file.exists():
                try:
                    # Read and parse the YAML file
                    with open(config_file, 'r') as f:
                        config = yaml.safe_load(f)
                    
                    # Build service dictionary
                    service_info = {
                        "name": service_folder.name,
                        "caption": config.get("caption", service_folder.name),
                        "help": config.get("help", f"{service_folder.name} text to image services")
                    }
                    ttm_services.append(service_info)
                except Exception as e:
                    # Log error if needed, skip invalid config files
                    continue
    
    return ttm_services

@router.post("/list_ttm_services")
async def list_ttm_services(request: ServiceListingRequest):
    """
    Dumb endpoint that returns a static list of TTM services.
    
    Args:
        request (ServiceListingRequest): The request body containing the client_id.
    
    Returns:
        List[str]: A list of TTM service names.
    """
    # Validate the client_id (dumb validation for demonstration)
    check_access(lollmsElfServer, request.client_id)
    
    
    # Static list of TTM services
    ttm_services = [
                    {"name": "suno", "caption":"Suno AI",  "help":"Suno ai"},
                    {"name": "music_gen", "caption":"Music Gen",  "help":"Music Gen"},
                ]
    return ttm_services


@router.post("/get_active_ttm_settings")
async def get_active_ttm_settmngs(request: Request):
    data = await request.json()
    check_access(lollmsElfServer,data["client_id"])
    print("- Retreiving ttm settmngs")
    if lollmsElfServer.ttm is not None:
        if hasattr(lollmsElfServer.ttm,"service_config"):
            return lollmsElfServer.ttm.service_config.config_template.template
        else:
            return {}
    else:
        return {}

@router.post("/set_active_ttm_settings")
async def set_active_ttm_settmngs(request: Request):
    data = await request.json()
    check_access(lollmsElfServer,data["client_id"])
    settmngs = data["settmngs"]
    """
    Sets the active ttm settmngs.

    :param request: The Request object.
    :return: A JSON response with the status of the operation.
    """

    try:
        print("- Settmng ttm settmngs")
        
        if lollmsElfServer.ttm is not None:
            if hasattr(lollmsElfServer.ttm,"service_config"):
                lollmsElfServer.ttm.service_config.update_template(settmngs)
                lollmsElfServer.ttm.service_config.config.save_config()
                lollmsElfServer.ttm.settmngs_updated()
                return {'status':True}
            else:
                return {'status':False}
        else:
            return {'status':False}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}