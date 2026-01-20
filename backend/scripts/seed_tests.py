#!/usr/bin/env python3
"""Seed tests into the database"""
import sys
sys.path.insert(0, '..')

from core.database import SessionLocal, engine, Base
from models import TestMetadata

# Create tables
Base.metadata.create_all(bind=engine)

TESTS = [
    {
        "title": "IOT Readiness Assessment",
        "description": "Embedded systems, IoT protocols, and hardware fundamentals",
        "icon_name": "Cpu",
        "category": "Embedded Systems & IoT",
    },
    {
        "title": "Computer Science Fundamentals",
        "description": "Data structures, algorithms, and software engineering",
        "icon_name": "Code",
        "category": "Software Development",
    },
]

def main():
    db = SessionLocal()
    try:
        if db.query(TestMetadata).count() > 0:
            print("Tests already exist. Skipping.")
            return
        
        for t in TESTS:
            db.add(TestMetadata(**t, is_active=True))
        
        db.commit()
        print(f"Seeded {len(TESTS)} tests.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
