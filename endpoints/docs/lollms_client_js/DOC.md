# LollmsClient Quick Start

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

1. Initialize:
   ```javascript
   const client = new LollmsClient('http://localhost:9600', <(optional) model name>);
   ```

2. Generate Text:
   ```javascript
   const response = await client.generateText("Write a short story.");
   console.log(response);
   ```

3. Tokenize/Detokenize:
   ```javascript
   const tokens = await client.tokenize("Hello, world!");
   // the tokens are a list of a list, the first entry is the token text and the second is the token id
   // Extract only the token IDs from the tokenized result
   const tokenIds = tokens.map(token => token[1]);
   // Use the token IDs for detokenization
   const text = await client.detokenize(tokenIds);
   ```

4. List Resources:
   ```javascript
   const personalities = await client.listMountedPersonalities();
   const models = await client.listModels();
   ```
