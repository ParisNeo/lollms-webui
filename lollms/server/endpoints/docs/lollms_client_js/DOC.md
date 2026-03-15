## Instructions for LLM: Using `lollms_client.js` Effectively & Managing Context

You are an AI assistant tasked with generating JavaScript code that uses the `lollms_client.js` library. Your primary goal is to produce functional, efficient code that interacts with a LoLLMs server. A critical aspect of this is **managing the language model's context window** to prevent errors and ensure optimal performance.

**Assume you have a pre-instantiated `LollmsClient` object available as `lc` and a `TasksLibrary` object as `tasks` (i.e., `const tasks = new TasksLibrary(lc);`).**

**Core Principles for Context Management:**

1.  **Be Aware of Context Limits:** Remember that every call to `lc.generate()` (or related generation methods) consumes context. The context includes the prompt you send and the space needed for the model's reply. The `lc.ctx_size` property holds the *model's* context size.
2.  **Input Preprocessing is Key:** Do not blindly pass large amounts of text (e.g., full documents, long chat histories) directly into a generation prompt.
3.  **Output Control:** Use the `n_predict` parameter wisely to limit the length of the AI's response, reserving context.
4.  **Iterative Processing for Large Data:** For tasks involving large texts (summarization, Q&A over documents), break them down.

**Specific Strategies Using `lollms_client.js`:**

**1. Handling Large Text Inputs (e.g., Documents, User Pastes):**

*   **Use `TextChunker`:**
    *   When the input text is long, **ALWAYS** consider using `TextChunker.chunkText(text, lc, chunkSize, overlap)` to split it into manageable pieces *before* processing with generation.
    *   `chunkSize` should be significantly smaller than `lc.ctx_size` (e.g., `lc.ctx_size * 0.4` to `lc.ctx_size * 0.6`) to allow room for your prompt instructions and the model's response for each chunk.
    *   The `lc` instance itself can serve as the tokenizer for `TextChunker.chunkText(text, lc, ...)`.
    *   **Example:**
        ```javascript
        // User provides a long document
        const longDocument = "very_long_text_content...";
        const modelContextSize = lc.ctx_size || 2048; // Get model context size
        const chunkSize = Math.floor(modelContextSize * 0.5); // Leave room for prompt and response
        const overlap = 50; // Token overlap

        try {
            const chunks = await TextChunker.chunkText(longDocument, lc, chunkSize, overlap);
            // Now process each chunk individually or sequentially
            for (const chunk of chunks) {
                // const prompt = build_prompt_for_chunk(chunk);
                // const result = await lc.generate(prompt, { n_predict: 256 });
                // ...
            }
        } catch (error) {
            console.error("Error chunking text:", error);
        }
        ```

*   **Use `TasksLibrary.summarizeText()` for Compression:**
    *   If the goal is to get a condensed version of a long text to use as *context* for a subsequent task, use `tasks.summarizeText()`.
    *   This method internally handles chunking and iterative summarization to fit within context limits.
    *   Provide a reasonable `maxSummarySizeInTokens` to control the output length of the summary.
    *   **Example:**
        ```javascript
        const veryLongArticle = "...";
        const targetSummaryTokens = 512; // How long the final summary should be
        const articleSummary = await tasks.summarizeText(
            veryLongArticle,
            "Extract the key points from this article.",
            "article_doc",
            "", // answerStart
            lc.n_predict || 1024, // maxGenerationSize for intermediate steps
            targetSummaryTokens
        );
        // Now 'articleSummary' can be used as a smaller piece of context
        // const followUpPrompt = lc.user_message() + `Based on this summary: ${articleSummary}\nWhat is your opinion on X?` + lc.ai_message();
        // const opinion = await lc.generate(followUpPrompt);
        ```

**2. Building Prompts Efficiently:**

*   **Use Prompt Template Helpers:** Construct prompts using `lc.system_message()`, `lc.user_message()`, `lc.ai_message()`, `lc.separatorTemplate()`, etc. This ensures correct formatting expected by the model.
*   **`TasksLibrary.buildPrompt()` for Contextual Truncation:**
    *   When you have multiple parts in your prompt, and one part (like a long chat history or a retrieved document snippet) might be too long, use `tasks.buildPrompt(promptParts, sacrificeId)`.
    *   The `sacrificeId` should be the index of the potentially long part in the `promptParts` array. This part will be truncated (from the beginning) if the total prompt is too long.
    *   **Remember:** `buildPrompt` is `async` if using the token-based calculation internally.
    *   **Example:**
        ```javascript
        const chatHistory = "User: Hi\nAI: Hello\nUser: Tell me about X...\nAI: (long explanation)"; // Potentially very long
        const currentUserQuery = "Can you elaborate on the last point?";

        const promptParts = [
            lc.system_message() + "You are a helpful assistant.",
            chatHistory, // This is the part we might sacrifice (index 1)
            lc.user_message() + currentUserQuery,
            lc.ai_message()
        ];
        // This assumes buildPrompt has been made async in the library as intended
        const finalPrompt = await tasks.buildPrompt(promptParts, 1, lc.ctx_size, (lc.n_predict || 256) + 50);
        // const response = await lc.generate(finalPrompt);
        ```

**3. Managing Chat History:**

*   **Don't Append Full Raw History Indefinitely:** For ongoing conversations, sending the entire raw history each time will quickly exceed context.
*   **Strategies:**
    *   **Summarize Older Turns:** Use `tasks.summarizeText()` on older parts of the conversation.
    *   **Sliding Window:** Keep only the N most recent turns.
    *   **Sacrificial History:** Use `tasks.buildPrompt()` with the chat history as the `sacrificeId`.
    *   **RAG for Knowledge:** If the conversation refers to long-term knowledge, consider if that knowledge should be in a RAG system (`LOLLMSRAGClient`) instead of directly in the chat prompt.

**4. When Generating Code (`lc.generateCode()` / `lc.generateCodes()`):**

*   The prompt for code generation itself (instructions, context, existing code snippets) contributes to context.
*   If providing existing code for modification, and it's very long, consider sending only relevant snippets or a summary.
*   The `lc.generateCode()` method has a loop to ask the AI to continue if the code is incomplete. This re-prompting also consumes context. Be mindful if the *initial* code block generated is already very large.

**5. Parameter Usage for Context Control:**

*   **`n_predict`:** Set this to a reasonable value. If you only need a short answer, don't leave it at the default (which might be very large or infinite for some models). `n_predict` reserves space in the context for the *output*.
    `lc.ctx_size - prompt_token_length - n_predict > buffer` (e.g., buffer of 50-100 tokens).
*   **Streaming (`stream: true`, `streamingCallback`):** While streaming doesn't directly save context on the *server-side* for a single generation call, it allows the *client* to process output as it arrives. This is good for UX but doesn't solve the fundamental context limit of the prompt itself.

**General Best Practices:**

*   **Be Concise:** Make your instructions to the model clear and to the point.
*   **Async/Await:** All generation and many utility methods are `async`. Always use `await`.
*   **Error Handling:** Wrap `await` calls in `try...catch` blocks.
*   **Iterate and Test:** If you suspect context issues, log the token counts of your prompts (e.g., `(await lc.tokenize(myPrompt)).length`) to debug.

By following these guidelines, you will help ensure that the JavaScript code you generate uses the `lollms_client.js` library effectively and avoids common pitfalls related to context window limitations. Prioritize preprocessing and strategic prompting.