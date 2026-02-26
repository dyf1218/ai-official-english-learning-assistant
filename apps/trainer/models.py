"""
Models for trainer app - training sessions and turns.
"""

import uuid

from django.contrib.auth.models import User
from django.db import models

from apps.common.constants import (
    ErrorTag,
    Level,
    Scenario,
    Track,
    TurnStatus,
)


class TrainingSession(models.Model):
    """Represents one multi-turn training flow under one scenario."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="training_sessions",
    )
    track = models.CharField(
        max_length=20,
        choices=Track.choices,
        default=Track.WORKPLACE,
    )
    scenario = models.CharField(
        max_length=30,
        choices=Scenario.choices,
    )
    level = models.CharField(
        max_length=20,
        choices=Level.choices,
        default=Level.JUNIOR,
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Training Session"
        verbose_name_plural = "Training Sessions"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "-updated_at"]),
            models.Index(fields=["user", "scenario"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_scenario_display()} ({self.id})"

    @property
    def turn_count(self):
        """Get the number of turns in this session."""
        return self.turns.count()

    @property
    def latest_turn(self):
        """Get the most recent turn."""
        return self.turns.order_by("-turn_index").first()


class TrainingTurn(models.Model):
    """Represents one user submission and one AI response."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        TrainingSession,
        on_delete=models.CASCADE,
        related_name="turns",
    )
    turn_index = models.PositiveIntegerField()
    user_input = models.TextField()
    normalized_intent_json = models.JSONField(default=dict, blank=True)
    retrieved_public_card_ids = models.JSONField(default=list, blank=True)
    retrieved_user_card_ids = models.JSONField(default=list, blank=True)
    llm_output_json = models.JSONField(default=dict, blank=True)
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=TurnStatus.choices,
        default=TurnStatus.SUCCESS,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Training Turn"
        verbose_name_plural = "Training Turns"
        ordering = ["session", "turn_index"]
        constraints = [
            models.UniqueConstraint(
                fields=["session", "turn_index"],
                name="unique_session_turn_index",
            )
        ]
        indexes = [
            models.Index(fields=["session", "turn_index"]),
            models.Index(fields=["session", "created_at"]),
        ]

    def __str__(self):
        return f"Turn {self.turn_index} - Session {self.session_id}"

    @property
    def scores(self):
        """Extract scores from LLM output."""
        return self.llm_output_json.get("scores", {})

    @property
    def error_tags(self):
        """Extract error tags from LLM output."""
        return self.llm_output_json.get("error_tags", [])

    @property
    def rewrites(self):
        """Extract rewrites from LLM output."""
        return self.llm_output_json.get("rewrites", [])

    @property
    def next_task(self):
        """Extract next task from LLM output."""
        return self.llm_output_json.get("next_task", {})

    @property
    def templates_to_save(self):
        """Extract templates to save from LLM output."""
        return self.llm_output_json.get("templates_to_save", [])


class ErrorEvent(models.Model):
    """Represents one structured error tag generated from a turn."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="error_events",
    )
    session = models.ForeignKey(
        TrainingSession,
        on_delete=models.CASCADE,
        related_name="error_events",
    )
    turn = models.ForeignKey(
        TrainingTurn,
        on_delete=models.CASCADE,
        related_name="error_events",
    )
    scenario = models.CharField(
        max_length=30,
        choices=Scenario.choices,
    )
    error_tag = models.CharField(
        max_length=50,
        choices=ErrorTag.choices,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Error Event"
        verbose_name_plural = "Error Events"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "error_tag"]),
        ]

    def __str__(self):
        return f"{self.get_error_tag_display()} - {self.user.username}"