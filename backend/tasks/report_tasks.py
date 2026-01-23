# tasks/report_tasks.py - Background Report Generation Tasks
"""
Background tasks for generating AI insights and PDF reports.
"""
from typing import Dict, List
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import asyncio

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
    Background task to generate PRI Report and Reflection Session IN PARALLEL.
    """
    from core.database import SessionLocal
    from models import Submission, ReflectionSession
    from services.pri.report_generator import PRIReportGenerator
    from services.pri.reflection_generator import ReflectionSessionGenerator
    from core.monitoring import capture_exception
    from routers.websocket import get_connection_manager
    
    logger.info(f"[PRI Sub #{submission_id}] Starting parallel generation task")
    start_time = time.time()
    
    db = SessionLocal()
    
    try:
        # Get WebSocket manager for real-time updates
        try:
            ws_manager = get_connection_manager()
        except:
            ws_manager = None
            logger.warning("WebSocket manager not available")
        
        # Helper to send WebSocket update
        async def send_ws_update(status: str, message: str):
            if ws_manager:
                try:
                    await ws_manager.send_status_update(submission_id, status, message)
                except Exception as e:
                    logger.debug(f"WebSocket update failed: {e}")
        
        # Update status to processing
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if submission:
            submission.report_status = "processing_pri"
            db.commit()
            # Notify via WebSocket
            try:
                asyncio.run(send_ws_update("processing_pri", "Starting report generation"))
            except:
                pass
        
        # Worker functions for parallel execution
        def generate_report_worker():
            """Generate PRI report in parallel thread"""
            try:
                report_start = time.time()
                logger.info(f"[PRI Sub #{submission_id}] Starting report generation (gpt-5.2)...")
                
                report_gen = PRIReportGenerator(model="gpt-5.2")
                report_md = report_gen.generate_report(
                    user_profile=user_settings,
                    pri_data=pri_data,
                    archetype_data=archetype_results,
                    signals=signals
                )
                
                report_duration = time.time() - report_start
                logger.info(f"[PRI Sub #{submission_id}] Report completed in {report_duration:.2f}s")
                return ("report", report_md, None)
                
            except Exception as e:
                logger.error(f"[PRI Sub #{submission_id}] Report generation failed: {e}")
                return ("report", None, e)
        
        def generate_reflection_worker():
            """Generate reflection session in parallel thread"""
            try:
                reflection_start = time.time()
                logger.info(f"[PRI Sub #{submission_id}] Starting reflection generation (gpt-4o-mini)...")
                
                reflection_gen = ReflectionSessionGenerator(model="gpt-4o-mini")
                session_data = reflection_gen.generate_session(
                    user_profile=user_settings,
                    pri_data=pri_data,
                    archetype_data=archetype_results,
                    signals=signals
                )
                
                reflection_duration = time.time() - reflection_start
                logger.info(f"[PRI Sub #{submission_id}] Reflection completed in {reflection_duration:.2f}s")
                return ("reflection", session_data, None)
                
            except Exception as e:
                logger.error(f"[PRI Sub #{submission_id}] Reflection generation failed: {e}")
                return ("reflection", None, e)
        
        # Execute both tasks in parallel using ThreadPoolExecutor
        report_result = None
        reflection_result = None
        report_error = None
        reflection_error = None
        report_saved = False
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both tasks
            futures = {
                executor.submit(generate_report_worker): "report",
                executor.submit(generate_reflection_worker): "reflection"
            }
            
            # Collect results as they complete and IMMEDIATELY save report
            for future in as_completed(futures):
                task_type, data, error = future.result()
                
                if task_type == "report":
                    report_result = data
                    report_error = error
                    
                    # IMMEDIATELY save report to allow frontend to display it
                    if report_result and not report_error:
                        submission = db.query(Submission).filter(Submission.id == submission_id).first()
                        submission.pri_report_md = report_result
                        submission.report_status = "completed"
                        submission.ai_generated = True
                        db.commit()
                        report_saved = True
                        logger.info(f"[PRI Sub #{submission_id}] Report saved successfully (displayed to user)")
                        
                        # Notify completion via WebSocket
                        try:
                            asyncio.run(send_ws_update("completed", "Report generation completed"))
                        except:
                            pass
                    else:
                        # Report failed - mark submission as failed immediately
                        logger.error(f"[PRI Sub #{submission_id}] Report generation failed, marking submission as failed")
                        submission = db.query(Submission).filter(Submission.id == submission_id).first()
                        submission.report_status = "failed"
                        db.commit()
                        if report_error:
                            raise report_error
                    
                elif task_type == "reflection":
                    reflection_result = data
                    reflection_error = error
        
        total_duration = time.time() - start_time
        logger.info(f"[PRI Sub #{submission_id}] Parallel generation completed in {total_duration:.2f}s")
        
        # 2. Save reflection session if successful (non-critical)
        if reflection_result and not reflection_error:
            try:
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
                    session_title=reflection_result['reflection_session_title'],
                    final_archetype=reflection_result['final_archetype'],
                    primary_theme_dimension=reflection_result['primary_theme']['dimension'],
                    primary_theme_reason=reflection_result['primary_theme']['reason'],
                    secondary_theme_dimension=reflection_result['secondary_theme']['dimension'],
                    secondary_theme_reason=reflection_result['secondary_theme']['reason'],
                    unlock_default_time=reflection_result.get('unlock_default_time_local', '09:00'),
                    session_data=reflection_result
                )
                db.add(reflection_session)
                db.commit()
                logger.info(f"[PRI Sub #{submission_id}] Reflection session saved successfully")
                
            except Exception as save_err:
                logger.error(f"[PRI Sub #{submission_id}] Failed to save reflection session: {save_err}")
                capture_exception(save_err, context={"submission_id": submission_id})
        else:
            # Reflection failed but report succeeded - log but don't fail entire task
            logger.warning(f"[PRI Sub #{submission_id}] Reflection generation failed (non-critical)")
            if reflection_error:
                capture_exception(reflection_error, context={"submission_id": submission_id})

    except Exception as e:
        logger.error(f"[PRI Sub #{submission_id}] Critical failure in background task: {e}")
        capture_exception(e, context={"submission_id": submission_id})
        try:
            submission = db.query(Submission).filter(Submission.id == submission_id).first()
            submission.report_status = "failed"
            db.commit()
            # Notify failure via WebSocket
            try:
                asyncio.run(send_ws_update("failed", f"Report generation failed: {str(e)}"))
            except:
                pass
        except:
            pass
    finally:
        db.close()
