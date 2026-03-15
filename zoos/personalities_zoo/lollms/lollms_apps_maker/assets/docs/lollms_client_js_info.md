## Lollms client Library Information

The Lollms library provides a robust framework for building applications that interact with Lollms as a client. This documentation will guide you through the essential steps to integrate and utilize the Lollms library effectively within your projects.


#### Importing Lollms in HTML

To start using the Lollms library in your HTML file, you need to include the following script tags:

```html
<script src="/lollms_assets/js/lollms_client_js"></script>
<script src="/lollms_assets/js/axios.min"></script>
```

> **Note:** The Lollms library requires Axios for making HTTP requests. Ensure that Axios is included in your HTML.

#### Initial Setup

Before using the Lollms client, you need to define a variable `ctx_size` which represents the size of the context for the LLM. This can be a fixed or modifiable value based on user requirements. It is recommended to store this value in local storage. The default context size is 4096 tokens.

Additionally, you can define `max_gen_size`, which indicates the maximum number of tokens the model can generate in one go. The default value for `max_gen_size` is also 4096 tokens.

#### Using Lollms Client in JavaScript

To generate text using the Lollms client, follow these steps:

1. **Build the Lollms Client:**

```javascript
const lc = new LollmsClient(
    host_address = null,  // Host address (default: http://localhost:9600 if null)
    model_name = null,    // Model name (default model used if null)
    ctx_size = 4096,      // Context size
    personality = -1,
    n_predict = 4096,     // Max tokens to be predicted
    temperature = 0.1,
    top_k = 50,
    top_p = 0.95,
    repeat_penalty = 0.8,
    repeat_last_n = 40,
    seed = null,
    n_threads = 8,
    service_key = "",
    default_generation_mode = ELF_GENERATION_FORMAT.LOLLMS
);
```
Supported generation modes:
ELF_GENERATION_FORMAT.LOLLMS : The default one that uses the lollms backend (key is optional)
ELF_GENERATION_FORMAT.OPENAI : Uses openai API as backend and requires a key
ELF_GENERATION_FORMAT.OLLAMA : Uses ollama API as backend (key is optional)
ELF_GENERATION_FORMAT.VLLM : Uses vllm API as backend (key is optional)

-1. **Change settings**
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


0. **Delimiters:**
Delimiters can be used while crafting a prompt to make the prompt match the format expected by the LLM.
`lc.separatorTemplate()` : the separator between dialogue roles
`lc.system_message()` : the system message keyword 
`lc.user_message()` : the user message start keyword 
`lc.ai_message()` : the ai message start keyword 
`lc.custom_message()` : a custom message header

Use these to structure the prompts. The last thing in the prompt must be lc.ai_message()
Best way is to structure the prompt as a system prompt followed by user input or data followed by ai message. The Ai will respond.

1. **Generate Text from a Prompt:**

To generate text, construct the prompt and use the `generate` method:

```javascript
// Build the prompt
const system_prompt = ""; // Instruction for the AI
const user_prompt = "";   // User prompt if applicable

let prompt = lc.system_message() + system_prompt + lc.template.separator_template + lc.ai_message();

if (user_prompt) {
    prompt = lc.system_message() + system_prompt + lc.template.separator_template + lc.user_message() + user_prompt + lc.template.separator_template + lc.ai_message();
}

// Generate text
const generated_text = await lc.generate(prompt);
```
if you want to send one or multiple images to the AI then use lc.generate_with_images instead of generate:
```javascript
// Generate text from a prompt and a list of images encoded in base64
const generated_text = await lc.generate_with_images(prompt, images);
```

2. **Generate a single code from a Prompt:**
```javascript
// This is the full signature of generateCode method
async generateCode(
  prompt, 
  template=null,
  language="json",
  images = [],  
  {
    n_predict = null,
    temperature = 0.1,
    top_k = 50,
    top_p = 0.95,
    repeat_penalty = 0.8,
    repeat_last_n = 40,
    streamingCallback = null
  } = {}
)
```
When you need to generate code, please use this function that allows a better generation of code, json, yaml etc...
```javascript
// Generate  code from prompt (the prompt must contain just the generation instruction without delimiters)
const code = await lc.generateCode(prompt);
// the generated code is a string without the markdown delimiters so you can directly parse it if applicable
if (code!=null){
  // Use the code
  // for example for json, here you can directly parse the code
  presentationData = JSON.parse(jsonStructure);
}
```
This is useful to recover structured data like json. Don't forget to give the format of the expected json in the prompt.
Make sure you give an example of the sytructure to force the AI to use exact code

  

```javascript
// Generate  code from prompt (the prompt must contain just the generation instruction without delimiters)
const code = await lc.generateCode(prompt,
                      // Example of template for jenerating a json with specific fields
                      template=`{
  "name":"string: the name",
  "age":int: the age,
}`,
  language="json");

// the generated code is a string without the markdown delimiters so you can directly parse it if applicable
if (code!=null){
  // Use the code
  // for example for json, here you can directly parse the code
  presentationData = JSON.parse(jsonStructure);
}
```

2. **Generate a list of Codes from a Prompt:**
When you need to generate a list of codes, please use this function that allows a better generation of multiple codes, json, yaml etc...
```javascript
// Generate  code
const codes = await lc.generateCodes(prompt);
if (codes.length>0){
  // Use the code
  codes.forEach(code => {
    console.log(code.language); // The language json, python, c, etc
    console.log(code.content); // The actual code that can be parsed if needed
  });
}
```
Make sure to explicitely instruct the LLM togenerate the codes in the right order in the prompt.
#### Tokenization Functions

The `LollmsClient` also provides functions for tokenization and detokenization, enabling you to convert prompts to tokens and vice versa.

1. **Tokenize a Prompt:**

```javascript
tokens = await lc.tokenize(prompt, return_named=false/*optional*/)
```

- The `tokenize` function sends a prompt to the Lollms API and receives a response containing two types of tokens:
  - **raw_tokens:** A list of integer token IDs.
  - **named_tokens:** A list of lists, where each inner list contains a token ID and its corresponding string representation.

2. **Detokenize a List of Tokens:**

```javascript
text = await detokenize(tokensList, return_named=false/*optional*/) 
```

- The `detokenize` function takes a list of token IDs and sends it to the Lollms API, which returns the corresponding text string or a named version of the tokens which is a list of the tokens and their corresponding text.


Note:
When generating, use a spinner to show that the system is buzy:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Toggleable Spinning Strawberry Loader</title>
    <style>
        html,body{margin:0;padding:0;height:100%;overflow:hidden}
        body{display:flex;justify-content:center;align-items:center;background:#fff;font-family:sans-serif}
        .overlay{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(255,255,255,0.8);display:none;justify-content:center;align-items:center}
        .loading{text-align:center;color:#ff69b4}
        .strawberry{font-size:64px;animation:spin 2s linear infinite}
        @keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(-360deg)}}
    </style>
</head>
<body>
    <div id="loadingOverlay" class="overlay">
        <div class="loading">
            <div class="strawberry">🌟</div>
            <div style="margin-top:20px">Interrogating L🌟LLMS ...</div>
        </div>
    </div>

    <script>
        function showLoader() {
            document.getElementById('loadingOverlay').style.display = 'flex';
        }

        function hideLoader() {
            document.getElementById('loadingOverlay').style.display = 'none';
        }
        hideLoader()
    </script>
</body>
</html>
```
