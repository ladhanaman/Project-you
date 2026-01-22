# routers/submissions.py
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from typing import Dict, List
import os
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

from core.database import get_db
from models import User, Question, Submission, TestMetadata, ReflectionSession
from schemas import AssessmentSubmission, ScoringResponse, SubmissionResponse
from core.security import get_current_user
from core.monitoring import capture_exception
from services.pri.calculator import PRICalculator
from services.pri.archetype_classifier import ArchetypeClassifier
from services.pri.report_generator import PRIReportGenerator
from services.pri.reflection_generator import ReflectionSessionGenerator
import sentry_sdk
from datetime import date

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/submissions", tags=["Submissions"])


def process_pri_assessment(
    db_submission: Submission,
    question_map: Dict,
    answers: List,
    current_user: User,
    db: Session
):
    """
    Process PRI assessment: calculate scores, classify archetype, generate report and session.
    
    Args:
        db_submission: The submission record
        question_map: Dict of question_id -> Question object
        answers: List of answer submissions
        current_user: Current user object
        db: Database session
    """
    try:
        # Helper to get option index (supports 5 options)
        def get_option_index_pri(selected_answer: str, question: Question) -> int:
            """Map selected answer to option index (1-5)"""
            selected_answer = selected_answer.strip()
            options = [
                question.option_1,
                question.option_2,
                question.option_3,
                question.option_4,
                question.option_5
            ]
            
            for idx, option in enumerate(options, 1):
                if option and selected_answer == option.strip():
                    return idx
            
            raise HTTPException(
                status_code=400,
                detail=f"Invalid answer '{selected_answer}' for question {question.id}"
            )
        
        # Collect answers with PRI weights
        answers_with_weights = []
        positive_tags = set()
        negative_tags = set()
        
        for answer_sub in answers:
            question = question_map[answer_sub.question_id]
            option_index = get_option_index_pri(answer_sub.selected_answer, question)
            pri_weights = question.get_pri_weights(option_index)
            
            answers_with_weights.append({
                'question_id': question.id,
                'selected_option': option_index,
                'weights': pri_weights
            })
            
            # Use option-specific tags for better signal tracking
            option_tags = question.get_option_tags(option_index)
            
            # Track positive tags (high scores) and negative tags (low scores)
            avg_weight = (pri_weights['P'] + pri_weights['R'] + pri_weights['I']) / 3
            if avg_weight >= 60 and option_tags:  # High average (60+ out of 100)
                positive_tags.update(option_tags)
            elif avg_weight <= 30 and option_tags:  # Low average (30 or below out of 100)
                negative_tags.update(option_tags)
        
        # Calculate PRI scores
        calculator = PRICalculator()
        user_age = None
        if current_user.date_of_birth:
            today = date.today()
            user_age = today.year - current_user.date_of_birth.year
            if today.month < current_user.date_of_birth.month or \
               (today.month == current_user.date_of_birth.month and today.day < current_user.date_of_birth.day):
                user_age -= 1
        
        pri_results = calculator.calculate_pri_scores(
            answers=answers_with_weights,
            user_age=user_age
        )
        
        # Classify archetype
        classifier = ArchetypeClassifier()
        archetype_results = classifier.classify(
            purpose_level=pri_results['purpose_level'],
            relevance_level=pri_results['relevance_level'],
            identity_level=pri_results['identity_level'],
            age_category=pri_results['age_category']
        )
        
        # Update submission with PRI data (store as 0-1 float scale)
        db_submission.purpose_score = pri_results['purpose_score']
        db_submission.relevance_score = pri_results['relevance_score']
        db_submission.identity_score = pri_results['identity_score']
        db_submission.purpose_level = pri_results['purpose_level'][0]  # H, M, or L
        db_submission.relevance_level = pri_results['relevance_level'][0]
        db_submission.identity_level = pri_results['identity_level'][0]
        db_submission.archetype = archetype_results['internal_base_archetype']
        db_submission.display_archetype = archetype_results['display_archetype']
        db_submission.final_archetype = archetype_results['final_archetype']
        db_submission.positive_tags = list(positive_tags)[:10]  # Top 10
        db_submission.negative_tags = list(negative_tags)[:10]
        
        logger.info(f"PRI scores calculated for submission {db_submission.id}: " +
                   f"P={pri_results['purpose_score']:.2f}, " +
                   f"R={pri_results['relevance_score']:.2f}, " +
                   f"I={pri_results['identity_score']:.2f}, " +
                   f"Archetype={archetype_results['final_archetype']}")
        
        # Generate PRI report (asynchronously handled, so just mark status)
        db_submission.report_status = "processing_pri"
        db.commit()
        
        # Store generation request in background
        # We'll generate the report and reflection session after commit
        return {
            'pri_results': pri_results,
            'archetype_results': archetype_results,
            'user_profile': {
                'name': current_user.first_name or current_user.full_name,
                'age': user_age,
                'city': current_user.city,
                'occupation': current_user.occupation,
                'education': current_user.education,
                'industry': current_user.industry_domain,
                'hobbies': current_user.hobbies
            },
            'signals': {
                'positive_tags': list(positive_tags)[:10],
                'negative_tags': list(negative_tags)[:10]
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing PRI assessment: {str(e)}")
        raise


@router.post("", response_model=ScoringResponse)
@limiter.limit("10/hour")
def submit_assessment(
    request: Request,
    submission: AssessmentSubmission,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit assessment and calculate scores
    
    Protected endpoint - requires authentication
    Rate limited to 10 submissions per hour per user
    Triggers asynchronous background task for insight generation and PDF report creation
    """
    try:
        # Verify test exists
        test = db.query(TestMetadata).filter(
            TestMetadata.id == submission.test_id
        ).first()
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
        
        # Fetch all questions for this test
        all_questions = db.query(Question).filter(
            Question.test_id == submission.test_id
        ).all()
        question_map = {q.id: q for q in all_questions}
        
        # Validate all submitted questions exist
        submitted_ids = [a.question_id for a in submission.answers]
        invalid_ids = [id for id in submitted_ids if id not in question_map]
        if invalid_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid question IDs: {invalid_ids}"
            )
        
        # Calculate scores with three-tier classification
        # PRI assessment handling - logic simplified

        
        # Create submission record (PRI-only fields)
        db_submission = Submission(
            user_id=current_user.id,
            test_id=submission.test_id,
            answers={a.question_id: a.selected_answer for a in submission.answers},
            report_status="processing"
        )
        
        db.add(db_submission)
        db.commit()
        db.refresh(db_submission)
        
        # Check if this is a PRI assessment (Know Yourself test)
        is_pri_assessment = test.title == "Know Yourself"
        
        if is_pri_assessment:
            # Process PRI assessment
            try:
                pri_data = process_pri_assessment(
                    db_submission=db_submission,
                    question_map=question_map,
                    answers=submission.answers,
                    current_user=current_user,
                    db=db
                )
                
                # Generate PRI report and reflection session in BACKGROUND
                try:
                    from tasks.report_tasks import generate_pri_report_task
                    
                    # Prepare data for background task
                    user_profile_data = pri_data['user_profile']
                    pri_scores_data = {
                        'purpose_score': pri_data['pri_results']['purpose_score'],
                        'relevance_score': pri_data['pri_results']['relevance_score'],
                        'identity_score': pri_data['pri_results']['identity_score'],
                        'purpose_level': pri_data['pri_results']['purpose_level'],
                        'relevance_level': pri_data['pri_results']['relevance_level'],
                        'identity_level': pri_data['pri_results']['identity_level']
                    }
                    
                    background_tasks.add_task(
                        generate_pri_report_task,
                        db_submission.id,
                        current_user.full_name,
                        pri_scores_data,
                        pri_data['archetype_results'],
                        pri_data['signals'],
                        user_profile_data
                    )
                    
                    logger.info(f"Queued PRI report generation task for submission {db_submission.id}")
                
                except Exception as task_error:
                    logger.error(f"Failed to queue PRI background task: {task_error}")
                    db_submission.report_status = "failed"
                    db.commit()
            
            except Exception as pri_error:
                logger.error(f"Error in PRI processing: {str(pri_error)}")
                capture_exception(pri_error, context={"submission_id": db_submission.id})
        

        else:
            # Fallback for non-PRI tests
            logger.warning(f"Submission {db_submission.id} is NOT a PRI assessment. No logic available.")
            db_submission.report_status = "completed"
            db.commit()

        
        logger.info(
            f"Assessment submitted: user_id={current_user.id} test_id={submission.test_id} "
            f"(Submission ID: {db_submission.id})"
        )
        
        return ScoringResponse(
            submission_id=db_submission.id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting assessment: {str(e)}")
        capture_exception(e, context={"user_id": current_user.id, "test_id": submission.test_id})
        raise HTTPException(status_code=500, detail="Failed to submit assessment")


@router.get("/{submission_id}", response_model=SubmissionResponse)
def get_submission(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve submission details and generated insights
    
    Protected endpoint - users can only access their own submissions
    """
    try:
        submission = db.query(Submission).filter(
            Submission.id == submission_id,
            Submission.user_id == current_user.id
        ).first()
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        return SubmissionResponse.model_validate(submission)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching submission: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch submission")


@router.get("/{submission_id}/download")
@limiter.limit("10/minute")  # Prevent download abuse
def download_report(
    request: Request,
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download the generated PDF report
    
    Protected endpoint - users can only download their own reports
    """
    try:
        submission = db.query(Submission).filter(
            Submission.id == submission_id,
            Submission.user_id == current_user.id
        ).first()
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
            
        if not submission.pdf_generated or not os.path.exists(submission.pdf_generated):
            raise HTTPException(status_code=404, detail="PDF report not available")
            
        return FileResponse(
            path=submission.pdf_generated,
            filename=os.path.basename(submission.pdf_generated),
            media_type='application/pdf'
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        capture_exception(e, context={"submission_id": submission_id, "user_id": current_user.id})
        raise HTTPException(status_code=500, detail="Failed to download report")


@router.get("", response_model=List[SubmissionResponse])
def get_user_submissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20
):
    """
    Get user's submission history with pagination
    
    Protected endpoint - returns only current user's submissions
    """
    try:
        submissions = db.query(Submission).filter(
            Submission.user_id == current_user.id
        ).order_by(
            Submission.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return [SubmissionResponse.model_validate(sub) for sub in submissions]
    
    except Exception as e:
        logger.error(f"Error fetching submissions: {str(e)}")
        capture_exception(e, context={"user_id": current_user.id})
        raise HTTPException(status_code=500, detail="Failed to fetch submissions")


# Legacy retry endpoint removed

