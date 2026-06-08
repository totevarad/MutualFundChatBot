"""
Diff Detector — Hash-based change detection for incremental ingestion.
Compares SHA-256 hashes of source content against a cached hash file.
"""

from src.utils.logger import get_logger

logger = get_logger(__name__)


def detect_changes(sources_file: str, cache_file: str) -> list[dict]:
    """Compare current source content hashes against cached hashes.

    Args:
        sources_file: Path to sources.json.
        cache_file: Path to hashes.json cache.

    Returns:
        List of source dicts that have changed since last run.
    """
    # TODO: Implement in Phase 2
    raise NotImplementedError("Diff detection will be implemented in Phase 2")
