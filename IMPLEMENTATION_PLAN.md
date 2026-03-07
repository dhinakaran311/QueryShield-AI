# QueryShield AI — Phase-wise Implementation Plan

> **Project:** QueryShield AI – Secure Conversational Text-to-SQL with Dynamic Data Upload  
> **Stack:** Python · FastAPI · PostgreSQL · Pandas · Streamlit · LLM (OpenAI/Gemini)  
> **Last Updated:** 2026-03-01

---

## 📁 Final Project Folder Structure

```
QueryShield AI/
│
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── database.py              # DB connection & helpers
│   ├── schema_detector.py       # Dynamic schema fetcher
│   ├── sql_generator.py         # LLM integration & prompt builder
│   ├── security.py              # Query validation & injection blocker
│   ├── optimizer.py             # EXPLAIN ANALYZE cost checker
│   ├── memory.py                # Conversational memory store
│   ├── access_control.py        # Role-based access
│   └── csv_uploader.py          # CSV ingestion & table creator
│
├── frontend/
│   └── app.py                   # Streamlit UI
│
├── db/
│   ├── schema.sql               # Base DDL (demo schema + metadata table)
│   ├── seed.sql                 # Demo INSERT data
│   └── setup.sql                # Combined runner
│
├── tests/
│   ├── test_security.py
│   ├── test_sql_gen.py
│   ├── test_csv_upload.py
│   └── test_optimizer.py
│
├── requirements.txt
├── .env                         # DB credentials, API keys
└── IMPLEMENTATION_PLAN.md       # This file
```

---

## 🔹 PHASE 1 — Core Database Setup

**Goal:** Prepare the system database and metadata tracking.

### Tasks

| # | Task | File/Command |
|---|------|-------------|
| 1 | Install PostgreSQL (v15+) | System install |
| 2 | Create `queryshield_db` database | `psql` |
| 3 | Create `uploaded_tables` metadata table | `db/schema.sql` |
| 4 | Add demo schema: `customers`, `products`, `orders`, `order_items` | `db/schema.sql` |
| 5 | Add indexes on all foreign keys | `db/schema.sql` |
| 6 | Seed demo data | `db/seed.sql` |

### Schema DDL

```sql
-- Metadata tracking
CREATE TABLE uploaded_tables (
    id          SERIAL PRIMARY KEY,
    table_name  TEXT,
    uploaded_by TEXT,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Demo tables
CREATE TABLE customers (
    id      SERIAL PRIMARY KEY,
    name    TEXT NOT NULL,
    email   TEXT UNIQUE,
    city    TEXT,
    country TEXT
);

CREATE TABLE products (
    id       SERIAL PRIMARY KEY,
    name     TEXT NOT NULL,
    category TEXT,
    price    NUMERIC(10,2)
);

CREATE TABLE orders (
    id          SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date  DATE DEFAULT CURRENT_DATE,
    status      TEXT DEFAULT 'pending'
);

CREATE TABLE order_items (
    id         SERIAL PRIMARY KEY,
    order_id   INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity   INTEGER,
    unit_price NUMERIC(10,2)
);

-- Indexes on foreign keys
CREATE INDEX idx_orders_customer_id      ON orders(customer_id);
CREATE INDEX idx_order_items_order_id    ON order_items(order_id);
CREATE INDEX idx_order_items_product_id  ON order_items(product_id);
```

### Phase 1 Test

```sql
SELECT * FROM uploaded_tables;  -- Expected: empty table
\dt                              -- Expected: 5 tables listed
\di                              -- Expected: 3 FK indexes listed
```

---

## 🔹 PHASE 2 — CSV Upload System

**Goal:** Allow users to upload CSV files and auto-create tables dynamically.

### Backend Tasks (`backend/csv_uploader.py` + `backend/main.py`)

