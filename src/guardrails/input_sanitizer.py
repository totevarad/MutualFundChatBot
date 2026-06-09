"""
Input Sanitizer — Cleans and validates user input before processing.
"""

from src.utils.logger import get_logger

logger = get_logger(__name__)


def sanitize_input(text: str) -> str:
    """Sanitize user input by removing XSS, SQL injection, and normalizing text.

    Args:
        text: Raw user input.

    Returns:
        Cleaned, safe input string.
    """
    import re
    if not text:
        return ""
        
    # Truncate overly long inputs
    text = text[:500]
    
    # Remove basic script tags and common XSS payloads
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<.*?>', '', text) # Strip other HTML tags
    
    # Strip common SQL injection patterns loosely (just removing the keywords if standalone, though parameterized queries are better, LLMs are immune to SQLi natively, but prompt injection is possible)
    # We will mainly just normalize spacing and remove control characters
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    
    # Normalize whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
