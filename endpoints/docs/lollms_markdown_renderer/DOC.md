Certainly! Here's the updated version of the quick guide using `await` for rendering the Markdown content:

## MarkdownRenderer Library - Quick Guide

The `MarkdownRenderer` library is a JavaScript class for converting Markdown content into HTML with features like code highlighting, LaTeX math rendering, and Mermaid diagrams.

### Key Features

1. **Mermaid Diagrams**: Render diagrams from Markdown code blocks.
2. **Code Highlighting**: Use Prism.js for syntax highlighting.
3. **Math Equations**: Support LaTeX-style math equations.
4. **Tables**: Convert Markdown tables into HTML.
5. **Text Formatting**: Handle headers, bold, italic, links, lists, blockquotes, and horizontal rules.
6. **Copy Code**: Enable copying of code blocks with line numbers.

### Integration Steps

Include the following in your HTML file header (this must be added to the html to allow the rendering):

```html
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
    <!-- needed for math rendering in markdown -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.13.11/dist/katex.min.css">
    <script src="https://cdn.jsdelivr.net/npm/katex@0.13.11/dist/katex.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>

    <!-- MarkdownRenderer -->
    <script src="/lollms_assets/js/lollms_markdown_renderer"></script>
    <link rel="stylesheet" href="/lollms_assets/css/lollms_markdown_renderer">
```

### Usage

```javascript
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
```


- **Code Blocks**: Use Prism.js for syntax highlighting by specifying the language (e.g., `javascript`).
- **Mermaid Diagrams**: Use `mermaid` identifier in code blocks.
- **Math Equations**: Use `$...$` for inline and `$$...$$` for block equations.
- **Tables**: Automatically convert Markdown tables to HTML.
