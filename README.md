# QueryShield AI

**Secure Conversational Text-to-SQL with Dynamic Data Upload**

QueryShield AI is a full-stack application that converts plain English questions into safe, optimized PostgreSQL queries. It combines a FastAPI backend with a Next.js frontend to provide an end-to-end natural language database interface with built-in security, query optimization, self-correction, and role-based access control.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [System Flow](#system-flow)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
- [Running the Application](#running-the-application)
- [API Reference](#api-reference)
- [Security Model](#security-model)
- [Role-Based Access Control](#role-based-access-control)
- [Application Output](#application-output)

---

## Overview

QueryShield AI eliminates the need for users to write SQL manually. A user types a natural language question — such as "Show all employees whose salary is above average" — and the system generates, validates, optimizes, and executes the corresponding SQL query, then returns the results as a paginated table with an auto-generated chart.

The system is designed with a defense-in-depth security strategy: every generated query passes through keyword filtering, injection pattern detection, role-based access checking, and cost-based optimization before it is executed against the database.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Next.js Frontend                         │
│         Query Tab  |  Upload CSV Tab  |  Schema Sidebar         │
└────────────────────────────┬────────────────────────────────────┘
                             │  HTTP / REST
┌────────────────────────────▼────────────────────────────────────┐
│                     FastAPI Backend                             │
│                                                                 │
│  /generate-sql  →  LLM (Groq / Gemini)  →  Security Validator  │
│  /execute-sql   →  RBAC  →  Optimizer   →  DB Executor          │
│  /upload-csv    →  Pandas Ingest  →  PostgreSQL                 │
│  /schema        →  Schema Detector                              │
└────────────────────────────┬────────────────────────────────────┘
                             │  SQLAlchemy / psycopg2
┌────────────────────────────▼────────────────────────────────────┐
│                      PostgreSQL Database                        │
│         Dynamic user tables  |  Demo schema  |  Metadata       │
└─────────────────────────────────────────────────────────────────┘
```

---

## System Flow

The following diagram describes the complete request lifecycle from a natural language question to a rendered result:

```
User enters natural language question
              |
              v
  ┌─────────────────────────┐
  │   Conversational Memory │  <-- Injects prior NL + SQL context
  │   (Follow-up detection) │      for multi-turn refinement
  └────────────┬────────────┘
               |
               v
  ┌─────────────────────────┐
  │   Dynamic Schema        │
  │   Detection             │  <-- Fetches all table schemas,
  │   (schema_detector.py)  │      columns, and FK relationships
  └────────────┬────────────┘
               |
               v
  ┌─────────────────────────┐
  │   LLM SQL Generation    │
  │   (Groq / Gemini)       │  <-- Schema-aware prompt with
  │   (sql_generator.py)    │      SELECT-only constraint
  └────────────┬────────────┘
               |
               v
  ┌─────────────────────────┐
  │   Security Validation   │  <-- Blocks: DROP, DELETE, UPDATE,
  │   (security.py)         │      UNION SELECT, stacked queries,
  │                         │      comment injection, tautologies
  └────────────┬────────────┘
               |
               v
  ┌─────────────────────────┐
  │   Role-Based Access     │  <-- Admin / Analyst / Viewer
  │   Control               │      Table whitelist + column
  │   (access_control.py)   │      blacklist enforcement
  └────────────┬────────────┘
               |
               v
  ┌─────────────────────────┐
  │   Cost Optimization     │  <-- EXPLAIN ANALYZE cost check
  │   (optimizer.py)        │      Auto-appends LIMIT on large
  │                         │      table scans (threshold-based)
  └────────────┬────────────┘
               |
               v
  ┌─────────────────────────┐
  │   SQL Execution         │
  │   (database.py)         │  <-- SQLAlchemy executes query
  └────────────┬────────────┘
               |
          ┌────┴────┐
          |  Error? |
          └────┬────┘
          Yes  |  No
               |         ┌─────────────────────────────┐
               |         │   PII Masking                │
               |         │   Sensitive columns masked   │
               |         │   (***) by role              │
               |         └──────────────┬──────────────┘
               |                        |
               v                        v
  ┌─────────────────────────┐  ┌─────────────────────────┐
  │   Self-Correction       │  │   Result Rendering       │
  │   Engine                │  │                         │
  │   (sql_generator.py)    │  │   Paginated table        │
  │   Sends error + SQL     │  │   Auto-generated chart   │
  │   back to LLM for fix   │  │   (bar / line / KPI)     │
  │   then re-executes      │  └─────────────────────────┘
  └─────────────────────────┘
```

---

## Features

**Natural Language to SQL**
Converts plain English questions into valid PostgreSQL SELECT statements using Groq (Llama) or Gemini LLM with full schema context injected into the prompt.

**Dynamic CSV Upload**
Users can upload any CSV file and assign it a table name. The system infers column types via Pandas, auto-generates the `CREATE TABLE` DDL, bulk-inserts rows, and records metadata. Uploaded tables are immediately available for querying.

**Schema-Aware Prompt Engineering**
Before sending a question to the LLM, the backend fetches the complete public schema — all tables, columns with data types, and foreign key relationships — and injects it as structured context. This ensures the model generates accurate, join-aware SQL.

**Multi-Layer Security**
Every generated SQL passes through a dedicated security validator that blocks dangerous keywords (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`, `EXEC`), stacked queries, comment-based injection, tautologies (`OR 1=1`), and UNION-based attacks.

**Query Cost Optimization**
Before execution, the query is run through `EXPLAIN ANALYZE`. If the estimated cost exceeds a configurable threshold, the optimizer automatically appends a `LIMIT` clause or requests a rewrite from the LLM.

**Self-Correction Engine**
If a query fails at runtime due to a schema mismatch or syntax error, the original SQL and the database error message are sent back to the LLM, which returns a corrected query. The corrected SQL is re-validated and re-executed automatically.

**Conversational Memory**
The system stores the last natural language query and its generated SQL in session memory. Follow-up phrases like "only January", "also show product name", or "filter by department" trigger context-aware refinement of the previous SQL rather than generating a new query from scratch.

**Role-Based Access Control**
Three roles — Admin, Analyst, and Viewer — each have a configured table whitelist and column blacklist. Sensitive columns such as `salary`, `email`, and `ssn` are masked as `***` in results returned to lower-privilege roles.

**Auto-Generated Visualizations**
Query results are automatically classified and rendered as a bar chart, line chart, or KPI metric based on column types detected in the result set.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16 (App Router), TypeScript, Tailwind CSS |
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Database | PostgreSQL 15+ |
| ORM / Driver | SQLAlchemy, psycopg2-binary |
| Data Processing | Pandas, NumPy |
| LLM Providers | Groq (Llama 3), Google Gemini, OpenAI |
| Visualization | Plotly (backend), Recharts (frontend) |
| Environment | python-dotenv, python-multipart |

---

## Project Structure

```
QueryShield AI/
│
├── backend/
│   ├── main.py                  # FastAPI application entry point
│   ├── database.py              # Database connection and query executor
│   ├── schema_detector.py       # Dynamic schema fetcher and prompt builder
│   ├── sql_generator.py         # LLM integration, prompt construction, self-correction
│   ├── security.py              # SQL injection and keyword validator
│   ├── optimizer.py             # EXPLAIN ANALYZE cost checker and optimizer
│   ├── memory.py                # Conversational session memory
│   ├── access_control.py        # Role-based table and column access enforcement
│   └── csv_uploader.py          # CSV ingestion and dynamic table creation
│
├── frontend-next/
│   ├── app/                     # Next.js App Router pages
│   ├── components/              # React UI components
│   └── lib/                     # API client utilities
│
├── db/
│   ├── schema.sql               # Base DDL (demo schema and metadata table)
│   ├── seed.sql                 # Demo INSERT data
│   └── setup.sql                # Combined runner script
│
├── tests/
│   ├── test_security.py
│   ├── test_upload.py
│   └── test_upload_http.py
│
├── requirements.txt
├── output.png                   # Application screenshot
└── .env                         # Environment variables (not committed)
```

---

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL 15 or higher (running locally or via a connection string)
- A Groq API key (free tier available) or a Gemini / OpenAI API key

---

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/dhinakaran311/QueryShield-AI.git
cd QueryShield-AI
```

### 2. Create and activate a Python virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root with the following values:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/queryshield_db
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Initialize the PostgreSQL database

```bash
psql -U postgres -c "CREATE DATABASE queryshield_db;"
psql -U postgres -d queryshield_db -f db/setup.sql
```

### 6. Install frontend dependencies

```bash
cd frontend-next
npm install
```

---

## Running the Application

### Start the backend

From the project root, with the virtual environment active:

```bash
uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive API documentation: `http://localhost:8000/docs`

### Start the frontend

In a separate terminal:

```bash
cd frontend-next
npm run dev
```

The application will be available at `http://localhost:3000`.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check and database status |
| GET | `/health` | Structured health response |
| POST | `/upload-csv` | Upload a CSV file and create a database table |
| GET | `/uploaded-tables` | List all user-uploaded tables |
| GET | `/schema` | Return full schema with tables, columns, and FK relationships |
| GET | `/schema/{table_name}` | Return column details for a specific table |
| GET | `/schema-prompt` | Return schema formatted as an LLM-ready string |
| POST | `/generate-sql` | Convert a natural language question to a SQL query |
| POST | `/execute-sql` | Execute a validated SQL query and return results |
| POST | `/clear-memory` | Clear the current conversational session context |

### Request body for `/generate-sql` and `/execute-sql`

```json
{
  "question": "Show all employees whose salary is above average",
  "last_nl": "Show all employees",
  "last_sql": "SELECT * FROM employees;",
  "role": "Admin"
}
```

---

## Security Model

QueryShield AI enforces a multi-layer security strategy to prevent SQL injection and unauthorized data access.

**Blocked Keywords**

`DROP`, `DELETE`, `UPDATE`, `ALTER`, `INSERT`, `TRUNCATE`, `EXEC`, `EXECUTE`, `GRANT`, `REVOKE`, `CREATE`, `REPLACE`

**Blocked Injection Patterns**

| Pattern | Example |
|---|---|
| Stacked queries | `SELECT * FROM users; DROP TABLE users;` |
| Comment injection | `SELECT * FROM users --` |
| Tautology | `WHERE id = 1 OR 1=1` |
| UNION attack | `UNION SELECT password FROM admin` |

Every generated SQL is validated before execution, and every corrected SQL is re-validated before the correction retry.

---

## Role-Based Access Control

| Role | Table Access | Restricted Columns |
|---|---|---|
| Admin | All tables | None |
| Analyst | All tables except HR-sensitive tables | `salary`, `ssn` |
| Viewer | Public tables only | `email`, `salary`, `ssn` |

Restricted columns are not omitted from results — they are replaced with `***` to preserve result structure while hiding sensitive values.

---

## Application Output

The screenshot below shows a live query session: the user asks for all employees whose salary is above average, the system generates the SQL, executes it, and renders a bar chart alongside a paginated result table.

![QueryShield AI — Application Output](output.png)

---

## License

This project is intended for academic and demonstration purposes.
