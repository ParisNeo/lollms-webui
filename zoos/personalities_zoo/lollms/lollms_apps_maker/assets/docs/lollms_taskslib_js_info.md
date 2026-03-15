
#### Advanced Usage with TasksLibrary

The `TasksLibrary` provides advanced functionalities such as summarization, yes/no questions, multi-choice questions, and code updating.

1. **Initialize TasksLibrary:**

```javascript
const tl = new TasksLibrary(lc); // lc is a LollmsClient object
```

2. **Summarize Text:**
prototype:
```javascript
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
```
```javascript
async function summarizeText(textChunk, summaryLength = 512, summaryInstruction="Summarize the text") {
    return await tl.summarizeText(textChunk, summaryLength, lc.host_address, lc.model_name, lc.temperature, 1000);
}
```
3. **Smart data extraction from A long document:**
If the input document is very large to process, you can use this method to chunk the document into pieces, extract any relevant information for each piece, then synthesize a final response using what was learned from chunks.
Make sure you use this if the input text is larger than the 75% of the context size. 
prototype:
```javascript
async smartDataExtraction({
  text,
  dataExtractionInstruction = "summarize the current chunk.",
  finalTaskInstruction = "reformulate with better wording",
  docName = "chunk",
  answerStart = "",
  maxGenerationSize = 3000,
  maxSummarySize = 512,
  callback = null,
  chunkSummaryPostProcessing = null,
  summaryMode = "SEQUENTIAL"
})
``` 

1. **Extract Code Blocks:**

```javascript
const codes = tl.extractCodeBlocks(text);

// Process extracted code blocks
if (codes.length > 0) {
    codes.forEach(code => {
        console.log(code.content);
    });
}
```

4. **Yes/No Questions:**

```javascript
const isYes = await tl.yesNo("Is this a question?", "Context about the question", 50, "Optional conditioning message");

if (isYes) {
    console.log("The answer is yes.");
} else {
    console.log("The answer is no.");
}
```

5. **Update Code:**

```javascript
  updateCode(originalCode, queryString)
```

You can use the `updateCode()` function in your `TasksLibrary` class like this:

```javascript
const tl = new TasksLibrary();
const originalCode = `
def my_function(a, b):
    return a + b
my_function(2,5)
`;

const queryString = `
# REPLACE
# ORIGINAL
def my_function(a, b):
    return a + b
# SET
def my_function(x, y):
    return x * y
`;

const updatedCode = tl.updateCode(originalCode, queryString);
console.log(updatedCode);
```

This will output:

```python
def my_function(x, y):
    return x * y
my_function(2,5)
```

#### Important Considerations

- **Text Processing Only:** Lollms can only process text. For operations that are not text generation (e.g., accessing the internet, recovering the content of a page), manually perform the operation and send the extracted text to Lollms.
- **Context Size Configuration:** Use a context size of 128000 if required, and make it configurable along with the host path.
