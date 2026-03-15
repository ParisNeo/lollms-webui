# Import necessary libraries
import re
from pathlib import Path
from functools import partial
from typing import List
from ascii_colors import trace_exception

# Define the conversion function
def markdown_to_latex(file_path: str) -> str:
    try:
        # Load the markdown file
        markdown_text = Path(file_path).read_text()

        # Extract title, author, and prompted by information
        title_match = re.search(r'^# (.*)', markdown_text, re.MULTILINE)
        author_match = re.search(r'^Author: (.*)', markdown_text, re.MULTILINE)
        prompted_by_match = re.search(r'^Prompted by: (.*)', markdown_text, re.MULTILINE)

        title = title_match.group(1) if title_match else "Untitled"
        author = author_match.group(1) if author_match else ""
        prompted_by = prompted_by_match.group(1) if prompted_by_match else ""

        # Remove the extracted parts from the markdown text
        markdown_text = re.sub(r'^# .*\n', '', markdown_text, flags=re.MULTILINE)
        markdown_text = re.sub(r'^Author: .*\n', '', markdown_text, flags=re.MULTILINE)
        markdown_text = re.sub(r'^Prompted by: .*\n', '', markdown_text, flags=re.MULTILINE)

        # Define conversion rules from markdown to LaTeX
        conversion_rules = [
            (r'\\', r'\\textbackslash{}'),  # Escape backslashes
            (r'^## (Chapter\s*\d+:\s*)?(.*)', lambda match: f"\\chapter{{{match.group(2)}}}"),  # Convert chapters
            (r'^### (.*)', r'\\section*{\1}'),  # Convert subsections without numbering
            (r'\*\*(.*?)\*\*', r'\\textbf{\1}'),  # Bold text
            (r'\*(.*?)\*', r'\\textit{\1}'),  # Italic text
            (r'\!\[(.*?)\]\((.*?)\)', r'\\begin{figure}[h!]\n\\centering\n\\includegraphics[width=\\textwidth]{\2}\n\\caption{\1}\n\\end{figure}'),  # Images
            (r'\[(.*?)\]\((.*?)\)', r'\\href{\2}{\1}'),  # Links
            (r'`([^`]*)`', r'\\texttt{\1}'),  # Inline code
            (r'^```\s*([a-z]*)\s*\n([\s\S]*?)\n```', r'\\begin{verbatim}\2\\end{verbatim}'),  # Code blocks
            (r'^-\s+(.*)', r'\\begin{itemize}\n\\item \1\n\\end{itemize}'),  # Unordered lists
            (r'^\d+\.\s+(.*)', r'\\begin{enumerate}\n\\item \1\n\\end{enumerate}'),  # Ordered lists
            (r'^>(.*)', r'\\begin{quote}\1\\end{quote}'),  # Block quotes
        ]
        
        # Apply conversion rules
        latex_text = markdown_text
        for pattern, replacement in conversion_rules:
            if callable(replacement):
                latex_text = re.sub(pattern, replacement, latex_text, flags=re.MULTILINE)
            else:
                latex_text = re.sub(pattern, replacement, latex_text, flags=re.MULTILINE)

        # Add lettrine to the first letter of the first paragraph of each chapter
        latex_text = re.sub(r'(\\chapter{[^}]*}\n\n?)(\w)', r'\1\\lettrine[lines=2]{\2}{}', latex_text)

        # Create the LaTeX document structure with fancyhdr for headers
        latex_document = f"""
\\documentclass{{book}}
\\usepackage{{hyperref}}
\\usepackage{{graphicx}}
\\usepackage{{verbatim}}
\\usepackage{{fancyhdr}}
\\usepackage{{lettrine}}
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[LE,RO]{{\\thepage}}
\\fancyhead[RE,LO]{{\\leftmark}}

\\begin{{document}}

\\title{{{title}}}
\\author{{{author}}}
\\date{{}}

\\maketitle

\\begin{{flushleft}}
\\textbf{{Prompted by:}} {prompted_by}
\\end{{flushleft}}

{latex_text}

\\end{{document}}
        """

        # Define output file path
        output_path = Path(file_path).with_suffix('.tex')
        
        # Save the LaTeX text to a file
        output_path.write_text(latex_document)
        
        # Finally we return the path to the LaTeX file
        return str(output_path)
    except Exception as e:
        return trace_exception(e)

# Metadata function
def markdown_to_latex_function():
    return {
        "function_name": "markdown_to_latex",  # The function name in string
        "function": markdown_to_latex,  # The function to be called
        "function_description": "Converts a markdown file to a LaTeX file.",  # Description
        "function_parameters": [{"name": "file_path", "type": "str"}]  # The set of parameters
    }

if __name__ == "__main__":
    # Test the function with a sample file
    test_file_path = "story.md"
    result = markdown_to_latex(test_file_path)
    print(f"Generated LaTeX file: {result}")
