// Requires importing:
// <!-- For code highlighting -->
// <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.5.1/styles/default.min.css">
// <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.5.1/highlight.min.js"></script>

// <!-- For LaTeX math rendering -->
// <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/tex-mml-chtml.js"></script>

// <!-- For Mermaid graph rendering -->
// <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>


// <script src="https://cdn.tailwindcss.com"></script>
// <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
// <script src="https://cdn.jsdelivr.net/npm/animejs@3.2.1/lib/anime.min.js"></script>


// <!-- Prism CSS -->
// <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/themes/prism.min.css" rel="stylesheet" />

// <!-- Prism JS -->
// <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/prism.min.js"></script>

// <!-- If you want additional languages, include them like this -->
// <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-python.min.js"></script>
// <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-javascript.min.js"></script>
// <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-markup.min.js"></script>
// <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-c.min.js"></script>
// <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-cpp.min.js"></script>
// <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-java.min.js"></script>
// <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-latex.min.js"></script>
// When served with lollms, just use     <script src="/lollms_assets/js/lollms_markdown_renderer"></script>
// Don't forget to get the css too <link rel="stylesheet" href="/lollms_assets/css/lollms_markdown_renderer">

// Make sure there is a global variable called mr that instanciate MarkdownRenderer
// mr = new MarkdownRenderer()


class MarkdownRenderer {
  async renderMermaidDiagrams(text) {
        const mermaidCodeRegex = /```mermaid\n([\s\S]*?)```/g;
        const matches = text.match(mermaidCodeRegex);

        if (!matches) return text;

        for (const match of matches) {
            const mermaidCode = match.replace(/```mermaid\n/, '').replace(/```$/, '');
            const uniqueId = 'mermaid-' + Math.random().toString(36).substr(2, 9);

            try {
                const result = await mermaid.render(uniqueId, mermaidCode);
                const htmlCode = `
                    <div class="mermaid-container relative flex justify-center items-center mt-4 mb-4 w-full">
                        <div class="mermaid-diagram bg-white p-4 rounded-lg shadow-md overflow-auto w-full" style="max-height: 80vh;">
                            <div id="${uniqueId}" style="transform-origin: top left; transition: transform 0.3s;">
                                ${result.svg}
                            </div>
                        </div>
                        <div class="absolute top-2 right-2 flex gap-1">
                            <button onclick="mr.zoomMermaid('${uniqueId}', 1.1)" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="11" cy="11" r="8"></circle>
                                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                                    <line x1="11" y1="8" x2="11" y2="14"></line>
                                    <line x1="8" y1="11" x2="14" y2="11"></line>
                                </svg>
                            </button>
                            <button onclick="mr.zoomMermaid('${uniqueId}', 0.9)" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="11" cy="11" r="8"></circle>
                                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                                    <line x1="8" y1="11" x2="14" y2="11"></line>
                                </svg>
                            </button>
                            <button onclick="mr.saveMermaidAsPNG('${uniqueId}')" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                PNG
                            </button>
                            <button onclick="mr.saveMermaidAsSVG('${uniqueId}')" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                SVG
                            </button>
                        </div>
                    </div>
                `;
                text = text.replace(match, htmlCode);
            } catch (error) {
                console.error('Mermaid rendering failed:', error);
                text = text.replace(match, `<div class="mermaid-error bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">Failed to render diagram</div>`);
            }
        }

        return text;
    }

async renderSVG(text) {
        const svgCodeRegex = /```svg\n([\s\S]*?)```/g;
        const matches = text.match(svgCodeRegex);
    
        if (!matches) return text;
    
        for (const match of matches) {
            const svgCode = match.replace(/```svg\n/, '').replace(/```$/, '');
            const uniqueId = 'svg-' + Math.random().toString(36).substr(2, 9);
    
            try {
                // Wrap the SVG code in a div with a unique ID
                const htmlCode = `
                    <div class="svg-container relative flex justify-center items-center mt-4 mb-4 w-full">
                        <div class="svg-diagram bg-white p-4 rounded-lg shadow-md overflow-auto w-full" style="max-height: 80vh;">
                            <div id="${uniqueId}" style="transform-origin: top left; transition: transform 0.3s;">
                                ${svgCode}
                            </div>
                        </div>
                        <div class="absolute top-2 right-2 flex gap-1">
                            <button onclick="svgr.zoomSVG('${uniqueId}', 1.1)" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="11" cy="11" r="8"></circle>
                                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                                    <line x1="11" y1="8" x2="11" y2="14"></line>
                                    <line x1="8" y1="11" x2="14" y2="11"></line>
                                </svg>
                            </button>
                            <button onclick="svgr.zoomSVG('${uniqueId}', 0.9)" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="11" cy="11" r="8"></circle>
                                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                                    <line x1="8" y1="11" x2="14" y2="11"></line>
                                </svg>
                            </button>
                            <button onclick="svgr.saveSVGAsPNG('${uniqueId}')" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                PNG
                            </button>
                            <button onclick="svgr.saveSVGAsSVG('${uniqueId}')" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                SVG
                            </button>
                        </div>
                    </div>
                `;
                text = text.replace(match, htmlCode);
            } catch (error) {
                console.error('SVG rendering failed:', error);
                text = text.replace(match, `<div class="svg-error bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">Failed to render SVG</div>`);
            }
        }
    
        return text;
    }
  
