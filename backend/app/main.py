from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, chat
from app.config import settings
from app.core.rag import get_rag


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_rag()  # warm-up: load the embedding model and open the DB once at startup
    yield


app = FastAPI(title=settings.PROJECT_NAME, version="2.1.0", docs_url="/docs", lifespan=lifespan)

# Only needed if a browser calls the API directly. Streamlit calls it server-side, so CORS is moot.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["Chat Engine"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin Operations"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "project": settings.PROJECT_NAME}
