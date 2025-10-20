"""
project: lollms
file: lollms_binding_files_server.py 
author: ParisNeo
description: 
    This module contains a set of FastAPI routes that provide information about the Lord of Large Language and Multimodal Systems (LoLLMs) Web UI
    application. These routes are specific to serving files

"""
from fastapi import APIRouter, Request, Depends
from fastapi import HTTPException
from pydantic import BaseModel, validator
import pkg_resources
from lollms.server.elf_server import LOLLMSElfServer
from fastapi.responses import FileResponse
from lollms.binding import BindingBuilder, InstallOption
from lollms.security import sanitize_path
from ascii_colors import ASCIIColors
from lollms.utilities import load_config, trace_exception, gc, PackageManager, run_async
from safe_store import SafeStore, SAFE_STORE_SUPPORTED_FILE_EXTENSIONS, GraphStore
from pathlib import Path
from typing import List, Optional, Dict
from lollms.security import check_access
from functools import partial
import os
import re
import threading

import pipmaster as pm
if not pm.is_installed("PyQt5"):
    pm.install("PyQt5")

import sys
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog
from pathlib import Path
from PyQt5.QtCore import Qt
from typing import Optional, Dict
# ----------------------- Defining router and main class ------------------------------
router = APIRouter()
lollmsElfServer = LOLLMSElfServer.get_instance()



def open_folder() -> Optional[Path]:
    try:
        app = QApplication(sys.argv)
        
        # Créer une instance de QFileDialog au lieu d'utiliser la méthode statique
        dialog = QFileDialog()
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        
        # Afficher le dialogue et le mettre au premier plan
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        
        if dialog.exec_() == QFileDialog.Accepted:
            selected_folder = dialog.selectedFiles()[0]
            return Path(selected_folder)
        else:
            return None
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
        return None

def open_file(file_types: List[str]) -> Optional[Path]:
    try:
        app = QApplication(sys.argv)
        
        # Créer une instance de QFileDialog
        dialog = QFileDialog()
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter(';;'.join(file_types))
        
        # Afficher le dialogue et le mettre au premier plan
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        
        if dialog.exec_() == QFileDialog.Accepted:
            selected_file = dialog.selectedFiles()[0]
            return Path(selected_file)
        else:
            return None
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
        return None
    

