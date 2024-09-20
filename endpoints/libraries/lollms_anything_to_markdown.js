class LollmsFileLoader {
    constructor() {
        this.supportedExtensions = [
            'txt', 'md', 'markdown', 'rtf', 'log', 'csv', 'json', 'xml',
            'html', 'htm', 'css', 'js', 'py', 'java', 'c', 'cpp',
            'docx', 'pdf', 'pptx'
        ];
    }

    async loadFile(file) {
        const fileExtension = file.name.split('.').pop().toLowerCase();
        if (!this.supportedExtensions.includes(fileExtension)) {
            throw new Error('Unsupported file type');
        }

        let content = '';
        switch (fileExtension) {
            case 'docx':
                content = await this.readDocxFile(file);
                break;
            case 'pdf':
                content = await this.readPdfFile(file);
                break;
            case 'pptx':
                content = await this.readPptxFile(file);
                break;
            default:
                content = await this.readTextFile(file);
        }

        return this.convertToMarkdown(content, fileExtension);
    }

    readTextFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(e);
            reader.readAsText(file);
        });
    }

    readDocxFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = function(e) {
                mammoth.extractRawText({arrayBuffer: e.target.result})
                    .then(result => resolve(result.value))
                    .catch(reject);
            };
            reader.onerror = (e) => reject(e);
            reader.readAsArrayBuffer(file);
        });
    }

    async readPdfFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = async function(e) {
                try {
                    const pdf = await pdfjsLib.getDocument({data: e.target.result}).promise;
                    let content = '';
                    
                    for (let i = 1; i <= pdf.numPages; i++) {
                        const page = await pdf.getPage(i);
                        const textContent = await page.getTextContent();
                        content += textContent.items.map(item => item.str).join(' ') + '\n\n';
                    }
                    
                    resolve(content.trim());
                } catch (error) {
                    console.error("Error processing PDF:", error);
                    reject(error);
                }
            };
            reader.onerror = (e) => reject(e);
            reader.readAsArrayBuffer(file);
        });
    }
    readPptxFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = async function(e) {
                try {
                    const arrayBuffer = e.target.result;
                    const pptx2json = new PPTX2Json();
                    
                    // Create a Blob from the ArrayBuffer
                    const blob = new Blob([arrayBuffer], { type: file.type });
                    
                    // Create a temporary URL for the Blob
                    const url = URL.createObjectURL(blob);
                    
                    // Use the URL with toJson
                    const result = await pptx2json.toJson(url);
                    
                    let text = '';
                    result.slides.forEach((slide, index) => {
                        text += `Slide ${index + 1}:\n`;
                        slide.data.forEach(item => {
                            if (item.type === 'text') {
                                text += item.text + '\n';
                            }
                        });
                        text += '\n';
                    });
                    
                    // Clean up the temporary URL
                    URL.revokeObjectURL(url);
                    
                    resolve(text);
                } catch (error) {
                    console.error('Error extracting text from PPTX:', error);
                    reject(new Error('Unable to process PPTX file. ' + error.message));
                }
            };
            reader.onerror = (e) => reject(e);
            reader.readAsArrayBuffer(file);
        });
    }
    
    
    
    
    convertToMarkdown(content, fileExtension) {
        // Basic conversion to markdown
        // This can be extended for more sophisticated conversions
        let markdown = '';

        const lines = content.split('\n');
        let inCodeBlock = false;

        for (let line of lines) {
            line = line.trim();
            if (line === '') {
                markdown += '\n';
                continue;
            }

            // Check for headings
            if (line.startsWith('#')) {
                markdown += line + '\n';
            } 
            // Check for lists
            else if (line.match(/^[\u2022\u25E6\u25AA\u25AB\u25CF\u25CB\u25A0\u25A1]/)) {
                markdown += '- ' + line.substring(1).trim() + '\n';
            }
            // Check for code blocks
            else if (line.startsWith('```')) {
                inCodeBlock = !inCodeBlock;
                markdown += line + '\n';
            }
            // Regular text
            else {
                if (inCodeBlock) {
                    markdown += line + '\n';
                } else {
                    markdown += line + '\n\n';
                }
            }
        }

        return markdown.trim();
    }
}

// Usage example:
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const fileLoader = new LollmsFileLoader();
    try {
        const markdown = await fileLoader.loadFile(file);
        console.log(markdown);
        // You can now use the markdown content as needed
    } catch (error) {
        console.error('Error processing file:', error);
        alert('Error processing file: ' + error.message);
    }
}
