"""
Service layer for reports app.
"""

import logging
from collections import Counter
from datetime import date, timedelta
from typing import Optional

from django.contrib.auth.models import User
from django.db.models import Avg

from apps.common.constants import ErrorTag, SCORING_DIMENSIONS
from apps.reports.models import WeeklyReport
from apps.trainer.models import ErrorEvent, TrainingTurn

logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating and managing reports."""

    @staticmethod
    def get_latest_report(user: User) -> Optional[WeeklyReport]:
        """Get the most recent report for a user."""
        return WeeklyReport.objects.filter(user=user).first()

    @staticmethod
    def get_report_for_period(
        user: User,
        period_start: date,
        period_end: date,
    ) -> Optional[WeeklyReport]:
        """Get report for a specific period."""
        try:
            return WeeklyReport.objects.get(
                user=user,
                period_start=period_start,
                period_end=period_end,
            )
        except WeeklyReport.DoesNotExist:
            return None

    @staticmethod
    def generate_weekly_report(
        user: User,
        period_start: date,
        period_end: date,
    ) -> WeeklyReport:
        """
        Generate a weekly report for a user.

        Args:
            user: The user to generate report for
            period_start: Start of the reporting period
            period_end: End of the reporting period

        Returns:
            The created or updated WeeklyReport
        """
        # Get turns for the period
        turns = TrainingTurn.objects.filter(
            session__user=user,
            created_at__date__gte=period_start,
            created_at__date__lte=period_end,
        )

        # Get error events for the period
        error_events = ErrorEvent.objects.filter(
            user=user,
            created_at__date__gte=period_start,
            created_at__date__lte=period_end,
        )

        # Calculate statistics
        total_turns = turns.count()

        # Calculate average scores
        average_scores = ReportService._calculate_average_scores(turns)

        # Get top error tags
        top_error_tags = ReportService._get_top_error_tags(error_events)

        # Determine recommended focus
        recommended_focus = ReportService._determine_focus(
            average_scores, top_error_tags
        )

        # Build summary JSON
        summary = {
            "total_turns": total_turns,
            "average_scores": average_scores,
            "top_error_tags": top_error_tags,
            "recommended_focus": recommended_focus,
            "turns_by_scenario": ReportService._get_turns_by_scenario(turns),
        }

        # Create or update report
        report, created = WeeklyReport.objects.update_or_create(
            user=user,
            period_start=period_start,
            period_end=period_end,
            defaults={"summary_json": summary},
        )

        action = "Created" if created else "Updated"
        logger.info(f"{action} weekly report for {user.username}: {period_start} to {period_end}")

        return report

    @staticmethod
    def _calculate_average_scores(turns) -> dict:
        """Calculate average scores across all turns."""
        if not turns.exists():
            return {}

        scores = {dim: [] for dim in SCORING_DIMENSIONS}

        for turn in turns:
            turn_scores = turn.llm_output_json.get("scores", {})
            for dim in SCORING_DIMENSIONS:
                if dim in turn_scores:
                    scores[dim].append(turn_scores[dim])

        return {
            dim: round(sum(values) / len(values), 2) if values else 0
            for dim, values in scores.items()
        }

    @staticmethod
    def _get_top_error_tags(error_events, limit: int = 5) -> list:
        """Get the most common error tags."""
        tag_counts = Counter(event.error_tag for event in error_events)
        return [
            {"tag": tag, "count": count, "label": ErrorTag(tag).label}
            for tag, count in tag_counts.most_common(limit)
        ]

    @staticmethod
    def _get_turns_by_scenario(turns) -> dict:
        """Get turn counts by scenario."""
        scenario_counts = Counter(turn.session.scenario for turn in turns)
        return dict(scenario_counts)

    @staticmethod
    def _determine_focus(average_scores: dict, top_error_tags: list) -> str:
        """Determine recommended focus area based on scores and errors."""
        # Find lowest scoring dimension
        if average_scores:
            lowest_dim = min(average_scores, key=average_scores.get)
            lowest_score = average_scores[lowest_dim]

            if lowest_score < 3.5:
                focus_messages = {
                    "clarity": "Focus on making your communication clearer and easier to understand.",
                    "conciseness": "Work on being more concise - remove unnecessary words.",
                    "correctness": "Pay attention to grammar and technical accuracy.",
                    "tone": "Adjust your tone to be more professional and appropriate.",
                    "actionability": "Make sure your messages lead to clear next steps.",
                }
                return focus_messages.get(lowest_dim, f"Improve your {lowest_dim}.")

        # Fall back to most common error
        if top_error_tags:
            top_tag = top_error_tags[0]["tag"]
            error_focus = {
                "too_vague": "Add more specific details to your communication.",
                "too_long": "Practice being more concise.",
                "missing_metric": "Include quantifiable metrics and data.",
                "missing_role": "Clarify your role and contributions.",
                "missing_impact": "Highlight the impact of your work.",
                "missing_next_step": "Always include clear next steps.",
                "weak_tradeoff": "Explain trade-offs in your technical decisions.",
                "tone_too_direct": "Soften your tone for better collaboration.",
                "tone_too_soft": "Be more assertive in your requests.",
                "unclear_request": "Make your requests more explicit.",
                "unclear_expected_actual": "Clearly state expected vs actual behavior.",
            }
            return error_focus.get(top_tag, "Keep practicing!")

        return "Keep up the good work! Continue practicing to maintain your skills."

    @staticmethod
    def get_current_week_bounds() -> tuple[date, date]:
        """Get the start and end dates for the current week."""
        today = date.today()
        # Week starts on Monday
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return start, end

    @staticmethod
    def get_last_week_bounds() -> tuple[date, date]:
        """Get the start and end dates for last week."""
        today = date.today()
        start = today - timedelta(days=today.weekday() + 7)
        end = start + timedelta(days=6)
        return start, end