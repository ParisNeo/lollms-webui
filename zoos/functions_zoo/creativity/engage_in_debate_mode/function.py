from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.personality import AIPersonality
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails
from ascii_colors import ASCIIColors, trace_exception
import pipmaster as pm
from typing import List
import json 

class EngageInDebateMode(FunctionCall):
    """
    A function to engage in a playful debate with the user about various topics.

    Args:
        app (LollmsApplication): The main application object.
        client (Client): The client interacting with the application.
        static_parameters (dict, optional): Dictionary containing static parameters for the function.

    Attributes:
        personality (Personality): Access to personality methods for LLM interaction.
    """

    def __init__(self, app: LollmsApplication, client: Client):
        super().__init__("engage_in_debate_mode", app, FunctionType.CONTEXT_UPDATE, client)

    def update_context(self, context: LollmsContextDetails, constructed_context: List[str]):
        """
        Adds some humor to the debate context.

        Args:
            context (LollmsContextDetails): Context details for the debate.
            constructed_context (List[str]): List to update with humorous debate rules.

        Returns:
            List[str]: Updated context with debate rules.
        """
        collective:List[AIPersonality] = self.app.mounted_personalities
        collective_dict = {drone.name: drone for drone in collective}
        mounted_names = [drone.name for drone in collective]
        request_json = self.personality.generate_structured_content(f"This is a debate mode, we need to select some personalities from the list in order to debate the user prompt\nuser prompt:\n{context.prompt}\nList of potential personalities:\n{mounted_names}\nassistant:",template="\n```json\n{\n    personalities_names: [#Here place the list of names as strings. Make sure you select relevant personalities#]}",callback=self.personality.sink)
        selection = json.loads(request_json)
        debaters = selection["personalities_names"]
        for debater in debaters:
            context.conditionning = collective_dict[debater].personality_conditioning
            prompt = context.build_prompt(self.app.template, ignore_function_calls=True) + self.personality.ai_custom_header(debater)
            self.personality.new_message(f"## {debater}\n")
            output = self.personality.ai_custom_header(debater)+self.personality.fast_gen(prompt)
            context.discussion_messages+=self.personality.ai_custom_header(debater)+output+"\n"
            constructed_context.append(self.personality.ai_custom_header(debater)+output+"\n")
        
        constructed_context += "instruction: Wrap the debate\n"+self.personality.ai_full_header
        return constructed_context

    def process_output(self, context: LollmsContextDetails, llm_output: str):
        """
        Processes the AI's output to ensure it's in line with the fun debate mode.

        Args:
            context (LollmsContextDetails): Context details for the debate.
            llm_output (str): The AI's output to be processed.

        Returns:
            str: A processed and humorously enhanced output string.
        """
        

        return f"{llm_output}\n\nAnd remember, in this debate, the only winning move is to laugh!"