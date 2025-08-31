import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Dict, Any, AsyncGenerator
import json
import asyncio
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Import the Message class from models
from app.models import Message

# Load environment variables from .env file
load_dotenv()

class RAGSystem:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.documents = []
        self.is_initialized = False
        
        # Initialize Azure OpenAI client
        self.azure_openai_client = self._init_azure_openai()
        
        self.initialize_rag()
    
    def _init_azure_openai(self):
        """Initialize Azure OpenAI client with environment variables"""
        print(os.getenv("AZURE_OPENAI_ENDPOINT"))
        try:
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            print(
                azure_endpoint, api_key, api_version, deployment_name
            )
            if not all([azure_endpoint, api_key, deployment_name]):
                raise ValueError("Azure OpenAI environment variables not properly configured")
            
            # Create Azure OpenAI client with minimal configuration
            # Using http_client parameter instead of proxies to avoid deprecation warning
            from openai import AzureOpenAI
            import httpx
            
            # Create a custom http client without proxies to avoid the issue
            http_client = httpx.Client()
            
            client = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                api_version=api_version,
                http_client=http_client
            )
            
            return client
        except Exception as e:
            print(f"Warning: Azure OpenAI initialization failed: {e}")
            print("Please set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and AZURE_OPENAI_DEPLOYMENT_NAME environment variables")
            return None
    
    def initialize_rag(self):
        # Load your knowledge base (customize with your data)
        self.documents = self.load_knowledge_base()
        
        # Create embeddings and FAISS index
        embeddings = self.embedding_model.encode([doc["content"] for doc in self.documents])
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings.astype(np.float32))
        
        self.is_initialized = True
    
    def load_knowledge_base(self) -> List[Dict[str, Any]]:
        # Load actual knowledge base documents
        documents = []
        
        # Load the sample document
        try:
            with open("app/knowledge_base/sample_document.md", "r") as f:
                content = f.read()
                documents.append({
                    "id": "sample_document",
                    "content": content,
                    "metadata": {"type": "documentation", "source": "sample_document.md"}
                })
        except FileNotFoundError:
            # Fallback to placeholder content if file doesn't exist
            documents.extend([
                {
                    "id": "system_prompt",
                    "content": "Your complete system prompt content here...",
                    "metadata": {"type": "system_prompt"}
                },
                {
                    "id": "projects_info",
                    "content": "Information about projects...",
                    "metadata": {"type": "project"}
                }
            ])
        
        return documents
    
    def retrieve_relevant_documents(self, query: str, k: int = 3) -> List[Dict]:
        query_embedding = self.embedding_model.encode([query])
        distances, indices = self.index.search(query_embedding.astype(np.float32), k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                results.append({
                    **self.documents[idx],
                    "similarity_score": float(1 / (1 + distances[0][i]))
                })
        return results
    
    async def chat(self, messages: List[Message]) -> str:
        last_message = messages[-1].content
        
        # Retrieve relevant documents
        relevant_docs = self.retrieve_relevant_documents(last_message)
        
        # Build context from retrieved documents
        context = "\n\n".join([doc["content"] for doc in relevant_docs])
        
        # Generate response using Azure OpenAI
        if self.azure_openai_client is None:
            # Fallback response if Azure OpenAI is not configured
            return "I'm sorry, but the AI service is not currently available. Please check your Azure OpenAI configuration."
        
        try:
            # Construct the conversation with context
            conversation = [
                {
                    "role": "system",
                    "content": f"""You are a helpful AI assistant. Use the following context to answer the user's question.
                    If the context doesn't contain relevant information, say you don't know based on the available information.
                    
                    Context: {context}
                    
                    Please provide a helpful response based on the context above. If appropriate, suggest a follow-up question or related topic to explore further."""
                }
            ]
            
            # Add previous messages to maintain conversation context
            for msg in messages:
                conversation.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Call Azure OpenAI
            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            response = self.azure_openai_client.chat.completions.create(
                model=deployment_name,
                messages=conversation,
                temperature=0.7,
                max_tokens=800
            )
            print(response)
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error calling Azure OpenAI: {e}")
            return "I apologize, but I encountered an error while processing your request. Please try again later."
    
    async def stream_chat(self, messages: List[Message]) -> AsyncGenerator[str, None]:
        # Implement streaming response generation with Azure OpenAI
        if self.azure_openai_client is None:
            yield f"data: {json.dumps({'content': 'AI service not available. Please check configuration.'})}\n\n"
            yield "data: [DONE]\n\n"
            return
        
        last_message = messages[-1].content
        relevant_docs = self.retrieve_relevant_documents(last_message)
        context = "\n\n".join([doc["content"] for doc in relevant_docs])
        
        try:
            # Construct the conversation with context
            conversation = [
                {
                    "role": "system",
                    "content": f"""You are a helpful AI assistant. Use the following context to answer the user's question.
                    If the context doesn't contain relevant information, say you don't know based on the available information.
                    
                    Context: {context}
                    
                    Please provide a helpful response based on the context above. If appropriate, suggest a follow-up question or related topic to explore further."""
                }
            ]
            
            # Add previous messages to maintain conversation context
            for msg in messages:
                conversation.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Call Azure OpenAI with streaming
            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            response = self.azure_openai_client.chat.completions.create(
                model=deployment_name,
                messages=conversation,
                temperature=0.7,
                max_tokens=800,
                stream=True
            )
            
            # Stream the response
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': content})}\n\n"
                    await asyncio.sleep(0.01)
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            print(f"Error in streaming chat: {e}")
            yield f"data: {json.dumps({'content': 'Sorry, I encountered an error. Please try again.'})}\n\n"
            yield "data: [DONE]\n\n"
    
    def is_ready(self) -> bool:
        return self.is_initialized
