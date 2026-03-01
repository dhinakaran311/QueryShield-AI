"""
backend/csv_uploader.py
Handles CSV file ingestion:
  - Reads CSV with Pandas
  - Infers column types
  - Auto-generates CREATE TABLE SQL
  - Bulk inserts data
  - Records metadata in uploaded_tables
"""

import re
import pandas as pd
from sqlalchemy import text
from backend.database import engine


# ─── Pandas dtype → PostgreSQL type mapping ───────────────────────────────────
DTYPE_MAP = {
    "int64":          "INTEGER",
    "int32":          "INTEGER",
    "float64":        "NUMERIC",
    "float32":        "NUMERIC",
    "bool":           "BOOLEAN",
    "object":         "TEXT",
    "string":         "TEXT",
    "datetime64[ns]": "TIMESTAMP",
    "date":           "DATE",
}


def _sanitize_name(name: str) -> str:
    """Convert column/table name to a safe PostgreSQL identifier."""
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9_]", "_", name)  # replace special chars with _
    name = re.sub(r"_+", "_", name)           # collapse multiple underscores
    name = name.strip("_")
    if name[0].isdigit():
        name = "col_" + name                  # prefix if starts with digit
    return name


def _infer_pg_type(series: pd.Series) -> str:
    """Return the PostgreSQL type string for a pandas Series."""
    dtype_str = str(series.dtype)
    return DTYPE_MAP.get(dtype_str, "TEXT")


def _build_create_table_sql(table_name: str, df: pd.DataFrame) -> str:
    """Generate CREATE TABLE SQL from a DataFrame."""
    columns_sql = []
    for col in df.columns:
        safe_col = _sanitize_name(col)
        pg_type  = _infer_pg_type(df[col])
        columns_sql.append(f'    "{safe_col}" {pg_type}')

    cols_joined = ",\n".join(columns_sql)
    return (
        f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n'
        f'    id SERIAL PRIMARY KEY,\n'
        f'{cols_joined}\n'
        f');'
    )


def upload_csv(
    file_bytes: bytes,
    table_name: str,
    uploaded_by: str = "user"
) -> dict:
    """
    Main entry point: parse CSV, create table, insert data, record metadata.

    Returns:
        dict with keys: table_name, rows_inserted, columns, schema
    """
    # 1. Sanitize table name
    table_name = _sanitize_name(table_name)

    # 2. Read CSV
    import io
    df = pd.read_csv(io.BytesIO(file_bytes))
    if df.empty:
        raise ValueError("Uploaded CSV is empty.")

    # 3. Sanitize column names
    df.columns = [_sanitize_name(c) for c in df.columns]

    # 4. Build schema info for response
    schema = {col: _infer_pg_type(df[col]) for col in df.columns}

    # 5. Create table + insert in a transaction
    create_sql = _build_create_table_sql(table_name, df)

    with engine.begin() as conn:
        # Create table
        conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}"'))
        conn.execute(text(create_sql))

        # Bulk insert using to_sql (fast path)
        df.to_sql(
            name        = table_name,
            con         = conn,
            if_exists   = "append",
            index       = False,
            method      = "multi",
            chunksize   = 500,
        )

        # Record metadata
        conn.execute(
            text(
                "INSERT INTO uploaded_tables (table_name, uploaded_by) "
                "VALUES (:tn, :ub) "
                "ON CONFLICT DO NOTHING"
            ),
            {"tn": table_name, "ub": uploaded_by},
        )

    return {
        "table_name":    table_name,
        "rows_inserted": len(df),
        "columns":       list(df.columns),
        "schema":        schema,
    }


def get_uploaded_tables() -> list[dict]:
    """Return all rows from uploaded_tables."""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, table_name, uploaded_by, upload_time "
                 "FROM uploaded_tables ORDER BY upload_time DESC")
        )
        return [dict(row._mapping) for row in result]
