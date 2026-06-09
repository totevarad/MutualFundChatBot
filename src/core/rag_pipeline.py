"""
RAG Pipeline — End-to-end Retrieve → Re-Rank → Generate orchestration.
"""

import os
import json
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder

from src.utils.logger import get_logger
from src.core.prompt_templates import SYSTEM_PROMPT, QUERY_TEMPLATE, NO_INFO_RESPONSE
from src.core.response_formatter import format_response

from src.guardrails.input_sanitizer import sanitize_input
from src.guardrails.pii_detector import detect_pii
from src.core.query_classifier import classify_query
from src.guardrails.output_validator import validate_output

from src.memory.memory_manager import get_user_context, store_interaction
from src.memory.memory_formatter import format_memories

logger = get_logger(__name__)

# Initialize ChromaDB client
CHROMA_DIR = os.environ.get("CHROMA_PERSIST_DIR", "./vectorstore")
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_or_create_collection(
    name="mutual_fund_docs",
    metadata={"hnsw:space": "cosine"}
)

# Initialize BGE model
# Note: In production this should be loaded once globally
bge_model = SentenceTransformer('BAAI/bge-large-en')

# Initialize Re-ranker lazily
_cross_encoder = None
def get_reranker():
    global _cross_encoder
    if _cross_encoder is None:
        logger.info("Loading cross-encoder model...")
        _cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)
    return _cross_encoder

# Initialize OpenAI Client (Groq)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "dummy-key-for-tests")
llm_client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)
LLM_MODEL = os.environ.get("LLM_MODEL", "openai/gpt-oss-120b")


def get_fallback_url(query: str) -> str:
    """Find a relevant URL from sources.json if no valid chunks are found."""
    sources_path = os.path.join("data", "sources.json")
    if not os.path.exists(sources_path):
        return "https://www.amfiindia.com/investor-corner"
    
    with open(sources_path, "r") as f:
        sources = json.load(f)
        
    query_lower = query.lower()
    for s in sources:
        scheme = str(s.get("scheme", "")).lower()
        category = str(s.get("category", "")).lower()
        if scheme and scheme != "null" and scheme in query_lower:
            return s["url"]
        if category and category != "null" and category in query_lower:
            return s["url"]
            
    # Default fallback
    return "https://www.amfiindia.com/investor-corner"


def retrieve_chunks(query: str, top_k: int = 5) -> list[dict]:
    """Retrieve the top-K most relevant chunks for a query.

    Args:
        query: The user's query.
        top_k: Number of chunks to retrieve.

    Returns:
        List of chunk dicts with 'text', 'source_url', 'scheme_name', 'distance', etc.
    """
    # Embed query with BGE specific instruction
    query_prefix = "Represent this sentence for searching relevant passages: "
    query_vector = bge_model.encode(query_prefix + query, normalize_embeddings=True).tolist()
    
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k
    )
    
    chunks = []
    if not results["documents"] or not results["documents"][0]:
        return chunks
        
    for i in range(len(results["documents"][0])):
        text = results["documents"][0][i]
        metadata = results["metadatas"][0][i] if results["metadatas"] else {}
        distance = results["distances"][0][i] if results["distances"] else 1.0
        
        chunks.append({
            "text": text,
            "distance": distance,
            **metadata
        })
        
    return chunks


def query_pipeline(query: str, user_id: str | None = None) -> dict:
    """Execute the full RAG pipeline for a user query.

    Args:
        query: The user's factual query.
        user_id: Optional pseudonymous user ID for memory context.

    Returns:
        Dict with 'answer', 'source_url', 'last_updated', 'is_refusal', 'memory_used'.
    """
    # Phase 4 Guardrails: Input Sanitization
    query = sanitize_input(query)
    if not query:
        return format_response("Please provide a valid query.", source_url="", is_refusal=True)

    # Phase 4 Guardrails: PII Detection
    pii_results = detect_pii(query)
    if any(res.get("found") for res in pii_results):
        logger.warning("PII detected in query. Blocking request.")
        return format_response(
            answer="I cannot process queries containing sensitive personal information (like PAN, Aadhaar, phone numbers, or bank accounts). Please remove this information and try again.",
            source_url="",
            is_refusal=True
        )
        
    # Phase 4 Guardrails: Query Classification
    classification = classify_query(query)
    if classification["category"] == "advisory":
        logger.info("Advisory query detected. Refusing.")
        return format_response(
            answer="I can only provide factual information. Please refer to an AMFI-registered distributor or SEBI-registered advisor for investment recommendations.",
            source_url="https://www.amfiindia.com/investor-corner",
            is_refusal=True
        )
    elif classification["category"] == "out_of_scope":
        logger.info("Out of scope query detected. Will attempt to answer using general facts.")

    # 1. Retrieve
    chunks = retrieve_chunks(query, top_k=5)
    
    # Check similarity threshold (cosine distance: lower is better, similarity = 1 - distance)
    # If the closest chunk has distance > 0.40 (similarity < 0.60), fallback
    if not chunks or chunks[0].get("distance", 1.0) > 0.40:
        logger.info(f"Low similarity. Triggering fallback for query: {query}")
        fallback_url = get_fallback_url(query)
        answer = NO_INFO_RESPONSE.replace("<URL>", fallback_url)
        return format_response(
            answer=answer,
            source_url=fallback_url,
            last_updated=None,
            is_refusal=False,
            memory_used=[]
        )
        
    # 2. Re-rank (Optional)
    use_reranker = os.environ.get("USE_RERANKER", "false").lower() == "true"
    if use_reranker and len(chunks) > 1:
        reranker = get_reranker()
        pairs = [[query, chunk["text"]] for chunk in chunks]
        scores = reranker.predict(pairs)
        for i, score in enumerate(scores):
            chunks[i]["rerank_score"] = score
        chunks = sorted(chunks, key=lambda x: x["rerank_score"], reverse=True)[:3]
    else:
        chunks = chunks[:3]
        
    # 3. Generate
    context_text = "\n\n".join([f"- {c['text']}" for c in chunks])
    source_url = chunks[0].get("source_url", "Unknown")
    document_date = chunks[0].get("document_date", "Unknown")
    
    # Phase 5: Memory Integration
    raw_memories = get_user_context(user_id, query) if user_id else []
    user_memories = format_memories(raw_memories)
    
    prompt = QUERY_TEMPLATE.format(
        retrieved_chunks=context_text,
        source_url=source_url,
        document_date=document_date,
        user_memories=user_memories,
        user_query=query
    )
    
    try:
        response = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=200,
            top_p=0.9
        )
        raw_answer = response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM Generation failed: {e}")
        raw_answer = "I'm sorry, I encountered an error while processing your request."
        
    formatted = format_response(
        answer=raw_answer,
        source_url=source_url,
        last_updated=document_date,
        is_refusal=False,
        memory_used=[]
    )
    
    # Phase 4 Guardrails: Output Validation
    validation = validate_output(formatted)
    if not validation["is_valid"] and validation.get("has_advisory_language"):
        logger.warning("Advisory language detected in LLM output. Replacing with refusal.")
        return format_response(
            answer=validation["corrected_answer"],
            source_url="https://www.amfiindia.com/investor-corner",
            is_refusal=True,
            memory_used=raw_memories
        )
        
    # Phase 5: Store successful interaction
    if user_id:
        store_interaction(user_id, query, raw_answer)
        
    # Attach memory context to response
    formatted["memory_used"] = raw_memories
    return formatted
