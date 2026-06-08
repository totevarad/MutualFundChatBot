"""
Pipeline Runner — Orchestrates the full ingestion pipeline.
Entry point for both manual and GitHub Actions triggered runs.

Usage:
    python -m src.ingestion.run_pipeline [--full]
"""

import os
import json
from datetime import datetime
from src.utils.logger import get_logger
from src.ingestion.pdf_parser import parse_pdf
from src.ingestion.scraper import scrape_url
from src.ingestion.chunker import chunk_text
from src.ingestion.indexer import create_index, get_chroma_client
from src.ingestion.diff_detector import detect_changes, find_local_file, get_source_content_hash

logger = get_logger(__name__)


def parse_xlsx(file_path: str) -> str:
    """Extract rows and values from an Excel (.xlsx) file as pipe-separated markdown lines.
    
    Uses standard library zipfile and xml parsing.
    """
    import zipfile
    import xml.etree.ElementTree as ET
    
    try:
        with zipfile.ZipFile(file_path) as z:
            # 1. Load shared strings
            shared_strings = []
            try:
                with z.open("xl/sharedStrings.xml") as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    ns = {"ns": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
                    for t in root.findall(".//ns:t", ns):
                        shared_strings.append(t.text or "")
            except KeyError:
                pass
                
            # 2. Load sheet1 rows
            text_lines = []
            with z.open("xl/worksheets/sheet1.xml") as f:
                tree = ET.parse(f)
                root = tree.getroot()
                ns = {"ns": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
                
                for row in root.findall(".//ns:row", ns):
                    cells = []
                    for c in row.findall("ns:c", ns):
                        v = c.find("ns:v", ns)
                        if v is not None:
                            val = v.text or ""
                            t_attr = c.get("t")
                            if t_attr == "s":
                                idx = int(val)
                                if 0 <= idx < len(shared_strings):
                                    cells.append(shared_strings[idx])
                                else:
                                    cells.append(val)
                            else:
                                cells.append(val)
                        else:
                            cells.append("")
                    if any(cells):
                        text_lines.append("| " + " | ".join(c.strip().replace("\n", " ") for c in cells) + " |")
                        
            return "\n".join(text_lines)
    except Exception as e:
        logger.error(f"Error parsing Excel file {file_path}: {e}")
        return ""


def run(full_refresh: bool = False):
    """Execute the full ingestion pipeline.

    Args:
        full_refresh: If True, re-process all sources. If False, incremental only.
    """
    sources_file = "data/sources.json"
    cache_file = "data/hashes.json"

    logger.info(f"Ingestion pipeline started. Mode: {'Full' if full_refresh else 'Incremental'}")

    # If full refresh, clean vector store collection and hash cache
    if full_refresh:
        logger.info("Performing Full Refresh: Clearing vector store...")
        try:
            client = get_chroma_client()
            client.delete_collection(name="mutual_fund_docs")
            logger.info("ChromaDB collection cleared.")
        except Exception as e:
            logger.warning(f"Could not clear ChromaDB collection (might not exist): {e}")

        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                logger.info("Hash cache file cleared.")
            except Exception as e:
                logger.warning(f"Could not clear hash cache: {e}")

    # Detect sources to process
    if full_refresh:
        if not os.path.exists(sources_file):
            logger.error(f"Sources file not found: {sources_file}")
            return
        with open(sources_file) as f:
            sources_to_process = json.load(f)
    else:
        sources_to_process = detect_changes(sources_file, cache_file)

    if not sources_to_process:
        logger.info("No changed or new sources detected. Pipeline execution skipped.")
        return

    logger.info(f"Processing {len(sources_to_process)} sources...")

    total_indexed = 0
    all_chunks = []

    for i, source in enumerate(sources_to_process, 1):
        url = source.get("url")
        src_type = source.get("type", "unknown")
        scheme = source.get("scheme")
        fmt = source.get("format", "html")

        logger.info(f"[{i}/{len(sources_to_process)}] Processing source: {url or scheme} ({src_type})")

        content = ""

        if fmt == "pdf":
            local_path = find_local_file(source)
            if local_path and os.path.exists(local_path):
                logger.info(f"Parsing local PDF file: {local_path}")
                content = parse_pdf(local_path)
            else:
                logger.warning(f"Local PDF file not found for source {url or scheme}")

        elif fmt == "html":
            if url:
                content = scrape_url(url)
            else:
                logger.warning("HTML source has no URL, skipping")

        if content:
            chunks = chunk_text(
                text=content,
                source_url=url or "",
                scheme_name=scheme,
                source_type=src_type,
                document_date=datetime.now().strftime("%Y-%m-%d")
            )
            all_chunks.extend(chunks)
        else:
            logger.warning(f"No content extracted for source {url or scheme}")

    # Parse and index local Excel sheets matching our active schemes
    raw_dir = "data/raw"
    if os.path.exists(raw_dir):
        xlsx_files = [f for f in os.listdir(raw_dir) if f.endswith(".xlsx")]
        if xlsx_files:
            logger.info(f"Scanning raw folder: Found {len(xlsx_files)} Excel portfolio files...")
            for f in xlsx_files:
                local_path = os.path.join(raw_dir, f)
                
                # Filename example: "Monthly HDFC Large Cap Fund - 30 April 2026.xlsx"
                scheme_name = None
                if f.startswith("Monthly HDFC "):
                    scheme_name = f[8:].split(" - ")[0]

                active_schemes = [
                    "HDFC Large Cap Fund",
                    "HDFC Flexi Cap Fund",
                    "HDFC ELSS Tax saver",
                    "HDFC Hybrid Equity Fund",
                    "HDFC Mid Cap Fund"
                ]

                matched_scheme = None
                if scheme_name:
                    for s in active_schemes:
                        if s.replace(" ", "").lower() in scheme_name.replace(" ", "").lower():
                            matched_scheme = s
                            break

                if matched_scheme:
                    logger.info(f"Processing Excel portfolio for scheme: {matched_scheme} ({f})")
                    excel_content = parse_xlsx(local_path)
                    if excel_content:
                        excel_chunks = chunk_text(
                            text=excel_content,
                            source_url="https://www.hdfcfund.com/mutual-funds/factsheets",
                            scheme_name=matched_scheme,
                            source_type="factsheet",
                            document_date="2026-04-30"
                        )
                        all_chunks.extend(excel_chunks)

    # Index chunks in vector store
    if all_chunks:
        total_indexed = create_index(all_chunks)
        logger.info(f"Ingestion pipeline completed successfully. Total indexed chunks: {total_indexed}")
        
        # Save hashes to cache file so subsequent incremental runs can skip them
        try:
            new_hashes = {}
            if os.path.exists(sources_file):
                with open(sources_file) as f:
                    sources = json.load(f)
                for source in sources:
                    url_key = source.get("url") or source.get("scheme") or ""
                    if url_key:
                        new_hashes[url_key] = get_source_content_hash(source)
                
                # Make sure the directory exists
                cache_dir = os.path.dirname(cache_file)
                if cache_dir and not os.path.exists(cache_dir):
                    os.makedirs(cache_dir, exist_ok=True)
                    
                with open(cache_file, "w") as f:
                    json.dump(new_hashes, f, indent=2)
                logger.info(f"Updated hash cache saved to {cache_file}")
        except Exception as e:
            logger.error(f"Error updating hash cache: {e}")
    else:
        logger.warning("No chunks generated. Ingestion indexing skipped.")

    return total_indexed


if __name__ == "__main__":
    import sys

    full = "--full" in sys.argv
    run(full_refresh=full)

