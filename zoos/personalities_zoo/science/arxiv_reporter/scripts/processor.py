import subprocess
import sys
from pathlib import Path
from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails
from typing import Callable
import arxiv

class Processor(APScript):
    def __init__(self, personality: AIPersonality, callback: Callable = None) -> None:
        # Define dynamic configuration for user-adjustable settings
        personality_config_template = ConfigTemplate(
            [
                {"name": "max_articles", "type": "int", "value": 5, "min": 1, "max": 20, "help": "Maximum number of articles to retrieve and include in the report."},
            ]
        )
        personality_config_vals = BaseConfig.from_template(personality_config_template)
        personality_config = TypedConfig(personality_config_template, personality_config_vals)
        super().__init__(personality, personality_config, callback=callback)

    def install(self):
        """Install dependencies from requirements.txt."""
        super().install()
        requirements_file = self.personality.personality_package_path / "requirements.txt"
        if requirements_file.exists():
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])

    def run_workflow(self, context_details: LollmsContextDetails, client: Client = None, callback: Callable = None):
        """Handle user input: search ArXiv or chat."""
        prompt = context_details.prompt.strip()

        # Use yes_no to determine if this is a search request
        is_search_request = self.yes_no(
            question="Is this a search request? Answer with 'yes' or 'no'.",
            context=prompt,
            conditionning="""
You are ArXiv Reporter, an AI assistant that can search ArXiv for research articles or engage in conversation.
Determine if the user's message is a request to search for articles on ArXiv.
Examples of search requests:
- "search quantum computing"
- "find articles on machine learning"
- "look up papers about neural networks"
- "Can you find recent papers on quantum computing?"
Examples of non-search requests:
- "what is quantum computing?"
- "tell me about ArXiv"
- "how are you?"
"""
        )

        if is_search_request:
            # Generate the search query from the user's prompt
            query_prompt = f"""
You are ArXiv Reporter. Based on the user's message, extract the search query for ArXiv.
The search query should be the keywords or topic the user wants to search for.
Respond with only the search query.

User's message: {prompt}
Search query:
"""
            search_query = self.fast_gen(query_prompt, max_size=50).strip()
            try:
                articles = self.search_arxiv(search_query)
                if not articles:
                    self.set_message_content("No articles found for your query.")
                    return ""
                report = self.generate_report(search_query, articles)
                self.set_message_content(report)
                return report
            except Exception as e:
                self.set_message_content(f"Error searching ArXiv: {str(e)}")
                return ""
        else:
            # Regular conversation with system message
            system_message = """
You are ArXiv Reporter, an AI assistant knowledgeable about research articles on ArXiv.
Respond to the user's message in a helpful and informative way.
"""
            full_context = context_details.get_discussion_to()  # Assuming this method exists to get discussion as a string
            response_prompt = f"{system_message}\n{full_context}\n{prompt}\n{self.personality.ai_message_prefix}:"
            response = self.fast_gen(response_prompt, callback=self.sink)
            self.set_message_content(response)
            return response

    def search_arxiv(self, query):
        """Search ArXiv for articles based on the query."""
        search = arxiv.Search(
            query=query,
            max_results=self.personality_config.max_articles,
            sort_by=arxiv.SortCriterion.Relevance
        )
        return list(search.results())

    def generate_report(self, query, articles):
        """Generate a detailed analysis report from ArXiv articles."""
        article_list = "\n\n".join([
            f"**Title**: {article.title}\n**Authors**: {', '.join(author.name for author in article.authors)}\n**Summary**: {article.summary[:200]}..."
            for article in articles
        ])
        report_prompt_parts = [
            f"""
You are ArXiv Reporter. Analyze the following ArXiv articles related to '{query}'.
Provide a report formatted with markdown, including the following sections:
## Overview
A brief overview of the main topics covered.
## Key Findings
Key findings or contributions from the articles.
## Trends and Patterns
Any notable trends or patterns across the articles.
## Further Research
Potential areas for further research.
\n\n""",
            article_list,
            "\n\nReport:"
        ]
        report_prompt = self.build_prompt(report_prompt_parts, sacrifice_id=1)
        report = self.fast_gen(report_prompt, max_size=2048)
        references = "\n".join([
            f"- [{article.title}]({article.entry_id}) by {', '.join(author.name for author in article.authors)}"
            for article in articles
        ])
        full_report = f"# ArXiv Search Report for '{query}'\n\n{report}\n\n## References\n{references}"
        return full_report

    def sink(self, text):
        """Stream text chunks to the UI."""
        self.add_chunk_to_message_content(text)