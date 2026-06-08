"""
Pipeline Runner — Orchestrates the full ingestion pipeline.
Entry point for both manual and GitHub Actions triggered runs.

Usage:
    python -m src.ingestion.run_pipeline [--full]
"""

from src.utils.logger import get_logger

logger = get_logger(__name__)


def run(full_refresh: bool = False):
    """Execute the full ingestion pipeline.

    Args:
        full_refresh: If True, re-process all sources. If False, incremental only.
    """
    # TODO: Implement in Phase 2
    raise NotImplementedError("Pipeline runner will be implemented in Phase 2")


if __name__ == "__main__":
    import sys

    full = "--full" in sys.argv
    run(full_refresh=full)
