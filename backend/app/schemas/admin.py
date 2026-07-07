from pydantic import BaseModel, Field

class IngestionResponse(BaseModel):
    success: bool = Field(..., description="Indicates whether the document ingest operation was completed cleanly.")
    filename: str = Field(..., description="The name of the file processed.")
    chunks_created: int = Field(..., description="The structural slice count generated from parsing this payload.")
    message: str = Field(..., description="Human-readable execution status details.")