"""
Service layer for billing app.
"""

import logging
from typing import Optional

from django.contrib.auth.models import User

from apps.billing.models import UsageLedger
from apps.common.constants import UsageFeature

logger = logging.getLogger(__name__)


class QuotaExceededError(Exception):
    """Raised when user has exceeded their quota."""

    pass


class UsageService:
    """Service for managing usage and quotas."""

    @staticmethod
    def can_submit_turn(user: User) -> bool:
        """
        Check if user can submit a turn.
        
        Args:
            user: The user to check
            
        Returns:
            True if user can submit, False otherwise
        """
        profile = user.profile
        return profile.monthly_turn_used < profile.monthly_turn_limit

    @staticmethod
    def ensure_can_submit(user: User):
        """
        Ensure user can submit a turn, raise if not.
        
        Args:
            user: The user to check
            
        Raises:
            QuotaExceededError: If user has exceeded their quota
        """
        if not UsageService.can_submit_turn(user):
            raise QuotaExceededError(
                f"Monthly turn limit reached ({user.profile.monthly_turn_limit}). "
                "Please upgrade your plan or wait until next month."
            )

    @staticmethod
    def consume_turn(user: User, session_id: Optional[str] = None):
        """
        Record turn consumption and update user's usage.
        
        Args:
            user: The user who submitted the turn
            session_id: Optional related session ID
        """
        # Create ledger entry
        UsageLedger.objects.create(
            user=user,
            feature=UsageFeature.TURN_SUBMIT,
            units=1,
            related_session_id=session_id,
        )
        
        # Update profile
        profile = user.profile
        profile.monthly_turn_used += 1
        profile.save(update_fields=["monthly_turn_used"])
        
        logger.info(
            f"User {user.username} consumed 1 turn. "
            f"Usage: {profile.monthly_turn_used}/{profile.monthly_turn_limit}"
        )

    @staticmethod
    def record_usage(
        user: User,
        feature: str,
        units: int = 1,
        related_session_id: Optional[str] = None,
    ):
        """
        Record general usage for tracking purposes.
        
        Args:
            user: The user
            feature: The feature being used
            units: Number of units consumed
            related_session_id: Optional related session ID
        """
        UsageLedger.objects.create(
            user=user,
            feature=feature,
            units=units,
            related_session_id=related_session_id,
        )

    @staticmethod
    def get_current_usage(user: User) -> dict:
        """
        Get current usage stats for a user.
        
        Args:
            user: The user
            
        Returns:
            Dict with usage information
        """
        profile = user.profile
        return {
            "plan": profile.plan,
            "plan_status": profile.plan_status,
            "monthly_turn_used": profile.monthly_turn_used,
            "monthly_turn_limit": profile.monthly_turn_limit,
            "turns_remaining": profile.turns_remaining,
            "can_submit": profile.can_submit_turn,
        }

    @staticmethod
    def reset_monthly_usage(user: User):
        """
        Reset monthly usage for a user.
        Called at the start of a new billing period.
        
        Args:
            user: The user to reset
        """
        profile = user.profile
        profile.monthly_turn_used = 0
        profile.save(update_fields=["monthly_turn_used"])
        logger.info(f"Reset monthly usage for {user.username}")