# services/ai/utils.py - AI Service Utilities
"""
Utility functions for the AI Insight Engine.
Includes input sanitization and retry logic.
"""
import re
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def sanitize_input(text: str, max_length: int = 255) -> str:
    """
    Sanitize user input to prevent prompt injection attacks
    
    Args:
        text: User-provided text
        max_length: Maximum allowed length
    
    Returns:
        Sanitized text safe for LLM prompts
    """
    if not text:
        return ""
    
    # Truncate to max length
    text = text[:max_length]
    
    # Remove newlines and control characters
    text = re.sub(r'[\n\r\t]', ' ', text)
    
    # Remove potential prompt injection keywords
    dangerous_patterns = [
        r'ignore (previous|all) instructions?',
        r'disregard (previous|all) instructions?',
        r'forget (previous|all) instructions?',
        r'system:',
        r'<\|.*?\|>',  # Special tokens
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Escape special characters
    text = text.strip()
    
    return text


def retry_with_backoff(max_retries: int = 3, initial_delay: float = 1.0, backoff_factor: float = 2.0):
    """
    Decorator for retrying function calls with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_str = str(e).lower()
                    
                    # Don't retry on authentication/authorization errors (fail fast)
                    if any(code in error_str for code in ['401', '403', 'unauthorized', 'forbidden', 'invalid api key', 'authentication failed']):
                        logger.error(f"Authentication error in {func.__name__}, not retrying: {str(e)}")
                        raise
                    
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {delay:.2f} seconds..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            
            raise last_exception
        return wrapper
    return decorator


def get_performance_level(pct: float) -> str:
    """Determine performance level from percentage score"""
    if pct >= 80:
        return "Excellent"
    elif pct >= 60:
        return "Good"
    elif pct >= 40:
        return "Average"
    else:
        return "Needs Improvement"
