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
// <!-- Render math -->
// <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.13.11/dist/katex.min.css">
// <script src="https://cdn.jsdelivr.net/npm/katex@0.13.11/dist/katex.min.js"></script>
// <!-- Render graphviz -->
// <script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/viz.js"></script>
// <script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/full.render.js"></script>
// Don't forget to get the css too <link rel="stylesheet" href="/lollms_assets/css/lollms_markdown_renderer">



class MarkdownRenderer {
    constructor() {
        this.svgState = {};
        this.initDiagramZoomPan();
    }    

    initDiagramZoomPan = (id, type) => {
        if (!this.diagramState) {
            this.diagramState = {};
        }
        this.diagramState[id] = { scale: 1, translateX: 0, translateY: 0, isDragging: false, startX: 0, startY: 0, type: type };

        setTimeout(() => {
            const container = document.getElementById(id);
            if (!container) return;

            container.addEventListener('wheel', (e) => this.handleDiagramWheel(e, id));
            container.addEventListener('mousedown', (e) => this.handleDiagramMouseDown(e, id));
            container.addEventListener('mousemove', (e) => this.handleDiagramMouseMove(e, id));
            container.addEventListener('mouseup', () => this.handleDiagramMouseUp(id));
            container.addEventListener('mouseleave', () => this.handleDiagramMouseUp(id));
        }, 100);
    }

    handleDiagramWheel = (e, id) => {
        e.preventDefault();
        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        this.zoomDiagram(id, delta);
    }

    handleDiagramMouseDown = (e, id) => {
        const state = this.diagramState[id];
        if (!state) return;
        state.isDragging = true;
        state.startX = e.clientX - state.translateX;
        state.startY = e.clientY - state.translateY;
    }

    handleDiagramMouseMove = (e, id) => {
        const state = this.diagramState[id];
        if (!state || !state.isDragging) return;
        state.translateX = e.clientX - state.startX;
        state.translateY = e.clientY - state.startY;
        this.updateDiagramTransform(id);
    }

    handleDiagramMouseUp = (id) => {
        if (this.diagramState[id]) {
            this.diagramState[id].isDragging = false;
        }
    }

    zoomDiagram = (id, delta) => {
        const state = this.diagramState[id];
        if (!state) return;
        state.scale *= delta;
        this.updateDiagramTransform(id);
    }

    resetDiagramZoomPan = (id) => {
        const type = this.diagramState[id]?.type;
        this.diagramState[id] = { scale: 1, translateX: 0, translateY: 0, isDragging: false, startX: 0, startY: 0, type: type };
        this.updateDiagramTransform(id);
    }

    updateDiagramTransform = (id) => {
        const container = document.getElementById(id);
        if (!container) return;
        const state = this.diagramState[id];
        container.style.transform = `translate(${state.translateX}px, ${state.translateY}px) scale(${state.scale})`;
    }
    saveDiagramAsPNG(id) {
        console.log('Starting saveDiagramAsPNG function');
        const container = document.getElementById(id);
        if (!container) {
            console.error('Container element not found');
            alert('Container element not found');
            return;
        }
    
        console.log('Container element found:', container);
    
        // Find the SVG element within the container
        const svgElement = container.querySelector('svg');
        if (!svgElement) {
            console.error('SVG element not found within the container');
            alert('SVG element not found within the container');
            return;
        }
    
        console.log('SVG element found:', svgElement);
        console.log('SVG element outerHTML:', svgElement.outerHTML);
    
        try {
            // Get SVG data
            const svgData = new XMLSerializer().serializeToString(svgElement);
            console.log('Serialized SVG data:', svgData);
            
            // Create a data URI
            const svgDataUri = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
            console.log('SVG Data URI created');
            
            // Create image
            const img = new Image();
            img.onload = function() {
                console.log('Image loaded successfully');
                console.log('Image dimensions:', img.width, 'x', img.height);
                
                const promptResolution = prompt("Enter the desired scaling factor (e.g., 1.5 for 150% resolution):");
                if (promptResolution) {
                    const scaleFactor = parseFloat(promptResolution);
                    if (!isNaN(scaleFactor) && scaleFactor > 0) {
                        console.log('Scale factor:', scaleFactor);
                        
                        const canvas = document.createElement('canvas');
                        const ctx = canvas.getContext('2d');
                        canvas.width = img.width * scaleFactor;
                        canvas.height = img.height * scaleFactor;
                        
                        console.log('Canvas dimensions:', canvas.width, 'x', canvas.height);
                        
                        ctx.fillStyle = 'white';
                        ctx.fillRect(0, 0, canvas.width, canvas.height);
                        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                        
                        // Convert canvas to blob and download
                        canvas.toBlob(function(blob) {
                            if (blob) {
                                console.log('Blob created successfully');
                                const link = document.createElement('a');
                                link.download = 'graph.png';
                                link.href = URL.createObjectURL(blob);
                                link.click();
                                URL.revokeObjectURL(link.href);
                                console.log('Download link clicked');
                            } else {
                                console.error('Failed to create blob');
                                alert('Failed to create image. Please try again.');
                            }
                        }, 'image/png');
                    } else {
                        console.error('Invalid scale factor:', promptResolution);
                        alert("Invalid scaling factor. Please enter a positive number.");
                    }
                } else {
                    console.log('User cancelled the prompt');
                }
            };
            img.onerror = function() {
                console.error('Error loading image');
                console.log('SVG Data URI:', svgDataUri);
                alert('Failed to load SVG image. Please check the console for more details.');
            };
            console.log('Setting image source');
            img.src = svgDataUri;
        } catch (error) {
            console.error('Error saving diagram as PNG:', error);
            alert('An error occurred while saving the diagram. Please try again.');
        }
    }
    
    
        

