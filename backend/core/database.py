# core/database.py - Database Connection
"""
SQLAlchemy database engine and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import settings

DATABASE_URL = settings.DATABASE_URL

# Configure engine with connection pooling for PostgreSQL
# Conservative pool settings: 10 base + 20 overflow = 30 max connections
# Adjust pool_size/max_overflow for high-traffic production if needed
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,  # Reduced from 50
        max_overflow=20,  # Reduced from 100
        pool_timeout=30,
        pool_recycle=3600,
        pool_pre_ping=True,
        echo=False
    )
else:
    # SQLite configuration (for development)
    engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
