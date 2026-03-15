from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails
from pathlib import Path
from typing import List, Dict

class CreateReadme(FunctionCall):
    def __init__(self, app: LollmsApplication, client: Client):
        super().__init__("create_readme", app, FunctionType.CLASSIC, client)
        self.personality = app.personality

    def update_context(self, context: LollmsContextDetails, constructed_context: List[str]):
        # No additional context needed for this function
        return constructed_context

    def execute(self, context: LollmsContextDetails, *args, **kwargs):
        """
        Creates a README.md file in the current discussion folder with the provided content.
        
        Args:
            context (LollmsContextDetails): The context details for the function call.
            **kwargs: Keyword arguments containing the parameters.
        
        Returns:
            str: Confirmation message after creating the README.md file.
        """
        # Get the content parameter
        content = kwargs.get("content", "")
        
        # Get the current discussion folder path
        discussion_folder = Path(self.client.discussion.discussion_folder)
        
        # Define the README.md file path
        readme_path = discussion_folder / "README.md"
        
        # Write the content to the README.md file
        with open(readme_path, "w", encoding="utf-8") as file:
            file.write(content)
        
        # Return confirmation message
        return f"README.md file created successfully at {readme_path}."