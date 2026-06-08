"""
Output Validator — Validates LLM responses for format compliance.
"""

from src.utils.logger import get_logger

logger = get_logger(__name__)


def validate_output(output: dict) -> dict:
    """Validate an LLM response against format rules.

    Args:
        output: Dict with 'answer', 'source_url', 'last_updated'.

    Returns:
        Dict with 'is_valid', 'errors', 'has_advisory_language', and optionally 'corrected_answer'.
    """
    # TODO: Implement in Phase 4
    return {"is_valid": True, "errors": [], "has_advisory_language": False}
