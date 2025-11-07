from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    intent: Optional[str] = None  # "greetings", "query", "information", "feedback"
    intent_confidence: Optional[float] = None
    keywords: Optional[List[str]] = None
    complexity: Optional[str] = None  # "simple", "moderate", "complex"

class ChatSession(BaseModel):
    session_id: str
    created_at: datetime
    messages: List[ChatMessage]

class ChatRequest(BaseModel):
    message: str

class ContinueChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    session_id: str
    message: str
    conversation_history: List[ChatMessage]
    user_intent: Optional[str] = None
    intent_confidence: Optional[float] = None

class SessionResponse(BaseModel):
    session_id: str
    message: str
    conversation_history: List[ChatMessage]
    user_intent: Optional[str] = None
    intent_confidence: Optional[float] = None

class IntentAnalysis(BaseModel):
    intent: str
    confidence: float
    description: str
    keywords: List[str]
    complexity: str
