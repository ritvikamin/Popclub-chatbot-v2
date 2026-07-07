from fastapi import APIRouter, HTTPException, status
from app.schemas.chat import ChatRequest, ChatResponse
from app.core.rag import RAGOrchestrator

router = APIRouter()

# Instantiate the engine globally at startup so we don't reload the models on every request
orchestrator = RAGOrchestrator()

@router.post("/query", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def query_bot(payload: ChatRequest):
    """
    Accepts user prompts, retrieves grounded context documents from the database,
    and returns a factual response certified with exact source citations.
    """
    try:
        # Run the complete RAG cycle
        result = orchestrator.generate_grounded_answer(user_query=payload.message)
        
        return ChatResponse(
            answer=result["answer"],
            citations=result["citations"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal pipeline failure: {str(e)}"
        )