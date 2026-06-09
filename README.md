# SmartInvest AI (Mutual Fund FAQ Assistant)

A full-stack, facts-only Mutual Fund chatbot powered by **Retrieval-Augmented Generation (RAG)**. 

Designed to strictly retrieve objective financial data (expense ratios, exit loads, NAV, minimum SIPs) from official AMC factsheets while aggressively blocking subjective advisory queries or PII disclosures.

## 🏛 Architecture

- **Frontend**: Next.js 14 (App Router) + Tailwind CSS v4 (Nocturnal Growth Theme).
- **Backend**: FastAPI.
- **RAG Pipeline**:
  - **Vector Database**: Local ChromaDB instance (`./vectorstore`).
  - **Embeddings**: `BAAI/bge-large-en` (HuggingFace).
  - **Re-ranker**: `cross-encoder/ms-marco-MiniLM-L-6-v2`.
  - **LLM**: Groq (`llama-3.1-70b-versatile` or `llama3-70b-8192`).
- **Memory**: Mem0 (Stateful persistence per user UUID).
- **Automation**: GitHub Actions (Daily CRON scheduled data ingestion at 9:15 AM IST).

## 🏦 Sources Corpus

The bot relies exclusively on official data sources. The current corpus includes:
**AMC**: HDFC Mutual Fund
**Selected Schemes**:
1. HDFC Flexi Cap Fund (Flexi-Cap)
2. HDFC Top 100 Fund (Large-Cap)
3. HDFC Tax Saver Fund (ELSS)
4. HDFC Balanced Advantage Fund (Hybrid)

*Refer to `data/sources.json` for the exact URLs and metadata.*

## 🔒 Safety & Guardrails
- **Input Sanitization**: Strips XSS/SQLi attempts.
- **PII Detection**: Blocks queries containing PAN, Aadhaar, Phone, Email, or Bank Account numbers.
- **Query Classification**: Identifies and refuses "advisory" or "recommendation" queries with an educational fallback link to AMFI.
- **Output Validation**: Enforces exactly 1 citation, limits responses to 3 sentences, and scans LLM output for advisory language.

---

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.11+
- Node.js 18+

### 2. Backend Setup
```bash
# Install Python dependencies
python -m pip install -r requirements.txt
python -m pip install groq

# Set up environment variables
# Copy .env.example to .env and insert your Groq API key:
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

# (Optional) Run the data ingestion pipeline to build the vectorstore locally
python -m src.ingestion.run_pipeline

# Start the FastAPI Server
python -m uvicorn src.api.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend

# Install Node dependencies
npm install

# Start Next.js Development Server
npm run dev
```
Open `http://localhost:3000` to interact with the bot!

---

## ⚠️ Disclaimer
**Facts-only. No investment advice.**
This chatbot retrieves information from publicly available official documents. It does not calculate returns, compare historical performances for projection, or recommend funds. Please consult a SEBI-registered investment advisor for personal financial planning.
