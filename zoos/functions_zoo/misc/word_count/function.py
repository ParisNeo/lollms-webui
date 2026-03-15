from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client

class WordCountFunction(FunctionCall):
    def __init__(self, app: LollmsApplication, client: Client):
        super().__init__("word_count", FunctionType.CLASSIC, client)

    def execute(self, *args, **kwargs):
        # Extract the text input
        text = kwargs.get("text", "")
        
        # Call the custom logic to count words
        word_count = self._count_words(text)
        
        # Return the result as a string
        return f"The text contains {word_count} words."

    def _count_words(self, text):
        # Simple logic to count words
        return len(text.split())