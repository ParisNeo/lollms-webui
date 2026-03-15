
from ascii_colors import ASCIIColors

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lollms.app import LollmsApplication

from lollms.binding import BindingBuilder
from lollms.config import InstallOption
from lollms.personality import PersonalityBuilder
from lollms.helpers import trace_exception

from tqdm import tqdm
import pkg_resources
from pathlib import Path
import yaml
import sys
class Menu:
    """Console menu tool that allows the user to select options."""

    def __init__(self, name, options):
        """
        Initialize a new menu instance.

        Parameters:
            name (str): The name of the menu.
            options (list): A list of menu options, each represented as a dictionary
                            with 'name' as the option display name, 'fn' as the function
                            to be called when the user selects the option, an optional
                            'help' message to display a brief description of the option,
                            and an optional 'exit_after_exec' flag to exit the menu
                            automatically after executing the function.
        """
        self.name = name
        self.options = options

    def show(self, menu_structure=None):
        """
        Display the menu options to the user and handle the user's choice.

        Parameters:
            menu_structure (list, optional): A list of menu options to use instead of
                                             the ones sent to the constructor. If None,
                                             it uses the options sent to the constructor.

        Note: If both `menu_structure` and options sent to the constructor are None,
              the method will raise a ValueError.
        """
        if menu_structure is None and not self.options:
            raise ValueError("Menu options not provided.")

        if menu_structure is not None:
            current_options = menu_structure
        else:
            current_options = self.options

        while True:
            ASCIIColors.cyan(f"\n--- {self.name.upper()} MENU ---")
            for i, option in enumerate(current_options, start=1):
                ASCIIColors.yellow(f"{i}.",end="")
                print(f" {option['name']}")
            ASCIIColors.yellow("0.",end="")
            print(" Go back to the previous menu" if self.name != "Main" else "0. Exit")
            print("help")

            choice = input("Select an option: ")
            if choice.isdigit():
                choice = int(choice)
                if 0 <= choice <= len(current_options):
                    if choice == 0:
                        if self.name == "Main":
                            print("Exiting the menu.")
                            break
                        else:
                            return
                    else:
                        chosen_option = current_options[choice - 1]
                        sub_menu = chosen_option.get('sub_menu')
                        exit_after_exec = chosen_option.get('exit_after_exec', False)
                        if sub_menu:
                            self.show(sub_menu)
                        else:
                            chosen_option['fn']()
                            if exit_after_exec:
                                print(f"Exiting {self.name.upper()} menu.")
                                return
                else:
                    print("Invalid option. Please select again.")
            elif choice.lower() == "help":
                self.display_help(current_options)
            else:
                print("Invalid input. Please enter a number or 'help' for assistance.")

    def display_help(self, options):
        """
        Display a brief description of each option available in the menu.

        Parameters:
            options (list): The list of menu options to display the help for.
        """
        print(f"\n--- {self.name.upper()} MENU HELP ---")
        for option in options:
            help_msg = option.get('help', "No help available.")
            print(f"{option['name']}: {help_msg}")
    def yes_no_question(self, question):
        """
        Ask the user a yes or no question and wait for a valid response.

        Parameters:
            question (str): The question to be displayed to the user.

        Returns:
            bool: True if the user answers 'yes', False if the user answers 'no'.
        """
        while True:
            response = input(f"{question} (yes/no): ").lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Invalid response. Please answer with 'yes' or 'no' (or 'y'/'n').")

