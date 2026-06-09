"""
Response Formatter — Enforces response format rules (3-sentence limit, citation, footer).
"""

import re
from src.utils.logger import get_logger

logger = get_logger(__name__)


def truncate_to_sentences(text: str, max_sentences: int = 3) -> str:
    """Truncate text to a maximum number of sentences."""
    # Split text by sentence-ending punctuation followed by a space or end of string
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    # Filter out empty strings that might result from splitting
    sentences = [s for s in sentences if s.strip()]
    if len(sentences) <= max_sentences:
        return text.strip()
    return ' '.join(sentences[:max_sentences])


def format_response(
    answer: str,
    source_url: str,
    last_updated: str | None = None,
    is_refusal: bool = False,
    memory_used: list[str] | None = None
) -> dict:
    """Format and validate a response before returning to the user.

    Args:
        answer: The raw LLM-generated answer.
        source_url: The citation URL.
        last_updated: The document's last updated date.
        is_refusal: Whether this is a refusal response.
        memory_used: List of memories used to generate the response.

    Returns:
        Formatted response dict.
    """
    if memory_used is None:
        memory_used = []

    if is_refusal:
        return {
            "answer": answer.strip(),
            "source_url": source_url,
            "last_updated": None,
            "is_refusal": True,
            "memory_used": memory_used
        }

    # Truncate factual answer to max 3 sentences
    truncated_answer = truncate_to_sentences(answer)
    
    # Append footer for factual answers
    date_str = last_updated if last_updated else "Unknown"
    footer = f"\n\nLast updated from sources: {date_str}"
    
    final_answer = truncated_answer + footer

    return {
        "answer": final_answer,
        "source_url": source_url,
        "last_updated": last_updated,
        "is_refusal": False,
        "memory_used": memory_used
    }
