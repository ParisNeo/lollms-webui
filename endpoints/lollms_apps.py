from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from lollms_webui import LOLLMSWebUI
from pydantic import BaseModel
from pathlib import Path
import shutil
import uuid
import os
import requests
import yaml

router = APIRouter()
lollmsElfServer: LOLLMSWebUI = LOLLMSWebUI.get_instance()

class AuthRequest(BaseModel):
    client_id: str

class AppInfo:
    def __init__(self, uid: str, name: str, icon: str, description: str, author:str, version:str, model_name:str, disclaimer:str):
        self.uid = uid
        self.name = name
        self.icon = icon
        self.description = description
        self.author = author
        self.version = version
        self.model_name = model_name
        self.disclaimer = disclaimer

@router.get("/apps")
async def list_apps():
    apps = []
    binding_models_path = lollmsElfServer.lollms_paths.apps_zoo_path
    
    for app_name in binding_models_path.iterdir():
        if app_name.is_dir():
            icon_path = app_name / "icon.png"
            description_path = app_name / "description.yaml"
            description = ""
            author = ""
            version = ""
            model_name = ""
            disclaimer = ""
            
            if description_path.exists():
                with open(description_path, 'r') as file:
                    data = yaml.safe_load(file)
                    description = data.get('description', '')
                    author = data.get('author', '')
                    version = data.get('version', '')
                    model_name = data.get('model_name', '')
                    disclaimer = data.get('disclaimer', 'No disclaimer provided.')
                    
            if icon_path.exists():
                uid = str(uuid.uuid4())
                apps.append(AppInfo(
                    uid=uid,
                    name=app_name.name,
                    icon=f"/apps/{app_name.name}/icon",
                    description=description,
                    author=author,
                    version=version,
                    model_name=model_name,
                    disclaimer=disclaimer
                ))
    
    return apps


@router.post("/apps/{app_name}/code")
async def get_app_code(app_name: str, auth: AuthRequest):
    app_path = lollmsElfServer.lollms_paths.apps_zoo_path / app_name / "index.html"
    if not app_path.exists():
        raise HTTPException(status_code=404, detail="App not found")
    return FileResponse(app_path)


@router.post("/install/{app_name}")
async def install_app(app_name: str, auth: AuthRequest):
    # Create the app directory
    app_path = lollmsElfServer.lollms_paths.apps_zoo_path / app_name
    os.makedirs(app_path, exist_ok=True)

    # Define the URLs for the files to download
    files_to_download = {
        "icon.png": f"https://github.com/ParisNeo/lollms_apps_zoo/raw/main/{app_name}/icon.png",
        "description.yaml": f"https://raw.githubusercontent.com/ParisNeo/lollms_apps_zoo/main/{app_name}/description.yaml",
        "index.html": f"https://raw.githubusercontent.com/ParisNeo/lollms_apps_zoo/main/{app_name}/index.html"
    }

    # Download each file
    for file_name, url in files_to_download.items():
        response = requests.get(url)
        if response.status_code == 200:
            with open(app_path / file_name, 'wb') as f:
                f.write(response.content)
        else:
            raise HTTPException(status_code=404, detail=f"{file_name} not found on GitHub")

    return {"message": f"App {app_name} installed successfully."}

@router.post("/uninstall/{app_name}")
async def uninstall_app(app_name: str, auth: AuthRequest):
    app_path = lollmsElfServer.lollms_paths.apps_zoo_path / app_name
    if app_path.exists():
        shutil.rmtree(app_path)
        return {"message": f"App {app_name} uninstalled successfully."}
    else:
        raise HTTPException(status_code=404, detail="App not found")
    

@router.get("/github/apps")
async def fetch_github_apps():
    github_repo_url = "https://api.github.com/repos/ParisNeo/lollms_apps_zoo/contents"
    response = requests.get(github_repo_url)
    
    if response.status_code == 200:
        apps = []
        for item in response.json():
            if item['type'] == 'dir':
                app_name = item['name']
                description_url = f"https://api.github.com/repos/ParisNeo/lollms_apps_zoo/contents/{app_name}/description.yaml"
                icon_url = f"https://github.com/ParisNeo/lollms_apps_zoo/blob/main/{app_name}/icon.png?raw=true"
                
                # Fetch description.yaml
                description_response = requests.get(description_url)
                description_data = {}
                if description_response.status_code == 200:
                    description_data = yaml.safe_load(requests.get(description_url).text)
                
                apps.append(AppInfo(
                    uid=str(uuid.uuid4()),
                    name=app_name,
                    icon=icon_url,
                    description=description_data.get('description', ''),
                    author=description_data.get('author', ''),
                    version=description_data.get('version', ''),
                    model_name=description_data.get('model_name', ''),
                    disclaimer=description_data.get('disclaimer', 'No disclaimer provided.')
                ))
        return {"apps": apps}
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch apps from GitHub")

@router.get("/apps/{app_name}/icon")
async def get_app_icon(app_name: str):
    icon_path = lollmsElfServer.lollms_paths.apps_zoo_path / app_name / "icon.png"
    if not icon_path.exists():
        raise HTTPException(status_code=404, detail="Icon not found")
    return FileResponse(icon_path)
