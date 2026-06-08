"""
Configuration loader for the Mutual Fund FAQ Assistant.
Reads environment variables from .env and provides typed access.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_project_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(_project_root / ".env")


class Config:
    """Centralized configuration from environment variables."""

    # --- LLM ---
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.0"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "200"))

    # --- Embeddings ---
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en")

    # --- Vector Store ---
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./vectorstore")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "600"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "5"))

    # --- Mem0 (Memory) ---
    MEM0_API_KEY: str = os.getenv("MEM0_API_KEY", "")
    MEM0_ORG_ID: str = os.getenv("MEM0_ORG_ID", "")
    MEM0_PROJECT_ID: str = os.getenv("MEM0_PROJECT_ID", "")

    # --- Paths ---
    PROJECT_ROOT: Path = _project_root
    DATA_DIR: Path = _project_root / "data"
    RAW_DATA_DIR: Path = _project_root / "data" / "raw"
    PROCESSED_DATA_DIR: Path = _project_root / "data" / "processed"
    SOURCES_FILE: Path = _project_root / "data" / "sources.json"
    HASHES_FILE: Path = _project_root / "data" / "hashes.json"

    # --- API ---
    NEXT_PUBLIC_API_URL: str = os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:8000")

    @classmethod
    def validate(cls) -> list[str]:
        """Check for missing critical configuration. Returns list of warnings."""
        warnings = []
        if not cls.OPENAI_API_KEY and not cls.GOOGLE_API_KEY:
            warnings.append("Neither OPENAI_API_KEY nor GOOGLE_API_KEY is set")
        if not cls.CHROMA_PERSIST_DIR:
            warnings.append("CHROMA_PERSIST_DIR is not set")
        return warnings


config = Config()
