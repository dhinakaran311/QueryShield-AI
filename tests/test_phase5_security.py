"""
Phase 5 test: Security Layer (SQL Validation)
Tests: safe SELECT, blocked keywords, injection patterns, multi-statement
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.security import validate_sql

def run_test(title, sql):
    print(f"\nTEST: {title}")
    print(f"SQL:  {sql}")
    result = validate_sql(sql)
    if result["is_safe"]:
        print("RESULT: [PASS] SAFE")
    else:
        print(f"RESULT: [BLOCK] Reason: {result['reason']}")
    return result["is_safe"]

if __name__ == "__main__":
    print("="*60)
    print("PHASE 5: SECURITY VALIDATION TESTS")
    print("="*60)

    # 1. Safe Queries
    run_test("Basic SELECT", "SELECT * FROM customers;")
    run_test("JOIN query", "SELECT c.name, o.id FROM customers c JOIN orders o ON c.id = o.customer_id;")
    run_test("Aggregation", "SELECT SUM(price) FROM products WHERE category = 'Electronics';")

    # 2. Blocked Keywords
    run_test("DROP attempt", "DROP TABLE customers;")
    run_test("DELETE attempt", "DELETE FROM orders WHERE id = 1;")
    run_test("keyword inside string (Safe)", "SELECT * FROM comments WHERE msg = 'Please delete this account';") 
    # Note: Our simple keyword check might block the above if it's not context-aware. 
    # Let's see how our implementation handles it.

    # 3. Multi-statement (Stacked Queries)
    run_test("Stacked query", "SELECT * FROM customers; DROP TABLE orders;")
    run_test("Extra Semicolon", "SELECT * FROM customers; --")

    # 4. Injection Patterns
    run_test("Tautology (1=1)", "SELECT * FROM users WHERE id = 1 OR 1=1;")
    run_test("UNION SELECT", "SELECT name FROM users UNION SELECT password FROM secrets;")
    run_test("Postgres sleep", "SELECT * FROM products; SELECT pg_sleep(10);")

    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)
