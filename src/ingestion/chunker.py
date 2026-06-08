"""
Text Chunker — Splits documents into semantic chunks with metadata.
Uses RecursiveCharacterTextSplitter for intelligent boundary detection.
"""

from src.utils.logger import get_logger

logger = get_logger(__name__)


def chunk_text(
    text: str,
    source_url: str,
    scheme_name: str | None = None,
    source_type: str = "unknown",
    document_date: str | None = None,
) -> list[dict]:
    """Split text into chunks with attached metadata.

    Args:
        text: The full text to chunk.
        source_url: URL of the source document.
        scheme_name: Name of the mutual fund scheme (if applicable).
        source_type: Type of source (factsheet, kim, sid, faq, etc.).
        document_date: Date of the source document.

    Returns:
        List of chunk dicts with 'text', 'chunk_id', 'source_url',
        'scheme_name', 'source_type', 'document_date', 'ingestion_date'.
    """
    # TODO: Implement in Phase 2
    raise NotImplementedError("Text chunking will be implemented in Phase 2")
