"""
Simple Database Reset - Drop and Recreate All Tables

WARN ING: Deletes all data!
"""

from core.database import Base, engine
from models import User, TestMetadata, Question, Submission, ReflectionSession, DailyReflection
import sys

def reset_database():
    """Drop and recreate all tables"""
    
    print("=" * 60)
    print("DATABASE RESET")
    print("=" * 60)
    print("\n⚠️  WARNING: This will delete ALL data!\n")
    
    response = input("Type 'YES' to confirm: ")
    if response != 'YES':
        print("❌ Cancelled")
        sys.exit(0)
    
    print("\n🗑️  Dropping all tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("✓ All tables dropped")
    except Exception as e:
        print(f"✗ Error dropping tables: {e}")
        sys.exit(1)
    
    print("\n📋 Creating all tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        sys.exit(1)
    
    print("\n✅ Database reset complete!")
    print("\nNext: Run python seed_pri_questions.py")

if __name__ == "__main__":
    reset_database()
