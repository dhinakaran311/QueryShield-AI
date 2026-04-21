import sys
sys.path.insert(0, '.')
from backend.database import engine, test_connection
from sqlalchemy import text

print('DB connected:', test_connection())

with engine.connect() as conn:
    res = conn.execute(text(
        "SELECT EXISTS ("
        "  SELECT FROM information_schema.tables "
        "  WHERE table_schema='public' AND table_name='uploaded_tables'"
        ")"
    ))
    exists = res.scalar()
    print('uploaded_tables exists:', exists)

    if not exists:
        print('>>> CREATING uploaded_tables...')
        conn.execute(text("""
            CREATE TABLE uploaded_tables (
                id SERIAL PRIMARY KEY,
                table_name TEXT UNIQUE NOT NULL,
                uploaded_by TEXT DEFAULT 'user',
                upload_time TIMESTAMP DEFAULT NOW()
            )
        """))
        conn.commit()
        print('>>> uploaded_tables created OK')
    else:
        rows = conn.execute(text(
            'SELECT table_name, uploaded_by FROM uploaded_tables ORDER BY upload_time DESC LIMIT 5'
        ))
        print('Existing uploads:', [dict(r._mapping) for r in rows])

    # Also list all public tables
    all_tables = conn.execute(text(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"
    ))
    print('All public tables:', [r[0] for r in all_tables])
