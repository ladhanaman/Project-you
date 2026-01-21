"""
Fix existing PRI score data after migration.

The scores were stored as integers (12, 20, 18) but should be floats (0.12, 0.20, 0.18).
This script divides all existing scores by 100 to correct them.
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")

def fix_existing_scores():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("Fixing existing PRI scores...")
        
        # Update all existing scores by dividing by 100
        fix_sql = """
        UPDATE submissions
        SET 
            purpose_score = purpose_score / 100.0,
            relevance_score = relevance_score / 100.0,
            identity_score = identity_score / 100.0
        WHERE 
            purpose_score > 1.0 OR 
            relevance_score > 1.0 OR 
            identity_score > 1.0;
        """
        
        result = conn.execute(text(fix_sql))
        conn.commit()
        
        print(f"✓ Fixed {result.rowcount} submissions")
        
        # Verify the fix
        verify_sql = "SELECT id, purpose_score, relevance_score, identity_score FROM submissions ORDER BY id DESC LIMIT 5;"
        results = conn.execute(text(verify_sql))
        
        print("\nVerification (latest 5 submissions):")
        for row in results:
            print(f"  ID {row[0]}: P={row[1]:.3f}, R={row[2]:.3f}, I={row[3]:.3f}")
        
        print("\n✅ Data fix completed successfully!")

if __name__ == "__main__":
    fix_existing_scores()
