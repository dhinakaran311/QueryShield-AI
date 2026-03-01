"""Phase 3 test: Schema Detection endpoints"""
import urllib.request, json

BASE = "http://localhost:8000"

def get(path):
    r = urllib.request.urlopen(f"{BASE}{path}")
    return json.loads(r.read())

# ── Test 1: All tables ────────────────────────────────────────────────────────
print("=" * 60)
print("TEST 1: GET /schema — all tables + FK relationships")
print("=" * 60)
schema = get("/schema")
print(f"Table count: {schema['table_count']}")
print(f"Tables: {list(schema['tables'].keys())}")
print(f"Foreign keys:")
for fk in schema["foreign_keys"]:
    print(f"  {fk['table']}.{fk['column']} → {fk['references_table']}.{fk['references_column']}")

# ── Test 2: Single table columns ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("TEST 2: GET /schema/customers — column details")
print("=" * 60)
cust = get("/schema/customers")
print(f"Table: {cust['table_name']} | Columns: {cust['column_count']}")
for col in cust["columns"]:
    print(f"  {col['column_name']:20} {col['data_type']}")

# ── Test 3: Uploaded table schema ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("TEST 3: GET /schema/sales_data — uploaded CSV table")
print("=" * 60)
sales = get("/schema/sales_data")
print(f"Table: {sales['table_name']} | Columns: {sales['column_count']}")
for col in sales["columns"]:
    print(f"  {col['column_name']:20} {col['data_type']}")

# ── Test 4: Unknown table → 404 ───────────────────────────────────────────────
print("\n" + "=" * 60)
print("TEST 4: GET /schema/nonexistent → expect 404")
print("=" * 60)
try:
    get("/schema/nonexistent_table")
    print("  FAIL: Should have raised 404")
except urllib.error.HTTPError as e:
    print(f"  PASS: Got HTTP {e.code} as expected")

# ── Test 5: LLM schema prompt ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("TEST 5: GET /schema-prompt — LLM-ready text")
print("=" * 60)
prompt_resp = get("/schema-prompt")
prompt_text = prompt_resp["schema_prompt"]
lines = prompt_text.split("\n")
print(f"  Prompt length: {len(prompt_text)} chars, {len(lines)} lines")
print("  Preview (first 20 lines):")
for line in lines[:20]:
    print(f"    {line}")

print("\n✅ ALL PHASE 3 TESTS COMPLETE")