def select_lightrag_input_folder_(client) -> Optional[Dict[str, Path]]:
    """
    Opens a folder selection dialog and then a string input dialog to get the database name using PyQt5.
    
    Returns:
        Optional[Dict[str, Path]]: A dictionary with the database name and the database path, or None if no folder was selected.
    """
    try:
        # Create a QApplication instance
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        # Open the folder selection dialog
        dialog = QFileDialog()
        # dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.raise_()
        dialog.activateWindow()

        # Add a custom filter to show network folders
        dialog.setFileMode(QFileDialog.Directory)
        
        # Show the dialog modally
        if dialog.exec_() == QFileDialog.Accepted:
            folder_path = dialog.selectedFiles()[0]  # Get the selected folder path
            if folder_path:
                try:
                    run_async(partial(lollmsElfServer.sio.emit,'lightrag_input_folder_added', {"path": str(folder_path)}, to=client.client_id))
                except Exception as ex:
                    trace_exception(ex)
                return {"database_path": Path(folder_path)}

            else:
                return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def select_lightrag_output_folder_(client) -> Optional[Dict[str, Path]]:
    """
    Opens a folder selection dialog and then a string input dialog to get the database name using PyQt5.
    
    Returns:
        Optional[Dict[str, Path]]: A dictionary with the database name and the database path, or None if no folder was selected.
    """
    try:
        # Create a QApplication instance
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        # Open the folder selection dialog
        dialog = QFileDialog()
        # dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.raise_()
        dialog.activateWindow()

        # Add a custom filter to show network folders
        dialog.setFileMode(QFileDialog.Directory)
        
        # Show the dialog modally
        if dialog.exec_() == QFileDialog.Accepted:
            folder_path = dialog.selectedFiles()[0]  # Get the selected folder path
            if folder_path:
                try:
                    run_async(partial(lollmsElfServer.sio.emit,'lightrag_output_folder_added', {"path": str(folder_path)}, to=client.client_id))
                except Exception as ex:
                    trace_exception(ex)
                return {"database_path": Path(folder_path)}
            else:
                return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def select_safe_store_input_folder_(client) -> Optional[Dict[str, Path]]:
    """
    Opens a folder selection dialog and then a string input dialog to get the database name using PyQt5.
    
    Returns:
        Optional[Dict[str, Path]]: A dictionary with the database name and the database path, or None if no folder was selected.
    """
    try:
        # Create a QApplication instance
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        # Open the folder selection dialog
        dialog = QFileDialog()
        # dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.raise_()
        dialog.activateWindow()

        # Add a custom filter to show network folders
        dialog.setFileMode(QFileDialog.Directory)
        
        # Show the dialog modally
        if dialog.exec_() == QFileDialog.Accepted:
            folder_path = dialog.selectedFiles()[0]  # Get the selected folder path
            if folder_path:
                # Bring the input dialog to the foreground as well
                input_dialog = QInputDialog()
                input_dialog.setWindowFlags(input_dialog.windowFlags() | Qt.WindowStaysOnTopHint)
                input_dialog.setWindowModality(Qt.ApplicationModal)
                input_dialog.setWindowFlag(Qt.WindowStaysOnTopHint, True)
                input_dialog.setWindowModality(Qt.ApplicationModal)
                input_dialog.raise_()
                input_dialog.activateWindow()
                db_name, ok = input_dialog.getText(None, "Database Name", "Please enter the database name:")
                
                if ok and db_name:
                    try:
                        lollmsElfServer.ShowBlockingMessage("Adding a new database.")
                        
                        vdb = SafeStore(Path(folder_path)/f"{db_name}.sqlite")
                        # Get all files in the folder
                        folder = Path(folder_path)
                        file_types = [f"**/*{f}" if lollmsElfServer.config.rag_follow_subfolders else f"*{f}" for f in SAFE_STORE_SUPPORTED_FILE_EXTENSIONS]
                        files = []
                        for file_type in file_types:
                            files.extend(folder.glob(file_type))
                        
                        # Load and add each document to the database
                        for fn in files:
                            try:
                                lollmsElfServer.ShowBlockingMessage(f"Adding a new database.\nAdding {fn.stem}")
                                vdb.add_document(fn, lollmsElfServer.config.rag_vectorizer)
                                print(f"Added document: {fn.stem}")
                            except Exception as e:
                                lollmsElfServer.error(f"Failed to add document {fn}: {e}")
                                print(f"Failed to add document {fn}: {e}")
                        if vdb.new_data: #New files are added, need reindexing
                            lollmsElfServer.ShowBlockingMessage(f"Adding a new database.\nIndexing the database...")
                            vdb.build_index()
                            ASCIIColors.success("OK")
                        lollmsElfServer.HideBlockingMessage()
                        run_async(partial(lollmsElfServer.sio.emit,'safe_store_datalake_added', {"datalake_name": db_name, "path": str(folder_path)}, to=client.client_id))

                    except Exception as ex:
                        trace_exception(ex)
                        lollmsElfServer.HideBlockingMessage()
                    
                    return {"datalake_name": db_name, "database_path": Path(folder_path)}
                else:
                    return None
            else:
                return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


from typing import List, Optional, Tuple, Union, Dict
from typing import List, Tuple, Dict, Union

def find_rag_database_by_name(entries: List[Dict[str, Union[str, bool]]], name: str) -> Tuple[int, str]:
    """
    Finds a database entry in the list by its name.

    Args:
        entries (List[Dict]): The list of database entries as dictionaries with structure:
            {
                'alias': str,
                'type': str,
                'url': str,
                'key': str,
                'mounted': bool
            }
        name (str): The name to search for

    Returns:
        Tuple[int, str]: A tuple containing:
            - index of the found entry (-1 if not found)
            - path/url of the database ("" if not found)
    """
    ASCIIColors.green("find_rag_database_by_name:")
    
    for i, entry in enumerate(entries):
        ASCIIColors.green(str(entry))
        
        if entry['alias'] == name:
            # For remote databases, return the URL, for local ones return the type
            return i, entry
    
    return -1, ""


