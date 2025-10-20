## Documentation for `MarkdownRenderer` Library

The `MarkdownRenderer` library is a JavaScript class designed to render Markdown content into HTML. It supports various features such as code highlighting, LaTeX math rendering, Mermaid diagrams, and more. Below is a detailed explanation of how the library works, how to integrate it into an HTML file, and examples of its usage.

### Features

1. **Mermaid Diagrams**: Renders Mermaid diagrams from Markdown code blocks.
2. **Code Highlighting**: Uses Prism.js for syntax highlighting of code blocks.
3. **Math Equations**: Supports LaTeX-style math equations.
4. **Tables**: Converts Markdown tables into HTML tables.
5. **Text Formatting**: Handles headers, bold, italic, links, lists, blockquotes, and horizontal rules.
6. **Copy Code Functionality**: Allows users to copy code blocks with line numbers.

### Integration into an HTML File

To use the `MarkdownRenderer` library, you need to include several external libraries and stylesheets in your HTML file. Below is an example of how to set up your HTML file:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown Renderer Example</title>
    <!-- Highlight.js for code highlighting -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.5.1/styles/default.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.5.1/highlight.min.js"></script>

    <!-- MathJax for LaTeX math rendering -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/tex-mml-chtml.js"></script>

    <!-- Mermaid for graph rendering -->
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>

    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>

    <!-- Axios for HTTP requests -->
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>

    <!-- Anime.js for animations -->
    <script src="https://cdn.jsdelivr.net/npm/animejs@3.2.1/lib/anime.min.js"></script>

    <!-- Prism CSS and JS for code highlighting -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/themes/prism.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/prism.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-javascript.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-python.min.js"></script>
    <!-- Add more languages as needed -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>

    <!-- Include the MarkdownRenderer script -->
    <script src="/lollms_assets/js/lollms_markdown_renderer"></script>
    <link rel="stylesheet" href="/lollms_assets/css/lollms_markdown_renderer">
</head>
<body>
    <div id="markdown-content">
        <!-- Markdown content will be rendered here -->
    </div>

    <script>
        // Initialize the MarkdownRenderer
        const mr = new MarkdownRenderer();

        // Example Markdown text
        const markdownText = `
        # Sample Markdown
        This is a **bold** text and this is *italic* text.

        ## Code Block
        \`\`\`javascript
        console.log('Hello, World!');
        \`\`\`

        ## Mermaid Diagram
        \`\`\`mermaid
        graph TD;
            A-->B;
            A-->C;
            B-->D;
            C-->D;
        \`\`\`

        ## Math Equation
        $$E = mc^2$$

        ## Table
        | Name  | Age |
        |-------|-----|
        | Alice | 24  |
        | Bob   | 30  |
        `;

        // Render the Markdown text
        mr.renderMarkdown(markdownText).then(renderedHtml => {
            document.getElementById('markdown-content').innerHTML = renderedHtml;
        });
    </script>
</body>
</html>
```

Or using async

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown Renderer Example</title>
    <!-- External Libraries -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.5.1/styles/default.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.5.1/highlight.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/tex-mml-chtml.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/animejs@3.2.1/lib/anime.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/themes/prism.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/prism.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-javascript.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-python.min.js"></script>
    <!-- MarkdownRenderer -->
    <script src="/lollms_assets/js/lollms_markdown_renderer"></script>
    <link rel="stylesheet" href="/lollms_assets/css/lollms_markdown_renderer">
</head>
<body>
    <div id="markdown-content"></div>
    <script>
        (async () => {
            const mr = new MarkdownRenderer();
            const markdownText = `
            # Sample Markdown
            **Bold** text, *italic* text.

            ## Code Block
            \`\`\`javascript
            console.log('Hello, World!');
            \`\`\`

            ## Mermaid Diagram
            \`\`\`mermaid
            graph TD;
                A-->B;
                A-->C;
                B-->D;
                C-->D;
            \`\`\`

            ## Math Equation
            $$E = mc^2$$

            ## Table
            | Name  | Age |
            |-------|-----|
            | Alice | 24  |
            | Bob   | 30  |
            `;
            const renderedHtml = await mr.renderMarkdown(markdownText);
            document.getElementById('markdown-content').innerHTML = renderedHtml;
        })();
    </script>
</body>
</html>
```

### Explanation of the Code

- **External Libraries**: The HTML file includes several external libraries such as Highlight.js, MathJax, Mermaid, Tailwind CSS, Axios, Anime.js, and Prism.js. These libraries are necessary for rendering code, math equations, diagrams, and styling.

- **MarkdownRenderer Initialization**: An instance of `MarkdownRenderer` is created and used to render Markdown text into HTML.

- **Rendering Markdown**: The `renderMarkdown` method is called with the Markdown text. It processes the text and converts it into HTML, which is then inserted into the `#markdown-content` div.

### Usage Examples

1. **Rendering Code Blocks**: The library uses Prism.js to highlight code blocks. You can specify the language for syntax highlighting by using the appropriate language identifier (e.g., `javascript`, `python`).

2. **Rendering Mermaid Diagrams**: Wrap your Mermaid code in a code block with the `mermaid` identifier to render diagrams.

3. **Rendering Math Equations**: Use LaTeX-style syntax for math equations. Inline equations can be wrapped in `$...$`, and block equations can be wrapped in `$$...$$`.

4. **Rendering Tables**: Markdown tables are automatically converted into HTML tables with proper styling.

5. **Copy Code Functionality**: Each code block includes a "Copy" button that allows users to copy the code with line numbers.

This documentation provides a comprehensive guide to using the `MarkdownRenderer` library. By following the integration steps and examples, you can easily render Markdown content in your web applications.