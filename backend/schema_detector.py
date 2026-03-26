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
        
        # Also fetch a few sample rows to help the LLM understand the data
        sample_sql = f'SELECT * FROM "{table_name}" LIMIT 3'
        try:
            sample_rows = conn.execute(text(sample_sql)).fetchall()
            samples = [str(dict(r._mapping)) for r in sample_rows]
        except:
            samples = []

    return [
        {
            "column_name":    row[0],
            "data_type":      row[1],
            "is_nullable":    row[2],
            "column_default": row[3],
        }
        for row in rows
    ], samples


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
import re

def get_full_schema(context_strings: list[str] = None) -> dict:
    """
    Build a complete schema context dict.
    Filters tables matching any word in context_strings to reduce LLM confusion.
    """
    tables = get_all_tables()
    
    if context_strings and context_strings[0]:
        current_q = context_strings[0].lower()
        current_words = set(re.findall(r'\b\w+\b', current_q))
        
        # 1. Check if the current question explicitly mentions a table
        direct_matches = [t for t in tables if t.lower() in current_words]
        if direct_matches:
            tables = direct_matches
        else:
            # 2. Fall back to wider context (history) if no direct match in current Q
            blob = " ".join([s for s in context_strings if s]).lower()
            query_words = set(re.findall(r'\b\w+\b', blob))
            matched_tables = [
                t for t in tables 
                if t.lower() in query_words or any(t.lower() in w for w in query_words)
            ]
            if matched_tables:
                tables = matched_tables

    schema = {}
    samples_map = {}
    for table in tables:
        cols, samples = get_table_columns(table)
        schema[table] = cols
        samples_map[table] = samples

    foreign_keys = get_foreign_keys()
    
    # Filter FKs to only include relationships between matched tables
    if context_strings and tables:
        foreign_keys = [
            fk for fk in foreign_keys 
            if fk["table"] in tables and fk["references_table"] in tables
        ]

    return {
        "tables":       schema,
        "samples":      samples_map,
        "foreign_keys": foreign_keys,
    }


# ─── 5. LLM-ready prompt string ───────────────────────────────────────────────

def build_schema_prompt(schema: dict) -> str:
    """
    Convert the schema dict into a clean text block for LLM system prompts.
    Includes sample rows to help LLM understand the data content.
    """
    lines = []

    for table_name, columns in schema["tables"].items():
        lines.append(f"Table: {table_name}")
        for col in columns:
            nullable = "" if col["is_nullable"] == "YES" else " NOT NULL"
            lines.append(f"  - {col['column_name']} ({col['data_type']}{nullable})")
        
        # Add sample rows for this table
        samples = schema.get("samples", {}).get(table_name, [])
        if samples:
            lines.append("  Sample rows:")
            for s in samples:
                lines.append(f"    {s}")
        lines.append("")

    if schema["foreign_keys"]:
        lines.append("Foreign Key Relationships:")
        for fk in schema["foreign_keys"]:
            lines.append(
                f"  - {fk['table']}.{fk['column']} → "
                f"{fk['references_table']}.{fk['references_column']}"
            )

    return "\n".join(lines)
