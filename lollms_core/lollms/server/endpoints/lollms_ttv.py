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
from ascii_colors import ASCIIColors
import yaml 

router = APIRouter()
lollmsElfServer = LOLLMSWebUI.get_instance()


# Define a Pydantic model for the request body
class ServiceListingRequest(BaseModel):
    client_id: str

class TTVServiceGetConfigRequest(BaseModel):
    client_id: str
    service_name: str

class TTVServiceSetConfigRequest(BaseModel):
    client_id: str
    service_name: str


@router.post("/list_ttv_services")
async def list_ttv_services(request: ServiceListingRequest) -> List[Dict[str, str]]:
    """
    Endpoint that returns a list of TTV services by scanning subfolders in services_zoo_path.
    
    Args:
        request (ServiceListingRequest): The request body containing the client_id.
    
    Returns:
        List[Dict[str, str]]: A list of TTV service dictionaries containing name, caption, and help.
    """
    # Validate the client_id
    check_access(lollmsElfServer, request.client_id)
    
    # Get the services directory path
    services_path = lollmsElfServer.lollms_paths.services_zoo_path/"ttv"
    
    # Initialize empty list for services
    ttv_services = []
    
    # Check if the directory exists
    if not services_path.exists() or not services_path.is_dir():
        return ttv_services  # Return empty list if directory doesn't exist
    
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
                        "help": config.get("help", f"{service_folder.name} text to video services")
                    }
                    ttv_services.append(service_info)
                except Exception as e:
                    # Log error if needed, skip invalid config files
                    continue
    
    return ttv_services

@router.post("/get_active_ttv_settings")
async def get_active_ttv_settings(request: Request):
    data = await request.json()
    check_access(lollmsElfServer,data["client_id"])
    print("- Retreiving ttv settings")
    if lollmsElfServer.ttv is not None:
        if hasattr(lollmsElfServer.ttv,"service_config"):
            return lollmsElfServer.ttv.service_config.config_template.template
        else:
            return {}
    else:
        return {}


@router.post("/set_active_ttv_settings")
async def set_active_ttv_settings(request: Request):
    data = await request.json()
    check_access(lollmsElfServer,data["client_id"])
    settings = data["settings"]
    """
    Sets the active ttv settings.

    :param request: The ttvSettingsRequest object.
    :return: A JSON response with the status of the operation.
    """

    try:
        print("- Setting ttv settings")
        
        if lollmsElfServer.ttv is not None:
            if hasattr(lollmsElfServer.ttv,"service_config"):
                lollmsElfServer.ttv.service_config.update_template(settings)
                lollmsElfServer.ttv.service_config.config.save_config()
                lollmsElfServer.ttv.settings_updated()
                return {'status':True}
            else:
                return {'status':False}
        else:
            return {'status':False}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}