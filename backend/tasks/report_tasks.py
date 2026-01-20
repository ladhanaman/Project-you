# tasks/report_tasks.py - Background Report Generation Tasks
"""
Background tasks for generating AI insights and PDF reports.
"""
from typing import Dict, List
import logging
import os

from core.config import settings

logger = logging.getLogger(__name__)


def generate_fallback_insights(test_title, candidate_name, performance_data, strong_tags=[], weak_tags=[], critical_tags=[]):
    """Generate basic insights when AI service is unavailable"""
    logger.info(f"Generating FALLBACK insights for {candidate_name}")
    logger.info(f"  Strong tags: {len(strong_tags)} ({', '.join(strong_tags[:3])}{'...' if len(strong_tags) > 3 else ''})")
    logger.info(f"  Weak tags: {len(weak_tags)} ({', '.join(weak_tags[:3])}{'...' if len(weak_tags) > 3 else ''})")
    logger.info(f"  Critical tags: {len(critical_tags)} ({', '.join(critical_tags[:3])}{'...' if len(critical_tags) > 3 else ''})")
    
    total_score = performance_data.get('total_score', 0)
    fundamentals_score = performance_data.get('fundamentals_score', 0)
    applied_score = performance_data.get('applied_score', 0)
    industry_score = performance_data.get('industry_score', 0)
    
    # Determine readiness level
    if total_score >= 80:
        readiness_level = "Advanced"
        readiness_justification = "Excellent performance across all categories"
    elif total_score >= 60:
        readiness_level = "Intermediate"
        readiness_justification = "Good foundation with room for improvement"
    else:
        readiness_level = "Beginner"
        readiness_justification = "Building foundational knowledge"
    
    logger.info(f"  Readiness level: {readiness_level} ({total_score}%)")
    logger.info("Fallback insights generated successfully")
    
    return {
        "executive_summary": f"{candidate_name} completed the {test_title} assessment with a score of {total_score}%. This demonstrates {readiness_level.lower()} level proficiency in the subject matter.",
        "strengths": [
            f"Completed all sections of the assessment",
            f"Achieved {total_score}% overall score"
        ],
        "areas_for_improvement": [
            "Continue practicing fundamental concepts" if fundamentals_score < 80 else None,
            "Strengthen applied knowledge" if applied_score < 80 else None,
            "Develop industry-specific skills" if industry_score < 80 else None
        ],
        
        "learning_plan_weeks": [
            {"focus_area": "Fundamentals", "tasks": "Review core concepts and practice exercises", "expected_outcome": "Solid understanding of basics"},
            {"focus_area": "Applied Knowledge", "tasks": "Work on hands-on projects and code challenges", "expected_outcome": "Ability to apply theory to practice"},
            {"focus_area": "Industry Standards", "tasks": "Read industry blogs and study case studies", "expected_outcome": "Awareness of current best practices"},
            {"focus_area": "Career Preparation", "tasks": "Mock interviews and peer reviews", "expected_outcome": "Readiness for job interviews"}
        ],
        "industry_readiness_level": readiness_level,
        "readiness_level_justification": readiness_justification,
        "interview_prep_technical": [
            "Review core concepts from the assessment",
            "Practice explaining your approach to problems",
            "Prepare examples from your projects"
        ],
        "interview_prep_behavioral": [
            "Prepare STAR method responses",
            "Practice discussing teamwork experiences",
            "Be ready to discuss learning experiences"
        ],
        "project_recommendations": [
            f"Build a project related to {test_title}",
            "Contribute to open-source projects",
            "Create a portfolio showcasing your skills"
        ],
        "role_fit": f"{readiness_level} level roles in the field",
    }


