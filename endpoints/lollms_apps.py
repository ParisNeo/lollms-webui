from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse
from lollms_webui import LOLLMSWebUI
from pydantic import BaseModel
from pathlib import Path
import shutil
import uuid
import os
import requests
import yaml
from lollms.security import check_access, sanitize_path
import os
import subprocess
import yaml
import uuid


router = APIRouter()
lollmsElfServer: LOLLMSWebUI = LOLLMSWebUI.get_instance()

class AuthRequest(BaseModel):
    client_id: str

class AppInfo:
    def __init__(self, uid: str, name: str, icon: str, category:str, description: str, author:str, version:str, model_name:str, disclaimer:str):
        self.uid = uid
        self.name = name
        self.icon = icon
        self.category = category
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
                    application_name = data.get('name', app_name.name)
                    category = data.get('category', 'generic')
                    description = data.get('description', '')
                    author = data.get('author', '')
                    version = data.get('version', '')
                    model_name = data.get('model_name', '')
                    disclaimer = data.get('disclaimer', 'No disclaimer provided.')
                    
            if icon_path.exists():
                uid = str(uuid.uuid4())
                apps.append(AppInfo(
                    uid=uid,
                    name=application_name,
                    icon=f"/apps/{app_name.name}/icon",
                    category=category,
                    description=description,
                    author=author,
                    version=version,
                    model_name=model_name,
                    disclaimer=disclaimer
                ))
    
    return apps

class OpenFolderRequest(BaseModel):
    client_id: str = Field(...)
    app_name: str = Field(...)

@router.post("/open_app_in_vscode")
async def open_folder_in_vscode(request: OpenFolderRequest):
    check_access(lollmsElfServer, request.client_id)
    sanitize_path(request.app_name)
    # Construct the folder path
    folder_path = lollmsElfServer.lollms_paths.apps_zoo_path/ request.app_name

    # Check if the folder exists
    if not folder_path.exists():
        raise HTTPException(status_code=404, detail="Folder not found")

    # Open the folder in VSCode
    try:
        os.system(f'code -n "{folder_path}"')  # This assumes 'code' is in the PATH
        return {"message": f"Opened {folder_path} in VSCode."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to open folder: {str(e)}")

@router.post("/apps/{app_name}/code")
async def get_app_code(app_name: str, auth: AuthRequest):
    app_path = lollmsElfServer.lollms_paths.apps_zoo_path / app_name / "index.html"
    if not app_path.exists():
        raise HTTPException(status_code=404, detail="App not found")
    return FileResponse(app_path)


@router.post("/install/{app_name}")
async def install_app(app_name: str, auth: AuthRequest):
    check_access(lollmsElfServer, auth.client_id)
    REPO_DIR = lollmsElfServer.lollms_paths.personal_path/"apps_zoo_repo"
    
    # Create the app directory
    app_path = lollmsElfServer.lollms_paths.apps_zoo_path/app_name  # Adjust the path as needed
    os.makedirs(app_path, exist_ok=True)

    # Define the local paths for the files to copy
    files_to_copy = {
        "icon.png": REPO_DIR/app_name/"icon.png",
        "description.yaml": REPO_DIR/app_name/"description.yaml",
        "index.html": REPO_DIR/app_name/"index.html"
    }

    # Copy each file from the local repo
    for file_name, local_path in files_to_copy.items():
        if local_path.exists():
            with open(local_path, 'rb') as src_file:
                with open(app_path/file_name, 'wb') as dest_file:
                    dest_file.write(src_file.read())
        else:
            raise HTTPException(status_code=404, detail=f"{file_name} not found in the local repository")

    return {"message": f"App {app_name} installed successfully."}

@router.post("/uninstall/{app_name}")
async def uninstall_app(app_name: str, auth: AuthRequest):
    app_path = lollmsElfServer.lollms_paths.apps_zoo_path / app_name
    if app_path.exists():
        shutil.rmtree(app_path)
        return {"message": f"App {app_name} uninstalled successfully."}
    else:
        raise HTTPException(status_code=404, detail="App not found")
    

REPO_URL = "https://github.com/ParisNeo/lollms_apps_zoo.git"


def clone_repo():
    REPO_DIR = Path(lollmsElfServer.lollms_paths.personal_path) / "apps_zoo_repo"
    
    # Check if the directory exists and if it is empty
    if REPO_DIR.exists():
        if any(REPO_DIR.iterdir()):  # Check if the directory is not empty
            print(f"Directory {REPO_DIR} is not empty. Aborting clone.")
            return
    else:
        REPO_DIR.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist

    # Clone the repository
    subprocess.run(["git", "clone", REPO_URL, str(REPO_DIR)], check=True)
    print(f"Repository cloned into {REPO_DIR}")

def pull_repo():
    REPO_DIR = lollmsElfServer.lollms_paths.personal_path/"apps_zoo_repo"
    subprocess.run(["git", "-C", str(REPO_DIR), "pull"], check=True)

def load_apps_data():
    apps = []
    REPO_DIR = lollmsElfServer.lollms_paths.personal_path/"apps_zoo_repo"
    for item in os.listdir(REPO_DIR):
        item_path = os.path.join(REPO_DIR, item)
        if os.path.isdir(item_path):
            description_path = os.path.join(item_path, "description.yaml")
            icon_url = f"https://github.com/ParisNeo/lollms_apps_zoo/blob/main/{item}/icon.png?raw=true"
            
            if os.path.exists(description_path):
                with open(description_path, 'r') as file:
                    description_data = yaml.safe_load(file)
                    apps.append(AppInfo(
                        uid=str(uuid.uuid4()),
                        name=item,
                        icon=icon_url,
                        category=description_data.get('category', 'generic'),
                        description=description_data.get('description', ''),
                        author=description_data.get('author', ''),
                        version=description_data.get('version', ''),
                        model_name=description_data.get('model_name', ''),
                        disclaimer=description_data.get('disclaimer', 'No disclaimer provided.')
                    ))
    return apps

@router.get("/lollms_js", response_class=PlainTextResponse)
async def lollms_js():
    # Define the path to the JSON file using pathlib
    file_path = Path(__file__).parent / "lollms_client_js.js"
    
    # Read the JSON file
    with file_path.open('r') as file:
        data = file.read()
    return data

@router.get("/template")
async def lollms_js():
    return {
        "start_header_id_template": lollmsElfServer.config.start_header_id_template,
        "end_header_id_template": lollmsElfServer.config.end_header_id_template,
        "separator_template": lollmsElfServer.config.separator_template,
        "start_user_header_id_template": lollmsElfServer.config.start_user_header_id_template,
        "end_user_header_id_template": lollmsElfServer.config.end_user_header_id_template,
        "end_user_message_id_template": lollmsElfServer.config.end_user_message_id_template,
        "start_ai_header_id_template": lollmsElfServer.config.start_ai_header_id_template,
        "end_ai_header_id_template": lollmsElfServer.config.end_ai_header_id_template,
        "end_ai_message_id_template": lollmsElfServer.config.end_ai_message_id_template,
        "system_message_template": lollmsElfServer.config.system_message_template
    }

@router.get("/github/apps")
async def fetch_github_apps():
    try:
        clone_repo()
        pull_repo()
        apps = load_apps_data()
        return {"apps": apps}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/apps/{app_name}/icon")
async def get_app_icon(app_name: str):
    icon_path = lollmsElfServer.lollms_paths.apps_zoo_path / app_name / "icon.png"
    if not icon_path.exists():
        raise HTTPException(status_code=404, detail="Icon not found")
    return FileResponse(icon_path)
