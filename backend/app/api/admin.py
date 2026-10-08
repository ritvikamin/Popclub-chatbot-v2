import logging
import secrets

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from app.config import settings
from app.core.vector_db import get_vector_db
from app.schemas.admin import IngestionResponse
from app.services.document_parser import DocumentParser

logger = logging.getLogger(__name__)
router = APIRouter()


def require_admin(x_admin_key: str = Header(default="")) -> None:
    """Simple shared-secret auth: the caller must send the X-Admin-Key header."""
    if not settings.ADMIN_API_KEY:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Admin API is disabled (ADMIN_API_KEY not set).")
    # compare_digest runs in constant time, so response timing can't leak the key.
    if not secrets.compare_digest(x_admin_key.encode(), settings.ADMIN_API_KEY.encode()):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid admin key.")


@router.post(
    "/upload",
    response_model=IngestionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def upload_document(file: UploadFile = File(...)):
    """Accept a .txt/.md file, chunk it, embed it, and store it (replacing any older copy)."""
    if not (file.filename or "").lower().endswith((".txt", ".md")):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unsupported file format. Please upload a .txt or .md file.")

    raw = await file.read(settings.MAX_UPLOAD_BYTES + 1)
    if len(raw) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File too large.")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "File must be UTF-8 encoded text.")

    cleaned = DocumentParser.parse_markdown(text)
    chunks = DocumentParser.split_text(cleaned, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    chunks = [c for c in chunks if c]
    if not chunks:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The uploaded file contains no readable text.")

    try:
        await run_in_threadpool(get_vector_db().add_documents, chunks, file.filename)
    except Exception:
        logger.exception("Indexing failed")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to index the document.")

    return IngestionResponse(
        success=True,
        filename=file.filename,
        chunks_created=len(chunks),
        message=f"Indexed '{file.filename}' into {len(chunks)} searchable chunks.",
    )
