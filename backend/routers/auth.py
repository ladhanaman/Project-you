# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta

from core.database import get_db
from models import User
from schemas import UserCreate, UserLogin, Token, UserResponse, OnboardingData
from core.security import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)
import secrets
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
def signup(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account
    
    Rate limited to 3 requests per minute
    Returns JWT token for immediate login
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    verification_token = secrets.token_urlsafe(32)
    
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        verification_token=verification_token
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate tokens with token version
    access_token = create_access_token(new_user.id, new_user.token_version)
    refresh_token = create_refresh_token(new_user.id, new_user.token_version)
    
    # TODO: Send verification email
    # send_verification_email(new_user.email, verification_token)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(new_user)
    }


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token
    
    Rate limited to 5 requests per minute
    """
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate tokens with token version
    access_token = create_access_token(user.id, user.token_version)
    refresh_token = create_refresh_token(user.id, user.token_version)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information
    """
    return current_user


@router.post("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verify user email with token
    """
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    user.email_verified = True
    user.verification_token = None
    db.commit()
    
    return {"message": "Email verified successfully"}


@router.post("/refresh", response_model=Token)
@limiter.limit("10/minute")
def refresh_token(request: Request, refresh_token: str, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token
    """
    try:
        payload = decode_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        token_version = payload.get("v", 0)
        if token_version != user.token_version:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        new_access_token = create_access_token(user.id, user.token_version)
        new_refresh_token = create_refresh_token(user.id, user.token_version)
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user)
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


@router.post("/onboarding")
def complete_onboarding(
    data: OnboardingData,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete user onboarding with NEW profile information
    """
    current_user.first_name = data.first_name
    current_user.last_name = data.last_name
    current_user.date_of_birth = data.date_of_birth
    current_user.gender = data.gender                 # <--- NEW
    current_user.city = data.city
    current_user.address = data.address
    current_user.occupation = data.occupation
    current_user.education = data.education           # <--- NEW
    current_user.industry_domain = data.industry_domain # <--- NEW
    current_user.hobbies = data.hobbies
    
    current_user.onboarding_completed = True
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "Onboarding completed successfully",
        "user": UserResponse.model_validate(current_user)
    }

@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user by invalidating all existing tokens
    """
    current_user.token_version += 1
    db.commit()
    
    return {
        "message": "Successfully logged out",
        "detail": "All tokens have been invalidated"
    }