"""
Validation — Post-ingestion checks to verify data quality.

Usage:
    python -m src.ingestion.validate
"""

import sys
from src.utils.logger import get_logger
from src.ingestion.indexer import get_chroma_client

logger = get_logger(__name__)


def validate() -> bool:
    """Run post-ingestion validation checks.

    Returns:
        True if all checks pass, False otherwise.
    """
    logger.info("Starting post-ingestion validation checks...")

    try:
        client = get_chroma_client()
        collection = client.get_collection(name="mutual_fund_docs")
        results = collection.get()

        ids = results.get("ids", [])
        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])

        total_chunks = len(ids)
        logger.info(f"Total chunks in vector store: {total_chunks}")

        # 1. Verify minimum chunk count (target: 50+)
        if total_chunks < 50:
            logger.error(f"Validation FAILED: Too few chunks in vector store: {total_chunks} (expected >= 50)")
            return False

        # 2. Check metadata completeness
        logger.info("Checking metadata fields for all chunks...")
        sources = set()
        schemes = set()

        for i, meta in enumerate(metadatas):
            if not meta:
                logger.error(f"Validation FAILED: Chunk {ids[i]} has empty metadata")
                return False

            source_url = meta.get("source_url")
            if not source_url:
                logger.error(f"Validation FAILED: Chunk {ids[i]} is missing 'source_url' in metadata")
                return False
            sources.add(source_url)

            scheme_name = meta.get("scheme_name")
            if scheme_name:
                schemes.add(scheme_name)

        # 3. Log stats
        avg_chunk_size = sum(len(doc) for doc in documents) / total_chunks if total_chunks > 0 else 0
        logger.info("--- Ingestion Statistics ---")
        logger.info(f"Total Chunks: {total_chunks}")
        logger.info(f"Unique Source URLs: {len(sources)}")
        logger.info(f"Unique Schemes Indexed: {len(schemes)} ({', '.join(schemes)})")
        logger.info(f"Average Chunk Size: {avg_chunk_size:.2f} characters")
        logger.info("----------------------------")

        logger.info("Validation PASSED: All checks completed successfully.")
        return True

    except Exception as e:
        logger.error(f"Validation FAILED due to exception: {e}")
        return False


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