| # | Task |
|---|------|
| 1 | Create `POST /upload-csv` FastAPI endpoint |
| 2 | Accept multipart file + `table_name` form field |
| 3 | Use Pandas to read CSV and infer column types |
| 4 | Map Pandas dtypes → PostgreSQL types |
| 5 | Auto-generate and execute `CREATE TABLE` |
| 6 | Bulk insert rows via `COPY` or `executemany` |
| 7 | Insert row into `uploaded_tables` metadata table |

### Type Mapping Logic

```python
DTYPE_MAP = {
    "int64":   "INTEGER",
    "float64": "NUMERIC",
    "bool":    "BOOLEAN",
    "object":  "TEXT",
    "datetime64[ns]": "TIMESTAMP",
}
```

### Frontend Tasks (`frontend/app.py`)

```
- st.file_uploader("Upload CSV")
- st.text_input("Table Name")
- st.button("Upload")
- Upload status message (success / error)
- Schema preview: st.dataframe(df.head())
```

### CSV Upload Flow

```
User → Upload CSV → Streamlit UI
     → POST /upload-csv → FastAPI
     → Pandas (read + infer types)
     → PostgreSQL (CREATE TABLE + INSERT)
     → uploaded_tables (metadata record)
     → Success message + schema preview
```

### Phase 2 Tests

| Test | Action | Expected |
|------|--------|----------|
| Upload | Upload `sales_data.csv` | Table created, data inserted, success message |
| Query | `Show all data from sales_data` | Correct SELECT, data displayed |
| Aggregation | `Show total revenue from sales_data` | `SUM(revenue)` query, correct result |

---

## 🔹 PHASE 3 — Schema Detection & Injection

**Goal:** Auto-detect schema for both demo and uploaded tables.

### Tasks (`backend/schema_detector.py`)

| # | Task |
|---|------|
| 1 | Fetch all public table names from `information_schema` |
| 2 | Fetch column names + data types per table |
| 3 | Detect foreign key relationships |
| 4 | Build a structured schema dict for LLM injection |

### Key Queries

```sql
-- All tables
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';

-- Columns per table
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'sales_data';

-- Foreign keys
SELECT
    tc.table_name, kcu.column_name,
    ccu.table_name AS foreign_table,
    ccu.column_name AS foreign_column
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';
```

### Phase 3 Tests

| Prompt | Expected |
|--------|----------|
| `What tables are available?` | Lists all demo + uploaded tables |
| `Show columns in sales_data` | Returns correct schema |

---

## 🔹 PHASE 4 — LLM SQL Generation

**Goal:** Convert natural language → SQL using the dynamic schema context.

### Tasks (`backend/sql_generator.py`)

| # | Task |
|---|------|
| 1 | Build schema-aware system prompt with table names, columns, FK relationships |
| 2 | Send NL query + schema to LLM (OpenAI/Gemini) |
| 3 | Restrict output to SELECT-only queries |
| 4 | Parse and return only the SQL statement |

### Prompt Template

```
You are a SQL expert for PostgreSQL.

Available tables and their columns:
{schema_context}

Foreign key relationships:
{fk_context}

Rules:
- Generate ONLY a single SELECT query.
- Do NOT use DROP, DELETE, UPDATE, ALTER, INSERT, or TRUNCATE.
- Return ONLY the SQL query, no explanation.

User question: {user_question}
SQL:
```

### Phase 4 Tests

| Prompt | Expected SQL |
|--------|-------------|
| `Show all customers` | `SELECT * FROM customers;` |
| `Show total revenue from sales_data` | `SELECT SUM(revenue) FROM sales_data;` |
| `Show customer name and order amount` | `SELECT c.name, o.amount FROM customers c JOIN orders o ON c.id = o.customer_id;` |

---

## 🔹 PHASE 5 — Security Layer [COMPLETED]

**Goal:** Block all unsafe and injection queries.

### Tasks (`backend/security.py`)

