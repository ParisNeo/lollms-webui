# Lollms function call definition file

# Import necessary libraries
import requests
from pathlib import Path

# Partial is useful if we need to preset some parameters
from functools import partial

# It is advised to import typing elements
from typing import List, Optional, Any, Tuple, Dict

from lollms.utilities import discussion_path_to_url

# ascii_colors offers advanced console coloring and bug tracing
from ascii_colors import trace_exception, ASCIIColors

# Import Client from lollms.client_session
from lollms.client_session import Client
import pipmaster as pm
pm.ensure_packages({"beautifulsoup4":""})


# Now we can import the library
from bs4 import BeautifulSoup

# Core function to search for PDFs on arXiv and download them to a specified directory
def arxiv_pdf_search(query: str, max_results: Optional[int] = 5, sort_by: Optional[str] = 'relevance', start_date: Optional[str] = None, end_date: Optional[str] = None, author: Optional[str] = None, client: Optional[Any] = None) -> (str, Dict[str, Any]):
    try:
        if client is None:
            download_to = Path("./pdf_search")
        else:
            download_to = client.discussion.discussion_folder / "pdf_search"
        
        # Construct the search URL with additional parameters
        url = f'http://export.arxiv.org/api/query?search_query={query}&start=0&max_results={max_results}&sortBy={sort_by}'
        if start_date:
            url += f'&startDate={start_date}'
        if end_date:
            url += f'&endDate={end_date}'
        if author:
            url += f'&author={author}'
        
        response = requests.get(url)
        response.raise_for_status()

        # Parse the response
        soup = BeautifulSoup(response.content, 'xml')
        entries = soup.find_all('entry')

        # Create the directory if it doesn't exist
        download_to.mkdir(parents=True, exist_ok=True)

        # Extract PDF URLs and additional information
        html_output = "<html><body>"
        report_content = ""
        pdf_info = {}
        for entry in entries:
            pdf_url = entry.id.text.replace('abs', 'pdf') + '.pdf'
            pdf_name = pdf_url.split('/')[-1]
            pdf_path = download_to / pdf_name

            if client is None:
                local_url = f'/discussions/pdf_search/{pdf_name}'
            else:
                local_url = discussion_path_to_url(pdf_path)

            # Extract additional information
            title = entry.title.text
            authors = ', '.join(author.find('name').text for author in entry.find_all('author'))
            affiliations = ', '.join(affiliation.text for affiliation in entry.find_all('affiliation'))
            abstract = entry.summary.text
            published_date = entry.published.text
            journal_ref = entry.find('journal_ref').text if entry.find('journal_ref') else 'N/A'
            
            # Write abstract and additional information to text file
            abstract_path = download_to / f"{pdf_name}_abstract.txt"
            with abstract_path.open('w', encoding='utf-8') as abstract_file:
                abstract_file.write(f"Title: {title}\n")
                abstract_file.write(f"Authors: {authors}\n")
                abstract_file.write(f"Affiliations: {affiliations}\n")
                abstract_file.write(f"Abstract: {abstract}\n")
                abstract_file.write(f"Published Date: {published_date}\n")
                abstract_file.write(f"Journal/Conference: {journal_ref}\n")

            # Download PDF
            pdf_response = requests.get(pdf_url)
            with pdf_path.open('wb') as pdf_file:
                pdf_file.write(pdf_response.content)

            # Append to HTML output
            html_output += f"""
<div>
<h2>{title}</h2>
<p><strong>Authors:</strong> {authors}</p>
<p><strong>Affiliations:</strong> {affiliations}</p>
<p><strong>Abstract:</strong> {abstract}</p>
<p><strong>Published Date:</strong> {published_date}</p>
<p><strong>Journal/Conference:</strong> {journal_ref}</p>
<p><a href="{pdf_url}" target="_blank">PDF Link</a></p>
<p><a href="{local_url}" target="_blank">Local PDF</a></p>
</div>
            """
            # Append to report content
            report_content += f"""
Title: {title}
Authors: {authors}
Affiliations: {affiliations}
Abstract: {abstract}
Published Date: {published_date}
Journal/Conference: {journal_ref}
PDF Link: {pdf_url}
Local PDF: {local_url}
------------------------
            """
            # Append to pdf_info dict
            pdf_info[pdf_name] = {
                "title": title,
                "authors": authors,
                "affiliations": affiliations,
                "abstract": abstract,
                "published_date": published_date,
                "journal_ref": journal_ref,
                "pdf_url": pdf_url,
                "local_url": local_url
            }
        
        # Save the report to a text file
        report_path = download_to / "pdf_search_report.txt"
        with report_path.open('w', encoding='utf-8') as report_file:
            report_file.write(report_content)
        
        html_output += "</body></html>"
        return html_output, pdf_info

    except Exception as e:
        return trace_exception(e), {}

