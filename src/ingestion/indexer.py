"""
Indexer — Generates embeddings and indexes chunks into ChromaDB.
Uses BAAI/bge-large-en for 1024-dim embeddings.
"""

import os
import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Global model cache to avoid reloading
_embeddings = None


def get_embedding_model():
    """Load or retrieve the globally cached embedding model."""
    global _embeddings
    if _embeddings is None:
        model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en")
        logger.info(f"Loading embedding model: {model_name}...")
        
        # Configure HuggingFaceEmbeddings
        # BGE models should be run with normalize_embeddings=True for cosine similarity
        encode_kwargs = {"normalize_embeddings": True}
        _embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs=encode_kwargs
        )
        logger.info("Embedding model loaded successfully.")
    return _embeddings


def get_chroma_client():
    """Retrieve ChromaDB persistent client."""
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./vectorstore")
    return chromadb.PersistentClient(path=persist_dir)


def create_index(chunks: list[dict]) -> int:
    """Embed and index chunks into the ChromaDB vector store.

    Args:
        chunks: List of chunk dicts from the chunker.

    Returns:
        Number of chunks successfully indexed.
    """
    if not chunks:
        logger.info("No chunks provided for indexing.")
        return 0

    logger.info(f"Indexing {len(chunks)} chunks into ChromaDB...")
    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection(
            name="mutual_fund_docs",
            metadata={"hnsw:space": "cosine"}
        )

        embeddings_model = get_embedding_model()

        ids = []
        texts = []
        metadatas = []

        for chunk in chunks:
            ids.append(chunk["chunk_id"])
            texts.append(chunk["text"])
            
            # Formulate metadata primitives
            metadata = {
                "source_url": chunk["source_url"],
                "scheme_name": chunk["scheme_name"] or "",
                "source_type": chunk["source_type"] or "",
                "document_date": chunk["document_date"] or "",
                "ingestion_date": chunk["ingestion_date"]
            }
            metadatas.append(metadata)

        # Batch embedding generation with progress logging
        logger.info(f"Generating embeddings for {len(texts)} text chunks...")
        batch_size = 100
        vector_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            logger.info(f"Embedding batch {i // batch_size + 1}/{(len(texts) + batch_size - 1) // batch_size} ({len(batch_texts)} chunks)...")
            batch_embeddings = embeddings_model.embed_documents(batch_texts)
            vector_embeddings.extend(batch_embeddings)

        # Batch upsert into Chroma
        logger.info("Upserting chunks into ChromaDB collection...")
        collection.upsert(
            ids=ids,
            embeddings=vector_embeddings,
            documents=texts,
            metadatas=metadatas
        )

        logger.info(f"Successfully indexed {len(ids)} chunks.")
        return len(ids)

    except Exception as e:
        logger.error(f"Error creating index in ChromaDB: {e}")
        raise e


def get_collection_stats() -> dict:
    """Return statistics about the current vector store collection.

    Returns:
        Dict with 'total_chunks', 'sources_count', etc.
    """
    try:
        client = get_chroma_client()
        collection = client.get_collection(name="mutual_fund_docs")
        results = collection.get()

        total_chunks = len(results.get("ids", []))

        sources = set()
        for meta in results.get("metadatas", []):
            if meta and "source_url" in meta:
                sources.add(meta["source_url"])

        return {
            "total_chunks": total_chunks,
            "sources_count": len(sources),
            "collection_name": "mutual_fund_docs"
        }
    except Exception as e:
        logger.warning(f"Could not retrieve collection stats: {e}")
        return {
            "total_chunks": 0,
            "sources_count": 0,
            "collection_name": "mutual_fund_docs"
        }

