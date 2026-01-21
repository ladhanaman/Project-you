"""
Master Seeding Script - Combines test metadata and question seeding

Usage:
    python seed_database.py                    # Seed PRI questions from 'you 1.json'
    python seed_database.py --file custom.json # Seed from custom file
"""

import json
import sys
from pathlib import Path
from core.database import SessionLocal
from models import Question, TestMetadata

def seed_test_metadata(db):
    """Create or update test metadata"""
    test = db.query(TestMetadata).filter(TestMetadata.title == "Know Yourself").first()
    
    if not test:
        test = TestMetadata(
            title="Know Yourself",
            description="A comprehensive PRI (Purpose, Relevance, Identity) assessment to understand your professional alignment",
            duration_minutes=15,
            is_active=True
        )
        db.add(test)
        db.commit()
        print(f"✓ Created test: {test.title}")
    else:
        print(f"✓ Test already exists: {test.title}")
    
    return test

def seed_questions(db, test_id, json_file='you 1.json'):
    """Seed questions from JSON file"""
    
    # Load JSON
    json_path = Path(__file__).parent / json_file
    if not json_path.exists():
        json_path = Path(__file__).parent.parent / json_file
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    questions_data = data.get('questions', [])
    print(f"\n📄 Loaded {len(questions_data)} questions from {json_file}")
    
    # Delete existing questions for this test
    deleted = db.query(Question).filter(Question.test_id == test_id).delete()
    db.commit()
    print(f"🗑️  Deleted {deleted} existing questions")
    
    # Insert new questions
    for q_data in questions_data:
        question = Question(
            test_id=test_id,
            question_text=q_data['question'],
            option_1=q_data['options'][0],
            option_2=q_data['options'][1],
            option_3=q_data['options'][2],
            option_4=q_data['options'][3],
            option_5=q_data['options'][4] if len(q_data['options']) > 4 else None,
            
            # PRI weights
            weight_p_1=q_data.get('weight_p_1', 0),
            weight_p_2=q_data.get('weight_p_2', 0),
            weight_p_3=q_data.get('weight_p_3', 0),
            weight_p_4=q_data.get('weight_p_4', 0),
            weight_p_5=q_data.get('weight_p_5', 0),
            
            weight_r_1=q_data.get('weight_r_1', 0),
            weight_r_2=q_data.get('weight_r_2', 0),
            weight_r_3=q_data.get('weight_r_3', 0),
            weight_r_4=q_data.get('weight_r_4', 0),
            weight_r_5=q_data.get('weight_r_5', 0),
            
            weight_i_1=q_data.get('weight_i_1', 0),
            weight_i_2=q_data.get('weight_i_2', 0),
            weight_i_3=q_data.get('weight_i_3', 0),
            weight_i_4=q_data.get('weight_i_4', 0),
            weight_i_5=q_data.get('weight_i_5', 0),
            
            tags=q_data.get('tags', [])
        )
        db.add(question)
    
    db.commit()
    print(f"✅ Successfully seeded {len(questions_data)} questions!")
    
    # Verification
    count = db.query(Question).filter(Question.test_id == test_id).count()
    print(f"📊 Verification: {count} questions in database")
    
    # Show sample weights
    sample = db.query(Question).filter(Question.test_id == test_id).first()
    if sample:
        print(f"\n🔍 Sample question weights:")
        print(f"   Q1 Option 1: P={sample.weight_p_1}, R={sample.weight_r_1}, I={sample.weight_i_1}")
        print(f"   Q1 Option 5: P={sample.weight_p_5}, R={sample.weight_r_5}, I={sample.weight_i_5}")

def main():
    """Main seeding function"""
    print("=" * 60)
    print("DATABASE SEEDING - PRI Questions")
    print("=" * 60)
    
    # Parse args
    json_file = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != '--file' else 'you 1.json'
    if len(sys.argv) > 2 and sys.argv[1] == '--file':
        json_file = sys.argv[2]
    
    db = SessionLocal()
    
    try:
        # Step 1: Create test metadata
        test = seed_test_metadata(db)
        
        # Step 2: Seed questions
        seed_questions(db, test.id, json_file)
        
        print("\n✅ Seeding complete!\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Seeding failed: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
