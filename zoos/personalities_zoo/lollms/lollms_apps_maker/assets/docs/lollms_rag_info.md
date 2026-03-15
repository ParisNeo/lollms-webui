### LOLLMSRAGClient

- **constructor(baseURL, apiKey)**: Initializes a new LOLLMSRAGClient instance. the key is optional
- **async addDocument(title, content, path)**: Adds a document to the RAG database.
- **async removeDocument(documentId)**: Removes a document from the RAG database.
- **async indexDatabase()**: Indexes the RAG database.
- **async search(query)**: Searches the RAG database for documents matching the query.
- **async wipeDatabase()**: Wipes the RAG database.

This class is part of lollms client and can be used to extract information from documents 
```javascript
const lc = new LollmsClient()
const lr = new LOLLMSRAGClient(lc)
await lollmsRAG.addDocument("document title","content", "path")
await lollmsRAG.indexDatabase()
const extracted_data = lollmsRAG.search(message)
```
