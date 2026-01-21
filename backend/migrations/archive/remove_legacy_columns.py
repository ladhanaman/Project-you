"""
Database Migration: Remove Legacy Columns

This migration removes unused and legacy columns from the database schema.

Tables affected:
- test_metadata: Remove 'category'
- questions: Remove 'section', 'category'
- submissions: Remove 19 legacy columns

CRITICAL: This migration archives data before deletion.
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")

def archive_data(conn):
    """Archive data before deletion"""
    print("📦 Archiving data before deletion...")
    
    # Archive test_metadata.category
    try:
        result = conn.execute(text("""
            SELECT id, category FROM test_metadata WHERE category IS NOT NULL
        """))
        archived = [{"id": row[0], "category": row[1]} for row in result]
        if archived:
            with open(f'archive_test_metadata_category_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
                json.dump(archived, f, indent=2)
            print(f"  ✓ Archived {len(archived)} test_metadata.category values")
    except Exception as e:
        print(f"  ✗ Failed to archive test_metadata.category: {e}")
    
    # Archive questions section/category
    try:
        result = conn.execute(text("""
            SELECT id, section, category FROM questions 
            WHERE section IS NOT NULL OR category IS NOT NULL
        """))
        archived = [{"id": row[0], "section": row[1], "category": row[2]} for row in result]
        if archived:
            with open(f'archive_questions_fields_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
                json.dump(archived, f, indent=2)
            print(f"  ✓ Archived {len(archived)} question section/category values")
    except Exception as e:
        print(f"  ✗ Failed to archive questions: {e}")
    
    # Archive submissions legacy data
    try:
        result = conn.execute(text("""
            SELECT 
                id, candidate_email, candidate_name, fundamentals_score, 
                applied_score, industry_score, total_score, question_flags,
                marked_for_review, executive_summary, missed_tags,
                fundamentals_insights, applied_insights, industry_insights,
                skills_gap, career_recommendations, interview_prep_technical,
                interview_prep_behavioral, project_recommendations, role_fit
            FROM submissions
        """))
        
        columns = [
            'id', 'candidate_email', 'candidate_name', 'fundamentals_score',
            'applied_score', 'industry_score', 'total_score', 'question_flags',
            'marked_for_review', 'executive_summary', 'missed_tags',
            'fundamentals_insights', 'applied_insights', 'industry_insights',
            'skills_gap', 'career_recommendations', 'interview_prep_technical',
            'interview_prep_behavioral', 'project_recommendations', 'role_fit'
        ]
        
        archived = [dict(zip(columns, row)) for row in result]
        if archived:
            with open(f'archive_submissions_legacy_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
                json.dump(archived, f, indent=2, default=str)
            print(f"  ✓ Archived {len(archived)} submission legacy data records")
    except Exception as e:
        print(f"  ✗ Failed to archive submissions: {e}")


def drop_columns(conn):
    """Drop columns from tables"""
    print("\n🗑️  Dropping columns...")
    
    migrations = [
        # test_metadata
        ("test_metadata", "category"),
        
        # questions
        ("questions", "section"),
        ("questions", "category"),
        
        # submissions (19 columns)
        ("submissions", "candidate_email"),
        ("submissions", "candidate_name"),
        ("submissions", "fundamentals_score"),
        ("submissions", "applied_score"),
        ("submissions", "industry_score"),
        ("submissions", "total_score"),
        ("submissions", "question_flags"),
        ("submissions", "marked_for_review"),
        ("submissions", "executive_summary"),
        ("submissions", "missed_tags"),
        ("submissions", "fundamentals_insights"),
        ("submissions", "applied_insights"),
        ("submissions", "industry_insights"),
        ("submissions", "skills_gap"),
        ("submissions", "career_recommendations"),
        ("submissions", "interview_prep_technical"),
        ("submissions", "interview_prep_behavioral"),
        ("submissions", "project_recommendations"),
        ("submissions", "role_fit"),
    ]
    
    success_count = 0
    failed = []
    
    for table, column in migrations:
        try:
            conn.execute(text(f"ALTER TABLE {table} DROP COLUMN IF EXISTS {column}"))
            print(f"  ✓ Dropped {table}.{column}")
            success_count += 1
        except Exception as e:
            print(f"  ✗ Failed to drop {table}.{column}: {e}")
            failed.append((table, column))
    
    print(f"\n📊 Summary: {success_count} columns dropped successfully")
    if failed:
        print(f"⚠️  {len(failed)} columns failed:")
        for table, column in failed:
            print(f"   - {table}.{column}")
    
    return success_count, failed


def run_migration():
    """Execute the migration"""
    print("=" * 60)
    print("DATABASE MIGRATION: Remove Legacy Columns")
    print("=" * 60)
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Step 1: Archive
        archive_data(conn)
        
        # Step 2: Drop columns
        success_count, failed = drop_columns(conn)
        
        # Commit changes
        conn.commit()
        
        print("\n" + "=" * 60)
        if not failed:
            print("✅ Migration completed successfully!")
        else:
            print("⚠️  Migration completed with errors")
        print("=" * 60)
        
        return success_count, failed


if __name__ == "__main__":
    import sys
    
    print("\n⚠️  WARNING: This migration will permanently delete columns!")
    print("   Archives will be created before deletion.\n")
    
    response = input("Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Migration cancelled")
        sys.exit(0)
    
    success_count, failed = run_migration()
    sys.exit(0 if not failed else 1)
