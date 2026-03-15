# Lollms function call definition file
# Import necessary libraries
import requests
from typing import List

from ascii_colors import trace_exception
import pipmaster as pm
pm.ensure_packages({"beautifulsoup4":"", "html2text":""})

# Import the libraries
from bs4 import BeautifulSoup
import html2text

def clean_html_content(html_content: str) -> str:
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    clean_text = h.handle(html_content)
    return clean_text

def search_and_clean_content(keywords: List[str], num_pages: int) -> str:
    try:
        search_query = "+".join(keywords)
        base_url = "https://www.google.com/search?q={query}&start={page}"
        headers = {'User-Agent': 'Mozilla/5.0'}

        all_cleaned_content = []

        for page in range(0, num_pages * 10, 10):
            url = base_url.format(query=search_query, page=page)
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return "Oops! Google is not cooperating. Try again later."

            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('div', class_='BNeawe s3v9rd AP7Wnd')

            for result in results:
                raw_html = result.get_text()
                cleaned_content = clean_html_content(raw_html)
                all_cleaned_content.append(cleaned_content)

        formatted_content = "\n\n".join(all_cleaned_content)
        return formatted_content

    except Exception as e:
        return trace_exception(e)

def search_and_clean_content_function():
    return {
        "function_name": "search_and_clean_content", 
        "function": search_and_clean_content, 
        "function_description": "Searches multiple websites for the given keywords, cleans the content, and returns useful information formatted in sections.", 
        "function_parameters": [
            {"name": "keywords", "type": "List[str]"}, 
            {"name": "num_pages", "type": "int"}
        ] 
    }
