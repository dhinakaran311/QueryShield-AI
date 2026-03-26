"""
backend/memory.py
Phase 9 — Conversational Memory
Maintains per-session query context for follow-up question support.
"""

import re
from typing import Optional, Dict
from datetime import datetime

# ─── In-memory store (keyed by session_id) ────────────────────────────────────
# Structure: { session_id: { "question": str, "sql": str, "timestamp": str } }
_memory_store: Dict[str, Dict] = {}


# ─── Required API Functions ───────────────────────────────────────────────────

def save_query_context(session_id: str, question: str, sql: str) -> None:
    """
    Save the latest query context for a given session.
    Stores session_id, user_question, generated_sql, and timestamp.
    """
    _memory_store[session_id] = {
        "session_id": session_id,
        "question":   question,
        "sql":        sql,
        "timestamp":  datetime.now().isoformat(),
    }


def get_last_query(session_id: str) -> Optional[Dict]:
    """
    Retrieve the last stored query context for a given session.
    Returns None if no context exists yet.
    """
    return _memory_store.get(session_id, None)


def merge_followup_query(previous_sql: str, followup_question: str) -> str:
    """
    Combine a previous SQL query with a follow-up question into a
    single LLM prompt string that can be sent for SQL refinement.

    Example:
        previous_sql      = "SELECT * FROM sales WHERE year=2025"
        followup_question = "Only January"
        → prompt string ready to be passed to the LLM
    """
    return (
        f"Previous SQL: {previous_sql}\n"
        f"Follow-up question: {followup_question}\n"
        f"Modify the previous SQL to satisfy the follow-up. "
        f"Return ONLY the modified SELECT query ending with a semicolon."
    )


# ─── Legacy helpers (backwards compatible with existing code) ─────────────────

def update_memory(last_nl: str, last_sql: str, session_id: str = "default") -> None:
    """Convenience wrapper — saves context using the default session."""
    save_query_context(session_id, last_nl, last_sql)


def get_memory(session_id: str = "default") -> Dict:
    """Convenience wrapper — retrieves context for the default session."""
    ctx = get_last_query(session_id)
    if ctx:
        return {"last_nl": ctx["question"], "last_sql": ctx["sql"]}
    return {"last_nl": None, "last_sql": None}


# ─── Follow-up detection ──────────────────────────────────────────────────────

def is_followup(question: str) -> bool:
    """
    Detect if a question is a follow-up to the previous context
    by looking for conversational cues.
    """
    if not isinstance(question, str) or not question.strip():
        return False

    lower_q = question.lower().strip()

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
        r"for\b",
    ]

    if any(re.search(cue, lower_q) for cue in follow_up_cues):
        return True

    word_count = len(lower_q.split())
    if word_count < 5 and "show" not in lower_q and "select" not in lower_q and "get" not in lower_q:
        return True

    return False
