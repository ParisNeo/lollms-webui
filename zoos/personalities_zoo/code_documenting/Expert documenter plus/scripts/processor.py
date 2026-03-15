import subprocess
from pathlib import Path
from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate, InstallOption
from lollms.types import MSG_OPERATION_TYPE
from typing import Any
from lollms.personality import APScript, AIPersonality
from lollms.prompting import LollmsContextDetails
import re
import importlib
import requests
from tqdm import tqdm
import shutil
from lollms.types import GenerationPresets
from typing import Callable, Any
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
        self.word_callback = None
        personality_config_template = ConfigTemplate(
            [
                {"name":"layout_max_size","type":"int","value":512, "min":10, "max":personality.config["ctx_size"]},                
                {"name":"is_debug","type":"bool","value":False, "help":"Activates debug mode where all prompts are shown in the console"},                                
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
                            callback=callback
                            
                        )
        self.previous_versions = []
        
    def install(self):
        super().install()
        # Get the current directory
        root_dir = self.personality.lollms_paths.personal_path
        # We put this in the shared folder in order as this can be used by other personalities.
        shared_folder = root_dir/"shared"

        requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Step 2: Install dependencies using pip from requirements.txt
        subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])            
        ASCIIColors.success("Installed successfully")

    def convert_string_to_sections(self, string):
        lines = string.split('\n')  # Split the string into lines
        sections = []
        current_section = None
        for line in lines:
            if line.startswith('## '):  # Detect section
                section_title = line.replace('## ', '')
                current_section = {'title': section_title, 'subsections': [], 'content':''}
                sections.append(current_section)
            elif line.startswith('### '):  # Detect subsection
                if current_section is not None:
                    subsection_title = line.replace('### ', '')
                    current_section['subsections'].append({'title':subsection_title, 'content':''})
        return sections


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

        output_path = self.personality.lollms_paths.personal_outputs_path
        
        # First we create the yaml file
        # ----------------------------------------------------------------
        self.step_start("Building the title...", callback)
        gen_prompt = f"""Act as document title builder assistant. Infer a document title out of the project information.
project_information:
{prompt}
{self.config.start_header_id_template}User: Using the project information, Create a title for the document.
{self.config.start_header_id_template}Assistant:
Here is a suitable title for this project:"""
        if self.personality_config.is_debug:
            ASCIIColors.info(gen_prompt)

        title = self.generate(gen_prompt,512,**GenerationPresets.deterministic_preset()).strip().split("\n")[0]
        if title.startswith('"'):
            title = title[1:]
        self.step_end("Building the title...", callback)
        ASCIIColors.yellow(f"title:{title}")
        # ----------------------------------------------------------------

        # ----------------------------------------------------------------
        self.step_start("Building the table of contents...", callback)
        gen_prompt = f"""Act as a sophisticated document table of contents builder assistant, capable of breaking down complex projects into subtopics to generate an organized and logical structure. Leverage multiple expert perspectives to evaluate the relevance and coherence of each proposed section, ensuring that they maintain a natural flow. Construct a comprehensive table of contents by stitching together the strongest sections and providing explanatory details where necessary. Synthesize key insights into a final structure, written in a clear and concise manner suitable for an experienced technical writer at the doctoral level.
Do not write the sections contents. All you are asked to do is to make the table of contents which is the title, the sections and the subsections using # for main titles, ## for sections, and ### for subsections.
The table of content should be formatted in markdown format with # for main title, ## for sections and ### for subsections.
project information:
{prompt}
@!>User: Using the project information, Let's build a table of contents for our documentation of this project.
@!>Assistant:
Here is the table of contents in markdown format:
# {title}                                                  
## Introduction"""
        if self.personality_config.is_debug:
            ASCIIColors.info(gen_prompt)
        layout = "## Introduction\n"+self.generate(gen_prompt,512,**GenerationPresets.deterministic_preset())
        self.step_end("Building the table of contents...", callback)
        ASCIIColors.yellow(f"structure:\n{layout}")
        sections = self.convert_string_to_sections(layout)
        # ----------------------------------------------------------------
        
        
        
        document_text=f"# {title}\n"        
        
        
        
        for i,section in enumerate(sections):
            # ----------------------------------------------------------------
            self.step_start(f"Building section {section['title']}...", callback)
            if len(section['subsections'])>0:
                document_text += f"## {section['title']}\n"
                for subsection in section['subsections']:
                    gen_prompt = f"""Act as a sophisticated document section filler assistant, capable of filling in the next section of a document by breaking down complex project information into smaller components. Leverage multiple expert perspectives to generate intermediate thoughts and evaluate their relevance and logical flow within the context of the document. Construct a chain of reasoning, stitching together the strongest thoughts and providing explanatory details. Synthesize key insights and inferences into coherent content for the next section of the document, written in a style consistent with an experienced tech writer at the doctoral level.
project information:
{prompt}
{self.config.start_header_id_template}User: Given the project information, leverage your sophisticated AI capabilities to break down complex data into smaller components. Draw upon multiple expert perspectives to generate intermediate thoughts and evaluate their relevance within the context of the section's content. Establish a logical flow by connecting these strongest thoughts and providing necessary explanatory details. In doing so, populate the content of the section with coherent, insightful information written in a style consistent with an experienced tech writer at the doctoral level. {section['title']}. To ensure clarity and coherence, avoid repeating information previously stated in the text. Focus on generating content that is both novel and relevant to the current section. By synthesizing new insights and perspectives while maintaining logical flow, you'll provide valuable contributions to the overall document without unnecessary redundancy.
{self.config.start_header_id_template}previous chunk of text preview:
{document_text[-1000:]}
{self.config.start_header_id_template}Assistant:
Here is the subsection content:
### {subsection['title']}"""
                    if self.personality_config.is_debug:
                        ASCIIColors.info(gen_prompt)
                    
                    subsection["content"] = self.generate(gen_prompt,1024,**GenerationPresets.deterministic_preset()).strip()
                    document_text += f"### {subsection['title']}\n"
                    document_text += f"{subsection['content']}\n"
            else:
                gen_prompt = f"""Act as a sophisticated document section filler assistant, capable of filling in the next section of a document by breaking down complex project information into smaller components. Leverage multiple expert perspectives to generate intermediate thoughts and evaluate their relevance and logical flow within the context of the document. Construct a chain of reasoning, stitching together the strongest thoughts and providing explanatory details. Synthesize key insights and inferences into coherent content for the next section of the document, written in a style consistent with an experienced tech writer at the doctoral level.
project information:
{prompt}
{self.config.start_header_id_template}User: Given the project information, leverage your sophisticated AI capabilities to break down complex data into smaller components. Draw upon multiple expert perspectives to generate intermediate thoughts and evaluate their relevance within the context of the section's content. Establish a logical flow by connecting these strongest thoughts and providing necessary explanatory details. In doing so, populate the content of the section with coherent, insightful information written in a style consistent with an experienced tech writer at the doctoral level. {section['title']}. To ensure clarity and coherence, avoid repeating information previously stated in the text. Focus on generating content that is both novel and relevant to the current section. By synthesizing new insights and perspectives while maintaining logical flow, you'll provide valuable contributions to the overall document without unnecessary redundancy.
{self.config.start_header_id_template}previous chunk of text preview:
{document_text[-500:]}
{self.config.start_header_id_template}Assistant:
Here is the section content:
## {section['title']}"""
                if self.personality_config.is_debug:
                    ASCIIColors.info(gen_prompt)
                
                section["content"] = self.generate(gen_prompt,1024,**GenerationPresets.deterministic_preset()).strip()
                document_text += f"## {section['title']}\n"
                document_text += f"{section['content']}\n"

            self.step_end(f"Building section {section['title']}...", callback)
            ASCIIColors.yellow(f"{section}\n")
            # ----------------------------------------------------------------
        
        output = f"```markdown\n"   
        output += document_text
        output += "\n```\n"
        output += "Now we can update some of the sections using the commands.\nYou can use the command update_section followed by the section name to add information about the section"
        
        self.previous_versions.append(output)
        if callback:
            self.set_message_content(output, callback)
        
        self.current_document = sections
        
        if callback:
            self.json(sections, callback)
        
        
        return output


