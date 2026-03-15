from pathlib import Path
from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails
from datetime import datetime
import yaml
from typing import List
from ascii_colors import ASCIIColors, trace_exception

class BuildAFunction(FunctionCall):
    def __init__(self, app: LollmsApplication, client: Client):
        super().__init__("build_context_update_function", app, FunctionType.CONTEXT_UPDATE, client)
        self.personality = app.personality

    def update_context(self, context: LollmsContextDetails, constructed_context: List[str]):
        """Add instructions for building a function call to the context"""
        instructions_part_one = """
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
""" + self.personality.user_custom_header("task") + "generate the yaml file to fulfill the user request."

        yaml_code =  self.personality.generate_code("\n".join(constructed_context + [context.discussion_messages+instructions_part_one]),language="yaml")
        yaml_data = yaml.safe_load(yaml_code)
        self.personality.add_chunk_to_message_content("\n")
        folder:Path = self.app.lollms_paths.custom_function_calls_path / yaml_data["name"]
        folder.mkdir(exist_ok=True, parents=True)
        with open(folder / f"config.yaml", "w", encoding="utf-8") as f:
            f.write(yaml_code)
            
        instructions_part_two = """
```python
from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails
from ascii_colors import ASCIIColors, trace_exception
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
from typing import List, Dict
# Use pipmaster to check and install any missing module by its name
import pipmaster as pm
if not pm.is_installed("module name"):
    pm.install("module name")


class MyFunction(FunctionCall): #use the same name as class_name from the yaml file
    def __init__(self, app: LollmsApplication, client: Client): # This constructor must have this exact signature
        # Optionally if some static settings are needed. You need to build it exactly like this:
        static_parameters=TypedConfig(
            ConfigTemplate([
            {
                    "name": "the_parameter_name", # spaces are forbidden in the name, use _
                    "type": "str", # supported types are: int, float, str, bool (dict and list are not supported)
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
        # Initialize a CONTEXT_UPDATE function call that puts knowledge into the LLM context before the LLM is called.
        # It can also post process the LLM output.

        super().__init__("my_function_name", app, FunctionType.CONTEXT_UPDATE, client, static_parameters) # replace the string with the function name with no spaces, if no static_parameters are needed, just don't put the parameter here.
        # You can use this.static_parameters.the_parameter_name to recover parameters from the static parameters
        # for example, if I have a parameter named value, I can access it using this.static_parameters.value
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
        answer = self.personality.    yes_no(
          question: str, # the question
          context:str="", # context about which the question is asked (must be string)
          max_answer_length: int = None, conditionning="", return_explanation=False, callback = None)
        2 we can ask the ai to generate code 
        self.personality.generate_code(       
            prompt,         # The code generation prompt
            images=[],      # optional, if the user needs to use an image that contains the algorithm or some information he can send images here
            template=None,  # A template of the code (for example if it is json, a template of the json)
            language="json",# The language of the output
            code_tag_format="markdown",  # or "html" 
            accept_all_if_no_code_tags_is_present=False, 
            max_continues=3, #Maximum number of continues if the llm did not generate a complete text
            include_code_directives=True  # Make code directives optional
        )
        the output is a string containing the code
        \"\"\"
           
    def update_context(self, context: LollmsContextDetails, constructed_context: List[str]):
        # This method is mandatory for this kind of function calls
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
        # return the updated constructed_context

    def process_output(self, context: LollmsContextDetails, llm_output: str):
        # After the AI finish writing its answer we can post process it or do an extra thing after the end of the generation
        # llm_output contains the AI output, we still have access to the context if needed.
        # return a string 
```

Make sure the python code structure respects and implements the right methods.
Here is the yaml file:
```yaml
"""+yaml_code+"""
```
""" + self.personality.user_custom_header("task") + "generate the python file"

        python_code =  self.personality.generate_code("\n".join(constructed_context + [context.discussion_messages, instructions_part_two]),language="python")
        folder:Path = self.app.lollms_paths.custom_function_calls_path / yaml_data["name"]
        folder.mkdir(exist_ok=True, parents=True)
        with open(folder / f"function.py", "w", encoding="utf-8") as f:
            f.write(python_code)
        constructed_context.append(f"Building in background ... OK") 
        constructed_context.append(f"Function '{yaml_data['name']}' created successfully in '{folder}'!\nTell the user where he can find the function call.") 
        self.personality.add_chunk_to_message_content("\n")

        return constructed_context 

    def process_output(self, context: LollmsContextDetails, llm_output: str):
        """Generate Python and YAML files based on the AI's output"""
        return llm_output