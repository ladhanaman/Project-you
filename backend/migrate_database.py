#!/usr/bin/env python
"""
Migration script to add missing columns to database
Run this with: python migrate_database.py
"""
from sqlalchemy import text
from core.database import engine

def run_migration():
    """Add retry_metadata and duration_minutes columns"""
    
    with engine.connect() as conn:
        try:
            # Add retry_metadata column to submissions table
            print("Adding retry_metadata column to submissions...")
            conn.execute(text("""
                ALTER TABLE submissions 
                ADD COLUMN IF NOT EXISTS retry_metadata JSON DEFAULT '{}'::json
            """))
            conn.commit()
            print("✓ Added retry_metadata column")
            
        except Exception as e:
            print(f"Note: retry_metadata column may already exist - {e}")
        
        try:
            # Add duration_minutes column to test_metadata table
            print("Adding duration_minutes column to test_metadata...")
            conn.execute(text("""
                ALTER TABLE test_metadata 
                ADD COLUMN IF NOT EXISTS duration_minutes INTEGER DEFAULT 30
            """))
            conn.commit()
            print("✓ Added duration_minutes column")
            
        except Exception as e:
            print(f"Note: duration_minutes column may already exist - {e}")
    
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    print("Starting database migration...\n")
    run_migration()
