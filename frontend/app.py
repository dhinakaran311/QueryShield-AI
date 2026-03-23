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
    upload_btn = st.button("🚀 Upload & Create Table", width='stretch')

    st.divider()
    st.header("📋 Uploaded Tables")
    if st.button("🔄 Refresh Table List", width='stretch'):
        st.session_state["refresh_tables"] = True

    st.divider()
    st.header("🧠 Memory Context")
    if st.session_state.get("last_nl"):
        st.info(f"**Previous Q:** {st.session_state['last_nl']}")
        with st.expander("View SQL Memory"):
            st.code(st.session_state.get("last_sql", ""), language="sql")
    else:
        st.caption("No active conversation.")

    st.divider()
    st.header("🔐 Access Role")
    selected_role = st.selectbox(
        label   = "Select your role",
        options = ["Admin", "Analyst", "Viewer"],
        index   = 0,
        help    = "Admin: full access | Analyst: no HR/salary | Viewer: public only"
    )
    st.session_state["role"] = selected_role

    role_badges = {"Admin": "🟢", "Analyst": "🟡", "Viewer": "🔴"}
    st.caption(f"{role_badges.get(selected_role, '')} Active role: **{selected_role}**")

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
    st.dataframe(schema_df, width='stretch', hide_index=True)

    # Preview uploaded data
    if "uploaded_file_bytes" in st.session_state:
        st.subheader("👁️ Data Preview (first 10 rows)")
        preview_df = pd.read_csv(io.BytesIO(st.session_state["uploaded_file_bytes"]))
        st.dataframe(preview_df.head(10), width='stretch')

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
            st.dataframe(tables_df, width='stretch', hide_index=True)
        else:
            st.info("No tables uploaded yet. Upload a CSV to get started!")
    else:
        st.warning("Could not fetch table list from backend.")
except requests.exceptions.ConnectionError:
    st.warning("⚠️ Backend not connected. Start the FastAPI server to see tables.")

# ─── Query Interface (Phase 4 & 6) ──────────────────────────────────────────
st.divider()
st.header("💬 Ask your Data")
st.info("QueryShield AI securely converts your question to SQL and visualizes the results.")

user_question = st.text_input(
    label       = "Enter your question in natural language",
    placeholder = "e.g., Show total revenue by category",
    help        = "The AI will generate a safe SELECT query to fetch answers."
)

col_q1, col_q2 = st.columns([1, 4])
with col_q1:
    ask_btn = st.button("🔍 Ask AI", width='stretch', type="primary")
with col_q2:
    if st.button("🗑️ Clear History"):
        st.session_state["history"] = []
        st.session_state["last_sql"] = None
        st.session_state["last_nl"] = None

# --- Visualization Logic ---
def auto_detect_viz(df: pd.DataFrame):
    """Auto-detect best visualization based on DataFrame structure."""
    if df.empty:
        st.warning("No data returned for this query.")
        return

    cols = df.columns.tolist()
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime', 'date']).columns.tolist()
    cat_cols = [c for c in cols if c not in num_cols and c not in date_cols]

    # CASE 1: Single numeric value (KPI Card)
    if len(df) == 1 and len(num_cols) == 1 and len(cols) == 1:
        st.metric(label=cols[0], value=f"{df.iloc[0, 0]:,}")
    
    # CASE 2: Time Series (Line Chart)
    elif date_cols and num_cols:
        st.subheader("📈 Trend Analysis")
        st.line_chart(df.set_index(date_cols[0])[num_cols[0]])

    # CASE 3: Categorical + Numeric (Bar Chart)
    elif cat_cols and num_cols:
        st.subheader("📊 Comparison")
        # Use first categorical and first numeric
        st.bar_chart(df.set_index(cat_cols[0])[num_cols[0]])
    
    # CASE 4: Default Table
    else:
        st.subheader("📋 Query Results")
        st.dataframe(df, width='stretch')

if ask_btn and user_question.strip():
    with st.spinner("Shielding and querying..."):
        try:
            # 1. Generate SQL
            gen_payload = {
                "question": user_question,
                "last_nl":  st.session_state.get("last_nl"),
                "last_sql": st.session_state.get("last_sql")
            }
            gen_resp = requests.post(f"{API_URL}/generate-sql", json=gen_payload, timeout=180)
            
            if gen_resp.status_code == 200:
                gen_data = gen_resp.json()
                sql = gen_data["sql"]
                
                if gen_data.get("is_followup"):
                    st.success("💬 Smart Follow-up Detected – Refined previous query")
                    
                st.code(sql, language="sql")
                
                # 2. Execute SQL
                current_role = st.session_state.get("role", "Admin")
                exec_payload = {"question": user_question, "last_sql": sql, "role": current_role}
                exec_resp = requests.post(f"{API_URL}/execute-sql", json=exec_payload, timeout=180)
                
                if exec_resp.status_code == 200:
                    exec_data = exec_resp.json()
                    results_df = pd.DataFrame(exec_data["data"])

                    if exec_data.get("was_corrected"):
                        st.info("⚙️ AI auto-corrected the query")
                        st.code(exec_data.get("corrected_sql", ""), language="sql")

                    cost_label = exec_data.get("cost_label", "🟢 Low")
                    query_cost = exec_data.get("query_cost", 0)
                    st.metric("Query Cost", cost_label, help=f"Raw cost: {query_cost:.1f}")
                    if exec_data.get("was_optimized"):
                        st.info("⚡ Query was auto-optimized for performance")

                    # Store for memory
                    st.session_state["last_nl"] = user_question
                    st.session_state["last_sql"] = exec_data.get("corrected_sql", sql) if exec_data.get("was_corrected") else sql

                    # 3. Visualize
                    auto_detect_viz(results_df)

                    with st.expander("Show Raw Data"):
                        st.write(results_df)

                elif exec_resp.status_code == 403:
                    st.error(f"🛡️ Security Block: {exec_resp.json()['detail']['reason']}")
                else:
                    st.error(f"❌ Execution failed: {exec_resp.json().get('detail', 'Unknown error')}")
            else:
                st.error(f"❌ AI Generation failed: {gen_resp.json().get('detail', 'Unknown error')}")
                
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")

st.divider()
st.caption("QueryShield AI v0.4.0 | Phase 9: Conversational Memory")
