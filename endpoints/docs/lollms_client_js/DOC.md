# LollmsClient Quick Start

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
