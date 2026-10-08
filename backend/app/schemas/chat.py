from typing import List, Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="The new user question.")
    history: List[ChatMessage] = Field(
        default_factory=list, description="Earlier messages, so follow-up questions work."
    )


class Citation(BaseModel):
    source: str
    text: str
    score: float = Field(..., description="Cosine similarity of the chunk to the question (0-1).")


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation] = Field(default_factory=list)


class StatsResponse(BaseModel):
    chunks: int = Field(..., description="Number of chunks currently indexed.")
    sources: List[str] = Field(..., description="Filenames that have been indexed.")
