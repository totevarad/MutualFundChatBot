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
        List of dicts with 'type' (pan|aadhaar|phone|email|otp|account) and 'found' (bool).
        Actual PII values are NEVER returned or stored.
    """
    # TODO: Implement in Phase 4
    return []
