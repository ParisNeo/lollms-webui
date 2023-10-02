from lollms.helpers import ASCIIColors
from flask import jsonify, request
from pathlib import Path


def get_active_model(self):
    if self.binding is not None:
        try:
            models = self.binding.list_models(self.config)
            index = models.index(self.config.model_name)
            ASCIIColors.yellow("Listing models")
            return jsonify({"model":models[index],"index":index})
        except Exception as ex:
            return jsonify(None)
    else:
        return jsonify(None)

def add_reference_to_local_model(self):     
    data = request.get_json()
    if data["path"]=="":
        return jsonify({"status": False, "error":"Empty model path"})         
        
    path = Path(data["path"])
    if path.exists():
        self.config.reference_model(path)
        return jsonify({"status": True})         
    else:        
        return jsonify({"status": False, "error":"Model not found"})         

            

def install_model_from_path(self):
    from tkinter import Tk
    from tkinter.filedialog import askopenfilename
    
    ASCIIColors.info(f"- Selecting model ...")
    # Define the file types
    filetypes = [
        ("Model file", self.binding.supported_file_extensions),
    ]
    # Create the Tkinter root window
    root = Tk()

    # Hide the root window
    root.withdraw()

    # Open the file dialog
    file_path = askopenfilename(filetypes=filetypes)
    
    file_path = Path(file_path)
    #
    with open(str(self.lollms_paths.personal_models_path/self.config.binding_name/(file_path.stem+".reference")),"w") as f:
        f.write(file_path)
    
    return jsonify({
                    "status": True
                })
    
def add_model_reference(self):
    try:
        ASCIIColors.info("Creating a model reference")
        path = Path(request.path)
        ref_path=self.lollms_paths.personal_models_path/self.config.binding_name/(path.name+".reference")
        with open(ref_path,"w") as f:
            f.write(str(path))

        return jsonify({"status": True})   
    except Exception as ex:
        ASCIIColors.error(ex)
        trace_exception(ex)
        return jsonify({"status": False})   

def upload_model(self):      
    file = request.files['file']
    file.save(self.lollms_paths.personal_models_path/self.config.binding_name/file.filename)
    return jsonify({"status": True})

def get_available_models(self):
    """Get the available models

    Returns:
        _type_: _description_
    """
    if self.binding is None:
        return jsonify([])
    model_list = self.binding.get_available_models()
    return jsonify(model_list)