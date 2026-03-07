"""
frontend/app.py
Streamlit UI for QueryShield AI — Phase 2: CSV Upload
"""

import streamlit as st
import requests
import pandas as pd
import io

API_URL = "http://localhost:8000"

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "QueryShield AI",
    page_icon  = "🛡️",
    layout     = "wide",
)

# ─── Header ───────────────────────────────────────────────────────────────────
st.title("🛡️ QueryShield AI")
st.caption("Secure Conversational Text-to-SQL with Dynamic Data Upload")
st.divider()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📁 Upload CSV")
    uploaded_file = st.file_uploader(
        label = "Choose a CSV file",
        type  = ["csv"],
        help  = "Max 50 MB. Column types are auto-detected.",
    )
    table_name_input = st.text_input(
        label       = "Table Name",
        placeholder = "e.g. sales_data",
        help        = "Lowercase letters, numbers, underscores only.",
    )
    uploaded_by = st.text_input(
        label       = "Your Name / ID",
        value       = "user",
        help        = "Tracked in metadata.",
    )
    upload_btn = st.button("🚀 Upload & Create Table", use_container_width=True)

    st.divider()
    st.header("📋 Uploaded Tables")
    if st.button("🔄 Refresh Table List", use_container_width=True):
        st.session_state["refresh_tables"] = True

# ─── Upload Logic ─────────────────────────────────────────────────────────────
if upload_btn:
    if not uploaded_file:
        st.sidebar.error("Please select a CSV file first.")
    elif not table_name_input.strip():
        st.sidebar.error("Please enter a table name.")
    else:
        with st.spinner("Uploading and creating table..."):
            try:
                response = requests.post(
                    f"{API_URL}/upload-csv",
                    files   = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")},
                    data    = {"table_name": table_name_input.strip(), "uploaded_by": uploaded_by},
                    timeout = 60,
                )
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ {result['message']}")
                    st.session_state["last_upload"] = result
                    st.session_state["refresh_tables"] = True
                else:
                    st.error(f"❌ Upload failed: {response.json().get('detail', 'Unknown error')}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend. Is the FastAPI server running on port 8000?")

# ─── Show last upload result ──────────────────────────────────────────────────
if "last_upload" in st.session_state:
    result = st.session_state["last_upload"]
    st.subheader("📊 Upload Result")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Table Name",    result["table_name"])
        st.metric("Rows Inserted", result["rows_inserted"])
    with col2:
        st.metric("Columns",       len(result["columns"]))

    st.subheader("🔍 Detected Schema")
    schema_df = pd.DataFrame(
        list(result["schema"].items()),
        columns=["Column Name", "PostgreSQL Type"]
    )
    st.dataframe(schema_df, use_container_width=True, hide_index=True)

    # Preview uploaded data
    if "uploaded_file_bytes" in st.session_state:
        st.subheader("👁️ Data Preview (first 10 rows)")
        preview_df = pd.read_csv(io.BytesIO(st.session_state["uploaded_file_bytes"]))
        st.dataframe(preview_df.head(10), use_container_width=True)

# Cache uploaded file bytes for preview
if uploaded_file:
    st.session_state["uploaded_file_bytes"] = uploaded_file.getvalue()

# ─── Uploaded Tables List ─────────────────────────────────────────────────────
st.divider()
st.subheader("📋 All Available Tables")

try:
    resp = requests.get(f"{API_URL}/uploaded-tables", timeout=5)
    if resp.status_code == 200:
        tables = resp.json().get("tables", [])
        if tables:
            tables_df = pd.DataFrame(tables)
            tables_df["upload_time"] = pd.to_datetime(tables_df["upload_time"]).dt.strftime("%Y-%m-%d %H:%M")
            st.dataframe(tables_df, use_container_width=True, hide_index=True)
        else:
            st.info("No tables uploaded yet. Upload a CSV to get started!")
    else:
        st.warning("Could not fetch table list from backend.")
except requests.exceptions.ConnectionError:
    st.warning("⚠️ Backend not connected. Start the FastAPI server to see tables.")

st.divider()
st.caption("QueryShield AI v0.2.0 | Phase 2: CSV Upload System")
