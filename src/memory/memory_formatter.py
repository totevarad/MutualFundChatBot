"""
Memory Formatter — Formats retrieved memories for injection into LLM prompts.
"""

from src.utils.logger import get_logger

logger = get_logger(__name__)


def format_memories(memories: list[str]) -> str:
    """Format a list of memory strings for prompt injection.

    Args:
        memories: List of memory strings from Mem0.

    Returns:
        Formatted string for the {user_memories} prompt slot.
    """
    if not memories:
        return "No prior interactions."
    return "\n".join(f"- {m}" for m in memories)
