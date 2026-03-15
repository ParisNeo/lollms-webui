# processor.py

from typing import Callable, Dict, Any
from lollms.personality import APScript, AIPersonality
from lollms.types import MSG_OPERATION_TYPE
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate, InstallOption
import json
from pathlib import Path
import subprocess
from ascii_colors import ASCIIColors, trace_exception
import os, sys
from lollms.client_session import Client
import platform
import tempfile
import time
import subprocess
import os
import sys
import time
import threading
import queue

class CommandExecutor:
    def __init__(self, work_dir = None, shell='cmd.exe' if os.name == 'nt' else '/bin/bash'):
        self.work_dir = work_dir
        self.shell = shell
        self.process = subprocess.Popen(
            self.shell,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )

        self.stdout_queue = queue.Queue()
        self.stderr_queue = queue.Queue()

        # Start threads to read stdout and stderr
        threading.Thread(target=self._enqueue_output, args=(self.process.stdout, self.stdout_queue), daemon=True).start()
        threading.Thread(target=self._enqueue_output, args=(self.process.stderr, self.stderr_queue), daemon=True).start()

        self.execute_command(f"cd {work_dir}")

    def _enqueue_output(self, stream, queue):
        for line in iter(stream.readline, ''):
            queue.put(line)
        stream.close()

    def execute_command(self, command, timeout=5):
        try:
            # Send the command to the shell
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()

            # Collect output and errors
            output = ''
            errors = ''
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Fetch stdout
                while not self.stdout_queue.empty():
                    line = self.stdout_queue.get()
                    output += line

                # Fetch stderr
                while not self.stderr_queue.empty():
                    line = self.stderr_queue.get()
                    errors += line

                # Check if the process has terminated
                if self.process.poll() is not None:
                    break

                time.sleep(0.1)

            return {
                'stdout': output,
                'stderr': errors,
                'returncode': self.process.returncode or 0
            }
        except Exception as e:
            return {
                'stdout': '',
                'stderr': str(e),
                'returncode': -1,
                'error': 'An error occurred'
            }

    def get_current_directory(self):
        if os.name == 'nt':
            result = self.execute_command('cd')
        else:
            result = self.execute_command('pwd')
        
        # Extract the actual path from the output
        path = result['stdout'].strip().split('\n')[-1]
        return path

    def create_file(self, filename, content):
        try:
            with open(filename, 'w') as f:
                f.write(content)
            return {'success': True, 'message': f"File {filename} created successfully"}
        except Exception as e:
            return {'success': False, 'message': f"Error creating file {filename}: {str(e)}"}

    def close(self):
        self.process.stdin.close()
        self.process.terminate()
        self.process.wait(timeout=0.2)
