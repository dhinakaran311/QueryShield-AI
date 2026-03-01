-- =============================================================
-- QueryShield AI — Full Setup Runner
-- Run as: psql -U postgres -f db/setup.sql
-- =============================================================

-- Step 1: Create the database (run this outside psql or as a superuser)
-- CREATE DATABASE queryshield_db;

-- Step 2: Connect to queryshield_db then run schema + seed
\c queryshield_db

\echo '>>> Running schema.sql ...'
\i db/schema.sql

\echo '>>> Running seed.sql ...'
\i db/seed.sql

\echo '>>> Setup complete! Verifying tables...'
\dt

\echo '>>> uploaded_tables contents:'
SELECT * FROM uploaded_tables;

\echo '>>> Index list:'
\di idx_*
