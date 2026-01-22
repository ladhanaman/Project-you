# routers/tests.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from models import User, TestMetadata, Question, Submission
from schemas import TestMetadataResponse, QuestionResponse, QuestionsResponse
from core.security import get_current_user
from core.cache import cache_get, cache_set
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tests", tags=["Tests"])


@router.get("", response_model=List[TestMetadataResponse])
def get_tests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all available tests for the dashboard
    
    Protected endpoint - requires authentication
    Includes user's latest submission ID if they've completed the test
    """
    
    # Fetch active tests
    tests = db.query(TestMetadata).filter(TestMetadata.is_active == True).all()
    
    result = []
    for test in tests:
        # Check if user has a submission for this test
        latest_submission = db.query(Submission).filter(
            Submission.user_id == current_user.id,
            Submission.test_id == test.id
        ).order_by(Submission.created_at.desc()).first()
        
        # Calculate total questions for this test
        total_questions = db.query(Question).filter(Question.test_id == test.id).count()
        
        # Create response with submission ID if exists
        test_data = {
            'id': test.id,
            'title': test.title,
            'description': test.description,
            'duration_minutes': test.duration_minutes,
            'total_questions': total_questions,
            'created_at': test.created_at,
            'user_submission_id': latest_submission.id if latest_submission else None
        }
        result.append(TestMetadataResponse(**test_data))
    
    return result


@router.get("/{test_id}/questions", response_model=QuestionsResponse)
def get_test_questions(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all questions for a specific test as a flat array
    
    Protected endpoint - requires authentication
    Cached for 1 hour
    """
    # Try cache first (v2 cache key for new response format)
    cache_key = f"tests:{test_id}:questions:v2"
    cached_questions = cache_get(cache_key)
    if cached_questions:
        logger.debug(f"Returning cached questions for test {test_id}")
        return cached_questions
    
    # Verify test exists
    test = db.query(TestMetadata).filter(TestMetadata.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Fetch all questions for this test
    all_questions = db.query(Question).filter(Question.test_id == test_id).all()
    
    # Return as flat array
    result = QuestionsResponse(
        questions=[QuestionResponse.model_validate(q) for q in all_questions]
    )
    
    # Cache for 1 hour
    cache_set(cache_key, result.model_dump(), ttl=3600)
    
    return result
