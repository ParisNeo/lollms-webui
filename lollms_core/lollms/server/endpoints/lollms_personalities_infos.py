"""
project: lollms
file: lollms_personalities_infos.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes are specific to handling personalities related operations.

"""
from fastapi import APIRouter, Request
from fastapi import HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import pkg_resources
from lollms.server.elf_server import LOLLMSElfServer
from lollms.personality import AIPersonality, InstallOption
from ascii_colors import ASCIIColors
from lollms.utilities import load_config, trace_exception, gc, show_yes_no_dialog
from lollms.security import check_access, forbid_remote_access
from pathlib import Path
from typing import List, Optional
import psutil
import yaml
from lollms.security import sanitize_path

# --------------------- Parameter Classes -------------------------------

class PersonalityListingInfos(BaseModel):
    category:str


class PersonalitySelectionInfos(BaseModel):
    client_id:str
    id:int

# ----------------------- Defining router and main class ------------------------------
router = APIRouter()
lollmsElfServer = LOLLMSElfServer.get_instance()

# --------------------- Listing -------------------------------

@router.get("/list_personalities_categories")
def list_personalities_categories():
    personalities_categories_dir = lollmsElfServer.lollms_paths.personalities_zoo_path  # replace with the actual path to the models folder
    personalities_categories = ["custom_personalities"]+[f.stem for f in personalities_categories_dir.iterdir() if f.is_dir() and not f.name.startswith(".")]
    return personalities_categories

@router.get("/list_personalities")
def list_personalities(category:str):
    category = sanitize_path(category)
    if not category:
        return []
    try:
        if category=="custom_personalities":
            personalities_dir = lollmsElfServer.lollms_paths.custom_personalities_path  # replace with the actual path to the models folder
        else:
            personalities_dir = lollmsElfServer.lollms_paths.personalities_zoo_path/f'{category}'  # replace with the actual path to the models folder
        personalities = [f.stem for f in personalities_dir.iterdir() if f.is_dir() and not f.name.startswith(".")]
    except Exception as ex:
        personalities=[]
        ASCIIColors.error(f"No personalities found. Using default one {ex}")
    return personalities


@router.get("/get_personality")
def get_personality():
    ASCIIColors.yellow("Getting current personality")
    personality = lollmsElfServer.personality

    real_assets_path = lollmsElfServer.lollms_paths.personalities_zoo_path / personality.category / personality.personality_folder_name / 'assets'
    assets_path = Path("personalities") / personality.category / personality.personality_folder_name / 'assets'
    gif_logo_path = assets_path / 'logo.gif'
    webp_logo_path = assets_path / 'logo.webp'
    png_logo_path = assets_path / 'logo.png'
    jpg_logo_path = assets_path / 'logo.jpg'
    jpeg_logo_path = assets_path / 'logo.jpeg'
    svg_logo_path = assets_path / 'logo.svg'
    bmp_logo_path = assets_path / 'logo.bmp'

    gif_logo_path_ = real_assets_path / 'logo.gif'
    webp_logo_path_ = real_assets_path / 'logo.webp'
    png_logo_path_ = real_assets_path / 'logo.png'
    jpg_logo_path_ = real_assets_path / 'logo.jpg'
    jpeg_logo_path_ = real_assets_path / 'logo.jpeg'
    svg_logo_path_ = real_assets_path / 'logo.svg'
    bmp_logo_path_ = real_assets_path / 'logo.bmp'
        
    has_logo = png_logo_path.is_file() or gif_logo_path.is_file()
    
    if gif_logo_path_.exists():
        avatar = str(gif_logo_path).replace("\\","/")
    elif webp_logo_path_.exists():
        avatar = str(webp_logo_path).replace("\\","/")
    elif png_logo_path_.exists():
        avatar = str(png_logo_path).replace("\\","/")
    elif jpg_logo_path_.exists():
        avatar = str(jpg_logo_path).replace("\\","/")
    elif jpeg_logo_path_.exists():
        avatar = str(jpeg_logo_path).replace("\\","/")
    elif svg_logo_path_.exists():
        avatar = str(svg_logo_path).replace("\\","/")
    elif bmp_logo_path_.exists():
        avatar = str(bmp_logo_path).replace("\\","/")
    else:
        avatar = ""    
    personality = {
        "folder":personality.personality_folder_name,
        "has_scripts":personality.processor is not None,
        "name":personality.name,
        "description":personality.personality_description,
        "disclaimer":personality.disclaimer,
        "author":personality.author,
        "language":personality.language,
        "version":personality.version,
        "creation_date":personality.creation_date,
        "last_update_date":personality.last_update_date,
        "installed":True,
        "help":personality.help,
        "commands":personality.commands,
        "prompts_list":personality.prompts_list,
        "avatar":avatar,
        "has_logo":has_logo
    }
    return personality

