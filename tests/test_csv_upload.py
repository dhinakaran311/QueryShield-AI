"""Phase 2 endpoint test script"""
import urllib.request, urllib.parse, json, io

BASE = "http://localhost:8000"

def get(path):
    r = urllib.request.urlopen(f"{BASE}{path}")
    return json.loads(r.read())

def post_csv(csv_content: str, table_name: str):
    import http.client, mimetypes
    boundary = "----FormBoundary7MA4YWxkTrZu0gW"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="test.csv"\r\n'
        f"Content-Type: text/csv\r\n\r\n"
        f"{csv_content}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="table_name"\r\n\r\n{table_name}\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="uploaded_by"\r\n\r\ntest_user\r\n'
        f"--{boundary}--\r\n"
    ).encode()
    conn = http.client.HTTPConnection("localhost", 8000)
    conn.request("POST", "/upload-csv", body, {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
    })
    resp = conn.getresponse()
    return json.loads(resp.read())

# 1. Health check
print("=== Health ===")
print(json.dumps(get("/health"), indent=2))

# 2. Uploaded tables before
print("\n=== Uploaded Tables (before) ===")
print(json.dumps(get("/uploaded-tables"), indent=2))

# 3. Upload test CSV
sample_csv = """product_id,product_name,category,revenue,units_sold
1,Laptop Pro,Electronics,450000.00,6
2,Office Chair,Furniture,72000.00,6
3,Python Book,Books,14970.00,30
4,Monitor 4K,Electronics,168000.00,6
5,Wireless Mouse,Electronics,36000.00,30
"""

print("\n=== Upload CSV: sales_data ===")
print(json.dumps(post_csv(sample_csv, "sales_data"), indent=2))

# 4. Uploaded tables after
print("\n=== Uploaded Tables (after) ===")
print(json.dumps(get("/uploaded-tables"), indent=2))