    saveDiagramAsSVG = (id) => {
        const svgElement = document.getElementById(id);
        if (!svgElement) {
            console.error('SVG element not found');
            return;
        }

        try {
            const svgData = new XMLSerializer().serializeToString(svgElement);
            const svgBlob = new Blob([svgData], {type: 'image/svg+xml;charset=utf-8'});
            const downloadLink = document.createElement('a');
            downloadLink.href = URL.createObjectURL(svgBlob);
            downloadLink.download = `diagram-${id}.svg`;
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
            URL.revokeObjectURL(downloadLink.href);
        } catch (error) {
            console.error('Error saving diagram as SVG:', error);
        }
    }    

    async renderMermaidDiagrams(text) {
        const mermaidCodeRegex = /```mermaid\n([\s\S]*?)```/g;
        let match;
        let lastIndex = 0;
        let result = '';

        while ((match = mermaidCodeRegex.exec(text)) !== null) {
            const mermaidCode = match[1];
            const uniqueId = 'mermaid-' + Math.random().toString(36).substr(2, 9);

            // Add the text before the Mermaid diagram
            result += text.slice(lastIndex, match.index);

            try {
                const renderResult = await mermaid.render(uniqueId, mermaidCode);
                const htmlCode = `
                    <div class="mermaid-container relative flex justify-center items-center mt-4 mb-4 w-full">
                        <div class="mermaid-diagram bg-white p-4 rounded-lg shadow-md overflow-hidden w-full" style="max-height: 80vh;">
                            <div id="${uniqueId}" class="mermaid-zoom-pan" style="transform-origin: 0 0; transition: transform 0.1s;">
                                ${renderResult.svg}
                            </div>
                        </div>
                        <div class="absolute top-2 right-2 flex gap-1">
                            <button onclick="mr.zoomDiagram('${uniqueId}', 1.1)" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="11" cy="11" r="8"></circle>
                                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                                    <line x1="11" y1="8" x2="11" y2="14"></line>
                                    <line x1="8" y1="11" x2="14" y2="11"></line>
                                </svg>
                            </button>
                            <button onclick="mr.zoomDiagram('${uniqueId}', 0.9)" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="11" cy="11" r="8"></circle>
                                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                                    <line x1="8" y1="11" x2="14" y2="11"></line>
                                </svg>
                            </button>
                            <button onclick="mr.resetDiagramZoomPan('${uniqueId}')" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                Reset
                            </button>
                            <button onclick="mr.saveDiagramAsPNG('${uniqueId}')" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                PNG
                            </button>
                            <button onclick="mr.saveDiagramAsSVG('${uniqueId}')" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                SVG
                            </button>
                        </div>
                    </div>
                `;
                result += htmlCode;

                // Initialize zoom and pan for this Mermaid diagram
                this.initDiagramZoomPan(uniqueId);
            } catch (error) {
                console.error('Mermaid rendering failed:', error);
                result += `<div class="mermaid-error bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">Failed to render diagram</div>`;
            }

            lastIndex = mermaidCodeRegex.lastIndex;
        }

        // Add any remaining text after the last Mermaid diagram
        result += text.slice(lastIndex);

        return result;
    }
    async renderGraphvizDiagrams(text) {
        // Check if viz.js is loaded
        if (typeof Viz === 'undefined') {
            console.warn('Viz.js is not loaded. Graphviz diagrams will not be rendered.');
            return text;
        }

        const graphvizCodeRegex = /```graphviz\n([\s\S]*?)```/g;
        let match;
        let lastIndex = 0;
        let result = '';

        while ((match = graphvizCodeRegex.exec(text)) !== null) {
            const graphvizCode = match[1];
            const uniqueId = 'graphviz-' + Math.random().toString(36).substr(2, 9);

            // Add the text before the Graphviz diagram
            result += text.slice(lastIndex, match.index);

            try {
                const viz = new Viz();
                const svgElement = await viz.renderSVGElement(graphvizCode);
                const svgString = new XMLSerializer().serializeToString(svgElement);

                const htmlCode = `
                    <div class="graphviz-container relative flex justify-center items-center mt-4 mb-4 w-full">
                        <div class="graphviz-diagram bg-white p-4 rounded-lg shadow-md overflow-hidden w-full" style="max-height: 80vh;">
                            <div id="${uniqueId}" class="diagram-zoom-pan" style="transform-origin: 0 0; transition: transform 0.1s;">
                                ${svgString}
                            </div>
                        </div>
                        <div class="absolute top-2 right-2 flex gap-1">
                            <button onclick="mr.zoomDiagram('${uniqueId}', 1.1)" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="11" cy="11" r="8"></circle>
                                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                                    <line x1="11" y1="8" x2="11" y2="14"></line>
                                    <line x1="8" y1="11" x2="14" y2="11"></line>
                                </svg>
                            </button>
                            <button onclick="mr.zoomDiagram('${uniqueId}', 0.9)" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="11" cy="11" r="8"></circle>
                                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                                    <line x1="8" y1="11" x2="14" y2="11"></line>
                                </svg>
                            </button>
                            <button onclick="mr.resetDiagramZoomPan('${uniqueId}')" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                Reset
                            </button>
                            <button onclick="mr.saveDiagramAsPNG('${uniqueId}')" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                PNG
                            </button>
                            <button onclick="mr.saveDiagramAsSVG('${uniqueId}')" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                SVG
                            </button>
                        </div>
                    </div>
                `;
                result += htmlCode;

                // Initialize zoom and pan for this Graphviz diagram
                this.initDiagramZoomPan(uniqueId, 'graphviz');
            } catch (error) {
                console.error('Graphviz rendering failed:', error);
                result += `<div class="graphviz-error bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">Failed to render diagram</div>`;
            }

            lastIndex = graphvizCodeRegex.lastIndex;
        }

        // Add any remaining text after the last Graphviz diagram
        result += text.slice(lastIndex);

        return result;
    }
    