class Processor(APScript):
    def __init__(self, personality: AIPersonality, callback: Callable = None) -> None:
        personality_config_template = ConfigTemplate([
            {"name": "work_folder", "type": "str", "value":"", "help": "The working directory"},
            {"name": "save_context_for_recovery", "type": "bool", "value":True, "help": "Saves current context for recovering from previous generation"},
            {"name": "max_retries", "type": "int", "value":1, "help": "When something fails, retry n times before stopping"},
            {"name": "build_image_assets", "type": "bool", "value":False, "help": "Build image assets"},
            {"name": "build_sound_assets", "type": "bool", "value":False, "help": "Build sound assets"},
            {"name": "verbose", "type": "bool", "value":False, "help": "If true, you will see all details in the message"},
            
            {"name": "license", "type": "str", "value":"Apache 2.0", "help": "The license"},
        ])
        personality_config_vals = BaseConfig.from_template(personality_config_template)
        personality_config = TypedConfig(personality_config_template, personality_config_vals)
        
        super().__init__(
            personality,
            personality_config,
            states_list=[
                {
                    "name": "idle",
                    "commands": {
                        "help": self.help,
                    },
                    "default": None
                },
            ],
            callback=callback
        )
        self.workflow_steps = []
        self.project_details = None
        self.project_structure = {}
        self.current_response = ""

    def mounted(self):
        self.step_start("Personality mounted successfully.")

    def selected(self):
        self.step_start("Personality selected.")

    def install(self):
        self.step_start("Installing necessary dependencies.")
        self.step_end("Dependencies installed.")

    def help(self, prompt="", full_context=""):
        help_text = (
            "This personality helps you build Python projects step by step. "
            "Provide an instruction to get started."
        )
        self.set_message_content(help_text)

    def run_workflow(self, context_details: Dict[str, Any] = None, client:Client = None, callback: Callable = None):

        prompt = context_details.prompt
        previous_discussion_text = context_details.discussion_messages
        
        self.callback = callback
        self.step_start("Starting project build workflow.")

        self.current_response = ""
        # Check if work_folder is set
        work_folder = self.personality_config.work_folder
        if not work_folder or work_folder == "":
            self.set_message_content("<b>Work folder not set. Please set the work_folder in the personality configuration.</b>")
            return

        self.work_folder = Path(work_folder)
        self.work_folder.mkdir(parents=True, exist_ok=True)
        self.project_details_file = self.work_folder/"project_cfg.json"
        if self.project_details_file.exists():
            with open(self.project_details_file,"r") as f:
                self.project_details = json.load(f)
        else:
            self.project_details = None


        output_type =  self.multichoice_question("select the most approproate description of the user prompt",[
            "The user is asking to start building a new project",
            "The user is asking to do a modification or update to the project",
            "The user is asking to view information about the project",
        ],prompt)
        
        if output_type==0: 
            # Parse the instruction
            self.project_details = self.plan_project(prompt)
            with open(self.project_details_file, "w") as f:
                json.dump(self.project_details, f, indent=2)
                
            self.terminal = CommandExecutor(self.work_folder)
            if not self.project_details:
                self.step_start("Failed to parse the instruction. Please try again with a clearer instruction.")
                return
            self.add_chunk_to_message_content("\n")

            # Execute the project tasks
            self.execute_project()
        elif output_type == 1:
            # Parse the instruction
            if not self.project_details:
                self.add_chunk_to_message_content("Warning! No project details file found.\\nBuilding a new file from the content ...")
                folder_structure = self.describe_folder_structure(self.work_folder)

                self.project_details = self.build_project_details(folder_structure)

            self.project_details = self.update_project(prompt)
            self.terminal = CommandExecutor(self.work_folder)
            if not self.project_details:
                self.step_start("Failed to parse the instruction. Please try again with a clearer instruction.")
                return
            self.add_chunk_to_message_content("\n")

            # Execute the project tasks
            self.execute_project()
        self.terminal.close()

    def plan_project(self, prompt: str) -> Dict[str, Any]:
        task_types = "execute_command, create_file, run_application"
        if self.personality.app.tti and self.personality_config.build_image_assets:
            image_generator = (
                "   {\n"
                '       "task_type":"generate_image", generates an image asset for the project\n'
                '       "file_name":"relative path to the file to be generated"\n'
                '       "generation_prompt":"A prompt for generating the image"\n'
                "   },\n"
            )
            task_types += ", generate_image"
        else:
            image_generator ="Do not use any image assets in the code"

        if self.personality.app.tts and self.personality_config.build_sound_assets:
            sound_generator = (
                "   {\n"
                '       "task_type":"generate_sound", generates a sound or music asset for the project\n'
                '       "file_name":"relative path to the file to be generated"\n'
                '       "generation_prompt":"A prompt for generating the sound or music"\n'
                "   },\n"
            )
            task_types += ", generate_sound"
        else:
            sound_generator ="Do not use any sound or music assets in the code\n"

        formatted_prompt = (
            "Please provide a JSON representation of the steps to fulfill the following instruction: "
            f"{prompt}.\n"
            "Json structure:\n"
            "```json\n"
            "{\n"
            '"user_prompt":"Rewrite the user request here use multilines",\n'
            '"project_title":"A string representing the project title",\n'
            '"project_type":"A string representing the project type",\n'
            f'"project_author":"{self.config.user_name if self.config.user_name and self.config.user_name!="user" else "Lollms Project Builder"}",\n'
            '"project_description":"A string representing the project type",\n'
            f'"platform":"{sys.platform}",\n'
            '"structure":[,\n'
            '   "folder1":[\n'
            '       "file1":"description",\n'
            '       "file2":"description",\n'
            '       "subfolder1":[\n'
            '       ...\n'
            '       ],\n'
            '       "file1":"description",\n'
            '   ...\n'
            '   ]'
            '],\n'
            '"tasks":"[ A list of tasks to do in order to fulfill the user request\n'
            "   {\n"
            '       "task_type":"execute_command", This executes a console command\n'
            '       "command":"command to execute"\n'
            "   },\n"
            "   {\n"
            '       "task_type":"create_file", This creates a file at a specific path\n'
            '       "file_name":"relative path to the file",\n'
            '       "content_description": "Single line string. Write a description of the content and its structure in textual description. For code files, do not write any code, just the full signature of contructors, methods and variables with typing if needed. The objective is for this to be sufficient to build other files that use this file as import. So it is important to be specific",\n'
            "   },\n"
            "   {\n"
            '       "task_type":"run_application", This runs an application and returns back the output to check\n'
            '       "command":"the command to run the application"\n'
            "   },\n"+image_generator+sound_generator+""

            "]\n"
            "}\n"
            "```\n"
            "\n"    
            "Only the following task types are allowed: "+task_types+".\n"
            "Make sure to include the JSON delimiters and respect the formatting.\n"
            "The tasks are executed in a consistant shell. The folders can be changed using cd.\n"
            "Make sure you make a rigorous setup and plan documentation.\n"
        )
        if self.personality_config.verbose:
            self.print_prompt("Generating project structure", formatted_prompt)

        try_number = 0
        while(try_number<3):
            try_number+=1
            json_str = self.generate_code(formatted_prompt,callback=self.sink)
            if self.personality_config.verbose:
                self.print_prompt("Json generation",json_str)
            
            if json_str:
                try:
                    json_response = json.loads(json_str)
                    json_response["current_task_index"]=0
                    with open(self.work_folder/"project_cfg.json","w") as f:
                        json.dump(json_response,f,indent=2)

                    formatted_info = f'''
<div class="w-full mx-auto p-6 bg-white rounded-lg shadow-lg">
<div class="mb-6">
<h1 class="text-2xl font-bold text-gray-800 mb-4">📋 Project Information</h1>
<div class="border-b border-gray-300 mb-4"></div>

<div class="grid grid-cols-2 gap-4 mb-4">
    <div class="flex items-center">
        <span class="text-gray-600">🏷️ Title:</span>
        <span class="ml-2 font-medium">{json_response.get('project_title', 'N/A')}</span>
    </div>
    <div class="flex items-center">
        <span class="text-gray-600">📁 Type:</span>
        <span class="ml-2 font-medium">{json_response.get('project_type', 'N/A')}</span>
    </div>
    <div class="flex items-center">
        <span class="text-gray-600">👤 Author:</span>
        <span class="ml-2 font-medium">{json_response.get('project_author', 'N/A')}</span>
    </div>
    <div class="flex items-center">
        <span class="text-gray-600">💻 Platform:</span>
        <span class="ml-2 font-medium">{json_response.get('platform', 'N/A')}</span>
    </div>
</div>

<div class="mb-6">
    <h2 class="text-xl font-semibold text-gray-800 mb-2">📝 Description</h2>
    <p class="text-gray-700">{json_response.get('project_description', 'N/A')}</p>
</div>
<div class="mb-6">
    <h2 class="text-xl font-semibold text-gray-800 mb-2">📝 Structure</h2>
    <p class="text-gray-700">{json_response.get('structure', 'N/A')}</p>
</div>
<div>
    <h2 class="text-xl font-semibold text-gray-800 mb-4">📋 Tasks</h2>
    <div class="border-b border-gray-300 mb-4"></div>
    <div class="space-y-4">'''

                    # Add tasks
                    for idx, task in enumerate(json_response.get('tasks', []), 1):
                        formatted_info += f'''
<div class="bg-gray-50 p-4 rounded-lg">
    <h3 class="text-lg font-medium text-gray-800 mb-2">🔹 Task {idx}: {task.get("task_type","N/A")}</h3>
    <div class="pl-4">
        <h4 class="text-gray-700 font-medium mb-2">Parameters:</h4>
        <ul class="list-disc pl-6">'''
                        
                        for param_key, param_value in task.items():
                            if param_key != "task_type":
                                formatted_info += f'''
<li class="text-gray-600"><span class="font-medium">{param_key}:</span><textarea class="w-full" readonly>{param_value}</textarea></li>'''
                        
                        formatted_info += '''
        </ul>
    </div>
</div>
    '''
                    # Close all divs
                    formatted_info += '''
</div>
</div>
    '''

                    self.current_response  += formatted_info
                    self.set_message_html(self.current_response)
                    return json_response
                except Exception as ex:
                    trace_exception(ex)
                    ASCIIColors.error("Error decoding JSON response or extracting JSON part.")
            


    def read_doc_file(self, file_path, max_length=2048):
        """
        Reads the content of a documentation file
        
        Args:
            file_path (Path): Path to the documentation file
        
        Returns:
            str: Content of the file or error message
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Truncate content if too long
                if len(content) > max_length:
                    content = content[:max_length] + "...\n[Content truncated]"
                return content
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def describe_folder_structure(self, folder_path, indent="", collect_docs=True):
        """
        Recursively describes the folder structure and collects documentation files
        
        Args:
            folder_path (str): Path to the folder to analyze
            indent (str): Current indentation level for pretty printing
            collect_docs (bool): Whether to collect documentation files
        
        Returns:
            tuple: (structure description, list of documentation files found)
        """
        path = Path(folder_path)
        if not path.exists():
            return "Error: Specified path does not exist", []
        
        description = f"{indent}📁 {path.name}/\n"
        doc_files = []
        
        try:
            items = list(path.iterdir())
            folders = sorted([item for item in items if item.is_dir()])
            files = sorted([item for item in items if item.is_file()])
            
            # Process folders
            for folder in folders:
                sub_desc, sub_docs = self.describe_folder_structure(folder, indent + "    ", collect_docs)
                description += sub_desc
                doc_files.extend(sub_docs)
                
            # Process files
            for file in files:
                description += f"{indent}    📄 {file.name}\n"
                
                # Collect documentation files
                if collect_docs and file.suffix.lower() in ['.md', '.txt']:
                    doc_files.append({
                        'path': file,
                        'name': file.name,
                        'type': file.suffix.lower(),
                        'content': self.read_doc_file(file)
                    })
                
        except PermissionError:
            description += f"{indent}    ⚠️ Permission denied\n"
        except Exception as e:
            description += f"{indent}    ⚠️ Error: {str(e)}\n"
            
        return description, doc_files
    
    def build_project_details(self, folder_structure, doc_files):
        formatted_prompt = (
            "Please provide a JSON representation of the project. "
            "Folder structure:\n"
            f"{folder_structure}.\n"
            "Doc files:\n"
            f"{doc_files}.\n"
            "The project json representation structure looks like this:"
            "```json\n"
            "{\n"
            '"project_title":"A string representing the project title",\n'
            '"project_type":"A string representing the project type",\n'
            f'"project_author":"{self.config.user_name if self.config.user_name and self.config.user_name!="user" else "Lollms Project Builder"}",\n'
            '"project_description":"A string representing the project type",\n'
            f'"platform":"{sys.platform}",\n'
            f'"structure":"a simple structure of the project",\n'
            "```\n"
            "Make sure to include the JSON delimiters and respect the formatting.\n"
            "The tasks are executed in a consistant shell. The folders can be changed using cd.\n"
            "Make sure you make a rigorous setup and plan documentation.\n"
        )
        if self.personality_config.verbose:
            self.print_prompt("Generating project structure", formatted_prompt)

        json_str = self.generate_code(formatted_prompt,callback=self.sink)
        
        if json_str:
            try:
                json_response = json.loads(json_str)
                json_response["current_task_index"]=0
                with open(self.work_folder/"project_cfg.json","w") as f:
                    json.dump(json_response,f,indent=2)

                formatted_info = f'''
<div class="w-full mx-auto p-6 bg-white rounded-lg shadow-lg">
<div class="mb-6">
<h1 class="text-2xl font-bold text-gray-800 mb-4">📋 Project Information</h1>
<div class="border-b border-gray-300 mb-4"></div>

<div class="grid grid-cols-2 gap-4 mb-4">
    <div class="flex items-center">
        <span class="text-gray-600">🏷️ Title:</span>
        <span class="ml-2 font-medium">{json_response.get('project_title', 'N/A')}</span>
    </div>
    <div class="flex items-center">
        <span class="text-gray-600">📁 Type:</span>
        <span class="ml-2 font-medium">{json_response.get('project_type', 'N/A')}</span>
    </div>
    <div class="flex items-center">
        <span class="text-gray-600">👤 Author:</span>
        <span class="ml-2 font-medium">{json_response.get('project_author', 'N/A')}</span>
    </div>
    <div class="flex items-center">
        <span class="text-gray-600">💻 Platform:</span>
        <span class="ml-2 font-medium">{json_response.get('platform', 'N/A')}</span>
    </div>
</div>

<div class="mb-6">
    <h2 class="text-xl font-semibold text-gray-800 mb-2">📝 Description</h2>
    <p class="text-gray-700">{json_response.get('project_description', 'N/A')}</p>
</div>

<div>
    <h2 class="text-xl font-semibold text-gray-800 mb-4">📋 Tasks</h2>
    <div class="border-b border-gray-300 mb-4"></div>
    <div class="space-y-4">
</div>
</div>
'''
                self.current_response  += formatted_info
                self.set_message_html(self.current_response)
                return json_response
            except Exception as ex:
                trace_exception(ex)
                ASCIIColors.error("Error decoding JSON response or extracting JSON part.")
                return None
        
        return None        


    def update_project(self, prompt: str) -> Dict[str, Any]:
        task_types = "execute_command, create_file, run_application"
        if self.personality.app.tti and self.personality_config.build_image_assets:
            image_generator = (
                "   {\n"
                '       "task_type":"generate_image", generates an image asset for the project\n'
                '       "file_name":"relative path to the file to be generated"\n'
                '       "generation_prompt":"A prompt for generating the image"\n'
                "   },\n"
            )
            task_types += ", generate_image"
        else:
            image_generator ="Do not use any image assets in the code"

        if self.personality.app.tts and self.personality_config.build_sound_assets:
            sound_generator = (
                "   {\n"
                '       "task_type":"generate_sound", generates a sound or music asset for the project\n'
                '       "file_name":"relative path to the file to be generated"\n'
                '       "generation_prompt":"A prompt for generating the sound or music"\n'
                "   },\n"
            )
            task_types += ", generate_sound"
        else:
            sound_generator ="Do not use any sound or music assets in the code\n"

        formatted_prompt = (
            "Project details:\n"
            f"{self.project_details}\n"
            "Please provide a JSON representation of the steps to fulfill the following instruction: "
            f"{prompt}.\n"
            "Json structure:\n"
            "```json\n"
            "{\n"
            '"tasks":"[ A list of tasks to do in order to fulfill the user request\n'
            "   {\n"
            '       "task_type":"execute_command", This executes a console command\n'
            '       "command":"command to execute"\n'
            "   },\n"
            "   {\n"
            '       "task_type":"edit_file", This shows the file content and prepared it for editing\n'
            '       "file_name":"relative path to the file",\n'
            "   },\n"
            "   {\n"
            '       "task_type":"create_file", This creates a new file at a specific path\n'
            '       "file_name":"relative path to the file",\n'
            '       "content_description":"Write a description of the content and its structure in textual description. Do not write any code, just a description. Here you need to write the structure of the file content. If this is a code list very detailed funtion signature, classes, variables with their types in a packed but detailed manner.",\n'
            "   },\n"
            "   {\n"
            '       "task_type":"run_application", This runs an application and returns back the output to check\n'
            '       "command":"the command to run the application"\n'
            "   },\n"+image_generator+sound_generator+""

            "]\n"
            "}\n"
            "```\n"
            "Only the following task types are allowed: "+task_types+".\n"
            "Make sure to include the JSON delimiters and respect the formatting.\n"
            "The tasks are executed in a consistant shell. The folders can be changed using cd.\n"
            "Make sure you make a rigorous setup and plan documentation.\n"
        )
        if self.personality_config.verbose:
            self.print_prompt("Generating project structure", formatted_prompt)

        json_str = self.generate_code(formatted_prompt,callback=self.sink)
        
        if json_str:
            try:
                json_response = json.loads(json_str)
                json_response["current_task_index"]=0
                with open(self.work_folder/"project_cfg.json","w") as f:
                    json.dump(json_response,f,indent=2)

                formatted_info = f'''
<div class="w-full mx-auto p-6 bg-white rounded-lg shadow-lg">
<div class="mb-6">
<h1 class="text-2xl font-bold text-gray-800 mb-4">📋 Project Information</h1>
<div class="border-b border-gray-300 mb-4"></div>

<div class="grid grid-cols-2 gap-4 mb-4">
    <div class="flex items-center">
        <span class="text-gray-600">🏷️ Title:</span>
        <span class="ml-2 font-medium">{json_response.get('project_title', 'N/A')}</span>
    </div>
    <div class="flex items-center">
        <span class="text-gray-600">📁 Type:</span>
        <span class="ml-2 font-medium">{json_response.get('project_type', 'N/A')}</span>
    </div>
    <div class="flex items-center">
        <span class="text-gray-600">👤 Author:</span>
        <span class="ml-2 font-medium">{json_response.get('project_author', 'N/A')}</span>
    </div>
    <div class="flex items-center">
        <span class="text-gray-600">💻 Platform:</span>
        <span class="ml-2 font-medium">{json_response.get('platform', 'N/A')}</span>
    </div>
</div>

<div class="mb-6">
    <h2 class="text-xl font-semibold text-gray-800 mb-2">📝 Description</h2>
    <p class="text-gray-700">{json_response.get('project_description', 'N/A')}</p>
</div>

<div>
    <h2 class="text-xl font-semibold text-gray-800 mb-4">📋 Tasks</h2>
    <div class="border-b border-gray-300 mb-4"></div>
    <div class="space-y-4">'''

                # Add tasks
                for idx, task in enumerate(json_response.get('tasks', []), 1):
                    formatted_info += f'''
<div class="bg-gray-50 p-4 rounded-lg">
    <h3 class="text-lg font-medium text-gray-800 mb-2">🔹 Task {idx}: {task.get("task_type","N/A")}</h3>
    <div class="pl-4">
        <h4 class="text-gray-700 font-medium mb-2">Parameters:</h4>
        <ul class="list-disc pl-6">'''
                    
                    for param_key, param_value in task.items():
                        if param_key != "task_type":
                            formatted_info += f'''
<li class="text-gray-600"><span class="font-medium">{param_key}:</span><textarea class="w-full" readonly>{param_value}</textarea></li>'''
                    
                    formatted_info += '''
        </ul>
    </div>
</div>
'''
                # Close all divs
                formatted_info += '''
</div>
</div>
'''

                self.current_response  += formatted_info
                self.set_message_html(self.current_response)
                return json_response
            except Exception as ex:
                trace_exception(ex)
                ASCIIColors.error("Error decoding JSON response or extracting JSON part.")
                return None
        
        return None





    def generate_file_content(self, file_name: str, project_context: Dict[str, Any], extra_information:str=None) -> str:
        prompt = "\n".join(
            [
            f"Generate the content for the file '{file_name}' in the context of the following project structure:",
            f"{json.dumps(project_context, indent=2)}",
            "If the file is a code, make sure that it is compatible with the existing project structure and functions.",
            f"If this is a README.md file, then Make sure you describe the project and make detailed documentation. Use badges and licence {self.personality_config.license}.",
            (extra_information if extra_information else "")              
            ]
        )+"\n"  
        return self.generate_code(prompt, callback=self.sink)

    def extract_functions(self, code: str) -> Dict[str, Any]:
        prompt = (
            "Extract the functions, classes, and methods from the following code and return them as a JSON object. "
            "Include the function/class/method names, parameters, and brief descriptions.\n\n"
            f"Code:\n{code}\n\n"
            "Return the JSON in the following format:\n"
            "```json\n"
            "{\n"
            "  \"functions\": [\n"
            "    {\"name\": \"function_name\", \"parameters\": [\"param1\", \"param2\"], \"description\": \"Brief description\"}\n"
            "  ],\n"
            "  \"classes\": [\n"
            "    {\n"
            "      \"name\": \"ClassName\",\n"
            "      \"methods\": [\n"
            "        {\"name\": \"method_name\", \"parameters\": [\"param1\", \"param2\"], \"description\": \"Brief description\"}\n"
            "      ]\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "```\n"
        )
        json_str = self.generate_code(prompt)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {}




    # **************************** Cre ate a file ************************************************************
    def create_file(self, context_memory, task):
            file_name = task.get("file_name")
            if file_name:
                self.step_start(f"Generating content for {file_name}")
                code = self.generate_file_content(file_name, context_memory)
                current_dir = self.terminal.get_current_directory()
                file_path:Path = Path(current_dir) / file_name
                file_path.parent.mkdir(parents=True, exist_ok=True)
                context_memory["files_information"][file_name]= self.generate(f"list all elements anf functions of this file in a textual simplified manner:\n{code}", callback=self.sink)
                
                try:
                    self.terminal.create_file(file_path, code)
                    self.current_response  += f'''
<div class="bg-green-50 p-4 rounded-lg">
    <h3 class="text-lg font-medium text-gray-800 mb-2">🔹 Task: {task.get("task_type","N/A")}</h3>
    <div class="pl-4">
        <h4 class="text-gray-700 font-medium mb-2">Task completed successfully:</h4>
        <ul class="list-disc pl-6">
                    Content of file: {file_path} written successfuly
        </ul>
    </div>
</div>
'''
                    self.set_message_html(self.current_response)
                    return True
                except Exception as e:
                    self.current_response  += f'''
<div class="bg-red-50 p-4 rounded-lg">
    <h3 class="text-lg font-medium text-gray-800 mb-2">🔹 Task: {task.get("task_type","N/A")}</h3>
    <div class="pl-4">
        <h4 class="text-gray-700 font-medium mb-2">Task completed successfully:</h4>
        <ul class="list-disc pl-6">
                    Error writing file: {str(e)}
        </ul>
    </div>
</div>
'''
                    self.set_message_html(self.current_response)
                    return False

    # **************************** edit a file ************************************************************
    def edit_file(self, context_memory, task, error_info):
            file_name = task.get("file_name")
            if file_name:
                self.step_start(f"Editing {file_name}")
                with open(self.work_folder/file_name,"r") as f:
                    code = f.read()
                data= f"Previous_code:{code}\nError_info:"+error_info+"\n"
                code = self.generate_file_content(context_memory, file_name, data)
                current_dir = self.terminal.get_current_directory()
                file_path:Path = Path(current_dir) / file_name
                file_path.parent.mkdir(parents=True, exist_ok=True)
                # context_memory["files_information"][file_name]= self.generate(f"list all elements of this file in a textual simplified manner:\n{code}", callback=self.sink)
                
                try:
                    self.terminal.create_file(file_path, code)
                    self.current_response  += f'''
<div class="bg-green-50 p-4 rounded-lg">
    <h3 class="text-lg font-medium text-gray-800 mb-2">🔹 Task: {task.get("task_type","N/A")}</h3>
    <div class="pl-4">
        <h4 class="text-gray-700 font-medium mb-2">Task completed successfully:</h4>
        <ul class="list-disc pl-6">
                    Content of file: {file_path} written successfuly
        </ul>
    </div>
</div>
'''
                    self.set_message_html(self.current_response)
                    return True
                except Exception as e:
                    self.current_response  += f'''
<div class="bg-red-50 p-4 rounded-lg">
    <h3 class="text-lg font-medium text-gray-800 mb-2">🔹 Task: {task.get("task_type","N/A")}</h3>
    <div class="pl-4">
        <h4 class="text-gray-700 font-medium mb-2">Task completed successfully:</h4>
        <ul class="list-disc pl-6">
                    Error writing file: {str(e)}
        </ul>
    </div>
</div>
'''
                    self.set_message_html(self.current_response)
                    return False


    # **************************** Executes a command ************************************************************
    def exec_command(self, context_memory, task):
            command = task.get("command")
            if command:
                self.step_start(f"Executing command: {command}")
                try:
                    result = self.terminal.execute_command(command)
                    
                    # Show output in markdown format
                    output_html = f"""
