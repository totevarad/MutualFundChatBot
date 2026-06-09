# Project Design Decisions & Implementation Plans

This document catalogs key design decisions, architectural optimizations, and the phase-wise implementation plans for the Mutual Fund FAQ Assistant.

---

## 📋 Architectural Decisions by Phase

### Phase 1: Project Setup & Corpus Definition
*   **Selected AMC**: HDFC Asset Management Company (HDFC AMC) as the single reference entity.
*   **Selected Schemes**: 5 category-diverse schemes chosen for validation:
    1.  **Large-Cap**: HDFC Large Cap Fund
    2.  **Flexi-Cap**: HDFC Flexi Cap Fund
    3.  **ELSS (Tax-Saving)**: HDFC ELSS Tax saver
    4.  **Debt/Hybrid**: HDFC Hybrid Equity Fund
    5.  **Mid-Cap**: HDFC Mid Cap Fund
*   **Corpus Mapping**: Curated [sources.json](file:///c:/Users/varad/Desktop/Gen%20AI/MutualFundChatBot/data/sources.json) containing 24 official URLs from HDFC AMC, AMFI, and SEBI mapping factsheets, KIM, SID, FAQ, performance metrics, and statement procedures.
*   **Next.js Frontend**: Configured App Router scaffold in `frontend/` using custom CSS, preparing for the Nocturnal Growth dark-theme implementation.

### Phase 2: Data Ingestion Pipeline
*   **Dependency-Free Excel Parser**: Implemented a lightweight XML-based spreadsheet reader in Python (`parse_xlsx` in `run_pipeline.py`) using standard library `zipfile` and `xml.etree.ElementTree`. This parses the 100+ raw portfolio `.xlsx` files into pipe-separated markdown lines without external heavy libraries like `pandas` or `openpyxl`.
*   **Embedding Choice**: `BAAI/bge-large-en` (1024-dimensional normalized vectors) run on CPU with cosine similarity configuration in ChromaDB.
*   **Deduplication & Collision-Free Chunk IDs**: Formulated chunk IDs by hashing `{source_url}_{scheme_name or ''}_{i}_{split}`. This ensures unique IDs for different schemes whose factsheet chunks are indexed under the same factsheet landing URL, preventing ChromaDB `DuplicateIDError`.
*   **Unique Cache Key Hashing**: Designed diff-detection keys combining `{url}_{scheme}_{type}` in `data/hashes.json` to prevent collisions when different documents share the same URL, enabling incremental ingestion updates.
*   **Batched Progress Logging**: Added batched embedding generation (batch size = 100) in the indexer to monitor CPU generation progress (average 24-25s per batch for 1,820 chunks).
*   **Unit Test Optimizations**: Added `max_pages=2` parameter in `pdf_parser.py` and mocked offline sources in `test_ingestion.py` to reduce test runtimes from minutes to **7.57 seconds**.
*   **Avoiding LangChain Document Loaders for Ingestion**: Decided not to use generic `PyPDFLoader` or `WebBaseLoader`. Built custom extractions with `pdfplumber` and `trafilatura` for granular table precision and layout control (see ADR 1).

---

## 🛠️ Phase 3: RAG Pipeline Core Design

### 1. LLM Integration (Groq)
*   **Provider**: Groq via standard OpenAI-compatible client endpoint (`https://api.groq.com/openai/v1`).
*   **Model**: `openai/gpt-oss-120b` (loaded from configuration).
*   **Inference Settings**: `temperature=0.0`, `max_tokens=200`, `top_p=0.9`.

### 2. Retrieval & Re-ranking Flow
*   **Query Embedding**: Queries must be embedded using `BAAI/bge-large-en` with the instruction prefix:
    `"Represent this sentence for searching relevant passages: "` (achieves optimal BGE retrieval quality).
*   **Semantic Retrieval**: Queries ChromaDB collection `mutual_fund_docs` to fetch the top-5 chunks using cosine distance.
*   **Toggleable Re-ranker**: Implemented optional re-ranking using `cross-encoder/ms-marco-MiniLM-L-6-v2` locally on CPU (Top-5 chunks re-ranked down to Top-3). Controlled by the `USE_RERANKER` environment variable (disabled by default to maintain latency).

### 3. Factual & Layout Constraints
*   **Length Check**: Truncates LLM responses to a maximum of **3 sentences** along clean punctuation boundaries.
*   **Source Citations**: Extracts the metadata `source_url` from the retrieved context and appends it to the response dictionary as `source_url`.
*   **Last-Updated Footer**: Extends every response with a footer: `"Last updated from sources: <date>"` based on chunk metadata.

### 4. Fallback Lookup Search
*   **Similarity Threshold**: If the highest retrieval similarity score is less than `0.60` (indicating no relevant context in ChromaDB):
    1. The pipeline falls back to keyword matching the query against `scheme` and `notes` fields in `data/sources.json`.
    2. If a match is found, it extracts the official URL and returns:
       `"I don't have this information in my current sources. You may find more details at: <URL>"`
    3. If no match is found, it falls back to the standard AMFI guidance portal:
       `"I don't have this information in my current sources. Please visit the official AMC website or AMFI portal for the latest details."`

---

## 🏗️ Architectural Decisions Record (ADR)

### ADR 1: Avoiding LangChain Document Loaders for Ingestion
**Status:** Accepted
**Date:** 2026-06-09

#### Context
In Phase 2 (Data Ingestion Pipeline), we need to extract and index text from complex mutual fund PDFs (Factsheets, Scheme Information Documents) and HTML pages (AMC/AMFI guidelines). LangChain offers built-in Document Loaders (e.g., `PyPDFLoader`, `WebBaseLoader`, `Unstructured`), but we must decide whether to use them or rely on specialized, native Python libraries.

#### Decision
We will **not** use LangChain's built-in Document Loaders for the initial data extraction and parsing phase. Instead, we will use specialized libraries like `pdfplumber` for PDFs and `BeautifulSoup` / `trafilatura` for HTML web scraping.

#### Rationale
1. **Granular Control Over Complex Layouts:** Mutual fund documents (like Factsheets) have dense tabular data, multi-column layouts, watermarks, and repeating headers/footers. LangChain's generic PDF loaders often extract text as a flat string, scrambling multi-column layouts and ruining table integrity. `pdfplumber` gives us the exact coordinate-based control needed to extract tables accurately and ignore recurring noise (like headers and watermarks).
2. **Clean Web Extraction:** LangChain's web loaders typically fetch the entire page, including navigation menus, ads, and footers. By using `trafilatura` and `BeautifulSoup`, we can precisely target the main article content and strip out boilerplate "noise," which reduces token waste and significantly lowers the risk of hallucinations.
3. **Avoiding the "Black Box":** LangChain is excellent for Retrieve-and-Generate orchestration (which we leverage later), but its ingestion modules can be rigid. Writing custom extraction pipelines allows us to cleanly integrate our hash-based diff-detection (Phase 2.5) and tightly control the metadata schema on every chunk before inserting it into the vector store.

#### Consequences
- **Positive:** Higher quality, cleaner context provided to the LLM. Less noise and better tabular data understanding.
- **Negative:** Increased initial development time, as we must manually write and maintain parsing scripts rather than using one-line LangChain loaders.

*(Note: LangChain components like `RecursiveCharacterTextSplitter` are still used for text chunking, and we may leverage LangChain/LlamaIndex for the runtime RAG orchestration in Phase 3. This decision strictly applies to the initial document parsing and loading).*