    async renderSVG(text) {
        const svgCodeRegex = /```svg\n([\s\S]*?)```/g;
        let match;
        let lastIndex = 0;
        let result = '';

        while ((match = svgCodeRegex.exec(text)) !== null) {
            const svgCode = match[1];
            const uniqueId = 'svg-' + Math.random().toString(36).substr(2, 9);

            // Add the text before the SVG
            result += text.slice(lastIndex, match.index);

            try {
                // Wrap the SVG code in a div with a unique ID
                const htmlCode = `
                    <div class="svg-container relative flex justify-center items-center mt-4 mb-4 w-full">
                        <div class="svg-diagram bg-white p-4 rounded-lg shadow-md overflow-hidden w-full" style="max-height: 80vh;">
                            <div id="${uniqueId}" class="svg-zoom-pan" style="transform-origin: 0 0; transition: transform 0.1s;">
                                ${svgCode}
                            </div>
                        </div>
                        <div class="absolute top-2 right-2 flex gap-1">
                            <button onclick="mr.zoomDiagram('${uniqueId}', 1.1)" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="11" cy="11" r="8"></circle>
                                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                                    <line x1="11" y1="8" x2="11" y2="14"></line>
                                    <line x1="8" y1="11" x2="14" y2="11"></line>
                                </svg>
                            </button>
                            <button onclick="mr.zoomDiagram('${uniqueId}', 0.9)" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="11" cy="11" r="8"></circle>
                                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                                    <line x1="8" y1="11" x2="14" y2="11"></line>
                                </svg>
                            </button>
                            <button onclick="mr.resetDiagramZoomPan('${uniqueId}')" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                Reset
                            </button>
                            <button onclick="mr.saveDiagramAsPNG('${uniqueId}')" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                PNG
                            </button>
                            <button onclick="mr.saveDiagramAsSVG('${uniqueId}')" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold p-1 rounded">
                                SVG
                            </button>
                        </div>
                    </div>
                `;
                result += htmlCode;

                // Initialize zoom and pan for this SVG
                this.initZoomPan(uniqueId);
            } catch (error) {
                console.error('SVG rendering failed:', error);
                result += `<div class="svg-error bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">Failed to render SVG</div>`;
            }

            lastIndex = svgCodeRegex.lastIndex;
        }

        // Add any remaining text after the last SVG
        result += text.slice(lastIndex);

        return result;
    }

