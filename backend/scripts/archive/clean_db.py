#!/usr/bin/env python3
"""
Clean database - Delete all questions, submissions, and users
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal, engine
from models import Base, User, Question, Submission, TestMetadata

def clean_database():
    """Delete all users, submissions, and questions"""
    db = SessionLocal()
    
    try:
        print("🗑️  Cleaning database...")
        
        # Delete in correct order (respect foreign keys)
        submissions_deleted = db.query(Submission).delete()
        print(f"   ✓ Deleted {submissions_deleted} submissions")
        
        questions_deleted = db.query(Question).delete()
        print(f"   ✓ Deleted {questions_deleted} questions")
        
        users_deleted = db.query(User).delete()
        print(f"   ✓ Deleted {users_deleted} users")
        
        # Commit changes
        db.commit()
        print("\n✅ Database cleaned successfully!")
        
        # Show remaining test metadata
        tests = db.query(TestMetadata).all()
        print(f"\n📋 Test metadata preserved: {len(tests)} tests")
        for test in tests:
            print(f"   - {test.title}")
        
    except Exception as e:
        print(f"\n❌ Error cleaning database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    clean_database()