<b>Command:</b>{command}<br>
<b>Output:</b><br>
<textarea class="w-full">
{result["stdout"] if result and result["stdout"]!="" else "success"}
</textarea>
"""

                    self.current_response  += output_html
                    self.set_message_html(self.current_response)
                    
                    # Ask AI to analyze the output
                    analysis_prompt = f"""
Analyze the following command execution results and determine next steps:
Command: {command}
Output: {result["stdout"] if result and result["stdout"]!="" else "success"}
Error output: {result["stderr"] if result["stderr"] and result["stderr"]!="" else "no errors detected"}

Respond with a JSON containing:
1. status: "success" or "error"
2. message: Description of what happened
Example:
```json
{{
    "status": "success",
    "message": "Command executed successfully",
}}
```
"""
                    
                    analysis_response = self.generate_code(analysis_prompt, callback=self.sink)
                    try:
                        analysis = json.loads(analysis_response)
                        if analysis.get("status") == "success":
                            self.current_response  += f'''
<div class="bg-green-50 p-4 rounded-lg">
    <h3 class="text-lg font-medium text-gray-800 mb-2">🔹 Task: {task.get("task_type","N/A")}</h3>
    <div class="pl-4">
        <h4 class="text-gray-700 font-medium mb-2">Task completed successfully:</h4>
        <ul class="list-disc pl-6">
                    {analysis.get("message", "")}
        </ul>
    </div>
</div>
'''
                            self.set_message_html(self.current_response)

                            self.step_end(f"Executing command: {command}")
                            return True
                        else:
                            self.step(f"Task failed: {analysis.get('message', 'Unknown error')}")
                            self.current_response  += f'''
<div class="bg-red-50 p-4 rounded-lg">
    <h3 class="text-lg font-medium text-gray-800 mb-2">🔹 Task: {task.get("task_type","N/A")}</h3>
    <div class="pl-4">
        <h4 class="text-gray-700 font-medium mb-2">Task failed:</h4>
        <ul class="list-disc pl-6">
                    {analysis.get("message", 'Unknown error')}
        </ul>
    </div>
</div>
'''
                            self.set_message_html(self.current_response)          
                            self.step_end(f"Executing command: {command}", False)
                            return False
                    except json.JSONDecodeError:
                        self.step_start("Failed to parse AI analysis response")
                        return False
                    
                except subprocess.CalledProcessError as e:
                    error_html = f"""
