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
import yaml
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


# ----------------------------------- Endpoints -----------------------------------------

from datetime import datetime
from pathlib import Path

@router.get("/list_function_calls")
async def list_function_calls():
    """List all available function calls in the functions zoo and custom functions zoo"""
    functions_zoo_path = lollmsElfServer.lollms_paths.functions_zoo_path
    custom_function_calls_path = lollmsElfServer.lollms_paths.custom_function_calls_path
    function_calls = []
    
    # Helper function to process a directory and append function calls
    def process_directory(directory, category_name):
        for fn_dir in directory.iterdir():
            if fn_dir.is_dir():
                yaml_file = fn_dir / "config.yaml"
                py_file = fn_dir / "function.py"
                
                if yaml_file.exists() and py_file.exists():
                    try:
                        with open(yaml_file, "r") as f:
                            config = yaml.safe_load(f)
                            
                            # Ensure creation_date_time and last_update_date_time exist
                            if "creation_date_time" not in config:
                                config["creation_date_time"] = datetime.now().isoformat()
                            if "last_update_date_time" not in config:
                                config["last_update_date_time"] = datetime.now().isoformat()
                            
                            # Save the updated YAML file if changes were made
                            with open(yaml_file, "w") as f:
                                yaml.safe_dump(config, f)
                            
                            # Check if the function is mounted
                            mounted = False
                            selected = False
                            try:
                                for mounted_function in lollmsElfServer.config.mounted_function_calls:
                                    if mounted_function["name"] == config.get("name", fn_dir.name):
                                        mounted = True
                                        selected = mounted_function.get("selected", False)
                                        break
                            except:
                                pass
                            function_info = {
                                "name": config.get("function_name", fn_dir.name),
                                "category":  config.get("name", fn_dir.parent.name),
                                "description": config.get("description", ""),
                                "parameters": config.get("parameters", {}),
                                "returns": config.get("returns", {}),
                                "examples": config.get("examples", []),
                                "author": config.get("author", "Unknown"),
                                "version": config.get("version", "1.0.0"),
                                "category": category_name,
                                "creation_date_time": config.get("creation_date_time"),
                                "last_update_date_time": config.get("last_update_date_time"),
                                "mounted": mounted,
                                "selected": selected
                            }
                            function_calls.append(function_info)
                    except Exception as e:
                        trace_exception(e)
                        ASCIIColors.error(f"Error loading function {fn_dir.name}: {e}")
    
    # Process the main functions zoo
    for category_dir in functions_zoo_path.iterdir():
        if category_dir.is_dir():
            process_directory(category_dir, category_dir.name)
    
    # Process the custom functions zoo under the "custom" category
    if custom_function_calls_path.exists():
        process_directory(custom_function_calls_path, "custom")
    
    return {"function_calls": function_calls}

@router.get("/list_mounted_function_calls")
async def list_mounted_function_calls():
    """List currently mounted function calls"""
    mounted = [fc["name"] for fc in lollmsElfServer.config.mounted_function_calls if fc["mounted"]]
    return {"mounted_function_calls": mounted}