def generate_insights_and_report_task(
    submission_id: int,
    candidate_name: str,
    candidate_email: str,
    scores: Dict[str, int],
    answers_data: List[Dict],
    tag_classification: Dict  # NEW: strong_tags and weak_tags
):
    """
    Background task to generate AI insights and PDF report
    This runs asynchronously using FastAPI BackgroundTasks
    """
    # Import here to avoid circular imports
    from core.database import SessionLocal
    from models import Submission, User, TestMetadata
    from services.ai import AIInsightEngine
    from services.report import PDFReportGenerator
    from core.monitoring import capture_exception
    
    # Initialize services
    OPENAI_API_KEY = settings.OPENAI_API_KEY
    GEMINI_API_KEY = settings.GEMINI_API_KEY
    OUTPUT_DIR = settings.REPORT_OUTPUT_DIR
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    logger.info(f"[Submission {submission_id}] Initializing AI Engine. OpenAI Key present: {bool(OPENAI_API_KEY)}, Gemini Key present: {bool(GEMINI_API_KEY)}")

    ai_engine = AIInsightEngine(api_key=OPENAI_API_KEY, gemini_api_key=GEMINI_API_KEY)
    pdf_generator = PDFReportGenerator(output_dir=OUTPUT_DIR)
    
    db = SessionLocal()
    
    try:
        # Update status to processing
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if submission:
            submission.report_status = "processing"
            db.commit()
        
        # Extract section-specific tag classification
        fundamentals_tags = tag_classification.get('fundamentals_tags', {'strong': [], 'weak': [], 'critical': []})
        applied_tags = tag_classification.get('applied_tags', {'strong': [], 'weak': [], 'critical': []})
        industry_tags = tag_classification.get('industry_tags', {'strong': [], 'weak': [], 'critical': []})
        
        # Global tags for 4-week plan and projects
        all_strong_tags = tag_classification.get('all_strong_tags', [])
        all_weak_tags = tag_classification.get('all_weak_tags', [])
        all_critical_tags = tag_classification.get('all_critical_tags', [])
        
        # Get test name for dynamic industry context
        test = db.query(TestMetadata).filter(TestMetadata.id == submission.test_id).first()
        test_name = test.title if test else "Assessment"
        
        # Generate AI insights using section-specific tags
        logger.info(f"[Sub #{submission_id}] Starting report generation")
        ai_generated = False
        insights = None
        
        try:
            # Use section-specific insights generation
            insights = ai_engine.generate_insights_simplified(
                candidate_name=candidate_name,
                test_name=test_name,
                scores=scores,
                fundamentals_tags=fundamentals_tags,
                applied_tags=applied_tags,
                industry_tags=industry_tags,
                all_strong_tags=all_strong_tags,
                all_weak_tags=all_weak_tags,
                all_critical_tags=all_critical_tags
            )
            ai_generated = True
        except Exception as ai_error:
            # AI failed - set status to pending_ai for retry later
            logger.warning(f"[Sub #{submission_id}] AI failed: {str(ai_error)[:80]}")
            logger.info(f"[Sub #{submission_id}] Setting status to pending_ai for later retry")
            
            try:
                # Get submission to save tag data for retry
                submission = db.query(Submission).filter(Submission.id == submission_id).first()
                if submission:
                    # Save tag data in retry_metadata for later retry
                    submission.retry_metadata = {
                        'fundamentals_tags': fundamentals_tags,
                        'applied_tags': applied_tags,
                        'industry_tags': industry_tags,
                        'all_strong_tags': all_strong_tags,
                        'all_weak_tags': all_weak_tags,
                        'all_critical_tags': all_critical_tags,
                        'scores': scores,
                        'test_name': test_name
                    }
                    submission.report_status = "pending_ai"
                    submission.ai_generated = False
                    db.commit()
                    logger.info(f"[Sub #{submission_id}] Saved for retry. User will see friendly message.")
            except Exception as save_error:
                logger.error(f"[Sub #{submission_id}] Failed to save pending_ai status: {save_error}")
                # Even if save fails, don't let it cascade to outer exception
            
            return {"status": "pending_ai", "submission_id": submission_id, "message": "Report generation queued"}
        
        # Get submission to retrieve user info
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            raise ValueError(f"Submission {submission_id} not found")
        
        # Get user for onboarding details
        user = db.query(User).filter(User.id == submission.user_id).first()
        
        # Generate PDF report
        logger.info(f"[Submission {submission_id}] Generating PDF report for submission {submission_id}")
        
        # Prepare scores dict
        scores = {
            'fundamentals': submission.fundamentals_score,
            'applied': submission.applied_score,
            'industry': submission.industry_score,
            'total': submission.total_score
        }

        pdf_path = pdf_generator.generate_report(
            submission_id=submission_id,
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            candidate_college=user.college if user else 'N/A',
            candidate_course=user.course if user and hasattr(user, 'course') else 'N/A',
            candidate_year=user.year_of_study if user and hasattr(user, 'year_of_study') else 'N/A',
            candidate_phone=user.phone_number if user and hasattr(user, 'phone_number') else 'N/A',
            candidate_specialization=user.specialization if user and hasattr(user, 'specialization') else None,
            candidate_linkedin=user.linkedin_url if user and hasattr(user, 'linkedin_url') else None,
            scores=scores,
            insights=insights
        )
        
        # Update submission with insights and report
        submission.executive_summary = insights.get('executive_summary')
        submission.fundamentals_insights = insights.get('fundamentals_insights', {})
        submission.applied_insights = insights.get('applied_insights', {})
        submission.industry_insights = insights.get('industry_insights', {})
        submission.strengths = insights.get('strengths', [])
        submission.areas_for_improvement = insights.get('areas_for_improvement', [])
        submission.learning_plan_weeks = insights.get('learning_plan_weeks')
        submission.industry_readiness_level = insights.get('industry_readiness_level')
        submission.readiness_level_justification = insights.get('readiness_level_justification')
        submission.interview_prep_technical = insights.get('interview_prep_technical')
        submission.interview_prep_behavioral = insights.get('interview_prep_behavioral')
        submission.project_recommendations = insights.get('project_recommendations')
        submission.missed_tags = insights.get('missed_tags', [])
        
        # Serialize role_fit to JSON string if it's a list (new format)
        role_fit = insights.get('role_fit', 'Junior Engineer')
        if isinstance(role_fit, list):
            import json
            submission.role_fit = json.dumps(role_fit)
        else:
            submission.role_fit = role_fit
            
        submission.pdf_generated = pdf_path
        submission.report_status = "completed"
        submission.ai_generated = ai_generated
        
        db.commit()

        logger.info(f"[Sub #{submission_id}] Report complete (AI)")
        
        return {"status": "completed", "submission_id": submission_id}
        
    except Exception as exc:
        logger.error(f"[Submission {submission_id}] Error processing submission {submission_id}: {str(exc)}")
        capture_exception(exc, context={"submission_id": submission_id})
        
        try:
            submission = db.query(Submission).filter(Submission.id == submission_id).first()
            if submission:
                submission.report_status = "failed"
                db.commit()
                logger.info(f"[Submission {submission_id}] Status updated to failed")
        except Exception as db_error:
            logger.error(f"[Submission {submission_id}] Failed to update submission status: {db_error}")

    finally:
        db.close()