<b>Command:</b>{command}<br>
<b>Error:</b><br>
<textarea class="w-full" style="background-color: #fdf2f2; padding: 16px; border-radius: 6px; font-family: monospace; color: #cc0000;">
{e.stderr}
</textarea>
"""

                    
                    self.current_response  += error_html
                    self.set_message_html(self.current_response)                         
                    return False

    def run_application(self, context_memory, task):
            command = task.get("command")
            if command:
                self.step_start(f"Running application with command: {command}")
                try:
                    # For Windows
                    result = self.terminal.execute_command(command)
                    # Show output in markdown format
                    output_html = f"""
<b>Application:</b>{command}<br>
<b>Output:</b><br>
<textarea class="w-full">
{result}
</textarea>
"""

                    self.current_response  += output_html
                    self.set_message_html(self.current_response)
                    
                    # Ask AI to analyze the application output
                    analysis_prompt = f"""
Analyze the following application execution results:
Command: {command}
Output: {result["stdout"] if result["stdout"] and result["stdout"]!="" else "success"}
Error output: {result["stderr"] if result["stderr"] and result["stderr"]!="" else "no errors detected"}

Respond with a JSON containing:
1. status: "success" or "error"
2. message: Description of application behavior
3. todo: None if success, but if error, then write a list of tasks to do to fix the code before retrying to executre the code. You may need to update multiple files.
[
{{
"task_type":"edit_file", This edits a file at a specific path
"file_name":"relative path to the file",
}},
...
]

