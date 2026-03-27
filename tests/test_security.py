"""
tests/test_security.py
Phase 5 — Security Layer Tests
Tests injection blocking, keyword blocking, and SELECT-only enforcement.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.security import validate_sql

def sep(title):
    print(f"\n{'='*60}")
    print(f"TEST: {title}")
    print('='*60)

# ── Test 1: Valid SELECT ──────────────────────────────────────────
sep("Valid SELECT query")
result = validate_sql("SELECT * FROM customers;")
print(f"Is safe: {result['is_safe']}")
assert result["is_safe"] is True, "❌ Valid SELECT should pass"
print("✅ PASS")

# ── Test 2: Stacked query injection ───────────────────────────────
sep("Stacked query: SELECT; DROP TABLE")
result = validate_sql("SELECT * FROM customers; DROP TABLE customers;")
print(f"Is safe: {result['is_safe']}, Reason: {result.get('reason')}")
assert result["is_safe"] is False, "❌ Stacked DROP should be blocked"
print("✅ PASS")

# ── Test 3: Delete keyword ────────────────────────────────────────
sep("DELETE keyword")
result = validate_sql("DELETE FROM customers WHERE id=1")
print(f"Is safe: {result['is_safe']}, Reason: {result.get('reason')}")
assert result["is_safe"] is False, "❌ DELETE should be blocked"
print("✅ PASS")

# ── Test 4: OR 1=1 tautology ─────────────────────────────────────
sep("OR 1=1 injection")
result = validate_sql("SELECT * FROM customers WHERE id=1 OR 1=1")
print(f"Is safe: {result['is_safe']}, Reason: {result.get('reason')}")
assert result["is_safe"] is False, "❌ OR 1=1 should be blocked"
print("✅ PASS")

# ── Test 5: UNION SELECT ─────────────────────────────────────────
sep("UNION SELECT injection")
result = validate_sql("SELECT id FROM customers UNION SELECT password FROM users")
print(f"Is safe: {result['is_safe']}, Reason: {result.get('reason')}")
assert result["is_safe"] is False, "❌ UNION SELECT should be blocked"
print("✅ PASS")

# ── Test 6: Non-SELECT statement ─────────────────────────────────
sep("UPDATE statement")
result = validate_sql("UPDATE customers SET name='hacked' WHERE id=1")
print(f"Is safe: {result['is_safe']}, Reason: {result.get('reason')}")
assert result["is_safe"] is False, "❌ UPDATE should be blocked"
print("✅ PASS")

print("\n✅ ALL PHASE 5 SECURITY TESTS PASSED")