# Metadata function
def arxiv_pdf_search_function(client: Optional[Any] = None):
    return {
        "function_name": "arxiv_pdf_search",  # The function name in string
        "function": partial(arxiv_pdf_search, client=client),  # The function to be called with partial to preset client
        "function_description": "Searches for PDFs on arXiv based on a query, downloads them to a specified directory, and returns a HTML string containing article details and links, along with a dictionary containing detailed information about each PDF.",  # Description of the function
        "function_parameters": [  # The set of parameters
            {"name": "query", "type": "str", "description": "The search query for arXiv."},
            {"name": "max_results", "type": "int", "description": "The maximum number of results to return. (Optional)", "optional": True, "default": 5},
            {"name": "sort_by", "type": "str", "description": "The sorting criteria for the search results (e.g., relevance, lastUpdatedDate). (Optional)", "optional": True, "default": "relevance"},
            {"name": "start_date", "type": "str", "description": "The start date for the search results in the format YYYY-MM-DD. (Optional)", "optional": True},
            {"name": "end_date", "type": "str", "description": "The end date for the search results in the format YYYY-MM-DD. (Optional)", "optional": True},
            {"name": "author", "type": "str", "description": "The author name for the search results. (Optional)", "optional": True},
        ]
    }

# Core function to search for PDFs on HAL and download them to a specified directory
def hal_pdf_search(query: str, max_results: Optional[int] = 5, sort_by: Optional[str] = 'relevance', start_date: Optional[str] = None, end_date: Optional[str] = None, author: Optional[str] = None, client: Optional[Any] = None) -> (str, Dict[str, Any]):
    try:
        if client is None:
            download_to = Path("./pdf_search")
        else:
            download_to = client.discussion.discussion_folder / "pdf_search"
        
        # Construct the search URL with additional parameters
        url = f'https://api.archives-ouvertes.fr/search/?q={query}&rows={max_results}&sort={sort_by}'
        if start_date:
            url += f'&fq=submittedDate:[{start_date} TO {end_date if end_date else "*"}]'
        if author:
            url += f'&fq=authIdHal_s:{author}'
        
        ASCIIColors.multicolor(["URL:",url],[ASCIIColors.red, ASCIIColors.yellow])
        response = requests.get(url)
        response.raise_for_status()

        # Parse the response
        soup = BeautifulSoup(response.content, 'xml')
        entries = soup.find_all('doc')

        # Create the directory if it doesn't exist
        download_to.mkdir(parents=True, exist_ok=True)

        # Extract PDF URLs and additional information
        html_output = "<html><body>"
        report_content = ""
        pdf_info = {}
        for entry in entries:
            pdf_url = entry.find('str', {'name': 'fileMain_s'}).text
            pdf_name = pdf_url.split('/')[-1]
            pdf_path = download_to / pdf_name

            if client is None:
                local_url = f'/discussions/pdf_search/{pdf_name}'
            else:
                local_url = discussion_path_to_url(pdf_path)

            # Extract additional information
            title = entry.find('str', {'name': 'title_s'}).text
            authors = ', '.join(author.text for author in entry.find_all('str', {'name': 'authFullName_s'}))
            abstract = entry.find('str', {'name': 'abstract_s'}).text if entry.find('str', {'name': 'abstract_s'}) else 'N/A'
            published_date = entry.find('date', {'name': 'producedDate_tdate'}).text
            journal_ref = entry.find('str', {'name': 'journalTitle_s'}).text if entry.find('str', {'name': 'journalTitle_s'}) else 'N/A'
            
            # Write abstract and additional information to text file
            abstract_path = download_to / f"{pdf_name}_abstract.txt"
            with abstract_path.open('w', encoding='utf-8') as abstract_file:
                abstract_file.write(f"Title: {title}\n")
                abstract_file.write(f"Authors: {authors}\n")
                abstract_file.write(f"Abstract: {abstract}\n")
                abstract_file.write(f"Published Date: {published_date}\n")
                abstract_file.write(f"Journal/Conference: {journal_ref}\n")

            # Download PDF
            pdf_response = requests.get(pdf_url)
            with pdf_path.open('wb') as pdf_file:
                pdf_file.write(pdf_response.content)

            # Append to HTML output
            html_output += f"""
<div>
<h2>{title}</h2>
<p><strong>Authors:</strong> {authors}</p>
<p><strong>Abstract:</strong> {abstract}</p>
<p><strong>Published Date:</strong> {published_date}</p>
<p><strong>Journal/Conference:</strong> {journal_ref}</p>
<p><a href="{pdf_url}" target="_blank">PDF Link</a></p>
<p><a href="{local_url}" target="_blank">Local PDF</a></p>
</div>
            """
            # Append to report content
            report_content += f"""
Title: {title}
Authors: {authors}
Abstract: {abstract}
Published Date: {published_date}
Journal/Conference: {journal_ref}
PDF Link: {pdf_url}
Local PDF: {local_url}
------------------------
            """
            # Append to pdf_info dict
            pdf_info[pdf_name] = {
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "published_date": published_date,
                "journal_ref": journal_ref,
                "pdf_url": pdf_url,
                "local_url": local_url
            }
        
        # Save the report to a text file
        report_path = download_to / "pdf_search_report.txt"
        with report_path.open('w', encoding='utf-8') as report_file:
            report_file.write(report_content)
        
        html_output += "</body></html>"
        return html_output, pdf_info

    except Exception as e:
        return trace_exception(e), {}