"""
                    self.add_chunk_to_message_content("\n")
                    analysis_response = self.generate_code(analysis_prompt, callback=self.sink)
                    try:
                        analysis = json.loads(analysis_response)
                        if analysis.get("status") == "success":
                            self.current_response  += f'''
<div class="bg-green-50 p-4 rounded-lg">
    <h3 class="text-lg font-medium text-gray-800 mb-2">🔹 Task: {task.get("task_type","N/A")}</h3>
    <div class="pl-4">
        <h4 class="text-gray-700 font-medium mb-2">Task completed successfully:</h4>
        <ul class="list-disc pl-6">
        {analysis.get("message", "")}
        </ul>
    </div>
</div>
'''
                            self.set_message_html(self.current_response)               
                            return True
                        else:
                            self.step_end(f"Running application with command: {command}", False)
                            self.step(f"Application run failed: {analysis.get('message', 'Unknown error')}")
                            self.current_response  += f'''
<div class="bg-red-50 p-4 rounded-lg">
    <h3 class="text-lg font-medium text-gray-800 mb-2">🔹 Task: {task.get("task_type","N/A")}</h3>
    <div class="pl-4">
        <h4 class="text-gray-700 font-medium mb-2">Task completed successfully:</h4>
        <ul class="list-disc pl-6">
        Application run failed: {analysis.get('message', 'Unknown error')}
        Suggested operations:
            {analysis.get("todo")}
        </ul>
    </div>
</div>
'''
                            self.set_message_html(self.current_response)   
                            for todo_entry in analysis.get("todo"):
                                if todo_entry["task_type"]=="edit_file":
                                    self.edit_file(context_memory, todo_entry, analysis.get('message', 'Unknown error'))
                            return False
                    except json.JSONDecodeError:
                        self.step_start("Failed to parse AI analysis response")
                        return False
                    
                except subprocess.CalledProcessError as e:
                    error_html = f"""
