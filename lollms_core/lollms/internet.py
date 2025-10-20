from ascii_colors import ASCIIColors, trace_exception
import time
import re
import pipmaster as pm
if not pm.is_installed("freedom_search"):
    pm.install("freedom_search")
from freedom_search import InternetSearchEnhancer
from scrapemaster import ScrapeMaster
from pathlib import Path
from safe_store import SafeStore

def get_favicon_url(url):
    import requests
    from bs4 import BeautifulSoup
    try:
        response = requests.get(url,timeout=3)
        soup = BeautifulSoup(response.text, 'html.parser')
        favicon_link = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')
        
        if favicon_link:
            favicon_url = favicon_link['href']
            if not favicon_url.startswith('http'):
                favicon_url = url + favicon_url
            return favicon_url
    except:
        ASCIIColors.warning(f"Couldn't get fav icon from {url}")
    return None


def get_root_url(url):
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    root_url = parsed_url.scheme + "://" + parsed_url.netloc
    return root_url


def format_url_parameter(value:str):
    encoded_value = value.strip().replace("\"","").replace(" ","+")
    return encoded_value


def wait_for_page(driver, step_delay=1):
    # Get the initial page height
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for the page to load new content
        time.sleep(step_delay)
        
        # Get the new page height
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        # If the page height hasn't changed, exit the loop
        if new_height == last_height:
            break
        
        last_height = new_height


def prepare_chrome_driver(chromedriver_path = None):
    from selenium import webdriver
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    # Create a new instance of the Chrome driver
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    # chrome_options.add_argument('--ignore-certificate-errors')
    # chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument("--enable-third-party-cookies")

    # Set path to chromedriver executable (replace with your own path)
    if chromedriver_path is None: 
        chromedriver_path = ""#"/snap/bin/chromium.chromedriver"    

    # Create a new Chrome webdriver instance
    try:
        driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
    except:
        driver = webdriver.Chrome(options=chrome_options)    
    return driver

def press_buttons(driver, buttons_to_press=['accept']):
    from selenium.webdriver.common.by import By
    from bs4 import BeautifulSoup

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find the button that contains the text "accept" (case-insensitive)
    for button_to_press in buttons_to_press.split(",") if isinstance(buttons_to_press, str) else buttons_to_press:
        try:
            button_to_press = button_to_press.strip()
            button = soup.find('button', text=lambda t: button_to_press in t.lower())

            if button:
                # Click the button using Selenium
                button_element = driver.find_element(By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]")
                button_element.click()
                print(f"Button {button_to_press} clicked!")
            else:
                print(f"Button {button_to_press} not found in page.")
        except:
            ASCIIColors.warning(f"Couldn't press button {button_to_press} in this page.")




import os
from scrapemaster import ScrapeMaster

def scrape_and_save(url, file_path:str|Path=None, use_selenium=False, follow_links=False, max_depth=3, lollms_com=None, chromedriver_path=None, wait_step_delay=1, buttons_to_press=['accept'], max_size=None):
    """
    Scrapes text and image data from a specified URL and saves the images to a given file path.

    Parameters:
    - url (str): The URL to scrape data from.
    - file_path (str, optional): The markdown file path where scraped texts will be saved. If None, texts will not be saved.
    - lollms_com (str, optional): A specific parameter for the ScrapeMaster, if needed.
    - chromedriver_path (str, optional): The path to the ChromeDriver executable for web scraping.
    - wait_step_delay (int, optional): The delay in seconds to wait between steps during scraping. Default is 1 second.
    - buttons_to_press (list, optional): A list of button identifiers to press during the scraping process. Default is ['accept'].
    - max_size (int, optional): The maximum size of images to scrape. If None, all images will be scraped.

    Returns:
    dict: A dictionary containing scraped texts and image URLs.
    """
    # Initialize the scraper with the provided URL
    scraper = ScrapeMaster(url)

    # Optionally handle button presses
    #for button in buttons_to_press:
    #    scraper.press_button(button)

    # Create a subfolder for images if file_path is provided
    if file_path:
        file_path = Path(file_path)
        images_folder = os.path.join(file_path.parent, 'images')
        os.makedirs(images_folder, exist_ok=True)

    # Perform the scraping
    if follow_links:
        results = scraper.scrape_website(max_depth=max_depth, output_dir=file_path.parent, prefix=file_path.stem+'_')
    else:
        results = scraper.scrape_all(output_dir = images_folder, use_selenium=use_selenium)

    # Save scraped texts to the markdown file
    if file_path:
        with open(file_path, 'w', encoding="utf8", errors='ignore') as md_file:
            for text in results['texts']:
                md_file.write(text + '\n\n')
        print(f"Texts saved to {file_path}")
        print(f"Images saved to {images_folder}")
    if len(results['texts'])==0:
        return {
            'texts': ["Query returned no information. Please try to change the query."],
            'image_urls': []
        }
        
    return {
        'texts': results['texts'],
        'image_urls': results['image_urls']
    }


