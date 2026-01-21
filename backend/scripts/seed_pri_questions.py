#!/usr/bin/env python3
"""Seed PRI questions into the database"""
import sys
import json
sys.path.insert(0, '..')

from core.database import SessionLocal, engine, Base
from models import Question, TestMetadata, CategoryEnum

# Create tables
Base.metadata.create_all(bind=engine)

def seed_pri_questions(json_file_path):
    """
    Seed questions from JSON file
    
    Args:
        json_file_path: Path to JSON file with questions
    """
    db = SessionLocal()
    
    try:
        # Load questions from JSON
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        # Get or verify the "Know Yourself" test exists
        test = db.query(TestMetadata).filter(
            TestMetadata.title == data.get('test_title', 'Know Yourself')
        ).first()
        
        if not test:
            print("❌ Error: 'Know Yourself' test not found in database.")
            print("   Run: python init_test_metadata.py first")
            return
        
        test_id = data.get('test_id', test.id)
        
        # Check if questions already exist for this test
        existing_count = db.query(Question).filter(Question.test_id == test_id).count()
        if existing_count > 0:
            print(f"⚠️  Warning: {existing_count} questions already exist for test ID {test_id}")
            response = input("Delete existing questions and reseed? (yes/no): ")
            if response.lower() == 'yes':
                db.query(Question).filter(Question.test_id == test_id).delete()
                db.commit()
                print("✅ Deleted existing questions")
            else:
                print("❌ Cancelled. Exiting without changes.")
                return
        
        # Insert questions
        questions = data['questions']
        print(f"\n🌱 Seeding {len(questions)} questions...")
        
        for idx, q in enumerate(questions, 1):
            question = Question(
                test_id=test_id,
                question_text=q['question_text'],
                category=CategoryEnum[q['category']],
                option_1=q['option_1'],
                option_2=q['option_2'],
                option_3=q['option_3'],
                option_4=q['option_4'],
                option_5=q['option_5'],
                weight_p_1=q['weight_p_1'],
                weight_p_2=q['weight_p_2'],
                weight_p_3=q['weight_p_3'],
                weight_p_4=q['weight_p_4'],
                weight_p_5=q['weight_p_5'],
                weight_r_1=q['weight_r_1'],
                weight_r_2=q['weight_r_2'],
                weight_r_3=q['weight_r_3'],
                weight_r_4=q['weight_r_4'],
                weight_r_5=q['weight_r_5'],
                weight_i_1=q['weight_i_1'],
                weight_i_2=q['weight_i_2'],
                weight_i_3=q['weight_i_3'],
                weight_i_4=q['weight_i_4'],
                weight_i_5=q['weight_i_5'],
                tags_option_1=q.get('tags_option_1', []),
                tags_option_2=q.get('tags_option_2', []),
                tags_option_3=q.get('tags_option_3', []),
                tags_option_4=q.get('tags_option_4', []),
                tags_option_5=q.get('tags_option_5', []),
                tags=[]  # General tags not used for PRI
            )
            db.add(question)
            print(f"  ✓ Added question {idx}: {q['question_text'][:50]}...")
        
        db.commit()
        print(f"\n🎉 Successfully seeded {len(questions)} PRI questions!")
        print(f"   Test ID: {test_id}")
        print(f"   Test: {test.title}")
        
    except FileNotFoundError:
        print(f"❌ Error: File not found: {json_file_path}")
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python seed_pri_questions.py <path_to_questions.json>")
        print("\nExample:")
        print("  python seed_pri_questions.py pri_questions.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    seed_pri_questions(json_file)
