from functools import lru_cache
from typing import Any, Dict, List

import chromadb
from sentence_transformers import SentenceTransformer

from app.config import settings


class VectorDBEngine:
    def __init__(self):
        # Local embedding model: text -> 384 numbers that represent meaning.
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)

        # Persistent on-disk ChromaDB (survives restarts).
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)

        # Cosine distance: compares the *direction* of vectors, ignoring length.
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(self, chunks: List[str], filename: str) -> None:
        """Index a file's chunks. Re-uploading the same filename REPLACES the old version."""
        embeddings = self.model.encode(chunks).tolist()
        ids = [f"{filename}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename} for _ in chunks]

        # Delete the file's old chunks first. Chroma's add() silently ignores existing ids,
        # and a shorter new version would otherwise leave stale chunks behind.
        self.collection.delete(where={"source": filename})
        self.collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)

    def search_similar_chunks(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Embed the question and return the closest chunks with similarity scores (0-1)."""
        total = self.collection.count()
        if total == 0:
            return []

        query_embedding = self.model.encode([query]).tolist()[0]
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(limit, total),
        )

        formatted = []
        for text, meta, dist in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        ):
            # Chroma returns cosine *distance* (0 = identical). similarity = 1 - distance.
            formatted.append({"text": text, "source": meta["source"], "score": 1.0 - dist})
        return formatted

    def count(self) -> int:
        return self.collection.count()

    def sources(self) -> List[str]:
        metas = self.collection.get(include=["metadatas"])["metadatas"] or []
        return sorted({m["source"] for m in metas})


@lru_cache(maxsize=1)
def get_vector_db() -> VectorDBEngine:
    """One shared instance per process, so the embedding model is loaded only once."""
    return VectorDBEngine()
