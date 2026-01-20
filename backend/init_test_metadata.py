from core.database import SessionLocal
from models import TestMetadata

def init_test():
    db = SessionLocal()
    
    # 1. Check if the test already exists to avoid duplicates
    existing_test = db.query(TestMetadata).filter(TestMetadata.title == "Know Yourself").first()
    
    if existing_test:
        print(f"✅ 'Know Yourself' test already exists (ID: {existing_test.id}). Skipping.")
    else:
        # 2. Create the 'Container' Test
        new_test = TestMetadata(
            title="Know Yourself",
            description="Take this comprehensive assessment to evaluate your skills and readiness for the industry.",
            icon_name="BookOpen",   # This matches your Dashboard logic
            category="General",
            duration_minutes=30,
            is_active=True
        )
        
        db.add(new_test)
        db.commit()
        db.refresh(new_test)
        print(f"🎉 Successfully created 'Know Yourself' test with ID: {new_test.id}")

    db.close()

if __name__ == "__main__":
    init_test()