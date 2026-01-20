# core/monitoring.py - Sentry Error Tracking
"""
Sentry error tracking and monitoring utilities.
"""
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def init_sentry():
    """Initialize Sentry error tracking"""
    sentry_dsn = os.getenv("SENTRY_DSN")
    environment = os.getenv("ENVIRONMENT", "development")
    
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            before_send=before_send_filter,
        )
        logger.info(f"Sentry initialized for environment: {environment}")
    else:
        logger.warning("SENTRY_DSN not set. Error tracking disabled.")


def before_send_filter(event, hint):
    """Filter events before sending to Sentry"""
    if "url" in event.get("request", {}):
        if "/health" in event["request"]["url"]:
            return None
    return event


def capture_exception(error: Exception, context: dict = None):
    """Capture exception with additional context"""
    if context:
        sentry_sdk.set_context("custom", context)
    sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", context: dict = None):
    """Capture message with additional context"""
    if context:
        sentry_sdk.set_context("custom", context)
    sentry_sdk.capture_message(message, level=level)
