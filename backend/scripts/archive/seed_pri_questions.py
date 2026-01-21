"""
Seed script for PRI Assessment Questions

Loads questions from you 1.json and seeds the database.
"""

import json
import os
from core.database import SessionLocal
from models import TestMetadata, Question
from sqlalchemy.exc import IntegrityError

def seed_pri_questions():
    """Seed PRI questions from you 1.json"""
    db = SessionLocal()
    
    try:
        # Load JSON file
        json_path = os.path.join(os.path.dirname(__file__), "you 1.json")
        
        if not os.path.exists(json_path):
            print(f"❌ File not found: {json_path}")
            return False
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        print(f"📄 Loaded {len(data.get('questions', []))} questions from you 1.json")
        
        # Create or get test metadata
        test = db.query(TestMetadata).filter(TestMetadata.id == 1).first()
        
        if not test:
            test = TestMetadata(
                id=1,
                title=data.get('test_title', 'Know Yourself'),
                description="A comprehensive PRI (Purpose, Relevance, Identity) assessment to help you understand yourself better.",
                icon_name="brain",
                duration_minutes=15,
                is_active=True
            )
            db.add(test)
            db.commit()
            print(f"✓ Created test: {test.title}")
        else:
            print(f"✓ Test already exists: {test.title}")
        
        # Delete existing questions for this test
        deleted_count = db.query(Question).filter(Question.test_id == 1).delete()
        db.commit()
        if deleted_count > 0:
            print(f"🗑️  Deleted {deleted_count} existing questions")
        
        # Insert questions
        questions_added = 0
        for q_data in data['questions']:
            question = Question(
                test_id=1,
                question_text=q_data['question_text'],
                option_1=q_data['option_1'],
                option_2=q_data['option_2'],
                option_3=q_data['option_3'],
                option_4=q_data['option_4'],
                option_5=q_data.get('option_5'),  # Optional
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
                tags=[]  # Empty for now
            )
            db.add(question)
            questions_added += 1
        
        db.commit()
        
        print(f"\n✅ Successfully seeded {questions_added} questions!")
        
        # Verify
        total_questions = db.query(Question).filter(Question.test_id == 1).count()
        print(f"📊 Verification: {total_questions} questions in database")
        
        # Sample check weights
        sample = db.query(Question).filter(Question.test_id == 1).first()
        if sample:
            print(f"\n🔍 Sample question weights:")
            print(f"   Q1 Option 1: P={sample.weight_p_1}, R={sample.weight_r_1}, I={sample.weight_i_1}")
            print(f"   Q1 Option 5: P={sample.weight_p_5}, R={sample.weight_r_5}, I={sample.weight_i_5}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding questions: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("PRI QUESTION SEEDING")
    print("=" * 60)
    
    success = seed_pri_questions()
    
    if success:
        print("\n✅ Seeding complete!")
    else:
        print("\n❌ Seeding failed!")
        exit(1)
