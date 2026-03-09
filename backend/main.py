"""
backend/main.py
FastAPI application entry point for QueryShield AI.
Phase 2: CSV Upload | Phase 3: Schema Detection
"""

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.database import test_connection
from backend.csv_uploader import upload_csv, get_uploaded_tables
from backend.schema_detector import (
    get_all_tables,
    get_table_columns,
    get_foreign_keys,
    get_full_schema,
    build_schema_prompt,
)

# ─── App init ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "QueryShield AI API",
    description = "Secure Conversational Text-to-SQL with Dynamic Data Upload",
    version     = "0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)


# ─── Health check ─────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    db_ok = test_connection()
    return {
        "app":    "QueryShield AI",
        "status": "running",
        "db":     "connected" if db_ok else "error",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "db_connected": test_connection()}


# ─── Phase 2: CSV Upload ───────────────────────────────────────────────────────
@app.post("/upload-csv", tags=["CSV Upload"])
async def upload_csv_endpoint(
    file:        UploadFile = File(..., description="CSV file to upload"),
    table_name:  str        = Form(..., description="Name for the new table"),
    uploaded_by: str        = Form("user", description="Uploader identifier"),
):
    """
    Upload a CSV file and auto-create a PostgreSQL table from it.

    - Detects column names and infers data types via Pandas
    - Creates and populates the table automatically
    - Records metadata in `uploaded_tables`
    """
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code = 400,
            detail      = "Only .csv files are supported."
        )

    # Read file bytes
    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Max size guard (50 MB)
    max_bytes = 50 * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code = 413,
            detail      = "File too large. Maximum allowed size is 50 MB."
        )

    try:
        result = upload_csv(
            file_bytes  = file_bytes,
            table_name  = table_name,
            uploaded_by = uploaded_by,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    return JSONResponse(
        status_code = 200,
        content     = {
            "success":       True,
            "message":       f"Table '{result['table_name']}' created successfully.",
            "table_name":    result["table_name"],
            "rows_inserted": result["rows_inserted"],
            "columns":       result["columns"],
            "schema":        result["schema"],
        }
    )


@app.get("/uploaded-tables", tags=["CSV Upload"])
def list_uploaded_tables():
    """List all tables that have been uploaded by users."""
    try:
        tables = get_uploaded_tables()
        return {"tables": tables, "count": len(tables)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Phase 3: Schema Detection ────────────────────────────────────────────────

@app.get("/schema", tags=["Schema"])
def get_schema():
    """
    Return full schema: all tables, their columns, and FK relationships.
    Used by the LLM in Phase 4 to generate accurate SQL.
    """
    try:
        schema = get_full_schema()
        return {
            "table_count": len(schema["tables"]),
            "tables":      {t: cols for t, cols in schema["tables"].items()},
            "foreign_keys": schema["foreign_keys"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/schema/{table_name}", tags=["Schema"])
def get_table_schema(table_name: str):
    """
    Return column details for a specific table.
    """
    try:
        all_tables = get_all_tables()
        if table_name not in all_tables:
            raise HTTPException(
                status_code=404,
                detail=f"Table '{table_name}' not found in public schema."
            )
        columns = get_table_columns(table_name)
        return {
            "table_name": table_name,
            "columns":    columns,
            "column_count": len(columns),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/schema-prompt", tags=["Schema"])
def get_schema_prompt():
    """
    Return the schema as a formatted text string ready for LLM injection.
    (Used internally by Phase 4 SQL generator)
    """
    try:
        schema = get_full_schema()
        prompt = build_schema_prompt(schema)
        return {"schema_prompt": prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Phase 4 & 5: LLM SQL Generation & Security ──────────────────────────────
from pydantic import BaseModel
from typing import Optional
import sqlalchemy.exc
from backend.sql_generator import generate_sql as llm_generate_sql, correct_sql
from backend.security import validate_sql
from backend.optimizer import optimize_sql

class SQLRequest(BaseModel):
    question: str
    last_nl:  Optional[str] = None
    last_sql: Optional[str] = None


@app.post("/generate-sql", tags=["SQL Generation"])
def generate_sql_endpoint(req: SQLRequest):
    """
    Convert a natural language question to a PostgreSQL SELECT query.

    - Uses Gemini 2.0 / Ollama with full schema context
    - Returns SELECT-only SQL (validated via security layer)
    """
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    try:
        # 1. Generate SQL from LLM
        result = llm_generate_sql(
            user_question = req.question,
            last_nl       = req.last_nl,
            last_sql      = req.last_sql,
        )
        sql = result["sql"]

        # 2. Security Validation (Phase 5)
        sec_check = validate_sql(sql)
        if not sec_check["is_safe"]:
            raise HTTPException(
                status_code = 403,
                detail      = {
                    "error":  "Security Violation",
                    "reason": sec_check["reason"],
                    "sql":    sql
                }
            )

        return {
            "success":     True,
            "question":    req.question,
            "sql":         sql,
            "is_followup": result["is_followup"],
            "schema_used": result["schema_used"],
            "security":    "passed"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Operation failed: {str(e)}")


@app.post("/execute-sql", tags=["SQL Execution"])
def execute_sql_endpoint(req: SQLRequest):
    """
    Execute a validated SELECT query and return results.
    Phase 6: Result processing & data extraction.
    """
    if not req.last_sql:
        raise HTTPException(status_code=400, detail="SQL query is required.")

    # 1. Security check (Phase 5)
    sec_check = validate_sql(req.last_sql)
    if not sec_check["is_safe"]:
        raise HTTPException(
            status_code=403,
            detail={"error": "Security Violation", "reason": sec_check["reason"]}
        )

    from backend.database import execute_query

    # 2. Cost Optimization (Phase 8)
    opt = optimize_sql(req.last_sql)
    sql_to_run  = opt["sql"]
    query_cost  = opt["query_cost"]
    cost_level  = opt["cost_level"]
    cost_label  = opt["cost_label"]
    was_optimized = opt["was_optimized"]

    def _run(sql):
        return execute_query(sql)

    try:
        rows = _run(sql_to_run)
    except (sqlalchemy.exc.ProgrammingError, sqlalchemy.exc.OperationalError) as e:
        error_msg = str(e.orig) if hasattr(e, "orig") and e.orig else str(e)
        try:
            fixed_sql = correct_sql(sql_to_run, error_msg)
            rows = _run(fixed_sql)
        except Exception as inner:
            raise HTTPException(status_code=500, detail=f"Execution failed after correction attempt: {str(inner)}")
        if not rows:
            return {
                "success":        True,
                "data":           [],
                "columns":        [],
                "count":          0,
                "was_corrected":  True,
                "corrected_sql":  fixed_sql,
                "query_cost":     query_cost,
                "cost_level":     cost_level,
                "cost_label":     cost_label,
                "was_optimized":  was_optimized,
                "message":        "Query auto-corrected and executed. No rows returned."
            }
        return {
            "success":        True,
            "data":           rows,
            "columns":        list(rows[0].keys()),
            "count":          len(rows),
            "was_corrected":  True,
            "corrected_sql":  fixed_sql,
            "query_cost":     query_cost,
            "cost_level":     cost_level,
            "cost_label":     cost_label,
            "was_optimized":  was_optimized,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

    if not rows:
        return {
            "success":        True,
            "data":           [],
            "columns":        [],
            "count":          0,
            "was_corrected":  False,
            "query_cost":     query_cost,
            "cost_level":     cost_level,
            "cost_label":     cost_label,
            "was_optimized":  was_optimized,
            "message":        "Query executed successfully. No rows returned."
        }
    return {
        "success":        True,
        "data":           rows,
        "columns":        list(rows[0].keys()),
        "count":          len(rows),
        "was_corrected":  False,
        "query_cost":     query_cost,
        "cost_level":     cost_level,
        "cost_label":     cost_label,
        "was_optimized":  was_optimized,
    }
