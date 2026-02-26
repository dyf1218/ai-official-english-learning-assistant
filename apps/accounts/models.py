"""
Account models for SE English Trainer.
"""

import uuid

from django.contrib.auth.models import User
from django.db import models

from apps.common.constants import (
    DEFAULT_MONTHLY_TURN_LIMIT,
    PlanStatus,
    PlanType,
)


class UserProfile(models.Model):
    """Extended user profile with plan and usage information."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    plan = models.CharField(
        max_length=20,
        choices=PlanType.choices,
        default=PlanType.FREE,
    )
    plan_status = models.CharField(
        max_length=20,
        choices=PlanStatus.choices,
        default=PlanStatus.ACTIVE,
    )
    monthly_turn_limit = models.PositiveIntegerField(
        default=DEFAULT_MONTHLY_TURN_LIMIT[PlanType.FREE],
    )
    monthly_turn_used = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username} - {self.plan}"

    @property
    def turns_remaining(self):
        """Calculate remaining turns for current month."""
        return max(0, self.monthly_turn_limit - self.monthly_turn_used)

    @property
    def can_submit_turn(self):
        """Check if user can submit more turns."""
        return (
            self.plan_status == PlanStatus.ACTIVE
            and self.turns_remaining > 0
        )

    def reset_monthly_usage(self):
        """Reset monthly usage counters."""
        self.monthly_turn_used = 0
        self.save(update_fields=["monthly_turn_used", "updated_at"])

    def increment_usage(self, count=1):
        """Increment usage counter."""
        self.monthly_turn_used += count
        self.save(update_fields=["monthly_turn_used", "updated_at"])

    def update_plan(self, new_plan: str):
        """Update user plan and adjust limits."""
        self.plan = new_plan
        self.monthly_turn_limit = DEFAULT_MONTHLY_TURN_LIMIT.get(
            new_plan, DEFAULT_MONTHLY_TURN_LIMIT[PlanType.FREE]
        )
        self.save(update_fields=["plan", "monthly_turn_limit", "updated_at"])