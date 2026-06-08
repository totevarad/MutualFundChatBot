"""
Response Formatter — Enforces response format rules (3-sentence limit, citation, footer).
"""

from src.utils.logger import get_logger

logger = get_logger(__name__)


def format_response(
    answer: str,
    source_url: str,
    last_updated: str | None = None,
) -> dict:
    """Format and validate a response before returning to the user.

    Args:
        answer: The raw LLM-generated answer.
        source_url: The citation URL.
        last_updated: The document's last updated date.

    Returns:
        Formatted response dict.
    """
    # TODO: Implement in Phase 3
    raise NotImplementedError("Response formatting will be implemented in Phase 3")
