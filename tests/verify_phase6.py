from fastapi.testclient import TestClient
import sys
import os
import pandas as pd

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app

client = TestClient(app)

def test_full_flow(question):
    print(f"\n--- TESTING: {question} ---")
    
    # 1. Generate SQL
    print("Step 1: Generating SQL (POST /generate-sql)...")
    gen_resp = client.post("/generate-sql", json={"question": question})
    if gen_resp.status_code != 200:
        print(f"FAILED to generate SQL: {gen_resp.text}")
        return False
    
    gen_data = gen_resp.json()
    sql = gen_data["sql"]
    print(f"AI generated: {sql}")

    # 2. Execute SQL
    print("Step 2: Executing SQL (POST /execute-sql)...")
    # Note: /execute-sql expects 'last_sql' in the request
    exec_resp = client.post("/execute-sql", json={"question": question, "last_sql": sql})
    if exec_resp.status_code != 200:
        print(f"FAILED to execute SQL: {exec_resp.text}")
        return False
    
    exec_data = exec_resp.json()
    print(f"Success! {exec_data['count']} rows returned.")
    
    if exec_data['count'] > 0:
        df = pd.DataFrame(exec_data['data'])
        print("Data Preview:")
        print(df.head(3))
        
    return True

if __name__ == "__main__":
    print("="*60)
    print("PHASE 6: IN-PROCESS INTEGRATION VERIFICATION")
    print("="*60)

    success_counts = 0
    test_cases = [
        "Show all customers",
        "How many orders are there in total?",
        "Show name and price of top 3 products",
        "Total subtotal from order_items"
    ]

    for q in test_cases:
        if test_full_flow(q):
            success_counts += 1

    print("\n" + "="*60)
    print(f"VERIFICATION COMPLETE: {success_counts}/{len(test_cases)} tests passed.")
    print("="*60)
    
    if success_counts == len(test_cases):
        sys.exit(0)
    else:
        sys.exit(1)
