import logging
import re
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

# Words that usually mean "this message refers to something said earlier".
FOLLOW_UP_MARKERS = {
    "it", "its", "that", "this", "those", "these", "they", "them", "their", "he", "she", "his",
    "her", "same", "also", "else", "more", "another", "previous", "above", "earlier",
}
FOLLOW_UP_PHRASES = ("what about", "how about", "and ", "but ")

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

    @staticmethod
    def _is_refusal(answer: str) -> bool:
        """True if the model replied with the 'I don't have that information' refusal."""
        normalised = answer.strip().lower().replace("\u2019", "'")  # curly apostrophe -> straight
        return normalised.startswith("i'm sorry, but i don't have that information")

    @staticmethod
    def _looks_like_followup(query: str) -> bool:
        """Cheap rule-of-thumb (no LLM): does this message depend on earlier conversation?"""
        q = query.lower().strip()
        words = re.findall(r"[a-z']+", q)
        return (
            len(words) <= 2                       # "fees?", "why?"
            or q.startswith(FOLLOW_UP_PHRASES)    # "what about the fee?"
            or any(w in FOLLOW_UP_MARKERS for w in words)  # "how long is it valid?"
        )

    def _retrieve(self, query: str) -> List[Dict[str, Any]]:
        """Top-k similar chunks, keeping only those above the relevance cutoff."""
        matches = self.db.search_similar_chunks(query=query, limit=settings.TOP_K)
        kept = [m for m in matches if m["score"] >= settings.MIN_RELEVANCE_SCORE]
        best = f"{max(m['score'] for m in matches):.2f}" if matches else "n/a"
        logger.info("SEARCH %r -> best score %s, %d chunk(s) kept", query, best, len(kept))
        return kept

    def _generate(self, contents: str, system_instruction: str) -> str:
        kind = "rewrite" if system_instruction == CONDENSE_INSTRUCTION else "answer"
        logger.info("GEMINI CALL (%s)", kind)
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
            rewritten = self._generate(prompt, CONDENSE_INSTRUCTION) or query
            logger.info("REWRITE %r -> %r", query, rewritten)
            return rewritten
        except Exception:
            logger.exception("Query condensing failed; falling back to the raw question")
            return query

    # ---- main entry ----------------------------------------------------------------------
    def generate_grounded_answer(
        self, user_query: str, history: List[Dict[str, str]] | None = None
    ) -> Dict[str, Any]:
        history = history or []
        # The UI's welcome message is an assistant turn, so "history is non-empty" is not enough:
        # only count it as a conversation once the user has actually said something before.
        has_prior_user_turn = any(m["role"] == "user" for m in history)
        history_text = self._format_history(history) if has_prior_user_turn else ""

        # 1. Retrieve. Rewrite the question into a standalone one only when it is needed:
        #    (a) it LOOKS like a follow-up (cheap heuristic) -> rewrite first, then search; or
        #    (b) the raw question found nothing relevant -> rewrite and search once more.
        search_query = user_query
        condensed = False
        if has_prior_user_turn and self._looks_like_followup(user_query):
            search_query = self._condense_query(user_query, history_text)
            condensed = True

        matches = self._retrieve(search_query)

        if not matches and has_prior_user_turn and not condensed:
            rewritten = self._condense_query(user_query, history_text)
            if rewritten != user_query:
                matches = self._retrieve(rewritten)

        # 2. Nothing relevant -> refuse without spending an LLM call
        if not matches:
            logger.info("NO RELEVANT CHUNKS -> refusing without an answer call")
            return {"answer": REFUSAL, "citations": []}

        context = "".join(
            f"\n--- SOURCE BLOCK {i + 1} (File: {m['source']}) ---\n{m['text']}\n"
            for i, m in enumerate(matches)
        )
        prompt = f"CONTEXT:\n{context}\n"
        if history_text:
            prompt += f"\nCONVERSATION SO FAR:\n{history_text}\n"
        prompt += f"\nUSER QUESTION: {user_query}"

        # 3. Generate the grounded answer (errors propagate; the API layer turns them into a 502)
        answer = self._generate(prompt, SYSTEM_INSTRUCTION)

        # If the model itself says "I don't have that information", showing sources beside it would
        # look like evidence for an answer that doesn't exist, so return no citations.
        if not answer or self._is_refusal(answer):
            return {"answer": answer or REFUSAL, "citations": []}
        return {"answer": answer, "citations": matches}


@lru_cache(maxsize=1)
def get_rag() -> RAGOrchestrator:
    return RAGOrchestrator()
