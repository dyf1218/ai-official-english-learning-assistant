"""
Service layer for trainer app.
"""

import logging
import time
from dataclasses import dataclass
from typing import Optional

from django.contrib.auth.models import User
from django.db import transaction

from apps.common.constants import ErrorTag, TurnStatus
from apps.trainer.models import ErrorEvent, TrainingSession, TrainingTurn

logger = logging.getLogger(__name__)


class QuotaExceededError(Exception):
    """Raised when user has exceeded their usage quota."""

    pass


@dataclass
class TurnResult:
    """Result of a turn submission."""

    turn: TrainingTurn
    success: bool
    error_message: Optional[str] = None


class UsageService:
    """Service for managing usage quotas."""

    @staticmethod
    def check_quota(user: User) -> bool:
        """Check if user can submit more turns."""
        return user.profile.can_submit_turn

    @staticmethod
    def ensure_can_submit(user: User) -> None:
        """Ensure user can submit, raise error if not."""
        if not UsageService.check_quota(user):
            raise QuotaExceededError(
                f"Monthly limit of {user.profile.monthly_turn_limit} turns reached. "
                "Please upgrade your plan or wait until next month."
            )

    @staticmethod
    def consume_turn(user: User, turn: TrainingTurn) -> None:
        """Consume a turn from user's quota."""
        user.profile.increment_usage(1)
        logger.info(
            f"User {user.username} consumed 1 turn. "
            f"Used: {user.profile.monthly_turn_used}/{user.profile.monthly_turn_limit}"
        )


class SessionService:
    """Service for managing training sessions."""

    @staticmethod
    def create_session(
        user: User,
        scenario: str,
        track: str,
        level: str,
        title: Optional[str] = None,
    ) -> TrainingSession:
        """Create a new training session."""
        session = TrainingSession.objects.create(
            user=user,
            scenario=scenario,
            track=track,
            level=level,
            title=title,
        )
        logger.info(f"Created session {session.id} for user {user.username}")
        return session

    @staticmethod
    def get_session(session_id: str, user: User) -> Optional[TrainingSession]:
        """Get a session with authorization check."""
        try:
            return TrainingSession.objects.get(id=session_id, user=user)
        except TrainingSession.DoesNotExist:
            return None

    @staticmethod
    def archive_session(session: TrainingSession) -> None:
        """Archive a session."""
        session.is_archived = True
        session.save(update_fields=["is_archived", "updated_at"])

    @staticmethod
    def list_user_sessions(user: User, include_archived: bool = False):
        """List all sessions for a user."""
        queryset = TrainingSession.objects.filter(user=user)
        if not include_archived:
            queryset = queryset.filter(is_archived=False)
        return queryset.order_by("-updated_at")


class ErrorEventService:
    """Service for managing error events."""

    @staticmethod
    def from_turn(turn: TrainingTurn) -> list[ErrorEvent]:
        """Create error events from a turn's error tags."""
        error_tags = turn.llm_output_json.get("error_tags", [])
        events = []

        for tag in error_tags:
            # Validate the tag is in our controlled vocabulary
            if tag in ErrorTag.values:
                event = ErrorEvent.objects.create(
                    user=turn.session.user,
                    session=turn.session,
                    turn=turn,
                    scenario=turn.session.scenario,
                    error_tag=tag,
                )
                events.append(event)
            else:
                logger.warning(f"Unknown error tag: {tag}")

        logger.info(f"Created {len(events)} error events for turn {turn.id}")
        return events


class TurnSubmissionService:
    """Service for handling turn submissions."""

    def __init__(self):
        # These will be injected or configured
        self.llm_service = None
        self.retrieval_service = None

    def execute(
        self,
        session: TrainingSession,
        user_input: str,
    ) -> TurnResult:
        """
        Execute a turn submission.

        This is the main entry point for processing user input and generating
        AI feedback.
        """
        start_time = time.time()

        try:
            # Check quota
            UsageService.ensure_can_submit(session.user)

            # Get next turn index
            turn_index = session.turns.count() + 1

            # For now, create a mock response
            # This will be replaced with actual AI integration
            llm_output = self._generate_mock_response(session, user_input)

            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)

            # Create the turn
            with transaction.atomic():
                turn = TrainingTurn.objects.create(
                    session=session,
                    turn_index=turn_index,
                    user_input=user_input,
                    normalized_intent_json={
                        "scenario": session.scenario,
                        "retrieval_query": user_input[:200],
                    },
                    retrieved_public_card_ids=[],
                    retrieved_user_card_ids=[],
                    llm_output_json=llm_output,
                    latency_ms=latency_ms,
                    status=TurnStatus.SUCCESS,
                )

                # Create error events
                ErrorEventService.from_turn(turn)

                # Consume usage
                UsageService.consume_turn(session.user, turn)

                # Update session timestamp
                session.save(update_fields=["updated_at"])

            logger.info(
                f"Turn {turn.id} submitted successfully in {latency_ms}ms"
            )
            return TurnResult(turn=turn, success=True)

        except QuotaExceededError as e:
            logger.warning(f"Quota exceeded for user {session.user.username}")
            return TurnResult(
                turn=None,
                success=False,
                error_message=str(e),
            )
        except Exception as e:
            logger.exception(f"Error processing turn: {e}")
            return TurnResult(
                turn=None,
                success=False,
                error_message="An error occurred while processing your submission. Please try again.",
            )

    def _generate_mock_response(
        self,
        session: TrainingSession,
        user_input: str,
    ) -> dict:
        """
        Generate a mock AI response for development.

        This will be replaced with actual LLM integration.
        """
        # Determine mock error tags based on input
        error_tags = []
        if len(user_input) < 50:
            error_tags.append("too_vague")
        if len(user_input) > 500:
            error_tags.append("too_long")
        if "%" not in user_input and "number" not in user_input.lower():
            error_tags.append("missing_metric")

        return {
            "scores": {
                "clarity": 3,
                "conciseness": 4,
                "correctness": 3,
                "tone": 4,
                "actionability": 3,
            },
            "error_tags": error_tags,
            "rewrites": [
                {
                    "original": user_input[:100] + "..." if len(user_input) > 100 else user_input,
                    "better": f"[Improved version of your text would appear here]",
                    "why": "This rewrite adds specific metrics and clearer impact statement.",
                }
            ],
            "next_task": {
                "type": "follow_up_question",
                "text": "What specific metrics or outcomes can you add to strengthen your statement?",
            },
            "templates_to_save": [
                {
                    "title": "Impact Statement Template",
                    "content": "I [action] which resulted in [metric] improvement in [area].",
                }
            ],
        }