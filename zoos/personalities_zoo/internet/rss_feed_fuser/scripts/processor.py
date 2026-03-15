from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.utilities import PackageManager
from lollms.personality import APScript, AIPersonality
from lollms.prompting import LollmsContextDetails
from lollms.types import MSG_OPERATION_TYPE
from lollms.internet import internet_search, scrape_and_save
from typing import Callable, Any
from datetime import datetime
import requests
from pathlib import Path
import json
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

import pipmaster as pm
if not pm.is_installed("docling"):
    pm.install("docling")
if not pm.is_installed("feedparser"):
    pm.install("feedparser")


from feedparser import parse as feedparse
import subprocess
from pathlib import Path
from datetime import datetime
import json
from lollms.client_session import Client
from ascii_colors import trace_exception

from urllib.parse import urlparse

from docling.document_converter import DocumentConverter

if not pm.is_installed("feedparser"):
   pm.is_installed("feedparser")

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
                {"name":"nb_rss_feeds_per_source","type":"int","value":5, "help":"the maximum number of rss feed pages to search"},
                {"name":"rss_scraping_type","type":"str","value":"quick","options":["quick","deep"], "help":"quick uses only the breafs to build the summary and the deep will scrape data from the website"},
                {"name":"rss_urls","type":"text","value":"https://feeds.bbci.co.uk/news/rss.xml, http://rss.cnn.com/rss/cnn_topstories.rss, https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml, https://www.theguardian.com/world/rss, https://www.reuters.com/rssfeed/topNews, http://feeds.foxnews.com/foxnews/latest, https://www.aljazeera.com/xml/rss/all.xml, https://www.bloomberg.com/politics/feeds/site.xml", "help":"Here you can put rss feed address to recover data."},
                {"name":"categories","type":"text","value":"World News,Entertainment,Sport,Technology,Education,Medicine,Space,R&D,Politics,Music,Business,Peaple", "help":"The list of categories to help the AI organize the news."},
                {"name":"keep_only_multi_articles_subjects","type":"bool","value":False, "help":"When this option is true, only articles that have more than one source are kept"},


                {"name":"memorization_prompt","type":"text","value":"Make sure you keep all important information as bullet points. If you find a new article url and title add it immediately to the memory.", "help":"The instructions about what to memorize from the articles"},
                {"name":"task_prompt","type":"text","value":"Using the following memories about the articles write your own making sure you use only the information from the memories. do not explicitely mention the articles except for specifying a point or criticizing. Make sure you are factual and unbioased. Identify key consistent points made, as well as contrasting points of view made across multiple articles. Use this information to write a new, unbiased news article, keeping it as factual and centric as possible. It should be written in a tone and style that reads like a news article or news anchor script. the output mist be a html div. make sure you format the output correctly.", "help":"The task to be done (after extracting information into a memory)"},
                {"name":"output_format","type":"text","value":"newspaper column in html format. Respond only with the html code, no comments or explanations.", "help":"The output format"},

                {"name":"quick_search","type":"bool","value":False, "help":"Quick search returns only a brief summary of the webpage"},
                {"name":"summary_mode","type":"str","value":"RAG", "options":["RAG","Full Summary"], "help":"If Rag is used then the AI will search for useful data before summerizing, else it's gonna read the whole page before summary. The first is faster, but the second allows accessing the whole information without compromize."},                
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
                                        "scrape_news":self.scrape_news
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

    def generate_thumbnail_html(self, entry):
        """
        Generates HTML for a single thumbnail or favicon from an RSS feed entry.
        Args:
            entry: A single RSS feed entry (from feedparser).
        Returns:
            str: HTML string containing a single thumbnail or favicon with citation.
        """
        if not entry or not isinstance(entry, dict):
            return ''
        
        # Try to find a thumbnail
        thumbnail = None
        if 'media_thumbnail' in entry and entry['media_thumbnail']:
            thumbnail = entry['media_thumbnail'][0]  # Take the first thumbnail
        elif 'media_content' in entry:
            thumbnails = [media for media in entry['media_content'] if media.get('type', '').startswith('image/')]
            if thumbnails:
                thumbnail = thumbnails[0]  # Take the first image media
        elif 'enclosures' in entry:
            thumbnails = [enclosure for enclosure in entry['enclosures'] if enclosure.get('type', '').startswith('image/')]
            if thumbnails:
                thumbnail = thumbnails[0]  # Take the first image enclosure
        
        # If no thumbnail is found, try to get the favicon
        if not thumbnail:
            try:
                # Get the base URL from the entry's link or source
                link = entry.get('link', '')
                if not link:
                    return ''
                
                base_url = urlparse(link).netloc
                if not base_url:
                    return ''
                
                # Fetch the website's HTML to find the favicon
                response = requests.get(f"https://{base_url}",timeout=3)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for the favicon in the HTML
                favicon = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')
                if favicon:
                    favicon_url = favicon['href']
                    if not favicon_url.startswith(('http:', 'https:')):
                        favicon_url = f"https://{favicon_url.lstrip('/')}"
                    
                    # Use the favicon as the thumbnail
                    thumbnail = {'url': favicon_url}
            except Exception as e:
                ASCIIColors.error(f"Error fetching favicon: {e}")
                return ''
        
        if not thumbnail:
            return ''
        
        # Generate HTML for the thumbnail or favicon
        try:
            url = thumbnail.get('url', '')
            if not url:
                return ''
            
            # Extract the base URL from the thumbnail URL
            base_url = urlparse(url).netloc
            
            # Use the source from the entry if available, otherwise use the base URL
            source = entry.get('source', {}).get('title', base_url)
            
            return f'''
            <div class="relative group">
                <img 
                    src="{url}" 
                    alt="Thumbnail" 
                    class="w-full h-32 object-cover rounded-lg transition-transform duration-300 group-hover:scale-105"
                >
                <div class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-60 text-white text-xs p-2 rounded-b-lg">
                    Source: {source}
                </div>
            </div>
            '''
        except Exception as e:
            print(f"Error processing thumbnail: {e}")
            return ''

    def recover_all_rss_feeds(self):
        """
        Fetches and processes RSS feeds from configured URLs.
        """
        output_folder = Path(self.personality_config.output_folder)
        if not output_folder.exists():
            print("Output folder does not exist. Please configure a valid path.")
            return
        
        if not self.personality_config.rss_urls:
            print("No RSS URLs configured.")
            return
        
        rss_feeds = [feed.strip() for feed in self.personality_config.rss_urls.split(",")]
        links = []
        feeds = []
        
        for rss_feed in rss_feeds:
            feed = feedparse(rss_feed)
            for p in feed.entries[:self.personality_config.nb_rss_feeds_per_source]:
                self.step(f"Processing {p.title}")
                content = p.get('summary', p.get('description', ''))
                thumbnail_html = self.generate_thumbnail_html(p)
                if content:
                    # Save feed data for later use in fuse_articles
                    feed_data = {
                        'title': p.title,
                        'link': p.link,
                        'description': content,
                        'media_thumbnail': p.get('media_thumbnail', []),  # Assuming media_thumbnail is available
                        'thumbnail_html': thumbnail_html,  # Add the thumbnail HTML to the JSON
                    }
                    feeds.append(feed_data)
                    
                    # Generate HTML card for immediate display
                    card = f'''
                    <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                        <div class="p-6">
                            <h3 class="text-lg font-medium text-gray-800 mb-2">
                                <a href="{p.link}" target="_blank" class="hover:text-blue-600 transition-colors">{p.title}</a>
                            </h3>
                            {thumbnail_html}
                            <p class="text-gray-600 text-sm">{content}</p>
                        </div>
                    </div>
                    '''
                    links.append(card)
        
        self.step("Saving the news json file")
        # Save feeds to JSON for later use in fuse_articles
        with open(output_folder / "news_data.json", "w") as f:
            json.dump(feeds, f, indent=4)
        
        # Generate HTML output for immediate display
        output = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>News Aggregator</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-50">
            <div class="container mx-auto px-4 py-8">
                <h1 class="text-3xl font-bold text-gray-800 mb-8">Latest News</h1>
                <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {"".join(links)}
                </div>
            </div>
        </body>
        </html>
        '''
        
        self.step("Saving the news html file")
        with open(output_folder / "news.html", "w", encoding="utf8") as f:
            f.write(output)
        
        self.set_message_html(output)

    def fuse_articles(self):
        """
        Fuses similar articles and generates a categorized JSON output with summaries.
        """
        output_folder = Path(self.personality_config.output_folder)
        if not output_folder.exists():
            self.set_message_content("Output folder does not exist. Please configure a valid path.")
            return
        
        with open(output_folder / "news_data.json", "r") as f:
            feeds = json.load(f)
        
        themes = {}
        processed = set()     
        total_feeds = len(feeds)   
        for i, feed in enumerate(feeds):
            if i in processed:
                continue
            
            # Create a new theme for this article
            theme_key = f"theme_{len(themes) + 1}"
            themes[theme_key] = {
                'title': feed['title'],
                'thumbnails': feed.get('media_thumbnail', []),
                'content': feed.get('description', ''),
                'urls': [feed['link']]
            }
            
            # Compare with other articles to find similar ones
            for j, other_feed in enumerate(feeds[i + 1:], start=i + 1):
                if j in processed:
                    continue
                
                # Simple similarity check (can be replaced with more advanced NLP)
                if self.are_articles_similar(feed, other_feed):
                    themes[theme_key]['urls'].append(other_feed['link'])
                    themes[theme_key]['content'] += f"\n\n{other_feed.get('description', '')}"
                    processed.add(j)
                self.update_double_progress(i, total_feeds, j-i, total_feeds - i, feed['title'], other_feed['title'])
            
            processed.add(i)
        nb_fused_articles = 0
        for theme_key, theme_data in themes.items():
            if len(theme_data['urls']) > 1:
                nb_fused_articles += 1

        self.set_message_html(f"""<div class="flex justify-center items-end">
            <p><span animate-pulse text-xl font-semibold mr-2>{nb_fused_articles} themes are being built out of the articles...</spam></div>
        </style>

        <script>
        // Simulate loading delay for demonstration purposes.
        setTimeout(function() {{
        document.querySelector('span').textContent = 'Summary complete!';
        }}, 30 * nb_fused_articles);
        </script>""")
        # Generate summaries for themes with multiple articles
        toremove = []
        for theme_key, theme_data in themes.items():
            if len(theme_data['urls']) > 1:
                prompt = self.create_summary_prompt(theme_data)
                summary = self.sequential_summarize(
                                                        prompt, 
                                                        summary_context=self.personality_config.memorization_prompt,
                                                        task=self.personality_config.task_prompt,format=self.personality_config.output_format)
                theme_data['summary'] = summary
            else:
                if self.personality_config.keep_only_multi_articles_subjects:
                    toremove.append(theme_key)
                else:
                    theme_data['summary'] = theme_data['content'].strip()
                    
        # Remove themes that are no longer needed using a dictionary comprehension.
        themes = {key: value for key, value in themes.items() if not key in toremove}

        # Save the fused data to a JSON file
        with open(output_folder / "fused_articles.json", "w") as f:
            json.dump(themes, f, indent=4)

    def load_article_text(self, url):
        """
        Loads the text content of an article from a given URL.
        
        :param url: The URL of the article.
        :return: The text content of the article.
        """
        converter = DocumentConverter()
        result = converter.convert(url)
        return result.document.export_to_markdown()

    def create_summary_prompt(self, theme_data):
        """
        Creates a prompt for generating a summary of the fused articles.
        
        :param theme_data: The data for the theme containing multiple articles.
        :return: A prompt string for the AI to generate a summary.
        """
        prompt = "List of articles:\n\n"
        for i, url in enumerate(theme_data['urls']):
            prompt += f"Article {i + 1}:\n"
            prompt += f"Title: {theme_data['title']}\n"
            prompt += f"URL: {url}\n"
            prompt += f"Description: {theme_data['content']}\n"
            try:
                prompt += f"Text Content:\n{self.load_article_text(url)}\n\n"
            except:
                ASCIIColors.warning("Couldn't load the webpage because of protection")
        return prompt
    

    def update_double_progress(self, outer_current, outer_total, inner_current, inner_total, current_feed_title, other_feed_title):
        # Calculate outer progress percentage
        outer_progress_percent = (outer_current / outer_total) * 100

        # Calculate inner progress percentage
        inner_progress_percent = (inner_current / inner_total) * 100

        # Generate the updated HTML
        html_code = f"""
        <div class="space-y-4">
            <!-- Outer Progress Bar -->
            <div>
                <div class="text-sm font-medium mb-1">Overall Progress</div>
                <div class="w-full bg-gray-200 rounded-full h-4 dark:bg-gray-700">
                    <div id="outer-progress-bar" class="bg-blue-600 h-4 rounded-full" style="width: {outer_progress_percent}%;"></div>
                </div>
                <div id="outer-progress-text" class="mt-1 text-sm text-gray-700 dark:text-gray-300">
                    {int(outer_progress_percent)}% - Processing feed {outer_current} of {outer_total}...
                </div>
            </div>

            <!-- Inner Progress Bar -->
            <div>
                <div class="text-sm font-medium mb-1">Comparing Current Feed</div>
                <div class="w-full bg-gray-200 rounded-full h-4 dark:bg-gray-700">
                    <div id="inner-progress-bar" class="bg-green-600 h-4 rounded-full" style="width: {inner_progress_percent}%;"></div>
                </div>
                <div id="inner-progress-text" class="mt-1 text-sm text-gray-700 dark:text-gray-300">
                    {int(inner_progress_percent)}% - Compared {inner_current} of {inner_total} feeds...
                </div>
            </div>

            <!-- Article Titles -->
            <div class="space-y-2">
                <div class="text-sm font-medium">Current Feed:</div>
                <div class="text-sm text-gray-700 dark:text-gray-300">{current_feed_title}</div>
                <div class="text-sm font-medium">Comparing With:</div>
                <div class="text-sm text-gray-700 dark:text-gray-300">{other_feed_title}</div>
            </div>

            <!-- Animation (Spinning Loader) -->
            <div class="flex justify-center items-center mt-4">
                <div class="animate-spin h-8 w-8 border-4 border-blue-500 rounded-full border-t-transparent"></div>
            </div>
        </div>
        """

        # Update the HTML in the UI
        self.set_message_html(html_code)

    def are_articles_similar(self, article1, article2):
        """
        Checks if two articles are similar based on their titles and descriptions.
        Args:
            article1: First article.
            article2: Second article.
        Returns:
            bool: True if articles are similar, False otherwise.
        """
        title1 = article1.get('title', '').lower()
        title2 = article2.get('title', '').lower()
        desc1 = article1.get('description', '').lower()
        desc2 = article2.get('description', '').lower()
        
        # Combine titles and descriptions for a more comprehensive similarity check
        combined_text1 = f"{title1} {desc1}"
        combined_text2 = f"{title2} {desc2}"
        
        # Use the yes_no method to determine similarity
        question = f"Are these two articles similar based on their titles and descriptions? Article 1: {combined_text1} Article 2: {combined_text2}"
        return self.yes_no(question, context="Determining article similarity", max_answer_length=50)
    def categorize_news(self):
        """
        Categorizes news articles and generates a categorized HTML output.
        Fused articles (themes with multiple articles) are displayed with AI-generated summaries,
        a clear indication that they are a fusion, and interactive buttons for copying summaries.
        The full summary is displayed in a scrollable container within the card.
        """
        output_folder = Path(self.personality_config.output_folder)
        if not output_folder.exists():
            print("Output folder does not exist. Please configure a valid path.")
            return
        
        # Load the fused articles instead of raw feeds
        with open(output_folder / "fused_articles.json", "r") as f:
            themes = json.load(f)
        
        categories = [c.strip() for c in self.personality_config.categories.split(",")]
        categorized = {cat: [] for cat in categories}
        
        # Assign categories to themes
        for theme_key, theme_data in themes.items():
            # Assign category based on content
            category = self.assign_category(theme_data, categories)
            if category:
                categorized[category].append(theme_data)
        
        # Generate navigation links for categories with articles
        navigation_links = []
        for cat in categories:
            if categorized[cat]:  # Only include categories with articles
                navigation_links.append(f'<a href="#{cat.lower().replace(" ", "-")}" class="text-blue-600 hover:text-blue-800">{cat}</a>')
        
        output = '<!DOCTYPE html>\n'
        output += '<html lang="en">\n'
        output += '<head>\n'
        output += '    <meta charset="UTF-8">\n'
        output += '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        output += '    <title>Categorized News</title>\n'
        output += '    <script src="https://cdn.tailwindcss.com"></script>\n'
        output += '    <style>\n'
        output += '        .favicon {\n'
        output += '            width: 16px;\n'
        output += '            height: 16px;\n'
        output += '            object-fit: cover;\n'
        output += '        }\n'
        output += '        .summary-scroll {\n'
        output += '            max-height: 150px;\n'
        output += '            overflow-y: auto;\n'
        output += '            scrollbar-width: thin;\n'
        output += '            scrollbar-color: #cbd5e0 #f3f4f6;\n'
        output += '        }\n'
        output += '        .summary-scroll::-webkit-scrollbar {\n'
        output += '            width: 8px;\n'
        output += '        }\n'
        output += '        .summary-scroll::-webkit-scrollbar-thumb {\n'
        output += '            background-color: #cbd5e0;\n'
        output += '            border-radius: 4px;\n'
        output += '        }\n'
        output += '        .summary-scroll::-webkit-scrollbar-track {\n'
        output += '            background-color: #f3f4f6;\n'
        output += '        }\n'
        output += '    </style>\n'
        output += '</head>\n'
        output += '<body class="bg-gray-50">\n'
        output += '    <div class="container mx-auto px-4 py-8">\n'
        output += '        <h1 class="text-3xl font-bold text-gray-800 mb-8">Categorized News</h1>\n'
        
        # Add navigation UI
        if navigation_links:
            output += '        <div class="sticky top-0 bg-white shadow-sm py-4 mb-8 z-50">\n'
            output += '            <nav class="flex space-x-4">\n'
            output += '                <span class="font-semibold">Jump to:</span>\n'
            output += '                ' + ' | '.join(navigation_links) + '\n'
            output += '            </nav>\n'
            output += '        </div>\n'
        
        for cat, themes_in_category in categorized.items():
            if not themes_in_category:  # Skip empty categories
                continue
            
            output += f'        <section id="{cat.lower().replace(" ", "-")}" class="mb-12">\n'
            output += f'            <h2 class="text-2xl font-semibold text-gray-800 mb-6">{cat}</h2>\n'
            output += '            <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">\n'

            for theme_data in themes_in_category:
                output += '                <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">\n'
                
                # Add thumbnail or favicon if available
                thumbnail = theme_data.get("thumbnails", [{}])[0].get("url", "") if theme_data.get("thumbnails") else ""
                if not thumbnail:
                    # Try to get favicon from the website
                    domain = urlparse(theme_data['urls'][0]).netloc if theme_data['urls'] else ""
                    if domain:
                        favicon_url = f"https://{domain}/favicon.ico"
                        try:
                            # Check if favicon exists
                            response = requests.head(favicon_url)
                            if response.status_code == 200:
                                thumbnail = favicon_url
                        except:
                            pass
                
                if thumbnail:
                    output += f'                    <img src="{thumbnail}" alt="Thumbnail" class="w-full h-48 object-cover">\n'
                
                output += '                    <div class="p-6">\n'
                output += f'                        <h3 class="text-lg font-medium text-gray-800 mb-2">\n'
                output += f'                            <a href="{theme_data["urls"][0]}" class="hover:text-blue-600 transition-colors">{theme_data["title"]}</a>\n'
                
                # Add a "Fusion" label if this theme contains multiple articles
                if len(theme_data['urls']) > 1:
                    output += '                            <span class="ml-2 bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-1 rounded">Fusion</span>\n'
                
                output += '                        </h3>\n'
                
                # Display the AI-generated summary in a scrollable container
                if len(theme_data['urls']) > 1:
                    full_summary = theme_data.get("summary", "")
                    output += f'                        <div class="summary-scroll text-gray-600 text-sm mb-4">\n'
                    output += f'                            <strong>Summary:</strong> {full_summary}\n'
                    output += '                        </div>\n'
                else:
                    output += f'                        <p class="text-gray-600 text-sm mb-4">{theme_data.get("content", "")[:150]}...</p>\n'
                
                output += '                        <div class="flex items-center text-xs text-gray-500">\n'
                
                # Use current date if published date is not available
                published_date = datetime.now().strftime("%Y-%m-%d")
                output += f'                            <span class="mr-2">📅 {published_date}</span>\n'
                
                # Shorten long URLs to website name
                source = urlparse(theme_data['urls'][0]).netloc if theme_data['urls'] else "Unknown source"
                output += f'                            <span>{source}</span>\n'
                
                # Add favicon next to the source
                if source != "Unknown source":
                    favicon_url = f"https://{source}/favicon.ico"
                    output += f'                            <img src="{favicon_url}" alt="Favicon" class="favicon ml-2">\n'
                
                output += '                        </div>\n'
                output += '                    </div>\n'
                output += '                </div>\n'

            output += '            </div>\n'
            output += '        </section>\n'

        output += '    </div>\n'
        output += '</body>\n'
        output += '</html>\n'
        
        with open(output_folder / "categorized_news.html", "w", encoding="utf8") as f:
            f.write(output)

        self.set_message_html(output)

        
    def assign_category(self, article, categories):
        """
        Assigns a category to an article based on its content.
        Args:
            article: The article to categorize.
            categories: List of available categories.
        Returns:
            str: The assigned category.
        """
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        
        # Simple keyword-based categorization
        for cat in categories:
            if cat.lower() in title or cat.lower() in description:
                return cat
        return categories[0]  # Default to the first category if no match is found

    def scrape_news(self, command, full_context, callback, context_state, client:Client):
        """
        Main function to scrape, fuse, and categorize news.
        """
        self.new_message("")
        self.set_message_content("Recovering all RSS feeds ...")
        self.set_message_content("Recovering the rss feeds ...")
        self.recover_all_rss_feeds()
        self.new_message("")
        self.set_message_content("Fusing articles ...")
        self.set_message_content("Fusing articles ...")
        self.fuse_articles()
        self.set_message_content("Categorizing the news ...")
        self.set_message_content("Categorizing the news ...")
        self.categorize_news()


    def search_and_zip(self, query,  output =""):
        self.step_start("Performing internet search")
        self.add_chunk_to_message_content("")
        pages = internet_search(query, self.personality_config.internet_nb_search_pages, buttons_to_press=self.personality_config.buttons_to_press, quick_search=self.personality_config.quick_search)
        processed_pages = ""
        if len(pages)==0:
            self.set_message_html("Failed to do internet search!!")
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
                page_text = self.sequential_summarize(page_text,"\n".join([
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
                            ])                            
                            )
                self.set_message_html(page_text)
            else:
                chunks = self.vectorize_and_query(page['content'], page['title'], page['url'], query)
                content = "\n".join([c.text for c in chunks])
                page_text = f"page_title:\n{page['title']}\npage_content:\n{content}"
                page_text = self.sequential_summarize(page_text,"\n".join([
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
                    ])
                    )
                self.set_message_html(page_text)
            self.set_message_html(page_text)

            self.step_end(f"Last composition")
            self.step_end(f"summerizing {page['title']}")
            processed_pages += f"{page['title']}\n{page_text}"

        page_text = self.sequential_summarize(processed_pages,"\n".join([
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
            ])
            )
        self.set_message_html(page_text)

        self.step_start(f"Last composition")
        page_text = self.sequential_summarize(page_text,"\n".join([
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
        self.set_message_html(page_text)
        self.step_end(f"Last composition")

        if self.personality_config.output_path:
            self.save_text(page_text, Path(self.personality_config.output_path)/(page['title']+"_summary.txt"))
        return page_text, output
                    

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
        if self.yes_no("Is the user asking for information that requires verification using internet search?", previous_discussion_text, callback=self.sink):
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