    async renderCodeBlocks(text) {
      if (typeof Prism === 'undefined') {
          throw new Error('Prism is not loaded. Please include Prism.js in your project.');
      }

      const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;

      const renderedText = await text.replace(codeBlockRegex, (match, language, code) => {
          language = language || 'plaintext';

          if (!Prism.languages[language]) {
              console.warn(`Language '${language}' is not supported by Prism. Falling back to plaintext.`);
              language = 'plaintext';
          }

          const highlightedCode = Prism.highlight(code.trim(), Prism.languages[language], language);

          const lines = highlightedCode.split(/\r?\n/);
          const numberedLines = lines.map((line, index) =>
              `<span class="code-line"><span class="line-number">${index + 1}</span><span class="line-content">${line}</span></span>`
          ).join('\n');

          return `
          <div class="code-block-wrapper bg-gray-100 rounded-lg shadow-md overflow-hidden my-4">
              <div class="code-block-header bg-gray-200 px-4 py-2 flex justify-between items-center">
                  <div class="language-label font-semibold text-gray-700">${language}</div>
                  <button class="copy-button bg-blue-500 hover:bg-blue-600 text-white font-bold py-1 px-3 rounded" onclick="mr.copyCode(this)">
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1">
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                      </svg>
                      Copy
                  </button>
              </div>
              <div class="code-content max-h-[500px] overflow-auto">
                  <pre class="line-numbers text-sm leading-tight"><code class="language-${language}">${numberedLines}</code></pre>
              </div>
          </div>`;
      });

      return renderedText;
  }

      
    handleInlineCode(text) {
      return text.replace(/`([^`]+)`/g, function(match, code) {
          return `<b>${code}</b>`;
      });
    }
  
    handleMathEquations(text) {
      return text.replace(/\\\[([\s\S]*?)\\\]|\$\$([\s\S]*?)\$\$|\$([^\n]+?)\$/g, function(match, p1, p2, p3) {
          const equation = p1 || p2 || p3;
          return '<span class="math">' + equation + '</span>';
      });
    }
  
    async handleTables(text) {
      let alignments = [];
      let tableRows = [];
      let isInTable = false;
      let hasHeader = false;
  
      // Process the text line by line
      text = text.split('\n').map(line => {
          // Check if the line is a table row
          if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
              isInTable = true;
              const tableRow = line.trim().slice(1, -1); // Remove leading and trailing |
              const cells = tableRow.split('|').map(cell => cell.trim());
              
              if (cells.every(cell => cell.match(/^:?-+:?$/))) {
                  // This is the header separator row
                  alignments = cells.map(cell => {
                      if (cell.startsWith(':') && cell.endsWith(':')) return 'center';
                      if (cell.endsWith(':')) return 'right';
                      return 'left';
                  });
                  hasHeader = true;
                  return ''; // Remove separator row
              }
              
              const cellType = !hasHeader ? 'th' : 'td';
              const renderedCells = cells.map((cell, cellIndex) => 
                  `<${cellType} class="border px-4 py-2" style="text-align: ${alignments[cellIndex] || 'left'};">${cell}</${cellType}>`
              ).join('');
              
              tableRows.push(`<tr>${renderedCells}</tr>`);
              return ''; // Remove the original Markdown line
          } else if (isInTable) {
              // We've reached the end of the table
              isInTable = false;
              hasHeader = false;
              const tableContent = tableRows.join('');
              tableRows = []; // Reset for next table
              return `<table class="table-auto w-full border-collapse border border-gray-300">${tableContent}</table>`;
          }
          return line; // Return non-table lines unchanged
      }).join('\n');
  
      // Handle case where table is at the end of the text
      if (isInTable) {
          const tableContent = tableRows.join('');
          text += `<table class="table-auto w-full border-collapse border border-gray-300">${tableContent}</table>`;
      }
      return text
    }
  
    handleHeaders(text) {
        return text.replace(/^(#{1,6})\s+(.*?)$/gm, function(match, hashes, content) {
            const level = hashes.length;
            const fontSize = 2.5 - (level * 0.3); // Decreasing font size for each level
            return `<h${level} style="font-size: ${fontSize}em; font-weight: bold;">${content}</h${level}>`;
        });
    }
  
  
    handleBoldText(text) {
      return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }
  
    handleItalicText(text) {
      return text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    }
  
    handleLinks(text) {
      return text.replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2">$1</a>');
    }
  
    handleUnorderedLists(text) {
      return text.replace(/^\s*[-*+]\s+(.*?)$/gm, '<li>$1</li>')
          .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    }
  
    handleOrderedLists(text) {
      return text.replace(/^\s*(\d+)\.\s+(.*?)$/gm, '<li>$2</li>')
          .replace(/(<li>.*<\/li>)/s, '<ol>$1</ol>');
    }
  
    handleBlockquotes(text) {
      return text.replace(/^>\s+(.*?)$/gm, '<blockquote>$1</blockquote>');
    }
  
    handleHorizontalRules(text) {
      return text.replace(/^(-{3,}|_{3,}|\*{3,})$/gm, '<hr>');
    }
  
    handleParagraphs(text) {
      //return text.replace(/^(?!<[uo]l|<blockquote|<h\d|<pre|<hr|<table|<li|<button)(.+)$/gm, '<p class="mb-4">$1</p>');
      // No need to handle paragraphs separately, they will be handled as the remaining content
      return text;
    }
  
    async renderMarkdown(text) {
      // Handle Mermaid graphs first
      text = await this.renderMermaidDiagrams(text);

      // Handle SVG graphs first
      text = await this.renderSVG(text);
      
      // Handle code blocks with syntax highlighting and copy button
      text = await this.renderCodeBlocks(text);
  
      // Handle inline code
      text = this.handleInlineCode(text);
  
      // Handle LaTeX-style math equations
      text = this.handleMathEquations(text);
  
      // Handle tables
      text = await this.handleTables(text);
  
      // Handle headers
      text = this.handleHeaders(text);
  
      // Handle bold text
      text = this.handleBoldText(text);
  
      // Handle italic text
      text = this.handleItalicText(text);
  
      // Handle links
      text = this.handleLinks(text);
  
      // Handle unordered lists
      text = this.handleUnorderedLists(text);
  
      // Handle ordered lists
      text = this.handleOrderedLists(text);
  
      // Handle blockquotes
      text = this.handleBlockquotes(text);
  
      // Handle horizontal rules
      text = this.handleHorizontalRules(text);
  
      // Handle paragraphs
      text = this.handleParagraphs(text);
  
      return text;
    }
  
    initMermaid() {
      if (typeof mermaid !== 'undefined') {
          mermaid.initialize({ startOnLoad: false });
      } else {
          console.error('Mermaid library is not loaded');
      }
    }
  
    initPrism() {
      if (typeof Prism !== 'undefined') {
          // No further initialization needed
      } else {
          console.error('Prism library is not loaded');
      }
    }
  
    // Helper functions for Mermaid and code block handling
    saveMermaidAsPNG(id) {
        const svg = document.querySelector(`#${id} svg`);
        const svgData = new XMLSerializer().serializeToString(svg);
        