@router.get("/get_all_personalities")
def get_all_personalities():
    ASCIIColors.yellow("Listing all personalities", end="")
    personalities_folder = lollmsElfServer.lollms_paths.personalities_zoo_path
    personalities = {}

    for category_folder in  [lollmsElfServer.lollms_paths.custom_personalities_path] + list(personalities_folder.iterdir()):
        cat = category_folder.stem
        if category_folder.is_dir() and not category_folder.stem.startswith('.'):
            personalities[cat if category_folder!=lollmsElfServer.lollms_paths.custom_personalities_path else "custom_personalities"] = []
            for personality_folder in category_folder.iterdir():
                pers = personality_folder.stem
                if lollmsElfServer.personality.personality_folder_name==pers:
                    personality = lollmsElfServer.personality
                    lollmsElfServer.lollms_paths.custom_personalities_path
                    real_assets_path = lollmsElfServer.lollms_paths.personalities_zoo_path / cat / personality.personality_folder_name / 'assets'
                    category = personality.category if category_folder!=lollmsElfServer.lollms_paths.custom_personalities_path!=category_folder else "custom_personalities"
                    assets_path = Path("personalities") / category / personality.personality_folder_name / 'assets'
                    gif_logo_path = assets_path / 'logo.gif'
                    webp_logo_path = assets_path / 'logo.webp'
                    png_logo_path = assets_path / 'logo.png'
                    jpg_logo_path = assets_path / 'logo.jpg'
                    jpeg_logo_path = assets_path / 'logo.jpeg'
                    svg_logo_path = assets_path / 'logo.svg'
                    bmp_logo_path = assets_path / 'logo.bmp'

                    gif_logo_path_ = real_assets_path / 'logo.gif'
                    webp_logo_path_ = real_assets_path / 'logo.webp'
                    png_logo_path_ = real_assets_path / 'logo.png'
                    jpg_logo_path_ = real_assets_path / 'logo.jpg'
                    jpeg_logo_path_ = real_assets_path / 'logo.jpeg'
                    svg_logo_path_ = real_assets_path / 'logo.svg'
                    bmp_logo_path_ = real_assets_path / 'logo.bmp'
                        
                    has_logo = png_logo_path.is_file() or gif_logo_path.is_file()
                    
                    if gif_logo_path_.exists():
                        avatar = str(gif_logo_path).replace("\\","/")
                    elif webp_logo_path_.exists():
                        avatar = str(webp_logo_path).replace("\\","/")
                    elif png_logo_path_.exists():
                        avatar = str(png_logo_path).replace("\\","/")
                    elif jpg_logo_path_.exists():
                        avatar = str(jpg_logo_path).replace("\\","/")
                    elif jpeg_logo_path_.exists():
                        avatar = str(jpeg_logo_path).replace("\\","/")
                    elif svg_logo_path_.exists():
                        avatar = str(svg_logo_path).replace("\\","/")
                    elif bmp_logo_path_.exists():
                        avatar = str(bmp_logo_path).replace("\\","/")
                    else:
                        avatar = ""    
                    personality = {
                        "folder":personality.personality_folder_name,
                        "has_scripts":personality.processor is not None,
                        "name":personality.name,
                        "description":personality.personality_description,
                        "disclaimer":personality.disclaimer,
                        "author":personality.author,
                        "language":personality.language,
                        "version":personality.version,
                        "creation_date":personality.creation_date,
                        "last_update_date":personality.last_update_date,
                        "installed":True,
                        "help":personality.help,
                        "commands":personality.commands,
                        "prompts_list":personality.prompts_list,
                        "avatar":avatar,
                        "has_logo":has_logo
                    }
                    personalities[cat if category_folder!=lollmsElfServer.lollms_paths.custom_personalities_path else "custom_personalities"].append(personality)
                else:
                    if personality_folder.is_dir() and not personality_folder.stem.startswith('.'):
                        personality_info = {"folder":personality_folder.stem}
                        config_path = personality_folder / 'config.yaml'
                        if not config_path.exists():
                            """
                            try:
                                shutil.rmtree(str(config_path.parent))
                                ASCIIColors.warning(f"Deleted useless personality: {config_path.parent}")
                            except Exception as ex:
                                ASCIIColors.warning(f"Couldn't delete personality ({ex})")
                            """
                            continue                                    
                        try:
                            scripts_path = personality_folder / 'scripts'
                            personality_info['has_scripts'] = scripts_path.exists()
                            with open(config_path, "r", encoding="utf8") as config_file:
                                config_data = yaml.load(config_file, Loader=yaml.FullLoader)
                                personality_info['name'] = config_data.get('name',"No Name")
                                personality_info['description'] = config_data.get('personality_description',"")
                                personality_info['disclaimer'] = config_data.get('disclaimer',"")
                                personality_info['author'] = config_data.get('author', 'ParisNeo')
                                personality_info['language'] = config_data.get('language', 'english')
                                personality_info['version'] = config_data.get('version', '1.0.0')
                                personality_info['creation_date'] = config_data.get("creation_date",None)
                                personality_info['last_update_date'] = config_data.get("last_update_date",None)
                                personality_info['installed'] = (lollmsElfServer.lollms_paths.personal_configuration_path/f"personality_{personality_folder.stem}.yaml").exists() or personality_info['has_scripts']
                                personality_info['help'] = config_data.get('help', '')
                                personality_info['commands'] = config_data.get('commands', '')
                                personality_info['prompts_list'] = config_data.get('prompts_list', [])


                            try:
                                help_path = personality_folder / 'README.md'
                                if help_path.exists():
                                    personality_info['help']=help_path.read_text()
                            except:
                                pass

                            languages_path = personality_folder/ 'languages'

                            real_assets_path = personality_folder/ 'assets'
                            assets_path = Path("personalities") / cat / pers / 'assets'
                            gif_logo_path = assets_path / 'logo.gif'
                            webp_logo_path = assets_path / 'logo.webp'
                            png_logo_path = assets_path / 'logo.png'
                            jpg_logo_path = assets_path / 'logo.jpg'
                            jpeg_logo_path = assets_path / 'logo.jpeg'
                            svg_logo_path = assets_path / 'logo.svg'
                            bmp_logo_path = assets_path / 'logo.bmp'

                            gif_logo_path_ = real_assets_path / 'logo.gif'
                            webp_logo_path_ = real_assets_path / 'logo.webp'
                            png_logo_path_ = real_assets_path / 'logo.png'
                            jpg_logo_path_ = real_assets_path / 'logo.jpg'
                            jpeg_logo_path_ = real_assets_path / 'logo.jpeg'
                            svg_logo_path_ = real_assets_path / 'logo.svg'
                            bmp_logo_path_ = real_assets_path / 'logo.bmp'

                            if languages_path.exists():
                                personality_info['languages']= [""]+[f.stem for f in languages_path.iterdir() if f.suffix==".yaml"]
                            else:
                                personality_info['languages']=None
                                
                            personality_info['has_logo'] = png_logo_path.is_file() or gif_logo_path.is_file()
                            
                            if gif_logo_path_.exists():
                                personality_info['avatar'] = str(gif_logo_path).replace("\\","/")
                            elif webp_logo_path_.exists():
                                personality_info['avatar'] = str(webp_logo_path).replace("\\","/")
                            elif png_logo_path_.exists():
                                personality_info['avatar'] = str(png_logo_path).replace("\\","/")
                            elif jpg_logo_path_.exists():
                                personality_info['avatar'] = str(jpg_logo_path).replace("\\","/")
                            elif jpeg_logo_path_.exists():
                                personality_info['avatar'] = str(jpeg_logo_path).replace("\\","/")
                            elif svg_logo_path_.exists():
                                personality_info['avatar'] = str(svg_logo_path).replace("\\","/")
                            elif bmp_logo_path_.exists():
                                personality_info['avatar'] = str(bmp_logo_path).replace("\\","/")
                            else:
                                personality_info['avatar'] = ""
                            
                            personalities[cat if category_folder!=lollmsElfServer.lollms_paths.custom_personalities_path else "custom_personalities"].append(personality_info)
                        except Exception as ex:
                            ASCIIColors.warning(f"Couldn't load personality from {personality_folder} [{ex}]")
                            trace_exception(ex)
    ASCIIColors.green("OK")

    return personalities


