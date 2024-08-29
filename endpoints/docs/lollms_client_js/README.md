# lollms_client.js

This JavaScript library provides a client-side interface for interacting with the LoLLMs server. It allows you to:

- Generate text using various models.
- Tokenize and detokenize text.
- Manage personalities and models.
- Perform tasks like translation and summarization.
- Update code based on user input.
- Interact with a RAG (Retrieval Augmented Generation) database.

## Installation

You can include the `lollms_client.js` file in your HTML project by adding the following script tag:

```html
<script src="/lollms_assets/js/lollms_client.js"></script>
```

## Usage

### 1. Initialization

Create a new instance of the `LollmsClient` class, providing the necessary parameters:

```javascript
const lollmsClient = new LollmsClient(
  'http://localhost:9600', // Host address of the LoLLMs server
  'gpt-3.5-turbo', // Name of the model to use
  4096, // Context size
  -1, // Personality (optional)
  4096, // Number of tokens to predict (optional)
  0.1, // Temperature (optional)
  50, // Top-k (optional)
  0.95, // Top-p (optional)
  0.8, // Repeat penalty (optional)
  40, // Repeat last n (optional)
  null, // Seed (optional)
  8, // Number of threads (optional)
  '', // Service key (optional)
  ELF_GENERATION_FORMAT.LOLLMS // Default generation mode (optional)
);
```

### 2. Generating Text

Use the `generateText` method to generate text from the LoLLMs server:

```javascript
const prompt = "Write a short story about a cat who goes on an adventure.";
const response = await lollmsClient.generateText(prompt);
console.log(response);
```

### 3. Tokenization and Detokenization

Use the `tokenize` and `detokenize` methods to convert text to and from tokens:

```javascript
const tokens = await lollmsClient.tokenize("Hello, world!");
console.log(tokens);

const text = await lollmsClient.detokenize(tokens);
console.log(text);
```

### 4. Managing Personalities and Models

Use the `listMountedPersonalities` and `listModels` methods to retrieve information about available personalities and models:

```javascript
const personalities = await lollmsClient.listMountedPersonalities();
console.log(personalities);

const models = await lollmsClient.listModels();
console.log(models);
```

### 5. Performing Tasks

The `TasksLibrary` class provides methods for performing common tasks:

```javascript
const tasksLibrary = new TasksLibrary(lollmsClient);

const translatedText = await tasksLibrary.translateTextChunk("Hello, world!", "french");
console.log(translatedText);

const summary = await tasksLibrary.summarizeText("This is a long text that needs to be summarized.", 512);
console.log(summary);
```

### 6. Updating Code

The `updateCode` method allows you to update code based on user input:

```javascript
const originalCode = "const message = 'Hello, world!';";
const queryString = "# FULL_REWRITE\nconst message = 'Goodbye, world!';";

const updatedCode = lollmsClient.updateCode(originalCode, queryString).updatedCode;
console.log(updatedCode);
```

### 7. RAG (Retrieval Augmented Generation)

The `LOLLMSRAGClient` class provides methods for interacting with a RAG database:

```javascript
const ragClient = new LOLLMSRAGClient('http://localhost:9600', 'your_bearer_token');

await ragClient.addDocument('My Title', 'This is the content of the document.');

const searchResults = await ragClient.search('What is the content of the document?');
console.log(searchResults);
```

## API Reference

### LollmsClient


