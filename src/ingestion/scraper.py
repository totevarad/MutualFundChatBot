"""
HTML Scraper — Extracts main content from AMC, AMFI, and SEBI web pages.
Uses BeautifulSoup and trafilatura for content extraction.
"""

import requests
import trafilatura
from bs4 import BeautifulSoup
from src.utils.logger import get_logger

logger = get_logger(__name__)


def scrape_url(url: str) -> str:
    """Scrape and extract main text content from a web page.

    Args:
        url: The URL to scrape.

    Returns:
        Extracted text content (HTML tags stripped).
    """
    if not url:
        return ""

    logger.info(f"Starting scrape for URL: {url}")

    try:
        # First, try to fetch and extract content with trafilatura
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            extracted_text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                no_fallback=False
            )
            if extracted_text:
                logger.info(f"Successfully scraped URL via trafilatura: {url} ({len(extracted_text)} chars)")
                return extracted_text

        # If trafilatura fails to extract or download, fallback to requests + BeautifulSoup
        logger.warning(f"Trafilatura extraction failed for {url}. Falling back to BeautifulSoup.")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code != 200:
            logger.error(f"Failed to fetch {url}, status code: {res.status_code}")
            return ""

        soup = BeautifulSoup(res.text, "lxml")

        # Strip script, style, head, nav, footer, header elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "head", "noscript"]):
            element.decompose()

        # Extract plain text
        text = soup.get_text(separator=" ")

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = "\n".join(chunk for chunk in chunks if chunk)

        logger.info(f"Successfully scraped URL via BeautifulSoup fallback: {url} ({len(clean_text)} chars)")
        return clean_text

    except Exception as e:
        logger.error(f"Error scraping URL {url}: {e}")
        return ""