@router.get("/list_mounted_personalities")
def list_mounted_personalities():
    ASCIIColors.yellow("- Listing mounted personalities")
    return {"status": True,
            "personalities":lollmsElfServer.config["personalities"],
            "active_personality_id":lollmsElfServer.config["active_personality_id"]
            }   




@router.get("/get_current_personality_path_infos")
def get_current_personality_path_infos():
    if lollmsElfServer.personality is None:
        return {
            "personality_category":"", 
            "personality_name":""
        }
    else:
        return {
            "personality_category":lollmsElfServer.personality_category, 
            "personality_name":lollmsElfServer.personality_name
        }

# ----------------------------------- Installation/Uninstallation/Reinstallation ----------------------------------------


class PersonalityIn(BaseModel):
    client_id:str
    name: str = Field(None)

@router.post("/reinstall_personality")
async def reinstall_personality(personality_in: PersonalityIn):
    """
    Endpoint to reinstall personality

    :param personality_in: PersonalityIn contans personality name.
    :return: A JSON response with the status of the operation.
    """
    check_access(lollmsElfServer, personality_in.client_id)
    try:
        sanitize_path(personality_in.name)
        if not personality_in.name:
            personality_in.name=lollmsElfServer.config.personalities[lollmsElfServer.config["active_personality_id"]]
        personality_path = lollmsElfServer.lollms_paths.personalities_zoo_path / personality_in.name
        ASCIIColors.info(f"- Reinstalling personality {personality_in.name}...")
        ASCIIColors.info("Unmounting personality")
        idx = lollmsElfServer.config.personalities.index(personality_in.name)
        print(f"index = {idx}")
        lollmsElfServer.mounted_personalities[idx] = None
        gc.collect()
        try:
            lollmsElfServer.mounted_personalities[idx] = AIPersonality(personality_path,
                                        lollmsElfServer.lollms_paths, 
                                        lollmsElfServer.config,
                                        model=lollmsElfServer.model,
                                        app=lollmsElfServer,
                                        run_scripts=True,installation_option=InstallOption.FORCE_INSTALL)
            return {"status":True}
        except Exception as ex:
            trace_exception(ex)
            ASCIIColors.error(f"Personality file not found or is corrupted ({personality_in.name}).\nReturned the following exception:{ex}\nPlease verify that the personality you have selected exists or select another personality. Some updates may lead to change in personality name or category, so check the personality selection in settings to be sure.")
            ASCIIColors.info("Trying to force reinstall")
            return {"status":False, 'error':str(e)}

    except Exception as e:
        return {"status":False, 'error':str(e)}


