from sqlalchemy import text
from core.database import SessionLocal

def fix_schema():
    db = SessionLocal()
    
    # List of all new columns to add
    new_columns = [
        ("first_name", "VARCHAR(100)"),
        ("last_name", "VARCHAR(100)"),
        ("date_of_birth", "DATE"),
        ("gender", "VARCHAR(20)"),
        ("city", "VARCHAR(100)"),
        ("address", "TEXT"),
        ("occupation", "VARCHAR(100)"),
        ("education", "VARCHAR(100)"),
        ("industry_domain", "VARCHAR(100)"),
        ("hobbies", "VARCHAR(255)"),
    ]

    print("🔧 Starting PostgreSQL Schema Update...")
    
    try:
        for col_name, col_type in new_columns:
            try:
                # Try to add the column
                print(f"Attempting to add: {col_name}...")
                db.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type};"))
                print(f"✅ Successfully added '{col_name}'")
            except Exception as e:
                # If it fails, it likely already exists. Rollback the transaction to continue.
                db.rollback()
                print(f"ℹ️  Skipped '{col_name}' (Likely already exists)")
        
        db.commit()
        print("\n🎉 Database patching complete! You can now restart your server.")
        
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_schema()