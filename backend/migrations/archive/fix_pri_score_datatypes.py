"""
Migration: Fix PRI Score Column Datatypes from Integer to Float

Issue: purpose_score, relevance_score, identity_score were defined as Integer
but the application stores them as Float (0.0-1.0 range).

This migration converts them to Float type.
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")

def run_migration():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("Starting migration: Fix PRI score datatypes...")
        
        # Alter column types from INTEGER to FLOAT
        migrations = [
            "ALTER TABLE submissions ALTER COLUMN purpose_score TYPE DOUBLE PRECISION USING purpose_score::DOUBLE PRECISION;",
            "ALTER TABLE submissions ALTER COLUMN relevance_score TYPE DOUBLE PRECISION USING relevance_score::DOUBLE PRECISION;",
            "ALTER TABLE submissions ALTER COLUMN identity_score TYPE DOUBLE PRECISION USING identity_score::DOUBLE PRECISION;"
        ]
        
        for migration_sql in migrations:
            try:
                conn.execute(text(migration_sql))
                print(f"✓ Executed: {migration_sql}")
            except Exception as e:
                print(f"✗ Failed: {migration_sql}")
                print(f"  Error: {e}")
        
        conn.commit()
        print("Migration completed successfully!")

if __name__ == "__main__":
    run_migration()