# ------------------------------------------- Files manipulation -----------------------------------------------------
class Identification(BaseModel):
    client_id:str

@router.post("/get_current_personality_files_list")
def get_current_personality_files_list(data:Identification):
    check_access(lollmsElfServer, data.client_id)
    if lollmsElfServer.personality is None:
        return {"state":False, "error":"No personality selected"}
    return {"state":True, "files":[{"name":Path(f).name, "size":Path(f).stat().st_size} for f in lollmsElfServer.personality.text_files]+[{"name":Path(f).name, "size":Path(f).stat().st_size} for f in lollmsElfServer.personality.image_files]}

@router.post("/clear_personality_files_list")
def clear_personality_files_list(data:Identification):
    check_access(lollmsElfServer, data.client_id)
    if lollmsElfServer.personality is None:
        return {"state":False, "error":"No personality selected"}
    lollmsElfServer.personality.remove_all_files()
    return {"state":True}

class RemoveFileData(BaseModel):
    client_id:str
    name:str
    
@router.post("/remove_file")
def remove_file(data:RemoveFileData):
    """
    Removes a file form the personality files
    """
    check_access(lollmsElfServer, data.client_id)
    
    if lollmsElfServer.personality is None:
        return {"state":False, "error":"No personality selected"}
    lollmsElfServer.personality.remove_file(data.name)
    return {"state":True}



# ------------------------------------------- Languages endpoints ------------------------------------------------
@router.post("/get_personality_languages_list")
def get_current_personality_files_list(data:Identification):
    check_access(lollmsElfServer, data.client_id)
    languages_list = lollmsElfServer.get_personality_languages()
    
    # Return the languages list
    return languages_list

@router.post("/get_personality_language")
def get_personality_language(request: Identification):
    # Access verification
    check_access(lollmsElfServer, request.client_id)
    return lollmsElfServer.config.current_language

