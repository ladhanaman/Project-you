# models.py
from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, ForeignKey, DateTime, Date, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from core.database import Base

# CategoryEnum removed - PRI system no longer uses categories


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

    # Old onboarding fields removed - no longer needed
    
    onboarding_completed = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submissions = relationship("Submission", back_populates="user")

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"

    reflections = relationship("DailyReflection", back_populates="user")
    reflection_sessions = relationship("ReflectionSession", back_populates="user")


class TestMetadata(Base):
    __tablename__ = "test_metadata"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    icon_name = Column(String(50), nullable=False)
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
    
    # Five answer options (PRI assessment uses 5 options)
    option_1 = Column(String(255), nullable=False)
    option_2 = Column(String(255), nullable=False)
    option_3 = Column(String(255), nullable=False)
    option_4 = Column(String(255), nullable=False)
    option_5 = Column(String(255), nullable=True)  # Nullable for backward compatibility
    
    # Legacy weights (keep for backward compatibility with old tests)
    weight_1 = Column(Integer, default=0, nullable=False)
    weight_2 = Column(Integer, default=0, nullable=False)
    weight_3 = Column(Integer, default=0, nullable=False)
    weight_4 = Column(Integer, default=0, nullable=False)
    weight_5 = Column(Integer, default=0, nullable=False)
    
    # PRI Weights for Purpose (P) - Float values 0.0-1.0
    weight_p_1 = Column(Integer, default=0, nullable=False)  # Using Integer for now, will be Float
    weight_p_2 = Column(Integer, default=0, nullable=False)
    weight_p_3 = Column(Integer, default=0, nullable=False)
    weight_p_4 = Column(Integer, default=0, nullable=False)
    weight_p_5 = Column(Integer, default=0, nullable=False)
    
    # PRI Weights for Relevance (R) - Float values 0.0-1.0
    weight_r_1 = Column(Integer, default=0, nullable=False)
    weight_r_2 = Column(Integer, default=0, nullable=False)
    weight_r_3 = Column(Integer, default=0, nullable=False)
    weight_r_4 = Column(Integer, default=0, nullable=False)
    weight_r_5 = Column(Integer, default=0, nullable=False)
    
    # PRI Weights for Identity (I) - Float values 0.0-1.0
    weight_i_1 = Column(Integer, default=0, nullable=False)
    weight_i_2 = Column(Integer, default=0, nullable=False)
    weight_i_3 = Column(Integer, default=0, nullable=False)
    weight_i_4 = Column(Integer, default=0, nullable=False)
    weight_i_5 = Column(Integer, default=0, nullable=False)
    
    # Metadata
    tags = Column(JSON, default=list)  # General question-level tags
    
    # Option-wise tags (for signal tracking per option)
    tags_option_1 = Column(JSON, default=list)
    tags_option_2 = Column(JSON, default=list)
    tags_option_3 = Column(JSON, default=list)
    tags_option_4 = Column(JSON, default=list)
    tags_option_5 = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    test = relationship("TestMetadata", back_populates="questions")

    def __repr__(self):
        return f"<Question id={self.id} category={self.category}>"

    def get_all_options(self):
        """Return all options in order"""
        options = [self.option_1, self.option_2, self.option_3, self.option_4]
        if self.option_5:
            options.append(self.option_5)
        return options

    # get_weight() removed - use get_pri_weights() instead
    
    def get_pri_weights(self, option_index: int) -> dict:
        """Get P, R, I weights for a given option (1-5)"""
        p_weights = [self.weight_p_1, self.weight_p_2, self.weight_p_3, self.weight_p_4, self.weight_p_5]
        r_weights = [self.weight_r_1, self.weight_r_2, self.weight_r_3, self.weight_r_4, self.weight_r_5]
        i_weights = [self.weight_i_1, self.weight_i_2, self.weight_i_3, self.weight_i_4, self.weight_i_5]
        
        if 1 <= option_index <= 5:
            idx = option_index - 1
            return {
                'P': p_weights[idx],
                'R': r_weights[idx],
                'I': i_weights[idx]
            }
        return {'P': 0, 'R': 0, 'I': 0}
    
    def get_option_tags(self, option_index: int) -> list:
        """Get tags for a specific option (1-5)"""
        option_tags = [
            self.tags_option_1 or [],
            self.tags_option_2 or [],
            self.tags_option_3 or [],
            self.tags_option_4 or [],
            self.tags_option_5 or []
        ]
        
        if 1 <= option_index <= 5:
            return option_tags[option_index - 1]
        return []


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    test_id = Column(Integer, ForeignKey("test_metadata.id"), nullable=False, index=True)
    
    # Candidate info moved to user relationship
    
    # PRI Scores (0.0-1.0 scale)
    purpose_score = Column(Float, default=0.0, nullable=True)
    relevance_score = Column(Float, default=0.0, nullable=True)
    identity_score = Column(Float, default=0.0, nullable=True)
    
    # PRI Levels (H/M/L)
    purpose_level = Column(String(1), nullable=True)  # H, M, or L
    relevance_level = Column(String(1), nullable=True)
    identity_level = Column(String(1), nullable=True)
    
    # Archetype Classification
    archetype = Column(String(100), nullable=True)  # Internal base archetype
    display_archetype = Column(String(100), nullable=True)  # Display archetype
    final_archetype = Column(String(100), nullable=True)  # Age-variant final archetype
    
    # Signals/Tags (PRI-specific)
    positive_tags = Column(JSON, default=list)
    negative_tags = Column(JSON, default=list)
    
    # PRI Report (markdown format)
    pri_report_md = Column(Text, nullable=True)
    
    # Answers & Metadata
    answers = Column(JSON, nullable=False)  # {question_id: selected_answer}
    
    # Report Generation
    pdf_generated = Column(String(255), nullable=True)
    report_status = Column(String(50), default="pending")
    ai_generated = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="submissions")
    test = relationship("TestMetadata", back_populates="submissions")
    reflection_session = relationship("ReflectionSession", back_populates="submission", uselist=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Submission id={self.id} user_id={self.user_id} test_id={self.test_id}>"

class DailyReflection(Base):
    __tablename__ = "daily_reflections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    day_number = Column(Integer, nullable=False)  # 1 to 7
    answer = Column(Text, nullable=False)
    
    # Enhanced fields for structured reflection sessions
    content_id = Column(String(50), nullable=True)  # e.g., "REFLECT_D1"
    day_title = Column(String(255), nullable=True)
    unlock_day = Column(Integer, nullable=True)
    unlock_time_local = Column(String(10), nullable=True)
    questions = Column(JSON, default=list)  # Array of question strings
    micro_action = Column(Text, nullable=True)
    notice_cue = Column(Text, nullable=True)
    completion_check = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="reflections")


class ReflectionSession(Base):
    __tablename__ = "reflection_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    session_title = Column(String(255), nullable=False)
    final_archetype = Column(String(100), nullable=False)
    
    # Themes
    primary_theme_dimension = Column(String(1), nullable=False)  # P, R, or I
    primary_theme_reason = Column(Text, nullable=False)
    secondary_theme_dimension = Column(String(1), nullable=False)
    secondary_theme_reason = Column(Text, nullable=False)
    
    unlock_default_time = Column(String(10), default="09:00")
    
    # Full session JSON
    session_data = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    submission = relationship("Submission", back_populates="reflection_session")
    user = relationship("User", back_populates="reflection_sessions")