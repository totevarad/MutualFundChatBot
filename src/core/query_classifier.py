"""
Query Classifier — Classifies user queries as factual, advisory, or out-of-scope.
"""

from src.utils.logger import get_logger

logger = get_logger(__name__)


def classify_query(query: str) -> dict:
    """Classify a user query into a category.

    Args:
        query: The user's input query.

    Returns:
        Dict with 'category' (factual|advisory|performance_comparison|pii|out_of_scope)
        and 'confidence' (float 0-1).
    """
    # TODO: Implement in Phase 4
    raise NotImplementedError("Query classification will be implemented in Phase 4")
