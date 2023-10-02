from flask import send_from_directory
import os
from pathlib import Path


def serve_static(self, filename):
    root_dir = os.getcwd()
    path = os.path.join(root_dir, 'web/dist/')+"/".join(filename.split("/")[:-1])                            
    fn = filename.split("/")[-1]
    return send_from_directory(path, fn)


def serve_images(self, filename):
    root_dir = os.getcwd()
    path = os.path.join(root_dir, 'images/')+"/".join(filename.split("/")[:-1])
                        
    fn = filename.split("/")[-1]
    return send_from_directory(path, fn)

def serve_bindings(self, filename):
    path = str(self.lollms_paths.bindings_zoo_path/("/".join(filename.split("/")[:-1])))
                        
    fn = filename.split("/")[-1]
    return send_from_directory(path, fn)

def serve_user_infos(self, filename):
    path = str(self.lollms_paths.personal_user_infos_path/("/".join(filename.split("/")[:-1])))
                        
    fn = filename.split("/")[-1]
    return send_from_directory(path, fn)



def serve_personalities(self, filename):
    path = str(self.lollms_paths.personalities_zoo_path/("/".join(filename.split("/")[:-1])))
                        
    fn = filename.split("/")[-1]
    return send_from_directory(path, fn)

def serve_outputs(self, filename):
    root_dir = self.lollms_paths.personal_path / "outputs"
    root_dir.mkdir(exist_ok=True, parents=True)
    path = str(root_dir/"/".join(filename.split("/")[:-1]))
                        
    fn = filename.split("/")[-1]
    return send_from_directory(path, fn)

def serve_help(self, filename):
    root_dir = Path(__file__).parent/f"help"
    root_dir.mkdir(exist_ok=True, parents=True)
    path = str(root_dir/"/".join(filename.split("/")[:-1]))
                        
    fn = filename.split("/")[-1]
    return send_from_directory(path, fn)

def serve_data(self, filename):
    root_dir = self.lollms_paths.personal_path / "data"
    root_dir.mkdir(exist_ok=True, parents=True)
    path = str(root_dir/"/".join(filename.split("/")[:-1]))
                        
    fn = filename.split("/")[-1]
    return send_from_directory(path, fn)

def serve_uploads(self, filename):
    root_dir = self.lollms_paths.personal_path / "uploads"
    root_dir.mkdir(exist_ok=True, parents=True)

    path = str(root_dir/"/".join(filename.split("/")[:-1]))
                        
    fn = filename.split("/")[-1]
    return send_from_directory(path, fn)