from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from models import User, DailyReflection
from schemas import ReflectionCreate, ReflectionResponse
from core.security import get_current_user

router = APIRouter(prefix="/journey", tags=["7-Day Journey"])

@router.post("/submit", response_model=ReflectionResponse)
def submit_reflection(
    reflection: ReflectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if already submitted for this day
    existing = db.query(DailyReflection).filter(
        DailyReflection.user_id == current_user.id,
        DailyReflection.day_number == reflection.day_number
    ).first()

    if existing:
        # Update existing answer
        existing.answer = reflection.answer
        db.commit()
        db.refresh(existing)
        return existing

    # Create new reflection
    new_reflection = DailyReflection(
        user_id=current_user.id,
        day_number=reflection.day_number,
        answer=reflection.answer
    )
    db.add(new_reflection)
    db.commit()
    db.refresh(new_reflection)
    return new_reflection

@router.get("/history", response_model=List[ReflectionResponse])
def get_user_reflections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(DailyReflection).filter(
        DailyReflection.user_id == current_user.id
    ).all()