"""
Diff Detector — Hash-based change detection for incremental ingestion.
Compares SHA-256 hashes of source content against a cached hash file.
"""

import hashlib
import json
import os
import requests
from src.utils.logger import get_logger

logger = get_logger(__name__)


def find_local_file(source: dict) -> str | None:
    """Find a matching local raw file for the given source document metadata."""
    raw_dir = "data/raw"
    if not os.path.exists(raw_dir):
        return None

    scheme = source.get("scheme")
    src_type = source.get("type")

    # 1. Factsheet with scheme name: look for Excel sheets or factsheet PDF
    if src_type == "factsheet" and scheme:
        # Match Excel filenames: e.g. "Monthly HDFC Large Cap Fund - 30 April 2026.xlsx"
        normalized_scheme = scheme.replace(" ", "").lower()
        for f in os.listdir(raw_dir):
            normalized_f = f.replace(" ", "").lower()
            if normalized_scheme in normalized_f:
                return os.path.join(raw_dir, f)

        # Fallback to general Facts sheets
        for f in os.listdir(raw_dir):
            if "factsheet" in f.lower():
                return os.path.join(raw_dir, f)

    # 2. Statutory documents (KIM/SID): use the booklet
    if src_type in ["kim", "sid"]:
        for f in os.listdir(raw_dir):
            if "booklet" in f.lower() or "final" in f.lower():
                return os.path.join(raw_dir, f)

    # 3. Default fallback: match type name in filename
    for f in os.listdir(raw_dir):
        if src_type and src_type in f.lower():
            return os.path.join(raw_dir, f)

    return None


def get_source_content_hash(source: dict) -> str:
    """Generate a SHA-256 hash of the source content (local file or fetched HTML)."""
    # 1. Check local file for PDFs/Excel sheets
    if source.get("format") in ["pdf", "xlsx"]:
        local_path = find_local_file(source)
        if local_path and os.path.exists(local_path):
            try:
                with open(local_path, "rb") as f:
                    return hashlib.sha256(f.read()).hexdigest()
            except Exception as e:
                logger.warning(f"Error reading local file {local_path} for hash: {e}")

    # 2. Try fetching URL for web pages
    url = source.get("url")
    if url and url.startswith("http"):
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                return hashlib.sha256(res.content).hexdigest()
        except Exception as e:
            logger.debug(f"Could not fetch URL {url} for hashing (using URL fallback): {e}")

    # 3. Stable fallback hash
    fallback_str = url or source.get("scheme") or source.get("notes") or ""
    return hashlib.sha256(fallback_str.encode()).hexdigest()


def detect_changes(sources_file: str, cache_file: str) -> list[dict]:
    """Compare current source content hashes against cached hashes.

    Args:
        sources_file: Path to sources.json.
        cache_file: Path to hashes.json cache.

    Returns:
        List of source dicts that have changed since last run.
    """
    if not os.path.exists(sources_file):
        logger.error(f"Sources file not found: {sources_file}")
        return []

    try:
        with open(sources_file) as f:
            sources = json.load(f)
    except Exception as e:
        logger.error(f"Error parsing sources.json: {e}")
        return []

    # Load cache
    try:
        if os.path.exists(cache_file):
            with open(cache_file) as f:
                cached_hashes = json.load(f)
        else:
            cached_hashes = {}
    except Exception as e:
        logger.warning(f"Error reading hash cache {cache_file}, starting fresh: {e}")
        cached_hashes = {}

    changed_sources = []
    new_hashes = {}

    for source in sources:
        # Build a unique key combining URL, scheme name, and type
        url_key = source.get("url") or ""
        scheme = source.get("scheme")
        src_type = source.get("type")
        if scheme:
            url_key += f"_{scheme}"
        if src_type:
            url_key += f"_{src_type}"

        if not url_key:
            continue

        current_hash = get_source_content_hash(source)
        new_hashes[url_key] = current_hash

        # If hash is new or changed, add to list
        if url_key not in cached_hashes or cached_hashes[url_key] != current_hash:
            logger.info(f"Source changed: {url_key}")
            changed_sources.append(source)

    # Save updated hashes back to cache
    try:
        # Ensure directory exists
        cache_dir = os.path.dirname(cache_file)
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
            
        with open(cache_file, "w") as f:
            json.dump(new_hashes, f, indent=2)
        logger.info(f"Updated hash cache saved to {cache_file}")
    except Exception as e:
        logger.error(f"Error writing hash cache {cache_file}: {e}")

    return changed_sources