| # | Task |
|---|------|
| 1 | Whitelist only `SELECT` statements |
| 2 | Block keywords: `DROP`, `DELETE`, `UPDATE`, `ALTER`, `INSERT`, `TRUNCATE`, `EXEC` |
| 3 | Block multiple statements (`;` detection) |
| 4 | Detect SQL injection patterns (`'--`, `OR 1=1`, `UNION SELECT`, etc.) |
| 5 | Return structured error with reason |

### Blocked Pattern Examples

```python
BLOCKED_KEYWORDS = [
    "DROP", "DELETE", "UPDATE", "ALTER",
    "INSERT", "TRUNCATE", "EXEC", "EXECUTE",
    "GRANT", "REVOKE", "CREATE", "REPLACE"
]
INJECTION_PATTERNS = [
    r";\s*(DROP|DELETE|UPDATE)",  # stacked queries
    r"(--|#)\s",                  # comment-based injection
    r"OR\s+1\s*=\s*1",           # tautology
    r"UNION\s+SELECT",            # UNION injection
]
```

### Phase 5 Tests

| Input | Expected |
|-------|----------|
| `Show all customers; DROP TABLE customers;` | Blocked – stacked query |
| `Delete all data` | Blocked – unsafe keyword |
| `Show all WHERE id=1 OR 1=1` | Blocked – injection pattern |

---

## 🔹 PHASE 6 — Query Execution & Visualization [COMPLETED]

**Goal:** Execute SQL, display results, and auto-generate charts.

### Tasks (`backend/main.py` + `frontend/app.py`)

| # | Task |
|---|------|
| 1 | Execute validated SQL via SQLAlchemy |
| 2 | Convert result to Pandas DataFrame |
| 3 | Auto-detect chart type from columns |
| 4 | Render chart in Streamlit |
| 5 | Paginate large results (default: 100 rows/page) |

### Chart Auto-Detection Logic

```python
if date_column_present:
    chart = "line"
elif categorical_column + numeric_column:
    chart = "bar"
elif single_numeric_value:
    chart = "KPI metric"
else:
    chart = "table"
```

### Phase 6 Tests

| Prompt | Expected Visualization |
|--------|----------------------|
| `Show monthly revenue from sales_data` | Line chart |
| `Show top 5 products by revenue` | Bar chart |
| `Total number of customers` | KPI card |

---

## 🔹 PHASE 7 — Self-Correction Engine

**Goal:** Automatically fix invalid SQL on execution error.

### Tasks (`backend/sql_generator.py`)

| # | Task |
|---|------|
| 1 | Catch `psycopg2.ProgrammingError` / `sqlalchemy.exc` |
| 2 | Send correction prompt to LLM with original query + error message |
| 3 | Retry execution once with corrected SQL |
| 4 | Show correction notice in UI |

### Correction Prompt Template

```
The following SQL query failed with an error:

SQL: {original_sql}
Error: {error_message}

Fix the SQL query. Return ONLY the corrected SQL.
Corrected SQL:
```

### Phase 7 Tests

| Input | Expected |
|-------|----------|
| `Show total revene from sales_data` | LLM corrects `revene` → `revenue`, re-executes |
| Invalid column name | Error caught, correction sent, retry succeeds |

---

## 🔹 PHASE 8 — Cost Optimization

**Goal:** Prevent expensive full-table scans and unoptimized queries.

### Tasks (`backend/optimizer.py`)

| # | Task |
|---|------|
| 1 | Run `EXPLAIN ANALYZE <query>` before execution |
| 2 | Parse total cost from EXPLAIN output |
| 3 | If cost > threshold → send query to LLM for optimization |
| 4 | Add `LIMIT` if missing on large table queries |
| 5 | Show cost indicator (🟢 Low / 🟡 Medium / 🔴 High) in UI |

### Cost Threshold

```python
COST_THRESHOLDS = {
    "low":    1000,    # Green
    "medium": 10000,   # Yellow — warn user
    "high":   50000,   # Red — auto-optimize
}
```

