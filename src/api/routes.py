"""
API Routes — Route definitions for chat, sources, memory, and ingestion.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from src.core.rag_pipeline import query_pipeline
from src.memory.memory_manager import clear_user_memory
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    source_url: str
    last_updated: str
    is_refusal: bool

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """Process a user query through the RAG pipeline."""
    try:
        result = query_pipeline(query=request.query, user_id=request.user_id)
        return ChatResponse(
            answer=result.get("answer", ""),
            source_url=result.get("source_url", ""),
            last_updated=result.get("last_updated", ""),
            is_refusal=result.get("is_refusal", False)
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during chat processing.")

@router.delete("/memory/{user_id}")
def clear_memory_endpoint(user_id: str):
    """Clear memory for a specific user."""
    try:
        clear_user_memory(user_id)
        return {"status": "success", "message": f"Memory cleared for user {user_id}"}
    except Exception as e:
        logger.error(f"Error clearing memory in endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear memory.")
