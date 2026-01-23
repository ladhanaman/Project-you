# routers/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from fastapi.exceptions import WebSocketException
from sqlalchemy.orm import Session
from typing import Dict, Optional
import logging
import json
from datetime import datetime, timedelta

from core.database import get_db
from core.security import decode_token
from models import Submission, User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])




# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.connection_timestamps: Dict[int, datetime] = {}  # Track last activity
        


    async def connect(self, submission_id: int, websocket: WebSocket):
        # Clean up stale connections before accepting new one (memory management)
        self.cleanup_stale_connections()
        
        await websocket.accept()
        self.active_connections[submission_id] = websocket
        self.connection_timestamps[submission_id] = datetime.utcnow()

        logger.info(f"WebSocket connected for submission {submission_id}")
    
    def disconnect(self, submission_id: int):
        if submission_id in self.active_connections:
            del self.active_connections[submission_id]
        if submission_id in self.connection_timestamps:
            del self.connection_timestamps[submission_id]

        logger.info(f"WebSocket disconnected for submission {submission_id}")
    
    def cleanup_stale_connections(self, max_age_minutes: int = 30):
        """Remove connections older than max_age_minutes"""
        now = datetime.utcnow()
        stale_ids = [
            sid for sid, timestamp in self.connection_timestamps.items()
            if now - timestamp > timedelta(minutes=max_age_minutes)
        ]
        for sid in stale_ids:
            logger.info(f"Cleaning up stale WebSocket connection for submission {sid}")
            self.disconnect(sid)
    
    async def send_status_update(self, submission_id: int, status: str, message: str) -> bool:
        """
        Send status update to connected client
        Returns: True if sent successfully, False otherwise
        """
        if submission_id in self.active_connections:
            try:
                # Update last activity timestamp
                self.connection_timestamps[submission_id] = datetime.utcnow()
                
                await self.active_connections[submission_id].send_json({
                    "type": "report_status",
                    "submission_id": submission_id,
                    "status": status,
                    "message": message
                })
                return True
            except (WebSocketDisconnect, RuntimeError) as e:
                # Connection lost or closed
                logger.info(f"WebSocket client disconnected for submission {submission_id}: {repr(e)}")
                self.disconnect(submission_id)
                return False
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {repr(e)}")
                self.disconnect(submission_id)
                return False
        return False

manager = ConnectionManager()


@router.websocket("/submission/{submission_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    submission_id: int,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time submission status updates with JWT authentication

     Usage from frontend:
        const ws = new WebSocket(`ws://localhost:8000/ws/submission/${submissionId}?token=${authToken}`);
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log(data.status, data.message);
        };
    """
    # Validate JWT token before accepting connection
    if not token:
        logger.warning(f"WebSocket connection rejected for submission {submission_id}: No token provided")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication required")
    
    try:
        # Decode and validate token
        payload = decode_token(token)
        user_id_str = payload.get("sub")
        
        if not user_id_str:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        
        user_id = int(user_id_str)
        
        # Verify user exists and is active
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid user")
        
        # Check token version for logout/revocation support
        token_version = payload.get("v", 0)
        if token_version != user.token_version:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Token revoked")
        
        # Verify user owns this submission
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            raise WebSocketException(code=status.WS_1003_UNSUPPORTED_DATA, reason="Submission not found")
        
        if submission.user_id != user_id:
            logger.warning(f"WebSocket connection rejected: User {user_id} doesn't own submission {submission_id}")
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Access denied")
        
        logger.info(f"WebSocket authenticated: user {user_id} for submission {submission_id}")
        
    except WebSocketException:
        raise
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        raise WebSocketException(code=status.WS_1011_INTERNAL_ERROR, reason="Authentication failed")

    await manager.connect(submission_id, websocket)
    
    try:
        # Send initial status
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if submission:
            sent = await manager.send_status_update(
                submission_id,
                submission.report_status,
                f"Current status: {submission.report_status}"
            )
            # If initial send failed, client is gone, stop here
            if not sent:
                logger.info(f"Initial status send failed for submission {submission_id}, stopping.")
                return
        
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            
            # Client can request current status
            if data == "get_status":
                submission = db.query(Submission).filter(Submission.id == submission_id).first()
                if submission:
                    await manager.send_status_update(
                        submission_id,
                        submission.report_status,
                        f"Current status: {submission.report_status}"
                    )
    
    except WebSocketDisconnect:
        manager.disconnect(submission_id)
    except RuntimeError as e:
        # Handle "WebSocket is not connected" specifically
        if "not connected" in str(e) or "shutdown" in str(e):
            logger.info(f"WebSocket disconnected (RuntimeError) for submission {submission_id}")
        else:
            logger.error(f"WebSocket runtime error for submission {submission_id}: {repr(e)}")
        manager.disconnect(submission_id)
    except Exception as e:
        logger.error(f"WebSocket error: {repr(e)}")
        manager.disconnect(submission_id)


# Export manager for use in tasks
def get_connection_manager():
    return manager
