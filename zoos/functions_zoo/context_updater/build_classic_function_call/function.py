from pathlib import Path
from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails
from datetime import datetime
import yaml
from typing import List
from ascii_colors import ASCIIColors, trace_exception
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig

class BuildAFunction(FunctionCall):
    def __init__(self, app: LollmsApplication, client: Client):
        super().__init__("build_classic_function_call", app, FunctionType.CONTEXT_UPDATE, client)
        self.personality = app.personality

    def update_context(self, context: LollmsContextDetails, constructed_context: List[str]):
        """Add instructions for building a function call to the context"""
        instructions = """
### How to Build a Function Call

To create a new function call, provide the following details:
1. **Function Name**: A unique name for the function (e.g., `my_function`).
2. **Description**: A brief description of what the function does.
3. **Parameters**: A list of parameters the function accepts (name, description, and type).
4. **Return Value**: A description of what the function returns.

The AI will generate the Python and YAML files for you. Here’s an example:

```yaml
author: The user name (default to ParisNeo)
category: custom # must be custom as this is a custom function
class_name: MyFunction
name: my_function
description: A custom function.
parameters: # Parameters are parameters that do change depending on the request
- name: param1
  description: The first parameter.
  type: str (supported types are all default python types)
  ...
returns:
  status:
    description: The output of the function.
    type: str (only supports str)
version: 1.0.0
```

```python
from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails
from datetime import datetime
import yaml
from typing import List, Dict
from ascii_colors import ASCIIColors, trace_exception
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig

#Use pipmaster to check and install any missing module by its name
import pipmaster as pm
if not pm.is_installed("module name"):
    pm.install("module name")


class MyFunction(FunctionCall): #use the same name as class_name from the yaml file
    def __init__(self, app: LollmsApplication, client: Client):
        # Optionally if some static settings are needed:
        static_parameters=TypedConfig(
            ConfigTemplate([
            {
                    "name": "the_parameter_name", # spaces are forbidden in the name, use _
                    "type": "str", # supported types are: int, float, str, bool (dict and list are not supported²)
                    "value": "value string", # the value of the parameter
                    "options": ["value string","another value string" ...], # only for str type if there are fixed possibilities 
                    "help": "A help text to explain the parameter"                
            },
            {
                    "name": "the_parameter_name", # spaces are forbidden in the name, use _
                    "type": "int", # supported types are: int, float, str, bool (dict and list are not supported²)
                    "value": 7, # the value of the parameter
                    "help": "A help text to explain the parameter"                
            },
            ...
            ])
        )
        super().__init__("my_function_name", app, FunctionType.CLASSIC, client, static_parameters) # replace the string with the function name with no spaces, if no static_parameters are needed, just don't put the parameter here.
        # You can use this.static_parameters.the_parameter_name to recover parameters from the static parameters
        \"\"\"
        Make sur to use app.lollms_paths.personal_outputs_path for any output files the function will output unless secified by the user
        Extract the static parameters from the dictionary here. these are parameters that can be set by the user in the settings of the function call in the ui.
        it is a simple dictionary
        \"\"\"
        self.personality = app.personality # Personlity has many usefil LLM tools
        \"\"\"
        Here are some of the functionalities of personality
        1 we can call an LLM and make it generate text using fastgen method
        text = self.personality.fastgen(prompt, callback=None)
        callback is optional if used then it must be a function that takes the generated chunk, the chunk_type and a dict containing information
        use self.personality.sink to prevent showing the generation chunks to the user.
        summary = self.personality.sequential_summarize(
          text, # The text to summerize
          summary_context="", # this is a prompt to the ai when it is extracting information from the chunks and updating its memory content before doing the final extraction
          task="Create final summary using this memory.", # the final text synthesis after recovering all important informations from the text
          format="bullet points", #The output format
          tone="neutral", # The tone
          ctx_size=4096, #the size of context
          callback = None)
        Ask the AI yes no question. Very useful to understand some text if we have two possibilities
        answer = self.personality.yes_no(
          question: str, # the question
          context:str="", # context about which the question is asked (must be string)
          max_answer_length: int = None, conditionning="", return_explanation=False, callback = None)
        2 we can ask the ai to generate code 
        self.personality.generate_code(       
            prompt,         # The code generation prompt
            images=[],      # optional, if the user needs to use an image that contains the algorithm or some information he can send images here
            template:str|None=None,  # A template of the code (for example if it is json, a template of the json) (thisis a string)
            language:str="json",# The language of the output
            code_tag_format:str="markdown",  # or "html" 
            accept_all_if_no_code_tags_is_present:bool=False, 
            max_continues:int=3, #Maximum number of continues if the llm did not generate a complete text
            include_code_directives:int=True  # Make code directives optional
        )
        the output is a string containing the code
        full_context = context.build_prompt(self.app.template,custom_entries=[#here we can add other text entries to be added at the end of the context#]) #this creates a full prompt out of the context
        \"\"\"

    def update_context(self, context: LollmsContextDetails, constructed_context: List[str]):
        # Here you can add more instructions to the AI so that it can perform the task provided by the user correctly
        # You need to update the constructed_context list by adding extra information
        # You have access to all these informations from the context parameter:
        # --
        # client (str): Unique identifier for the client or user interacting with the LLM.
        # conditionning (Optional[str]): Optional field to store conditioning information or context for the LLM.
        # internet_search_infos (Optional[Dict]): Dictionary to store metadata or details about internet searches performed by the LLM.
        # internet_search_results (Optional[List]): List to store the results of internet searches performed by the LLM.
        # documentation (Optional[str]): Optional field to store documentation or reference material for the LLM.
        # documentation_entries (Optional[List]): List to store individual entries or sections of documentation.
        # user_description (Optional[str]): Optional field to store a description or profile of the user.
        # discussion_messages (Optional[List]): List to store the history of messages in the current discussion or conversation.
        # positive_boost (Optional[float]): Optional field to store a positive boost value for influencing LLM behavior.
        # negative_boost (Optional[float]): Optional field to store a negative boost value for influencing LLM behavior.
        # current_language (Optional[str]): Optional field to store the current language being used in the interaction.
        # fun_mode (Optional[bool]): Optional boolean field to enable or disable "fun mode" for the LLM.
        # think_first_mode (Optional[bool]): Optional boolean field to enable or disable "think first mode" for the LLM.
        # ai_prefix (Optional[str]): Optional field to store a prefix or identifier for the AI in the conversation.
        # extra (Optional[str]): Optional field to store additional custom or extra information.
        # available_space (Optional[int]): Optional field to store the available space or capacity for the context.
        # skills (Optional[Dict]): Dictionary to store skills or capabilities of the LLM.
        # is_continue (Optional[bool]): Optional boolean field to indicate if the LLM is continuing from a previous chunk or context.
        # previous_chunk (Optional[str]): Optional field to store the previous chunk of text or context.
        # prompt (Optional[str]): Optional field to store the current prompt or input for the LLM.
        # function_calls (Optional[List]): List to store function calls or actions performed by the LLM.
        # debug (bool): Enable or disable debug mode.
        # ctx_size (int): The maximum context size for the LLM.
        # max_n_predict (Optional[int]): The maximum number of tokens to generate.
        # model : The model (required to perform tokenization)
        # --
        # if you don't need to add anything to the context, just return the received constructed_context without changes
        # Do not put in the context information about the parameters of the function as it will automatically be added
        # Only use it if you need some extra information for the AI to call the function with more context information 
        # return the updated constructed_context        
        
    def execute(self, context: LollmsContextDetails, *args, **kwargs):
        # You can recover the parameters stated in the yaml from kwargs
        # use kwargs.get("the parameter name",default value) to recover the parameters
        # here do the requested functionality of the function call and return a string
        # if the performed action needs to be reviewed by an llm before outputting a resule, 
        # use self.personality.fastgen or self.personality.generate_code to generate the output then return that output
        # the current discussion assets should be stored in client.discussion.discussion_folder
        return "Your output as a string"
```
"""
        constructed_context.append(instructions)
        return constructed_context

    def process_output(self, context: LollmsContextDetails, llm_output: str):
        """Generate Python and YAML files based on the AI's output"""
        try:
            # Extract code blocks from the AI's output
            codes = self.personality.extract_code_blocks(llm_output)
            if len(codes) >= 2:  # Expecting one Python and one YAML block
                python_code = None
                yaml_code = None

                for code in codes[:2]:
                    if code["type"] == "python":
                        python_code = code["content"]
                    elif code["type"] == "yaml":
                        yaml_code = code["content"]
                        yaml_data = yaml.safe_load(yaml_code)

                folder:Path = self.app.lollms_paths.custom_function_calls_path / yaml_data["name"]
                folder.mkdir(exist_ok=True, parents=True)
                with open(folder / f"function.py", "w", encoding="utf-8") as f:
                    f.write(python_code)

                with open(folder / f"config.yaml", "w", encoding="utf-8") as f:
                    f.write(yaml_code)

                self.personality.set_message_html(self.personality.build_message_element(f"Function '{yaml_data['name']}' created successfully in '{folder}'!"), client_id=self.client.client_id)
                return llm_output
            else:
                return "Error: The AI was not smart enough to generate the required code blocks. Please try again."
        except Exception as e:
            trace_exception(e)
            return f"Error: {e}"