class SetLanguageRequest(BaseModel):
    client_id: str
    language: str

# Definition of the endpoint for setting the personality language
@router.post("/set_personality_language")
def set_personality_language(request: SetLanguageRequest):
    # Access verification
    check_access(lollmsElfServer, request.client_id)
    sanitize_path(request.language)

    # Calling the method to set the personality language
    success = lollmsElfServer.set_personality_language(request.language)
    
    # Returning an appropriate response depending on whether the operation was successful or not
    if success:
        return {"message": f"The personality language has been successfully set to {request.language}."}
    else:
        raise HTTPException(status_code=400, detail="Failed to set the personality language")

# Definition of the endpoint for setting the personality language
@router.post("/del_personality_language")
def del_personality_language(request: SetLanguageRequest):
    # Access verification
    check_access(lollmsElfServer, request.client_id)
    sanitize_path(request.language)
    language = request.language.lower().strip().split()[0]
    default_language = lollmsElfServer.personality.language.lower().strip().split()[0]

    if language==default_language:
        lollmsElfServer.InfoMessage("It is not possible to delete the default language of a personality")
        return
    # Calling the method to set the personality language
    if lollmsElfServer.config.turn_on_language_validation:
        if not show_yes_no_dialog("Language deletion request received","I have received a language deletion request. Are you sure?"):
            return
    success = lollmsElfServer.del_personality_language(request.language)
    
    # Returning an appropriate response depending on whether the operation was successful or not
    if success:
        return {"message": f"The personality language has been successfully set to {request.language}."}
    else:
        raise HTTPException(status_code=400, detail="Failed to set the personality language")

# ------------------------------------------- Mounting/Unmounting/Remounting ------------------------------------------------
class PersonalityDataRequest(BaseModel):
    client_id:str
    category:str
    name:str



@router.post("/get_personality_config")
def get_personality_config(data:PersonalityDataRequest):
    check_access(lollmsElfServer, data.client_id)
    print("- Recovering personality config")
    category = sanitize_path(data.category)
    name = sanitize_path(data.name)
    if category=="":
        return {"status":False, "error":"category must not be empty."}

    package_path = f"{category}/{name}"
    if category=="custom_personalities":
        package_full_path = lollmsElfServer.lollms_paths.custom_personalities_path/f"{name}"
    else:            
        package_full_path = lollmsElfServer.lollms_paths.personalities_zoo_path/package_path
    
    config_file = package_full_path / "config.yaml"
    if config_file.exists():
        with open(config_file,"r") as f:
            config = yaml.safe_load(f)
        return {"status":True, "config":config}
    else:
        return {"status":False, "error":"Not found"}
    
class PersonalityConfig(BaseModel):
    client_id:str
    category:str
    name:str
    config:dict

@router.post("/set_personality_config")
def set_personality_config(data:PersonalityConfig):
    forbid_remote_access(lollmsElfServer)
    check_access(lollmsElfServer, data.client_id)
    print("- Recovering personality config")
    category = sanitize_path(data.category)
    name = sanitize_path(data.name)
    config = data.config
    if category=="":
        return {"status":False, "error":"category must not be empty."}
    
    package_path = f"{category}/{name}"
    if category=="custom_personalities":
        package_full_path = lollmsElfServer.lollms_paths.custom_personalities_path/f"{name}"
    else:            
        package_full_path = lollmsElfServer.lollms_paths.personalities_zoo_path/package_path
    
    config_file = package_full_path / "config.yaml"
    if config_file.exists():
        with open(config_file,"w") as f:
            yaml.safe_dump(config, f)

        lollmsElfServer.mounted_personalities = lollmsElfServer.rebuild_personalities(reload_all=True)
        lollmsElfServer.InfoMessage("Personality updated")
        return {"status":True}
    else:
        return {"status":False, "error":"Not found"}

class PersonalityMountingInfos(BaseModel):
    client_id:str
    category:str
    folder:str
    language:Optional[str] = None

