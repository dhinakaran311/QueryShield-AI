"""
backend/optimizer.py
Phase 8 — Query Cost Optimization using EXPLAIN ANALYZE.
"""

import re
import os
from backend.database import engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

COST_THRESHOLDS = {
    "low":    1000,
    "medium": 10000,
    "high":   50000,
}

COST_LABELS = {
    "low":    "🟢 Low",
    "medium": "🟡 Medium",
    "high":   "🔴 High",
}


def get_query_cost(sql: str) -> float:
    explain_sql = f"EXPLAIN ANALYZE {sql.rstrip(';')}"
    with engine.connect() as conn:
        rows = conn.execute(text(explain_sql)).fetchall()
    first_line = rows[0][0] if rows else ""
    match = re.search(r"cost=[\d.]+\.\.([\d.]+)", first_line)
    return float(match.group(1)) if match else 0.0


def classify_cost(cost: float) -> str:
    if cost <= COST_THRESHOLDS["low"]:
        return "low"
    elif cost <= COST_THRESHOLDS["medium"]:
        return "medium"
    return "high"


def _add_limit(sql: str, limit: int = 100) -> str:
    upper = sql.upper()
    if re.search(r"\bSELECT\s+\*", upper) and "LIMIT" not in upper:
        return sql.rstrip(";") + f" LIMIT {limit};"
    return sql


OPTIMIZE_PROMPT = """The following PostgreSQL query has a high execution cost:

SQL: {sql}

Rewrite it to be more efficient. Use indexes, avoid SELECT *, add LIMIT where safe.
Return ONLY the optimized SQL query ending with a semicolon."""


def optimize_sql(sql: str) -> dict:
    from backend.sql_generator import LLM_PROVIDER, _call_gemini, _call_ollama, _clean_sql

    sql = _add_limit(sql)

    try:
        cost  = get_query_cost(sql)
        level = classify_cost(cost)
    except Exception:
        cost  = 0.0
        level = "low"

    optimized = sql
    if level == "high":
        prompt = OPTIMIZE_PROMPT.format(sql=sql)
        raw    = _call_gemini(prompt) if LLM_PROVIDER == "gemini" else _call_ollama(prompt)
        optimized = _clean_sql(raw)

    return {
        "sql":         optimized,
        "query_cost":  cost,
        "cost_level":  level,
        "cost_label":  COST_LABELS[level],
        "was_optimized": level == "high",
    }
