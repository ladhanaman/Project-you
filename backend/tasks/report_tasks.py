# tasks/report_tasks.py - Background Report Generation Tasks
"""
Background tasks for generating AI insights and PDF reports.
"""
from typing import Dict, List
import logging
import os

from core.config import settings

logger = logging.getLogger(__name__)






def generate_pri_report_task(
    submission_id: int,
    candidate_name: str,
    pri_data: Dict,
    archetype_results: Dict,
    signals: Dict,
    user_settings: Dict  # Passed as dict to avoid serialization issues
):
    """
    Background task to generate PRI Report and Reflection Session.
    """
    from core.database import SessionLocal
    from models import Submission, ReflectionSession
    from services.pri.report_generator import PRIReportGenerator
    from services.pri.reflection_generator import ReflectionSessionGenerator
    from core.monitoring import capture_exception
    
    logger.info(f"[PRI Sub #{submission_id}] Starting background generation task")
    
    db = SessionLocal()
    
    try:
        # Update status to processing
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if submission:
            submission.report_status = "processing_pri"
            db.commit()
        
        # 1. Generate PRI Report
        try:
            report_gen = PRIReportGenerator()
            report_md = report_gen.generate_report(
                user_profile=user_settings,
                pri_data=pri_data,
                archetype_data=archetype_results,
                signals=signals
            )
            
            # Save report
            submission = db.query(Submission).filter(Submission.id == submission_id).first()
            submission.pri_report_md = report_md
            submission.report_status = "completed"
            db.commit()
            logger.info(f"[PRI Sub #{submission_id}] Report generated successfully")
            
        except Exception as report_err:
            logger.error(f"[PRI Sub #{submission_id}] Report generation failed: {report_err}")
            submission = db.query(Submission).filter(Submission.id == submission_id).first()
            submission.report_status = "failed"
            db.commit()
            raise report_err

        # 2. Generate Reflection Session
        try:
            reflection_gen = ReflectionSessionGenerator()
            session_data = reflection_gen.generate_session(
                user_profile=user_settings,
                pri_data=pri_data,
                archetype_data=archetype_results,
                signals=signals
            )
            
            # Save reflection session
            # Check if one already exists to avoid duplicates on retry
            existing_session = db.query(ReflectionSession).filter(
                ReflectionSession.submission_id == submission_id
            ).first()
            
            if existing_session:
                db.delete(existing_session)
                db.commit()

            reflection_session = ReflectionSession(
                submission_id=submission_id,
                user_id=submission.user_id,
                session_title=session_data['reflection_session_title'],
                final_archetype=session_data['final_archetype'],
                primary_theme_dimension=session_data['primary_theme']['dimension'],
                primary_theme_reason=session_data['primary_theme']['reason'],
                secondary_theme_dimension=session_data['secondary_theme']['dimension'],
                secondary_theme_reason=session_data['secondary_theme']['reason'],
                unlock_default_time=session_data.get('unlock_default_time_local', '09:00'),
                session_data=session_data
            )
            db.add(reflection_session)
            db.commit()
            logger.info(f"[PRI Sub #{submission_id}] Reflection session generated")
            
        except Exception as reflect_err:
            logger.error(f"[PRI Sub #{submission_id}] Reflection generation failed: {reflect_err}")
            # We don't fail the whole submission if just reflection fails, but valid to log
            capture_exception(reflect_err, context={"submission_id": submission_id})

    except Exception as e:
        logger.error(f"[PRI Sub #{submission_id}] Critical failure in background task: {e}")
        capture_exception(e, context={"submission_id": submission_id})
        try:
            submission = db.query(Submission).filter(Submission.id == submission_id).first()
            submission.report_status = "failed"
            db.commit()
        except:
            pass
    finally:
        db.close()
