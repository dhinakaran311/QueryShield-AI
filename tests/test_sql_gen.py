"""
Phase 4 test: LLM SQL Generation via POST /generate-sql
Tests: basic query, join query, aggregation, follow-up refinement
"""
import json, http.client

BASE_HOST = "localhost"
BASE_PORT = 8000

def post_json(path, payload):
    body = json.dumps(payload).encode()
    conn = http.client.HTTPConnection(BASE_HOST, BASE_PORT)
    conn.request("POST", path, body, {
        "Content-Type": "application/json",
        "Content-Length": str(len(body)),
    })
    resp = conn.getresponse()
    data = json.loads(resp.read())
    return resp.status, data

def sep(title):
    print(f"\n{'='*60}")
    print(f"TEST: {title}")
    print('='*60)

# ── Test 1: Basic SELECT ──────────────────────────────────────────
sep("Show all customers")
status, data = post_json("/generate-sql", {"question": "Show all customers"})
print(f"Status: {status}")
print(f"SQL: {data.get('sql')}")

# ── Test 2: Aggregation ───────────────────────────────────────────
sep("Show total revenue from sales_data")
status, data = post_json("/generate-sql", {"question": "Show total revenue from sales_data"})
print(f"Status: {status}")
print(f"SQL: {data.get('sql')}")

# ── Test 3: JOIN query ────────────────────────────────────────────
sep("Show customer name and their total order amount")
status, data = post_json("/generate-sql", {
    "question": "Show customer name and their total order amount"
})
print(f"Status: {status}")
print(f"SQL: {data.get('sql')}")

# ── Test 4: Top N query ───────────────────────────────────────────
sep("Show top 5 products by price")
status, data = post_json("/generate-sql", {
    "question": "Show top 5 products by price"
})
print(f"Status: {status}")
print(f"SQL: {data.get('sql')}")

# ── Test 5: Follow-up (conversational) ───────────────────────────
sep("Follow-up: Only delivered orders")
last_sql = "SELECT * FROM orders;"
status, data = post_json("/generate-sql", {
    "question": "Only show delivered ones",
    "last_nl":  "Show all orders",
    "last_sql": last_sql,
})
print(f"Status:      {status}")
print(f"Is followup: {data.get('is_followup')}")
print(f"SQL: {data.get('sql')}")

# ── Test 6: Tables used ───────────────────────────────────────────
sep("Schema tables available to LLM")
status, data = post_json("/generate-sql", {"question": "Count orders per customer"})
print(f"Status: {status}")
print(f"Schema used: {data.get('schema_used')}")
print(f"SQL: {data.get('sql')}")

print("\n✅ ALL PHASE 4 TESTS COMPLETE")
