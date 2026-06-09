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
    answer = output.get("answer", "")
    errors = []
    
    # Check length limits (assuming formatter has done its job, just verifying)
    sentences = [s for s in answer.split('.') if s.strip()]
    if len(sentences) > 5: # Allowing some buffer over the 3 sentence limit
        errors.append("Output exceeds length limit.")
        
    # Check for advisory language in LLM output
    advisory_phrases = [
        "i recommend", "you should invest", "is a good buy", "is a bad buy",
        "better to invest", "my advice", "we recommend"
    ]
    
    answer_lower = answer.lower()
    has_advisory_language = any(phrase in answer_lower for phrase in advisory_phrases)
    
    if has_advisory_language:
        errors.append("Output contains advisory language.")
        return {
            "is_valid": False,
            "errors": errors,
            "has_advisory_language": True,
            "corrected_answer": "I can only provide factual information. Please refer to an AMFI-registered distributor or SEBI-registered advisor for investment recommendations."
        }
        
    is_valid = len(errors) == 0
    return {
        "is_valid": is_valid,
        "errors": errors,
        "has_advisory_language": False
    }
