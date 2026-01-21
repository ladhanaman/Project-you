"""
Complete Database Reset Script

WARNING: This will DROP ALL TABLES and recreate from scratch.
Use with extreme caution - all data will be lost.
"""

from sqlalchemy import create_engine, text, inspect
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def drop_all_tables():
    """Drop all tables in the database"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Get inspector
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            print("✓ Database is already empty")
            return
        
        print(f"🗑️  Dropping {len(tables)} tables...")
        
        # Disable foreign key checks
        conn.execute(text("SET session_replication_role = 'replica';"))
        
        # Drop each table
        for table in tables:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                print(f"  ✓ Dropped {table}")
            except Exception as e:
                print(f"  ✗ Failed to drop {table}: {e}")
        
        # Re-enable foreign key checks
        conn.execute(text("SET session_replication_role = 'origin';"))
        
        conn.commit()
        print("\n✅ All tables dropped successfully!")


def create_tables():
    """Create all tables from models"""
    print("\n📋 Creating tables from models...")
    
    try:
        # Import Base and all models
        from core.database import Base, engine
        from models import User, TestMetadata, Question, Submission, ReflectionSession, DailyReflection
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
    except Exception as e:
        print(f"✗ Failed to create tables: {e}")
        raise


def verify_schema():
    """Verify the schema is correct"""
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\n📊 Schema verification:")
    print(f"  Tables created: {len(tables)}")
    for table in sorted(tables):
        columns = inspector.get_columns(table)
        print(f"  ✓ {table}: {len(columns)} columns")
    
    return len(tables) > 0


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("DATABASE DEEP CLEAN & RESET")
    print("=" * 60)
    print("\n⚠️  WARNING: This will permanently delete ALL data!")
    
    response = input("\nType 'RESET' to confirm: ")
    if response != 'RESET':
        print("❌ Reset cancelled")
        sys.exit(0)
    
    # Phase 1: Drop all tables
    drop_all_tables()
    
    # Phase 2: Create tables
    create_tables()
    
    # Phase 3: Verify
    if verify_schema():
        print("\n✅ Database reset complete!")
        print("\nNext steps:")
        print("1. Run: python init_test_metadata.py")
        print("2. Verify 5 options are rendering")
    else:
        print("\n❌ Schema verification failed")
        sys.exit(1)
