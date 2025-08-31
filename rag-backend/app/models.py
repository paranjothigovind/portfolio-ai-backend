from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    stream: bool = False

class ChatResponse(BaseModel):
    response: str

class Document(BaseModel):
    id: str
    content: str
    metadata: Optional[dict] = None
