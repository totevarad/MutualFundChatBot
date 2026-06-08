"""
Memory Manager — Retrieve, store, and clear user memories via Mem0.
"""

from src.utils.logger import get_logger

logger = get_logger(__name__)


def get_user_context(user_id: str, query: str) -> list[str]:
    """Fetch relevant memories for the current query."""
    # TODO: Implement in Phase 5
    return []


def store_interaction(user_id: str, query: str, response: str):
    """Store the Q&A interaction as a memory."""
    # TODO: Implement in Phase 5
    pass


def clear_user_memory(user_id: str):
    """Delete all stored memories for a user."""
    # TODO: Implement in Phase 5
    pass
