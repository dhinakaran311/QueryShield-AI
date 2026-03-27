import re

# Security validation layer for LLM-generated SQL queries

# Common SQL injection patterns (Optimized regex)
INJECTION_PATTERNS = [
    re.compile(r"--", re.IGNORECASE),                # SQL comments
    re.compile(r"/\*", re.IGNORECASE),               # Multi-line comments
    re.compile(r";", re.IGNORECASE),                 # Multiple statements (stacking)
    re.compile(r"\b(DROP|TRUNCATE|DELETE|INSERT|UPDATE|ALTER|CREATE|EXEC|UNION)\b", re.IGNORECASE), # Dangerous keywords
    re.compile(r"XP_", re.IGNORECASE),               # Extended stored procedures
    re.compile(r"UTL_HTTP", re.IGNORECASE),          # Oracle network access
    re.compile(r"DBMS_JAVA", re.IGNORECASE),         # Oracle shell access
    re.compile(r"OPENROWSET", re.IGNORECASE)         # File system access
]

def validate_sql(sql: str) -> dict:
    """
    Validates SQL query for potential injection attacks.
    Returns: {"is_safe": bool, "reason": str (optional)}
    """
    upper_sql = sql.upper()
    
    for pattern in INJECTION_PATTERNS:
        if pattern.search(upper_sql):
            return {
                "is_safe": False,
                "reason": "Security risk: Malicious SQL pattern detected."
            }
            
    return {"is_safe": True}
