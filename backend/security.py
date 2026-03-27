import re

# Security validation layer for LLM-generated SQL queries

# Common SQL injection patterns
INJECTION_PATTERNS = [
    # Stacked queries: semicolon followed by more non-whitespace content
    # A trailing semicolon at end of query is VALID — only block mid-statement ones
    (re.compile(r";\s*\S", re.IGNORECASE), "Stacked query detected (multiple statements)"),

    # SQL comments
    (re.compile(r"--", re.IGNORECASE), "SQL comment detected"),
    (re.compile(r"/\*", re.IGNORECASE), "Multi-line comment detected"),

    # Dangerous keywords (destructive / privilege-escalating operations)
    (re.compile(r"\b(DROP|TRUNCATE|DELETE|INSERT|UPDATE|ALTER|CREATE|EXEC|GRANT|REVOKE|UNION)\b", re.IGNORECASE),
     "Dangerous SQL keyword detected"),

    # Platform-specific attack vectors
    (re.compile(r"\bXP_", re.IGNORECASE), "Extended stored procedure detected"),
    (re.compile(r"\bUTL_HTTP\b", re.IGNORECASE), "Oracle network access detected"),
    (re.compile(r"\bDBMS_JAVA\b", re.IGNORECASE), "Oracle shell access detected"),
    (re.compile(r"\bOPENROWSET\b", re.IGNORECASE), "File system access detected"),
]


def validate_sql(sql: str) -> dict:
    """
    Validates SQL query for potential injection attacks.
    Returns: {"is_safe": bool, "reason": str (optional)}

    Rules:
    - A single trailing semicolon is ALLOWED (normal SQL syntax)
    - A semicolon followed by more content = stacked query = BLOCKED
    - Dangerous DDL/DML keywords are BLOCKED
    - SQL comments are BLOCKED
    """
    stripped = sql.strip()

    for pattern, reason in INJECTION_PATTERNS:
        if pattern.search(stripped):
            return {
                "is_safe": False,
                "reason": f"Security risk: {reason}.",
            }

    return {"is_safe": True}
