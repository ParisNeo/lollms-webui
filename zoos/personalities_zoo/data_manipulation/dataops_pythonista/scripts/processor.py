"""
project: lollms
personality: # Place holder: Personality name 
Author: # Place holder: creator name 
description: # Place holder: personality description
"""
from lollms.helpers import ASCIIColors
from fastapi import Request
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality
from lollms.prompting import LollmsContextDetails
import subprocess
from typing import Callable, Any
import random
from ascii_colors import get_trace_exception
from typing import Dict, Any
import importlib
# Helper functions
class Processor(APScript):
    """
    A class that processes model inputs and outputs.

    Inherits from APScript.
    """
    def __init__(
                 self, 
                 personality: AIPersonality,
                 callback = None,
                ) -> None:
        
        self.callback = None
        # Example entries
        #       {"name":"make_scripted","type":"bool","value":False, "help":"Makes a scriptred AI that can perform operations using python script"},
        #       {"name":"make_scripted","type":"bool","value":False, "help":"Makes a scriptred AI that can perform operations using python script"},
        # Supported types:
        # str, int, float, bool, list
        # options can be added using : "options":["option1","option2"...]        
        personality_config_template = ConfigTemplate(
            [
                {"name":"max_fails","type":"int","value":5, "help":"Maximum number of generation fails"},                
                {"name":"show_code","type":"bool","value":True, "help":"If true, this will show the generated code"},                
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
                                    "commands": { # list of commands (don't forget to add these to your config.yaml file)
                                        "help":self.help,
                                    },
                                    "default": None
                                },                           
                            ],
                            callback=callback
                        )
        
    def install(self):
        super().install()
        
        # requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Install dependencies using pip from requirements.txt
        # subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])      
        ASCIIColors.success("Installed successfully")        

    def help(self, prompt="", full_context=""):
        self.set_message_content(self.personality.help)
    
    def add_file(self, path, client, callback=None):
        """
        Here we implement the file reception handling
        """
        super().add_file(path, client, callback)


    def get_cols(self,files)->str:
        """
        This function takes a list of files, output folder path, and output path URL as input.
        It performs the user request based on the content of the files and returns the output in the specified format.
        If the user asks for plotting, it uses matplotlib to create a chart and saves it as a png in the output folder.
        If the user asks for computing something, it builds the code to perform the computation and returns the result as markdown code.
        """
        import pandas as pd
        outputs = []
        for file in files:
            if file.suffix == ".csv" or file.suffix == ".txt":
                df = pd.read_csv(file)
                outputs.append(str(df.columns.tolist()))
            elif file.suffix == ".xlsx":
                df = pd.read_excel(file)
                outputs.append(str(df.columns.tolist()))
        
        return outputs
    def get_types(self,files)->str:
        """
        This function takes a list of files, output folder path, and output path URL as input.
        It performs the user request based on the content of the files and returns the output in the specified format.
        If the user asks for plotting, it uses matplotlib to create a chart and saves it as a png in the output folder.
        If the user asks for computing something, it builds the code to perform the computation and returns the result as markdown code.
        """
        import pandas as pd
        outputs = []
        for file in files:
            if file.suffix == ".csv" or file.suffix == ".txt":
                df = pd.read_csv(file)
                outputs.append(str(df.dtypes))
            elif file.suffix == ".xlsx":
                df = pd.read_excel(file)
                outputs.append(str(df.dtypes))
        
        return outputs
    async def handle_request(self, data: dict, client:Client=None) -> Dict[str, Any]:
        """
        Handle client requests.

        Args:
            data (dict): A dictionary containing the request data.
            client (Client): A refertence to the client asking for this request.

        Returns:
            dict: A dictionary containing the response, including at least a "status" key.

        This method should be implemented by a class that inherits from this one.

        Example usage:
        ```
        handler = YourHandlerClass()
        client = checkaccess(lollmsServer, client_id)
        request_data = {"command": "some_command", "parameters": {...}}
        response = handler.handle_request(request_data, client)
        ```
        """        
        rnd_val=f"outgen_{random.randint(0,2000000000)}"
        code = data["code"]
        print(code)
        ASCIIColors.magenta(code)
        module_name = 'custom_module'
        spec = importlib.util.spec_from_loader(module_name, loader=None)
        module = importlib.util.module_from_spec(spec)
        output_folder = self.personality.lollms_paths.personal_outputs_path/self.personality.personality_folder_name/rnd_val
        output_folder.mkdir(exist_ok=True, parents=True)
        out = module.reply_to_user([str(f) for f in self.personality.text_files], str(output_folder))
        out= out.replace(str(output_folder),f"/outputs/{self.personality.personality_folder_name}/{rnd_val}")
        self.set_message_content(out)

    from lollms.client_session import Client
    def run_workflow(self,  context_details:LollmsContextDetails=None, client:Client=None,  callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, AIPersonality| None], bool]=None):
        """
        This function generates code based on the given parameters.

        Args:
            context_details (dict): A dictionary containing the following context details for code generation:
                - conditionning (str): The conditioning information.
                - documentation (str): The documentation information.
                - knowledge (str): The knowledge information.
                - user_description (str): The user description information.
                - discussion_messages (str): The discussion messages information.
                - positive_boost (str): The positive boost information.
                - negative_boost (str): The negative boost information.
                - current_language (str): The force language information.
                - fun_mode (str): The fun mode conditionning text
                - ai_prefix (str): The AI prefix information.
            client_id: The client ID for code generation.
            callback (function, optional): The callback function for code generation.

        Returns:
            None
        """
        prompt = context_details.prompt
        previous_discussion_text = context_details.discussion_messages
        previous_error =""
        code = ""
        self.callback = callback
        if len(self.personality.text_files)>0:
            done=False
            fails = 0
            types = self.get_types(self.personality.text_files)
            files_infos = ""
            for file, types_ in zip(self.personality.text_files, types):
                files_infos += f"file name:{file}\ncolumns with types:\n{types_}"
            while not done and fails < self.personality_config.max_fails:
                self.step_start(f"Building code, attempt {fails}")
                try:
                    print(context_details.discussion_messages)
                    module, code = self.build_and_execute_python_code(
                        context_details.discussion_messages,
                        "\n".join([
                        f"Build a python function called reply_to_user to perform the user request given the list of files that he provides:",
                        "The output should be crafted out of the data contained in one or multiple files depending on the user demand.",
                        "return a html text depicting the output.",
                        "It can be text or formatted html like table or img tags pointing to the saved plots or a tags pointing to generated file.",
                        "Files list with their columns:",
                        f"{files_infos}",
                        f"{self.config.start_header_id_template}previous code attempt:\n```python\n{code}\n```\n" if code!="" else "",
                        f"{self.config.start_header_id_template}detected bug:\n{previous_error}" if previous_error != "" else "",
                        ]),
                        "def reply_to_user(files, output_folder)->str:",
                        "\n".join([
                            "import pandas as pd",
                        ])                        
                        )
                    rnd_val=f"outgen_{random.randint(0,2000000000)}"
                    output_folder = self.personality.lollms_paths.personal_outputs_path/self.personality.personality_folder_name/rnd_val
                    output_folder.mkdir(exist_ok=True, parents=True)
                    out = module.reply_to_user([str(f) for f in self.personality.text_files], str(output_folder))
                    out= out.replace(str(output_folder),f"/outputs/{self.personality.personality_folder_name}/{rnd_val}")
                    
                    if self.personality_config.show_code:
                        out = f"```python\n{code}\n```\n"+out
                    ui= "\n".join([
                        '',
                        f'<button id="_{rnd_val}">Reexecute</button>',
                        '<script>',
                        f'    document.getElementById("_{rnd_val}")'+'.addEventListener("click", function() {',
                        '        console.log("reexecuting")',
                        '        var xhr = new XMLHttpRequest();',
                        '        var url = "/post_to_personality";',
                        '        xhr.open("POST", url, true);',
                        '        xhr.setRequestHeader("Content-Type", "application/json");',
                        '        xhr.onreadystatechange = function () {',
                        '            if (xhr.readyState === 4 && xhr.status === 200) {',
                        '                var json = JSON.parse(xhr.responseText);',
                        '                console.log(json);',
                        '            }',
                        '        };',
                        '        var data = JSON.stringify({"code": '+f'`{code}`'+'});',
                        '        xhr.send(data);',
                        '    });',
                        '</script>',
                    ])

                    self.set_message_html(ui)
                        
                    self.set_message_content(out)
                    done = True
                    self.step_end(f"Building code, attempt {fails}")
                except Exception as ex:
                    previous_error=str(get_trace_exception(ex))
                    self.step_end(f"Building code, attempt {fails}",False)
                    fails += 1
                    ASCIIColors.error(str(ex))
                    if fails < self.personality_config.max_fails:
                        out = "Failed to perform the task :(.\nLet me try again..."
                    else:
                        out = "Failed to perform the task :(.\nDon't be harsh, I'm still learning :(.Try using a bigger model or modify the parameters of the AI"
                    self.set_message_content(out)
        else:
            self.personality.info("Generating")
            self.callback = callback
            out = self.fast_gen(previous_discussion_text)
            self.set_message_content(out)
        return out