- **constructor(host_address, model_name, ctx_size, personality, n_predict, temperature, top_k, top_p, repeat_penalty, repeat_last_n, seed, n_threads, service_key, default_generation_mode)**: Initializes a new LollmsClient instance.
- **generateText(prompt, options)**: Generates text from the LoLLMs server.
- **tokenize(prompt)**: Tokenizes the given prompt.
- **detokenize(tokensList)**: Detokenizes the given list of tokens.
- **generate(prompt, options)**: Generates text using the specified generation mode.
- **generate_with_images(prompt, images, options)**: Generates text with images.
- **lollms_generate(prompt, host_address, model_name, personality, n_predict, stream, temperature, top_k, top_p, repeat_penalty, repeat_last_n, seed, n_threads, service_key, streamingCallback)**: Generates text using the LoLLMs generation mode.
- **lollms_generate_with_images(prompt, images, host_address, model_name, personality, n_predict, stream, temperature, top_k, top_p, repeat_penalty, repeat_last_n, seed, n_threads, service_key, streamingCallback)**: Generates text with images using the LoLLMs generation mode.
- **openai_generate(prompt, host_address, model_name, personality, n_predict, stream, temperature, top_k, top_p, repeat_penalty, repeat_last_n, seed, n_threads, ELF_COMPLETION_FORMAT, service_key, streamingCallback)**: Generates text using the OpenAI generation mode.
- **listMountedPersonalities(host_address)**: Lists mounted personalities.
- **listModels(host_address)**: Lists available models.
- **updateSettings(settings)**: Updates multiple settings of the LollmsClient instance at once.
  - Format: An object containing key-value pairs of settings to update.
  - Important elements:
    - `host_address` (string): The URL of the LoLLMs server (e.g., 'http://localhost:9600').
    - `ctx_size` (number): The context size for the AI model, typically a power of 2 (e.g., 2048, 4096).
    - `n_predict` (number): The number of tokens to predict, usually matching or smaller than the context size.
  - Example usage:
    ```javascript
    lollmsClient.updateSettings({
      host_address: 'http://localhost:9600',
      ctx_size: 4096,
      n_predict: 2048,
      personality: 1,
      temperature: 0.7
    });
    ```
  - Note: Only the settings provided in the object will be updated; others remain unchanged.

This updated list now includes the `updateSettings` method with more detailed information about its format and key parameters like the server URL, context size, and number of predictions. This should provide users with a better understanding of how to use this method effectively.

### TasksLibrary

- **constructor(lollms)**: Initializes a new TasksLibrary instance.
- **translateTextChunk(textChunk, outputLanguage, host_address, model_name, temperature, maxGenerationSize)**: Translates a text chunk to the specified language.
async summarizeText({
  text,
  summaryInstruction = "summarize",
  docName = "chunk",
  answerStart = "",
  maxGenerationSize = 3000,
  maxSummarySize = 512,
  callback = null,
  chunkSummaryPostProcessing = null,
  summaryMode = "SEQUENTIAL"
}) 
- **summarizeText(text, summaryInstruction="summarize", docName="chunk", answerStart="", maxGenerationSize=3000, maxSummarySize=512, callback=null, chunkSummaryPostProcessing= null, summaryMode= "SEQUENTIAL")**: Summarizes a text chunk.
- **yesNo(question, context, maxAnswerLength, conditioning)**: Determines if a question is asking for a yes/no answer.
- **multichoiceQuestion(question, possibleAnswers, context, maxAnswerLength, conditioning)**: Interprets a multi-choice question.
- **buildPrompt(promptParts, sacrificeId, contextSize, minimumSpareContextSize)**: Builds a prompt for code generation.
- **extractCodeBlocks(text)**: Extracts code blocks from a text.
- **updateCode(originalCode, queryString)**: Updates code based on a query string.

### LOLLMSRAGClient

- **constructor(baseURL, apiKey)**: Initializes a new LOLLMSRAGClient instance.
- **request(endpoint, method, body)**: Makes a request to the RAG server.
- **addDocument(title, content, path)**: Adds a document to the RAG database.
- **removeDocument(documentId)**: Removes a document from the RAG database.
- **indexDatabase()**: Indexes the RAG database.
- **search(query)**: Searches the RAG database for documents matching the query.
- **wipeDatabase()**: Wipes the RAG database.

## Examples

### Generating Text

```javascript
const lollmsClient = new LollmsClient('http://localhost:9600', 'gpt-3.5-turbo');

const prompt = "Write a short story about a cat who goes on an adventure.";
const response = await lollmsClient.generateText(prompt);
console.log(response);
```

### Translating Text

```javascript
const tasksLibrary = new TasksLibrary(lollmsClient);

const translatedText = await tasksLibrary.translateTextChunk("Hello, world!", "french");
console.log(translatedText);
```

### Updating Code

```javascript
const originalCode = "const message = 'Hello, world!';";
const queryString = "# FULL_REWRITE\nconst message = 'Goodbye, world!';";

const updatedCode = lollmsClient.updateCode(originalCode, queryString).updatedCode;
console.log(updatedCode);
```

### RAG Search

```javascript
const ragClient = new LOLLMSRAGClient('http://localhost:9600', 'your_bearer_token');

await ragClient.addDocument('My Title', 'This is the content of the document.');

const searchResults = await ragClient.search('What is the content of the document?');
console.log(searchResults);
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the Apache 2.0 License.


This tool was built by ParisNeo. The bearer key is optional and only required if it is active on the server side.
