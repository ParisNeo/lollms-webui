from pathlib import Path
from ascii_colors import ASCIIColors

from typing import Any
import yaml
from enum import Enum

class InstallOption(Enum):
    """Enumeration for installation options."""
    
    NEVER_INSTALL = 1
    """Do not install under any circumstances."""
    
    INSTALL_IF_NECESSARY = 2
    """Install if necessary, but do not force installation."""
    
    FORCE_INSTALL = 3
    """Force installation, regardless of current state."""


class ConfigTemplate:
    """
    A class representing a configuration template.

    The `ConfigTemplate` class provides functionality to define and manage configuration entries in the form of a template.

    Attributes:
        template (list): A list of dictionaries representing configuration entries.

    Methods:
        add_entry(entry_name, entry_value, entry_type, entry_min=None, entry_max=None):
            Adds a new entry to the configuration template.
        __getitem__(key):
            Retrieves the configuration entry with the specified key.
        __getattr__(key):
            Retrieves the configuration entry with the specified key as an attribute.
        __setattr__(key, value):
            Sets the value of the configuration entry with the specified key.
        __setitem__(key, value):
            Sets the value of the configuration entry with the specified key.
        __contains__(item):
            Checks if a configuration entry with the specified name exists in the template.
    """

    def __init__(self, template: list = None) -> None:
        """
        Initializes a new instance of the `ConfigTemplate` class.

        Args:
            template (list, optional): A list of dictionaries representing configuration entries. Defaults to an empty list.

        Raises:
            ValueError: If the `template` parameter is not a list of dictionaries or if any entry is missing required fields.
        """
        if template is None:
            template = []
        elif not isinstance(template, list):
            raise ValueError("Template must be a list of dictionaries.")
        else:
            for entry in template:
                if not isinstance(entry, dict):
                    raise ValueError("Each entry in the template must be a dictionary.")
                required_fields = ["name", "value", "type"]
                missing_fields = [field for field in required_fields if field not in entry]
                if missing_fields:
                    raise ValueError(f"Missing fields {', '.join(missing_fields)} in template entry.")
        self.template = template

    def add_entry(self, entry_name, entry_value, entry_type, entry_min=None, entry_max=None, entry_help=""):
        """
        Adds a new entry to the configuration template.

        Args:
            entry_name (str): The name of the configuration entry.
            entry_value (Any): The value of the configuration entry.
            entry_type (str): The type of the configuration entry.
            entry_min (Any, optional): The minimum allowed value for the configuration entry. Defaults to None.
            entry_max (Any, optional): The maximum allowed value for the configuration entry. Defaults to None.
            entry_help (str, optional): the help string to describe the entry
        """
        self.template.append({
            "name": entry_name,
            "value": entry_value,
            "type": entry_type,
            "min": entry_min,
            "max": entry_max,
            "help": entry_help
        })

    def __getitem__(self, key):
        """
        Retrieves the configuration entry with the specified key.

        Args:
            key (str): The name of the configuration entry.

        Returns:
            dict: The configuration entry with the specified key, or None if not found.

        Raises:
            ValueError: If no configuration is loaded.
        """
        if self.template is None:
            raise ValueError("No configuration loaded.")
        for entry in self.template:
            if entry["name"] == key:
                return entry
        return None

    def __getattr__(self, key):
        """
        Retrieves the configuration entry with the specified key as an attribute.

        Args:
            key (str): The name of the configuration entry.

        Returns:
            dict: The configuration entry with the specified key, or None if not found.

        Raises:
            ValueError: If no configuration is loaded.
        """
        if key == "exceptional_keys":
            return super().__getattribute__(key)
        if key in  ["template"] or key.startswith("__"):
            return super().__getattribute__(key)
        else:
            if self.template is None:
                raise ValueError("No configuration loaded.")
            for entry in self.template:
                if entry["name"] == key:
                    return entry
            return None

    def __setattr__(self, key, value):
        """
        Sets the value of the configuration entry with the specified key.

        Args:
            key (str): The name of the configuration entry.
            value (Any): The new value for the configuration entry.

        Raises:
            ValueError: If no configuration is loaded or if the specified key is not found.
        """
        if key == "exceptional_keys":
            return super().__setattr__(key, value)
        if key in ["template"] or key.startswith("__"):
            super().__setattr__(key, value)
        else:
            if self.template is None:
                raise ValueError("No configuration loaded.")
            for entry in self.template:
                if entry["name"] == key:
                    entry["value"] = value
                    return
            raise ValueError(f"Configuration entry '{key}' not found.")

    def __setitem__(self, key, value):
        """
        Sets the value of the configuration entry with the specified key.

        Args:
            key (str): The name of the configuration entry.
            value (Any): The new value for the configuration entry.

        Raises:
            ValueError: If no configuration is loaded or if the specified key is not found.
        """
        if self.template is None:
            raise ValueError("No configuration loaded.")
        for entry in self.template:
            if entry["name"] == key:
                entry["value"] = value
                return
        raise ValueError(f"Configuration entry '{key}' not found.")

    def __contains__(self, item):
        """
        Checks if a configuration entry with the specified name exists in the template.

        Args:
            item (str): The name of the configuration entry.

        Returns:
            bool: True if the configuration entry exists, False otherwise.

        Raises:
            ValueError: If no configuration is loaded.
        """
        if self.template is None:
            raise ValueError("No configuration loaded.")
        for entry in self.template:
            if entry["name"] == item:
                return True
        return False



