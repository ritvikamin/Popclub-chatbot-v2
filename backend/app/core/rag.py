import logging
from functools import lru_cache
from typing import Any, Dict, List

from google import genai
from google.genai import types

from app.config import settings
from app.core.vector_db import get_vector_db

logger = logging.getLogger(__name__)

REFUSAL = "I'm sorry, but I don't have that information in my knowledge base."

SYSTEM_INSTRUCTION = (
    "You are an expert customer support AI assistant for POPclub.\n"
    "Answer user questions using ONLY the provided Source Blocks.\n\n"
    "CRITICAL RULES:\n"
    "1. Stay strictly grounded in the Source Blocks. Do NOT use outside knowledge.\n"
    "2. The conversation history is only for understanding follow-up questions "
    "(e.g. what 'it' or 'that' refers to). It is NOT a source of facts.\n"
    f"3. If the answer is not fully contained in the Source Blocks, reply exactly with: '{REFUSAL}'\n"
    "4. Never invent facts, URLs, phone numbers, or details."
)

CONDENSE_INSTRUCTION = (
    "Rewrite the user's latest message as a standalone question that makes sense without the "
    "conversation, resolving words like 'it', 'that', 'the fee'. If it is already standalone, "
    "return it unchanged. Output ONLY the question."
)


class RAGOrchestrator:
    def __init__(self):
        self.db = get_vector_db()
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    # ---- helpers -------------------------------------------------------------------------
    @staticmethod
    def _format_history(history: List[Dict[str, str]]) -> str:
        recent = history[-settings.MAX_HISTORY_MESSAGES:]
        return "\n".join(f"{m['role'].upper()}: {m['content']}" for m in recent)

    def _generate(self, contents: str, system_instruction: str) -> str:
        response = self.client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.0),
        )
        return (response.text or "").strip()

    def _condense_query(self, query: str, history_text: str) -> str:
        """Turn a follow-up ('what about the fee?') into a standalone search query.

        Needed because the vector search only sees the text we give it - without this,
        'what about the fee?' has no meaning to the embedding model.
        """
        prompt = f"CONVERSATION:\n{history_text}\n\nLATEST MESSAGE: {query}"
        try:
            return self._generate(prompt, CONDENSE_INSTRUCTION) or query
        except Exception:
            logger.exception("Query condensing failed; falling back to the raw question")
            return query

    # ---- main entry ----------------------------------------------------------------------
    def generate_grounded_answer(
        self, user_query: str, history: List[Dict[str, str]] | None = None
    ) -> Dict[str, Any]:
        history = history or []
        history_text = self._format_history(history) if history else ""

        # 1. Make the question searchable on its own
        search_query = self._condense_query(user_query, history_text) if history_text else user_query

        # 2. Retrieve, then drop chunks that aren't actually relevant
        matches = self.db.search_similar_chunks(query=search_query, limit=settings.TOP_K)
        matches = [m for m in matches if m["score"] >= settings.MIN_RELEVANCE_SCORE]

        # 3. Nothing relevant -> refuse without spending an LLM call
        if not matches:
            return {"answer": REFUSAL, "citations": []}

        context = "".join(
            f"\n--- SOURCE BLOCK {i + 1} (File: {m['source']}) ---\n{m['text']}\n"
            for i, m in enumerate(matches)
        )
        prompt = f"CONTEXT:\n{context}\n"
        if history_text:
            prompt += f"\nCONVERSATION SO FAR:\n{history_text}\n"
        prompt += f"\nUSER QUESTION: {user_query}"

        # 4. Generate the grounded answer (errors propagate; the API layer turns them into a 502)
        answer = self._generate(prompt, SYSTEM_INSTRUCTION)
        return {"answer": answer or REFUSAL, "citations": matches}


@lru_cache(maxsize=1)
def get_rag() -> RAGOrchestrator:
    return RAGOrchestrator()
