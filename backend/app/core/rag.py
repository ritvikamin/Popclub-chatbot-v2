from google import genai
from google.genai import types
from app.config import settings
from app.core.vector_db import VectorDBEngine
from typing import Dict, Any, List

class RAGOrchestrator:
    def __init__(self):
        # 1. Connect to our vector database engine
        self.db = VectorDBEngine()
        
        # 2. Initialize the official Gemini Client using our API key
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def generate_grounded_answer(self, user_query: str) -> Dict[str, Any]:
        """
        Orchestrates the entire RAG pipeline: retrieves text blocks,
        builds a guarded prompt, and gets a factual answer from Gemini.
        """
        # Step 1: Search ChromaDB for the top 3 most relevant text chunks
        matched_chunks = self.db.search_similar_chunks(query=user_query, limit=3)
        
        # Step 2: Combine the retrieved chunks into a single block of text context
        context_str = ""
        citations = []
        
        for i, chunk in enumerate(matched_chunks):
            context_str += f"\n--- SOURCE BLOCK {i+1} (File: {chunk['source']}) ---\n{chunk['text']}\n"
            citations.append({
                "source": chunk["source"],
                "text": chunk["text"],
                "score": chunk["score"]
            })

        # Step 3: Define the strict prompt template (The Anti-Hallucination Guardrail)
        system_instruction = (
            "You are an expert customer support AI assistant for POPclub.\n"
            "Your core mission is to answer user questions using ONLY the provided Source Blocks below.\n\n"
            "CRITICAL RULES:\n"
            "1. Remain strictly grounded in the provided context. Do NOT use outside knowledge.\n"
            "2. If the answer cannot be found completely in the Source Blocks, reply exactly with:\n"
            "   'I'm sorry, but I don't have that information in my knowledge base.'\n"
            "3. Do not make up facts, URLs, phone numbers, or details under any circumstances."
        )

        user_content = f"CONTEXT:\n{context_str}\n\nUSER QUESTION: {user_query}"

        # Step 4: Call Gemini 2.5 Flash
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_content,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.0,  # Set temperature to 0 for maximum determinism/factual consistency
                )
            )
            
            return {
                "answer": response.text,
                "citations": citations
            }
            
        except Exception as e:
            return {
                "answer": "An operational error occurred while connecting to the AI system.",
                "citations": []
            }