"""
project: lollms
file: lollms_binding_infos.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes are specific to bindings

"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
import pkg_resources
from lollms.server.elf_server import LOLLMSElfServer
from lollms.binding import BindingBuilder, InstallOption
from ascii_colors import ASCIIColors
from lollms.utilities import load_config, trace_exception, gc
from lollms.security import sanitize_path_from_endpoint, sanitize_path, check_access
from lollms.security import check_access
from pathlib import Path
from typing import List, Any
import json
import os
# ----------------------------------- Personal files -----------------------------------------

class ClientAuthentication(BaseModel):
    client_id: str  = Field(...)

class ReloadBindingParams(BaseModel):
    binding_name: str = Field(..., min_length=1, max_length=50)

class BindingInstallParams(BaseModel):
    client_id: str
    name: str = Field(..., min_length=1, max_length=50)


# ----------------------- Defining router and main class ------------------------------
router = APIRouter()
lollmsElfServer = LOLLMSElfServer.get_instance()


# ----------------------------------- Listing -----------------------------------------
@router.get("/list_bindings")
def list_bindings():
    """
    List all available bindings in the Lollms server.

    Returns:
        List[str]: A list of binding names.
    """    
    bindings_dir = lollmsElfServer.lollms_paths.bindings_zoo_path  # replace with the actual path to the models folder
    bindings=[]
    for f in bindings_dir.iterdir():
        if f.stem!="binding_template":
            card = f/"binding_card.yaml"
            if card.exists():
                try:
                    bnd = load_config(card)
                    bnd["name"]=f.stem
                    bnd["folder"]=f.stem
                    installed = (lollmsElfServer.lollms_paths.personal_configuration_path/"bindings"/f.stem/f"config.yaml").exists()
                    bnd["installed"]=installed
                    ui_file_path = f/"ui.html"
                    if ui_file_path.exists():
                        with ui_file_path.open("r") as file:
                            text_content = file.read()
                            bnd["ui"]=text_content
                    else:
                        bnd["ui"]=None
                    disclaimer_file_path = f/"disclaimer.md"
                    if disclaimer_file_path.exists():
                        with disclaimer_file_path.open("r") as file:
                            text_content = file.read()
                            bnd["disclaimer"]=text_content
                    else:
                        bnd["disclaimer"]=None
                    icon_file = lollmsElfServer.find_extension(lollmsElfServer.lollms_paths.bindings_zoo_path/f"{f.name}", "logo", [".svg",".gif",".png"])
                    if icon_file is not None:
                        icon_path = Path(f"bindings/{f.name}/logo{icon_file.suffix}")
                        bnd["icon"]=str(icon_path)

                    bindings.append(bnd)
                except Exception as ex:
                    print(f"Couldn't load backend card : {f}\n\t{ex}")
    return bindings

# ----------------------------------- Reloading ----------------------------------------
class BindingReloadRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

@router.post("/reload_binding")
async def reload_binding(request: BindingReloadRequest):
    """
    Reloads a binding.

    :param request: The BindingReloadRequest object.
    :return: A JSON response with the status of the operation.
    """

    try:
        print(f"Reloading binding selected : {request.name}")
        safe_name = sanitize_path(os.path.basename(request.name)) # sanitize the file path to prevent path traversal
        lollmsElfServer.config["binding_name"]=safe_name
        if lollmsElfServer.binding:
            lollmsElfServer.binding.destroy_model()
        lollmsElfServer.binding = None
        lollmsElfServer.model = None
        for per in lollmsElfServer.mounted_personalities:
            if per is not None:
                per.model = None
        gc.collect()
        lollmsElfServer.binding = BindingBuilder().build_binding(lollmsElfServer.config, lollmsElfServer.lollms_paths, InstallOption.INSTALL_IF_NECESSARY, lollmsCom=lollmsElfServer)
        lollmsElfServer.model = None
        lollmsElfServer.config.save_config()
        ASCIIColors.green("Binding loaded successfully")
        return {"status":True}
    except Exception as ex:
        ASCIIColors.error(f"Couldn't build binding: [{ex}]")
        trace_exception(ex)
        return {"status":False, 'error':str(ex)}
    

# ----------------------------------- Installation/Uninstallation/Reinstallation ----------------------------------------

@router.post("/install_binding")
def install_binding(data:BindingInstallParams):
    """Install a new binding on the server.
    
    Args:
        data (BindingInstallParams): Parameters required for installation.
        format:
            name: str : the name of the binding
    
    Returns:
        dict: Status of operation.
    """
    check_access(lollmsElfServer, data.client_id)
    sanitize_path_from_endpoint(data.name)    
    
    ASCIIColors.info(f"- Reinstalling binding {data.name}...")
    try:
        lollmsElfServer.info("Unmounting binding and model")
        lollmsElfServer.info("Installing binding")
        cfg = lollmsElfServer.config.copy()
        cfg.binding_name = data.name
        BindingBuilder().build_binding(cfg, lollmsElfServer.lollms_paths, InstallOption.FORCE_INSTALL, lollmsCom=lollmsElfServer)
        lollmsElfServer.success("Binding installed successfully")
        return {"status": True}
    except Exception as ex:
        lollmsElfServer.error(f"Couldn't build binding: [{ex}]")
        trace_exception(ex)
        return {"status":False, 'error':str(ex)}

@router.post("/reinstall_binding")
def reinstall_binding(data:BindingInstallParams):
    """Reinstall an already installed binding on the server.
    
    Args:
        data (BindingInstallParams): Parameters required for reinstallation.
        format:
            name: str : the name of the binding
    
    Returns:
        dict: Status of operation.
    """    
    check_access(lollmsElfServer, data.client_id)
    ASCIIColors.info(f"- Reinstalling binding {data.name}...")
    try:
        ASCIIColors.info("Unmounting binding and model")
        del lollmsElfServer.binding
        lollmsElfServer.binding = None
        gc.collect()
        ASCIIColors.info("Reinstalling binding")
        lollmsElfServer.config.binding_name = sanitize_path(data.name)
        lollmsElfServer.binding =  BindingBuilder().build_binding(lollmsElfServer.config, lollmsElfServer.lollms_paths, InstallOption.FORCE_INSTALL, lollmsCom=lollmsElfServer)
        lollmsElfServer.success("Binding reinstalled successfully")
        lollmsElfServer.model = lollmsElfServer.binding.build_model()
        for per in lollmsElfServer.mounted_personalities:
            if per is not None:
                per.model = lollmsElfServer.model
        return {"status": True}
    except Exception as ex:
        ASCIIColors.error(f"Couldn't build binding: [{ex}]")
        trace_exception(ex)
        return {"status":False, 'error':str(ex)}

@router.post("/unInstall_binding")
def unInstall_binding(data:BindingInstallParams):
    """Uninstall an installed binding from the server.
    
    Args:
        data (BindingInstallParams): Parameters required for uninstallation.
        format:
            name: str : the name of the binding
    Returns:
        dict: Status of operation.
    """    
    check_access(lollmsElfServer, data.client_id)
    ASCIIColors.info(f"- Reinstalling binding {data.name}...")
    try:
        ASCIIColors.info("Unmounting binding and model")
        if lollmsElfServer.binding is not None:
            del lollmsElfServer.binding
            lollmsElfServer.binding = None
            gc.collect()
        ASCIIColors.info("Uninstalling binding")
        old_bn = lollmsElfServer.config.binding_name
        lollmsElfServer.config.binding_name = sanitize_path(data.name)
        lollmsElfServer.binding =  BindingBuilder().build_binding(lollmsElfServer.config, lollmsElfServer.lollms_paths, InstallOption.NEVER_INSTALL, lollmsCom=lollmsElfServer)
        lollmsElfServer.binding.uninstall()
        ASCIIColors.green("Uninstalled successful")
        if old_bn!=lollmsElfServer.config.binding_name:
            lollmsElfServer.config.binding_name = old_bn
            lollmsElfServer.binding =  BindingBuilder().build_binding(lollmsElfServer.config, lollmsElfServer.lollms_paths, lollmsCom=lollmsElfServer)
            lollmsElfServer.model = lollmsElfServer.binding.build_model()
            for per in lollmsElfServer.mounted_personalities:
                if per is not None:
                    per.model = lollmsElfServer.model
        else:
            lollmsElfServer.config.binding_name = None
        if lollmsElfServer.config.auto_save:
            ASCIIColors.info("Saving configuration")
            lollmsElfServer.config.save_config()
            
        return {"status": True}
    except Exception as ex:
        ASCIIColors.error(f"Couldn't build binding: [{ex}]")
        trace_exception(ex)
        return {"status":False, 'error':str(ex)}     
    
# ----------------------------------- Bet binding settings ----------------------------------------

@router.post("/get_active_binding_settings")
async def get_active_binding_settings(request: Request):
    data = await request.json()
    check_access(lollmsElfServer,data["client_id"])
    print("- Retreiving binding settings")
    if lollmsElfServer.binding is not None:
        if hasattr(lollmsElfServer.binding,"binding_config"):
            return lollmsElfServer.binding.binding_config.config_template.template
        else:
            return {}
    else:
        return {}

# class BindingSettingsRequest(BaseModel):
#     value: list 

# @router.post("/set_active_binding_settings")
# async def set_active_binding_settings(request: BindingSettingsRequest):

@router.post("/set_active_binding_settings")
async def set_active_binding_settings(request: Request):
    data = await request.json()
    check_access(lollmsElfServer,data["client_id"])
    settings = data["settings"]
    """
    Sets the active binding settings.

    :param request: The BindingSettingsRequest object.
    :return: A JSON response with the status of the operation.
    """

    try:
        print("- Setting binding settings")
        
        if lollmsElfServer.binding is not None:
            if hasattr(lollmsElfServer.binding,"binding_config"):
                lollmsElfServer.binding.binding_config.update_template(settings)
                lollmsElfServer.binding.binding_config.config.save_config()
                lollmsElfServer.binding.settings_updated()
                if lollmsElfServer.config.auto_save:
                    ASCIIColors.info("Saving configuration")
                    lollmsElfServer.config.save_config()
                return {'status':True}
            else:
                return {'status':False}
        else:
            return {'status':False}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}
    
@router.post("/update_binding_settings")
def update_binding_settings(request: ClientAuthentication):
    check_access(lollmsElfServer, request.client_id)
    if lollmsElfServer.binding:
        lollmsElfServer.binding.settings_updated()
        ASCIIColors.green("Binding setting updated successfully")
        return {"status":True}
    else:
        return {"status":False, 'error':"no binding found"}