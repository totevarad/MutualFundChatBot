"""
PDF Parser — Extracts text from mutual fund PDFs (factsheets, SID, KIM).
Uses pdfplumber for high-quality table and text extraction.
"""

import os
import pdfplumber
from src.utils.logger import get_logger

logger = get_logger(__name__)


def parse_pdf(file_path: str, max_pages: int | None = None) -> str:
    """Extract text content and tables from a PDF file.

    Args:
        file_path: Path to the PDF file.
        max_pages: Optional maximum number of pages to parse.

    Returns:
        Extracted text as a single string.
    """
    if not os.path.exists(file_path):
        logger.error(f"PDF file not found: {file_path}")
        return ""

    logger.info(f"Starting PDF extraction: {file_path}")
    extracted_pages = []

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                if max_pages is not None and page_num > max_pages:
                    break
                text = page.extract_text() or ""
                
                # Try table extraction
                tables_str = ""
                try:
                    tables = page.extract_tables()
                    for table in tables:
                        rows = []
                        for row in table:
                            clean_row = [
                                str(cell).strip().replace("\n", " ")
                                if cell is not None else ""
                                for cell in row
                            ]
                            if any(clean_row):
                                rows.append(clean_row)

                        if not rows:
                            continue

                        # Format as markdown table
                        col_count = len(rows[0])
                        markdown_table = []

                        # Header
                        markdown_table.append("| " + " | ".join(rows[0]) + " |")
                        markdown_table.append("|" + "|".join(["---"] * col_count) + "|")

                        # Data rows
                        for row in rows[1:]:
                            if len(row) < col_count:
                                row += [""] * (col_count - len(row))
                            markdown_table.append("| " + " | ".join(row[:col_count]) + " |")

                        tables_str += "\n\n### Extracted Table:\n" + "\n".join(markdown_table) + "\n\n"
                except Exception as table_err:
                    logger.debug(f"Table extraction skipped on page {page_num}: {table_err}")

                page_content = f"--- Page {page_num} ---\n{text}\n{tables_str}"
                extracted_pages.append(page_content)

        full_text = "\n\n".join(extracted_pages)
        logger.info(f"Successfully extracted {len(pdf.pages)} pages from {file_path}")
        return full_text

    except Exception as e:
        logger.error(f"Error parsing PDF {file_path}: {e}")
        return ""

