# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime
import traceback

from core.database import Base, engine
from core.config import settings
from routers import auth, tests, submissions, websocket, journey
from core.monitoring import init_sentry

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Sentry monitoring
init_sentry()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create database tables
Base.metadata.create_all(bind=engine)

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Industry Readiness Assessment API",
    description="Multi-test platform with JWT authentication for technical assessments",
    version="2.0.0"
)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Global exception handler to ensure CORS headers on all responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler that ensures CORS headers are sent
    even when unexpected errors occur
    """
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.ENVIRONMENT == "development" else "An unexpected error occurred"
        },
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Credentials": "true",
        }
    )

# ============================================================================
# CACHE CONTROL MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    """
    Add appropriate cache headers to prevent browser caching of user-specific data
    """
    response = await call_next(request)
    
    # PDF downloads can be cached privately for 1 hour
    if request.url.path.endswith("/download"):
        response.headers["Cache-Control"] = "private, max-age=3600"
    
    # API endpoints must not be cached (user-specific data)
    elif request.url.path.startswith(("/submissions", "/auth", "/tests")):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    
    # Health check can cache for 30 seconds
    elif request.url.path == "/health":
        response.headers["Cache-Control"] = "public, max-age=30"
    
    return response

# ============================================================================
# HTTPS REDIRECT MIDDLEWARE (Production Security)
# ============================================================================

@app.middleware("http")
async def https_redirect(request: Request, call_next):
    """
    Redirect HTTP to HTTPS in production.
    Checks X-Forwarded-Proto header (set by reverse proxies like nginx/cloudflare)
    """
    # Only enforce in production
    if settings.ENVIRONMENT == "production":
        # Default to http when header is missing to trigger redirect
        forwarded_proto = request.headers.get("x-forwarded-proto", "http")
        if forwarded_proto != "https":
            url = request.url.replace(scheme="https")
            return JSONResponse(
                status_code=301,
                headers={"Location": str(url)},
                content={"detail": "Redirecting to HTTPS"}
            )
    
    return await call_next(request)

# CORS middleware - environment-aware origins
CORS_ORIGINS = settings.cors_origins_list

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(tests.router)
app.include_router(submissions.router)
app.include_router(websocket.router)
app.include_router(journey.router)

# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Industry Readiness Assessment Backend",
        "version": "2.0.0"
    }


@app.get("/", tags=["Root"])
def root():
    """Root endpoint with API information"""
    return {
        "message": "Industry Readiness Assessment API - Multi-Test Platform",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "auth": {
                "signup": "/auth/signup",
                "login": "/auth/login",
                "me": "/auth/me"
            },
            "tests": {
                "list": "/tests",
                "questions": "/tests/{test_id}/questions"
            },
            "submissions": {
                "submit": "/submissions",
                "get": "/submissions/{submission_id}",
                "download": "/submissions/{submission_id}/download"
            }
        },
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)