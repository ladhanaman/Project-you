# routers/tests.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from core.database import get_db
from models import User, TestMetadata, Question, Submission
from schemas import TestMetadataResponse, QuestionResponse, QuestionsResponse
from core.security import get_current_user
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
    
    # Subquery to count questions per test
    question_counts = db.query(
        Question.test_id,
        func.count(Question.id).label('count')
    ).group_by(Question.test_id).subquery()
    
    # Subquery to get latest submission ID per test for current user
    latest_submissions = db.query(
        Submission.test_id,
        func.max(Submission.id).label('submission_id')
    ).filter(
        Submission.user_id == current_user.id
    ).group_by(Submission.test_id).subquery()
    
    # Main query
    query = db.query(
        TestMetadata,
        func.coalesce(question_counts.c.count, 0).label('total_questions'),
        latest_submissions.c.submission_id.label('user_submission_id')
    ).outerjoin(
        question_counts, TestMetadata.id == question_counts.c.test_id
    ).outerjoin(
        latest_submissions, TestMetadata.id == latest_submissions.c.test_id
    ).filter(
        TestMetadata.is_active.is_(True)
    )
    
    results = query.all()
    
    response = []
    for test, total_questions, submission_id in results:
        test_data = {
            'id': test.id,
            'title': test.title,
            'description': test.description,
            'duration_minutes': test.duration_minutes,
            'total_questions': total_questions,
            'created_at': test.created_at,
            'user_submission_id': submission_id
        }
        response.append(TestMetadataResponse(**test_data))
        
    return response


@router.get("/{test_id}/questions", response_model=QuestionsResponse)
def get_test_questions(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all questions for a specific test as a flat array
    """
    
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
    
    return result
