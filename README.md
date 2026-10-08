# POPclub Copilot v2

A Retrieval-Augmented Generation (RAG) chatbot that answers questions about POPclub (UPI payments, rewards, credit card) using only the documents you give it. **FastAPI** backend, **ChromaDB** vector store, local **sentence-transformers** embeddings, **Gemini 2.5 Flash** for generation, and a **Streamlit** chat UI.

## How it works

```
Streamlit UI ──HTTP──> FastAPI ──> embed question (MiniLM, local)
                                   │
                                   ├─> ChromaDB: top-3 chunks by cosine similarity
                                   ├─> drop chunks below MIN_RELEVANCE_SCORE
                                   │      └─ none left? -> refuse, no LLM call
                                   └─> Gemini: answer from those chunks only
                                         -> answer + citations (source, text, score)
```

**Ingestion** (`POST /admin/upload`): clean text -> split into 500-char chunks with 50-char overlap -> embed -> store in ChromaDB. Re-uploading a file replaces its previous chunks.

**Follow-up questions:** if there is chat history, the latest message is first rewritten into a standalone question (so "what about the fee?" becomes a searchable query), and recent history is included in the prompt for context.

## Design decisions

| Choice | Why |
| :-- | :-- |
| RAG instead of a fixed JSON/FAQ (v1) | Knowledge lives in documents that can be added or changed without code changes |
| FastAPI | Typed request/response models (Pydantic), automatic OpenAPI docs, easy to run blocking work in a thread pool |
| ChromaDB (embedded, persistent) | Zero-ops for a small corpus; no separate server. Would move to pgvector/Qdrant for multi-user scale |
| Local MiniLM embeddings | Free, fast on CPU, no extra API dependency or per-call cost |
| Cosine similarity | Compares meaning (direction) regardless of text length |
| Gemini 2.5 Flash, temperature 0 | Low latency/cost; deterministic output for factual answers |
| Streamlit | Python-only UI; the frontend is ~100 lines and talks to the same public API |

## Limitations (honest list)

- Grounding is enforced by prompt + a relevance cutoff; this **reduces** hallucination but cannot eliminate it.
- Chunking is character-based and can split mid-sentence; sentence/paragraph-aware splitting would retrieve better.
- Only `.txt` / `.md` files; no PDF parsing.
- No reranker, no hybrid (keyword + vector) search, no streaming responses.
- Admin auth is a single shared key, not per-user auth.
- `MIN_RELEVANCE_SCORE` was set by hand; it should be tuned against a labelled question set.

## Project structure

```text
backend/
  app/
    main.py              # app factory, CORS, router wiring, startup warm-up
    config.py            # settings from environment / .env (pydantic-settings)
    api/chat.py          # POST /chat/query, GET /chat/stats
    api/admin.py         # POST /admin/upload (requires X-Admin-Key)
    core/vector_db.py    # embeddings + ChromaDB access (shared singleton)
    core/rag.py          # retrieve -> filter -> prompt -> generate
    schemas/             # Pydantic request/response models
    services/document_parser.py  # cleaning + chunking
  requirements.txt
frontend/
  app.py                 # Streamlit UI
  requirements.txt
knowledge.txt            # sample knowledge base
```

## Setup

Backend and frontend use **separate virtual environments** so their dependencies cannot conflict.

**1. Backend**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```
Create `backend/.env`:
```
GEMINI_API_KEY="your-gemini-key"
ADMIN_API_KEY="any-long-random-string"
```
Run: `uvicorn app.main:app --reload`  (API docs at http://localhost:8000/docs)

**2. Frontend** (new terminal)
```bash
cd frontend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

**3. Load the knowledge base:** in the Streamlit sidebar enter your admin key, choose `knowledge.txt`, and click **Index document**.

## Configuration (environment variables)

| Variable | Default | Meaning |
| :-- | :-- | :-- |
| `GEMINI_API_KEY` | required | Google AI Studio key |
| `ADMIN_API_KEY` | empty (admin disabled) | Secret for the upload endpoint |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Generation model |
| `TOP_K` | `3` | Chunks retrieved per question |
| `MIN_RELEVANCE_SCORE` | `0.25` | Minimum cosine similarity for a chunk to be used |
| `MAX_HISTORY_MESSAGES` | `6` | Recent messages used for follow-ups |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | `500` / `50` | Chunking parameters |

Frontend: `API_URL` (default `http://localhost:8000`).

## API

- `POST /api/v1/chat/query` - body `{"message": "...", "history": [{"role": "user|assistant", "content": "..."}]}` -> `{"answer": "...", "citations": [{"source", "text", "score"}]}`
- `GET /api/v1/chat/stats` -> `{"chunks": 8, "sources": ["knowledge.txt"]}`
- `POST /api/v1/admin/upload` (header `X-Admin-Key`, multipart `file`) -> indexing receipt
- `GET /health`

## History

The earlier Next.js/TypeScript frontend is preserved in the `main` branch history.