### Phase 8 Tests

| Query | Expected |
|-------|----------|
| `Show all data from sales_data` | LIMIT appended, cost reduced |
| `SELECT * FROM orders` | Optimization applied if large |

---

## 🔹 PHASE 9 — Conversational Memory

**Goal:** Support follow-up queries that refine previous results.

### Tasks (`backend/memory.py`)

| # | Task |
|---|------|
| 1 | Store last NL query in session state |
| 2 | Store last generated SQL in session state |
| 3 | Detect follow-up cues (`only`, `also`, `filter by`, `just show`) |
| 4 | Inject previous SQL + follow-up into LLM for refinement |

### Memory State

```python
session = {
    "last_nl":  "Show revenue for 2025",
    "last_sql": "SELECT ... WHERE year = 2025",
}
```

### Phase 9 Tests

| Sequence | Expected |
|----------|----------|
| `Show revenue for 2025` | Base SQL generated |
| `Only January` | WHERE clause updated: `AND month = 1` |
| `Also show product name` | JOIN added to previous SQL |

---

## 🔹 PHASE 10 — Role-Based Access Control

**Goal:** Restrict sensitive data by user role.

### Tasks (`backend/access_control.py` + `frontend/app.py`)

| # | Task |
|---|------|
| 1 | Add role selector in UI: `Admin / Analyst / Viewer` |
| 2 | Define table whitelist per role |
| 3 | Define column blacklist per role (mask sensitive columns) |
| 4 | Block query before execution if role unauthorised |
| 5 | Replace masked column values with `***` in output |

### Role Permission Matrix

| Role | Can Query | Blocked Columns |
|------|-----------|----------------|
| Admin | All tables | None |
| Analyst | All except HR tables | `salary`, `ssn` |
| Viewer | Public tables only | `email`, `salary`, `ssn` |

### Phase 10 Tests

| Role | Query | Expected |
|------|-------|----------|
| Viewer | `Show employee salaries` | Blocked or masked |
| Analyst | `Show customer emails` | `email` masked as `***` |
| Admin | Any query | Full access |

---

## 🏁 Final System Flow

```
CSV Upload
    ↓
Dynamic Schema Detection
    ↓
NL Query (User Input)
    ↓
Schema-Aware LLM Prompt
    ↓
Role-Based Access Check
    ↓
Security Validation (Injection + Keyword Block)
    ↓
EXPLAIN ANALYZE (Cost Optimization)
    ↓
SQL Execution
    ↓
Self-Correction (if error)
    ↓
Pandas DataFrame
    ↓
Auto Visualization (Chart / KPI / Table)
    ↓
Conversational Memory Update
```

---

## 🧪 Full Test Checklist

| Phase | Test Case | Expected Result |
|-------|-----------|----------------|
| 1 | `SELECT * FROM uploaded_tables` | Empty table |
| 2 | Upload `sales_data.csv` | Table auto-created, data inserted |
| 3 | `What tables are available?` | All tables listed |
| 4 | `Show all customers` | `SELECT * FROM customers;` |
| 5 | `Show all customers; DROP TABLE customers;` | Blocked |
| 6 | `Show monthly revenue` | Line chart rendered |
| 7 | `Show total revene from sales_data` | Auto-corrected to `revenue` |
| 8 | `Show all data from sales_data` | LIMIT applied, cost reduced |
| 9 | `Show revenue for 2025` → `Only January` | WHERE updated |
| 10 | Viewer: `Show employee salaries` | Blocked or masked |

---

## 📦 Requirements

```
fastapi
uvicorn
psycopg2-binary
sqlalchemy
pandas
streamlit
python-multipart
openai          # or google-generativeai for Gemini
python-dotenv
plotly
```

---

## 🚀 Execution Order

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
       → Phase 6 → Phase 7 → Phase 8 → Phase 9 → Phase 10
```

Each phase is independently testable before moving forward.
