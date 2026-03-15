from lollms.helpers import ASCIIColors, trace_exception
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality, MSG_OPERATION_TYPE
from lollms.types import MSG_TYPE
from typing import Callable
import os
import subprocess
import shutil

class Processor(APScript):

    def __init__(
                 self, 
                 personality: AIPersonality,
                 callback = None,
                ) -> None:
        # Get the current directory
        root_dir = personality.lollms_paths.personal_path
        # We put this in the shared folder in order as this can be used by other personalities.
        shared_folder = root_dir/"shared"
        self.sd_folder = shared_folder / "auto_sd"
        self.word_callback = None
        self.sd = None
        self.sd_models_folder = self.sd_folder/"models"/"Stable-diffusion"
        if self.sd_models_folder.exists():
            self.sd_models = [f.stem for f in self.sd_models_folder.iterdir()]
        else:
            self.sd_models = ["Not installeed"]
        personality_config_template = ConfigTemplate(
            [

                {"name": "destination_folder", "type": "string", "value": "", "help": "Folder where to build the VSCode extension"},

            ]
            )
        personality_config_vals = BaseConfig.from_template(personality_config_template)

        personality_config = TypedConfig(
            personality_config_template,
            personality_config_vals
        )
        super().__init__(
                            personality,
                            personality_config,
                            [
                                {
                                    "name": "idle",
                                    "commands": { # list of commands
                                    },
                                    "default": None
                                },                           
                            ],
                            callback=callback
                        )
        self.sd = None
        self.assets_path = None

    def install(self):
        super().install()
        # Install any necessary dependencies for VSCode extension development
        try:
            self.personality.ShowBlockingMessage("Installing VSCode Extension Generator")
            subprocess.run(["npm", "install", "-g", "yo", "generator-code"], check=True,shell=True)
            self.personality.info("Successfully installed Yeoman and VSCode Extension Generator.")
            self.personality.HideBlockingMessage()
        except subprocess.CalledProcessError:
            self.personality.HideBlockingMessage()
            self.personality.error("Failed to install Yeoman and VSCode Extension Generator. Please make sure Node.js and npm are installed.")

    def run_workflow(self, prompt: str, previous_discussion_text: str = "", callback: Callable = None, context_details: dict = None):
        self.callback = callback
        try:
            # Determine if the user wants to build a new VSCode extension
            if self.multichoice_question(
                "Does the user want to build a new VSCode extension?",
                ["Yes", "No"],
                context=prompt
            ) == "Yes":
                self.build_vscode_extension(prompt)
            else:
                # General discussion
                response = self.fast_gen(f"User: {prompt}\nAI: ")
                self.add_chunk_to_message_content(response)
        except Exception as e:
            trace_exception(e)
            self.personality.error(f"An error occurred: {str(e)}")

    def build_vscode_extension(self, prompt):
        self.step_start("Initializing VSCode Extension Project")

        # Get extension name
        extension_name = self.ai_query("What should be the name of the VSCode extension?", context=prompt)
        folder_name = extension_name.replace(" ", "_").lower()

        # Create project folder
        project_path = os.path.join(self.personality_config.destination_folder, folder_name)
        os.makedirs(project_path, exist_ok=True)

        # Initialize git repository
        self.initialize_git_repo(project_path)

        # Use Yeoman to scaffold the extension
        self.scaffold_extension(project_path, extension_name)

        self.step_end("Project initialized successfully")

        # Update package.json
        self.update_package_json(project_path, extension_name)

        # Create extension files
        self.create_extension_files(project_path, extension_name, prompt)

        # Show installation and publishing instructions
        self.show_instructions(folder_name)

    def initialize_git_repo(self, project_path):
        try:
            subprocess.run(["git", "init"], cwd=project_path, check=True)
            with open(os.path.join(project_path, ".gitignore"), "w") as f:
                f.write("node_modules\n.vscode\n*.vsix\n")
            self.personality.info("Git repository initialized with .gitignore")
        except subprocess.CalledProcessError:
            self.personality.warning("Failed to initialize git repository. Make sure git is installed.")

    def scaffold_extension(self, project_path, extension_name):
        try:
            subprocess.run(["yo", "code"], cwd=project_path, input=f"{extension_name}\n\n\n\n\n\n\n\n\n", text=True, check=True)
            self.personality.info("Extension scaffolded successfully")
        except subprocess.CalledProcessError:
            self.personality.error("Failed to scaffold the extension. Make sure Yeoman and generator-code are installed.")
            raise

    def update_package_json(self, project_path, extension_name):
        package_json_path = os.path.join(project_path, "package.json")
        if os.path.exists(package_json_path):
            with open(package_json_path, "r") as f:
                content = f.read()
            
            updated_content = self.generate_code(
                f"Update the following package.json content for the VSCode extension '{extension_name}':\n\n{content}\n\nMake necessary changes to improve the extension configuration.",
                max_size=2000
            )
            
            with open(package_json_path, "w") as f:
                f.write(updated_content)
            
            self.personality.info("package.json updated successfully")
        else:
            self.personality.warning("package.json not found. Skipping update.")

    def create_extension_files(self, project_path, extension_name, prompt):
        self.step_start("Creating extension files")

        # Main extension file
        main_file_path = os.path.join(project_path, "src", "extension.ts")
        main_file_content = self.generate_code(
            f"Create the main TypeScript file for the VSCode extension '{extension_name}' based on this description:\n\n{prompt}\n\nInclude necessary imports, activate function, and main functionality.",
            max_size=3000
        )
        with open(main_file_path, "w") as f:
            f.write(main_file_content)

        # README file
        readme_path = os.path.join(project_path, "README.md")
        readme_content = self.generate_code(
            f"Create a README.md file for the VSCode extension '{extension_name}' based on this description:\n\n{prompt}\n\nInclude sections for features, installation, usage, and configuration.",
            max_size=2000
        )
        with open(readme_path, "w") as f:
            f.write(readme_content)

        self.step_end("Extension files created successfully")

    def show_instructions(self, folder_name):
        instructions = f"""
        VSCode Extension '{folder_name}' has been created successfully!

        To install and test the extension:
        1. Open the extension folder in VSCode
        2. Run 'npm install' in the terminal to install dependencies
        3. Press F5 to open a new window with your extension loaded
        4. Find your extension in the Extensions view (Ctrl+Shift+X) and enable it
        5. Execute the command "Hello World" from the Command Palette (Ctrl+Shift+P)

        To package and publish the extension:
        1. Install vsce: npm install -g vsce
        2. Run 'vsce package' to create a .vsix file
        3. To publish:
           a. Create a publisher on https://marketplace.visualstudio.com/manage
           b. Run 'vsce publish' (you'll need a Personal Access Token)

        For more information, visit: https://code.visualstudio.com/api/working-with-extensions/publishing-extension
        """
        self.add_chunk_to_message_content(instructions)

    def ai_query(self, question, context="", max_length=100):
        response = self.generate_code(f"Context: {context}\n\nQuestion: {question}\n\nAnswer:", max_size=max_length)
        return response.strip()

if __name__ == "__main__":
    print("This script is not meant to be run directly.")