# ----------------------------------- Personal files -----------------------------------------
class SelectDatabase(BaseModel):
    client_id: str

class FolderInfos(BaseModel):
    client_id: str
    rag_database: dict


class MountDatabase(BaseModel):
    client_id: str
    datalake_name:str


class FolderOpenRequest(BaseModel):
    client_id: str

class FileOpenRequest(BaseModel):
    client_id: str
    file_types: List[str]
    
    
@router.post("/get_folder")
def get_folder(folder_infos: FolderOpenRequest):
    """
    Open 
    """ 
    check_access(lollmsElfServer, folder_infos.client_id)
    return open_folder()

@router.post("/get_file")
def get_file(file_infos: FileOpenRequest):
    """
    Open 
    """ 
    check_access(lollmsElfServer, file_infos.client_id)
    return open_file(file_infos.file_types)


@router.post("/select_safe_store_input_folder")
async def select_safe_store_input_folder(database_infos: SelectDatabase):
    """
    Selects and names a database 
    """ 
    client = check_access(lollmsElfServer, database_infos.client_id)
    lollmsElfServer.rag_thread = threading.Thread(target=select_rag_store_input_folder_, args=[client])
    lollmsElfServer.rag_thread.start()
    return True


@router.post("/select_lightrag_input_folder")
async def select_lightrag_input_folder(database_infos: SelectDatabase):
    """
    Selects and names a database 
    """ 
    client = check_access(lollmsElfServer, database_infos.client_id)
    lollmsElfServer.rag_thread = threading.Thread(target=select_lightrag_input_folder_, args=[client])
    lollmsElfServer.rag_thread.start()
    return True

@router.post("/select_lightrag_output_folder")
async def select_lightrag_output_folder(database_infos: SelectDatabase):
    """
    Selects and names a database 
    """ 
    client = check_access(lollmsElfServer, database_infos.client_id)
    lollmsElfServer.rag_thread = threading.Thread(target=select_lightrag_output_folder_, args=[client])
    lollmsElfServer.rag_thread.start()
    return True

@router.post("/toggle_mount_rag_database")
def toggle_mount_rag_database(database_infos: MountDatabase):
    """
    Selects and names a database 
    """ 
    client = check_access(lollmsElfServer, database_infos.client_id)
    index, db_entry = find_rag_database_by_name(lollmsElfServer.config.datalakes, database_infos.datalake_name)
    

    if not db_entry['mounted']:
        def process():
            try:
                if db_entry['type']=="graph":
                    lollmsElfServer.ShowBlockingMessage(f"Mounting database {db_entry['alias']}")
                    lr = GraphStore(db_entry['url'])
                    lollmsElfServer.config.datalakes[index]['mounted'] = True
                    lollmsElfServer.active_datalakes.append(lollmsElfServer.config.datalakes[index] | {
                        "binding": lr
                    })
                    lollmsElfServer.config.save_config()
                    lollmsElfServer.info(f"Datalake {database_infos.datalake_name} mounted successfully")
                    lollmsElfServer.HideBlockingMessage()
                else:
                    lollmsElfServer.ShowBlockingMessage(f"Mounting database {db_entry['alias']}")
                    try:
                        vdb = SafeStore(
                            Path(db_entry['path'])/f"{database_infos.datalake_name}.sqlite"
                        )       
                        lollmsElfServer.config.datalakes[index]['mounted'] = True
                        lollmsElfServer.active_datalakes.append(lollmsElfServer.config.datalakes[index] | {
                            "binding": vdb
                        })
                        lollmsElfServer.config.save_config()
                        lollmsElfServer.info(f"Database {database_infos.datalake_name} mounted successfully")
                        lollmsElfServer.HideBlockingMessage()
                    except Exception as ex:
                        trace_exception(ex)
                        lollmsElfServer.error(f"Database {database_infos.datalake_name} couldn't be mounted!!\n{ex}\nTry reindexing the database.")
                        lollmsElfServer.HideBlockingMessage()

            except Exception as ex:
                trace_exception(ex)
                lollmsElfServer.HideBlockingMessage()

        lollmsElfServer.rag_thread = threading.Thread(target=process)
        lollmsElfServer.rag_thread.start()
    else:
        # Unmounting logic
        if db_entry['type']=="graph":
            lollmsElfServer.config.datalakes[index]['mounted'] = False
            lollmsElfServer.active_datalakes = [
                db for db in lollmsElfServer.active_datalakes 
                if db["alias"] != database_infos.datalake_name
            ]
            lollmsElfServer.config.save_config()
            lollmsElfServer.info(f"Datalake {database_infos.datalake_name} unmounted successfully")
        else:
            lollmsElfServer.config.datalakes[index]['mounted'] = False
            lollmsElfServer.active_datalakes = [
                db for db in lollmsElfServer.active_datalakes 
                if db["alias"] != database_infos.datalake_name
            ]
            lollmsElfServer.config.save_config()
            lollmsElfServer.info(f"Datalake {database_infos.datalake_name} unmounted successfully")


