#!/usr/bin/env python3
"""
Initialize database with updated schema
Creates all tables based on models.py
"""
import sys
sys.path.insert(0, '..')

from core.database import engine, Base
from models import User, TestMetadata, Question, Submission

def init_db():
    """Create all tables"""
    print("🔨 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    print("\n📋 Tables created:")
    print("   - users")
    print("   - test_metadata")
    print("   - questions (with weight_1, weight_2, weight_3, weight_4)")
    print("   - submissions")
    print("\n💡 Next steps:")
    print("   1. Run: python scripts/seed_tests.py")
    print("   2. Run: python scripts/seed_questions.py")

if __name__ == "__main__":
    init_db()
