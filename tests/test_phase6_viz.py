"""
Phase 6 test: SQL Execution & Visualization Bridge
Tests: full flow from /generate-sql to /execute-sql
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_flow(question):
    print(f"\n--- TESTING: {question} ---")
    
    # 1. Generate SQL
    print("Step 1: Generating SQL...")
    gen_resp = requests.post(f"{API_URL}/generate-sql", json={"question": question})
    if gen_resp.status_code != 200:
        print(f"FAILED to generate SQL: {gen_resp.text}")
        return
    
    gen_data = gen_resp.json()
    sql = gen_data["sql"]
    print(f"AI generated: {sql}")

    # 2. Execute SQL
    print("Step 2: Executing SQL...")
    exec_resp = requests.post(f"{API_URL}/execute-sql", json={"question": question, "last_sql": sql})
    if exec_resp.status_code != 200:
        print(f"FAILED to execute SQL: {exec_resp.text}")
        return
    
    exec_data = exec_resp.json()
    print(f"Success! Rows returned: {exec_data['count']}")
    if exec_data['count'] > 0:
        print(f"Columns: {exec_data['columns']}")
        print(f"Sample row: {exec_data['data'][0]}")
    return True

if __name__ == "__main__":
    print("="*60)
    print("PHASE 6: FULL FLOW INTEGRATION TESTS")
    print("="*60)

    try:
        test_flow("Show all customers")
        test_flow("Total count of orders")
        test_flow("Show revenue per category from products")
    except Exception as e:
        print(f"Error during test: {e}")
        print("NOTE: Make sure the FastAPI server is running (uvicorn backend.main:app)")

    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)
