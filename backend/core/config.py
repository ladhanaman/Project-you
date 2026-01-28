# core/config.py - Centralized Configuration Management
"""
Pydantic-based configuration with environment variable validation.
Ensures required variables are set before application starts.
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application configuration loaded from environment variables"""
    
    # Database
    DATABASE_URL: str
    
    # Security
    JWT_SECRET_KEY: str
    

    
    # AI Services (at least one required for production)
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # Report Generation
    REPORT_OUTPUT_DIR: str = "./reports"
    
    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://localhost:5175"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS into a list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    def validate_production(self):
        """Validate that critical variables are set for production deployment"""
        if self.ENVIRONMENT == "production":
            # At least one AI service must be configured
            if not self.OPENAI_API_KEY and not self.GEMINI_API_KEY:
                raise ValueError(
                    "Production requires at least one AI API key (OPENAI_API_KEY or GEMINI_API_KEY)"
                )
            
            # Database should not be localhost in production
            if "localhost" in self.DATABASE_URL or "127.0.0.1" in self.DATABASE_URL:
                raise ValueError(
                    "Production DATABASE_URL should not point to localhost"
                )
            
            # JWT secret should be strong
            if len(self.JWT_SECRET_KEY) < 32:
                raise ValueError(
                    "Production JWT_SECRET_KEY must be at least 32 characters"
                )


# Initialize settings singleton
settings = Settings()

# Validate production environment
if settings.ENVIRONMENT == "production":
    settings.validate_production()
