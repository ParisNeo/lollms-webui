import os
import subprocess
from typing import Callable
from lollms.helpers import ASCIIColors, trace_exception
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality, MSG_OPERATION_TYPE

class Processor(APScript):
    def __init__(self, personality: AIPersonality, callback: Callable = None) -> None:
        personality_config_template = ConfigTemplate([
            {"name": "extension_name", "type": "string", "value": "my-vscode-extension", "help": "Name of the VSCode extension"},
            {"name": "author", "type": "string", "value": "Your Name", "help": "Author of the extension"},
            {"name": "description", "type": "string", "value": "A VSCode extension", "help": "Short description of the extension"},
        ])
        personality_config_vals = BaseConfig.from_template(personality_config_template)
        personality_config = TypedConfig(personality_config_template, personality_config_vals)
        
        super().__init__(
            personality,
            personality_config,
            callback=callback
        )

    def install(self):
        super().install()
        # Check if Node.js is installed
        try:
            subprocess.run(["node", "--version"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            self.InfoMessage("Node.js is not installed. Please install Node.js before continuing.")
            return False
        
        # Check if Yeoman and VSCode Extension Generator are installed
        try:
            subprocess.run(["yo", "--version"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            self.step_start("Installing Yeoman and VSCode Extension Generator...")
            subprocess.run(["npm", "install", "-g", "yo", "generator-code"], check=True)
            self.step_end("Yeoman and VSCode Extension Generator installed successfully.")
        except Exception as ex:
            trace_exception(ex)
            self.step_start("Installing Yeoman and VSCode Extension Generator...")
            try:
                subprocess.run(["npm", "install", "-g", "yo", "generator-code"], check=True)
            except Exception as ex:
                trace_exception(ex)
            self.step_end("Yeoman and VSCode Extension Generator installed successfully.")

        return True

    def run_workflow(self, prompt: str, previous_discussion_text: str = "", callback: Callable = None, context_details: dict = None, client=None):
        self.callback = callback
        self.client = client

        if not self.install():
            return

        self.step_start("Initializing VSCode Extension Project")
        
        # Create project directory
        project_dir = os.path.join(os.getcwd(), self.personality_config.extension_name)
        os.makedirs(project_dir, exist_ok=True)
        os.chdir(project_dir)

        # Run Yeoman to scaffold the extension
        self.step_start("Scaffolding VSCode Extension")
        self.scaffold_extension()
        self.step_end("VSCode Extension scaffolded successfully")

        # Implement extension functionality
        self.step_start("Implementing Extension Functionality")
        self.implement_extension()
        self.step_end("Extension functionality implemented")

        # Package the extension
        self.step_start("Packaging the Extension")
        self.package_extension()
        self.step_end("Extension packaged successfully")

        self.set_message_content(f"VSCode extension '{self.personality_config.extension_name}' has been created and packaged successfully. You can find the .vsix file in the project directory.")

    def scaffold_extension(self):
        answers = [
            self.personality_config.extension_name,  # Extension name
            self.personality_config.description,     # Description
            self.personality_config.author,          # Author
            "Yes",                                   # Initialize a git repository
            "JavaScript"                             # Language
        ]

        process = subprocess.Popen(
            ["yo", "code"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        for answer in answers:
            process.stdin.write(f"{answer}\n")
            process.stdin.flush()

        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            self.step_start(f"Error scaffolding extension: {stderr}")
            return False

        return True

    def implement_extension(self):
        extension_js_path = os.path.join("extension.js")
        
        prompt = f"""
        Create a VSCode extension that does the following:
        1. Adds a new command to VSCode called "{self.personality_config.extension_name}"
        2. When the command is executed, it shows an information message with the text "Hello from {self.personality_config.extension_name}!"
        3. The command should be available in the Command Palette

        Provide the full content for the extension.js file.
        """

        code = self.generate_code(prompt, max_size=2000)
        
        if code:
            with open(extension_js_path, "w") as f:
                f.write(code)
            self.step_end("Extension functionality implemented successfully")
        else:
            self.step_start("Failed to generate extension code")

    def package_extension(self):
        try:
            subprocess.run(["npm", "install", "-g", "vsce"], check=True)
            subprocess.run(["vsce", "package"], check=True)
            self.step_end("Extension packaged successfully")
        except subprocess.CalledProcessError as e:
            self.step_start(f"Error packaging extension: {str(e)}")

    def help(self, prompt, full_context):
        return """
        This personality helps you create a full VSCode extension. Here are the main steps:

        1. Initialize the project structure
        2. Scaffold the extension using Yeoman
        3. Implement the extension functionality
        4. Package the extension

        You can customize the extension name, author, and description in the personality settings.

        To start, simply run the personality and follow the prompts.
        """