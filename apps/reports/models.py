"""
Models for reports app.
"""

import uuid

from django.contrib.auth.models import User
from django.db import models


class WeeklyReport(models.Model):
    """Stores report snapshots for one reporting period."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="weekly_reports",
    )
    period_start = models.DateField()
    period_end = models.DateField()
    summary_json = models.JSONField(
        default=dict,
        help_text="Structured report data including stats and insights",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Weekly Report"
        verbose_name_plural = "Weekly Reports"
        ordering = ["-period_end"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "period_start", "period_end"],
                name="unique_user_report_period",
            )
        ]
        indexes = [
            models.Index(fields=["user", "-period_end"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.period_start} to {self.period_end}"

    @property
    def total_turns(self) -> int:
        """Get total turns in this period."""
        return self.summary_json.get("total_turns", 0)

    @property
    def top_error_tags(self) -> list:
        """Get top error tags for this period."""
        return self.summary_json.get("top_error_tags", [])

    @property
    def average_scores(self) -> dict:
        """Get average scores for this period."""
        return self.summary_json.get("average_scores", {})

    @property
    def recommended_focus(self) -> str:
        """Get recommended focus area."""
        return self.summary_json.get("recommended_focus", "")