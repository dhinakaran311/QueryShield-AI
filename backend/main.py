"""
backend/main.py
FastAPI application entry point for QueryShield AI.
Phase 2: CSV Upload endpoint.
"""

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.database import test_connection
from backend.csv_uploader import upload_csv, get_uploaded_tables

# ─── App init ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "QueryShield AI API",
    description = "Secure Conversational Text-to-SQL with Dynamic Data Upload",
    version     = "0.2.0",
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
