"""
Celery tasks for reports app.
"""

from celery import shared_task
from datetime import date, timedelta
import logging

from django.contrib.auth.models import User

from apps.reports.services import ReportService

logger = logging.getLogger(__name__)


@shared_task
def generate_weekly_report(user_id: int, period_start: str, period_end: str):
    """
    Generate weekly report for a user.
    
    Args:
        user_id: ID of the user
        period_start: Start date string (YYYY-MM-DD)
        period_end: End date string (YYYY-MM-DD)
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"User not found: {user_id}")
        return
    
    start = date.fromisoformat(period_start)
    end = date.fromisoformat(period_end)
    
    report = ReportService.generate_weekly_report(user, start, end)
    logger.info(f"Generated weekly report for {user.username}: {report.id}")
    return str(report.id)


@shared_task
def generate_all_weekly_reports():
    """
    Generate weekly reports for all active users.
    Called by Celery beat schedule.
    """
    # Get last week bounds
    period_start, period_end = ReportService.get_last_week_bounds()
    
    # Get all users who had activity in the period
    from apps.trainer.models import TrainingTurn
    
    active_user_ids = (
        TrainingTurn.objects
        .filter(
            created_at__date__gte=period_start,
            created_at__date__lte=period_end,
        )
        .values_list("session__user_id", flat=True)
        .distinct()
    )
    
    count = 0
    for user_id in active_user_ids:
        generate_weekly_report.delay(
            user_id,
            period_start.isoformat(),
            period_end.isoformat(),
        )
        count += 1
    
    logger.info(f"Queued {count} weekly reports for generation")
    return f"Queued {count} reports"