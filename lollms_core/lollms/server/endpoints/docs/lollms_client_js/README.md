# LoLLMs Client JS Library Documentation

**Version:** 2.0
**Author:** ParisNeo
**Date:** 09/05/2025 (as per file header)

## Table of Contents

1.  [Introduction](#introduction)
2.  [Installation](#installation)
    *   [For LoLLMs WebUI Apps](#for-lollms-webui-apps)
    *   [For Standalone Projects](#for-standalone-projects)
3.  [Core Class: `LollmsClient`](#core-class-lollmsclient)
    *   [Constructor](#constructor)
    *   [Key Methods](#key-methods)
        *   [Settings Management](#settings-management)
        *   [Template Accessors](#template-accessors)
        *   [Tokenization](#tokenization)
        *   [Core Generation](#core-generation)
        *   [Specific Backend Generation](#specific-backend-generation)
        *   [Code Generation](#code-generation)
        *   [Utility Methods](#utility-methods)
        *   [Server Information](#server-information)
4.  [Utility Class: `TextChunker`](#utility-class-textchunker)
    *   [Constructor](#constructor-1)
    *   [Methods](#methods)
5.  [Utility Class: `TasksLibrary`](#utility-class-taskslibrary)
    *   [Constructor](#constructor-2)
    *   [Methods](#methods-1)
6.  [Utility Class: `LOLLMSRAGClient`](#utility-class-lollmsragclient)
    *   [Constructor](#constructor-3)
    *   [Methods](#methods-2)
7.  [UI Class: `LollmsSettingsUI`](#ui-class-lollmssettingsui)
    *   [Constructor](#constructor-4)
    *   [Methods](#methods-3)
    *   [Styling](#styling)
8.  [Enums and Constants](#enums-and-constants)
9.  [Example Usage](#example-usage)

---

## 1. Introduction

The `lollms_client.js` library provides a powerful JavaScript client for interacting with a LoLLMs (Lord of Large Language Models) server. It's designed to simplify common tasks such as text generation, code generation, image-assisted generation, tokenization, text chunking, and Retrieval Augmented Generation (RAG).

It supports multiple generation backends/formats:
*   LoLLMs (native)
*   OpenAI-compatible
*   Ollama-compatible
*   LiteLLM-compatible
*   vLLM-compatible

This library depends on `axios` for HTTP requests.

---

## 2. Installation

### For LoLLMs WebUI Apps

If you are building an application that will be served by the LoLLMs WebUI, the library and its dependencies are typically already available. You can include them in your HTML like this:

```html
<!-- Axios is required by lollms_client.js -->
<script src="/lollms_assets/js/axios.min.js"></script>
<!-- The LoLLMs Client library -->
<script src="/lollms_assets/js/lollms_client.js"></script>
```

### For Standalone Projects

If you are using this library in a standalone project not served by LoLLMs WebUI:
1.  **Download `lollms_client.js`**: Place it in your project's JavaScript directory.
2.  **Include Axios**: You can use a CDN or download `axios.min.js` and serve it locally.

```html
<!-- Example using Axios CDN -->
<script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
<!-- Path to your local copy of lollms_client.js -->
<script src="path/to/your/lollms_client.js"></script>
```

---

## 3. Core Class: `LollmsClient`

This is the main class for interacting with the LoLLMs server.

### Constructor

```javascript
new LollmsClient(
  host_address = null,         // String: URL of the LoLLMs server (e.g., "http://localhost:9600")
  model_name = null,           // String: Default model name to use for generation
  ctx_size = null,             // Number: Default context size for the model
  personality = -1,            // Number: Default personality ID (or -1 for server default)
  n_predict = null,            // Number: Default max tokens to predict (null for model default)
  temperature = 0.1,           // Number: Default temperature for sampling
  top_k = 50,                  // Number: Default top-k sampling
  top_p = 0.95,                // Number: Default top-p (nucleus) sampling
  repeat_penalty = 0.8,        // Number: Default repeat penalty
  repeat_last_n = 40,          // Number: Default window size for repeat penalty
  seed = null,                 // Number: Default seed for generation (null for random)
  n_threads = 8,               // Number: Default number of threads for generation (model dependent)
  service_key = "",            // String: API key for services requiring authentication
  default_generation_mode = ELF_GENERATION_FORMAT.LOLLMS, // Enum or String: Default generation API format
  verify_ssl_certificate = true // Boolean: Whether to verify SSL certs (mainly for Node.js vLLM calls)
)
```
*   If `host_address` is `null`, requests will be made to relative paths (e.g., `/lollms_generate`), assuming the client code is served from the same domain as the LoLLMs server.
*   The constructor asynchronously fetches prompt templates from the server.

### Key Methods

#### Settings Management

*   **`updateSettings(settings)`**
    *   Updates multiple client settings at once.
    *   `settings`: An object where keys are setting names (e.g., `model_name`, `temperature`) and values are the new settings.
    ```javascript
    lollms.updateSettings({
        model_name: "new_model",
        temperature: 0.7,
        default_generation_mode: "OPENAI" // or ELF_GENERATION_FORMAT.OPENAI
    });
    ```

*   **`updateServerAddress(newAddress)`**
    *   Changes the `host_address` of the LoLLMs server.
    *   `newAddress` (String): The new server URL.

#### Template Accessors

These methods return parts of the prompt template fetched from the server, useful for constructing well-formatted prompts.
*   `separatorTemplate()`: Returns the message separator string.
*   `system_message()`: Returns the start of a system message block (e.g., `!@>system: `).
*   `custom_system_message(msg)`: Returns a system message block with custom content.
*   `ai_message(ai_name="assistant")`: Returns the start of an AI message block.
*   `user_message(user_name="user")`: Returns the start of a user message block.
*   `custom_message(message_name="message")`: Returns the start of a generic message block.

Example:
```javascript
const prompt = lollms.system_message() + "You are a helpful assistant." +
               lollms.separatorTemplate() +
               lollms.user_message() + "Tell me a joke." +
               lollms.separatorTemplate() +
               lollms.ai_message();
```

#### Tokenization

*   **`async tokenize(prompt, return_named=false)`**
    *   Tokenizes the given prompt using the server's current model.
    *   `prompt` (String): The text to tokenize.
    *   `return_named` (Boolean): If `true`, server might return a more structured response (e.g., `{tokens: [...]}`). Default is `false`.
    *   Returns: An array of tokens or a structured object.

*   **`async detokenize(tokensList, return_named=false)`**
    *   Converts a list of tokens back into text.
    *   `tokensList` (Array): The list of tokens.
    *   `return_named` (Boolean): If `true`, server might expect/return a structured response.
    *   Returns: The detokenized string or a structured object.

#### Core Generation

These are the primary methods for text generation, automatically using the `default_generation_mode`.

*   **`generate(prompt, options = {})`**
    *   The main method for text generation.
    *   `prompt` (String): The input prompt.
    *   `options` (Object): Overrides for default generation parameters.
        *   `n_predict` (Number)
        *   `stream` (Boolean): If `true`, attempts streaming (behavior depends on backend & `streamingCallback`).
        *   `temperature` (Number)
        *   `top_k` (Number)
        *   `top_p` (Number)
        *   `repeat_penalty` (Number)
        *   `repeat_last_n` (Number)
        *   `seed` (Number)
        *   `n_threads` (Number)
        *   `service_key` (String)
        *   `streamingCallback` (Function): `function(chunk, type)` called with generated text chunks.
            *   `chunk` (String/Object): The piece of data from the stream.
            *   `type` (String): e.g., `'MSG_TYPE_CHUNK'`, `'MSG_TYPE_FULL_RESPONSE_CHUNK'`, `'MSG_TYPE_STREAM_END'`.
            *   If the callback returns `false`, streaming may be aborted.
    *   Returns: A Promise resolving to the generated text (if not streaming or if stream accumulates) or a JSON object (depends on backend).

*   **`generate_with_images(prompt, images, options = {})`**
    *   Generates text based on a prompt and one or more images.
    *   `prompt` (String): The text prompt.
    *   `images` (Array of Strings): An array of image paths or data URLs. These will be base64 encoded client-side for OpenAI mode, or passed as-is for LoLLMs mode.
    *   `options` (Object): Same as `generate()`, plus vision-model specific options for OpenAI mode (e.g., `max_image_width`).
    *   Currently, full support is best for `ELF_GENERATION_FORMAT.LOLLMS` and `ELF_GENERATION_FORMAT.OPENAI` (e.g., with GPT-4 Vision). Other modes may have limited or no support.

*   **`async generateText(prompt, options = {})`**
    *   A convenience method specifically for generating text using the `LOLLMS` generation mode. It's essentially a wrapper around `lollms_generate`.
    *   `prompt` (String): The input prompt.
    *   `options` (Object): Similar to `generate()`, but parameters are passed directly to `lollms_generate`.

#### Specific Backend Generation

These methods allow direct calls to specific backend generation endpoints, bypassing the `default_generation_mode` logic. They generally take more explicit parameters.

*   `async lollms_generate(prompt, host_address, model_name, ..., streamingCallback)`: For LoLLMs native generation.
*   `async lollms_generate_with_images(prompt, images, host_address, ..., streamingCallback)`: LoLLMs native with images.
*   `async openai_generate(prompt, host_address, ..., streamingCallback)`: For OpenAI-compatible endpoints (can be LoLLMs server adapting or a direct OpenAI proxy).
*   `async openai_generate_with_images(prompt, images, options = {})`: For OpenAI-compatible vision models (e.g., GPT-4V). Takes an `options` object. Handles client-side image encoding and SSE streaming.
*   `async ollama_generate(...)`: Template, currently forwards to `openai_generate`. Needs verification for specific Ollama parameters.
*   `async litellm_generate(...)`: Template, currently forwards to `openai_generate`. Needs verification for specific LiteLLM parameters.
*   `async vllm_generate(options)`: For vLLM's OpenAI-compatible API.
    *   Takes a single `options` object: `{ prompt, host_address, model_name, n_predict, stream, temperature, top_p, repeat_penalty, seed, completion_format, service_key, streamingCallback }`.
    *   Supports SSL verification toggle via `this.verifySslCertificate`.

#### Code Generation

*   **`async generateCode(prompt, template=null, language="json", images=[], options={})`**
    *   Generates a single code block.
    *   `prompt` (String): Instruction for code generation.
    *   `template` (String, optional): A template for the expected code structure.
    *   `language` (String): Target programming language.
    *   `images` (Array, optional): Images for multimodal code generation.
    *   `options` (Object): Generation parameters like `n_predict`, `temperature`, `streamingCallback`.
    *   Attempts to extract the first valid code block. If the AI indicates incompleteness, it will try to prompt for continuation.
    *   Returns: A string containing the generated code, or `null` on failure.

*   **`async generateCodes(prompt, images=[], options={})`**
    *   Generates multiple code blocks from a single AI response.
    *   Parameters are similar to `generateCode` (but no `template` or `language` as it expects multiple, potentially different, blocks).
    *   Returns: An array of objects, each representing a code block: `{ language: "...", content: "...", fileName: "..." }`.

#### Utility Methods

*   **`extractCodeBlocks(text, return_remaining_text = false)`**
    *   Parses text to find markdown code blocks (e.g., \`\`\`python ... \`\`\`).
    *   Also looks for `<file_name>...</file_name>` tags preceding code blocks.
    *   `text` (String): The text to parse.
    *   `return_remaining_text` (Boolean): If true, returns an object `{ codes, remainingText }`.
    *   Returns: An array of code block objects `{ fileName, content, type, is_complete }`, or an object if `return_remaining_text` is true.

*   **`async encode_image(image_path_or_data_url, max_image_width = -1)`**
    *   (Browser-specific) Encodes an image to a base64 JPEG string. Resizes if `max_image_width` is provided and positive.
    *   `image_path_or_data_url` (String): URL or data URI of the image.
    *   `max_image_width` (Number): Maximum width for resizing.
    *   Returns: A Promise resolving to the base64 data (without `data:image/jpeg;base64,` prefix).

#### Server Information

*   **`async listMountedPersonalities(host_address = this.host_address)`**
    *   Fetches the list of currently mounted personalities from the server.
    *   Returns: A Promise resolving to an array of personality objects or `null` on error.

*   **`async listModels(host_address = this.host_address)`**
    *   Fetches the list of available models from the server.
    *   Returns: A Promise resolving to an array of model objects or `null` on error.

---

## 4. Utility Class: `TextChunker`

Helps break down large texts into smaller, manageable chunks, optionally using a tokenizer.

### Constructor

```javascript
new TextChunker(chunkSize = 1024, overlap = 0, tokenizer = null)
```
*   `chunkSize` (Number): Target size of chunks (in tokens if tokenizer provided, otherwise character-based or paragraph-based).
*   `overlap` (Number): Number of tokens/paragraphs to overlap between chunks.
*   `tokenizer` (Object, optional): An object with `async tokenize(text)` and `async detokenize(tokens)` methods (like `LollmsClient` instance). If not provided, uses a simple space-based fallback for `getTextChunks`.

### Methods

*   **`async getTextChunks(text, docDetails = {name: "document"}, cleanChunk = true, minNbTokensInChunk = 10)`**
    *   Splits text by paragraphs (`\n\n`) and groups them into chunks aiming for `this.chunkSize` tokens.
    *   `docDetails` (Object): Metadata for the document.
    *   Returns: Array of chunk objects: `{ doc, id, text, tokens }`.

*   **`static async chunkText(text, tokenizer, chunkSize = 1024, overlap = 0, cleanChunk = true, minNbTokensInChunk = 10)`**
    *   A more robust static method for token-based chunking.
    *   **Requires** a valid `tokenizer`.
    *   Splits large paragraphs if they exceed `chunkSize`.
    *   Returns: Array of chunk text strings.

*   **`static removeUnnecessaryReturns(paragraph)`**: Removes empty lines within a paragraph.
*   **`static async splitLargeParagraph(paragraph, tokenizer, chunkSize, overlap)`**: Splits a single paragraph that's too large.

---

## 5. Utility Class: `TasksLibrary`

Provides higher-level NLP task functionalities built on top of `LollmsClient`.

### Constructor

```javascript
new TasksLibrary(lollmsClientInstance)
```
*   `lollmsClientInstance` (LollmsClient): A configured instance of `LollmsClient`.

### Methods

*   **`async translateTextChunk(textChunk, outputLanguage = "french", options = {})`**: Translates a text chunk.
*   **`async tokenize(text)` / `async detokenize(tokens)`**: Wrappers for `LollmsClient` tokenization.
*   **`async summarizeText(text, summaryInstruction, ..., summaryMode = "SEQUENTIAL", ...)`**
    *   Summarizes text, potentially iteratively for very long texts.
    *   `summaryMode`: `"SEQUENTIAL"` (context-aware chunk summarization) or `"MAP_REDUCE"` (summarize chunks independently then combine).
    *   `maxSummarySizeInTokens`: Target maximum token count for the final summary.
    *   `callback`: For progress updates.
*   **`async smartDataExtraction(text, dataExtractionInstruction, ...)`**: Placeholder for structured data extraction, uses `summarizeText` structure.
*   **`async summarizeChunks(chunks, summaryInstruction, ..., summaryMode = "SEQUENTIAL", ...)`**: Core logic for summarizing an array of text chunks.
*   **`async sequentialChunksSummary(chunks, ...)`**: A specific pairwise chunk summarization strategy.
*   **`async yesNo(question, context = "", ...)`**: Asks a yes/no question. Returns `true` for "yes", `false` for "no".
*   **`async multichoiceQuestion(question, possibleAnswers, context = "", ...)`**: Asks a multiple-choice question. Returns the index of the selected answer or -1.
*   **`buildPrompt(promptParts, sacrificeId = -1, ...)`**: (Intended to be async) Constructs a prompt from parts, potentially truncating a "sacrificial" part if total length exceeds context size. *Note: Current implementation has synchronous aspects with async tokenization, which might need refactoring in the library for perfect token-based truncation.*
*   **`updateCode(originalCode, queryString)`**: Modifies code based on a query string with directives like `#FULL_REWRITE ...`, `#ORIGINAL ... #SET ...`.
    *   Returns: `{ updatedCode, modifications, hasQuery }`.

---

## 6. Utility Class: `LOLLMSRAGClient`

Client for interacting with LoLLMs RAG (Retrieval Augmented Generation) server endpoints.

### Constructor

```javascript
new LOLLMSRAGClient(lollmsClientInstance)
```
*   `lollmsClientInstance` (LollmsClient): Used to get `host_address` and `service_key`. A separate random `key` is generated for RAG operations (this key is sent in the body of RAG requests).

### Methods

All methods return Promises resolving to the server's JSON response. They internally handle adding the RAG `key` to requests.

*   **`async addDocument(title, content, path = "unknown", metadata = {})`**: Adds a document to the RAG database.
*   **`async removeDocument(documentId)`**: Removes a document by its ID (often its path).
*   **`async indexDatabase()`**: Triggers indexing of the database.
*   **`async search(query, top_k = 5, filters = {})`**: Searches the RAG database.
*   **`async wipeDatabase()`**: Deletes all documents from the RAG database.

---

## 7. UI Class: `LollmsSettingsUI`

A utility class to dynamically render a settings form for the `LollmsClient` and apply changes.

### Constructor

```javascript
new LollmsSettingsUI(lollmsClient, targetElementOrId)
```
*   `lollmsClient` (LollmsClient): The client instance whose settings will be managed.
*   `targetElementOrId` (HTMLElement | String): The DOM element or its ID where the settings UI will be rendered.

### Methods

*   **`render()`**
    *   Clears the target element and builds the settings form.
    *   Dynamically populates model and personality dropdowns by calling `lollmsClient.listModels()` and `lollmsClient.listMountedPersonalities()`.

*   **`apply()`**
    *   Reads values from the rendered form inputs.
    *   Calls `lollmsClient.updateSettings()` with the new values.
    *   If the host address changed, it re-populates model/personality lists.
    *   Shows a temporary "Settings Applied!" message.

### Styling

The `LollmsSettingsUI` generates HTML with specific CSS classes (e.g., `lollms-settings-form`, `lollms-settings-row`). You'll need to provide CSS to style these elements. A minimal example is provided in the library's comments:

```css
/* Minimal CSS Example */
.lollms-settings-form { display: flex; flex-direction: column; gap: 10px; padding: 15px; border: 1px solid #ccc; border-radius: 5px; }
.lollms-settings-row { display: flex; flex-direction: column; gap: 5px; align-items: flex-start; } /* Changed to column for better mobile / narrow views */
.lollms-settings-label { font-weight: bold; margin-bottom: 2px; }
.lollms-settings-input { padding: 8px; border: 1px solid #ddd; border-radius: 4px; width: 100%; box-sizing: border-box; }
.lollms-settings-input[type="checkbox"] { width: auto; align-self: flex-start; }
.lollms-settings-header { margin-top: 15px; margin-bottom: 5px; border-bottom: 1px solid #eee; padding-bottom: 5px;}
.lollms-settings-description { font-size: 0.8em; color: #555; margin-top: 2px; }
.lollms-settings-feedback { margin-top: 10px; color: green; font-weight: bold; }

/* Optional: For wider screens, make label and input side-by-side */
@media (min-width: 600px) {
  .lollms-settings-row {
    flex-direction: row;
    align-items: center; /* Align items vertically in the center */
  }
  .lollms-settings-label {
    width: 200px; /* Adjust as needed */
    flex-shrink: 0; /* Prevent label from shrinking */
    margin-bottom: 0;
  }
  .lollms-settings-input {
    flex-grow: 1; /* Allow input to take remaining space */
  }
  .lollms-settings-input[type="checkbox"] {
    margin-left: 0; /* Align checkbox with other inputs if label is on side */
  }
  .lollms-settings-description {
      width: 100%; /* Full width below label/input row */
      margin-left: 205px; /* Align with input field start if labels are fixed width */
      flex-basis: 100%; /* Make it take the full width of the flex container */
  }
}
```

---

## 8. Enums and Constants

*   **`ELF_GENERATION_FORMAT`**
    *   `LOLLMS: 0`
    *   `OPENAI: 1`
    *   `OLLAMA: 2`
    *   `LITELLM: 3`
    *   `VLLM: 4`
    Used to specify the API format for generation. Can be passed as string (e.g., "OPENAI") or enum value.

*   **`ELF_COMPLETION_FORMAT`**
    *   `Instruct: 0`
    *   `Chat: 1`
    Used by some generation methods (like `vllm_generate`) to indicate if the prompt is for an instruction-tuned model or a chat model.

---

## 9. Example Usage

```html
<!DOCTYPE html>
<html>
<head>
    <title>LoLLMs Client Test</title>
    <script src="/lollms_assets/js/axios.min.js"></script> <!-- Or CDN -->
    <script src="/lollms_assets/js/lollms_client.js"></script> <!-- Or local path -->
    <style>
        /* Add CSS from LollmsSettingsUI.styling section here */
        body { font-family: sans-serif; padding: 20px; }
        #output { margin-top: 20px; padding:10px; border: 1px solid #eee; white-space: pre-wrap; }
        #settingsContainer { margin-bottom:20px; }
        button { padding: 8px 15px; margin-top:10px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>LoLLMs Client JS Test</h1>

    <div id="settingsContainer"></div>
    <button id="applySettingsBtn">Apply LoLLMs Settings</button>
    <button id="generateBtn">Generate Text</button>
    <button id="summarizeBtn">Summarize Sample Text</button>

    <div id="output">Output will appear here...</div>

    <script>
        document.addEventListener('DOMContentLoaded', async () => {
            const outputDiv = document.getElementById('output');
            const lc = new LollmsClient("http://localhost:9600"); // Adjust host if needed

            // --- Settings UI ---
            const settingsUI = new LollmsSettingsUI(lc, "settingsContainer");
            document.getElementById('applySettingsBtn').addEventListener('click', () => {
                settingsUI.apply();
                outputDiv.textContent = "Settings applied. New model/personality lists (if host changed) might take a moment to load.";
            });

            // --- Basic Generation ---
            document.getElementById('generateBtn').addEventListener('click', async () => {
                outputDiv.textContent = "Generating...";
                try {
                    const prompt = lc.user_message() + "Tell me a very short story about a robot learning to paint.";
                    // Example of using streaming callback
                    let fullText = "";
                    await lc.generate(prompt, {
                        n_predict: 150,
                        stream: true,
                        streamingCallback: (chunk, type) => {
                            if (type === "MSG_TYPE_CHUNK") {
                                fullText += chunk;
                                outputDiv.textContent = fullText;
                                return true; // Continue streaming
                            } else if (type === "MSG_TYPE_STREAM_END") {
                                outputDiv.textContent = fullText + "\n\n--- Generation Complete ---";
                                return false; // Stop
                            }
                            // For MSG_TYPE_FULL_RESPONSE_CHUNK, you might just set fullText = chunk
                        }
                    });
                    // If not streaming or stream callback accumulates:
                    // const generatedText = await lc.generate(prompt, { n_predict: 150 });
                    // outputDiv.textContent = generatedText;

                } catch (error) {
                    console.error("Generation error:", error);
                    outputDiv.textContent = "Error generating text: " + error.message;
                }
            });

            // --- Tasks Library Example ---
            const tasks = new TasksLibrary(lc);
            document.getElementById('summarizeBtn').addEventListener('click', async () => {
                outputDiv.textContent = "Summarizing...";
                try {
                    const textToSummarize = "The quick brown fox jumps over the lazy dog. This is a classic pangram used to test typefaces. It contains all letters of the English alphabet. The fox is known for its cunning, and the dog for its loyalty, though in this sentence, it is simply characterized by its laziness. One wonders what adventures the fox might have after this acrobatic feat.";
                    const summary = await tasks.summarizeText(
                        textToSummarize,
                        "Provide a very brief summary of the provided text.",
                        "pangram_doc",
                        "", // answerStart
                        200, // maxGenerationSize for each summary step
                        50   // maxSummarySizeInTokens for the final summary
                    );
                    outputDiv.textContent = "Summary:\n" + summary;
                } catch (error) {
                    console.error("Summarization error:", error);
                    outputDiv.textContent = "Error summarizing text: " + error.message;
                }
            });

            // --- List Models (Example, logs to console) ---
            try {
                const models = await lc.listModels();
                console.log("Available models:", models);
                const personalities = await lc.listMountedPersonalities();
                console.log("Mounted personalities:", personalities);
            } catch (error) {
                console.error("Error fetching server info:", error);
            }
        });
    </script>
</body>
</html>
```

This example demonstrates:
1.  Initializing `LollmsClient`.
2.  Setting up `LollmsSettingsUI` and an "Apply" button.
3.  A "Generate Text" button that uses `lc.generate()` with a streaming callback.
4.  A "Summarize Sample Text" button that uses `TasksLibrary.summarizeText()`.
5.  Logging available models and personalities to the console.

Make sure your LoLLMs server is running and accessible at the specified `host_address`.
