# tasks/__init__.py
"""Background tasks"""
from .report_tasks import generate_insights_and_report_task, generate_fallback_insights

__all__ = ["generate_insights_and_report_task", "generate_fallback_insights"]
