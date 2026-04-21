import sys; sys.path.insert(0,'.')
from backend.security import validate_sql

tests = [
    # (sql, expect_safe, label)
    ("SELECT * FROM superstore;", True, "Normal query with trailing semicolon"),
    ("SELECT sales FROM superstore ORDER BY sales DESC LIMIT 10;", True, "Complex valid query"),
    ("SELECT * FROM superstore; DROP TABLE superstore;", False, "Stacked DROP attack"),
    ("SELECT * FROM users; DELETE FROM users;", False, "Stacked DELETE attack"),
    ("SELECT * FROM t WHERE x='a'--", False, "SQL comment injection"),
    ("SELECT * FROM t /* comment */", False, "Multi-line comment"),
    ("DROP TABLE users;", False, "Direct DROP"),
    ("SELECT name FROM users UNION SELECT password FROM admin;", False, "UNION attack"),
]

all_passed = True
for sql, expect_safe, label in tests:
    result = validate_sql(sql)
    ok = result["is_safe"] == expect_safe
    status = "✅ PASS" if ok else "❌ FAIL"
    if not ok:
        all_passed = False
    print(f"{status} | {label}")
    if not ok:
        print(f"       Expected safe={expect_safe}, got {result}")

print()
print("ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED")
