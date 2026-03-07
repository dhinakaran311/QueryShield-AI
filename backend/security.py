"""
backend/security.py
Security validation layer for LLM-generated SQL queries.
Phase 5: Performance-optimized security checks.
"""

import re
from typing import Dict, Optional

# --- Configuration ---
# Strict whitelist: only SELECT is allowed for the general query engine.
ALLOWED_COMMANDS = r"^\s*SELECT\b"

# Blacklist of dangerous keywords (even inside SELECT, some are risky in certain contexts)
# though LLM is restricted, we double-check here.
BLOCKED_KEYWORDS = [
    "DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", 
    "ALTER", "CREATE", "REPLACE", "GRANT", "REVOKE", 
    "EXEC", "EXECUTE", "SYSTEM", "COPY", "VACUUM"
]

# Regex patterns for common SQL injection and multi-statement attacks
# Compiled for performance (optimization)
INJECTION_PATTERNS = [
    re.compile(r";\s*(DROP|DELETE|UPDATE|INSERT|TRUNCATE|ALTER|CREATE)", re.IGNORECASE), # Stacked queries
    re.compile(r"(--|#)\s*", re.IGNORECASE),                                          # SQL comments
    re.compile(r"UNION\s+(ALL\s+)?SELECT", re.IGNORECASE),                            # UNION based injection
    re.compile(r"OR\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+['\"]?", re.IGNORECASE),          # Tautologies (OR 1=1)
    re.compile(r"sleep\s*\(", re.IGNORECASE),                                         # Time-based injection
    re.compile(r"pg_sleep\s*\(", re.IGNORECASE),                                      # Postgres specific sleep
    re.compile(r"load_file\s*\(", re.IGNORECASE),                                     # File system access
]

def validate_sql(sql: str) -> Dict:
    """
    Validates a SQL query for security and constraints.
    Returns:
        {
            "is_safe": bool,
            "reason": str (optional)
        }
    """
    if not sql or not sql.strip():
        return {"is_safe": False, "reason": "Empty query."}

    clean_sql = sql.strip().upper()

    # 1. Check for allowed command (must start with SELECT)
    if not re.match(ALLOWED_COMMANDS, clean_sql, re.IGNORECASE):
        return {
            "is_safe": False, 
            "reason": "Unauthorized command. Only 'SELECT' queries are allowed."
        }

    # 2. Check for blocked keywords
    # Using a fast scan for keywords
    for kw in BLOCKED_KEYWORDS:
        if re.search(rf"\b{kw}\b", clean_sql):
            return {
                "is_safe": False,
                "reason": f"Security risk: Blocked keyword '{kw}' detected."
            }

    # 3. Check for multi-statement execution (semicolons outside strings)
    # Basic check: if semicolon exists and isn't the last character, it's suspicious
    if ";" in sql:
        parts = sql.split(";")
        # Allow a single semicolon at the very end
        if len([p for p in parts if p.strip()]) > 1:
            return {
                "is_safe": False, 
                "reason": "Multiple statements (stacked queries) are blocked."
            }

    # 4. Check against injection patterns (Optimized Regex)
    for pattern in INJECTION_PATTERNS:
        if pattern.search(sql):
            return {
                "is_safe": False,
                "reason": "Security risk: Malicious SQL pattern detected."
            }

    return {"is_safe": True}
