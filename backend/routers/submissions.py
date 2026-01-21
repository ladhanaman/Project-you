# routers/submissions.py
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import update
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
        scores = {
            'fundamentals': 0,
            'applied': 0,
            'industry': 0,
            'total': 0
        }
        
        # Section-specific tag classification (per-category)
        section_tags = {
            'fundamentals': {'strong': set(), 'weak': set(), 'critical': set()},
            'applied': {'strong': set(), 'weak': set(), 'critical': set()},
            'industry': {'strong': set(), 'weak': set(), 'critical': set()}
        }
        
        # Global tags for 4-week plan and projects
        all_strong_tags = set()
        all_weak_tags = set()
        all_critical_tags = set()
        
        # Helper to get option index
        def get_option_index(selected_answer: str, question: Question) -> int:
            """Map selected answer to option index (1-5)"""
            selected_answer = selected_answer.strip()
            
            if selected_answer == question.option_1.strip():
                return 1
            elif selected_answer == question.option_2.strip():
                return 2
            elif selected_answer == question.option_3.strip():
                return 3
            elif selected_answer == question.option_4.strip():
                return 4
            elif question.option_5 and selected_answer == question.option_5.strip():
                return 5
            
            # Raise error instead of silent failure
            raise HTTPException(
                status_code=400,
                detail=f"Invalid answer '{selected_answer}' for question {question.id}"
            )
        
        # PRI assessment doesn't use legacy category-based scoring
        # All scoring is done by PRI calculator based on P/R/I weights
        # Skip legacy weight calculation
        
        scores['total'] = scores['fundamentals'] + scores['applied'] + scores['industry']
        
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
        

        # Prepare data for background task (with tags classification)
        answers_data = []
        for answer_submission in submission.answers:
            question = question_map[answer_submission.question_id]
            option_index = get_option_index(answer_submission.selected_answer, question)
            # Legacy get_weight() removed - PRI uses get_pri_weights()
            
            answers_data.append({
                'id': question.id,
                'question_text': question.question_text,
                'tags': question.tags,
                'selected_answer': answer_submission.selected_answer,
                'earned_weight': 0  # PRI uses different weight system
            })
        
        # Section-specific tag classification for insights
        tag_classification = {
            # Per-section tags (for section-specific insights)
            'fundamentals_tags': {
                'strong': list(section_tags['fundamentals']['strong']),
                'weak': list(section_tags['fundamentals']['weak']),
                'critical': list(section_tags['fundamentals']['critical'])
            },
            'applied_tags': {
                'strong': list(section_tags['applied']['strong']),
                'weak': list(section_tags['applied']['weak']),
                'critical': list(section_tags['applied']['critical'])
            },
            'industry_tags': {
                'strong': list(section_tags['industry']['strong']),
                'weak': list(section_tags['industry']['weak']),
                'critical': list(section_tags['industry']['critical'])
            },
            # Global tags (for 4-week plan and projects)
            'all_strong_tags': list(all_strong_tags),
            'all_weak_tags': list(all_weak_tags),
            'all_critical_tags': list(all_critical_tags)
        }
        
        
        # Trigger background task for insights and PDF for LEGACY assessments only
        # PRI assessments handle their own generation synchronously above
        if not is_pri_assessment:
            try:
                from tasks.report_tasks import generate_insights_and_report_task
                background_tasks.add_task(
                    generate_insights_and_report_task,
                    db_submission.id,
                    current_user.full_name,
                    current_user.email,
                    scores,
                    answers_data,
                    tag_classification  # Pass tag classification
                )
            except Exception as e:
                logger.error(f"Failed to queue background task: {e}")
                capture_exception(e, context={"submission_id": db_submission.id})

                # Update status to failed so user is not stuck in processing
                try:
                    db_submission.report_status = "failed"
                    db.commit()
                except Exception as db_err:
                    logger.error(f"Failed to update submission status to failed: {db_err}")

            # Continue even if task queueing fails
        
        logger.info(
            f"Assessment submitted: user_id={current_user.id} test_id={submission.test_id} "
            f"(Score: {scores['total']}/300)"
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


@router.post("/{submission_id}/retry")
@limiter.limit("3/hour")  # Reduced from 5/minute to prevent AI credit waste
def retry_report_generation(
    request: Request,
    submission_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retry AI report generation for submissions with pending_ai status.
    
    Called when user returns to view a report that failed initial AI generation.
    Uses saved tag data from retry_metadata column for retry.
    Uses atomic update to prevent race conditions.
    """
    try:
        # Use atomic update to prevent race condition
        # Only update if status is still pending_ai
        stmt = (
            update(Submission)
            .where(Submission.id == submission_id)
            .where(Submission.user_id == current_user.id)
            .where(Submission.report_status == "pending_ai")
            .values(report_status="processing")
        )
        result = db.execute(stmt)
        db.commit()
        
        if result.rowcount == 0:
            # Either submission not found, not owned by user, or already processing
            submission = db.query(Submission).filter(
                Submission.id == submission_id,
                Submission.user_id == current_user.id
            ).first()
            
            if not submission:
                raise HTTPException(status_code=404, detail="Submission not found")
            
            return {"status": submission.report_status, "message": "Report already processed or processing"}
        
        # Get the submission to read retry data
        submission = db.query(Submission).filter(
            Submission.id == submission_id,
            Submission.user_id == current_user.id
        ).first()
        
        # Get saved retry data
        retry_data = submission.retry_metadata if isinstance(submission.retry_metadata, dict) else {}
        
        if not retry_data:
            logger.error(f"[Submission {submission_id}] No retry data found for pending_ai submission")
            # Reset status back to pending_ai
            submission.report_status = "pending_ai"
            db.commit()
            raise HTTPException(status_code=400, detail="Cannot retry - missing generation data")
        
        logger.info(f"[Submission {submission_id}] Retrying AI report generation")
        
        # Import and queue background task
        from tasks.report_tasks import generate_insights_and_report_task
        
        # Reconstruct the tag classification from saved data
        tag_classification = {
            'fundamentals_tags': retry_data.get('fundamentals_tags', {}),
            'applied_tags': retry_data.get('applied_tags', {}),
            'industry_tags': retry_data.get('industry_tags', {}),
            'all_strong_tags': retry_data.get('all_strong_tags', []),
            'all_weak_tags': retry_data.get('all_weak_tags', []),
            'all_critical_tags': retry_data.get('all_critical_tags', [])
        }
        
        # Queue the report generation task
        background_tasks.add_task(
            generate_insights_and_report_task,
            submission.id,
            current_user.full_name,
            current_user.email,
            retry_data.get('scores', {}),
            {},  # answers_data not needed for retry
            tag_classification
        )
        
        return {
            "status": "processing",
            "message": "Report generation started. Please refresh in a moment."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrying report generation: {str(e)}")
        capture_exception(e, context={"submission_id": submission_id, "user_id": current_user.id})
        raise HTTPException(status_code=500, detail="Failed to retry report generation")
