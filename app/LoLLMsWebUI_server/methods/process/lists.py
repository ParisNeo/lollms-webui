from api.config import load_config
from lollms.helpers import ASCIIColors
from flask import jsonify
from pathlib import Path
from flask import request


def list_bindings(self):
    bindings_dir = self.lollms_paths.bindings_zoo_path  # replace with the actual path to the models folder
    bindings=[]
    for f in bindings_dir.iterdir():
        card = f/"binding_card.yaml"
        if card.exists():
            try:
                bnd = load_config(card)
                bnd["folder"]=f.stem
                installed = (self.lollms_paths.personal_configuration_path/"bindings"/f.stem/f"config.yaml").exists()
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
                icon_file = self.find_extension(self.lollms_paths.bindings_zoo_path/f"{f.name}", "logo", [".svg",".gif",".png"])
                if icon_file is not None:
                    icon_path = Path(f"bindings/{f.name}/logo{icon_file.suffix}")
                    bnd["icon"]=str(icon_path)

                bindings.append(bnd)
            except Exception as ex:
                print(f"Couldn't load backend card : {f}\n\t{ex}")
    return jsonify(bindings)

def list_extensions(self):
    return jsonify([])

def list_models(self):
    if self.binding is not None:
        models = self.binding.list_models(self.config)
        ASCIIColors.yellow("Listing models")
        return jsonify(models)
    else:
        return jsonify([])

def list_personalities_categories(self):
    personalities_categories_dir = self.lollms_paths.personalities_zoo_path  # replace with the actual path to the models folder
    personalities_categories = [f.stem for f in personalities_categories_dir.iterdir() if f.is_dir() and not f.name.startswith(".")]
    return jsonify(personalities_categories)

def list_personalities(self):
    category = request.args.get('category')
    if not category:
        return jsonify([])
        
    try:
        personalities_dir = self.lollms_paths.personalities_zoo_path/f'{category}'  # replace with the actual path to the models folder
        personalities = [f.stem for f in personalities_dir.iterdir() if f.is_dir() and not f.name.startswith(".")]
    except Exception as ex:
        personalities=[]
        ASCIIColors.error(f"No personalities found. Using default one {ex}")
    return jsonify(personalities)



def list_discussions(self):
    discussions = self.db.get_discussions()
    return jsonify(discussions)

def list_mounted_personalities(self):
    ASCIIColors.yellow("- Listing mounted personalities")
    return jsonify({"status": True,
                    "personalities":self.config["personalities"],
                    "active_personality_id":self.config["active_personality_id"]
                    })