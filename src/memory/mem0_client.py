"""
Mem0 Client — Initializes and configures the Mem0 memory instance.
"""

import os
from mem0 import Memory
from src.utils.logger import get_logger

logger = get_logger(__name__)

_memory_instance = None

def get_memory_client() -> Memory | None:
    """Initialize and return the Mem0 memory instance."""
    global _memory_instance
    if _memory_instance is not None:
        return _memory_instance
        
    try:
        # Use local file-based vector store for Mem0 to avoid requiring a separate DB
        config = {
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": "mem0_user_memory",
                    "path": "./vectorstore"
                }
            }
        }
        _memory_instance = Memory.from_config(config)
        logger.info("Mem0 client initialized successfully.")
        return _memory_instance
    except Exception as e:
        logger.error(f"Failed to initialize Mem0 client: {e}")
        return None
