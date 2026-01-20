# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Enum, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from core.database import Base

class CategoryEnum(str, enum.Enum):
    FUNDAMENTALS = "Fundamentals"
    APPLIED = "Applied Knowledge"
    INDUSTRY = "Industry Orientation"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)
    
    # Security: Token versioning for logout/revocation support
    token_version = Column(Integer, default=0, nullable=False)
    
    # --- NEW ONBOARDING FIELDS ---
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)         # <--- NEW
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    occupation = Column(String(100), nullable=True)
    education = Column(String(100), nullable=True)     # <--- NEW
    industry_domain = Column(String(100), nullable=True) # <--- NEW
    hobbies = Column(String(255), nullable=True)

    # --- OLD ONBOARDING FIELDS (Kept to prevent DB errors, but unused) ---
    college = Column(String(255), nullable=True)
    course = Column(String(255), nullable=True)
    year_of_study = Column(String(50), nullable=True)
    phone_number = Column(String(20), nullable=True)
    specialization = Column(String(255), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    
    onboarding_completed = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submissions = relationship("Submission", back_populates="user")

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"

    reflections = relationship("DailyReflection", back_populates="user")


class TestMetadata(Base):
    __tablename__ = "test_metadata"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    icon_name = Column(String(50), nullable=False)
    category = Column(String(100), nullable=False)
    duration_minutes = Column(Integer, default=30)  # Test duration in minutes
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = relationship("Question", back_populates="test")
    submissions = relationship("Submission", back_populates="test")

    def __repr__(self):
        return f"<TestMetadata id={self.id} title={self.title}>"


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("test_metadata.id"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    option_1 = Column(String(255), nullable=False)
    option_2 = Column(String(255), nullable=False)
    option_3 = Column(String(255), nullable=False)
    option_4 = Column(String(255), nullable=False)
    
    # Weights for each option
    weight_1 = Column(Integer, default=0, nullable=False)
    weight_2 = Column(Integer, default=0, nullable=False)
    weight_3 = Column(Integer, default=0, nullable=False)
    weight_4 = Column(Integer, default=0, nullable=False)
    
    # Metadata
    category = Column(Enum(CategoryEnum), nullable=False, index=True)
    tags = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    test = relationship("TestMetadata", back_populates="questions")

    def __repr__(self):
        return f"<Question id={self.id} category={self.category}>"

    def get_all_options(self):
        """Return all options in order"""
        return [self.option_1, self.option_2, self.option_3, self.option_4]

    def get_weight(self, option_index: int) -> int:
        """Get weight for a given option index (1-4)"""
        weights = [self.weight_1, self.weight_2, self.weight_3, self.weight_4]
        if 1 <= option_index <= 4:
            return weights[option_index - 1]
        return 0


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    test_id = Column(Integer, ForeignKey("test_metadata.id"), nullable=False, index=True)
    
    # Legacy candidate info (kept for backward compatibility with existing reports)
    candidate_name = Column(String(255), nullable=True)
    candidate_email = Column(String(255), nullable=True)
    candidate_whatsapp = Column(String(20), nullable=True)
    candidate_education = Column(String(100), nullable=True)
    candidate_college = Column(String(255), nullable=True)
    
    # Scores
    fundamentals_score = Column(Integer, default=0)
    applied_score = Column(Integer, default=0)
    industry_score = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    
    # Answers & Metadata
    answers = Column(JSON, nullable=False)  # {question_id: selected_answer}
    marked_for_review = Column(JSON, default=list)
    
    # AI Insights
    missed_tags = Column(JSON, default=list)
    executive_summary = Column(Text, nullable=True)

    # Retry metadata (separate from missed_tags to prevent data collision)
    retry_metadata = Column(JSON, default=dict)

    # New per-section insights columns
    fundamentals_insights = Column(JSON, default=dict)
    applied_insights = Column(JSON, default=dict)
    industry_insights = Column(JSON, default=dict)

    # Legacy (optional/kept for compatibility)
    strengths = Column(JSON, default=list)
    areas_for_improvement = Column(JSON, default=list)

    learning_plan_weeks = Column(JSON, default=list)
    industry_readiness_level = Column(String(100), nullable=True)
    readiness_level_justification = Column(Text, nullable=True)
    interview_prep_technical = Column(JSON, default=list)
    interview_prep_behavioral = Column(JSON, default=list)
    project_recommendations = Column(JSON, default=list)
    role_fit = Column(Text, nullable=True)
    
    # Report Generation
    pdf_generated = Column(String(255), nullable=True)
    report_status = Column(String(50), default="pending")
    ai_generated = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="submissions")
    test = relationship("TestMetadata", back_populates="submissions")
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Submission id={self.id} email={self.candidate_email} score={self.total_score}>"

class DailyReflection(Base):
    __tablename__ = "daily_reflections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    day_number = Column(Integer, nullable=False)  # 1 to 7
    answer = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="reflections")