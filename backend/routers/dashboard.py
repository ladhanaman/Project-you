# routers/dashboard.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Dict, Any, Optional
import logging

from core.database import get_db
from models import User, Submission, DailyReflection, ReflectionSession
from core.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get dashboard summary with PRI scores, journey progress, and archetype.
    
    Returns aggregated data for the Bento Grid homepage:
    - User info
    - Latest PRI scores (if assessment completed)
    - Journey progress (if active)
    - Archetype information
    """
    try:
        # Get latest submission for this user
        latest_submission = db.query(Submission).filter(
            Submission.user_id == current_user.id
        ).order_by(desc(Submission.created_at)).first()
        
        # Initialize response structure
        response = {
            "user": {
                "first_name": current_user.first_name or current_user.full_name.split()[0] if current_user.full_name else "User",
                "full_name": current_user.full_name or "User"
            },
            "pri_scores": {
                "purpose_score": 0,
                "relevance_score": 0,
                "identity_score": 0,
                "has_completed_assessment": False,
                "latest_submission_id": None
            },
            "journey": {
                "has_active_session": False,
                "current_day": 1,
                "completed_days": 0,
                "total_days": 7,
                "completion_percentage": 0,
                "days": {}
            },
            "archetype": {
                "name": None,
                "level": None,
                "subtitle": None,
                "icon": None,
                "final_archetype": None
            }
        }
        
        # Populate PRI scores if submission exists
        if latest_submission:
            response["pri_scores"] = {
                "purpose_score": int(latest_submission.purpose_score * 100) if latest_submission.purpose_score else 0,
                "relevance_score": int(latest_submission.relevance_score * 100) if latest_submission.relevance_score else 0,
                "identity_score": int(latest_submission.identity_score * 100) if latest_submission.identity_score else 0,
                "has_completed_assessment": True,
                "latest_submission_id": latest_submission.id
            }
            
            # Populate archetype data
            if latest_submission.final_archetype:
                # Parse archetype data - format: "Young Explorer", "Mature Navigator", etc.
                archetype_name = latest_submission.display_archetype or latest_submission.final_archetype
                
                # Extract base archetype (e.g., "Explorer" from "Young Explorer")
                base_archetype = archetype_name.split()[-1] if ' ' in archetype_name else archetype_name
                
                # Map archetypes to icons
                archetype_icons = {
                    "Explorer": "🧭",
                    "Navigator": "🗺️",
                    "Builder": "🏗️",
                    "Guardian": "🛡️",
                    "Catalyst": "⚡",
                    "Harmonizer": "🎵",
                    "Visionary": "🔮",
                    "Sage": "📚"
                }
                
                # Calculate level based on PRI scores (simple heuristic)
                avg_score = (latest_submission.purpose_score + latest_submission.relevance_score + latest_submission.identity_score) / 3
                level = 1
                if avg_score >= 0.8:
                    level = 5
                elif avg_score >= 0.7:
                    level = 4
                elif avg_score >= 0.6:
                    level = 3
                elif avg_score >= 0.5:
                    level = 2
                
                response["archetype"] = {
                    "name": archetype_name,
                    "level": level,
                    "subtitle": "Trailblazer" if level >= 3 else "Seeker",
                    "icon": archetype_icons.get(base_archetype, "🌟"),
                    "final_archetype": latest_submission.final_archetype
                }
            
            # Check for active reflection session
            reflection_session = db.query(ReflectionSession).filter(
                ReflectionSession.submission_id == latest_submission.id,
                ReflectionSession.user_id == current_user.id
            ).first()
            
            if reflection_session:
                # Get completed reflections
                completed_reflections = db.query(DailyReflection).filter(
                    DailyReflection.user_id == current_user.id
                ).all()
                
                # Map reflections by day number
                completed_days_map = {}
                for reflection in completed_reflections:
                    day_num = reflection.day_number
                    if 1 <= day_num <= 7:
                        completed_days_map[day_num] = {
                            "completed": True,
                            "completed_at": reflection.created_at.isoformat() if reflection.created_at else None
                        }
                
                # Build days structure
                days_data = {}
                for day in range(1, 8):
                    if day in completed_days_map:
                        days_data[str(day)] = completed_days_map[day]
                    else:
                        days_data[str(day)] = {
                            "completed": False
                        }
                
                completed_count = len(completed_days_map)
                current_day = min(completed_count + 1, 7)
                
                response["journey"] = {
                    "has_active_session": True,
                    "current_day": current_day,
                    "completed_days": completed_count,
                    "total_days": 7,
                    "completion_percentage": int((completed_count / 7) * 100),
                    "days": days_data
                }
        
        logger.info(f"Dashboard summary retrieved for user {current_user.id}")
        return response
    
    except Exception as e:
        logger.error(f"Error fetching dashboard summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard summary")
