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
        Dict with 'category' (factual|advisory|performance_comparison|out_of_scope)
        and 'confidence' (float 0-1).
    """
    import re
    query_lower = query.lower()
    
    # Define keywords for categories
    advisory_keywords = [
        "should i", "which is better", "recommend", "invest in", "good fund",
        "where to invest", "best fund", "top fund"
    ]
    
    performance_keywords = [
        "compare returns", "better performance", "will give", "returns",
        "how much profit", "past performance"
    ]
    
    factual_keywords = [
        "expense ratio", "exit load", "sip", "nav", "benchmark", "lock-in", 
        "riskometer", "tax", "aum", "fund manager"
    ]
    
    # Check advisory first (highest priority for guardrails)
    if any(kw in query_lower for kw in advisory_keywords):
        return {"category": "advisory", "confidence": 0.9}
        
    # Check performance comparison next
    if any(kw in query_lower for kw in performance_keywords):
        return {"category": "performance_comparison", "confidence": 0.8}
        
    # Check factual
    if any(kw in query_lower for kw in factual_keywords):
        return {"category": "factual", "confidence": 0.8}
        
    # Default fallback
    return {"category": "out_of_scope", "confidence": 0.5}