        // Create a canvas with a higher resolution
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");
        
        // Set a scale factor for higher resolution (e.g., 2 for double resolution)
        const scaleFactor = 2;
        
        const img = new Image();
        img.onload = function() {
            canvas.width = img.width * scaleFactor;
            canvas.height = img.height * scaleFactor;
            
            // Scale the context to draw the image at a higher resolution
            ctx.scale(scaleFactor, scaleFactor);
            ctx.drawImage(img, 0, 0);
            
            const pngFile = canvas.toDataURL("image/png");
            const downloadLink = document.createElement("a");
            downloadLink.download = "mermaid_diagram.png";
            downloadLink.href = pngFile;
            downloadLink.click();
        };
        img.src = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(svgData)));
    }
  
    saveMermaidAsSVG(id) {
        const svg = document.querySelector(`#${id} svg`);
        const svgData = new XMLSerializer().serializeToString(svg);
        const svgBlob = new Blob([svgData], {type: "image/svg+xml;charset=utf-8"});
        const svgUrl = URL.createObjectURL(svgBlob);
        const downloadLink = document.createElement("a");
        downloadLink.href = svgUrl;
        downloadLink.download = "mermaid_diagram.svg";
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
    }
  
    zoomMermaid(id, factor) {
        const svg = document.getElementById(id).firstElementChild;
        const currentScale = svg.style.transform ? parseFloat(svg.style.transform.replace('scale(', '').replace(')', '')) : 1;
        const newScale = currentScale * factor;
        svg.style.transform = `scale(${newScale})`;
    }
  
    copyCode(button) {
        const codeBlock = button.closest('.code-block-wrapper').querySelector('code');
        const codeLines = codeBlock.querySelectorAll('.code-line');
        let codeText = '';
        
        codeLines.forEach((line) => {
            const lineNumber = line.querySelector('.line-number').textContent;
            const lineContent = line.querySelector('.line-content').textContent;
            codeText += `${lineNumber} ${lineContent}\n`;
        });

        navigator.clipboard.writeText(codeText.trim()).then(() => {
            button.classList.add('copied');
            button.querySelector('svg').style.display = 'none';
            button.innerHTML = 'Copied!';
            setTimeout(() => {
            button.classList.remove('copied');
            button.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
                Copy
            `;
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    }  
    async highlightCode(code, language) {
        // Make sure the language is supported by your highlighting library
        const supportedLanguage = Prism.languages[language] ? language : 'plaintext';
        return Prism.highlight(code, Prism.languages[supportedLanguage], supportedLanguage);
    }

    // Helper function to escape HTML special characters
    escapeHtml(unsafe) {
        if (typeof unsafe !== 'string') {
            console.log("Found unsafe string:", text)
            return '';
        }
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}