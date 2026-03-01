"""
backend/sql_generator.py
Phase 4 — LLM SQL Generation using Google Gemini.

Responsibilities:
  - Build a schema-aware system prompt
  - Send NL query + schema to Gemini
  - Return clean SELECT-only SQL
  - Support conversational memory (last SQL for follow-ups)
"""

import os
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

from backend.schema_detector import get_full_schema, build_schema_prompt

load_dotenv()

# ─── Gemini init ──────────────────────────────────────────────────────────────
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL   = "gemini-2.0-flash"


# ─── System prompt template ───────────────────────────────────────────────────
SYSTEM_PROMPT_TEMPLATE = """You are an expert PostgreSQL query generator for the QueryShield AI system.

Your job is to convert a user's natural language question into a precise PostgreSQL SELECT query.

DATABASE SCHEMA:
{schema}

STRICT RULES — you MUST follow all of them:
1. Generate ONLY a single SELECT query.
2. NEVER use: DROP, DELETE, UPDATE, ALTER, INSERT, TRUNCATE, CREATE, EXEC, GRANT, REVOKE.
3. Return ONLY the raw SQL query — no explanation, no markdown, no code fences.
4. Use correct table and column names exactly as shown in the schema above.
5. Use JOINs when the question involves multiple tables.
6. Use aliases for readability (e.g. c for customers, o for orders).
7. Add ORDER BY, LIMIT, GROUP BY where appropriate.
8. If the question is ambiguous, make a sensible best-guess query.
9. Always end the query with a semicolon.
"""

FOLLOWUP_PROMPT_TEMPLATE = """You are an expert PostgreSQL query generator for QueryShield AI.

DATABASE SCHEMA:
{schema}

The user previously asked:
"{last_nl}"

Which generated this SQL:
{last_sql}

Now the user is refining their query:
"{followup_question}"

Modify the previous SQL to satisfy the follow-up.

RULES:
1. Return ONLY the modified SELECT query — no explanation.
2. Never use destructive keywords (DROP, DELETE, UPDATE, etc.).
3. End with a semicolon.
"""


# ─── SQL extraction helper ────────────────────────────────────────────────────
def _extract_sql(raw_text: str) -> str:
    """
    Strip markdown fences and extra whitespace from LLM response.
    Handles ```sql ... ``` and plain text responses.
    """
    # Remove markdown code fences
    text = re.sub(r"```(?:sql)?", "", raw_text, flags=re.IGNORECASE)
    text = text.replace("```", "").strip()

    # Take only the first statement (safety: ignore anything after ;)
    # Preserve the semicolon at end
    lines = [l for l in text.splitlines() if l.strip()]
    sql = " ".join(lines).strip()

    # Ensure semicolon at end
    if not sql.endswith(";"):
        sql += ";"

    return sql


# ─── Main generation function ─────────────────────────────────────────────────
def generate_sql(
    user_question: str,
    last_nl: str  = None,
    last_sql: str = None,
) -> dict:
    """
    Convert a natural language question to a PostgreSQL SELECT query.

    Args:
        user_question: The user's NL question
        last_nl:       Previous NL question (for follow-ups)
        last_sql:      Previous SQL (for follow-ups)

    Returns:
        dict with keys: sql, is_followup, schema_used
    """
    # Get current schema
    schema = get_full_schema()
    schema_text = build_schema_prompt(schema)

    # Decide: fresh query or follow-up?
    is_followup = bool(last_sql and last_nl)

    if is_followup:
        prompt = FOLLOWUP_PROMPT_TEMPLATE.format(
            schema            = schema_text,
            last_nl           = last_nl,
            last_sql          = last_sql,
            followup_question = user_question,
        )
    else:
        prompt = SYSTEM_PROMPT_TEMPLATE.format(schema=schema_text)
        prompt += f"\n\nUser question: {user_question}\nSQL:"

    # ── Call Gemini with retry/backoff for free-tier rate limits ──────────────
    import time

    last_error = None
    for attempt in range(3):            # max 3 attempts
        try:
            response = _client.models.generate_content(
                model    = MODEL,
                contents = prompt,
            )
            raw_sql = response.text.strip()
            break                       # success — exit retry loop
        except Exception as exc:
            last_error = exc
            err_str = str(exc)
            # Parse retryDelay from error message if present
            delay_match = re.search(r"'retryDelay':\s*'(\d+)s'", err_str)
            wait_secs   = int(delay_match.group(1)) + 2 if delay_match else (2 ** attempt) * 5
            if attempt < 2:
                time.sleep(wait_secs)
            else:
                raise last_error        # all retries exhausted

    # Clean the response
    clean_sql = _extract_sql(raw_sql)

    return {
        "sql":         clean_sql,
        "is_followup": is_followup,
        "schema_used": list(schema["tables"].keys()),
    }