@router.post("/mount_personality")
def mount_personality(data:PersonalityMountingInfos):
    check_access(lollmsElfServer, data.client_id)
    print("- Mounting personality")
    category = sanitize_path(data.category)
    name = sanitize_path(data.folder)
    if category=="":
        return {"status":False, "error":"category must not be empty."}

    package_path = f"{category}/{name}"
    if category=="custom_personalities":
        package_full_path = lollmsElfServer.lollms_paths.custom_personalities_path/f"{name}"
    else:            
        package_full_path = lollmsElfServer.lollms_paths.personalities_zoo_path/package_path
    
    config_file = package_full_path / "config.yaml"
    if config_file.exists():
        """
        if package_path in lollmsElfServer.config["personalities"]:
            ASCIIColors.error("Can't mount exact same personality twice")
            return jsonify({"status": False,
                            "error":"Can't mount exact same personality twice",
                            "personalities":lollmsElfServer.config["personalities"],
                            "active_personality_id":lollmsElfServer.config["active_personality_id"]
                            })                
        """
        lollmsElfServer.config["personalities"].append(package_path)
        lollmsElfServer.mounted_personalities = lollmsElfServer.rebuild_personalities()
        lollmsElfServer.config["active_personality_id"]= len(lollmsElfServer.config["personalities"])-1
        lollmsElfServer.personality = lollmsElfServer.mounted_personalities[lollmsElfServer.config["active_personality_id"]]
        ASCIIColors.success("ok")
        if lollmsElfServer.config["active_personality_id"]<0:
            ASCIIColors.error("error:active_personality_id<0")
            return {"status": False,
                            "error":"active_personality_id<0",
                            "personalities":lollmsElfServer.config["personalities"],
                            "active_personality_id":lollmsElfServer.config["active_personality_id"]
                            }         
        else:
            if lollmsElfServer.config.auto_save:
                ASCIIColors.info("Saving configuration")
                lollmsElfServer.config.save_config()
            ASCIIColors.success(f"Personality {name} mounted successfully")
            return {"status": True,
                            "personalities":lollmsElfServer.config["personalities"],
                            "active_personality_id":lollmsElfServer.config["active_personality_id"]
                            }    
    else:
        pth = str(config_file).replace('\\','/')
        ASCIIColors.error(f"nok : Personality not found @ {pth}")            
        ASCIIColors.yellow(f"Available personalities: {[p.name for p in lollmsElfServer.mounted_personalities]}")
        return {"status": False, "error":f"Personality not found @ {pth}"}


@router.post("/remount_personality")
def remount_personality(data:PersonalityMountingInfos):
    check_access(lollmsElfServer, data.client_id)
    category = sanitize_path(data.category)
    name = sanitize_path(data.folder)
    language = data.language #.get('language', None)

    if category=="":
        return {"status":False, "error":"category must not be empty."}

    package_path = f"{category}/{name}"
    if category=="custom_personalities":
        package_full_path = lollmsElfServer.lollms_paths.custom_personalities_path/f"{name}"
    else:            
        package_full_path = lollmsElfServer.lollms_paths.personalities_zoo_path/package_path
    
    config_file = package_full_path / "config.yaml"
    if config_file.exists():
        ASCIIColors.info(f"Unmounting personality {package_path}")
        index = lollmsElfServer.config["personalities"].index(f"{category}/{name}")
        lollmsElfServer.config["personalities"].remove(f"{category}/{name}")
        if lollmsElfServer.config["active_personality_id"]>=index:
            lollmsElfServer.config["active_personality_id"]=0
        if len(lollmsElfServer.config["personalities"])>0:
            lollmsElfServer.mounted_personalities = lollmsElfServer.rebuild_personalities()
            lollmsElfServer.personality = lollmsElfServer.mounted_personalities[lollmsElfServer.config["active_personality_id"]]
        else:
            lollmsElfServer.personalities = ["generic/lollms"]
            lollmsElfServer.mounted_personalities = lollmsElfServer.rebuild_personalities()
            lollmsElfServer.personality = lollmsElfServer.mounted_personalities[lollmsElfServer.config["active_personality_id"]]


        ASCIIColors.info(f"Mounting personality {package_path}")
        lollmsElfServer.config["personalities"].append(package_path)
        lollmsElfServer.config["active_personality_id"]= len(lollmsElfServer.config["personalities"])-1
        lollmsElfServer.mounted_personalities = lollmsElfServer.rebuild_personalities()
        lollmsElfServer.personality = lollmsElfServer.mounted_personalities[lollmsElfServer.config["active_personality_id"]]
        ASCIIColors.success("ok")
        if lollmsElfServer.config["active_personality_id"]<0:
            return {"status": False,
                            "personalities":lollmsElfServer.config["personalities"],
                            "active_personality_id":lollmsElfServer.config["active_personality_id"]
                            }      
        else:
            return {"status": True,
                            "personalities":lollmsElfServer.config["personalities"],
                            "active_personality_id":lollmsElfServer.config["active_personality_id"]
                            }    
    else:
        pth = str(config_file).replace('\\','/')
        ASCIIColors.error(f"nok : Personality not found @ {pth}")
        ASCIIColors.yellow(f"Available personalities: {[p.name for p in lollmsElfServer.mounted_personalities]}")
        return {"status": False, "error":f"Personality not found @ {pth}"}  
    

