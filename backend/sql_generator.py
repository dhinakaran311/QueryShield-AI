"""
backend/sql_generator.py
Phase 4 — LLM SQL Generation.

Supports two providers (switch via LLM_PROVIDER in .env):
  - "ollama"  → local Ollama (no API key, no rate limits)
  - "gemini"  → Google Gemini 2.0 Flash (cloud)
"""

import os
import re
import time
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

from backend.schema_detector import get_full_schema, build_schema_prompt

load_dotenv()

# ─── Config ───────────────────────────────────────────────────────────────────
LLM_PROVIDER    = os.getenv("LLM_PROVIDER", "ollama").lower()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "mistral:latest")


# ─── Prompt templates ─────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert PostgreSQL query generator.

Convert the user's natural language question into a precise PostgreSQL SELECT query.

DATABASE SCHEMA:
{schema}

STRICT RULES:
1. Generate ONLY a single SELECT query.
2. NEVER use: DROP, DELETE, UPDATE, ALTER, INSERT, TRUNCATE, CREATE, EXEC, GRANT, REVOKE.
3. Return ONLY the raw SQL query — no explanation, no markdown, no code fences.
4. Use correct table/column names exactly as shown in the schema.
5. Use JOINs when multiple tables are involved.
6. Add ORDER BY, LIMIT, GROUP BY where appropriate.
7. Always end with a semicolon.
"""

FOLLOWUP_PROMPT = """You are an expert PostgreSQL query generator.

DATABASE SCHEMA:
{schema}

Previous question: "{last_nl}"
Previous SQL: {last_sql}

User follow-up: "{followup_question}"

Modify the previous SQL to satisfy the follow-up.
Return ONLY the modified SELECT query ending with a semicolon.
"""


# ─── SQL cleaning ─────────────────────────────────────────────────────────────
def _clean_sql(raw: str) -> str:
    """Strip markdown fences, extra whitespace from LLM output."""
    text = re.sub(r"```(?:sql)?", "", raw, flags=re.IGNORECASE)
    text = text.replace("```", "").strip()
    lines = [l for l in text.splitlines() if l.strip()]
    sql = " ".join(lines).strip()
    if not sql.endswith(";"):
        sql += ";"
    return sql


# ─── Ollama call ──────────────────────────────────────────────────────────────
def _call_ollama(prompt: str) -> str:
    """
    Call local Ollama REST API.
    POST http://localhost:11434/api/generate
    """
    payload = json.dumps({
        "model":  OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_BASE_URL}/api/generate",
        data    = payload,
        headers = {"Content-Type": "application/json"},
        method  = "POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        body = json.loads(resp.read())
    return body.get("response", "").strip()


# ─── Gemini call ──────────────────────────────────────────────────────────────
def _call_gemini(prompt: str) -> str:
    """Call Google Gemini 2.0 Flash with retry/backoff."""
    from google import genai
    api_key = os.getenv("GEMINI_API_KEY", "")
    client  = genai.Client(api_key=api_key)
    model   = "gemini-2.0-flash"

    last_error = None
    for attempt in range(3):
        try:
            resp = client.models.generate_content(model=model, contents=prompt)
            return resp.text.strip()
        except Exception as exc:
            last_error = exc
            delay_match = re.search(r"'retryDelay':\s*'(\d+)s'", str(exc))
            wait = int(delay_match.group(1)) + 2 if delay_match else (2 ** attempt) * 5
            if attempt < 2:
                time.sleep(wait)
            else:
                raise last_error
    raise last_error


# ─── Main generate function ───────────────────────────────────────────────────
def generate_sql(
    user_question: str,
    last_nl:  str = None,
    last_sql: str = None,
) -> dict:
    """
    Convert NL question → PostgreSQL SELECT query.

    Picks LLM provider from LLM_PROVIDER env var:
      "ollama" → local (no rate limits)
      "gemini" → Gemini 2.0 Flash
    """
    schema      = get_full_schema()
    schema_text = build_schema_prompt(schema)
    is_followup = bool(last_sql and last_nl)

    if is_followup:
        prompt = FOLLOWUP_PROMPT.format(
            schema            = schema_text,
            last_nl           = last_nl,
            last_sql          = last_sql,
            followup_question = user_question,
        )
    else:
        prompt = SYSTEM_PROMPT.format(schema=schema_text)
        prompt += f"\n\nUser question: {user_question}\nSQL:"

    # Dispatch to provider
    if LLM_PROVIDER == "gemini":
        raw = _call_gemini(prompt)
    else:  # default: ollama
        raw = _call_ollama(prompt)

    return {
        "sql":         _clean_sql(raw),
        "is_followup": is_followup,
        "schema_used": list(schema["tables"].keys()),
        "provider":    LLM_PROVIDER,
        "model":       OLLAMA_MODEL if LLM_PROVIDER == "ollama" else "gemini-2.0-flash",
    }


CORRECTION_PROMPT = """The following SQL query failed with an error:

SQL: {original_sql}
Error: {error_message}

Fix the SQL query. Return ONLY the corrected SQL.
Corrected SQL:"""


def correct_sql(original_sql: str, error_message: str) -> str:
    prompt = CORRECTION_PROMPT.format(
        original_sql=original_sql,
        error_message=error_message,
    )
    if LLM_PROVIDER == "gemini":
        raw = _call_gemini(prompt)
    else:
        raw = _call_ollama(prompt)
    return _clean_sql(raw)