    initZoomPan(id) {
        this.svgState[id] = { scale: 1, translateX: 0, translateY: 0, isDragging: false, startX: 0, startY: 0 };

        // We'll add event listeners after a short delay to ensure the element is in the DOM
        setTimeout(() => {
            const container = document.getElementById(id);
            if (!container) return;

            container.addEventListener('wheel', (e) => this.handleWheel(e, id));
            container.addEventListener('mousedown', (e) => this.handleMouseDown(e, id));
            container.addEventListener('mousemove', (e) => this.handleMouseMove(e, id));
            container.addEventListener('mouseup', () => this.handleMouseUp(id));
            container.addEventListener('mouseleave', () => this.handleMouseUp(id));
        }, 100);
    }

    handleWheel(e, id) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        this.zoomSVG(id, delta);
    }

    handleMouseDown(e, id) {
        const state = this.svgState[id];
        state.isDragging = true;
        state.startX = e.clientX - state.translateX;
        state.startY = e.clientY - state.translateY;
    }

    handleMouseMove(e, id) {
        const state = this.svgState[id];
        if (!state.isDragging) return;

        state.translateX = e.clientX - state.startX;
        state.translateY = e.clientY - state.startY;
        this.updateTransform(id);
    }

    handleMouseUp(id) {
        if (this.svgState[id]) {
            this.svgState[id].isDragging = false;
        }
    }

    zoomSVG(id, delta) {
        const state = this.svgState[id];
        if (!state) return;

        state.scale *= delta;
        this.updateTransform(id);
    }

    resetZoomPan(id) {
        this.svgState[id] = { scale: 1, translateX: 0, translateY: 0, isDragging: false, startX: 0, startY: 0 };
        this.updateTransform(id);
    }

    updateTransform(id) {
        const container = document.getElementById(id);
        if (!container) return;

        const state = this.svgState[id];
        container.style.transform = `translate(${state.translateX}px, ${state.translateY}px) scale(${state.scale})`;
    }
    renderCodeBlocks(text) {
        const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
        
        return text.replace(codeBlockRegex, (match, language, code) => {
            language = language || 'plaintext';
            let highlightedCode;
            
            try {
                highlightedCode = hljs.highlight(code.trim(), { language: language }).value;
            } catch (error) {
                console.warn(`Language '${language}' is not supported by highlight.js. Falling back to plaintext.`);
                highlightedCode = hljs.highlight(code.trim(), { language: 'plaintext' }).value;
            }
            
            const lines = highlightedCode.split('\n');
            const numberedLines = lines.map((line, index) => 
                `<div class="code-line">
                    <span class="line-number">${(index + 1).toString().padStart(2, '0')}</span>
                    <span class="line-content">${line}</span>
                 </div>`
            ).join('');
            
            return `
                <div class="code-block">
                    <div class="code-header">
                        <span class="language">${language}</span>
                        <button onclick="mr.copyCode(this)" class="copy-button">Copy</button>
                    </div>
                    <pre class="code-content"><code class="hljs language-${language}">${numberedLines}</code></pre>
                </div>
            `;
        });
    }

    copyCode(button) {
        const codeBlock = button.closest('.code-block');
        const codeLines = codeBlock.querySelectorAll('.line-content');
        const codeText = Array.from(codeLines).map(line => line.textContent).join('\n');

        navigator.clipboard.writeText(codeText).then(() => {
            button.textContent = 'Copied!';
            setTimeout(() => {
                button.textContent = 'Copy';
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
            button.textContent = 'Failed';
            setTimeout(() => {
                button.textContent = 'Copy';
            }, 2000);
        });
    }
    


    handleInlineCode(text) {
      return text.replace(/`([^`]+)`/g, function(match, code) {
          return `<b>${code}</b>`;
      });
    }

    handleLatexEquations(text) {
        if (typeof katex === 'undefined') {
            console.error('KaTeX is not loaded. Make sure to include KaTeX scripts and CSS.');
            return text;
        }
    
        // Function to render a single equation
        function renderEquation(match, p1, p2, p3, offset, string) {
            const equation = p1 || p2 || p3;
            const isDisplayMode = match.startsWith('\\[') || match.startsWith('$$');
            
            try {
                return katex.renderToString(equation, {
                    displayMode: isDisplayMode,
                    throwOnError: false,
                    output: 'html'
                });
            } catch (e) {
                console.error("KaTeX rendering error:", e);
                return `<span class="math-error">${match}</span>`;
            }
        }
    
        // Handle display equations: \[...\] and $$...$$
        text = text.replace(/\\\[([\s\S]*?)\\\]|\$\$([\s\S]*?)\$\$/g, renderEquation);
    
        // Handle inline equations: \(...\) and $...$
        // Be careful not to match single $ used for currency
        text = text.replace(/\\\(([\s\S]*?)\\\)|\$(\S.*?\S|\S)\$/g, renderEquation);
    
        return text;
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
        let lines = text.split('\n');
        let inList = false;
        let inCodeBlock = false;
        let result = [];
        let currentParagraph = '';
    
        for (let i = 0; i < lines.length; i++) {
            let line = lines[i];
            let trimmedLine = line.trim();
    
            // Check for code blocks
            if (trimmedLine.startsWith('```')) {
                if (currentParagraph) {
                    result.push('<p>' + currentParagraph + '</p>');
                    currentParagraph = '';
                }
                inCodeBlock = !inCodeBlock;
                result.push(line);
                continue;
            }
    
            // If we're in a code block, don't process the line
            if (inCodeBlock) {
                result.push(line);
                continue;
            }
    
            // Check for list items
            if (trimmedLine.match(/^[-*+]\s/) || trimmedLine.match(/^\d+\.\s/)) {
                if (currentParagraph) {
                    result.push('<p>' + currentParagraph + '</p>');
                    currentParagraph = '';
                }
                if (!inList) {
                    result.push('<ul>');
                    inList = true;
                }
                result.push('<li>' + trimmedLine.replace(/^[-*+]\s/, '').replace(/^\d+\.\s/, '') + '</li>');
            } 
            // Check for headers
            else if (trimmedLine.startsWith('#')) {
                if (currentParagraph) {
                    result.push('<p>' + currentParagraph + '</p>');
                    currentParagraph = '';
                }
                let level = trimmedLine.match(/^#+/)[0].length;
                result.push(`<h${level}>${trimmedLine.replace(/^#+\s/, '')}</h${level}>`);
            }
            // Check for horizontal rules
            else if (trimmedLine.match(/^(-{3,}|\*{3,}|_{3,})$/)) {
                if (currentParagraph) {
                    result.push('<p>' + currentParagraph + '</p>');
                    currentParagraph = '';
                }
                result.push('<hr>');
            }
            // Handle empty lines
            else if (trimmedLine === '') {
                if (inList) {
                    result.push('</ul>');
                    inList = false;
                }
                if (currentParagraph) {
                    result.push('<p>' + currentParagraph + '</p>');
                    currentParagraph = '';
                }
                result.push('<br>'); // Add a line break for empty lines
            }
            // Regular text
            else {
                if (inList) {
                    result.push('</ul>');
                    inList = false;
                }
                currentParagraph += (currentParagraph ? '\n' : '') + line;
            }
        }
    
        // Close any open list
        if (inList) {
            result.push('</ul>');
        }
    
        // Add any remaining paragraph
        if (currentParagraph) {
            result.push('<p>' + currentParagraph + '</p>');
        }
    
        return result.join('\n');
    }
    

      
    initMathJax() {
        // Configure MathJax
        window.MathJax = {
          tex: {
            inlineMath: [['$', '$']],
            displayMath: [['$$', '$$'], ['\\[', '\\]']]
          },
          svg: {
            fontCache: 'global'
          },
          startup: {
            ready: () => {
              MathJax.startup.defaultReady();
              MathJax.startup.promise.then(() => {
                console.log('MathJax is loaded and ready');
                // You can add any post-initialization logic here
              });
            }
          }
        };
    
        // Load MathJax
        if (!window.MathJax) {
          const script = document.createElement('script');
          script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js';
          script.async = true;
          document.head.appendChild(script);
        }
      }
    async renderMarkdown(text) {
      // Handle Mermaid graphs first
      text = await this.renderMermaidDiagrams(text);

      text = await this.renderGraphvizDiagrams(text);
     

      // Handle SVG graphs first
      text = await this.renderSVG(text);

      
      // Handle code blocks with syntax highlighting and copy button
      text = await this.renderCodeBlocks(text);

      // Handle inline code
      text = this.handleInlineCode(text);
  
      // Handle LaTeX-style math equations
      text = this.handleLatexEquations(text);
  
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
// Make sure there is a global variable called mr that instanciate MarkdownRenderer
mr = new MarkdownRenderer()
