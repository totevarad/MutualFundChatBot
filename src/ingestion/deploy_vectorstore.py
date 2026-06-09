"""
Deploy Vectorstore — Packages the ChromaDB vector database into a zip file for deployment.
"""

import os
import shutil
from src.utils.logger import get_logger

logger = get_logger(__name__)

VECTORSTORE_DIR = "./vectorstore"
OUTPUT_ZIP = "./vectorstore_backup"

def package_vectorstore():
    """Zips the vectorstore directory."""
    if not os.path.exists(VECTORSTORE_DIR):
        logger.error(f"Vectorstore directory '{VECTORSTORE_DIR}' not found!")
        return False

    try:
        logger.info(f"Packaging {VECTORSTORE_DIR} into {OUTPUT_ZIP}.zip...")
        shutil.make_archive(OUTPUT_ZIP, 'zip', VECTORSTORE_DIR)
        size_mb = os.path.getsize(f"{OUTPUT_ZIP}.zip") / (1024 * 1024)
        logger.info(f"Successfully created {OUTPUT_ZIP}.zip ({size_mb:.2f} MB)")
        return True
    except Exception as e:
        logger.error(f"Failed to package vectorstore: {e}")
        return False

if __name__ == "__main__":
    success = package_vectorstore()
    if not success:
        exit(1)
