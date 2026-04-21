"""Test the upload-csv endpoint directly."""
import io
import sys
sys.path.insert(0, '.')

# Create a minimal test CSV
csv_content = b"name,age,city\nAlice,30,Chennai\nBob,25,Delhi\nCarol,28,Mumbai\n"

from backend.csv_uploader import upload_csv

print("Testing upload_csv function directly...")
try:
    result = upload_csv(
        file_bytes=csv_content,
        table_name="test_upload_check",
        uploaded_by="diagnostic"
    )
    print("SUCCESS:", result)
except Exception as e:
    print("ERROR:", type(e).__name__, str(e))
    import traceback
    traceback.print_exc()
