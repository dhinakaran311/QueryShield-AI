"""
backend/memory.py
Phase 9 — Conversational Memory logic for tracking context and detecting follow-up cues.
"""

import re
from typing import Optional, Dict

# Global memory dictionary (in-memory storage for MVP)
memory_store: Dict[str, Optional[str]] = {
    "last_nl": None,
    "last_sql": None
}


def update_memory(last_nl: str, last_sql: str) -> None:
    """Store the latest successful question and generated SQL."""
    memory_store["last_nl"] = last_nl
    memory_store["last_sql"] = last_sql


def get_memory() -> Dict[str, Optional[str]]:
    """Retrieve the current memory state."""
    return memory_store


def is_followup(question: str) -> bool:
    """
    Intelligently detect if a question is a follow-up to the previous context.
    Looks for conversational cues vs completely new standalone questions.
    """
    if not isinstance(question, str) or not question.strip():
        return False
        
    lower_q = question.lower().strip()
    
    # Common follow-up prefix words/phrases
    follow_up_cues = [
        r"^only\b",
        r"^also\b",
        r"^filter by\b",
        r"^just\b",
        r"^but\b",
        r"^instead\b",
        r"^and\b",
        r"^what about\b",
        r"^how about\b",
        r"^exclude\b",
        r"^order by\b",
        r"^sort by\b",
        r"^group by\b",
        r"for\b" # Often used like "for 2025"
    ]
    
    # Check if the question starts with any cue or is very short (likely refining a previous query)
    if any(re.search(cue, lower_q) for cue in follow_up_cues):
        return True
        
    # If the text is very short (e.g., "India", "in 2024", "top 5"), it relies on context.
    # We consider < 5 words a high likelihood of being a follow-up refinement.
    word_count = len(lower_q.split())
    if word_count < 5 and "show" not in lower_q and "select" not in lower_q and "get" not in lower_q:
        return True
        
    return False
