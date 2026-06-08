# Mutual Fund FAQ Assistant — Evaluations

> **Comprehensive eval criteria for each implementation phase**
> Run these evaluations before advancing to the next phase.

---

## How to Use This Document

1. Complete all tasks for a phase in [implementationPlan.md](file:///c:/Users/varad/Desktop/Gen%20AI/MutualFundChatBot/docs/implementationPlan.md)
2. Run **every evaluation** in the corresponding phase section below
3. Mark each eval as ✅ PASS or ❌ FAIL
4. **All evals must pass** before moving to the next phase
5. If any eval fails, fix the issue and re-run

### Eval Types

| Type | Icon | Description |
|---|---|---|
| **Automated** | 🤖 | Run via script or command — objective pass/fail |
| **Manual** | 👁️ | Human review — inspect output or behavior |
| **Checklist** | 📋 | Verify a list of requirements is met |

---

## Phase 1: Project Setup & Corpus Definition

### 📋 EVAL-1.1: Directory Structure Verification

Verify the project structure matches the architecture specification.

```bash
# Run from project root
# Check that all required directories exist
python -c "
import os
required_dirs = [
    'docs', 'data', 'data/raw', 'data/processed',
    'src', 'src/ingestion', 'src/core', 'src/memory',
    'src/guardrails', 'src/api', 'src/utils',
    'frontend', 'tests', 'vectorstore',
    '.github/workflows'
]
missing = [d for d in required_dirs if not os.path.isdir(d)]
if missing:
    print(f'❌ FAIL: Missing directories: {missing}')
else:
    print('✅ PASS: All required directories exist')
"
```

| Check | Criterion | Pass? |
|---|---|---|
| `docs/` exists | Contains problemStatement.md, architecture.md, implementationPlan.md, evals.md | ☑ |
| `data/` exists | Contains `raw/`, `processed/`, `sources.json` | ☑ |
| `src/` exists | Contains `ingestion/`, `core/`, `memory/`, `guardrails/`, `api/`, `utils/` | ☑ |
| `frontend/` exists | Contains `app/`, `components/`, `lib/` | ☑ |
| `tests/` exists | Ready for test files | ☑ |
| `.github/workflows/` exists | Ready for CI/CD | ☑ |
| `.env` exists | Contains placeholder values for all required env vars | ☑ |
| `.gitignore` exists | Ignores `.env`, `vectorstore/`, `node_modules/`, `data/raw/` | ☑ |
| `requirements.txt` exists | Lists all Python dependencies | ☑ |

---

### 📋 EVAL-1.2: AMC & Scheme Selection Validation

| Check | Criterion | Pass? |
|---|---|---|
| One AMC selected | Single, official AMC chosen | ☑ |
| 3–5 schemes selected | Schemes are documented with names and categories | ☑ |
| Category diversity | At least 3 different categories (e.g., large-cap, flexi-cap, ELSS) | ☑ |
| All schemes belong to selected AMC | No cross-AMC mixing | ☑ |

---

### 🤖 EVAL-1.3: Corpus Source Validation

```bash
python -c "
import json

with open('data/sources.json') as f:
    sources = json.load(f)

# Check count
assert 15 <= len(sources) <= 25, f'❌ Source count: {len(sources)} (need 15-25)'

# Check required fields
required_fields = ['url', 'type', 'scheme', 'format']
for i, src in enumerate(sources):
    for field in required_fields:
        assert field in src, f'❌ Source {i}: missing field \"{field}\"'

# Check source types
types = set(s['type'] for s in sources)
required_types = {'factsheet', 'kim', 'sid', 'faq', 'amfi_guidance'}
missing_types = required_types - types
assert len(missing_types) <= 1, f'❌ Missing source types: {missing_types}'

# Check URLs are official
banned_domains = ['moneycontrol', 'groww', 'etmoney', 'kuvera', 'zerodha', 'paytm']
for src in sources:
    for domain in banned_domains:
        assert domain not in src['url'].lower(), f'❌ Non-official source: {src[\"url\"]}'

print(f'✅ PASS: {len(sources)} sources, types: {types}')
"
```

| Check | Criterion | Pass? |
|---|---|---|
| 15–25 URLs collected | Total source count in range | ☑ |
| All fields present | Each source has `url`, `type`, `scheme`, `format` | ☑ |
| Source type coverage | At least: factsheet, KIM/SID, FAQ, AMFI/SEBI | ☑ |
| Official sources only | No third-party blogs or aggregator sites | ☑ |
| URLs are accessible | All URLs return HTTP 200 (or downloadable PDF) | ☑ |
| Raw files downloaded | `data/raw/` contains downloaded PDFs and HTML files | ☑ |

---

### 🤖 EVAL-1.4: Environment Setup

```bash
# Python environment
pip install -r requirements.txt
python -c "import langchain; import chromadb; import fastapi; print('✅ Python deps OK')"

# Node.js / Next.js
cd frontend && npm install && npm run build
echo "✅ Next.js build OK"
```

| Check | Criterion | Pass? |
|---|---|---|
| Python dependencies install | `pip install -r requirements.txt` succeeds | ☑ |
| Key Python imports work | `langchain`, `chromadb`, `fastapi`, `pdfplumber`, `mem0` | ☑ |
| Next.js dependencies install | `npm install` in `frontend/` succeeds | ☑ |
| Next.js builds | `npm run build` in `frontend/` succeeds | ☑ |

---

## Phase 2: Data Ingestion Pipeline

### 🤖 EVAL-2.1: PDF Parsing Quality

```bash
python -c "
from src.ingestion.pdf_parser import parse_pdf
import os

pdf_files = [f for f in os.listdir('data/raw') if f.endswith('.pdf')]
assert len(pdf_files) > 0, '❌ No PDF files found in data/raw/'

for pdf_file in pdf_files[:3]:  # Test first 3
    text = parse_pdf(f'data/raw/{pdf_file}')
    assert len(text) > 100, f'❌ PDF too short: {pdf_file} ({len(text)} chars)'
    assert 'expense ratio' in text.lower() or 'nav' in text.lower() or 'fund' in text.lower(), \
        f'❌ PDF lacks expected content: {pdf_file}'
    print(f'  ✅ {pdf_file}: {len(text)} chars extracted')

print(f'✅ PASS: {len(pdf_files)} PDFs parsed successfully')
"
```

| Check | Criterion | Pass? |
|---|---|---|
| All PDFs parse without error | No exceptions during parsing | ☐ |
| Extracted text > 100 chars per PDF | Meaningful content extracted | ☐ |
| Tables extracted | Expense ratios, fund details readable in text | ☐ |
| Headers/footers removed | No page numbers, watermarks in output | ☐ |

---

### 🤖 EVAL-2.2: HTML Scraping Quality

```bash
python -c "
from src.ingestion.scraper import scrape_url
import json

with open('data/sources.json') as f:
    sources = json.load(f)

html_sources = [s for s in sources if s.get('format') == 'html']
assert len(html_sources) > 0, '❌ No HTML sources found'

for src in html_sources[:3]:
    text = scrape_url(src['url'])
    assert len(text) > 50, f'❌ Scrape too short: {src[\"url\"]} ({len(text)} chars)'
    assert '<script' not in text, f'❌ Script tags found in scraped text: {src[\"url\"]}'
    assert '<nav' not in text, f'❌ Nav elements found in scraped text: {src[\"url\"]}'
    print(f'  ✅ {src[\"url\"][:60]}...: {len(text)} chars')

print(f'✅ PASS: HTML scraping working')
"
```

| Check | Criterion | Pass? |
|---|---|---|
| All HTML pages scrape without error | No exceptions during scraping | ☐ |
| Extracted text > 50 chars per page | Meaningful content extracted | ☐ |
| No HTML tags in output | Script, nav, footer tags stripped | ☐ |
| Main content preserved | FAQ answers, scheme details present | ☐ |

---

### 🤖 EVAL-2.3: Chunking Quality

```bash
python -c "
from src.ingestion.chunker import chunk_text

sample_text = '''
Scheme Name: SBI Bluechip Fund
Category: Large Cap
Expense Ratio (Direct): 0.81%
Expense Ratio (Regular): 1.63%
Exit Load: 1% if redeemed within 1 year
Minimum SIP: Rs. 500
Benchmark: S&P BSE 100 TRI

The SBI Bluechip Fund is a large-cap equity fund that invests predominantly in
large-cap stocks. The fund aims to provide investors with opportunities for
long-term growth in capital through an active management of investments in a
diversified basket of equity stocks of companies whose market capitalization is
at least equal to or more than the least market capitalized stock of S&P BSE 100 Index.
'''

chunks = chunk_text(sample_text, source_url='https://example.com', scheme_name='SBI Bluechip Fund')

assert len(chunks) >= 1, f'❌ No chunks generated'
for i, chunk in enumerate(chunks):
    assert 100 <= len(chunk['text']) <= 1000, f'❌ Chunk {i} size: {len(chunk[\"text\"])} chars'
    assert 'source_url' in chunk, f'❌ Chunk {i}: missing source_url'
    assert 'scheme_name' in chunk, f'❌ Chunk {i}: missing scheme_name'
    assert 'chunk_id' in chunk, f'❌ Chunk {i}: missing chunk_id'

print(f'✅ PASS: {len(chunks)} chunks generated, all valid')
"
```

| Check | Criterion | Pass? |
|---|---|---|
| Chunks are 500–800 characters | Within configured size range | ☐ |
| Chunk overlap is 100–150 chars | No information lost at boundaries | ☐ |
| Metadata attached | Each chunk has `chunk_id`, `source_url`, `scheme_name`, `source_type`, `document_date`, `ingestion_date` | ☐ |
| Semantic boundaries preserved | No mid-sentence splits | ☐ |

---

### 🤖 EVAL-2.4: Embedding & Indexing

```bash
python -c "
from src.ingestion.indexer import create_index, get_collection_stats
import chromadb

# Verify embeddings are generated
stats = get_collection_stats()
assert stats['total_chunks'] > 0, f'❌ No chunks in vector store'
assert stats['total_chunks'] >= 50, f'❌ Too few chunks: {stats[\"total_chunks\"]} (expected 50+)'

# Verify embedding dimensionality (BAAI/bge-large-en = 1024-dim)
client = chromadb.PersistentClient(path='./vectorstore')
collection = client.get_collection('mutual_fund_docs')
result = collection.peek(1)
assert len(result['embeddings'][0]) == 1024, f'❌ Wrong embedding dimension: {len(result[\"embeddings\"][0])} (expected 1024)'

print(f'✅ PASS: {stats[\"total_chunks\"]} chunks indexed with 1024-dim embeddings')
"
```

| Check | Criterion | Pass? |
|---|---|---|
| ChromaDB collection created | `mutual_fund_docs` collection exists | ☐ |
| ≥ 50 chunks indexed | Sufficient coverage for 15–25 sources | ☐ |
| Embedding dimension = 1024 | `BAAI/bge-large-en` outputs 1024-dim vectors | ☐ |
| Metadata stored correctly | Query by `scheme_name` or `source_type` returns correct results | ☐ |
| No duplicate chunks | Deduplication logic removes near-identical chunks | ☐ |

---

### 🤖 EVAL-2.5: Diff Detection

```bash
python -c "
from src.ingestion.diff_detector import detect_changes
import json, os

# First run: all sources should be detected as 'changed'
changes = detect_changes('data/sources.json', 'data/hashes.json')
with open('data/sources.json') as f:
    total = len(json.load(f))
assert len(changes) == total, f'❌ First run should detect all sources as changed'

# Second run: no changes (same content)
changes2 = detect_changes('data/sources.json', 'data/hashes.json')
assert len(changes2) == 0, f'❌ Second run detected {len(changes2)} changes (expected 0)'

assert os.path.exists('data/hashes.json'), '❌ hashes.json not created'
print(f'✅ PASS: Diff detection working correctly')
"
```

| Check | Criterion | Pass? |
|---|---|---|
| First run detects all as changed | All sources flagged on first run | ☐ |
| Second run detects zero changes | No false positives on unchanged content | ☐ |
| `data/hashes.json` created | Hash cache persisted to disk | ☐ |

---

### 🤖 EVAL-2.6: Full Pipeline Run

```bash
python -m src.ingestion.run_pipeline
python -m src.ingestion.validate
```

| Check | Criterion | Pass? |
|---|---|---|
| Pipeline completes without error | No exceptions during full run | ☐ |
| Validation passes | All sources have at least one chunk | ☐ |
| Metadata complete | No null `source_url` or `scheme_name` values | ☐ |
| Logs generated | Structured logs with timestamps | ☐ |

---

## Phase 3: RAG Pipeline Core

### 🤖 EVAL-3.1: Factual Query Accuracy

Test with 10 known factual queries and expected answers:

```python
# tests/test_rag_pipeline.py
import pytest
from src.core.rag_pipeline import query_pipeline

FACTUAL_QUERIES = [
    {
        "query": "What is the expense ratio of SBI Bluechip Fund?",
        "expected_keywords": ["expense ratio", "0."],
        "must_have_source": True
    },
    {
        "query": "What is the exit load for SBI Bluechip Fund?",
        "expected_keywords": ["exit load", "1%", "year"],
        "must_have_source": True
    },
    {
        "query": "What is the minimum SIP amount?",
        "expected_keywords": ["sip", "500", "minimum"],
        "must_have_source": True
    },
    {
        "query": "What is the lock-in period for ELSS?",
        "expected_keywords": ["3 year", "lock"],
        "must_have_source": True
    },
    {
        "query": "What is the benchmark index for SBI Bluechip Fund?",
        "expected_keywords": ["benchmark", "bse", "nifty"],
        "must_have_source": True
    },
    {
        "query": "What is the riskometer classification?",
        "expected_keywords": ["risk", "high", "moderate"],
        "must_have_source": True
    },
    {
        "query": "How to download my account statement?",
        "expected_keywords": ["statement", "download"],
        "must_have_source": True
    },
    {
        "query": "What is NAV?",
        "expected_keywords": ["net asset value", "nav"],
        "must_have_source": True
    },
    {
        "query": "What is the fund manager name?",
        "expected_keywords": ["fund manager"],
        "must_have_source": True
    },
    {
        "query": "What are the investment options available?",
        "expected_keywords": ["growth", "dividend", "idcw"],
        "must_have_source": True
    },
]

@pytest.mark.parametrize("test_case", FACTUAL_QUERIES)
def test_factual_query(test_case):
    result = query_pipeline(test_case["query"])

    # Response is not empty
    assert result["answer"], f"Empty answer for: {test_case['query']}"

    # Response contains expected keywords (at least one)
    answer_lower = result["answer"].lower()
    keyword_match = any(kw in answer_lower for kw in test_case["expected_keywords"])
    assert keyword_match, f"Missing keywords {test_case['expected_keywords']} in: {result['answer']}"

    # Source URL present
    if test_case["must_have_source"]:
        assert result["source_url"], f"Missing source_url for: {test_case['query']}"
        assert result["source_url"].startswith("http"), f"Invalid source_url: {result['source_url']}"
```

| Check | Criterion | Pass? |
|---|---|---|
| ≥ 8/10 queries return correct answers | Answers contain expected keywords | ☐ |
| All answers have valid source URLs | URLs start with `http` and point to official sources | ☐ |
| No hallucinated information | Answers only contain facts from retrieved context | ☐ |

---

### 🤖 EVAL-3.2: Response Format Compliance

```python
# tests/test_response_format.py
import pytest, re
from src.core.rag_pipeline import query_pipeline

QUERIES = [
    "What is the expense ratio of SBI Bluechip Fund?",
    "What is the exit load?",
    "What is the minimum SIP amount?",
]

@pytest.mark.parametrize("query", QUERIES)
def test_response_format(query):
    result = query_pipeline(query)

    # ≤ 3 sentences
    sentences = [s.strip() for s in re.split(r'[.!?]+', result["answer"]) if s.strip()]
    assert len(sentences) <= 3, f"Too many sentences ({len(sentences)}): {result['answer']}"

    # Exactly 1 citation URL
    assert result["source_url"], "Missing source_url"
    assert isinstance(result["source_url"], str), "source_url must be a string"

    # Last updated date present
    assert result["last_updated"], "Missing last_updated date"

    # Not a refusal
    assert not result["is_refusal"], f"Unexpected refusal for factual query: {query}"
```

| Check | Criterion | Pass? |
|---|---|---|
| All responses ≤ 3 sentences | Sentence count validated | ☐ |
| Exactly 1 source URL per response | `source_url` field populated | ☐ |
| `last_updated` date present | Date field populated | ☐ |
| Footer format correct | `"Last updated from sources: <date>"` | ☐ |

---

### 🤖 EVAL-3.3: Retrieval Quality

```python
# tests/test_retrieval.py
from src.core.rag_pipeline import retrieve_chunks

def test_retrieval_relevance():
    query = "What is the expense ratio of SBI Bluechip Fund?"
    chunks = retrieve_chunks(query, top_k=5)

    assert len(chunks) == 5, f"Expected 5 chunks, got {len(chunks)}"

    # At least 1 chunk should contain "expense ratio"
    relevant = [c for c in chunks if "expense ratio" in c["text"].lower()]
    assert len(relevant) >= 1, "No relevant chunks found for 'expense ratio' query"

    # All chunks have metadata
    for chunk in chunks:
        assert chunk["source_url"], "Chunk missing source_url"
        assert chunk["scheme_name"], "Chunk missing scheme_name"

def test_no_results_handling():
    # Irrelevant query returns standard refusal
    query = "What is the weather in Mumbai?"
    res = query_pipeline(query)
    assert "I don't have this information in my current sources" in res["answer"]

    # Missing query with keyword match returns relevant link from sources.json
    query2 = "How to complete FATCA CRS forms?"
    res2 = query_pipeline(query2)
    assert "https://www.hdfcfund.com/investor-desk/fatca-crs" in res2["answer"] or res2["source_url"] == "https://www.hdfcfund.com/investor-desk/fatca-crs"
```

| Check | Criterion | Pass? |
|---|---|---|
| Top-5 retrieval returns 5 chunks | Correct chunk count | ☐ |
| ≥ 1 chunk is relevant to query | Contains query-related keywords | ☐ |
| All chunks have complete metadata | `source_url`, `scheme_name`, `source_type` present | ☐ |
| Out-of-scope queries handled | Returns fallback message and routes to relevant link from `sources.json` if possible | ☐ |

---

### 🤖 EVAL-3.4: LLM Integration

| Check | Criterion | Pass? |
|---|---|---|
| LLM API key configured | `.env` has valid `OPENAI_API_KEY` or `GOOGLE_API_KEY` | ☐ |
| LLM responds within 5 seconds | Response time < 5s per query | ☐ |
| Temperature = 0.0 | Deterministic outputs | ☐ |
| Fallback works | If LLM is unavailable, returns error gracefully (no crash) | ☐ |

---

## Phase 4: Safety & Guardrails

### 🤖 EVAL-4.1: Advisory Query Refusal

```python
# tests/test_query_classifier.py
import pytest
from src.core.query_classifier import classify_query

ADVISORY_QUERIES = [
    "Should I invest in SBI Bluechip Fund?",
    "Which fund is better, SBI Bluechip or HDFC Top 100?",
    "Can you recommend a good mutual fund?",
    "Will this fund give 15% returns next year?",
    "Is SBI Bluechip a good investment?",
    "Should I do SIP in this fund or lumpsum?",
    "Which is the best ELSS fund?",
    "Can this fund beat fixed deposits?",
]

@pytest.mark.parametrize("query", ADVISORY_QUERIES)
def test_advisory_refusal(query):
    result = classify_query(query)
    assert result["category"] in ["advisory", "performance_comparison"], \
        f"Advisory query not classified correctly: '{query}' → {result['category']}"
```

| Check | Criterion | Pass? |
|---|---|---|
| All 8 advisory queries refused | Classified as "advisory" or "performance_comparison" | ☐ |
| Refusal response is polite | Contains no rude or dismissive language | ☐ |
| Refusal includes educational link | AMFI or SEBI URL provided | ☐ |
| Facts-only limitation mentioned | Response reinforces the assistant's scope | ☐ |

---

### 🤖 EVAL-4.2: PII Detection

```python
# tests/test_guardrails.py
import pytest
from src.guardrails.pii_detector import detect_pii

PII_TESTS = [
    ("My PAN is ABCDE1234F", ["pan"]),
    ("Aadhaar: 1234 5678 9012", ["aadhaar"]),
    ("Call me at 9876543210", ["phone"]),
    ("Email: user@example.com", ["email"]),
    ("OTP is 456789", ["otp"]),
    ("Account number: 12345678901234", ["account"]),
    ("What is the expense ratio?", []),  # No PII
    ("My SIP amount is 500", []),  # Not PII — just a number
]

@pytest.mark.parametrize("text,expected_types", PII_TESTS)
def test_pii_detection(text, expected_types):
    detected = detect_pii(text)
    detected_types = [d["type"] for d in detected]
    for expected in expected_types:
        assert expected in detected_types, f"Failed to detect {expected} in: '{text}'"
    if not expected_types:
        assert len(detected) == 0, f"False positive PII detection in: '{text}' → {detected_types}"
```

| Check | Criterion | Pass? |
|---|---|---|
| PAN detected | `ABCDE1234F` pattern caught | ☐ |
| Aadhaar detected | `1234 5678 9012` pattern caught | ☐ |
| Phone detected | `9876543210` pattern caught | ☐ |
| Email detected | `user@example.com` pattern caught | ☐ |
| No false positives | "SIP amount is 500" does NOT trigger PII | ☐ |
| PII values never stored | Detected types logged, but actual values discarded | ☐ |

---

### 🤖 EVAL-4.3: Input Sanitization

```python
# tests/test_guardrails.py
from src.guardrails.input_sanitizer import sanitize_input

def test_xss_stripped():
    assert "<script>" not in sanitize_input('<script>alert("xss")</script>What is SIP?')

def test_sql_injection_stripped():
    assert "DROP TABLE" not in sanitize_input("'; DROP TABLE users; --")

def test_long_input_truncated():
    long_input = "a" * 1000
    result = sanitize_input(long_input)
    assert len(result) <= 500

def test_normal_input_preserved():
    normal = "What is the expense ratio of SBI Bluechip Fund?"
    assert sanitize_input(normal) == normal
```

| Check | Criterion | Pass? |
|---|---|---|
| XSS patterns removed | `<script>` tags stripped | ☐ |
| SQL injection neutralized | `DROP TABLE` removed | ☐ |
| Long inputs truncated | > 500 chars truncated | ☐ |
| Normal queries unchanged | Factual queries pass through intact | ☐ |

---

### 🤖 EVAL-4.4: Output Validation

```python
# tests/test_guardrails.py
from src.guardrails.output_validator import validate_output

def test_valid_output_passes():
    output = {
        "answer": "The expense ratio is 0.81%. This is for the Direct Plan.",
        "source_url": "https://www.sbimf.com/...",
        "last_updated": "2026-06-08"
    }
    assert validate_output(output)["is_valid"] == True

def test_too_long_output_fails():
    output = {
        "answer": "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five.",
        "source_url": "https://www.sbimf.com/...",
        "last_updated": "2026-06-08"
    }
    result = validate_output(output)
    assert result["is_valid"] == False or len(result["corrected_answer"].split('. ')) <= 3

def test_advisory_language_caught():
    output = {
        "answer": "I recommend investing in this fund for good returns.",
        "source_url": "https://www.sbimf.com/...",
        "last_updated": "2026-06-08"
    }
    result = validate_output(output)
    assert result["has_advisory_language"] == True
```

| Check | Criterion | Pass? |
|---|---|---|
| Valid outputs pass | Well-formed responses accepted | ☐ |
| Long outputs flagged/corrected | > 3 sentences triggers correction | ☐ |
| Advisory language detected | "recommend", "should invest" caught | ☐ |
| Missing citation flagged | No `source_url` triggers correction | ☐ |

---

### 👁️ EVAL-4.5: End-to-End Guardrail Flow

Manually test the integrated pipeline with these queries:

| # | Query | Expected Behavior | Pass? |
|---|---|---|---|
| 1 | "What is the expense ratio?" | ✅ Factual answer with citation | ☐ |
| 2 | "Should I invest in this fund?" | ❌ Polite refusal + AMFI link | ☐ |
| 3 | "My PAN is ABCDE1234F, check my account" | ❌ Privacy warning, PII not processed | ☐ |
| 4 | `<script>alert('xss')</script>What is SIP?` | ✅ XSS stripped, answers "What is SIP?" | ☐ |
| 5 | "Which fund will give best returns next year?" | ❌ Refusal + factsheet link | ☐ |
| 6 | "What is the weather in Mumbai?" | ❌ "I don't have this information" | ☐ |

---

## Phase 5: Memory Layer (Mem0)

### 🤖 EVAL-5.1: Memory Store & Retrieve

```python
# tests/test_memory.py
from src.memory.memory_manager import get_user_context, store_interaction, clear_user_memory

def test_store_and_retrieve():
    user_id = "test_user_001"
    clear_user_memory(user_id)  # Clean slate

    # Store an interaction
    store_interaction(user_id, "What is the expense ratio of SBI Bluechip?", "The expense ratio is 0.81%.")

    # Retrieve memories
    memories = get_user_context(user_id, "Tell me about SBI Bluechip Fund")
    assert len(memories) >= 1, "No memories retrieved after storing interaction"
    assert any("sbi" in m.lower() or "bluechip" in m.lower() or "expense" in m.lower() for m in memories), \
        f"Retrieved memories not relevant: {memories}"

    # Cleanup
    clear_user_memory(user_id)

def test_clear_memory():
    user_id = "test_user_002"
    store_interaction(user_id, "What is ELSS?", "ELSS is a tax-saving mutual fund.")
    clear_user_memory(user_id)
    memories = get_user_context(user_id, "ELSS")
    assert len(memories) == 0, f"Memories not cleared: {memories}"

def test_empty_memory_graceful():
    user_id = "new_user_999"
    memories = get_user_context(user_id, "What is SIP?")
    assert isinstance(memories, list), "Should return empty list for new user"
```

| Check | Criterion | Pass? |
|---|---|---|
| Store interaction works | No errors during `memory.add()` | ☐ |
| Retrieve returns relevant memories | Semantic search finds stored memories | ☐ |
| Clear memory works | `delete_all()` removes all user memories | ☐ |
| New user returns empty list | Graceful handling of cold start | ☐ |
| Memory limit respected | `limit=5` enforced in retrieval | ☐ |

---

### 🤖 EVAL-5.2: Memory Integration with RAG

```python
# tests/test_memory.py
from src.core.rag_pipeline import query_pipeline
from src.memory.memory_manager import store_interaction, clear_user_memory

def test_memory_enhances_followup():
    user_id = "test_user_followup"
    clear_user_memory(user_id)

    # First query
    r1 = query_pipeline("What is the expense ratio of SBI Bluechip Fund?", user_id=user_id)
    assert r1["answer"], "First query failed"

    # Follow-up query (should use memory context)
    r2 = query_pipeline("What about its exit load?", user_id=user_id)
    assert r2["answer"], "Follow-up query failed"
    # The response should relate to SBI Bluechip (from memory context)

    clear_user_memory(user_id)

def test_pipeline_works_without_memory():
    # No user_id — pipeline should work without memory
    result = query_pipeline("What is ELSS lock-in period?")
    assert result["answer"], "Pipeline failed without user_id"
    assert not result.get("is_refusal"), "Unexpected refusal"
```

| Check | Criterion | Pass? |
|---|---|---|
| Follow-up queries use memory | Second query leverages context from first | ☐ |
| Pipeline works without user_id | Graceful degradation when no memory | ☐ |
| Memory context appears in prompt | `{user_memories}` slot populated | ☐ |

---

### 📋 EVAL-5.3: Memory Privacy Compliance

| Check | Criterion | Pass? |
|---|---|---|
| `user_id` is UUID, not PII | No email/phone/name used as ID | ☐ |
| Memory contains no PII | Only behavioral preferences stored | ☐ |
| Memory contains no financial data | No account numbers, PAN, etc. in memory | ☐ |
| Clear memory is accessible | User can clear their own memory | ☐ |

---

## Phase 6: Backend API (FastAPI)

### 🤖 EVAL-6.1: API Endpoint Tests

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

def test_chat_factual():
    r = client.post("/api/chat", json={"query": "What is the expense ratio of SBI Bluechip Fund?"})
    assert r.status_code == 200
    data = r.json()
    assert data["answer"]
    assert data["source_url"]
    assert data["last_updated"]
    assert data["is_refusal"] == False

def test_chat_advisory():
    r = client.post("/api/chat", json={"query": "Should I invest in SBI Bluechip?"})
    assert r.status_code == 200
    data = r.json()
    assert data["is_refusal"] == True

def test_chat_with_memory():
    r = client.post("/api/chat", json={"query": "What is ELSS?", "user_id": "test_api_user"})
    assert r.status_code == 200
    assert "memory_used" in r.json()

def test_sources():
    r = client.get("/api/sources")
    assert r.status_code == 200
    sources = r.json()
    assert len(sources) >= 15

def test_memory_get():
    r = client.get("/api/memory/test_api_user")
    assert r.status_code == 200

def test_memory_delete():
    r = client.delete("/api/memory/test_api_user")
    assert r.status_code == 200

def test_invalid_input():
    r = client.post("/api/chat", json={})
    assert r.status_code == 422  # Validation error
```

| Check | Criterion | Pass? |
|---|---|---|
| `GET /api/health` returns 200 | Health check passes | ☐ |
| `POST /api/chat` with factual query | Returns answer + source + date | ☐ |
| `POST /api/chat` with advisory query | Returns refusal | ☐ |
| `POST /api/chat` with `user_id` | Memory context used | ☐ |
| `GET /api/sources` returns sources | ≥ 15 sources returned | ☐ |
| `GET /api/memory/{user_id}` works | Returns user memories | ☐ |
| `DELETE /api/memory/{user_id}` works | Clears user memories | ☐ |
| Invalid input returns 422 | Pydantic validation works | ☐ |

---

### 🤖 EVAL-6.2: Streaming Response

| Check | Criterion | Pass? |
|---|---|---|
| Streaming endpoint works | Tokens stream in real-time | ☐ |
| Citation sent as final chunk | Source URL appended at end | ☐ |
| Client can consume stream | `ReadableStream` consumable by frontend | ☐ |

---

### 📋 EVAL-6.3: CORS & Security

| Check | Criterion | Pass? |
|---|---|---|
| CORS allows Next.js origin | `localhost:3000` allowed in development | ☐ |
| CORS blocks unknown origins | Random domains rejected | ☐ |
| No API keys exposed | Keys only in `.env`, not in responses | ☐ |
| Error responses don't leak internals | No stack traces in production errors | ☐ |

---

## Phase 7: Frontend UI (Next.js - Nocturnal Growth Theme)

### 👁️ EVAL-7.1: UI Component Checklist (Nocturnal Growth)

| Component | Criterion / Specification | Pass? |
|---|---|---|
| **Theme & Palette** | Background and surface colors are deep slate/navy (`#101415`), primary actions/accents are emerald green (`#4edea3` or `#10b981`), borders are slate-gray (`#3c4a42` or `#86948a`). | ☐ |
| **Typography** | Headlines and body text use **Hanken Grotesk**; labels, badges, stats, and small numbers use **JetBrains Mono**. | ☐ |
| **Chat History Sidebar** | Collapsible left sidebar containing logo ("SmartInvest AI"), "New Conversation" button, past history sections ("Today", "Previous 7 Days"), and bottom "Settings" item. | ☐ |
| **Market Ticker** | Scrolling ticker present below the header, animating horizontal index trends (NIFTY 50, SENSEX, BANKNIFTY) with colored status indicators (green ▲ / red ▼). | ☐ |
| **Welcome Screen Dashboard** | Initial chat state displays welcome greeting: "How can I help you with your investments today?" and two column Quick Access Cards. | ☐ |
| **Active Chat Viewport** | Chat messages render with dynamic avatar (robot icon for assistant), user and assistant text, and suggested follow-ups. Scrollbar customized to be thin/dark. | ☐ |
| **Response Citation** | Clicking source citation badging opens the official document link in a new browser tab. | ☐ |
| **Regulatory Advisory** | Persistent advisory footer at the bottom of the screen displaying SEBI/AMFI regulatory warnings in `label-md` JetBrains Mono text. | ☐ |
| **Border Radii & Shapes** | Inputs and buttons utilize 4px border radius. Cards and containers use 8px border radius. Suggested follow-up prompt chips are fully pill-shaped. | ☐ |
| **Visual Animations** | `animated-mesh-bg` gradient shifts colors on the canvas; `marquee` scrolls index ticker smoothly; `typing-dot` bounces three indicators for bot loading states. | ☐ |

---

### 👁️ EVAL-7.2: Functional Test Scenarios

| # | Action | Expected Result | Pass? |
|---|---|---|---|
| 1 | Click Quick Access card (e.g. "What is an SIP?") | Sends query, transitions view state to active chat, displays response | ☐ |
| 2 | Type factual query + press Enter | Message displays, typing indicators animate, streaming response renders with citation and footer | ☐ |
| 3 | Type advisory query | Polite refusal shown with SEBI/AMFI educational reference link | ☐ |
| 4 | Click suggest follow-up pill | Appends query, sends, and displays relevant answers | ☐ |
| 5 | Focus input field | 1px border glows primary Emerald Green (`#4edea3`) | ☐ |
| 6 | Rapid successive queries | Chat history handles them, screen scrolls automatically to the latest bubble, customized scrollbar active | ☐ |
| 7 | Empty input + Send | Button disabled or input submission prevented | ☐ |
| 8 | Very long query (> 500 chars) | Sanitized/truncated warning displayed according to guardrails | ☐ |
| 9 | Click "Clear Chat" button | Prompts confirmation, clears memory context and local conversation history | ☐ |
| 10 | Refresh browser page | User session UUID persists in `localStorage`, maintaining continuity | ☐ |

---

### 👁️ EVAL-7.3: Responsive Design & Navigation

| Check | Criterion | Pass? |
|---|---|---|
| **Desktop View (>1024px)** | Left sidebar and main panel visible; grid layouts spread across columns; full footer advisory | ☐ |
| **Tablet View (768px - 1024px)** | Sidebar collapses or moves to side-panel; chat area occupies full width; responsive spacing | ☐ |
| **Mobile View (<768px)** | Left sidebar completely hidden (accessible via hamburger menu toggle); Bottom navigation bar (Chat, Portfolio, Markets, Profile) visible at the bottom of screen; input area adapts to full width | ☐ |
| **Keyboard Accessibility** | Full tab traversal through inputs, buttons, and badges with visible focus outlines | ☐ |

---

### 🤖 EVAL-7.4: Build & Performance

```bash
cd frontend
npm run build   # Must succeed with no errors
npm run lint    # No lint/typescript errors
```

| Check | Criterion | Pass? |
|---|---|---|
| `npm run build` succeeds | Production build compiles with zero errors | ☐ |
| `npm run lint` passes | ESLint checks complete successfully | ☐ |
| First Contentful Paint < 1.5s | Fast initial paint under 1.5 seconds | ☐ |
| Zero console exceptions | No error/exception trace in browser developer tools | ☐ |

---

## Phase 8: Scheduled Data Refresh (GitHub Actions)

### 📋 EVAL-8.1: Workflow Configuration

| Check | Criterion | Pass? |
|---|---|---|
| `.github/workflows/daily-data-refresh.yml` exists | File present | ☐ |
| Cron expression correct | `'45 3 * * *'` = 9:15 AM IST | ☐ |
| `workflow_dispatch` enabled | Manual trigger available | ☐ |
| Python 3.11 configured | Correct version in setup step | ☐ |
| Secrets referenced | `OPENAI_API_KEY`, `MEM0_API_KEY`, `DEPLOY_TARGET` | ☐ |
| Timeout set | `timeout-minutes: 30` | ☐ |
| Artifact upload configured | Vectorstore uploaded with 7-day retention | ☐ |

---

### 🤖 EVAL-8.2: Manual Trigger Test

```bash
# Trigger via GitHub CLI (or GitHub UI)
gh workflow run daily-data-refresh.yml
gh run list --workflow=daily-data-refresh.yml --limit=1
```

| Check | Criterion | Pass? |
|---|---|---|
| Manual trigger works | Workflow starts on `workflow_dispatch` | ☐ |
| Pipeline step succeeds | `run_pipeline` completes without error | ☐ |
| Validation step succeeds | `validate` confirms data integrity | ☐ |
| Artifact uploaded | Vectorstore artifact available in Actions | ☐ |
| Deploy step succeeds | Updated vectorstore deployed | ☐ |

---

### 📋 EVAL-8.3: Incremental Refresh Logic

| Check | Criterion | Pass? |
|---|---|---|
| First run processes all sources | Hash cache empty → all sources ingested | ☐ |
| Second run processes zero sources | No changes → no re-ingestion | ☐ |
| Changed source re-processed | Modified source detected and re-ingested | ☐ |
| Weekly full refresh works | Sunday run rebuilds entire corpus | ☐ |

---

## Phase 9: Integration Testing & Polish

### 🤖 EVAL-9.1: End-to-End Integration

```bash
# Start backend
cd .. && uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &

# Start frontend
cd frontend && npm run dev &

# Run integration tests
python -m pytest tests/ -v --tb=short
```

| Check | Criterion | Pass? |
|---|---|---|
| Frontend connects to backend | API calls succeed from browser | ☐ |
| Chat flow works end-to-end | Query → API → RAG → response → UI | ☐ |
| Memory persists across page loads | User context maintained | ☐ |
| Streaming works in browser | Tokens render incrementally | ☐ |
| Refusal displays correctly | Advisory queries show polite refusal in UI | ☐ |

---

### 🤖 EVAL-9.2: Performance Targets

| Metric | Target | How to Measure | Pass? |
|---|---|---|---|
| End-to-end response time | < 3 seconds | Measure from query submit to full response | ☐ |
| Retrieval latency | < 500ms | Time for ChromaDB semantic search | ☐ |
| Memory lookup latency | < 200ms | Time for Mem0 `search()` call | ☐ |
| Frontend First Contentful Paint | < 1.5s | Lighthouse audit | ☐ |
| API cold start | < 5 seconds | Time from `uvicorn` start to first response | ☐ |

---

### 📋 EVAL-9.3: Documentation Completeness

| Check | Criterion | Pass? |
|---|---|---|
| `README.md` exists | Contains setup, AMC/schemes, architecture, limitations | ☐ |
| Setup instructions work | A new developer can set up the project from README | ☐ |
| Architecture documented | Link to `docs/architecture.md` | ☐ |
| Known limitations listed | Honest assessment of gaps | ☐ |
| Disclaimer present | "Facts-only. No investment advice." in README and UI | ☐ |
| API docs accessible | FastAPI `/docs` endpoint works | ☐ |

---

### 📋 EVAL-9.4: Security & Compliance Final Checklist

| Check | Criterion | Pass? |
|---|---|---|
| No API keys in code | All keys in `.env` or secrets | ☐ |
| `.env` in `.gitignore` | Not committed to repository | ☐ |
| No PII stored anywhere | No PAN, Aadhaar, phone, email in DB or logs | ☐ |
| No investment advice in any response | Tested with 10+ advisory queries | ☐ |
| All sources are official | No third-party blogs or aggregators | ☐ |
| CORS properly configured | Only allowed origins accepted | ☐ |
| Error responses don't leak secrets | Stack traces hidden in production | ☐ |

---

### 👁️ EVAL-9.5: Cross-Browser & Device Testing

| Browser/Device | Works? | Notes |
|---|---|---|
| Chrome (Desktop) | ☐ | |
| Firefox (Desktop) | ☐ | |
| Safari (Desktop) | ☐ | |
| Edge (Desktop) | ☐ | |
| Chrome (Android) | ☐ | |
| Safari (iOS) | ☐ | |

---

## Summary: Eval Pass Rates

Track your eval pass rates per phase:

| Phase | Total Evals | Passed | Failed | Status |
|---|---|---|---|---|
| 1 - Project Setup | 23 | 23 | 0 | ☑ |
| 2 - Data Ingestion | 24 | _ | _ | ☐ |
| 3 - RAG Pipeline | 16 | _ | _ | ☐ |
| 4 - Safety & Guardrails | 24 | _ | _ | ☐ |
| 5 - Memory Layer | 12 | _ | _ | ☐ |
| 6 - Backend API | 16 | _ | _ | ☐ |
| 7 - Frontend UI | 26 | _ | _ | ☐ |
| 8 - Scheduled Refresh | 12 | _ | _ | ☐ |
| 9 - Integration & Polish | 22 | _ | _ | ☐ |
| **TOTAL** | **178** | **_** | **_** | **☐** |

> [!CAUTION]
> **All 178 evaluations must pass before the project is considered complete.** Any failing eval indicates a gap that must be fixed before deployment.
