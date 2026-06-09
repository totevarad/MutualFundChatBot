# Technology Stack Overview

This document details the granular technology stack, frameworks, libraries, and specific versions used across the Mutual Fund FAQ Assistant project.

## 1. Backend & API Layer
The backend is built as a lightweight, asynchronous REST API.

| Technology | Version | Purpose |
|---|---|---|
| **Python** | `3.11.x` | Core programming language for backend and AI pipelines. |
| **FastAPI** | `0.109.2` | High-performance async API framework for request routing. |
| **Uvicorn** | `0.27.1` | ASGI web server to run the FastAPI application. |
| **Pydantic** | `2.6.1` | Data validation, settings management, and API schemas. |
| **python-dotenv** | `1.0.1` | Environment variable management. |

## 2. Artificial Intelligence & RAG Pipeline
The core intelligence layer follows a Retrieve-Re-Rank-Generate (RAG) architecture.

| Technology | Version | Purpose |
|---|---|---|
| **LangChain** | `0.1.5` | Used selectively for text chunking (`RecursiveCharacterTextSplitter`) and optional prompt orchestration. |
| **OpenAI API** | `1.12.0` | Primary LLM generation (`gpt-4o-mini`). |
| **Mem0 (mem0ai)** | `0.1.0` | Persistent user-scoped conversational memory. |
| **Sentence-Transformers**| `2.3.1` | Local embedding generation. |
| **BAAI/bge-large-en** | `v1.5` | Embedding model (via HuggingFace/Sentence-Transformers). |
| **Cross-Encoder** | `v2` | Optional re-ranking model (`cross-encoder/ms-marco-MiniLM-L-6-v2`). |

## 3. Data Ingestion & Storage
The data ingestion pipeline heavily favors specialized, granular parsing over generic loaders.

| Technology | Version | Purpose |
|---|---|---|
| **ChromaDB** | `0.4.22` | Persistent local vector database for storing embeddings and metadata. |
| **pdfplumber** | `0.10.3` | High-fidelity PDF parsing (handling tables, ignoring watermarks/headers). |
| **BeautifulSoup4** | `4.12.3` | HTML parsing and targeted web scraping. |
| **Trafilatura** | `1.8.0` | Main content extraction from web pages (stripping nav/ads). |
| **PyMuPDF (fitz)** | `1.23.8` | Fallback high-speed PDF extraction (if needed). |
| **Requests** | `2.31.0` | HTTP requests for downloading PDFs and HTML. |

## 4. Frontend & User Interface
The frontend is a modern web application adhering to the **Nocturnal Growth** design system.

| Technology | Version | Purpose |
|---|---|---|
| **Next.js** | `14.1.0` | React framework using the App Router and Server Components. |
| **React / React DOM** | `18.2.0` | Core UI library. |
| **TypeScript** | `5.3.3` | Static typing for frontend stability. |
| **Tailwind CSS** | `3.4.1` | Utility-first CSS framework for styling and custom tokens. |
| **Lucide React** | `0.330.0` | Clean, modern iconography. |
| **clsx** | `2.1.0` | Utility for constructing `className` strings conditionally. |
| **tailwind-merge** | `2.2.1` | Utility to safely merge Tailwind CSS classes. |
| **Google Fonts** | `Latest` | `Hanken Grotesk` (Body) and `JetBrains Mono` (Code/Badges). |

## 5. DevOps, CI/CD & Testing
Infrastructure for scheduled updates and testing.

| Technology | Version | Purpose |
|---|---|---|
| **GitHub Actions** | `v4` | Automated CI/CD pipeline (daily cron jobs for data refresh). |
| **Pytest** | `8.0.0` | Backend unit and integration testing framework. |
| **Prettier** | `3.2.5` | Code formatting for frontend code. |
| **Ruff** | `0.2.1` | Extremely fast Python linter and code formatter. |
