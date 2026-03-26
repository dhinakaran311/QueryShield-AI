"""
backend/security.py
Phase 5 — Security Layer
Validates SQL queries to block injection attacks and unsafe operations.
"""

import re

# ─── Blocked DDL / DML keywords ──────────────────────────────────────────────
BLOCKED_KEYWORDS = [
    "DROP", "DELETE", "UPDATE", "ALTER", "INSERT",
    "TRUNCATE", "EXEC", "EXECUTE", "GRANT", "REVOKE",
    "CREATE", "REPLACE",
]

# ─── Injection patterns ───────────────────────────────────────────────────────
INJECTION_PATTERNS = [
    r";\s*(DROP|DELETE|UPDATE|INSERT|ALTER)",   # stacked queries
    r"(--|#)\s",                                  # comment injection
    r"\bOR\s+1\s*=\s*1\b",                       # tautology
    r"\bUNION\s+SELECT\b",                        # UNION injection
    r"'\s*(OR|AND)\s+'",                          # quote injection
    r"xp_cmdshell",                               # MSSQL shell
    r"SLEEP\s*\(",                                # time-based injection
    r"BENCHMARK\s*\(",                            # benchmark injection
]


def validate_sql(sql: str) -> dict:
    """
    Validate a SQL query for safety.

    Returns:
        {"is_safe": True}                   — if the query passes all checks
        {"is_safe": False, "reason": str}   — if the query is blocked
    """
    if not sql or not sql.strip():
        return {"is_safe": False, "reason": "Empty query."}

    upper = sql.upper().strip()

    # Must be a SELECT statement
    if not upper.lstrip().startswith("SELECT"):
        return {"is_safe": False, "reason": "Only SELECT queries are allowed."}

    # Block banned keywords
    for kw in BLOCKED_KEYWORDS:
        # Use word-boundary regex to avoid false positives
        if re.search(rf"\b{kw}\b", upper):
            return {"is_safe": False, "reason": f"Blocked keyword detected: {kw}"}

    # Block injection patterns
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, sql, re.IGNORECASE):
            return {"is_safe": False, "reason": f"Potential SQL injection pattern detected."}

    return {"is_safe": True}