@router.post("/mount_function_call")
async def mount_function_call(request: Request):
    """Mount a function call to make it available to the LLM"""
    data = await request.json()
    client_id = data.get("client_id")
    function_category = data.get("function_category")
    function_name = data.get("function_name")

    if not check_access(lollmsElfServer, client_id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Validate function exists
    if function_category!="custom":
        fn_dir = lollmsElfServer.lollms_paths.functions_zoo_path / function_category / function_name
    else:
        fn_dir = lollmsElfServer.lollms_paths.custom_function_calls_path / function_name
    if not fn_dir.exists() or not (fn_dir / "config.yaml").exists() or not (fn_dir / "function.py").exists():
        raise HTTPException(status_code=404, detail="Function not found")

    # Check if already mounted
    for fc in lollmsElfServer.config.mounted_function_calls:
        if fc["name"] == function_name:
            lollmsElfServer.config.save_config()
            return {"status": True, "message": "Function mounted"}

    # Add new entry
    lollmsElfServer.config.mounted_function_calls.append({
        "name": function_name,
        "dir": str(fn_dir),
        "selected": False,
        "mounted": True
    })
    lollmsElfServer.config.save_config()

    return {"status": True, "message": "Function mounted successfully"}

@router.post("/unmount_function_call")
async def unmount_function_call(request: Request):
    """Unmount a function call to remove it from LLM's availability"""
    data = await request.json()
    client_id = data.get("client_id")
    function_name = data.get("function_name")

    if not check_access(lollmsElfServer, client_id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Find and update the function call
    found = False
    for fc in lollmsElfServer.config.mounted_function_calls:
        if fc["name"] == function_name:
            lollmsElfServer.config.mounted_function_calls.remove(fc) 
            found = True
            break
    
    if not found:
        raise HTTPException(status_code=404, detail="Function not mounted")

    lollmsElfServer.config.save_config()
    return {"status": True, "message": "Function unmounted successfully"}

@router.post("/unmount_all_functions")
async def unmount_all_functions(request: Request):
    """Unmount a function call to remove it from LLM's availability"""
    data = await request.json()
    client_id = data.get("client_id")

    if not check_access(lollmsElfServer, client_id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Find and update the function call
    found = False
    lollmsElfServer.config.mounted_function_calls=[]

    lollmsElfServer.config.save_config()
    return {"status": True, "message": "Function unmounted successfully"}

@router.post("/toggle_function_call")
async def toggle_function_call(request: Request):
    """Mount a function call to make it available to the LLM"""
    data = await request.json()
    client_id = data.get("client_id")
    fn_dir = data.get("dir")
    function_name = data.get("name")
    if not check_access(lollmsElfServer, client_id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Add new entry
    for entry in lollmsElfServer.config.mounted_function_calls:
        if entry["name"] == function_name and entry["dir"] == str(fn_dir):
            entry["selected"] = not entry["selected"]
    lollmsElfServer.config.save_config()
    
    return {"status": True, "message": "Function mounted successfully"}


@router.post("/get_function_call_settings")
async def get_function_call_settings(request: Request):
    data = await request.json()
    client = check_access(lollmsElfServer,data["client_id"])
    fn_dir = data.get("category")
    function_name = data.get("name")

    # Add new entry
    for entry in lollmsElfServer.config.mounted_function_calls:
        if entry["name"] == function_name and (Path(entry["dir"]).parent.name == str(fn_dir) or (fn_dir=="custom" and Path(entry["dir"]).parent.name == "custom_function_calls")):
            try:
                fci = lollmsElfServer.load_function_call(entry, client)
                if hasattr(fci["class"],"static_parameters"):
                    return fci["class"].static_parameters.config_template.template
                else:
                    return {}
            except Exception as ex:
                trace_exception(ex)
                return {}

    return {}

@router.post("/set_function_call_settings")
async def set_function_call_settings(request: Request):
    data = await request.json()
    client = check_access(lollmsElfServer,data["client_id"])
    settings = data["settings"]
    """
    Sets the active ttv settings.

    :param request: The ttvSettingsRequest object.
    :return: A JSON response with the status of the operation.
    """

    try:
        print("- Setting function call settings")
        fn_dir = data.get("category")
        function_name = data.get("name")

        # Add new entry
        for entry in lollmsElfServer.config.mounted_function_calls:
            if entry["name"] == function_name and (Path(entry["dir"]).parent.name == str(fn_dir) or (fn_dir=="custom" and Path(entry["dir"]).parent.name == "custom_function_calls")):
                try:
                    fci = lollmsElfServer.load_function_call(entry, client)
                    if hasattr(fci["class"],"static_parameters"):
                        fci["class"].static_parameters.update_template(settings)
                        fci["class"].static_parameters.config.save_config()
                        fci["class"].settings_updated()
                        return {'status':True}
                    else:
                        return {'status':False}
                except Exception as ex:
                    trace_exception(ex)
                    return {}
        return {'status':False}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}
