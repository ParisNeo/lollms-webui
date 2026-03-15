from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails
from datetime import datetime
import yaml, json
from typing import List, Dict, Optional, Union, Any
from ascii_colors import ASCIIColors, trace_exception
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
from pathlib import Path
import os

import pipmaster as pm
if not pm.is_installed("docling"):
    pm.install("docling")

from docling.document_converter import DocumentConverter

class SummarizeFile(FunctionCall):
    def __init__(self, app: LollmsApplication, client: Client):
        static_parameters = TypedConfig(
            ConfigTemplate([
                # Chunk Processing Options
                {
                    "name": "chunk_processing_format",
                    "type": "str",
                    "value": "bullet points",
                    "options": [
                        "bullet points", 
                        "article meta data", 
                        "paragraph", 
                        "key-value pairs",
                        "json",
                        "yaml",
                        "table",
                        "custom template"
                    ],
                    "help": """Defines how chunks are processed and stored in memory during summarization. 
                    - 'bullet points': List format
                    - 'article meta data': Extracts metadata-like information
                    - 'paragraph': Narrative format
                    - 'key-value pairs': Structured key-value format
                    - 'json': Structured JSON format
                    - 'yaml': YAML format for hierarchical data
                    - 'table': Organized in tabular format
                    - 'custom template': Use custom template specified in chunk_processing_template"""
                },
                {
                    "name": "chunk_processing_template",
                    "type": "text",
                    "value": "",
                    "help": """Custom template for chunk processing when 'custom template' is selected.
                    Example: "## {section_title}\n- Key Points: {points}\n- Entities: {entities}"
                    Use placeholders that the model will populate based on chunk content."""
                },
                {
                    "name": "contextual_summary_information",
                    "type": "text",
                    "value": "",
                    "help": """Custom instructions for filtering or extracting specific information from chunks. 
                    Examples: 'Focus on statistical data', 'Extract only quotes', 'Prioritize conclusions'"""
                },
                
                # Final Summary Options
                {
                    "name": "summary_style",
                    "type": "str",
                    "value": "concise",
                    "options": ["concise", "detailed", "executive", "technical", "creative", "custom"],
                    "help": """Controls the final summary style:
                    - 'concise': Short and to the point
                    - 'detailed': Comprehensive with more context
                    - 'executive': High-level overview for decision-making
                    - 'technical': Focus on technical details
                    - 'creative': More engaging, storytelling approach
                    - 'custom': Use custom template specified in summary_template"""
                },
                {
                    "name": "summary_template",
                    "type": "text",
                    "value": "",
                    "help": """Custom template for final summary when 'custom' style is selected.
                    Example: "# Executive Summary\n## Key Findings\n{findings}\n## Recommendations\n{recommendations}"
                    Use placeholders that the model will populate based on the memory content."""
                },
                {
                    "name": "summary_tone",
                    "type": "str",
                    "value": "neutral",
                    "options": ["neutral", "formal", "informal", "academic", "enthusiastic", "critical", "humorous"],
                    "help": """Sets the tone of the summary:
                    - 'neutral': Balanced and unbiased
                    - 'formal': Professional and structured
                    - 'informal': Conversational and approachable
                    - 'academic': Scholarly and rigorous
                    - 'enthusiastic': Positive and energetic
                    - 'critical': Analytical and evaluative
                    - 'humorous': Light and entertaining"""
                },
                
                # Technical Parameters
                {
                    "name": "context_size",
                    "type": "int",
                    "value": 128000,
                    "min": 1024,
                    "max": 256000,
                    "help": """The maximum context size for the language model."""
                },
                {
                    "name": "chunk_size",
                    "type": "int",
                    "value": 4096,
                    "min": 512,
                    "max": 10000000,
                    "help": """Size of each text chunk to process."""
                },
                {
                    "name": "output_format",
                    "type": "str",
                    "value": "markdown",
                    "options": ["markdown", "html", "plain text", "json", "yaml"],
                    "help": """Format of the final summary output."""
                },
                
                # Presentation Parameters
                {
                    "name": "language_level",
                    "type": "str",
                    "value": "standard",
                    "options": ["simple", "standard", "advanced", "expert"],
                    "help": """Adjusts the complexity of language in the summary:
                    - 'simple': Basic vocabulary, suitable for non-specialists
                    - 'standard': Average readability for general audience
                    - 'advanced': Sophisticated terminology for informed audience
                    - 'expert': Domain-specific terminology for specialists"""
                },
                {
                    "name": "include_timestamps",
                    "type": "bool",
                    "value": False,
                    "help": """If True, adds approximate location references (e.g., 'from page 1') to summary points."""
                },
                {
                    "name": "include_metadata",
                    "type": "bool",
                    "value": True,
                    "help": """If True, includes document metadata (title, author, date) when available."""
                },
                {
                    "name": "include_sections",
                    "type": "bool",
                    "value": True,
                    "help": """If True, organizes summary by document sections when possible."""
                },
                {
                    "name": "highlight_key_findings",
                    "type": "bool",
                    "value": False,
                    "help": """If True, clearly highlights the most important findings or takeaways."""
                },
                
                # Advanced Options
                {
                    "name": "focus_areas",
                    "type": "text",
                    "value": "",
                    "help": """Comma-separated list of specific topics, themes or sections to focus on.
                    Example: "financial data, future projections, market analysis"."""
                },
                {
                    "name": "exclude_areas",
                    "type": "text",
                    "value": "",
                    "help": """Comma-separated list of topics or sections to exclude from summary.
                    Example: "appendices, background information, citations"."""
                },
                {
                    "name": "audience",
                    "type": "str",
                    "value": "general",
                    "options": ["general", "executive", "technical", "academic", "customer", "internal", "custom"],
                    "help": """Target audience for the summary, affecting terminology and focus:
                    - 'general': For broad consumption
                    - 'executive': For decision-makers
                    - 'technical': For engineers/specialists
                    - 'academic': For scholarly contexts
                    - 'customer': For external clients
                    - 'internal': For team members
                    - 'custom': Use custom audience specified in custom_audience"""
                },
                {
                    "name": "custom_audience",
                    "type": "text",
                    "value": "",
                    "help": """Description of custom audience when 'custom' is selected.
                    Example: "Marketing team with limited technical background but strong business focus"."""
                },
            ]),
            BaseConfig(config={})
        )
        super().__init__("summarize_file", app, FunctionType.CLASSIC, client, static_parameters)
        self.personality = app.personality

    def load_file(self, file_path: Path) -> str:
        if file_path.suffix in [".pdf", ".docx", ".pptx", ".html"]:        
            converter = DocumentConverter()
            result = converter.convert(str(file_path))
            file_content = result.document.export_to_markdown()
        elif file_path.suffix in [
            ".txt", ".md", ".markdown", ".c", ".cpp", ".h", ".hpp", ".py", ".python", ".java", ".js", ".jsx", ".ts", ".tsx",
            ".json", ".xml", ".yaml", ".yml", ".csv", ".ini", ".cfg", ".log", ".sh", ".bat", ".ps1", ".rb", ".go", ".rs",
            ".swift", ".kt", ".kts", ".php", ".css", ".scss", ".sass", ".less", ".html", ".htm", ".sql", ".lua", ".dart",
            ".r", ".m", ".vb", ".vbs", ".asm", ".s", ".erl", ".ex", ".exs", ".coffee", ".pl", ".perl", ".groovy", ".gradle",
            ".dockerfile", ".makefile", ".cmake", ".toml", ".tex"
        ]:
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
        else:
            return "Unsupported file type"
        return file_content   

    def _build_chunk_processing_prompt(self) -> str:
        """Build the prompt for processing individual chunks based on configuration."""
        prompt = (
            "Analyze the current text chunk and extract relevant information to update the memory.\n"
            f"Processing format: {self.static_parameters.chunk_processing_format}.\n"
            "Instructions:\n"
            "- Identify key points, facts, or insights relevant to the document's purpose.\n"
            "- Distinguish between major concepts and supporting details.\n"
            "- Recognize patterns, relationships, and connections between ideas.\n"
            "- Preserve technical accuracy and terminology where appropriate.\n"
        )

        # Format-specific instructions
        if self.static_parameters.chunk_processing_format == "bullet points":
            prompt += "- Organize memory as concise bullet points with clear hierarchy.\n"
            prompt += "- Use sub-bullets for supporting details or examples.\n"
        elif self.static_parameters.chunk_processing_format == "article meta data":
            prompt += "- Extract metadata such as author, date, title, publication, version, audience, etc.\n"
            prompt += "- Identify document structure, sections, and organization.\n"
        elif self.static_parameters.chunk_processing_format == "paragraph":
            prompt += "- Store information as coherent paragraphs with logical flow.\n"
            prompt += "- Ensure each paragraph has a clear topic sentence and supporting details.\n"
        elif self.static_parameters.chunk_processing_format == "key-value pairs":
            prompt += "- Structure memory as key-value pairs (e.g., 'Topic: Summary', 'Finding: Description').\n"
            prompt += "- Use consistent key naming for easier synthesis later.\n"
        elif self.static_parameters.chunk_processing_format == "json":
            prompt += """- Structure memory as valid JSON object with meaningful keys.
            Example format:
            ```json
            {
              "main_topics": ["topic1", "topic2"],
              "key_points": [
                {"point": "First important point", "relevance": "high"},
                {"point": "Second important point", "relevance": "medium"}
              ],
              "entities": {
                "people": ["Person A", "Person B"],
                "organizations": ["Org X", "Org Y"]
              },
              "quotes": ["Quote 1", "Quote 2"],
              "metrics": {"stat1": "value1", "stat2": "value2"}
            }
            ```
            - Adapt this structure to match the content of the document.
            - Ensure the JSON is valid and properly formatted.\n"""
        elif self.static_parameters.chunk_processing_format == "yaml":
            prompt += """- Structure memory as YAML with hierarchical organization.
            Example format:
            ```yaml
            main_topics:
              - topic1
              - topic2
            key_points:
              - point: First important point
                relevance: high
              - point: Second important point
                relevance: medium
            entities:
              people:
                - Person A
                - Person B
              organizations:
                - Org X
                - Org Y
            quotes:
              - Quote 1
              - Quote 2
            metrics:
              stat1: value1
              stat2: value2
            ```
            - Adapt this structure to match the content of the document.
            - Ensure the YAML is valid and properly formatted.\n"""
        elif self.static_parameters.chunk_processing_format == "table":
            prompt += """- Organize information in markdown tables for structured data.
            Example:
            | Category | Key Points | Evidence |
            |----------|------------|----------|
            | Topic 1  | Main finding| Supporting data |
            | Topic 2  | Secondary finding | Reference |
            
            - Create multiple tables if needed for different types of information.
            - Use appropriate column headers for the content type.\n"""
        elif self.static_parameters.chunk_processing_format == "custom template":
            if self.static_parameters.chunk_processing_template:
                prompt += f"- Use the following template to structure the memory:\n```\n{self.static_parameters.chunk_processing_template}\n```\n"
                prompt += "- Identify and fill in appropriate values for each placeholder in the template.\n"
            else:
                prompt += "- Organize information in a clear, structured format with logical sections and hierarchy.\n"

        # Contextual information focus
        if self.static_parameters.contextual_summary_information:
            prompt += f"Additional focus: {self.static_parameters.contextual_summary_information}\n"

        # Focus and exclusion areas
        if self.static_parameters.focus_areas:
            prompt += f"- Prioritize information about: {self.static_parameters.focus_areas}\n"
        if self.static_parameters.exclude_areas:
            prompt += f"- Exclude or minimize information about: {self.static_parameters.exclude_areas}\n"

        # Timestamp inclusion
        if self.static_parameters.include_timestamps:
            prompt += "- Include approximate location references (e.g., 'near beginning', 'middle section', 'page X') where relevant.\n"
        
        # Metadata handling
        if self.static_parameters.include_metadata:
            prompt += "- Capture any document metadata (author, date, version, etc.) when present.\n"

        # Sectioning
        if self.static_parameters.include_sections:
            prompt += "- Preserve section structure and hierarchy from the original document when possible.\n"

        # General guidance
        prompt += """
        - If no new information is found, preserve the existing memory unchanged.
        - Ensure clarity and relevance in all extracted data.
        - Avoid redundancy while preserving comprehensive coverage.
        - When uncertain about importance, err on the side of inclusion.
        """

        return prompt
    
    def _build_final_summary_prompt(self) -> str:
        """Build the prompt for the final summary based on configuration."""
        prompt = (
            "Synthesize the memory into a final summary.\n"
            f"Summary style: {self.static_parameters.summary_style}.\n"
            f"Tone: {self.static_parameters.summary_tone}.\n"
            f"Language level: {self.static_parameters.language_level}.\n"
            f"Output format: {self.static_parameters.output_format}.\n"
        )

        # Audience targeting
        if self.static_parameters.audience == "custom" and self.static_parameters.custom_audience:
            prompt += f"Target audience: {self.static_parameters.custom_audience}\n"
        else:
            prompt += f"Target audience: {self.static_parameters.audience}\n"

        # Style-specific instructions
        if self.static_parameters.summary_style == "concise":
            prompt += "- Provide a brief, high-level summary with minimal elaboration.\n"
            prompt += "- Focus on the most essential points and eliminate secondary details.\n"
            prompt += "- Aim for clarity and directness over comprehensiveness.\n"
        elif self.static_parameters.summary_style == "detailed":
            prompt += "- Include comprehensive details and context for each key point.\n"
            prompt += "- Provide supporting evidence, examples, and nuances.\n"
            prompt += "- Maintain logical organization while preserving important specifics.\n"
        elif self.static_parameters.summary_style == "executive":
            prompt += "- Focus on high-level insights, implications, and strategic considerations.\n"
            prompt += "- Emphasize actionable information and business impact.\n"
            prompt += "- Include recommendations or next steps when appropriate.\n"
        elif self.static_parameters.summary_style == "technical":
            prompt += "- Emphasize technical details, specifications, methodologies, and data.\n"
            prompt += "- Preserve precise terminology and quantitative information.\n"
            prompt += "- Maintain technical accuracy while ensuring clarity.\n"
        elif self.static_parameters.summary_style == "creative":
            prompt += "- Use narrative techniques and engaging language.\n"
            prompt += "- Connect ideas in novel ways while maintaining factual accuracy.\n"
            prompt += "- Consider using analogies or metaphors to explain complex concepts.\n"
        elif self.static_parameters.summary_style == "custom" and self.static_parameters.summary_template:
            prompt += f"- Use the following template for the final summary:\n```\n{self.static_parameters.summary_template}\n```\n"
            prompt += "- Identify and fill in appropriate content for each placeholder in the template.\n"
            prompt += "- Adapt the template as needed while preserving its overall structure.\n"

        # Tone-specific instructions
        if self.static_parameters.summary_tone == "neutral":
            prompt += "- Maintain an objective, balanced tone free from bias or emotion.\n"
            prompt += "- Present information impartially without editorializing.\n"
        elif self.static_parameters.summary_tone == "formal":
            prompt += "- Use professional, precise language appropriate for business or academic contexts.\n"
            prompt += "- Avoid colloquialisms, contractions, and informal expressions.\n"
        elif self.static_parameters.summary_tone == "informal":
            prompt += "- Adopt a conversational, approachable tone.\n"
            prompt += "- Use everyday language and occasional contractions.\n"
        elif self.static_parameters.summary_tone == "academic":
            prompt += "- Employ scholarly conventions and formal academic language.\n"
            prompt += "- Focus on evidence-based analysis and theoretical implications.\n"
        elif self.static_parameters.summary_tone == "enthusiastic":
            prompt += "- Convey positive energy and highlight promising aspects.\n"
            prompt += "- Emphasize opportunities, benefits, and potential.\n"
        elif self.static_parameters.summary_tone == "critical":
            prompt += "- Apply analytical scrutiny and evaluative judgment.\n"
            prompt += "- Identify limitations, challenges, and areas for improvement.\n"
        elif self.static_parameters.summary_tone == "humorous":
            prompt += "- Incorporate appropriate levity and wit while maintaining professionalism.\n"
            prompt += "- Use humor tactfully to enhance engagement without undermining credibility.\n"

        # Language level instructions
        if self.static_parameters.language_level == "simple":
            prompt += "- Use basic vocabulary and straightforward sentence structures.\n"
            prompt += "- Explain technical terms and avoid jargon.\n"
            prompt += "- Optimize for clarity and accessibility to non-specialists.\n"
        elif self.static_parameters.language_level == "standard":
            prompt += "- Use everyday professional language with moderate complexity.\n"
            prompt += "- Balance accessibility with appropriate terminology.\n"
        elif self.static_parameters.language_level == "advanced":
            prompt += "- Employ sophisticated vocabulary and complex sentence structures when appropriate.\n"
            prompt += "- Use domain-specific terminology with minimal simplification.\n"
        elif self.static_parameters.language_level == "expert":
            prompt += "- Use specialized terminology and technical language freely.\n"
            prompt += "- Assume high domain knowledge and expertise from the reader.\n"

        # Output format instructions
        if self.static_parameters.output_format == "markdown":
            prompt += "- Format the summary using Markdown for headings, lists, emphasis, etc.\n"
            prompt += "- Use appropriate Markdown features to enhance readability and structure.\n"
        elif self.static_parameters.output_format == "html":
            prompt += "- Format the summary using HTML tags for structure and emphasis.\n"
            prompt += "- Use appropriate HTML elements to enhance readability and organization.\n"
        elif self.static_parameters.output_format == "plain text":
            prompt += "- Format the summary as plain text without markup.\n"
            prompt += "- Use spacing, capitalization, and other text-based formatting for structure.\n"
        elif self.static_parameters.output_format == "json":
            prompt += """- Structure the summary as a valid JSON object with appropriate sections.
            Example structure:
            ```json
            {
            "title": "Document Title",
            "metadata": {
                "author": "Author Name",
                "date": "Date information",
                "source": "Source information"
            },
            "summary": {
                "overview": "Brief overview text",
                "key_points": ["Point 1", "Point 2", "Point 3"],
                "sections": [
                {
                    "title": "Section 1",
                    "content": "Section 1 summary"
                },
                {
                    "title": "Section 2",
                    "content": "Section 2 summary"
                }
                ],
                "conclusions": "Concluding remarks"
            }
            }
            ```
            - Adapt this structure based on the document content and features enabled.
            - Ensure the JSON is valid and properly formatted.\n"""
        elif self.static_parameters.output_format == "yaml":
            prompt += """- Structure the summary as YAML with appropriate sections.
            Example structure:
            ```yaml
            title: Document Title
            metadata:
            author: Author Name
            date: Date information
            source: Source information
            summary:
            overview: Brief overview text
            key_points:
                - Point 1
                - Point 2
                - Point 3
            sections:
                - title: Section 1
                content: Section 1 summary
                - title: Section 2
                content: Section 2 summary
            conclusions: Concluding remarks
            ```
            - Adapt this structure based on the document content and features enabled.
            - Ensure the YAML is valid and properly formatted.\n"""

        # Handling optional features
        if self.static_parameters.include_metadata:
            prompt += "- Include relevant document metadata (title, author, date, etc.) at the beginning of the summary.\n"
        
        if self.static_parameters.include_sections:
            prompt += "- Organize the summary according to the document's section structure when possible.\n"
            prompt += "- Use appropriate headings to reflect the original document organization.\n"
        
        if self.static_parameters.highlight_key_findings:
            prompt += "- Clearly identify and emphasize the most important findings or takeaways.\n"
            prompt += "- Consider using a dedicated 'Key Findings' section at the beginning or end.\n"
        
        # Focus and exclusion areas
        if self.static_parameters.focus_areas:
            prompt += f"- Prioritize information about: {self.static_parameters.focus_areas}\n"
        
        if self.static_parameters.exclude_areas:
            prompt += f"- Exclude or minimize information about: {self.static_parameters.exclude_areas}\n"

        # General instructions
        prompt += """
        General guidelines:
        - Ensure the summary accurately represents the original document's content.
        - Maintain logical flow and coherent organization throughout.
        - Balance comprehensiveness with concision based on the specified style.
        - Preserve the most important insights, findings, and conclusions.
        - Avoid introducing information not present in the original document.
        - When in doubt about inclusion, prioritize information that provides significant value to the audience.
        """

        return prompt
    def summarize_document(self, file_path: Path) -> str:
        """
        Summarize a document file using the configured parameters.
        
        Args:
            file_path: Path to the document file to summarize
            
        Returns:
            A string containing the summarized content
        """
        self.personality.step_start(f"Summarizing {file_path}")
        
        # Validate file existence
        file_path = Path(file_path)
        if not file_path.exists():
            self.personality.step_end(f"Summarizing {file_path}", False)
            return f"Error: File '{file_path}' not found."

        # Read the file content
        try:
            file_content = self.load_file(file_path)
            if not file_content.strip():
                self.personality.step_end(f"Summarizing {file_path}", False)
                return "Error: File is empty."
        except Exception as e:
            self.personality.step_end(f"Summarizing {file_path}", False)
            return f"Error reading file: {str(e)}"

        # Build processing prompts
        chunk_processing_prompt = self._build_chunk_processing_prompt()
        final_memory_processing_prompt = self._build_final_summary_prompt()
        
        # Determine output format
        chunk_output_format = "markdown"
        if self.static_parameters.chunk_processing_format == "json":
            chunk_output_format = "json"
        elif self.static_parameters.chunk_processing_format == "yaml":
            chunk_output_format = "yaml"
        
        final_output_format = self.static_parameters.output_format
        
        # Perform summarization
        try:
            self.personality.step(f"Starting sequential summarization process with {len(file_content)} characters...")
            self.personality.step(f"Using context size: {self.static_parameters.context_size}, chunk size: {self.static_parameters.chunk_size}")
            
            # Create progress callback
            def progress_callback(step_name, current_step, total_steps, output=None):
                progress_pct = int((current_step / total_steps) * 100) if total_steps > 0 else 0
                self.personality.step(f"[{progress_pct}%] {step_name}: Step {current_step}/{total_steps}")
                return True
            
            formatted_summary = self.personality.sequential_summarize(
                text=file_content,
                chunk_processing_prompt=chunk_processing_prompt,
                chunk_processing_output_format=chunk_output_format,
                final_memory_processing_prompt=final_memory_processing_prompt,
                final_output_format=final_output_format,
                ctx_size=self.static_parameters.context_size,
                chunk_size=self.static_parameters.chunk_size,
                callback=self.personality.sink,
                step_callback = progress_callback,
                debug=False
            )
            
            self.personality.step_end(f"Summarizing {file_path}")
            return formatted_summary
        except Exception as e:
            trace_exception(e)  # Log the exception for debugging
            self.personality.step_end(f"Summarizing {file_path}", False)
            return f"Error during summarization: {str(e)}"
        
    def execute(self, context: LollmsContextDetails, **kwargs) -> str:
        file_path = kwargs.get("file_path", None)
        
        if file_path is None:
            full_summaries = ""
            for file_path in self.client.discussion.text_files:
                summary = self.summarize_document(file_path)
                full_summaries += f"""
-----
Document Summary : {file_path}
-----
{summary}
"""     
            return full_summaries
        else:
            return self.summarize_document(file_path)
        