# Metadata function
def hal_pdf_search_function(client: Optional[Any] = None):
    return {
        "function_name": "hal_pdf_search",  # The function name in string
        "function": partial(hal_pdf_search, client=client),  # The function to be called with partial to preset client
        "function_description": "Searches for PDFs on HAL based on a query, downloads them to a specified directory, and returns a HTML string containing article details and links, along with a dictionary containing detailed information about each PDF.",  # Description of the function
        "function_parameters": [  # The set of parameters
            {"name": "query", "type": "str", "description": "The search query for HAL."},
            {"name": "max_results", "type": "int", "description": "The maximum number of results to return. (Optional)", "optional": True, "default": 5},
            {"name": "sort_by", "type": "str", "description": "The sorting criteria for the search results (e.g., relevance, lastUpdatedDate). (Optional)", "optional": True, "default": "relevance"},
            {"name": "start_date", "type": "str", "description": "The start date for the search results in the format YYYY-MM-DD. (Optional)", "optional": True},
            {"name": "end_date", "type": "str", "description": "The end date for the search results in the format YYYY-MM-DD. (Optional)", "optional": True},
            {"name": "author", "type": "str", "description": "The author name for the search results. (Optional)", "optional": True},
        ]
    }

# Core function to search for PDFs on ResearchGate and download them to a specified directory
def researchgate_pdf_search(query: str, max_results: Optional[int] = 5, sort_by: Optional[str] = 'relevance', start_date: Optional[str] = None, end_date: Optional[str] = None, author: Optional[str] = None, client: Optional[Any] = None) -> (str, Dict[str, Any]):
    try:
        if client is None:
            download_to = Path("./pdf_search")
        else:
            download_to = client.discussion.discussion_folder / "pdf_search"
        
        # Construct the search URL with additional parameters
        url = f'https://www.researchgate.net/search/publication?q={query}&limit={max_results}&sort={sort_by}'
        if start_date:
            url += f'&startDate={start_date}'
        if end_date:
            url += f'&endDate={end_date}'
        if author:
            url += f'&author={author}'
        
        ASCIIColors.multicolor(["URL:",url],[ASCIIColors.red, ASCIIColors.yellow])
        response = requests.get(url)
        response.raise_for_status()

        # Parse the response
        soup = BeautifulSoup(response.content, 'html.parser')
        entries = soup.find_all('div', class_='nova-o-stack__item')

        # Create the directory if it doesn't exist
        download_to.mkdir(parents=True, exist_ok=True)

        # Extract PDF URLs and additional information
        html_output = "<html><body>"
        report_content = ""
        pdf_info = {}
        for entry in entries:
            pdf_link_tag = entry.find('a', class_='nova-e-link')
            if not pdf_link_tag:
                continue
            pdf_url = pdf_link_tag['href']
            pdf_name = pdf_url.split('/')[-1] + '.pdf'
            pdf_path = download_to / pdf_name

            if client is None:
                local_url = f'/discussions/pdf_search/{pdf_name}'
            else:
                local_url = discussion_path_to_url(pdf_path)

            # Extract additional information
            title = entry.find('h3', class_='nova-e-text').text.strip()
            authors = ', '.join(author.text.strip() for author in entry.find_all('span', class_='nova-e-text'))
            abstract = entry.find('div', class_='nova-e-text').text.strip() if entry.find('div', class_='nova-e-text') else 'N/A'
            published_date = entry.find('span', class_='nova-e-text--size-s').text.strip() if entry.find('span', class_='nova-e-text--size-s') else 'N/A'
            journal_ref = entry.find('span', class_='nova-e-text--size-s').text.strip() if entry.find('span', class_='nova-e-text--size-s') else 'N/A'
            
            # Write abstract and additional information to text file
            abstract_path = download_to / f"{pdf_name}_abstract.txt"
            with abstract_path.open('w', encoding='utf-8') as abstract_file:
                abstract_file.write(f"Title: {title}\n")
                abstract_file.write(f"Authors: {authors}\n")
                abstract_file.write(f"Abstract: {abstract}\n")
                abstract_file.write(f"Published Date: {published_date}\n")
                abstract_file.write(f"Journal/Conference: {journal_ref}\n")

            # Download PDF
            pdf_response = requests.get(pdf_url)
            with pdf_path.open('wb') as pdf_file:
                pdf_file.write(pdf_response.content)

            # Append to HTML output
            html_output += f"""
<div>
<h2>{title}</h2>
<p><strong>Authors:</strong> {authors}</p>
<p><strong>Abstract:</strong> {abstract}</p>
<p><strong>Published Date:</strong> {published_date}</p>
<p><strong>Journal/Conference:</strong> {journal_ref}</p>
<p><a href="{pdf_url}" target="_blank">PDF Link</a></p>
<p><a href="{local_url}" target="_blank">Local PDF</a></p>
</div>
            """
            # Append to report content
            report_content += f"""
Title: {title}
Authors: {authors}
Abstract: {abstract}
Published Date: {published_date}
Journal/Conference: {journal_ref}
PDF Link: {pdf_url}
Local PDF: {local_url}
------------------------
            """
            # Append to pdf_info dict
            pdf_info[pdf_name] = {
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "published_date": published_date,
                "journal_ref": journal_ref,
                "pdf_url": pdf_url,
                "local_url": local_url
            }
        
        # Save the report to a text file
        report_path = download_to / "pdf_search_report.txt"
        with report_path.open('w', encoding='utf-8') as report_file:
            report_file.write(report_content)
        
        html_output += "</body></html>"
        return html_output, pdf_info

    except Exception as e:
        return trace_exception(e), {}

