# LOLLMS RAG System

## Overview

The LOLLMS RAG (Retrieval-Augmented Generation) System is a powerful tool that combines a FastAPI backend with a JavaScript client to provide efficient document management and search capabilities. This system allows users to add, remove, index, and search documents using vector embeddings, enhancing the retrieval process for various applications.

## Components

1. **Python Backend (`lollms_rag.py`)**: A FastAPI-based server that handles document management, indexing, and search operations.
2. **JavaScript Client (`LOLMSRAGClient`)**: A client-side class that interacts with the backend API, providing an easy-to-use interface for developers.

## Features

- Secure authentication using bearer tokens
- Document management (add, remove, index)
- Vector-based document search
- Database wiping capability
- Cross-platform compatibility

## Prerequisites

- Python 3.7+
- FastAPI
- LOLLMS WebUI
- Pydantic
- lollmsvectordb
- JavaScript environment (for client-side usage)

## Installation
Just install, configure and run lollms and import your client inside your webapp. By default the url should be http://localhost:9600/lollms_js. If you have changed the host name or port address, just change this to whatever you have built. Once imported you are ready to use the rag functionalities in your lollms webapp.

## Usage

### Python Backend

1. Include the `lollms_rag.py` module in your FastAPI application.
2. Configure the LOLLMS WebUI instance with appropriate RAG settings.
3. Add the router to your FastAPI app:
   ```python
   from lollms_rag import router as rag_router

   app.include_router(rag_router)
   ```

### JavaScript Client

1. Include the `LOLMSRAGClient` class in your JavaScript project.
2. Create an instance of the client:
   ```javascript
   const ragClient = new LOLMSRAGClient('http://your-api-url', 'your-bearer-token');
   ```

3. Use the client methods to interact with the RAG system:
   ```javascript
   // Add a document
   ragClient.addDocument('Title', 'Content', 'path/to/document')
     .then(response => console.log(response))
     .catch(error => console.error(error));

   // Search for documents
   ragClient.search('query text')
     .then(results => console.log(results))
     .catch(error => console.error(error));
   ```

## API Endpoints

- `POST /add_document`: Add a new document
- `POST /remove_document/{document_id}`: Remove a document
- `POST /index_database`: Index the database
- `POST /search`: Search for documents
- `DELETE /wipe_database`: Wipe the entire database

## Security

The system uses bearer token authentication. Ensure that you keep your API keys secure and don't expose them in client-side code.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the [Apache 2.0](LICENSE).
