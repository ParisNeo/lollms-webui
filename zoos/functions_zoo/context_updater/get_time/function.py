import datetime
from lollms.app import LollmsApplication
from lollms.personality import AIPersonality
from lollms.function_call import FunctionCall, FunctionType
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails
from datetime import datetime
from typing import List
class GetTimeFunction (FunctionCall):
    def __init__(self, app: LollmsApplication, client:Client):
        super().__init__("get_time", app, FunctionType.CONTEXT_UPDATE, client)
        self.model = app.model
    
    def update_context(self, context: LollmsContextDetails, contructed_context:List[str]):
        contructed_context.append(f"Current date/time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return contructed_context
    
    def process_output(self, context: LollmsContextDetails, llm_output:str):
        return llm_output       