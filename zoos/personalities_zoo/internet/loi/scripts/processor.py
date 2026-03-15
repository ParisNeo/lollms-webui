from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate, InstallOption
from lollms.prompting import LollmsContextDetails
from lollms.types import MSG_OPERATION_TYPE
from lollms.personality import APScript, AIPersonality, craft_a_tag_to_specific_text

from safe_store import TextVectorizer, VectorizationMethod, VisualizationMethod
from typing import Callable, Any
import subprocess

def get_favicon_url(url):
    import requests
    from bs4 import BeautifulSoup
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    favicon_link = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')
    
    if favicon_link:
        favicon_url = favicon_link['href']
        if not favicon_url.startswith('http'):
            favicon_url = url + favicon_url
        return favicon_url
    
    return None


def get_root_url(url):
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    root_url = parsed_url.scheme + "://" + parsed_url.netloc
    return root_url
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
        self.queries=[]
        self.formulations=[]
        self.summaries=[]
        self.word_callback = None
        self.generate_fn = None
        template = ConfigTemplate([
                {"name":"craft_search_query","type":"bool","value":False},
                {"name":"chromedriver_path","type":"str","value":""},
                {"name":"chunk_size","type":"int","value":512, "min":128, "max":personality.model.config["ctx_size"]//2},
                {"name":"chunk_overlap","type":"int","value":128, "min":0, "max":personality.model.config["ctx_size"]//2},
                {"name":"num_results","type":"int","value":5, "min":2, "max":100},
                {"name":"num_relevant_chunks","type":"int","value":2, "min":1, "max":100},

                {"name":"max_query_size","type":"int","value":50, "min":10, "max":personality.model.config["ctx_size"]},
                {"name":"max_summery_size","type":"int","value":256, "min":10, "max":personality.model.config["ctx_size"]},
            ])
        config = BaseConfig.from_template(template)
        personality_config = TypedConfig(
            template,
            config
        )
        super().__init__(
                            personality,
                            personality_config,
                            callback=callback
                        )
        
        
        
    def install(self):
        super().install()
        requirements_file = self.personality.personality_package_path / "requirements.txt"
        # install requirements
        subprocess.run(["pip", "install", "--upgrade", "--no-cache-dir", "-r", str(requirements_file)])        
        ASCIIColors.success("Installed successfully")

    def uninstall(self):
        super().uninstall()


    def format_url_parameter(self, value:str):
        encoded_value = value.strip().replace("\"","")
        return encoded_value


    def get_relevant_text_block(
                                    self, 
                                    url,
                                    driver,
                                ):
        from bs4 import BeautifulSoup    
        # Load the webpage
        driver.get(url)

        # Wait for JavaScript to execute and get the final page source
        html_content = driver.page_source

        # Parse the HTML content
        soup = BeautifulSoup(html_content, "html.parser")
        # Example: Remove all <script> and <style> tags
        for script in soup(["script", "style"]):
            script.extract()

        all_text = soup.get_text()
        # Example: Remove leading/trailing whitespace and multiple consecutive line breaks
        self.step_end("Recovering data")
        self.vectorizer.add_document(url,all_text, self.personality_config.chunk_size, self.personality_config.chunk_overlap)
        self.step_end("Vectorizing data")


    def extract_results(self, url, max_num, driver=None):
        from bs4 import BeautifulSoup    

        # Load the webpage
        driver.get(url)

        # Wait for JavaScript to execute and get the final page source
        html_content = driver.page_source

        # Parse the HTML content
        soup = BeautifulSoup(html_content, "html.parser")

        # Detect that no outputs are found
        Not_found = soup.find("No results found")

        if Not_found : 
            return []    

        # Find the <ol> tag with class="react-results--main"
        ol_tag = soup.find("ol", class_="react-results--main")

        # Initialize an empty list to store the results
        results_list = []

        try:
            # Find all <li> tags within the <ol> tag
            li_tags = ol_tag.find_all("li")

            # Loop through each <li> tag, limited by max_num
            for index, li_tag in enumerate(li_tags):
                if index > max_num*3:
                    break

                try:
                    # Find the three <div> tags within the <article> tag
                    div_tags = li_tag.find_all("div")

                    # Extract the link, title, and content from the <div> tags
                    links = div_tags[0].find_all("a")
                    href_value = links[1].get('href')
                    span = links[1].find_all("span")
                    link = span[0].text.strip()

                    title = div_tags[2].text.strip()
                    content = div_tags[3].text.strip()

                    # Add the extracted information to the list
                    results_list.append({
                        "link": link,
                        "href": href_value,
                        "title": title,
                        "brief": content
                    })
                except Exception:
                    pass
        except:
            pass
        return results_list
     
    def internet_search(self, query, chromedriver_path):
        """
        Perform an internet search using the provided query.

        Args:
            query (str): The search query.

        Returns:
            dict: The search result as a dictionary.
        """

        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        formatted_text = ""
        nb_non_empty = 0
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode

        # Set path to chromedriver executable (replace with your own path)
        if chromedriver_path is None: 
            chromedriver_path = ""#"/snap/bin/chromium.chromedriver"    

        # Create a new Chrome webdriver instance
        try:
            driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
        except:
            driver = webdriver.Chrome(options=chrome_options)

        results = self.extract_results(
                                    f"https://duckduckgo.com/?q={self.format_url_parameter(query)}&t=h_&ia=web",
                                    self.personality_config.num_results,
                                    driver
                                )
        for i, result in enumerate(results):
            title = result["title"]
            brief = result["brief"]
            href = result["href"]
            self.get_relevant_text_block(href, driver)
            nb_non_empty += 1
            if nb_non_empty>=self.personality_config.num_results:
                break
        self.vectorizer.index()

        # Close the browser
        driver.quit()

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
        self.vectorizer = TextVectorizer(VectorizationMethod.TFIDF_VECTORIZER, self.personality.model)

        if self.personality_config.craft_search_query:
            # 1 first ask the model to formulate a query
            search_formulation_prompt = self.build_prompt([
                f"{self.config.start_header_id_template}{self.config.system_message_template}:",
                "Formulate a web search query text based on the user prompt.",
                "Use the same language as the prompt",
                f"{self.config.start_header_id_template} previous discussion:",
                context_details.discussion_messages,
                f"{self.config.start_header_id_template}prompt:",
                f"{prompt}",
                f"{self.config.start_header_id_template}formulated web search query in the same language as the prompt: "
                ],
                4
            )

            self.step_start("Crafting search query")
            search_query = self.format_url_parameter(self.generate(search_formulation_prompt, self.personality_config.max_query_size)).strip()
            if search_query=="":
                search_query=prompt
            self.step_end("Crafting search query")
        else:
            search_query = prompt
            
        self.step_start("Performing internet search")
        self.internet_search(search_query, self.personality_config.chromedriver_path)
        self.step_end("Performing internet search")

        self.step_start("Organizing data")
        docs, sorted_similarities, document_ids = self.vectorizer.recover_text(search_query, self.personality_config.num_relevant_chunks)
        self.step_end("Organizing data")

        search_result = [f"[{i+1}] source: {s[0]}\n{d}" for i,(d,s) in enumerate(zip(docs, sorted_similarities))]
        self.step_start("Building summary")
        
        prompt =  self.build_prompt([
                f"{self.config.start_header_id_template}instructions:",
                "Use Search engine results to answer user question by summarizing the results in a single coherent paragraph in the form of a markdown text",
                "Sources must be  cited after each fact in the format [index].",
                "Place the citation links in front of each relevant information. Only use citation to the provided sources.",
                "If the information required by the user does not exist in the data recovered from the search engine, please notify the user.",
                "Citation is mandatory.",
                "Do not write the sources, just use their index. The sources will be added in a future query."
                f"{self.config.start_header_id_template} previous discussion:",
                context_details.discussion_messages,
                f"{self.config.start_header_id_template} search results:",
                f"{search_result}",              
                f"{self.config.start_header_id_template} question:",
                f"{prompt}",
                f"{self.config.start_header_id_template} answer:"
                ],
                7
            )
        print(prompt)
        output = self.fast_gen(prompt, self.personality_config.max_summery_size, callback=self.sink)
        self.set_message_content(output)
        sources_text = '<div class="mt-4 flex flex-wrap items-center gap-x-2 gap-y-1.5 text-sm ">'
        sources_text += '<div class="text-gray-400 mr-10px">Sources:</div>'
        for i,s in enumerate(sorted_similarities):
            url = "/".join(s[0].split("/")[:-1])
            anchor_url = craft_a_tag_to_specific_text("_".join(s[0].split('_')[:-2]),docs[i][0:2],"_".join(s[0].split('_')[:-2]))
            # link = "_".join(s[0].split('_')[:-2])
            # href = "_".join(s[0].split('_')[:-2])
            favicon_url = get_favicon_url(url)
            if favicon_url is None:
                favicon_url ="/personalities/internet/loi/assets/logo.png"
            root_url = get_root_url(url)
            sources_text += "\n".join([
                f'<a class="flex items-center gap-2 whitespace-nowrap rounded-lg border bg-white px-2 py-1.5 leading-none hover:border-gray-300 dark:border-gray-800 dark:bg-gray-900 dark:hover:border-gray-700" target="_blank" href="{anchor_url}">',
                f'<img class="h-3.5 w-3.5 rounded" src="{favicon_url}">'
                f'<div>{root_url}</div>'
                f'</a>',
                ])
            #sources_text += f"- [{i+1}] : {crafted_link}\n\n"#{link}]({href})\n\n"
        sources_text += '</div>'
        output = output+sources_text
        self.set_message_content(output)
        self.step_end("Building summary")

        return output



