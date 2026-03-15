from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.utilities import PackageManager
from lollms.personality import APScript, AIPersonality
from lollms.prompting import LollmsContextDetails
from lollms.types import MSG_OPERATION_TYPE
from lollms.internet import internet_search, scrape_and_save
from typing import Callable, Any

import subprocess
from pathlib import Path
from datetime import datetime
import json

if not PackageManager.check_package_installed("feedparser"):
    PackageManager.install_package("feedparser")

import feedparser
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
        # Example entry
        #       {"name":"make_scripted","type":"bool","value":False, "help":"Makes a scriptred AI that can perform operations using python script"},
        # Supported types:
        # str, int, float, bool, list
        # options can be added using : "options":["option1","option2"...]        
        personality_config_template = ConfigTemplate(
            [
                {"name":"output_folder","type":"str","value":"", "help":"The folder where all the files will be stored"},
                 
                {"name":"search_query","type":"text","value":"", "help":"Here you can put custom search query to be used. This automatically deactivates the rss, if you want the rss to work, then please empty this"},               
                {"name":"nb_search_pages","type":"int","value":5, "help":"the maximum number of pages to search"},
                {"name":"quick_search","type":"bool","value":False, "help":"Quick search returns only a brief summary of the webpage"},
                {"name":"summary_mode","type":"str","value":"RAG", "options":["RAG","Full Summary"], "help":"If Rag is used then the AI will search for useful data before summerizing, else it's gonna read the whole page before summary. The first is faster, but the second allows accessing the whole information without compromize."},                
                {"name":"zip_mode","type":"str","value":"hierarchical","options":["hierarchical","one_shot"], "help":"algorithm"},
                {"name":"zip_size","type":"int","value":1024, "help":"the maximum size of the summary in tokens"},
                {"name":"buttons_to_press","type":"str","value":"I agree,accept", "help":"Buttons to be pressed in the pages you want to load. A comma separated text that can be seen on the button to press. The buttons will be pressed sequencially"},
                {"name":"output_path","type":"str","value":"", "help":"The path to a folder where to put the summary file."},
                {"name":"contextual_zipping_text","type":"text","value":"", "help":"Here you can specify elements of the document that you want the AI to keep or to search for. This garantees that if found, those elements will not be filtered out which results in a more intelligent contextual based summary."},
                {"name":"keep_same_language","type":"bool","value":True, "help":"Force the algorithm to keep the same language and not translate the document to english"},
                {"name":"translate_to","type":"str","value":"", "help":"Force the algorithm to summarize the document in a specific language. If none is provided then it won't do any translation"},
                {"name":"preserve_document_title","type":"bool","value":False, "help":"Force the algorithm to preserve the document title as an important information"},
                {"name":"preserve_authors_name","type":"bool","value":False, "help":"Force the algorithm to preserve the authors names as an important information"},
                {"name":"preserve_results","type":"bool","value":True, "help":"Force the algorithm to preserve the document results the authors names as an important information"},
                {"name":"maximum_compression","type":"bool","value":False, "help":"Force the algorithm to compress the document as much as possible. Useful for what is this document talking about kind of summary"},
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
                                    "commands": { # list of commands
                                        "help":self.help,
                                        "start_scraping":self.start_scraping,
                                    },
                                    "default": None
                                },                           
                            ],
                            callback=callback
                        )
        self.cv = None
        self.position = None

    def install(self):
        super().install()
        
        requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Install dependencies using pip from requirements.txt
        subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])      
        ASCIIColors.success("Installed successfully")        

    def help(self, prompt="", full_context=""):
        self.personality.InfoMessage(self.personality.help)
    
    def add_file(self, path, client, callback=None):
        """
        Here we implement the file reception handling
        """
        super().add_file(path, client, callback)

    def save_text(self, text, path:Path):
        with open(path,"w", encoding="utf8") as f:
            f.write(text)

    def search_and_zip(self, query,  output =""):
        self.step_start("Performing internet search")
        self.add_chunk_to_message_content("")
        pages = internet_search(query, self.personality_config.nb_search_pages, buttons_to_press=self.personality_config.buttons_to_press, quick_search=self.personality_config.quick_search)
        processed_pages = ""
        if len(pages)==0:
            self.set_message_content("Failed to do internet search!!")
            self.step_end("Performing internet search",False)
            return
        self.step_end("Performing internet search")
        for page in pages:
            if self.personality_config.quick_search:
                page_text = f"page_title: {page['title']}\npage_brief:{page['brief']}"
            else:
                page_text = f"page_title: {page['title']}\npage_content:{page['content']}"
            tk = self.personality.model.tokenize(page_text)
            self.step_start(f"summerizing {page['title']}")
            if len(tk)<int(self.personality_config.zip_size) or self.personality_config.summary_mode!="RAG":
                page_text = self.summarize_text(page_text,"\n".join([
                                f"Extract from the document any information related to the query. Write the output as a short article.",
                                "The summary should contain exclusively information from the document chunk.",
                                "Do not provide opinions nor extra information that is not in the document chunk",
                                f"{'Keep the same language.' if self.personality_config.keep_same_language else ''}",
                                f"{'Preserve the title of this document if provided.' if self.personality_config.preserve_document_title else ''}",
                                f"{'Preserve author names of this document if provided.' if self.personality_config.preserve_authors_name else ''}",
                                f"{'Preserve results if presented in the chunk and provide the numerical values if present.' if self.personality_config.preserve_results else ''}",
                                f"{'Eliminate any useless information and make the summary as short as possible.' if self.personality_config.maximum_compression else ''}",
                                f"{self.personality_config.contextual_zipping_text if self.personality_config.contextual_zipping_text!='' else ''}",
                                f"{'The article should be written in '+self.personality_config.translate_to if self.personality_config.translate_to!='' else ''}"
                                f"{self.config.start_header_id_template}query: {query}"
                            ]),
                            "Document chunk"
                            )
                self.set_message_content(page_text)
            else:
                chunks = self.vectorize_and_query(page['content'], page['title'], page['url'], query)
                content = "\n".join([c.text for c in chunks])
                page_text = f"page_title:\n{page['title']}\npage_content:\n{content}"
                page_text = self.summarize_text(page_text,"\n".join([
                        f"Extract from the document any information related to the query. Write the output as a short article.",
                        "The summary should contain exclusively information from the document chunk.",
                        "Do not provide opinions nor extra information that is not in the document chunk",
                        f"{'Keep the same language.' if self.personality_config.keep_same_language else ''}",
                        f"{'Preserve the title of this document if provided.' if self.personality_config.preserve_document_title else ''}",
                        f"{'Preserve author names of this document if provided.' if self.personality_config.preserve_authors_name else ''}",
                        f"{'Preserve results if presented in the chunk and provide the numerical values if present.' if self.personality_config.preserve_results else ''}",
                        f"{'Eliminate any useless information and make the summary as short as possible.' if self.personality_config.maximum_compression else ''}",
                        f"{self.personality_config.contextual_zipping_text if self.personality_config.contextual_zipping_text!='' else ''}",
                        f"{'The article should be written in '+self.personality_config.translate_to if self.personality_config.translate_to!='' else ''}"
                        f"{self.config.start_header_id_template}query: {query}"
                    ]),
                    "Document chunk"
                    )
                self.set_message_content(page_text)
            self.set_message_content(page_text)

            self.step_end(f"Last composition")
            self.step_end(f"summerizing {page['title']}")
            processed_pages += f"{page['title']}\n{page_text}"

        page_text = self.summarize_text(processed_pages,"\n".join([
                f"Extract from the document any information related to the query. Write the output as a short article.",
                "The summary should contain exclusively information from the document chunk.",
                "Do not provide opinions nor extra information that is not in the document chunk",
                f"{'Keep the same language.' if self.personality_config.keep_same_language else ''}",
                f"{'Preserve the title of this document if provided.' if self.personality_config.preserve_document_title else ''}",
                f"{'Preserve author names of this document if provided.' if self.personality_config.preserve_authors_name else ''}",
                f"{'Preserve results if presented in the chunk and provide the numerical values if present.' if self.personality_config.preserve_results else ''}",
                f"{'Eliminate any useless information and make the summary as short as possible.' if self.personality_config.maximum_compression else ''}",
                f"{self.personality_config.contextual_zipping_text if self.personality_config.contextual_zipping_text!='' else ''}",
                f"{'The summary should be written in '+self.personality_config.translate_to if self.personality_config.translate_to!='' else ''}"
                f"{self.config.start_header_id_template}query: {query}"
            ]),
            "Document chunk",
            callback=self.sink
            )
        self.set_message_content(page_text)

        self.step_start(f"Last composition")
        page_text = self.summarize_text(page_text,"\n".join([
                f"Rewrite this document in a better way while respecting the following guidelines:",
                f"{'Keep the same language.' if self.personality_config.keep_same_language else ''}",
                f"{'Preserve the title of this document if provided.' if self.personality_config.preserve_document_title else ''}",
                f"{'Preserve author names of this document if provided.' if self.personality_config.preserve_authors_name else ''}",
                f"{'Preserve results if presented in the chunk and provide the numerical values if present.' if self.personality_config.preserve_results else ''}",
                f"{'Eliminate any useless information and make the summary as short as possible.' if self.personality_config.maximum_compression else ''}",
                f"{self.personality_config.contextual_zipping_text if self.personality_config.contextual_zipping_text!='' else ''}",
                f"{'The summary should be written in '+self.personality_config.translate_to if self.personality_config.translate_to!='' else ''}"
            ]),
            "Document chunk",
            callback=self.sink
            )
        self.set_message_content(page_text)
        self.step_end(f"Last composition")

        if self.personality_config.output_path:
            self.save_text(page_text, Path(self.personality_config.output_path)/(page['title']+"_summary.txt"))
        return page_text, output
                    
        

    def start_scraping(self, prompt="", full_context=""):
        self.new_message("")
        if self.personality_config.search_query!="":
            self.search_and_zip(self.personality_config.search_query)
        else:
            self.info("Please put a search query in the search query setting of this personality.")


    def generate_thumbnail_html(self, feed):
        if type(feed)==list:
            thumbnails = feed
        else:
            thumbnails = feed.get('media_thumbnail',[])
        
        thumbnail_html = ''
        for thumbnail in thumbnails:
            try:
                url = thumbnail['url']
            except:
                continue
            try:
                width = thumbnail['width']
            except:
                width = 500
            try:
                height = thumbnail['height']
            except:
                height = 200
            
            thumbnail_html += f'<img src="{url}" width="{width}" height="{height}" alt="Thumbnail" style="margin-right: 10px;">'
        
        card_html = f'''
<div style="width: 100%; border: 1px solid #ccc; border-radius: 5px; padding: 20px; font-family: Arial, sans-serif; margin-bottom: 20px; box-sizing: border-box;">
    {thumbnail_html}
</div>
        '''
        return card_html

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
        self.step_start("Understanding request")
        if self.yes_no("Is the user asking for information that requires verification using internet search?", previous_discussion_text):
            self.step_end("Understanding request")
            self.step("Decided to make an internet search")
            self.personality.step_start("Crafting internet search query")
            query = self.personality.fast_gen(f"{self.config.start_header_id_template}discussion:\n{previous_discussion_text}{self.config.separator_template}{self.config.start_header_id_template}{self.config.system_message_template}{self.config.end_header_id_template}Read the discussion and craft a web search query suited to recover needed information to reply to last {self.personality.config.user_name} message.\nDo not answer the prompt. Do not add explanations.{self.config.separator_template}{self.config.start_header_id_template}current date: {datetime.now()}{self.config.separator_template}{self.config.start_header_id_template}websearch query: ", max_generation_size=256, show_progress=True, callback=self.personality.sink).split("\n")[0]
            self.personality.step("Query: "+query)
            self.personality.step_end("Crafting internet search query")

            self.personality.step_start("Scraping (this may take time, so be patient) ....")
            self.search_and_zip(query)
            self.personality.step_end("Scraping (this may take time, so be patient) ....")
        else:
            self.step_end("Understanding request")
            self.fast_gen(previous_discussion_text, callback=self.callback)
        return ""


