from sqlalchemy import create_engine, inspect
from core.database import Base
from dotenv import load_dotenv
import os

load_dotenv()

def check_migrations():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found in .env")
        return

    engine = create_engine(database_url)
    inspector = inspect(engine)
    
    print("🔍 Checking Database Schema...")
    
    # 1. Check Questions Table
    columns = [c['name'] for c in inspector.get_columns('questions')]
    print(f"\nQuestions Table Columns ({len(columns)} total):")
    
    pri_cols = ['weight_p_1', 'weight_r_1', 'weight_i_1']
    option_tag_cols = ['tags_option_1', 'tags_option_2']
    
    missing_pri = [c for c in pri_cols if c not in columns]
    missing_tags = [c for c in option_tag_cols if c not in columns]
    
    if not missing_pri:
        print("✅ PRI Weight columns found")
    else:
        print(f"❌ Missing PRI columns: {missing_pri}")
        
    if not missing_tags:
        print("✅ Option Tag columns found")
    else:
        print(f"❌ Missing Option Tag columns: {missing_tags}")

    # 2. Check Submissions Table
    sub_columns = [c['name'] for c in inspector.get_columns('submissions')]
    print(f"\nSubmissions Table Columns ({len(sub_columns)} total):")
    if 'purpose_score' in sub_columns:
        print("✅ PRI Score columns found")
    else:
        print("❌ Missing PRI Score columns")

    # 3. Check Reflection Sessions Table
    tables = inspector.get_table_names()
    if 'reflection_sessions' in tables:
        print("\n✅ Reflection Sessions table found")
    else:
        print("\n❌ Reflection Sessions table MISSING")

if __name__ == "__main__":
    check_migrations()
