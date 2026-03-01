"""
backend/schema_detector.py
Dynamically detects schema from PostgreSQL information_schema.

Phase 3 responsibilities:
  - Fetch all public table names
  - Fetch columns + types per table
  - Detect foreign key relationships
  - Build a schema context dict ready for LLM injection (Phase 4)
"""

from sqlalchemy import text
from backend.database import engine


# ─── 1. All public tables ─────────────────────────────────────────────────────

def get_all_tables() -> list[str]:
    """Return list of all table names in the public schema."""
    sql = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type  = 'BASE TABLE'
        ORDER BY table_name;
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
    return [row[0] for row in rows]


# ─── 2. Columns for a specific table ─────────────────────────────────────────

def get_table_columns(table_name: str) -> list[dict]:
    """
    Return column info for a given table.
    Each row: { column_name, data_type, is_nullable, column_default }
    """
    sql = """
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name   = :tname
        ORDER BY ordinal_position;
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql), {"tname": table_name}).fetchall()
    return [
        {
            "column_name":    row[0],
            "data_type":      row[1],
            "is_nullable":    row[2],
            "column_default": row[3],
        }
        for row in rows
    ]


# ─── 3. Foreign key relationships ────────────────────────────────────────────

def get_foreign_keys() -> list[dict]:
    """
    Return all FK relationships in the public schema.
    Each row: { table, column, references_table, references_column }
    """
    sql = """
        SELECT
            tc.table_name        AS "table",
            kcu.column_name      AS "column",
            ccu.table_name       AS references_table,
            ccu.column_name      AS references_column
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
           AND tc.table_schema    = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
           AND ccu.table_schema    = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema    = 'public'
        ORDER BY tc.table_name;
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
    return [
        {
            "table":             row[0],
            "column":            row[1],
            "references_table":  row[2],
            "references_column": row[3],
        }
        for row in rows
    ]


# ─── 4. Full schema context (for LLM injection) ───────────────────────────────

def get_full_schema() -> dict:
    """
    Build a complete schema context dict:
    {
        "tables": {
            "customers": [
                {"column_name": "id", "data_type": "integer", ...},
                ...
            ],
            ...
        },
        "foreign_keys": [
            {"table": "orders", "column": "customer_id", ...},
            ...
        ]
    }
    """
    tables = get_all_tables()
    schema = {}
    for table in tables:
        schema[table] = get_table_columns(table)

    foreign_keys = get_foreign_keys()

    return {
        "tables":       schema,
        "foreign_keys": foreign_keys,
    }


# ─── 5. LLM-ready prompt string ───────────────────────────────────────────────

def build_schema_prompt(schema: dict) -> str:
    """
    Convert the schema dict into a clean text block for LLM system prompts.

    Example output:
        Table: customers
          - id (integer)
          - name (text)
          ...
        Foreign Keys:
          - orders.customer_id → customers.id
    """
    lines = []

    for table_name, columns in schema["tables"].items():
        lines.append(f"Table: {table_name}")
        for col in columns:
            nullable = "" if col["is_nullable"] == "YES" else " NOT NULL"
            lines.append(f"  - {col['column_name']} ({col['data_type']}{nullable})")
        lines.append("")

    if schema["foreign_keys"]:
        lines.append("Foreign Key Relationships:")
        for fk in schema["foreign_keys"]:
            lines.append(
                f"  - {fk['table']}.{fk['column']} → "
                f"{fk['references_table']}.{fk['references_column']}"
            )

    return "\n".join(lines)
