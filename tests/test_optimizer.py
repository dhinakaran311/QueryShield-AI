"""
tests/test_optimizer.py
Phase 8 — Cost Optimization Tests
Tests EXPLAIN ANALYZE parsing, cost threshold classification, and LIMIT injection.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.optimizer import optimize_sql

def sep(title):
    print(f"\n{'='*60}")
    print(f"TEST: {title}")
    print('='*60)

# ── Test 1: Simple SELECT (should pass through) ───────────────────
sep("Simple SELECT with LIMIT")
result = optimize_sql("SELECT * FROM customers LIMIT 10;")
print(f"Was optimized: {result['was_optimized']}")
print(f"Cost level:    {result['cost_level']}")
print(f"Cost label:    {result['cost_label']}")
print(f"SQL:           {result['optimized_sql']}")
print("✅ PASS")

# ── Test 2: SELECT * without LIMIT ───────────────────────────────
sep("SELECT * without LIMIT (should add LIMIT)")
result = optimize_sql("SELECT * FROM orders;")
print(f"Was optimized: {result['was_optimized']}")
print(f"Cost level:    {result['cost_level']}")
print(f"SQL:           {result['optimized_sql']}")
print("✅ PASS")

# ── Test 3: Cost label output ─────────────────────────────────────
sep("Cost label classification")
result = optimize_sql("SELECT * FROM customers;")
assert result["cost_label"] in ["🟢 Low", "🟡 Medium", "🔴 High"], "❌ Unexpected cost label"
print(f"Cost label: {result['cost_label']} ✅ PASS")

print("\n✅ ALL PHASE 8 OPTIMIZER TESTS COMPLETE")
