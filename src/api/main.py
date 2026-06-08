"""
FastAPI Application — Main entry point for the backend API server.

Usage:
    uvicorn src.api.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Mutual Fund FAQ Assistant",
    description="Facts-only mutual fund Q&A powered by RAG. No investment advice.",
    version="0.1.0",
)

# CORS — Allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # Next.js dev server
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


# TODO: Mount routes from src.api.routes in Phase 6
