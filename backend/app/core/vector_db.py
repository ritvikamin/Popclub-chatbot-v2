import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from app.config import settings
from typing import List, Dict, Any

class VectorDBEngine:
    def __init__(self):
        # 1. Load the embedding model locally onto our CPU
        # This model turns text chunks into a list of 384 numbers representing meaning.
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        
        # 2. Initialize ChromaDB client with persistent disk storage
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        
        # 3. Create or fetch our specific POPclub data collection
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"} # Use Cosine Distance to measure similarity
        )

    def add_documents(self, chunks: List[str], filename: str):
        """
        Takes a list of text chunks, converts them to vector numbers,
        and saves them to ChromaDB along with metadata.
        """
        # Generate embeddings (the lists of numbers) for all text chunks
        embeddings = self.model.encode(chunks).tolist()
        
        # Create unique IDs for each chunk so ChromaDB can track them
        ids = [f"{filename}_{i}" for i in range(len(chunks))]
        
        # Metadata allows us to filter or attribute where the text came from later
        metadatas = [{"source": filename} for _ in range(len(chunks))]
        
        # Store everything securely on the disk
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )

    def search_similar_chunks(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Converts a user question into numbers, finds the top closest chunks,
        and returns them to be used as context.
        """
        # Convert user's question into the exact same vector space numbers
        query_embedding = self.model.encode([query]).tolist()[0]
        
        # Query the database for the closest vector matches
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit
        )
        
        # Format the output into a clean, readable list of dictionaries
        formatted_results = []
        if results and results["documents"]:
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "text": results["documents"][0][i],
                    "source": results["metadatas"][0][i]["source"],
                    "score": 1.0 - results["distances"][0][i] # Convert distance to a similarity score
                })
                
        return formatted_results