import sys
import os
import pandas as pd
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.sql_generator import generate_sql, correct_sql
from backend.database import execute_query
from backend.security import validate_sql
import sqlalchemy.exc

load_dotenv()

def verify_query(question):
    print(f"\n--- VERIFYING: {question} ---")
    
    # 1. Generate SQL
    print("Step 1: LLM SQL Generation...")
    try:
        result = generate_sql(question)
        sql = result["sql"]
        print(f"Generated SQL: {sql}")
    except Exception as e:
        print(f"FAILED to generate SQL: {e}")
        return False

    # 2. Security Validation
    print("Step 2: Security Validation...")
    sec_check = validate_sql(sql)
    if not sec_check["is_safe"]:
        print(f"SECURITY BLOCK: {sec_check['reason']}")
        return False
    print("Passed.")

    # 3. Execution
    print("Step 3: Database Execution...")
    try:
        rows = execute_query(sql)
    except (sqlalchemy.exc.ProgrammingError, sqlalchemy.exc.OperationalError) as e:
        print(f"EXECUTION ERROR: {e}")
        error_msg = str(e.orig) if hasattr(e, "orig") and e.orig else str(e)
        print("Attempting to auto-correct SQL...")
        try:
            sql = correct_sql(sql, error_msg)
            print(f"Corrected SQL: {sql}")
            rows = execute_query(sql)
        except Exception as inner_e:
            print(f"EXECUTION FAILED after correction: {inner_e}")
            return False
    except Exception as e:
        print(f"EXECUTION FAILED: {e}")
        return False

    count = len(rows)
    print(f"Success! {count} rows returned.")
    if count > 0:
        df = pd.DataFrame(rows)
        print("Output Data:")
        print(df.head(5))
    return True

if __name__ == "__main__":
    print("="*60)
    print("PHASE 6: DIRECT LOGIC VERIFICATION (PROOF OF WORK)")
    print("="*60)

    test_cases = [
        "Show all customers",
        "How many orders are there in total?",
        "Show revenue per category from products"
    ]

    success = 0
    for q in test_cases:
        if verify_query(q):
            success += 1

    print("\n" + "="*60)
    print(f"SUMMARY: {success}/{len(test_cases)} modules verified.")
    print("="*60)
    
    if success == len(test_cases):
        sys.exit(0)
    else:
        sys.exit(1)