# Metadata function
def researchgate_pdf_search_function(client: Optional[Any] = None):
    return {
        "function_name": "researchgate_pdf_search",  # The function name in string
        "function": partial(researchgate_pdf_search, client=client),  # The function to be called with partial to preset client
        "function_description": "Searches for PDFs on ResearchGate based on a query, downloads them to a specified directory, and returns a HTML string containing article details and links, along with a dictionary containing detailed information about each PDF.",  # Description of the function
        "function_parameters": [  # The set of parameters
            {"name": "query", "type": "str", "description": "The search query for ResearchGate."},
            {"name": "max_results", "type": "int", "description": "The maximum number of results to return. (Optional)", "optional": True, "default": 5},
            {"name": "sort_by", "type": "str", "description": "The sorting criteria for the search results (e.g., relevance, lastUpdatedDate). (Optional)", "optional": True, "default": "relevance"},
            {"name": "start_date", "type": "str", "description": "The start date for the search results in the format YYYY-MM-DD. (Optional)", "optional": True},
            {"name": "end_date", "type": "str", "description": "The end date for the search results in the format YYYY-MM-DD. (Optional)", "optional": True},
            {"name": "author", "type": "str", "description": "The author name for the search results. (Optional)", "optional": True},
        ]
    }

# Define the core function
def rate_relevance(search_prompt: str, text_example: str, llm) -> Tuple[str, Dict[str, float]]:
    try:
        # Use the LLM to rate the relevance of the text example compared to the search prompt
        relevance_score = llm.fast_gen(f"Rate the relevance of the following text compared to the prompt on a scale of 0 to 1. Only respond with a number between 0 and 1:\nPrompt: {search_prompt}\nText: {text_example}\nRelevance score:")

        # Extract the relevance score from the generated text
        try:
            score = float(relevance_score.strip())
        except ValueError:
            score = 0.0  # Default score in case of parsing issues

        # Create the output tuple
        result = (f"Relevance Score: {score}", {"score": score})

        return result
    except Exception as e:
        return trace_exception(e)

