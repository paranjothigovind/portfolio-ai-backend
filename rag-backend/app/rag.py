import numpy as np
import faiss
from typing import List, Dict, Any, AsyncGenerator
import json
import asyncio
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from app.models import Message  # Custom model class

# Load environment variables from .env
load_dotenv()


class RAGSystem:
    def __init__(self):
        self.index = None
        self.documents = []
        self.embeddings = []
        self.is_initialized = False

        # Initialize Azure OpenAI client
        self.azure_openai_client = self._init_azure_openai()

        self.initialize_rag()

    def _init_azure_openai(self):
        try:
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

            if not all([azure_endpoint, api_key]):
                raise ValueError("Missing Azure OpenAI environment variables")

            import httpx
            http_client = httpx.Client()

            return AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                api_version=api_version,
                http_client=http_client
            )
        except Exception as e:
            print(f"Error initializing Azure OpenAI: {e}")
            return None

    def initialize_rag(self):
        self.documents = self.load_knowledge_base()

        if not self.azure_openai_client:
            print("Cannot initialize RAG — Azure OpenAI client missing")
            return

        texts = [doc["content"] for doc in self.documents]
        self.embeddings = self._compute_embeddings(texts)

        if not self.embeddings:
            print("No embeddings were computed — skipping FAISS initialization.")
            return

        self.index = faiss.IndexFlatL2(len(self.embeddings[0]))
        self.index.add(np.array(self.embeddings).astype(np.float32))
        self.is_initialized = True

    def _compute_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Use Azure OpenAI to compute embeddings for a list of texts."""
        try:
            deployment_name = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
            if not deployment_name:
                raise ValueError("Missing embedding deployment name")

            response = self.azure_openai_client.embeddings.create(
                input=texts,
                model=deployment_name
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"Error computing embeddings: {e}")
            return []

    def load_knowledge_base(self) -> List[Dict[str, Any]]:
        documents = []
        try:
            with open("app/knowledge_base/sample_document.md", "r") as f:
                content = f.read()
                documents.append({
                    "id": "sample_document",
                    "content": content,
                    "metadata": {"type": "documentation", "source": "sample_document.md"}
                })
        except FileNotFoundError:
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
        query_embedding = self._compute_embeddings([query])[0]
        distances, indices = self.index.search(np.array([query_embedding]).astype(np.float32), k)

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
        relevant_docs = self.retrieve_relevant_documents(last_message)
        context = "\n\n".join([doc["content"] for doc in relevant_docs])

        if not self.azure_openai_client:
            return "AI service is not available. Please check your Azure OpenAI configuration."

        try:
            conversation = [
                {
                    "role": "system",
                    "content": f"""You are a helpful AI assistant. Use the following context to answer the user's question.

                    Context: {context}

                    Please respond helpfully based on the context. If context is missing, say so."""
                }
            ] + [{"role": msg.role, "content": msg.content} for msg in messages]

            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            response = self.azure_openai_client.chat.completions.create(
                model=deployment_name,
                messages=conversation,
                temperature=0.7,
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error during chat completion: {e}")
            return "I encountered an error. Please try again later."

    async def stream_chat(self, messages: List[Message]) -> AsyncGenerator[str, None]:
        if not self.azure_openai_client:
            yield f"data: {json.dumps({'content': 'AI service not available.'})}\n\n"
            yield "data: [DONE]\n\n"
            return

        last_message = messages[-1].content
        relevant_docs = self.retrieve_relevant_documents(last_message)
        context = "\n\n".join([doc["content"] for doc in relevant_docs])

        try:
            conversation = [
                {
                    "role": "system",
                    "content": f"""You are a helpful AI assistant. Use the following context to answer the user's question.

                    Context: {context}

                    Please respond helpfully based on the context. If context is missing, say so."""
                }
            ] + [{"role": msg.role, "content": msg.content} for msg in messages]

            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            response = self.azure_openai_client.chat.completions.create(
                model=deployment_name,
                messages=conversation,
                temperature=0.7,
                max_tokens=800,
                stream=True
            )

            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': content})}\n\n"
                    await asyncio.sleep(0.01)

            yield "data: [DONE]\n\n"
        except Exception as e:
            print(f"Streaming error: {e}")
            yield f"data: {json.dumps({'content': 'Streaming failed'})}\n\n"
            yield "data: [DONE]\n\n"

    def is_ready(self) -> bool:
        return self.is_initialized
