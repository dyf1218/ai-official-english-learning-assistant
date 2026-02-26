"""
Models for billing app.
"""

import uuid

from django.contrib.auth.models import User
from django.db import models

from apps.common.constants import UsageFeature


class UsageLedger(models.Model):
    """Stores consumption by plan and feature for quota enforcement."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="usage_ledger",
    )
    feature = models.CharField(
        max_length=30,
        choices=UsageFeature.choices,
    )
    units = models.PositiveIntegerField(default=1)
    related_session_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="Related training session if applicable",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Usage Ledger Entry"
        verbose_name_plural = "Usage Ledger Entries"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "feature"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_feature_display()} ({self.units})"