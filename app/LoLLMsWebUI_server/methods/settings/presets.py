from flask import jsonify
from pathlib import Path
from flask import request


def get_presets(self):
        presets = []
        presets_folder = Path("__file__").parent/"presets"
        for filename in presets_folder.glob('*.yaml'):
            with open(filename, 'r', encoding='utf-8') as file:
                preset = yaml.safe_load(file)
                if preset is not None:
                    presets.append(preset)
        presets_folder = self.lollms_paths.personal_databases_path/"lollms_playground_presets"
        presets_folder.mkdir(exist_ok=True, parents=True)
        for filename in presets_folder.glob('*.yaml'):
            with open(filename, 'r', encoding='utf-8') as file:
                preset = yaml.safe_load(file)
                if preset is not None:
                    presets.append(preset)
        return jsonify(presets)

def add_preset(self):
    # Get the JSON data from the POST request.
    preset_data = request.get_json()
    presets_folder = self.lollms_paths.personal_databases_path/"lollms_playground_presets"
    if not presets_folder.exists():
        presets_folder.mkdir(exist_ok=True, parents=True)

    fn = preset_data["name"].lower().replace(" ","_")
    filename = presets_folder/f"{fn}.yaml"
    with open(filename, 'w', encoding='utf-8') as file:
        yaml.dump(preset_data, file)
    return jsonify({"status": True})

def del_preset(self):
    presets_folder = self.lollms_paths.personal_databases_path/"lollms_playground_presets"
    if not presets_folder.exists():
        presets_folder.mkdir(exist_ok=True, parents=True)
        self.copy_files("presets",presets_folder)
    presets = []
    for filename in presets_folder.glob('*.yaml'):
        print(filename)
        with open(filename, 'r') as file:
            preset = yaml.safe_load(file)
            if preset is not None:
                presets.append(preset)
    return jsonify(presets)


def save_presets(self):
    """Saves a preset to a file.

    Args:
        None.

    Returns:
        None.
    """

    # Get the JSON data from the POST request.
    preset_data = request.get_json()

    presets_file = self.lollms_paths.personal_databases_path/"presets.json"
    # Save the JSON data to a file.
    with open(presets_file, "w") as f:
        json.dump(preset_data, f, indent=4)

    return jsonify({"status":True,"message":"Preset saved successfully!"})