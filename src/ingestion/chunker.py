"""
Text Chunker — Splits documents into semantic chunks with metadata.
Uses RecursiveCharacterTextSplitter for intelligent boundary detection.
"""

import hashlib
import os
from datetime import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter
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
    if not text:
        return []

    chunk_size = int(os.getenv("CHUNK_SIZE", 600))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 100))

    logger.info(f"Chunking text from {source_url} (size={chunk_size}, overlap={chunk_overlap})")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " "]
    )

    splits = splitter.split_text(text)
    chunks = []
    ingestion_date = datetime.now().strftime("%Y-%m-%d")

    for i, split in enumerate(splits):
        # Generate a unique stable chunk_id
        hash_input = f"{source_url}_{scheme_name or ''}_{i}_{split}"
        chunk_id = hashlib.sha256(hash_input.encode()).hexdigest()

        chunk = {
            "chunk_id": chunk_id,
            "text": split.strip(),
            "source_url": source_url,
            "scheme_name": scheme_name or "",
            "source_type": source_type,
            "document_date": document_date or "",
            "ingestion_date": ingestion_date
        }
        chunks.append(chunk)

    logger.info(f"Generated {len(chunks)} chunks for {source_url}")
    return chunks

