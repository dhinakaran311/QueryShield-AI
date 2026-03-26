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
5. Use JOINs when multiple tables are involved. NEVER wrap table aliases in parentheses (e.g. use "JOIN table AS t", NOT "JOIN (table AS t)").
6. Do NOT hallucinate column names. For example, if a table's primary key is "id", do NOT refer to it as "order_id" or "customer_id" unless that exact name exists in the schema.
7. Add ORDER BY, LIMIT, GROUP BY where appropriate.
8. If joining a TEXT/VARCHAR column with an INTEGER column, use explicit casting (e.g., `table1.col::INTEGER = table2.col`).
9. Use exact table names provided. NEVER use dot-notation for table names (e.g., use `superstore`, NOT `superstore.sales_data`).
10. Always end with a semicolon.
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
    """Extract only the SQL statement, ignoring conversational text."""
    # Grab markdown block if it exists
    code_match = re.search(r"```(?:sql)?\s*(.*?)\s*```", raw, re.IGNORECASE | re.DOTALL)
    text = code_match.group(1) if code_match else raw
    
    # Extract from SELECT to the first semicolon
    upper_text = text.upper()
    select_idx = upper_text.find("SELECT ")
    
    if select_idx != -1:
        text = text[select_idx:]
        semi_idx = text.find(";")
        if semi_idx != -1:
            text = text[:semi_idx+1]
        else:
            text = text + ";"
    else:
        # Fallback if no SELECT found
        text = text.replace("```sql", "").replace("```", "").strip()
        if not text.endswith(";"):
            text += ";"
            
    # Flatten newlines
    lines = [l for l in text.splitlines() if l.strip()]
    return " ".join(lines).strip()


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
    context = [user_question, last_nl, last_sql]
    schema      = get_full_schema(context)
    schema_text = build_schema_prompt(schema)
    
    from backend.memory import is_followup as detect_followup
    is_followup = bool(last_sql and last_nl and detect_followup(user_question))

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


CORRECTION_PROMPT = """You are an expert PostgreSQL query fix tool.
The following SQL query failed with an error:

SQL: {original_sql}
Error: {error_message}

Fix the SQL query.
STRICT RULES:
1. Return ONLY the raw SQL query.
2. NO explanation, NO conversational text, NO markdown formatting.
3. Must start with SELECT and end with a semicolon.
4. Ensure valid PostgreSQL syntax. NEVER wrap table aliases in parentheses.
5. If the error is a type mismatch (e.g., 'operator does not exist: text = integer'), use explicit casting like `column::INTEGER`.
6. If the error is 'UndefinedTable', ensure you are using the EXACT table name from the schema. NEVER use dot-notation (like `schema.table`).
"""


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