# Define the metadata function
def rate_relevance_function(llm):
    return {
        "function_name": "rate_relevance",  # The function name in string
        "function": partial(rate_relevance, llm=llm),  # The function to be called with LLM as a preset parameter
        "function_description": "Rates the relevance of a text example compared to a search prompt using an LLM.",  # Description
        "function_parameters": [
            {"name": "search_prompt", "type": "str"},
            {"name": "text_example", "type": "str"}
        ]  # The set of parameters
    }



# Example usage
if __name__ == "__main__":
    # Example client initialization (if needed)
    client = None  # Replace with actual client initialization if available

    # Example function call
    html_output = arxiv_pdf_search(
        query="machine learning",
        max_results=3,
        sort_by="relevance",
        start_date="2020-01-01",
        end_date="2021-01-01",
        author="John Doe",
        client=client
    )

    # Print the HTML output
    print(html_output)



# Core function to search for PDFs on arXiv and download them to a specified directory
def search_and_rank(llm, search_subject:str, score_threshold:float, query: str, max_results: Optional[int] = 5, sort_by: Optional[str] = 'relevance', start_date: Optional[str] = None, end_date: Optional[str] = None, author: Optional[str] = None, client: Optional[Any] = None) -> (str, Dict[str, Any]):
    try:

        if client is None:
            download_to = Path("./pdf_search")
        else:
            download_to = client.discussion.discussion_folder / "pdf_search"
        
        # Construct the search URL with additional parameters
        url = f'http://export.arxiv.org/api/query?search_query={query}&start=0&max_results={max_results}&sortBy={sort_by}'
        if start_date:
            url += f'&startDate={start_date}'
        if end_date:
            url += f'&endDate={end_date}'
        if author:
            url += f'&author={author}'
        
        response = requests.get(url)
        response.raise_for_status()

        # Parse the response
        soup = BeautifulSoup(response.content, 'xml')
        entries = soup.find_all('entry')

        # Create the directory if it doesn't exist
        download_to.mkdir(parents=True, exist_ok=True)

        # Extract PDF URLs and additional information
        html_output = "<html><body>"
        report_content = ""
        pdf_info = {}
        for entry in entries:
            pdf_url = entry.id.text.replace('abs', 'pdf') + '.pdf'
            pdf_name = pdf_url.split('/')[-1]
            pdf_path = download_to / pdf_name

            if client is None:
                local_url = f'/discussions/pdf_search/{pdf_name}'
            else:
                local_url = discussion_path_to_url(pdf_path)

            # Extract additional information
            title = entry.title.text
            authors = ', '.join(author.find('name').text for author in entry.find_all('author'))
            affiliations = ', '.join(affiliation.text for affiliation in entry.find_all('affiliation'))
            abstract = entry.summary.text
            published_date = entry.published.text
            journal_ref = entry.find('journal_ref').text if entry.find('journal_ref') else 'N/A'

            # Use the LLM to rate the relevance of the text example compared to the search prompt
            relevance_score = llm.fast_gen(f"Rate the relevance of the following text compared to the prompt on a scale of 0 to 1. Only respond with a number between 0 and 1:\nPrompt: {search_subject}\nText: {abstract}\nRelevance score:")

            # Extract the relevance score from the generated text
            try:
                score = float(relevance_score.strip())
            except ValueError:
                score = 0.0  # Default score in case of parsing issues

            if score<score_threshold: # drop irrelevant scores
                continue

            # Create the output tuple
            result = (f"Relevance Score: {score}", {"score": score})

            # Write abstract and additional information to text file
            abstract_path = download_to / f"{pdf_name}_abstract.txt"
            with abstract_path.open('w', encoding='utf-8') as abstract_file:
                abstract_file.write(f"Title: {title}\n")
                abstract_file.write(f"Authors: {authors}\n")
                abstract_file.write(f"Affiliations: {affiliations}\n")
                abstract_file.write(f"Abstract: {abstract}\n")
                abstract_file.write(f"Published Date: {published_date}\n")
                abstract_file.write(f"Journal/Conference: {journal_ref}\n")
                abstract_file.write(f"Relevance score: {score}\n")

            # Download PDF
            pdf_response = requests.get(pdf_url)
            with pdf_path.open('wb') as pdf_file:
                pdf_file.write(pdf_response.content)

            # Append to HTML output
            html_output += f"""
<div>
<h2>{title}</h2>
<p><strong>Authors:</strong> {authors}</p>
<p><strong>Affiliations:</strong> {affiliations}</p>
<p><strong>Abstract:</strong> {abstract}</p>
<p><strong>Published Date:</strong> {published_date}</p>
<p><strong>Journal/Conference:</strong> {journal_ref}</p>
<p><strong>Relevance score:</strong> {score}</p>
<p><a href="{pdf_url}" target="_blank">PDF Link</a></p>
<p><a href="{local_url}" target="_blank">Local PDF</a></p>
</div>
            """
            # Append to report content
            report_content += f"""
Title: {title}
Authors: {authors}
Affiliations: {affiliations}
Abstract: {abstract}
Published Date: {published_date}
Journal/Conference: {journal_ref}
Relevance score: {score}
PDF Link: {pdf_url}
Local PDF: {local_url}
------------------------
            """
            # Append to pdf_info dict
            pdf_info[pdf_name] = {
                "title": title,
                "authors": authors,
                "affiliations": affiliations,
                "abstract": abstract,
                "published_date": published_date,
                "journal_ref": journal_ref,
                "pdf_url": pdf_url,
                "local_url": local_url
            }
        
        # Save the report to a text file
        report_path = download_to / "pdf_search_report.txt"
        with report_path.open('w', encoding='utf-8') as report_file:
            report_file.write(report_content)
        
        html_output += "</body></html>"
        return html_output, pdf_info

    except Exception as e:
        return trace_exception(e), {}

