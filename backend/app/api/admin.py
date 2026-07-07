from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.schemas.admin import IngestionResponse
from app.services.document_parser import DocumentParser
from app.core.vector_db import VectorDBEngine

router = APIRouter()

# Instantiate our vector database engine
db_engine = VectorDBEngine()

@router.post("/upload", response_model=IngestionResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    """
    Accepts a raw file upload (.txt or .md), reads its contents,
    chops it into overlapping context chunks, and saves it to ChromaDB.
    """
    # 1. Guardrail: Only allow text or markdown files for now
    if not file.filename.endswith(('.txt', '.md')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a .txt or .md file."
        )
        
    try:
        # 2. Read the raw text content from the uploaded file
        raw_bytes = await file.read()
        raw_text = raw_bytes.decode("utf-8")
        
        # 3. Clean up the text (remove excessive empty blank lines)
        cleaned_text = DocumentParser.parse_markdown(raw_text)
        
        # 4. Chop the text into 500-character pieces with a 50-character overlap
        chunks = DocumentParser.split_text(cleaned_text, chunk_size=500, chunk_overlap=50)
        
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file contains no readable text."
            )
            
        # 5. Convert chunks to math vectors and save them into ChromaDB
        db_engine.add_documents(chunks=chunks, filename=file.filename)
        
        # 6. Return a clear execution receipt to the client
        return IngestionResponse(
            success=True,
            filename=file.filename,
            chunks_created=len(chunks),
            message=f"Successfully processed file and generated {len(chunks)} searchable database entries."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process and index the document: {str(e)}"
        )