class MainMenu(Menu):
    def __init__(self, lollms_app:'LollmsApplication', callback=None):
        self.binding_infs = []
        self.lollms_app = lollms_app
        self.callback = callback
        main_menu_options = [
            {'name': 'Main settings', 'fn': self.main_settings, 'help': "Show main settings."},
            {'name': 'Select Binding', 'fn': self.select_binding, 'help': "Choose a binding."},
            {'name': 'Select Model', 'fn': self.select_model, 'help': "Choose a model."},
            {'name': 'View mounted Personalities', 'fn': self.vew_mounted_personalities, 'help': "View all currently mounted personalities."},
            {'name': 'Mount Personality', 'fn': self.mount_personality, 'help': "Mount a new personality."},
            {'name': 'Unmount Personality', 'fn': self.unmount_personality, 'help': "Unmount a personality."},
            {'name': 'Select Personality', 'fn': self.select_personality, 'help': "Choose a personality."},
            {'name': 'Reinstall Binding', 'fn': self.reinstall_binding, 'help': "Reinstall the selected binding."},
            {'name': 'Reinstall current Personality', 'fn': self.reinstall_personality, 'help': "Reinstall the current selected personality."},
            {'name': 'Reset all installs', 'fn': self.lollms_app.reset_all_installs, 'help': "Reset all installed personalities."},
            {'name': 'Reset paths', 'fn': self.lollms_app.lollms_paths.resetPaths, 'help': "Reset all paths to default."},
        ]
        super().__init__("Lollms Main menu", main_menu_options)

    def main_settings(self):
        self.show([
            {'name': 'Set host', 'fn': self.set_host, 'help': "Sets the host name."},
            {'name': 'Set port', 'fn': self.set_port, 'help': "Sets the port number."},
            {'name': 'Set user name', 'fn': self.set_user_name, 'help': "Sets t1he user name."},
            {'name': 'Set use user name in discussion', 'fn': self.set_use_user_name_in_discussions, 'help': "Sets the user name."},
        ])
    def set_host(self):
        print(f"Current host name : {self.lollms_app.config.host}")
        self.lollms_app.config.host = input("New host name:")
        self.lollms_app.config.save_config()

    def set_port(self):
        print(f"Current port number : {self.lollms_app.config.port}")
        self.lollms_app.config.port = int(input("New port number:"))
        self.lollms_app.config.save_config()


    def set_user_name(self):
        print(f"Current user name : {self.lollms_app.config.user_name}")
        self.lollms_app.config.user_name = input("New user name:")
        self.lollms_app.config.save_config()

    def set_use_user_name_in_discussions(self):
        ASCIIColors.info(f"Current status: {self.lollms_app.config.use_user_name_in_discussions}")
        self.lollms_app.config.use_user_name_in_discussions = self.yes_no_question('Use user name in dicsussion')
        self.lollms_app.config.save_config()

    def show_logo(self):
        print(f"{ASCIIColors.color_bright_yellow}")
        print("      ___       ___           ___       ___       ___           ___      ")
        print("     /\__\     /\  \         /\__\     /\__\     /\__\         /\  \     ")
        print("    /:/  /    /::\  \       /:/  /    /:/  /    /::|  |       /::\  \    ")
        print("   /:/  /    /:/\:\  \     /:/  /    /:/  /    /:|:|  |      /:/\ \  \   ")
        print("  /:/  /    /:/  \:\  \   /:/  /    /:/  /    /:/|:|__|__   _\:\~\ \  \  ")
        print(" /:/__/    /:/__/ \:\__\ /:/__/    /:/__/    /:/ |::::\__\ /\ \:\ \ \__\ ")
        print(" \:\  \    \:\  \ /:/  / \:\  \    \:\  \    \/__/~~/:/  / \:\ \:\ \/__/ ")
        print("  \:\  \    \:\  /:/  /   \:\  \    \:\  \         /:/  /   \:\ \:\__\   ")
        print("   \:\  \    \:\/:/  /     \:\  \    \:\  \       /:/  /     \:\/:/  /   ")
        print("    \:\__\    \::/  /       \:\__\    \:\__\     /:/  /       \::/  /    ")
        print("     \/__/     \/__/         \/__/     \/__/     \/__/         \/__/     ")




        print(f"{ASCIIColors.color_reset}")
        print(f"{ASCIIColors.color_red}Version: {ASCIIColors.color_green}{pkg_resources.get_distribution('lollms').version}")
        print(f"{ASCIIColors.color_red}By : {ASCIIColors.color_green}ParisNeo")
        print(f"{ASCIIColors.color_reset}")

    def show_commands_list(self):
        print()
        print("Commands:")
        print(f"   {ASCIIColors.color_red}├{ASCIIColors.color_reset} menu: shows main menu")        
        print(f"   {ASCIIColors.color_red}├{ASCIIColors.color_reset} help: shows this info")        
        print(f"   {ASCIIColors.color_red}├{ASCIIColors.color_reset} reset: resets the context")
        print(f"   {ASCIIColors.color_red}├{ASCIIColors.color_reset} <empty prompt>: forces the model to continue generating")
        print(f"   {ASCIIColors.color_red}├{ASCIIColors.color_reset} context_infos: current context size and space left before cropping")
        print(f"   {ASCIIColors.color_red}├{ASCIIColors.color_reset} start_log: starts logging the discussion to a text file")
        print(f"   {ASCIIColors.color_red}├{ASCIIColors.color_reset} stop_log: stops logging the discussion to a text file")
        print(f"   {ASCIIColors.color_red}├{ASCIIColors.color_reset} send_file: uploads a file to the AI")
        print(f"   {ASCIIColors.color_red}└{ASCIIColors.color_reset} exit: exists the console")
        
        if self.lollms_app.personality:
            if self.lollms_app.personality.help !="":
                print(f"Personality help:")
                print(f"{self.lollms_app.personality.help}")
            
        

    def show_menu(self, options, title="Menu:", selection:int=None):
        ASCIIColors.yellow(title)
        for index, option in enumerate(options):
            if selection is not None and index==selection:
                print(f"{ASCIIColors.color_green}{index + 1} - {option}{ASCIIColors.color_reset}")
            else:
                print(f"{ASCIIColors.color_green}{index + 1} -{ASCIIColors.color_reset} {option}")
        choice = input("Enter your choice: ")
        return int(choice) if choice.isdigit() else -1

    def select_binding(self):
        bindings_list = []
        print()
        print(f"{ASCIIColors.color_green}Current binding: {ASCIIColors.color_reset}{self.lollms_app.config['binding_name']}")
        for p in self.lollms_app.lollms_paths.bindings_zoo_path.iterdir():
            if p.is_dir() and not p.stem.startswith(".") and p.stem !="binding_template":
                if (p/"binding_card.yaml").exists():
                    with open(p/"binding_card.yaml", "r") as f:
                        card = yaml.safe_load(f)
                    models =[]
                    for accepted_model in card["accepted_models"]:
                        models_path = self.lollms_app.lollms_paths.models_zoo_path/f"{accepted_model}.yaml"
                        with open(models_path, "r") as f:
                            models += yaml.safe_load(f)

                    is_installed = (self.lollms_app.lollms_paths.personal_configuration_path/f"binding_{p.name}.yaml").exists()
                    entry=f"{ASCIIColors.color_green if is_installed else ''}{'*' if self.lollms_app.config['binding_name']==card['name'] else ''} {card['name']} (by {card['author']})"
                    bindings_list.append(entry)
                    entry={
                        "name":p.name,
                        "card":card,
                        "models":models,
                        "installed": is_installed
                    }
                    self.binding_infs.append(entry)
        bindings_list += ["Back"]
        choice = self.show_menu(bindings_list)
        if 1 <= choice <= len(bindings_list)-1:
            print(f"You selected binding: {ASCIIColors.color_green}{self.binding_infs[choice - 1]['name']}{ASCIIColors.color_reset}")
            self.lollms_app.config['binding_name']=self.binding_infs[choice - 1]['name']
            self.lollms_app.binding = self.lollms_app.load_binding()
            self.lollms_app.config['model_name']=None
            self.lollms_app.config.save_config()
        elif choice <= len(bindings_list):
            return
        else:
            print("Invalid choice!")

    def select_model(self):
        print()
        print(f"{ASCIIColors.color_green}Current binding: {ASCIIColors.color_reset}{self.lollms_app.config['binding_name']}")
        print(f"{ASCIIColors.color_green}Current model: {ASCIIColors.color_reset}{self.lollms_app.config['model_name']}")

        models_dir:Path = (self.lollms_app.lollms_paths.personal_models_path/self.lollms_app.config['binding_name'])
        models_dir.mkdir(parents=True, exist_ok=True)

        models_list = self.lollms_app.binding.list_models() + ["Install model", "Change binding", "Back"]
        choice = self.show_menu(models_list)
        if 1 <= choice <= len(models_list)-3:
            print(f"You selected model: {ASCIIColors.color_green}{models_list[choice - 1]}{ASCIIColors.color_reset}")
            self.lollms_app.config['model_name']=models_list[choice - 1]
            self.lollms_app.config.save_config()
            self.lollms_app.load_model()
        elif choice <= len(models_list)-2:
            self.install_model()
        elif choice <= len(models_list)-1:
            self.select_binding()
            self.select_model()
        elif choice <= len(models_list):
            return
        else:
            print("Invalid choice!")

    def install_model(self):

        models_list = ["Install model from internet","Install model from local file","Back"]
        choice = self.show_menu(models_list)
        if 1 <= choice <= len(models_list)-2:
            url = input("Give a URL to the model to be downloaded :")
            def progress_callback(blocks, block_size, total_size):
                tqdm_bar.total=total_size
                tqdm_bar.update(block_size)

            # Usage example
            with tqdm(total=100, unit="%", desc="Download Progress", ncols=80) as tqdm_bar:
                self.lollms_app.config.download_model(url,self.lollms_app.binding, progress_callback)
            self.select_model()
        elif choice <= len(models_list)-1:
            path = Path(input("Give a path to the model to be used on your PC:"))
            if path.exists():
                self.lollms_app.config.reference_model(path)
            self.select_model()
        elif choice <= len(models_list):
            return
        else:
            print("Invalid choice!")

    def mount_personality(self):
        print()
        ASCIIColors.red(f"Mounted personalities:")
        for i,personality in enumerate(self.lollms_app.config['personalities']):
            if i==self.lollms_app.config['active_personality_id']:
                ASCIIColors.green(personality)
            else:
                ASCIIColors.yellow(personality)
        personality_categories = [p.stem for p in (self.lollms_app.lollms_paths.personalities_zoo_path).iterdir() if p.is_dir() and not p.name.startswith(".")]+["Custom personalities","Back"]
        print("Select category")
        choice = self.show_menu(personality_categories)
        if 1 <= choice <= len(personality_categories)-1:
            category = personality_categories[choice - 1]
            print(f"You selected category: {ASCIIColors.color_green}{category}{ASCIIColors.color_reset}")
            if category == "Custom personalities":
                personality_names = [p.stem for p in (self.lollms_app.lollms_paths.custom_personalities_path).iterdir() if p.is_dir() and not p.name.startswith(".")]+["Back"]
            else:
                personality_names = [p.stem for p in (self.lollms_app.lollms_paths.personalities_zoo_path/category).iterdir() if p.is_dir() and not p.name.startswith(".")]+["Back"]
            print("Select personality")
            choice = self.show_menu(personality_names)
            if 1 <= choice <= len(personality_names)-1:
                name = personality_names[choice - 1]
                if category == "Custom personalities":
                    print(f"You selected personality: {ASCIIColors.color_green}{name}{ASCIIColors.color_reset}")
                    langs_dir = self.lollms_app.lollms_paths.custom_personalities_path/name/"languages"
                else:
                    print(f"You selected personality: {ASCIIColors.color_green}{name}{ASCIIColors.color_reset}")
                    langs_dir = self.lollms_app.lollms_paths.personalities_zoo_path/category/name/"languages"
                if langs_dir.exists():
                    languages = [f.stem for f in langs_dir.iterdir()]
                    print("Select language")
                    choice = self.show_menu(languages)
                    if 1 <= choice <= len(languages):
                        language = languages[choice - 1]
                        self.lollms_app.config["personalities"].append(f"{category}/{name}")
                    else:
                        print("Invalid choice!")
                else:
                    self.lollms_app.config["personalities"].append(f"{category}/{name}")
                self.lollms_app.mount_personality(len(self.lollms_app.config["personalities"])-1, callback = self.callback)
                self.lollms_app.config.save_config()
                print("Personality mounted successfully!")
            elif 1 <= choice <= len(personality_names):
                return
            else:
                print("Invalid choice!")
        elif 1 <= choice <= len(personality_categories):
            return
        else:
            print("Invalid choice!")

    def vew_mounted_personalities(self):
        ASCIIColors.info("Here is the list of mounted personalities")
        entries = self.lollms_app.config['personalities']
        for id, entry in enumerate(entries):
            if id != self.lollms_app.config.active_personality_id:
                ASCIIColors.yellow(f"{id+1} - {entry}")
            else:
                ASCIIColors.green(f"{id+1} - {entry}")
        self.show_menu(["Back"])


    def unmount_personality(self):
        ASCIIColors.info("Select personality to unmount")
        entries = self.lollms_app.config['personalities']+["Back"]
        try:
            choice = int(self.show_menu(entries, self.lollms_app.config['active_personality_id']))-1
            if choice<len(entries)-1:
                self.lollms_app.unmount_personality(choice)
        except Exception as ex:
            ASCIIColors.error(f"Couldn't uhnmount personality.\nGot this exception:{ex}")

    def select_personality(self):
        ASCIIColors.info("Select personality to activate")
        entries = self.lollms_app.config['personalities']+["Back"]
        try:
            choice = int(self.show_menu(entries, self.lollms_app.config['active_personality_id']))-1
            if choice<len(entries)-1 and choice>=0:
                if self.lollms_app.select_personality(choice):
                    ASCIIColors.success(f"Selected personality: {self.lollms_app.personality.name}")
        except Exception as ex:
            ASCIIColors.error(f"Couldn't set personality.\nGot this exception:{ex}")
            trace_exception(ex)

    def reinstall_binding(self):
        lollms_app = self.lollms_app
        bindings_list = []
        print()
        print(f"{ASCIIColors.color_green}Current binding: {ASCIIColors.color_reset}{self.lollms_app.config['binding_name']}")
        for p in self.lollms_app.lollms_paths.bindings_zoo_path.iterdir():
            if p.is_dir() and not p.stem.startswith(".") and p.stem !="binding_template":
                if (p/"binding_card.yaml").exists():
                    with open(p/"binding_card.yaml", "r") as f:
                        card = yaml.safe_load(f)
                    models =[]
                    for accepted_model in card["accepted_models"]:
                        models_path = self.lollms_app.lollms_paths.models_zoo_path/f"{accepted_model}.yaml"
                        with open(models_path, "r") as f:
                            models += yaml.safe_load(f)

                    is_installed = (self.lollms_app.lollms_paths.personal_configuration_path/f"binding_{p.name}.yaml").exists()
                    entry=f"{ASCIIColors.color_green if is_installed else ''}{'*' if self.lollms_app.config['binding_name']==card['name'] else ''} {card['name']} (by {card['author']})"
                    bindings_list.append(entry)
                    entry={
                        "name":p.name,
                        "card":card,
                        "models":models,
                        "installed": is_installed
                    }
                    self.binding_infs.append(entry)
        bindings_list += ["Back"]
        choice = self.show_menu(bindings_list)
        if 1 <= choice <= len(bindings_list)-1:
            print(f"You selected binding: {ASCIIColors.color_green}{self.binding_infs[choice - 1]['name']}{ASCIIColors.color_reset}")
            self.lollms_app.config['binding_name']=self.binding_infs[choice - 1]['name']

            try:
                lollms_app.binding = BindingBuilder().build_binding(lollms_app.config, lollms_app.lollms_paths,InstallOption.FORCE_INSTALL, lollmsCom=self)
            except Exception as ex:
                print(ex)
                print(f"Couldn't find binding. Please verify your configuration file at {lollms_app.config.file_path} or use the next menu to select a valid binding")
                self.select_binding()

            self.lollms_app.config['model_name']=None
            self.lollms_app.config.save_config()
        elif choice <= len(bindings_list):
            return
        else:
            print("Invalid choice!")


    
    def reinstall_personality(self, callback=None):
        lollms_app = self.lollms_app
        try:
            lollms_app.personality = PersonalityBuilder(lollms_app.lollms_paths, lollms_app.config, lollms_app.model, installation_option=InstallOption.FORCE_INSTALL, callback=callback).build_personality()
        except Exception as ex:
            ASCIIColors.error(f"Couldn't load personality. Please verify your configuration file at {lollms_app.configuration_path} or use the next menu to select a valid personality")
            ASCIIColors.error(f"Binding returned this exception : {ex}")
            trace_exception(ex)
            ASCIIColors.error(f"{lollms_app.config.get_personality_path_infos()}")
            print("Please select a valid model or install a new one from a url")
            self.select_model()

    def main_menu(self):
        self.show()