# Metadata function
def search_and_rank_function(llm, score_threshold:float, client: Optional[Any] = None):
    return {
        "function_name": "search_and_rank",  # The function name in string
        "function": partial(search_and_rank, llm=llm, client=client, score_threshold= score_threshold),  # The function to be called with partial to preset client
        "function_description": "Searches for PDFs on arXiv based on a query, downloads them to a specified directory, rates them, sort them by rating and returns a HTML string containing article details and links, along with a dictionary containing detailed information about each PDF.",  # Description of the function
        "function_parameters": [  # The set of parameters
            {"name": "search_subject", "type": "str", "description": "The search subject."},
            {"name": "query", "type": "str", "description": "The search query for arXiv."},
            {"name": "max_results", "type": "int", "description": "The maximum number of results to return. (Optional)", "optional": True, "default": 5},
            {"name": "sort_by", "type": "str", "description": "The sorting criteria for the search results (e.g., relevance, lastUpdatedDate). (Optional)", "optional": True, "default": "relevance"},
            {"name": "start_date", "type": "str", "description": "The start date for the search results in the format YYYY-MM-DD. (Optional)", "optional": True},
            {"name": "end_date", "type": "str", "description": "The end date for the search results in the format YYYY-MM-DD. (Optional)", "optional": True},
            {"name": "author", "type": "str", "description": "The author name for the search results. (Optional)", "optional": True},
        ]
    }