@router.post("/upload_files_2_rag_db")
async def upload_files_2_rag_db(database_infos: FolderInfos):
    client = check_access(lollmsElfServer, database_infos.client_id)
    index, path = find_rag_database_by_name(lollmsElfServer.config.datalakes, database_infos.datalake_name)
    
    if index < 0:
        # Check remote databases
        index, path = find_rag_database_by_name(lollmsElfServer.config.datalakes, database_infos.datalake_name)
        db_entry = lollmsElfServer.config.datalakes[index]
    else:
        # Local database
        db_entry = lollmsElfServer.config.datalakes[index]

@router.post("/vectorize_folder")
async def vectorize_folder(database_infos: FolderInfos):
    """
    Selects and names a database 
    """ 
    client = check_access(lollmsElfServer, database_infos.client_id)
    def process():
        if database_infos.rag_database["alias"]:
            db_name = database_infos.rag_database["alias"]
            folder_path = sanitize_path( database_infos.rag_database["path"], True) 
        else:
            # Create a QApplication instance
            app = QApplication.instance()
            if not app:
                app = QApplication(sys.argv)
            
            # Ask for the database name
            db_name, ok = QInputDialog.getText(None, "Database Name", "Please enter the database name:")
            folder_path = sanitize_path( database_infos.rag_database["path"], True) 
            
            if not ok or not db_name:
                return
        
        try:
            lollmsElfServer.ShowBlockingMessage("Revectorizing the database.")
        



            vector_db_path = Path(folder_path)/f"{db_name}.sqlite"

            vdb = SafeStore(vector_db_path)
            # Get all files in the folder
            folder = Path(folder_path)
            file_types = [f"**/*{f}" if lollmsElfServer.config.rag_follow_subfolders else f"*{f}" for f in SAFE_STORE_SUPPORTED_FILE_EXTENSIONS]
            files = []
            for file_type in file_types:
                files.extend(folder.glob(file_type))
            
            # Load and add each document to the database
            for fn in files:
                try:
                    title = fn.stem  # Use the file name without extension as the title
                    lollmsElfServer.ShowBlockingMessage(f"Adding a new database.\nAdding {title}")
                    vdb.add_document(fn)
                    print(f"Added document: {title}")
                except Exception as e:
                    lollmsElfServer.error(f"Failed to add document {fn}: {e}")
            lollmsElfServer.HideBlockingMessage()
            run_async(partial(lollmsElfServer.sio.emit,'lollmsvectordb_datalake_added', {"datalake_name": db_name, "path": str(folder_path)}, to=client.client_id))

        except Exception as ex:
            trace_exception(ex)
            lollmsElfServer.HideBlockingMessage()
    
    lollmsElfServer.rag_thread = threading.Thread(target=process)
    lollmsElfServer.rag_thread.start()