Command: {command}
Error:
<textarea style="background-color: #fdf2f2; padding: 16px; border-radius: 6px; font-family: monospace; color: #cc0000;">
{e.stderr}
</textarea>
"""
                    self.current_response  += error_html
                    self.set_message_html(self.current_response)
                    return False

    def execute_task(self, context_memory, task: Dict[str, Any]) -> bool:
        task_type = task.get("task_type")
        if task_type == "execute_command":
            return self.exec_command(context_memory, task)

        elif task_type == "create_file":
            return self.create_file(context_memory, task)

        elif task_type == "run_application":
            return self.run_application(context_memory, task)

        elif task_type == "finished":
            self.step_start("Workflow completed successfully.")
            return True

        else:
            self.step_start(f"Unknown task type: {task_type}")
            return False


    def execute_project(self):
        if not self.project_details:
            self.step_start("No project details available. Please parse the instruction first.")
            return

        self.step_start("Executing project tasks...")

        for task_index, task in enumerate(self.project_details.get("tasks", [])):
            n=0
            while n<self.personality_config.max_retries:
                success = self.execute_task(self.project_details, task)
                task["status"]="success" if success else "failure"
                if success:
                    self.project_details["current_task_index"]=task_index
                    with open(self.work_folder/"project_cfg.json","w") as f:
                        json.dump(self.project_details,f,indent=2)
                    n=self.personality_config.max_retries
                else:
                    self.add_chunk_to_message_content(f"Failed to execute task: {task['task_type']}")
                    self.step(f"Failed to execute task: {task['task_type']}")
                    self.step(f"Thinking...")
                    n += 1

        self.step_start("Project execution completed successfully.")
        
