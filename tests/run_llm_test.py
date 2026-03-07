from dotenv import load_dotenv
load_dotenv()
from backend.sql_generator import generate_sql

tests = [
    "Show all customers",
    "Show total revenue from sales_data",
    "Show customer name and their total order amount",
]

for i, q in enumerate(tests, 1):
    print(f"\n=== Test {i} ===")
    print(f"Question: {q}")
    r = generate_sql(q)
    sql      = r["sql"]
    provider = r["provider"]
    model    = r["model"]
    print(f"SQL:      {sql}")
    print(f"Provider: {provider} | Model: {model}")

print("\n✅ ALL 3 TESTS DONE")
