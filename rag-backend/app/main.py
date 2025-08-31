from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import logging
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from app.rag import RAGSystem

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Backend API")

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system
rag_system = RAGSystem()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    stream: bool = False

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"Chat request received: {len(request.messages)} messages, stream={request.stream}")
        
        if request.stream:
            # For streaming responses
            logger.info("Starting streaming response")
            return StreamingResponse(
                rag_system.stream_chat(request.messages),
                media_type="text/event-stream"
            )
        else:
            # For non-streaming responses
            logger.info("Processing non-streaming response")
            response = await rag_system.chat(request.messages)
            logger.info(f"Response generated: {response[:100]}...")
            return {"response": response}
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "rag_loaded": rag_system.is_ready()}
