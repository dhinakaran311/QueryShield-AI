"""
Direct HTTP test of /upload-csv endpoint.
Run while uvicorn is running on port 8000.
"""
import requests
import io

# Create a minimal test CSV
csv_bytes = b"name,age,city\nAlice,30,Chennai\nBob,25,Delhi\n"

print("=" * 60)
print("TEST 1: Direct upload to /upload-csv endpoint")
print("=" * 60)

try:
    response = requests.post(
        "http://localhost:8000/upload-csv",
        files={"file": ("test.csv", io.BytesIO(csv_bytes), "text/csv")},
        data={"table_name": "diag_test_table", "uploaded_by": "diagnostic"},
        timeout=30,
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

print()
print("=" * 60)
print("TEST 2: Missing table_name (should get 422)")
print("=" * 60)

try:
    response = requests.post(
        "http://localhost:8000/upload-csv",
        files={"file": ("test.csv", io.BytesIO(csv_bytes), "text/csv")},
        data={"uploaded_by": "diagnostic"},  # no table_name
        timeout=30,
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

print()
print("=" * 60)
print("TEST 3: Health check")
print("=" * 60)

try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

print()
print("=" * 60)
print("TEST 4: CORS preflight (simulate browser)")
print("=" * 60)

try:
    response = requests.options(
        "http://localhost:8000/upload-csv",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
        timeout=5,
    )
    print(f"Status: {response.status_code}")
    print(f"CORS Headers: {dict(response.headers)}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
