"""
backend/database.py
Database connection and helper utilities for QueryShield AI.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

from urllib.parse import quote_plus

# ─── Connection URL ───────────────────────────────────────────────────────────
_password = quote_plus(os.getenv("DB_PASSWORD", ""))   # encodes '@' → '%40'

DB_URL = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{_password}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ─── Dependency (FastAPI) ─────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── Raw query helper ─────────────────────────────────────────────────────────
def execute_query(sql: str, params: dict = None):
    """
    Execute a raw SQL query and return rows as list of dicts.
    """
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        if result.returns_rows:
            columns = list(result.keys())
            rows    = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        conn.commit()
        return []


def test_connection() -> bool:
    """Check if DB is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
