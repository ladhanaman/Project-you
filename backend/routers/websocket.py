# routers/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict
import logging
import json




from core.database import get_db
from models import Submission

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])




# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        


    async def connect(self, submission_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[submission_id] = websocket


        logger.info(f"WebSocket connected for submission {submission_id}")
    
    def disconnect(self, submission_id: int):
        if submission_id in self.active_connections:
            del self.active_connections[submission_id]

            logger.info(f"WebSocket disconnected for submission {submission_id}")
    
    async def send_status_update(self, submission_id: int, status: str, message: str):
        """Send status update to connected client"""
        if submission_id in self.active_connections:
            try:
                await self.active_connections[submission_id].send_json({
                    "type": "status_update",
                    "status": status,
                    "message": message
                })
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                self.disconnect(submission_id)

manager = ConnectionManager()


@router.websocket("/submission/{submission_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    submission_id: int,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time submission status updates

     Usage from frontend:
        const ws = new WebSocket(`ws://localhost:8000/ws/submission/${submissionId}`);
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log(data.status, data.message);
        };
    """
    await manager.connect(submission_id, websocket)
    
    try:
        # Send initial status
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if submission:
            await manager.send_status_update(
                submission_id,
                submission.report_status,
                f"Current status: {submission.report_status}"
            )
        
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
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(submission_id)


# Export manager for use in tasks
def get_connection_manager():
    return manager
