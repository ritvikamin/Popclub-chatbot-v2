import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.concurrency import run_in_threadpool

from app.core.rag import get_rag
from app.core.vector_db import get_vector_db
from app.schemas.chat import ChatRequest, ChatResponse, StatsResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/query", response_model=ChatResponse)
async def query_bot(payload: ChatRequest):
    """Retrieve relevant chunks and return a grounded answer with citations."""
    history = [m.model_dump() for m in payload.history]
    try:
        # The pipeline is blocking (embedding model + network call to Gemini). Running it in a
        # worker thread keeps the event loop free to serve other requests meanwhile.
        result = await run_in_threadpool(get_rag().generate_grounded_answer, payload.message, history)
    except Exception:
        logger.exception("RAG pipeline failed")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "The AI service failed. Please try again.")
    return ChatResponse(**result)


@router.get("/stats", response_model=StatsResponse)
async def stats():
    """How much is indexed. Lets the UI warn when the knowledge base is empty."""
    db = get_vector_db()
    return StatsResponse(chunks=await run_in_threadpool(db.count), sources=await run_in_threadpool(db.sources))
