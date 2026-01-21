"""
Master Database Migration Script - PRI System

Combines all schema migrations for the PRI assessment system.
Run this only once on fresh databases or when resetting.
"""

from sqlalchemy import text, inspect
from core.database import Base, engine, SessionLocal
import sys

def run_migrations():
    """Execute all migrations in sequence"""
    
    print("=" * 60)
    print("PRI SYSTEM MASTER MIGRATION")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Migration 1: Convert PRI score columns to Float
        print("\n1️⃣  Converting PRI score columns to Float...")
        
        inspector = inspect(engine)
        columns = inspector.get_columns('submissions')
        score_cols = ['purpose_score', 'relevance_score', 'identity_score']
        
        for col in score_cols:
            col_info = next((c for c in columns if c['name'] == col), None)
            if col_info and str(col_info['type']) != 'DOUBLE_PRECISION':
                db.execute(text(f"ALTER TABLE submissions ALTER COLUMN {col} TYPE DOUBLE PRECISION USING {col}::double precision"))
                print(f"   ✓ {col} → DOUBLE PRECISION")
        
        # Migration 2: Fix existing scores (divide by 100)
        print("\n2️⃣  Fixing existing PRI scores (converting from integer scale)...")
        
        result = db.execute(text("""
            UPDATE submissions 
            SET purpose_score = purpose_score / 100.0,
                relevance_score = relevance_score / 100.0,
                identity_score = identity_score / 100.0
            WHERE purpose_score > 1.0 OR relevance_score > 1.0 OR identity_score > 1.0
        """))
        
        print(f"   ✓ Updated {result.rowcount} submissions")
        
        db.commit()
        print("\n✅ All migrations completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    response = input("\n⚠️  Run PRI migrations? This will modify the database. Type 'YES' to confirm: ")
    if response == 'YES':
        run_migrations()
    else:
        print("❌ Cancelled")
