"""
PII Detector — Regex-based detection of sensitive personal information.
"""

from src.utils.logger import get_logger

logger = get_logger(__name__)


def detect_pii(text: str) -> list[dict]:
    """Detect PII patterns in the given text.

    Args:
        text: Text to scan for PII.

    Returns:
        List of dicts with 'type' (pan|aadhaar|phone|email|bank_account) and 'found' (bool).
        Actual PII values are NEVER returned or stored.
    """
    import re
    
    pii_found = []
    
    # regex patterns
    patterns = {
        "pan": r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
        "aadhaar": r'\b\d{4}\s?\d{4}\s?\d{4}\b',
        "phone": r'\b[6-9]\d{9}\b',
        "email": r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
        "bank_account": r'\b\d{9,18}\b'
    }
    
    for pii_type, pattern in patterns.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            pii_found.append({"type": pii_type, "found": True})
            
    return pii_found