def get_relevant_text_block(
    url,
    vectorizer:SafeStore,
    title=None,
):
    try:
        sm = ScrapeMaster(url)
        result = sm.scrape_all()
        if len(result["texts"])>0:
            vectorizer.add_text(title if title else url, "\n".join(result["texts"]), url)
    except Exception as ex:
        trace_exception(ex)        


def extract_results(url, max_num, driver=None, wait_step_delay=0.5):
    from bs4 import BeautifulSoup    

    # Load the webpage
    driver.get(url)

    # Get the initial page height
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    wait_for_page(driver, wait_step_delay)

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
    
def internet_search(query, internet_nb_search_pages, chromedriver_path=None, quick_search:bool=False, buttons_to_press=['acccept']):
    """
    """

    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    search_results = []

    nb_non_empty = 0
    # Configure Chrome options
    driver = prepare_chrome_driver(chromedriver_path)

    results = extract_results(
                                f"https://duckduckgo.com/?q={format_url_parameter(query)}&t=h_&ia=web",
                                internet_nb_search_pages,
                                driver
                            )
    
    for i, result in enumerate(results):
        title = result["title"]
        brief = result["brief"]
        href = result["href"]
        if quick_search:
            search_results.append({'url':href, 'title':title, 'brief': brief, 'content':""})
        else:
            search_results.append({'url':href, 'title':title, 'brief': brief, 'content':scrape_and_save(href, chromedriver_path=chromedriver_path, buttons_to_press=buttons_to_press)})
        nb_non_empty += 1
        if nb_non_empty>=internet_nb_search_pages:
            break

    return search_results

def internet_search_with_vectorization(query, chromedriver_path=None, internet_nb_search_pages=5, internet_vectorization_chunk_size=512, internet_vectorization_overlap_size=20, internet_vectorization_nb_chunks=4, model = None, quick_search:bool=False, vectorizer = "tfidf", vectorize=True, asses_using_llm=True, yes_no=None):
    """
    """

    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from safe_store import SafeStore

    from safe_store import SafeStore
    # Vectorizer selection
    if vectorizer == "st":
        vectorizer_name = "st:all-MiniLM-L6-v2"
    elif vectorizer == "tfidf":
        vectorizer_name = "tfidf:standard"
    elif vectorizer == "openai":
        vectorizer_name = "openai:text-embedding-3-small"
    elif vectorizer == "ollama":
        vectorizer_name = "ollama:bge-3m"
    tmp_path = Path.home()
    # Create database path and initialize VectorDatabase
    db_path = tmp_path / f"internet_ss.db"
    vdb = SafeStore(db_path)   
    formatted_text = ""
    nb_non_empty = 0
    ise = InternetSearchEnhancer()
    results = ise.search(query, num_results=internet_nb_search_pages)
    
    if len(results)>0:
        for i, result in enumerate(results):
            ASCIIColors.orange(f"Processing result:{result['title']}")
            title = result["title"]
            brief = result["snippet"]
            href = result["url"]
            formatted_text = f"""title: {title}
brenf: {brief}
href: {href}
"""
            if quick_search:
                vdb.add_text(title, formatted_text,vectorizer_name, metadata={"title":title,"brenf":brief,"href":href})
            else:
                get_relevant_text_block(href, vectorizer, title)
            nb_non_empty += 1
            if nb_non_empty>=internet_nb_search_pages:
                break
        chunks = vdb.query(query,vectorizer_name, top_k= internet_vectorization_nb_chunks)
    else:
        chunks = []

    return chunks
