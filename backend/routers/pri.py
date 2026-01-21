from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
import logging

from core.database import get_db
from models import User, Submission, ReflectionSession
from core.security import get_current_user
from services.pri.report_generator import PRIReportGenerator
from services.pri.reflection_generator import ReflectionSessionGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pri", tags=["PRI"])


@router.get("/report/{submission_id}")
def get_pri_report(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get PRI "Meet Yourself" report for a submission.
    
    Returns:
        {
            "submission_id": int,
            "archetype": str,
            "display_archetype": str,
            "final_archetype": str,
            "purpose_score": float,
            "relevance_score": float,
            "identity_score": float,
            "purpose_level": str,
            "relevance_level": str,
            "identity_level": str,
            "report_markdown": str
        }
    """
    try:
        # Fetch submission
        submission = db.query(Submission).filter(
            Submission.id == submission_id,
            Submission.user_id == current_user.id
        ).first()
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Check if PRI data exists
        if not submission.purpose_score:
            raise HTTPException(
                status_code=400,
                detail="PRI assessment not completed for this submission"
            )
        
        return {
            "submission_id": submission.id,
            "archetype": submission.archetype,
            "display_archetype": submission.display_archetype,
            "final_archetype": submission.final_archetype,
            "purpose_score": submission.purpose_score,
            "relevance_score": submission.relevance_score,
            "identity_score": submission.identity_score,
            "purpose_level": submission.purpose_level,
            "relevance_level": submission.relevance_level,
            "identity_level": submission.identity_level,
            "report_markdown": submission.pri_report_md,
            "positive_tags": submission.positive_tags or [],
            "negative_tags": submission.negative_tags or []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching PRI report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch PRI report")


@router.get("/reflection-session/{submission_id}")
def get_reflection_session(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get 7-day reflection session for a submission.
    
    Returns:
        {
            "session_id": int,
            "session_title": str,
            "final_archetype": str,
            "primary_theme": {
                "dimension": str,
                "reason": str
            },
            "secondary_theme": {
                "dimension": str,
                "reason": str
            },
            "unlock_default_time_local": str,
            "days": [...]
        }
    """
    try:
        # Fetch reflection session
        session = db.query(ReflectionSession).filter(
            ReflectionSession.submission_id == submission_id,
            ReflectionSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Reflection session not found")
        
        return {
            "session_id": session.id,
            "session_title": session.session_title,
            "final_archetype": session.final_archetype,
            "primary_theme": {
                "dimension": session.primary_theme_dimension,
                "reason": session.primary_theme_reason
            },
            "secondary_theme": {
                "dimension": session.secondary_theme_dimension,
                "reason": session.secondary_theme_reason
            },
            "unlock_default_time_local": session.unlock_default_time,
            "days": session.session_data.get("days", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching reflection session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch reflection session")
