from lollms.config import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate, InstallOption
from lollms.personality import APScript, AIPersonality
from lollms.paths import LollmsPaths
import urllib.parse
import urllib.request
import json

from urllib.parse import quote
from pathlib import Path
import subprocess

def format_url_parameter(value):
    encoded_value = value.strip().replace("\"","")
    return encoded_value

def extract_results(url, max_num):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from bs4 import BeautifulSoup

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode

    # Set path to chromedriver executable (replace with your own path)
    chromedriver_path = "path/to/chromedriver"

    # Create a new Chrome webdriver instance
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)

    # Load the webpage
    driver.get(url)

    # Wait for JavaScript to execute and get the final page source
    html_content = driver.page_source

    # Close the browser
    driver.quit()

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

    # Find all <li> tags within the <ol> tag
    li_tags = ol_tag.find_all("li")

    # Loop through each <li> tag, limited by max_num
    for index, li_tag in enumerate(li_tags):
        if index > max_num:
            break

        try:
            # Find the three <div> tags within the <article> tag
            div_tags = li_tag.find_all("div")

            # Extract the link, title, and content from the <div> tags
            links = div_tags[0].find_all("a")
            span = links[1].find_all("span")
            link = span[0].text.strip()

            title = div_tags[2].text.strip()
            content = div_tags[3].text.strip()

            # Add the extracted information to the list
            results_list.append({
                "link": link,
                "title": title,
                "content": content
            })
        except Exception:
            pass

    return results_list

   
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
        
        personality_config = TypedConfig(
            ConfigTemplate([
                {"name":"num_results","type":"int","value":3, "min":2, "max":100},
            ]),
            BaseConfig(config={
                'num_results'            : 3
            })
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

    
    def internet_search(self, query):
        """
        Perform an internet search using the provided query.

        Args:
            query (str): The search query.

        Returns:
            dict: The search result as a dictionary.
        """
        formatted_text = ""
        results = extract_results(f"https://duckduckgo.com/?q={format_url_parameter(query)}&t=h_&ia=web", self.personality_config.num_results)
        for result in results:
            title = result["title"]
            content = result["content"]
            link = result["link"]
            formatted_text += f"{title}: {content}\nsource: {link}\n\n"

        print("Searchengine results : ")
        print(formatted_text)
        return formatted_text

    def process_model_input(self, search_query):
        """
        Process the model input.

        Currently, this method returns None.

        Args:
            text (str): The model input text.

        Returns:
            None: Currently, this method returns None.
        """
        
        return "question:\n"+search_query+"\nsearch results:\n"+self.internet_search(search_query)+"\nsummary:\n"

    def process_model_output(self, text):
        """
        Process the model output.

        If the output contains a search query, perform an internet search.

        Args:
            text (str): The model output text.

        Returns:
            dict or None: The search result as a dictionary if a search query is found,
                otherwise returns None.
        """
        return None