@router.post("/unmount_personality")
def unmount_personality(data:PersonalityMountingInfos):
    check_access(lollmsElfServer, data.client_id)
    print("- Unmounting personality ...")
    category = sanitize_path(data.category)
    name = sanitize_path(data.folder)
    language = data.language #.get('language', None)

    if category=="":
        return {"status":False, "error":"category must not be empty."}

    try:
        personality_id = f"{category}/{name}" if language is None or language=="" else f"{category}/{name}"
        index = lollmsElfServer.config["personalities"].index(personality_id)
        lollmsElfServer.config["personalities"].remove(personality_id)
        if lollmsElfServer.config["active_personality_id"]>=index:
            lollmsElfServer.config["active_personality_id"]=0
        if len(lollmsElfServer.config["personalities"])>0:
            lollmsElfServer.mounted_personalities = lollmsElfServer.rebuild_personalities()
            lollmsElfServer.personality = lollmsElfServer.mounted_personalities[lollmsElfServer.config["active_personality_id"]]
        else:
            lollmsElfServer.personalities = ["generic/lollms"]
            lollmsElfServer.mounted_personalities = lollmsElfServer.rebuild_personalities()
            if lollmsElfServer.config["active_personality_id"]<len(lollmsElfServer.mounted_personalities):
                lollmsElfServer.personality = lollmsElfServer.mounted_personalities[lollmsElfServer.config["active_personality_id"]]
            else:
                lollmsElfServer.config["active_personality_id"] = -1
        ASCIIColors.success("ok")
        if lollmsElfServer.config.auto_save:
            ASCIIColors.info("Saving configuration")
            lollmsElfServer.config.save_config()
        return {
                    "status": True,
                    "personalities":lollmsElfServer.config["personalities"],
                    "active_personality_id":lollmsElfServer.config["active_personality_id"]
                    }
    except Exception as ex:
        trace_exception(ex)
        if language:
            ASCIIColors.error(f"nok : Personality not found @ {category}/{name}")
        else:
            ASCIIColors.error(f"nok : Personality not found @ {category}/{name}")
            
        ASCIIColors.yellow(f"Available personalities: {[p.name for p in lollmsElfServer.mounted_personalities if p is not None]}")
        return {"status": False, "error":"Couldn't unmount personality"}
    

class AuthenticationInfos(BaseModel):
    client_id:str

@router.post("/unmount_all_personalities")
def unmount_all_personalities(data:AuthenticationInfos):
    check_access(lollmsElfServer, data.client_id)
    lollmsElfServer.config.personalities=["generic/lollms"]
    lollmsElfServer.mounted_personalities=[]
    lollmsElfServer.personality=None
    lollmsElfServer.mount_personality(0)
    lollmsElfServer.config.save_config()
    return {"status":True}



# ------------------------------------------- Selecting personality ------------------------------------------------

@router.post("/select_personality")
def select_personality(data:PersonalitySelectionInfos):
    check_access(lollmsElfServer, data.client_id)
    ASCIIColors.info(f"Selecting personality : {lollmsElfServer.mounted_personalities[data.id]}")
    id = data.id
    if id<len(lollmsElfServer.mounted_personalities):
        lollmsElfServer.config["active_personality_id"]=id
        lollmsElfServer.personality:AIPersonality = lollmsElfServer.mounted_personalities[lollmsElfServer.config["active_personality_id"]]
        if lollmsElfServer.personality is None:
            return {"status": False, "error":"Something is wrong with the personality"}
        if lollmsElfServer.personality.processor:
            lollmsElfServer.personality.processor.selected()
        ASCIIColors.success("ok")
        
        print(f"Selected {lollmsElfServer.personality.name}")

        language = lollmsElfServer.config.current_language
        if lollmsElfServer.personality.language is None:
            lollmsElfServer.personality.language = "english"
        default_language = lollmsElfServer.personality.language.lower().strip().split()[0]

        if language != default_language:
            lollmsElfServer.set_personality_language(language)

        if lollmsElfServer.config.auto_save:
            ASCIIColors.info("Saving configuration")
            lollmsElfServer.config.save_config()
        return {
            "status": True,
            "personalities":lollmsElfServer.config["personalities"],
            "active_personality_id":lollmsElfServer.config["active_personality_id"]                
            }
    else:
        ASCIIColors.error(f"nok : personality id out of bounds @ {id} >= {len(lollmsElfServer.mounted_personalities)}")
        return {"status": False, "error":"Invalid ID"}
            
