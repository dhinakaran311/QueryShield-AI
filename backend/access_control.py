"""
backend/access_control.py
Phase 10 — Role-Based Access Control
Restricts table access and masks sensitive columns based on user role.
"""

import re
from typing import List, Dict, Optional

# ─── Role Permission Matrix ────────────────────────────────────────────────────
ROLE_PERMISSIONS = {
    "Admin": {
        "blocked_tables": [],          # Admin can query everything
        "blocked_columns": [],         # Admin sees all columns
    },
    "Analyst": {
        "blocked_tables": ["hr", "employees", "payroll", "secret_deals"],
        "blocked_columns": ["salary", "ssn", "profit", "customer_name"],
    },
    "Viewer": {
        "blocked_tables": ["hr", "employees", "payroll"], # Viewer is banned from HR
        "blocked_columns": ["email", "salary", "ssn", "profit", "customer_name", "customer_id"],
    },
}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_role_permissions(role: str) -> dict:
    """Return permission config for a role. Falls back to Viewer if unknown."""
    return ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["Viewer"])


def check_table_access(role: str, sql: str) -> dict:
    """
    Check whether the SQL query accesses any tables blocked for this role.
    Returns {"is_allowed": bool, "reason": str}
    """
    perms = get_role_permissions(role)
    blocked = perms["blocked_tables"]

    if not blocked:
        return {"is_allowed": True, "reason": ""}

    # Extract table names from SQL using simple regex (FROM and JOIN clauses)
    tables_in_query = re.findall(
        r"(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        sql,
        re.IGNORECASE,
    )

    for table in tables_in_query:
        if table.lower() in [b.lower() for b in blocked]:
            return {
                "is_allowed": False,
                "reason": f"Role '{role}' does not have access to table '{table}'.",
            }

    return {"is_allowed": True, "reason": ""}


def mask_columns(role: str, rows: List[Dict]) -> List[Dict]:
    """
    Replace values of blacklisted columns with '***' in result rows.
    """
    perms = get_role_permissions(role)
    blocked_cols = [c.lower() for c in perms["blocked_columns"]]

    if not blocked_cols or not rows:
        return rows

    masked_rows = []
    for row in rows:
        new_row = {}
        for key, val in row.items():
            if key.lower() in blocked_cols:
                new_row[key] = "***"
            else:
                new_row[key] = val
        masked_rows.append(new_row)

    return masked_rows
