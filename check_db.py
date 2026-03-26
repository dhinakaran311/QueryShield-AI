from backend.database import engine
from sqlalchemy import text

print("--- TABLES AND COLUMNS ---")
with engine.connect() as conn:
    tables = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")).fetchall()
    for t in tables:
        tname = t[0]
        cols = conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='{tname}'")).fetchall()
        print(f"[{tname}]: {[c[0] for c in cols]}")