# ------------------------------------------- Personality settings------------------------------------------------

@router.post("/get_personality_settings")
def get_personality_settings(data:PersonalityMountingInfos):
    check_access(lollmsElfServer, data.client_id)
    print("- Retreiving personality settings")
    category = sanitize_path(data.category)
    name = sanitize_path(data.folder)
    if category=="":
        return {"status":False, "error":"category must not be empty."}

    if category == "custom_personalities":
        personality_folder = lollmsElfServer.lollms_paths.personal_personalities_path/f"{name}"
    else:
        personality_folder = lollmsElfServer.lollms_paths.personalities_zoo_path/f"{category}"/f"{name}"

    personality = AIPersonality(personality_folder,
                                lollmsElfServer.lollms_paths, 
                                lollmsElfServer.config,
                                model=lollmsElfServer.model,
                                app=lollmsElfServer,
                                run_scripts=True)
    if personality.processor is not None:
        if hasattr(personality.processor,"personality_config"):
            return personality.processor.personality_config.config_template.template
        else:
            return {}   
    else:
        return {}  


@router.get("/get_active_personality_settings")
def get_active_personality_settings():
    print("- Retreiving personality settings")
    if lollmsElfServer.personality.processor is not None:
        if hasattr(lollmsElfServer.personality.processor,"personality_config"):
            return lollmsElfServer.personality.processor.personality_config.config_template.template
        else:
            return {}
    else:
        return {}


@router.post("/set_active_personality_settings")
async def set_active_personality_settings(request: Request):
    """
    sets the active personality settings.

    :param request: The HTTP request object.
    :return: A JSON response with the status of the operation.
    """

    try:
        config_data = (await request.json())

        print("- Setting personality settings")
        
        if lollmsElfServer.personality.processor is not None:
            if hasattr(lollmsElfServer.personality.processor,"personality_config"):
                lollmsElfServer.personality.processor.personality_config.update_template(config_data)
                lollmsElfServer.personality.processor.personality_config.config.save_config()
                if lollmsElfServer.config.auto_save:
                    ASCIIColors.info("Saving configuration")
                    lollmsElfServer.config.save_config()
                if lollmsElfServer.personality.processor:
                    lollmsElfServer.personality.processor.settings_updated()
                return {'status':True}
            else:
                return {'status':False}
        else:
            return {'status':False}  
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}


class PersonalityInfos(BaseModel):
    client_id: str
    category:str
    name:str

class PersonalityRequest(BaseModel):
    client_id:str
    data:dict

@router.post("/copy_to_custom_personas")
async def copy_to_custom_personas(data: PersonalityInfos):
    """
    Copies the personality to custom personas so that you can modify it.

    """
    import shutil
    client = check_access(lollmsElfServer, data.client_id)
    
    category = sanitize_path(data.category)
    name = sanitize_path(data.name)

    if category=="custom_personalities":
        lollmsElfServer.InfoMessage("This persona is already in custom personalities folder")
        return {"status":False}
    else:
        personality_folder = lollmsElfServer.lollms_paths.personalities_zoo_path/f"{category}"/f"{name}"
        destination_folder = lollmsElfServer.lollms_paths.custom_personalities_path
        shutil.copytree(personality_folder, destination_folder/f"{name}")
        return {"status":True}

# ------------------------------------------- Interaction with personas ------------------------------------------------
@router.post("/post_to_personality")
async def post_to_personality(request: PersonalityRequest):
    """Post data to a personality"""
    client =check_access(lollmsElfServer, request.client_id)
    try:
        if hasattr(lollmsElfServer.personality.processor,'handle_request'):
            return await lollmsElfServer.personality.processor.handle_request(request.data, client)
        else:
            return {}
    except Exception as ex:
        trace_exception(ex)
        lollmsElfServer.error(ex)
        return {"status":False,"error":str(ex)}
    
