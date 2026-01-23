#!/usr/bin/env python3
"""
Flush all user data from the database

This script deletes:
- All daily reflections
- All reflection sessions
- All submissions (test results and reports)
- All users

This script preserves:
- Test metadata
- Questions

Usage:
    python flush_user_data.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import SessionLocal
from models import User, Submission, DailyReflection, ReflectionSession

def flush_user_data():
    """Delete all user-related data from the database"""
    print("=" * 60)
    print("FLUSHING USER DATA FROM DATABASE")
    print("=" * 60)
    print("\n⚠️  WARNING: This will delete ALL user-related data!")
    print("   - Daily reflections")
    print("   - Reflection sessions")
    print("   - Submissions (test results)")
    print("   - Users")
    print("\n✓ This will preserve:")
    print("   - Test metadata")
    print("   - Questions\n")
    
    # Ask for confirmation
    response = input("Type 'YES' to confirm deletion: ")
    if response != "YES":
        print("\n❌ Operation cancelled.")
        return
    
    db = SessionLocal()
    
    try:
        print("\n🗑️  Starting deletion...\n")
        
        # Delete in order of dependencies (child tables first)
        
        # 1. Daily reflections
        daily_count = db.query(DailyReflection).count()
        db.query(DailyReflection).delete()
        print(f"   ✓ Deleted {daily_count} daily reflections")
        
        # 2. Reflection sessions
        session_count = db.query(ReflectionSession).count()
        db.query(ReflectionSession).delete()
        print(f"   ✓ Deleted {session_count} reflection sessions")
        
        # 3. Submissions
        submission_count = db.query(Submission).count()
        db.query(Submission).delete()
        print(f"   ✓ Deleted {submission_count} submissions")
        
        # 4. Users
        user_count = db.query(User).count()
        db.query(User).delete()
        print(f"   ✓ Deleted {user_count} users")
        
        # Commit all deletions
        db.commit()
        
        print("\n✅ Successfully flushed all user data!")
        print(f"\nSummary:")
        print(f"   - {user_count} users deleted")
        print(f"   - {submission_count} submissions deleted")
        print(f"   - {session_count} reflection sessions deleted")
        print(f"   - {daily_count} daily reflections deleted")
        print("\n✓ Database is now fresh and ready for new data!\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error occurred: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    flush_user_data()
