from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple, Callable
import json
import time
import re
import urllib.parse

from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails
from ascii_colors import ASCIIColors, trace_exception
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig

# Ensuring required packages are installed
import pipmaster as pm
for package in ["requests", "bs4", "arxiv", "wikipedia", "duckduckgo_search"]:
    if not pm.is_installed(package):
        pm.install(package)

import requests
from bs4 import BeautifulSoup
import arxiv
import wikipedia
from duckduckgo_search import DDGS


class DeepSearch(FunctionCall):
    """
    A function that performs deep internet searches across multiple engines,
    iteratively analyzing results and performing follow-up searches until
    sufficient information is gathered to answer the user's query.
    """
    
    def __init__(self, app: LollmsApplication, client: Client):
        # Define static parameters for the function
        static_parameters = TypedConfig(
            ConfigTemplate([
                {
                    "name": "api_keys",
                    "type": "str",
                    "value": json.dumps({"google": "", "bing": "", "serp": ""}),
                    "help": "JSON string containing API keys for various search engines"
                },
                {
                    "name": "default_engine",
                    "type": "str",
                    "value": "ddg",
                    "options": ["ddg", "wikipedia", "arxiv", "google", "bing", "serp", "scholar"],
                    "help": "Default search engine to use when none specified"
                },
                {
                    "name": "free_engines",
                    "type": "str",
                    "value": json.dumps(["ddg", "wikipedia", "arxiv"]),
                    "help": "JSON list of engines that don't require API keys"
                },
                {
                    "name": "paid_engines",
                    "type": "str",
                    "value": json.dumps(["google", "bing", "serp", "scholar"]),
                    "help": "JSON list of engines that require API keys"
                }
            ])
        )
        
        # Initialize the function call
        super().__init__("deep_search", app, FunctionType.CONTEXT_UPDATE, client, static_parameters)
        
        # Setup class attributes
        self.personality = app.personality
        self.search_engines = {
            "ddg": self._search_ddg,
            "google": self._search_google,
            "bing": self._search_bing,
            "wikipedia": self._search_wikipedia,
            "arxiv": self._search_arxiv,
            "scholar": self._search_scholar,
            "serp": self._search_serp
        }
        
        # Parse static parameters
        try:
            self.api_keys = json.loads(self.static_parameters.api_keys)
        except json.JSONDecodeError:
            self.api_keys = {"google": "", "bing": "", "serp": ""}
            
        try:
            self.free_engines = json.loads(self.static_parameters.free_engines)
        except json.JSONDecodeError:
            self.free_engines = ["ddg", "wikipedia", "arxiv"]
            
        try:
            self.paid_engines = json.loads(self.static_parameters.paid_engines)
        except json.JSONDecodeError:
            self.paid_engines = ["google", "bing", "serp", "scholar"]
            
        self.default_engine = self.static_parameters.default_engine
        
        # Setup logging directory
        self.log_dir = app.lollms_paths.personal_outputs_path / "deep_search_logs"
        self.log_dir.mkdir(exist_ok=True, parents=True)

    def update_context(self, context: LollmsContextDetails, constructed_context: List[str]) -> List[str]:
        """
        Update the context with deep search results based on user query.
        
        Args:
            context: The current context details
            constructed_context: The context being constructed
            
        Returns:
            The updated constructed context with search results
        """
        try:
            # Extract parameters from the function call
            parameters = self.extract_parameters(context)
            query = parameters.get("query", "")
            engine = parameters.get("engine", self.default_engine)
            max_iterations = int(parameters.get("max_iterations", 3))
            depth = int(parameters.get("depth", 5))
            timeout = int(parameters.get("timeout", 30))
            
            if not query:
                # Try to extract query from the last user message
                if context.discussion_messages and len(context.discussion_messages) > 0:
                    last_user_msg = [m for m in reversed(context.discussion_messages) if m["role"] == "user"]
                    if last_user_msg:
                        query = last_user_msg[0]["content"]
            
            if not query:
                constructed_context.append("ERROR: No search query provided")
                return constructed_context
                
            # Log the start of search process
            search_log = f"Deep Search for: {query}\n"
            search_log += f"Engine: {engine}, Max Iterations: {max_iterations}, Depth: {depth}\n"
            search_log += "="*50 + "\n\n"
            
            constructed_context.append(f"[Deep searching for information about: {query}]")
            
            # Validate engine selection
            if engine not in self.search_engines:
                available_engines = list(self.search_engines.keys())
                constructed_context.append(f"ERROR: Invalid search engine '{engine}'. Available engines: {', '.join(available_engines)}")
                return constructed_context
                
            # Check if engine requires API key and if it's available
            if engine in self.paid_engines and not self.api_keys.get(engine):
                constructed_context.append(f"ERROR: The {engine} search engine requires an API key which is not configured.")
                return constructed_context
            
            # Perform the iterative search
            all_results = []
            iteration_summaries = []
            current_query = query
            
            for iteration in range(max_iterations):
                # Log the current iteration
                search_log += f"Iteration {iteration+1}, Query: {current_query}\n"
                
                # Get search results
                results = self._perform_search(engine, current_query, depth, timeout)
                if not results:
                    search_log += "No results found for this query.\n\n"
                    break
                    
                all_results.extend(results)
                
                # Combine results for this iteration
                iteration_content = "\n\n".join([f"SOURCE: {r['title']}\nURL: {r['url']}\nCONTENT: {r['content']}" for r in results])
                
                # Log the results
                search_log += f"Found {len(results)} results\n"
                for i, r in enumerate(results):
                    search_log += f"Result {i+1}: {r['title']} ({r['url']})\n"
                
                # Analyze results to determine next steps using the LLM
                analysis_prompt = f"""
                You are analyzing search results for the query: "{query}"
                
                Here are the search results from iteration {iteration+1}:
                
                {iteration_content}
                
                Based on these results, please:
                1. Summarize the key information found (focus on facts, data, and important details)
                2. Identify what information is still missing to fully answer the original query
                3. Suggest a follow-up search query that would help find the missing information
                4. Determine if we have enough information to answer the original query completely (Yes/No)
                
                Format your response as:
                SUMMARY: [key information summary]
                MISSING: [missing information]
                FOLLOW_UP_QUERY: [suggested follow-up query]
                SUFFICIENT: [Yes/No]
                """
                
                with self.personality.sink:
                    analysis = self.personality.fastgen(analysis_prompt)
                
                # Extract components from the analysis
                summary_match = re.search(r"SUMMARY:(.*?)(?:MISSING:|$)", analysis, re.DOTALL)
                missing_match = re.search(r"MISSING:(.*?)(?:FOLLOW_UP_QUERY:|$)", analysis, re.DOTALL)
                follow_up_match = re.search(r"FOLLOW_UP_QUERY:(.*?)(?:SUFFICIENT:|$)", analysis, re.DOTALL)
                sufficient_match = re.search(r"SUFFICIENT:\s*(\w+)", analysis)
                
                summary = summary_match.group(1).strip() if summary_match else "No summary available"
                missing = missing_match.group(1).strip() if missing_match else "Unknown missing information"
                follow_up = follow_up_match.group(1).strip() if follow_up_match else current_query
                sufficient = sufficient_match.group(1).strip().lower() == "yes" if sufficient_match else False
                
                iteration_summaries.append(summary)
                
                # Log the analysis
                search_log += f"\nAnalysis:\n{analysis}\n"
                search_log += "="*30 + "\n\n"
                
                # Check if we have enough information
                if sufficient or iteration == max_iterations - 1:
                    search_log += "Search complete: Sufficient information found or maximum iterations reached.\n"
                    break
                    
                # Update query for next iteration
                current_query = follow_up
            
            # Final synthesis of all gathered information
            synthesis_prompt = """
            You are synthesizing information gathered from a deep search on: "{}"
            
            Here are summaries from each search iteration:
            
            {}
            
            Please create a comprehensive, well-organized summary of all the information found.
            Focus on providing accurate, relevant, and complete information that addresses the original query.
            Include key facts, data points, and context that would be most helpful to the user.
            """.format(query, "\n\n".join([f"ITERATION {i+1}:\n{summary}" for i, summary in enumerate(iteration_summaries)]))
            
            with self.personality.sink:
                final_synthesis = self.personality.fastgen(synthesis_prompt)
            
            # Save the search log
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            sanitized_query = "".join(c if c.isalnum() else "_" for c in query[:30])
            log_file = self.log_dir / f"search_{sanitized_query}_{timestamp}.txt"
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(search_log)
                f.write("\n\nFINAL SYNTHESIS:\n")
                f.write(final_synthesis)
            
            # Add the results to the context
            constructed_context.append("\n\n[Deep Search Results]\n")
            constructed_context.append(final_synthesis)
            constructed_context.append(f"\n[Based on {len(all_results)} sources from {engine} search]")
            
            # Add detailed sources as reference
            sources_text = "\n\nSources consulted:\n"
            unique_sources = {}
            for result in all_results:
                if result['url'] not in unique_sources:
                    unique_sources[result['url']] = result['title']
                    
            for i, (url, title) in enumerate(unique_sources.items()):
                sources_text += f"{i+1}. {title} - {url}\n"
                
            constructed_context.append(sources_text)
            
            return constructed_context
            
        except Exception as e:
            trace_exception(e)
            constructed_context.append(f"ERROR: An error occurred during deep search: {str(e)}")
            return constructed_context

    def process_output(self, context: LollmsContextDetails, llm_output: str) -> str:
        """
        Process the output from the LLM after context has been updated.
        
        Args:
            context: The context details
            llm_output: The output generated by the LLM
            
        Returns:
            Potentially modified LLM output
        """
        # We don't need to modify the output, but we could add post-processing if needed
        return llm_output

    def _perform_search(self, engine: str, query: str, depth: int, timeout: int) -> List[Dict[str, str]]:
        """
        Perform a search using the specified engine.
        
        Args:
            engine: The search engine to use
            query: The search query
            depth: Number of results to retrieve
            timeout: Search timeout in seconds
            
        Returns:
            List of search results as dictionaries with 'title', 'url', and 'content' keys
        """
        if engine not in self.search_engines:
            return []
            
        search_func = self.search_engines[engine]
        try:
            return search_func(query, depth, timeout)
        except Exception as e:
            ASCIIColors.warning(f"Search error with {engine}: {str(e)}")
            return []

    def _search_ddg(self, query: str, depth: int, timeout: int) -> List[Dict[str, str]]:
        """Search using DuckDuckGo."""
        results = []
        try:
            with DDGS() as ddgs:
                search_results = list(ddgs.text(query, max_results=depth))
                
            for result in search_results:
                # Extract relevant text from the webpage if possible
                content = self._extract_content_from_url(result.get('href', ''), timeout)
                results.append({
                    'title': result.get('title', 'No Title'),
                    'url': result.get('href', ''),
                    'content': content or result.get('body', 'No content available')
                })
        except Exception as e:
            ASCIIColors.warning(f"DDG search error: {str(e)}")
        
        return results

    def _search_google(self, query: str, depth: int, timeout: int) -> List[Dict[str, str]]:
        """Search using Google Custom Search API."""
        api_key = self.api_keys.get("google", "")
        if not api_key:
            return []
            
        results = []
        try:
            # Google Custom Search API endpoint
            cx = "YOUR_CUSTOM_SEARCH_ENGINE_ID"  # This should ideally be in static params
            url = f"https://www.googleapis.com/customsearch/v1"
            
            params = {
                "key": api_key,
                "cx": cx,
                "q": query,
                "num": depth
            }
            
            response = requests.get(url, params=params, timeout=timeout)
            data = response.json()
            
            if "items" in data:
                for item in data["items"]:
                    content = self._extract_content_from_url(item.get("link", ""), timeout)
                    results.append({
                        "title": item.get("title", "No Title"),
                        "url": item.get("link", ""),
                        "content": content or item.get("snippet", "No content available")
                    })
        except Exception as e:
            ASCIIColors.warning(f"Google search error: {str(e)}")
            
        return results

    def _search_bing(self, query: str, depth: int, timeout: int) -> List[Dict[str, str]]:
        """Search using Bing Search API."""
        api_key = self.api_keys.get("bing", "")
        if not api_key:
            return []
            
        results = []
        try:
            headers = {
                "Ocp-Apim-Subscription-Key": api_key,
                "Content-Type": "application/json"
            }
            
            search_url = "https://api.bing.microsoft.com/v7.0/search"
            params = {
                "q": query,
                "count": depth,
                "responseFilter": "Webpages"
            }
            
            response = requests.get(search_url, headers=headers, params=params, timeout=timeout)
            data = response.json()
            
            if "webPages" in data and "value" in data["webPages"]:
                for result in data["webPages"]["value"]:
                    content = self._extract_content_from_url(result.get("url", ""), timeout)
                    results.append({
                        "title": result.get("name", "No Title"),
                        "url": result.get("url", ""),
                        "content": content or result.get("snippet", "No content available")
                    })
        except Exception as e:
            ASCIIColors.warning(f"Bing search error: {str(e)}")
            
        return results

    def _search_wikipedia(self, query: str, depth: int, timeout: int) -> List[Dict[str, str]]:
        """Search using Wikipedia API."""
        results = []
        try:
            # Search Wikipedia
            search_results = wikipedia.search(query, results=depth)
            
            # Get content for each result
            for title in search_results:
                try:
                    page = wikipedia.page(title, auto_suggest=False)
                    content = page.content[:10000]  # Limit content length
                    results.append({
                        "title": page.title,
                        "url": page.url,
                        "content": content
                    })
                except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError) as e:
                    continue  # Skip problematic pages
        except Exception as e:
            ASCIIColors.warning(f"Wikipedia search error: {str(e)}")
            
        return results

    def _search_arxiv(self, query: str, depth: int, timeout: int) -> List[Dict[str, str]]:
        """Search using arXiv API."""
        results = []
        try:
            search = arxiv.Search(
                query=query,
                max_results=depth,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            for paper in search.results():
                results.append({
                    "title": paper.title,
                    "url": paper.pdf_url,
                    "content": f"Authors: {', '.join(a for a in paper.authors)}\nPublished: {paper.published}\nSummary: {paper.summary}"
                })
        except Exception as e:
            ASCIIColors.warning(f"arXiv search error: {str(e)}")
            
        return results

    def _search_scholar(self, query: str, depth: int, timeout: int) -> List[Dict[str, str]]:
        """Search using Google Scholar (via SerpAPI)."""
        api_key = self.api_keys.get("serp", "")
        if not api_key:
            return []
            
        results = []
        try:
            url = "https://serpapi.com/search"
            params = {
                "engine": "google_scholar",
                "q": query,
                "api_key": api_key,
                "num": depth
            }
            
            response = requests.get(url, params=params, timeout=timeout)
            data = response.json()
            
            if "organic_results" in data:
                for result in data["organic_results"]:
                    link = result.get("link", "")
                    content = self._extract_content_from_url(link, timeout) if link else ""
                    
                    results.append({
                        "title": result.get("title", "No Title"),
                        "url": link,
                        "content": content or f"Publication: {result.get('publication_info', {}).get('summary', 'Unknown')}\nSummary: {result.get('snippet', 'No summary available')}"
                    })
        except Exception as e:
            ASCIIColors.warning(f"Google Scholar search error: {str(e)}")
            
        return results

    def _search_serp(self, query: str, depth: int, timeout: int) -> List[Dict[str, str]]:
        """Search using SerpAPI general search."""
        api_key = self.api_keys.get("serp", "")
        if not api_key:
            return []
            
        results = []
        try:
            url = "https://serpapi.com/search"
            params = {
                "engine": "google",
                "q": query,
                "api_key": api_key,
                "num": depth
            }
            
            response = requests.get(url, params=params, timeout=timeout)
            data = response.json()
            
            if "organic_results" in data:
                for result in data["organic_results"]:
                    link = result.get("link", "")
                    content = self._extract_content_from_url(link, timeout) if link else ""
                    
                    results.append({
                        "title": result.get("title", "No Title"),
                        "url": link,
                        "content": content or result.get("snippet", "No content available")
                    })
        except Exception as e:
            ASCIIColors.warning(f"SERP search error: {str(e)}")
            
        return results

    def _extract_content_from_url(self, url: str, timeout: int) -> str:
        """
        Extract the main content from a URL.
        
        Args:
            url: The URL to extract content from
            timeout: Request timeout in seconds
            
        Returns:
            Extracted text content or empty string if extraction fails
        """
        if not url or not url.startswith(('http://', 'https://')):
            return ""
            
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # Check if content type is HTML
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type:
                return ""
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script_or_style in soup(['script', 'style', 'header', 'footer', 'nav']):
                script_or_style.decompose()
                
            # Extract text and clean it
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit text length
            return text[:5000]
            
        except Exception as e:
            ASCIIColors.warning(f"URL content extraction error for {url}: {str(e)}")
            return ""

    def extract_parameters(self, context: LollmsContextDetails) -> Dict[str, Any]:
        """
        Extract parameters from the function call in the context.
        
        Args:
            context: The context details
            
        Returns:
            Dictionary of function parameters
        """
        parameters = {}
        
        # Try to extract from function call format
        if context.discussion_messages:
            last_messages = [m for m in reversed(context.discussion_messages) if m["role"] == "user"]
            if last_messages:
                content = last_messages[0]["content"]
                
                # Check for function call pattern
                match = re.search(r"deep_search\s*\(\s*(.*?)\s*\)", content, re.DOTALL)
                if match:
                    param_str = match.group(1)
                    # Extract key=value pairs
                    for pair in re.finditer(r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|(\S+))', param_str):
                        key = pair.group(1)
                        # Get the first non-None group from the alternatives
                        value = next((g for g in pair.group(2, 3, 4) if g is not None), "")
                        parameters[key] = value
        
        return parameters

# Register the function call
def register_function_call(app: LollmsApplication, client: Client):
    app.register_function(DeepSearch(app, client))