"""
Pydantic Schemas — Request and response models for the API.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for POST /api/chat."""
    query: str = Field(..., min_length=1, max_length=500, description="User's factual query")
    user_id: str | None = Field(None, description="Optional pseudonymous user ID for memory")


class ChatResponse(BaseModel):
    """Response body for POST /api/chat."""
    answer: str = Field(..., description="Facts-only answer (≤ 3 sentences)")
    source_url: str | None = Field(None, description="Citation link to official source")
    last_updated: str | None = Field(None, description="Date the source was last updated")
    is_refusal: bool = Field(False, description="True if the query was refused (advisory/PII)")
    memory_used: list[str] = Field(default_factory=list, description="Memories used for context")


class SourceItem(BaseModel):
    """A single curated source."""
    url: str
    type: str
    scheme: str | None
    category: str | None
    format: str
    last_scraped: str | None


class HealthResponse(BaseModel):
    """Response body for GET /api/health."""
    status: str
    version: str
