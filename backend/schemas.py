# schemas.py
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Dict, Optional, Any
from enum import Enum
import re
import bleach

# CategoryEnum removed - PRI system no longer uses categories



# ============================================================================
# AUTHENTICATION SCHEMAS
# ============================================================================

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    
    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """Validate password meets complexity requirements"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v
    
    @field_validator('full_name')
    @classmethod
    def sanitize_full_name(cls, v: str) -> str:
        """Strip HTML tags from full name"""
        return bleach.clean(v, strip=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class OnboardingData(BaseModel):
    """User onboarding information - UPDATED"""
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    date_of_birth: date
    gender: str = Field(pattern="^(Male|Female)$")     # <--- NEW
    city: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=500)
    occupation: str = Field(min_length=1, max_length=100)
    education: str = Field(min_length=1, max_length=100)      # <--- NEW
    industry_domain: str = Field(min_length=1, max_length=100) # <--- NEW
    hobbies: Optional[str] = Field(None, max_length=255)
    
    @field_validator('first_name', 'last_name', 'city', 'address', 'occupation', 'education', 'industry_domain', 'hobbies')
    @classmethod
    def sanitize_text_fields(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return bleach.clean(v, strip=True)


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    email_verified: bool = False
    
    # New Onboarding fields
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None           # <--- NEW
    city: Optional[str] = None
    address: Optional[str] = None
    occupation: Optional[str] = None
    education: Optional[str] = None        # <--- NEW
    industry_domain: Optional[str] = None  # <--- NEW
    hobbies: Optional[str] = None
    
    # Old fields kept for backward compatibility (optional)
    college: Optional[str] = None
    course: Optional[str] = None
    year_of_study: Optional[str] = None
    
    onboarding_completed: bool = False
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse


# ============================================================================
# TEST METADATA SCHEMAS
# ============================================================================

class TestMetadataResponse(BaseModel):
    """Test metadata for listing (no questions)"""
    id: int
    title: str
    description: Optional[str] = None
    duration_minutes: Optional[int] = 30
    total_questions: int
    created_at: datetime
    user_submission_id: Optional[int] = None  # ID of user's latest submission if exists

    class Config:
        from_attributes = True


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class CandidateInfo(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    whatsapp: str = Field(..., pattern=r"^\d{10}$")
    education: str
    college: str = Field(..., min_length=1, max_length=255)


class AnswerSubmission(BaseModel):
    question_id: int
    selected_answer: str


class AssessmentSubmission(BaseModel):
    test_id: int
    answers: List[AnswerSubmission]

    class Config:
        json_schema_extra = {
            "example": {
                "test_id": 1,
                "answers": [
                    {"question_id": 1, "selected_answer": "O(log n)"},
                    {"question_id": 2, "selected_answer": "Stack"}
                ]
            }
        }


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class QuestionResponse(BaseModel):
    id: int
    question_text: str
    option_1: str
    option_2: str
    option_3: str
    option_4: str
    option_5: Optional[str] = None  # ✅ CRITICAL FIX: Added 5th option
    tags: List[str]

    class Config:
        from_attributes = True


class QuestionsGroupedResponse(BaseModel):
    fundamentals: List[QuestionResponse]
    applied: List[QuestionResponse]
    industry: List[QuestionResponse]


class SectionInsight(BaseModel):
    opportunities: List[str] = Field(default_factory=list, description="List of 3-4 strengths/achievements in this section")
    work_towards: List[str] = Field(default_factory=list, description="List of 3-4 areas to improve/study in this section")

class SubmissionResponse(BaseModel):
    id: int
    user_id: int
    test_id: int
    report_status: str
    pdf_generated: Optional[str]
    ai_generated: bool = False
    
    # PRI System Fields
    purpose_score: Optional[float] = None
    relevance_score: Optional[float] = None
    identity_score: Optional[float] = None
    purpose_level: Optional[str] = None
    relevance_level: Optional[str] = None
    identity_level: Optional[str] = None
    archetype: Optional[str] = None
    display_archetype: Optional[str] = None
    final_archetype: Optional[str] = None
    pri_report_md: Optional[str] = None
    
    created_at: datetime

    class Config:
        from_attributes = True


class ScoringResponse(BaseModel):
    submission_id: int
    status: str = "Processing..."
    message: str = "Your assessment has been submitted. We're generating your personalized report."

    class Config:
        json_schema_extra = {
            "example": {
                "submission_id": 42,
                "status": "Processing...",
                "message": "Your assessment has been submitted. We're generating your personalized report."
            }
        }


class ErrorResponse(BaseModel):
    detail: str
    error_code: str
    timestamp: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid answer provided",
                "error_code": "INVALID_ANSWER",
                "timestamp": "2025-01-13T10:30:00Z"
            }
        }


# ============================================================================
# AI INSIGHT SCHEMAS (for LLM output validation)
# ============================================================================

class LearningWeek(BaseModel):
    """Enhanced weekly learning plan with deliverables and validation"""
    focus_area: str = Field(description="Week theme derived from weak/critical tags")
    tasks: str = Field(description="4-5 concrete tasks for this week")
    deliverables: Optional[List[str]] = Field(default_factory=list, description="2-3 tangible artifacts")
    validation: Optional[List[str]] = Field(default_factory=list, description="1-2 verification checks")
    time_budget_hours: Optional[str] = Field(default=None, description="Weekly time estimate")
    expected_outcome: str = Field(description="Measurable improvement")

class ProjectRecommendation(BaseModel):
    """Structured project recommendation"""
    title: str = Field(description="Project name")
    description: str = Field(description="20-30 word description")
    addresses_tags: Optional[List[str]] = Field(default_factory=list, description="Tags this project addresses")
    time_estimate: Optional[str] = Field(default=None, description="Estimated time to complete")

class RoleFit(BaseModel):
    """Job role recommendation with description"""
    job_title: str = Field(description="Role title")
    role_description: str = Field(description="Day-to-day responsibilities and why candidate aligns")

class InsightResponse(BaseModel):
    """Pydantic model for ensuring structured LLM output with flexible validation"""
    executive_summary: str = Field(default="Summary not available", description="2-3 sentences summarizing readiness")

    # Per-section insights
    fundamentals_insights: SectionInsight = Field(description="Insights for Fundamentals section")
    applied_insights: SectionInsight = Field(description="Insights for Applied Knowledge section")
    industry_insights: SectionInsight = Field(description="Insights for Industry Orientation section")

    # Enhanced 4-week learning plan
    learning_plan_weeks: List[LearningWeek] = Field(default_factory=list, description="4-week learning plan with deliverables and validation")
    
    # Readiness level
    industry_readiness_level: str = Field(default="Foundation Level", description="Readiness level")
    readiness_level_justification: str = Field(default="", description="Justification for the level")
    
    # Interview prep (optional)
    interview_prep_technical: Optional[List[str]] = Field(default_factory=list, description="Technical topics to prepare")
    interview_prep_behavioral: Optional[List[str]] = Field(default_factory=list, description="Behavioral areas to prepare")
    
    # Enhanced project recommendations
    project_recommendations: List[ProjectRecommendation] = Field(default_factory=list, description="2-3 recommended projects")
    
    # Enhanced role fit
    role_fit: List[RoleFit] = Field(default_factory=list, description="2-4 job role recommendations")

    class Config:
        extra = "ignore"  # Ignore extra fields from LLM
        json_schema_extra = {
            "example": {
                "executive_summary": "John demonstrates a solid foundation...",
                "fundamentals_insights": {
                    "opportunities": ["Good understanding of GPIO"],
                    "work_towards": ["Study NVIC", "Deep dive into timers"]
                },
                "applied_insights": {
                    "opportunities": ["Strong C basics"],
                    "work_towards": ["Practice UART drivers"]
                },
                "industry_insights": {
                    "opportunities": ["Knows Git basics"],
                    "work_towards": ["Learn CI/CD"]
                },
                "learning_plan_weeks": [{
                    "focus_area": "Week 1: Core Foundations",
                    "tasks": "Study fundamentals, complete exercises",
                    "deliverables": ["Notes document", "Code exercises"],
                    "validation": ["Quiz completion", "Code review"],
                    "time_budget_hours": "10-12 hours",
                    "expected_outcome": "Solid foundation in basics"
                }],
                "industry_readiness_level": "Internship Ready",
                "readiness_level_justification": "Good basics but lacks...",
                "interview_prep_technical": ["Review HashMaps"],
                "interview_prep_behavioral": ["Prepare STAR stories"],
                "project_recommendations": [{
                    "title": "Task Manager App",
                    "description": "Build a full-stack task manager with auth",
                    "addresses_tags": ["api_design", "authentication"],
                    "time_estimate": "2-3 weeks"
                }],
                "role_fit": [{
                    "job_title": "Embedded Firmware Intern",
                    "role_description": "Work on firmware development, aligned with strong C skills"
                }]
            }
        }

class ReflectionCreate(BaseModel):
    day_number: int = Field(..., ge=1, le=7)
    answer: str = Field(..., min_length=1)

class ReflectionResponse(BaseModel):
    id: int
    day_number: int
    answer: str
    created_at: datetime

    class Config:
        from_attributes = True