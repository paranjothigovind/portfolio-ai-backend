# RAG Backend System

A FastAPI-based Retrieval-Augmented Generation (RAG) backend with Azure OpenAI integration for intelligent response generation.

## Project Structure

```
rag-backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── rag.py           # RAG core functionality
│   ├── models.py        # Data models
│   └── knowledge_base/  # Your documents and data
├── requirements.txt
└── README.md
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Azure OpenAI environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your Azure OpenAI credentials:
     - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
     - `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
     - `AZURE_OPENAI_DEPLOYMENT_NAME`: Your deployment name
     - `AZURE_OPENAI_API_VERSION`: API version (default: 2024-02-15-preview)

3. Add your knowledge base documents to `app/knowledge_base/` directory

4. Customize the `load_knowledge_base()` method in `rag.py` to load your specific documents

## Running the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at: http://localhost:8000

## API Endpoints

### POST /chat
Main chat endpoint that accepts streaming or non-streaming requests.

**Request Body:**
```json
{
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "stream": true
}
```

### GET /health
Health check endpoint to verify the system is running and RAG is loaded.

**Response:**
```json
{
  "status": "healthy",
  "rag_loaded": true
}
```

## Frontend Integration

Update your Next.js API route to call this backend instead of OpenAI:

```typescript
// Replace OpenAI call with:
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    messages: messagesWithSystemPrompt,
    stream: true
  })
});
```

## Customization Points

1. **Knowledge Base**: Populate `load_knowledge_base()` with your actual system prompt, tool information, and portfolio data
2. **LLM Integration**: Uses Azure OpenAI for intelligent response generation
3. **Document Parsing**: Add support for different document formats (PDF, Word, etc.)
4. **Vector Store**: Customize FAISS index parameters for better retrieval
5. **Embedding Model**: Use different sentence transformer models based on your needs

## Features

- ✅ FastAPI backend with CORS support
- ✅ SentenceTransformers for local embeddings
- ✅ FAISS vector storage for efficient retrieval
- ✅ Azure OpenAI integration for intelligent responses
- ✅ Streaming response support
- ✅ Health check endpoint
- ✅ Modular architecture for easy customization

## Next Steps

1. Add your actual knowledge base documents
2. Integrate a local LLM for response generation
3. Add authentication and rate limiting
4. Implement document parsing for various formats
5. Add monitoring and logging
