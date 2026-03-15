from cProfile import label
from email.mime import image
from datetime import datetime
import subprocess
from pathlib import Path
from xml.etree.ElementTree import Comment
from lollms.helpers import ASCIIColors, trace_exception
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate, InstallOption
from lollms.types import MSG_OPERATION_TYPE
from lollms.personality import APScript, AIPersonality
from lollms.utilities import PromptReshaper, git_pull
import re
import importlib
import sys
from typing import Callable, Any
from lollms.prompting import LollmsContextDetails
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
        # Get the current directory
        root_dir = personality.lollms_paths.personal_path
        # We put this in the shared folder in order as this can be used by other personalities.

        self.diagramAI_folder = root_dir / "outputs/DiagramAI/"
        self.file_name = ''
        self.callback = None

        
        #self.callback = callback

        personality_config_template = ConfigTemplate(
            [
                {"name":"continuous_discussion","type":"bool","value":True,"help":"If true then previous prompts and infos are taken into acount to generate the next image"},
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
                            ],
                            callback=callback
                        )
        if not self.verify_graphviz():
            self.install()

    def install(self):
        super().install()
        requirements_file = self.personality.personality_package_path / "requirements.txt"
        
        try:
            self.personality.ShowBlockingMessage("Installing dependencies...")
            
            # Install graphviz using pip
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "graphviz"], check=True)
            
            # Install other dependencies from requirements.txt
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "-r", str(requirements_file)], check=True)
            
            ASCIIColors.info("Loading graphviz and PIL")
            import graphviz
            from PIL import Image
            from io import BytesIO
            
            self.personality.HideBlockingMessage()
            ASCIIColors.success("Dependencies installed successfully.")
        
        except subprocess.CalledProcessError as e:
            self.personality.HideBlockingMessage()
            ASCIIColors.error(f"Error occurred while installing dependencies: {e}")
            raise
        except ImportError as e:
            self.personality.HideBlockingMessage()
            ASCIIColors.error(f"Error importing installed packages: {e}")
            ASCIIColors.warning("Please make sure graphviz is installed on your system and added to PATH.")
            raise
        except Exception as ex:
            self.personality.HideBlockingMessage()
            ASCIIColors.error(f"An unexpected error occurred: {ex}")
            trace_exception(ex)
            raise

    def gen_regex_image(self,call_graph_str,nb):
        import graphviz
        from PIL import Image
        from io import BytesIO
        import re

        # Use regex to find function call relations in the input string
        call_relations = re.findall(r'\b\w+\s*->\s*\w+\b', call_graph_str)

        # Create a new Graphviz graph
        graph = graphviz.Digraph(format='svg')
        graph.attr(label=f"Map N° : {nb}")

        # Add nodes and edges to the graph
        for graph_call in call_relations:
            from_node, to_node = map(str.strip, graph_call.split('->'))

            graph.node(from_node)
            graph.node(to_node)
            graph.edge(from_node, to_node)

        # Render the graph to a PNG image
        image_bytes = graph.pipe(format='svg')

        # Create an image from the bytes
        image = Image.open(BytesIO(image_bytes))
        self.file_name = datetime.now().strftime("%d_%m_%Y-%I_%M_%S")
        graph.render(self.diagramAI_folder / f'{self.file_name}_graph', cleanup=True)
        #graph.view()

        return image
    
    def verify_graphviz(self):
        try:
            import graphviz
            from PIL import Image
            from io import BytesIO
            # Create a new Graphviz graph
            graph = graphviz.Digraph(format='svg')

            # Split the input string into function calls
            calls = "a->b".split('->')

            # Add nodes and edges to the graph
            for i in range(len(calls) - 1):
                from_node = calls[i].strip()
                to_node = calls[i + 1].strip()

                graph.node(from_node)
                graph.node(to_node)
                graph.edge(from_node, to_node)

            # Render the graph to a PNG image
            image_bytes = graph.pipe(format='svg')
            return True
        except:
            return False

    def gen_image(self,call_graph_str):
        import graphviz
        from PIL import Image
        from io import BytesIO
        # Create a new Graphviz graph
        graph = graphviz.Digraph(format='svg',engine="dot")
        title = self.fast_gen(self.build_prompt(
            [
                f"{self.config.start_header_id_template}task:Make a very short title to this graph."
                f"{self.config.start_header_id_template}warning: Don't respond with extra information."
                f"{self.config.start_header_id_template}graph:",
                call_graph_str,
                f"{self.config.start_header_id_template}short title:"
            ]
        ))

        graph.attr(label=title)

        # Split the input string into function calls
        calls = call_graph_str.split('->')

        # Add nodes and edges to the graph
        for i in range(len(calls) - 1):
            from_node = calls[i].strip()
            to_node = calls[i + 1].strip()

            graph.node(from_node)
            graph.node(to_node)
            graph.edge(from_node, to_node)

        # Create an image from the bytes
        self.file_name = datetime.now().strftime("%d_%m_%Y-%I_%M_%S")
        graph.render(self.diagramAI_folder / f'{self.file_name}_graph', cleanup=True, format='svg',renderer="svg",formatter='core')

    def gen_graph(self,call_graph_str="",output ="", append_infos=False):
        # Create a new Graphviz graph
        files = []
        try:
            self.gen_image(call_graph_str)
            file = self.diagramAI_folder / f'{self.file_name}_graph.core.svg.svg'
            file = str(file).replace("\\","/")
            pth = file.split('/')
            idx = pth.index("outputs")
            pth = "/".join(pth[idx:])
            file_path = f"![](/{pth})\n"
            output += file_path
            ASCIIColors.yellow(f"Generated file in here : {file}")

        except Exception as ex:
            trace_exception(ex)
            self.personality.error("Couldn't generate the graph")
            #trace_exception(f"gen_graph Exception:{ex}") 
        

        return files, output

    def remove_image_links(self, markdown_text):
        # Regular expression pattern to match image links in Markdown
        image_link_pattern = r"!\[.*?\]\((.*?)\)"

        # Remove image links from the Markdown text
        text_without_image_links = re.sub(image_link_pattern, "", markdown_text)

        return text_without_image_links
    

           
            
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

        self.callback = callback
        """
        toto belong to tata and tata belong to titi , please make the Diagram

        Can you create a process flow diagram illustrating the key steps involved in developing a software application, from initial concept to deployment?
        """        
        # ====================================================================================
        self.step_start("Generating the Diagram")
        # 1 first ask the model to formulate a query
        
        prompt = self.build_prompt([
            f"{self.config.start_header_id_template}{self.config.system_message_template}:",
            "text2graph() is a function that converts text to graph in the following format.",
            'Create a diagram representing a series of sequential steps or relationships in the following format: "a -> b -> c".',
            'Each node (a, b, c, etc.) represents a distinct step or entity. The arrows "->" indicate the flow or relationship between them.',
            'The diagram should illustrate a clear sequence or connection between the elements.',
            '{self.config.start_header_id_template}text2graph(simple workdlow)=Start -> Process Data -> Analyze Results -> End{self.config.start_header_id_template}',
            'To get this task done No extra text must be generated , no explanation , no comment , no question , no echo , only the notation representig the scenario.',
            'The graph description should end with {self.config.start_header_id_template}',
            context_details.documentation,
            context_details.user_description,
            context_details.discussion_messages if self.personality_config.continuous_discussion else "",
            context_details.positive_boost,
            context_details.negative_boost,
            context_details.current_language,
            context_details.fun_mode,
            f"{self.config.start_header_id_template}text2graph({prompt})=",
        ],11)

        #ASCIIColors.yellow(prompt)

        gh_prompt = self.fast_gen(prompt,callback=self.sink)
        #print(gh_prompt)
        #ASCIIColors.yellow(gh_prompt)
        
        #------------------
        #gh_prompt = prompt

        files, out = self.gen_graph(gh_prompt)
        self.set_message_content(out.strip())
        self.step_end("Generating the Diagram")

        return ""