class BaseConfig:
    """
    A base class for managing configuration data.

    The `BaseConfig` class provides basic functionality to load, save, and access configuration data.

    Attributes:
        exceptional_keys (list): A list of exceptional keys that can be accessed directly as attributes.
        config (dict): The configuration data stored as a dictionary.

    Methods:
        to_dict():
            Returns the configuration data as a dictionary.
        __getitem__(key):
            Retrieves the configuration value associated with the specified key.
        __getattr__(key):
            Retrieves the configuration value associated with the specified key as an attribute.
        __setattr__(key, value):
            Sets the value of the configuration key.
        __setitem__(key, value):
            Sets the value of the configuration key.
        __contains__(item):
            Checks if the configuration contains the specified key.
        load_config(file_path):
            Loads the configuration from a YAML file.
        save_config(file_path):
            Saves the configuration to a YAML file.
    """

    def __init__(self, exceptional_keys: list = [], config: dict = None, file_path:Path|str=None):
        """
        Initializes a new instance of the `BaseConfig` class.

        Args:
            exceptional_keys (list, optional): A list of exceptional keys that can be accessed directly as attributes.
                Defaults to an empty list.
            config (dict, optional): The configuration data stored as a dictionary. Defaults to None.
        """
        self.exceptional_keys   = exceptional_keys
        self.config             = config
        self.file_path          = file_path

    @staticmethod
    def from_template(template:ConfigTemplate, exceptional_keys: list = [], file_path: Path | str = None):
        config = {}
        for entry in template.template:
            config[entry["name"]]=entry["value"]

        return BaseConfig(exceptional_keys, config, file_path)

    def to_dict(self):
        """
        Returns the configuration data as a dictionary.

        Returns:
            dict: The configuration data as a dictionary.
        """
        return self.config

    def __getitem__(self, key):
        """
        Retrieves the configuration value associated with the specified key.

        Args:
            key (Any): The key to retrieve the configuration value.

        Returns:
            Any: The configuration value associated with the key.

        Raises:
            ValueError: If no configuration is loaded.
            KeyError: If the specified key is not found in the configuration.
        """
        if self.config is None:
            raise ValueError("No configuration loaded.")
        return self.config[key]
    
    def copy(self):
        
        return BaseConfig(self.exceptional_keys, self.config.copy(), self.file_path)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieves the configuration value associated with the specified key.

        If the key is found, its value is returned. If the key is not found,
        the specified default value is returned.

        Args:
            key (Any): The key to retrieve the configuration value.
            default (Any, optional): The value to return if the key is not found.
                                    Defaults to None.

        Returns:
            Any: The configuration value associated with the key, or the default value.

        Raises:
            ValueError: If no configuration is loaded (`self.config` is None).
        """
        if self.config is None:
            raise ValueError("No configuration loaded.")
        return self.config.get(key, default)
    
    def __getattr__(self, key):
        """
        Retrieves the configuration value associated with the specified key as an attribute.

        Args:
            key (str): The key to retrieve the configuration value.

        Returns:
            Any: The configuration value associated with the key.

        Raises:
            ValueError: If no configuration is loaded.
            AttributeError: If the specified key is not found in the configuration.
        """
        if key == "exceptional_keys":
            return super().__getattribute__(key)
        if key in self.exceptional_keys + ["config","file_path","copy"] or key.startswith("__"):
            return super().__getattribute__(key)
        else:
            if self.config is None:
                raise ValueError("No configuration loaded.")
            return self.config[key]

    def __setattr__(self, key, value):
        """
        Sets the value of the configuration key.

        Args:
            key (str): The key of the configuration.
            value (Any): The new value for the configuration key.

        Raises:
            ValueError: If no configuration is loaded.
        """
        if key == "exceptional_keys":
            return super().__setattr__(key, value)
        if key in self.exceptional_keys + ["config","file_path","copy"] or key.startswith("__"):
            super().__setattr__(key, value)
        else:
            if self.config is None:
                raise ValueError("No configuration loaded.")
            self.config[key] = value

    def __setitem__(self, key, value):
        """
        Sets the value of the configuration key.

        Args:
            key (str): The key of the configuration.
            value (Any): The new value for the configuration key.

        Raises:
            ValueError: If no configuration is loaded.
        """
        if self.config is None:
            raise ValueError("No configuration loaded.")
        self.config[key] = value

    def __contains__(self, item):
        """
        Checks if the configuration contains the specified key.

        Args:
            item (str): The key to check.

        Returns:
            bool: True if the key is present in the configuration, False otherwise.

        Raises:
            ValueError: If no configuration is loaded.
        """
        if self.config is None:
            raise ValueError("No configuration loaded.")
        return item in self.config

    def load_config(self, file_path: Path | str = None):
        """
        Loads the configuration from a YAML file.

        Args:
            file_path (str or Path, optional): The path to the YAML file. If not provided, uses the previously set file path.

        Raises:
            ValueError: If no configuration file path is specified.
            FileNotFoundError: If the specified file path does not exist.
            yaml.YAMLError: If there is an error parsing the YAML file.
        """
        if file_path is None:
            if self.file_path is None:
                raise ValueError("No configuration file path specified.")
            file_path = self.file_path

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as stream:
            # Load the entire YAML file content into a temporary dict
            yaml_data = yaml.safe_load(stream)
            if self.config:
                # Check if the loaded data is a dictionary (YAML can load lists, etc.)
                if isinstance(yaml_data, dict):
                    # Iterate through the key-value pairs loaded from the YAML file
                    for key, value in yaml_data.items():
                        # Check if the key exists in the current self.config
                        if key in self.config:
                            # Update the value in self.config only if the key exists
                            self.config[key] = value
                            # print(f"Updated config: {key} = {value}") # Optional: for logging/debugging
                        # else:
                            # print(f"Ignoring key from file (not in existing config): {key}") # Optional

                elif yaml_data is not None: # Handle cases where YAML is valid but not a dict
                        print(f"Warning: YAML file '{file_path}' does not contain a dictionary at the root. No configuration updated.")
            else:
                self.config = yaml_data
            # If yaml_data is None (e.g., empty file), do nothing.

    def save_config(self, file_path=None):
        """
        Saves the configuration to a YAML file.

        Args:
            file_path (str or Path, optional): The path to the YAML file. If not provided, uses the previously set file path.

        Raises:
            ValueError: If no configuration is loaded.
            ValueError: If no configuration file path is specified.
            PermissionError: If the user does not have permission to write to the specified file path.
            yaml.YAMLError: If there is an error serializing the configuration to YAML.
        """
        if file_path is None:
            if self.file_path is None:
                raise ValueError("No configuration file path specified.")
            file_path = self.file_path

        if self.config is None:
            raise ValueError("No configuration loaded.")

        file_path = Path(file_path)
        with open(file_path, "w") as f:
            yaml.dump(self.config, f)





class TypedConfig:
    """
    This type of configuration contains a template of descriptions for the fields of the configuration.
    Field types: int, float, str.
    """

    def __init__(self, config_template: ConfigTemplate, config: BaseConfig=None):
        """
        Initializes a new instance of the `TypedConfig` class.

        Args:
            config_template (ConfigTemplate): The template of descriptions for the fields of the configuration.
            config (BaseConfig): The base configuration object containing the configuration values.
        """
        if config is None:
            config = BaseConfig(config={})
        self.config = config
        self.config_template = config_template

        # Fill the template values from the config values
        self.sync()
        
    def addConfigs(self, cfg_template:list):
        self.config_template.template += cfg_template
        self.sync()

    def update_template(self, new_template):
        self.config_template.template = new_template
        self.config = BaseConfig.from_template(self.config_template,self.config.exceptional_keys, self.config.file_path)

    def get(self, key, default_value=None):
        if self.config is None:
            raise ValueError("No configuration loaded.")
        if key in self.config:
            return self.config[key]
        else:
            return default_value


    def __getattr__(self, key):
        """
        Retrieves the configuration entry with the specified key as an attribute.

        Args:
            key (str): The name of the configuration entry.

        Returns:
            dict: The configuration entry with the specified key, or None if not found.

        Raises:
            ValueError: If no configuration is loaded.
        """
        if key in  ["config","config_template"] or key.startswith("__"):
            return super().__getattribute__(key)
        else:
            if self.config is None:
                raise ValueError("No configuration loaded.")
            return self.config[key]
        
    def __setattr__(self, key, value):
        """
        Retrieves the configuration entry with the specified key as an attribute.

        Args:
            key (str): The name of the configuration entry.

        Returns:
            dict: The configuration entry with the specified key, or None if not found.

        Raises:
            ValueError: If no configuration is loaded.
        """
        if key in ["config","config_template"] or key.startswith("__"):
            super().__setattr__(key, value)
        else:
            if self.config is None:
                raise ValueError("No configuration loaded.")
            self.config[key] = value
            self.sync()
            

    def __getitem__(self, key):
        """
        Retrieves the configuration entry with the specified key as an attribute.

        Args:
            key (str): The name of the configuration entry.

        Returns:
            dict: The configuration entry with the specified key, or None if not found.

        Raises:
            ValueError: If no configuration is loaded.
        """
        if self.config is None:
            raise ValueError("No configuration loaded.")
        return self.config[key]
    
    def __setitem__(self, key, value):
        """
        Retrieves the configuration entry with the specified key as an attribute.

        Args:
            key (str): The name of the configuration entry.

        Returns:
            dict: The configuration entry with the specified key, or None if not found.

        Raises:
            ValueError: If no configuration is loaded.
        """
        if self.config is None:
            raise ValueError("No configuration loaded.")
        self.config[key] = value   
        self.sync()

    def sync(self):
        """
        Fills the template values from the config values.
        """
        if self.config_template is None:
            raise ValueError("No configuration template loaded.")
        if self.config is None:
            raise ValueError("No configuration loaded.")

        for entry in self.config_template.template:
            entry_name = entry["name"]
            if entry_name in self.config:
                entry_value = self.config[entry_name]
                entry_type = entry["type"]

                # Validate and convert the entry value based on its type
                if entry_type == "int":
                    entry_value = int(entry_value)
                elif entry_type == "float":
                    entry_value = float(entry_value)
                elif entry_type == "str" or entry_type == "text" or entry_type == "string" or entry_type == "btn" or entry_type == "file" or entry_type == "folder":
                    entry_value = str(entry_value)                   
                elif entry_type == "bool":
                    entry_value = bool(entry_value)
                elif entry_type == "list":
                    entry_value = list(entry_value)
                elif entry_type == "dict":
                    entry_value = eval(entry_value)
                else:
                    raise ValueError(f"Invalid field type '{entry_type}' for entry '{entry_name}'.")

                # Skip checking min and max if the entry type is not numeric
                if entry_type == "int" or entry_type == "float":
                    entry_min = entry.get("min")
                    entry_max = entry.get("max")

                    # Check if the value is within the allowed range (if specified)
                    if entry_min is not None and entry_max is not None:
                        if entry_value < entry_min:
                            entry_value = entry_min
                        elif entry_value > entry_max:
                            entry_value = entry_max
                    elif entry_min is not None:
                        if entry_value < entry_min:
                            entry_value = entry_min
                    elif entry_max is not None:
                        if entry_value > entry_max:
                            entry_value = entry_max

                # Update the template entry with the converted value
                entry["value"] = entry_value
            else:
                self.config[entry_name] = entry["value"]

    def set_config(self, config: BaseConfig):
        """
        Sets the configuration and updates the values of the template.

        Args:
            config (BaseConfig): The base configuration object containing the configuration values.
        """
        self.config = config
        self.sync()

    def save(self, file_path:str|Path|None=None):
        self.config.save_config(file_path=file_path)
        
    def to_dict(self, use_template=False):
        if not use_template:
            return self.config
        else:
            return self.config_template
