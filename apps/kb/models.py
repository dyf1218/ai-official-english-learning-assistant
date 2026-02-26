"""
Models for knowledge base app.
"""

import uuid

from django.contrib.auth.models import User
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from pgvector.django import VectorField

from apps.common.constants import (
    KBSourceType,
    Level,
    RegionStyle,
    Scenario,
    Track,
    UserKBSourceType,
)


class PublicKBCard(models.Model):
    """
    Represents one reusable card in the product-maintained knowledge base.

    These cards contain curated content like templates, rubrics, examples,
    and question patterns for different scenarios and levels.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    subskill = models.CharField(
        max_length=100,
        help_text="Specific subskill this card addresses (e.g., 'impact_statement', 'trade_off')",
    )
    region_style = models.CharField(
        max_length=10,
        choices=RegionStyle.choices,
        default=RegionStyle.EU,
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    when_to_use = models.TextField(
        blank=True,
        null=True,
        help_text="Guidance on when to use this card",
    )
    source_type = models.CharField(
        max_length=30,
        choices=KBSourceType.choices,
        default=KBSourceType.TEMPLATE,
    )
    embedding = VectorField(
        dimensions=1536,
        null=True,
        blank=True,
        help_text="Vector embedding for semantic search",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Public KB Card"
        verbose_name_plural = "Public KB Cards"
        ordering = ["scenario", "level", "subskill"]
        indexes = [
            models.Index(fields=["scenario", "level", "subskill"]),
            models.Index(fields=["track", "scenario"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_scenario_display()} - {self.get_level_display()})"


class UserKBCard(models.Model):
    """
    Represents one user-specific reusable card.

    This includes saved templates from training sessions, uploaded materials,
    and best outputs that users want to reference later.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="kb_cards",
    )
    scenario = models.CharField(
        max_length=30,
        choices=Scenario.choices,
    )
    source_type = models.CharField(
        max_length=30,
        choices=UserKBSourceType.choices,
        default=UserKBSourceType.SAVED_TEMPLATE,
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    embedding = VectorField(
        dimensions=1536,
        null=True,
        blank=True,
        help_text="Vector embedding for semantic search",
    )
    metadata_json = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata like source session, turn, etc.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User KB Card"
        verbose_name_plural = "User KB Cards"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "scenario"]),
            models.Index(fields=["user", "source_type"]),
        ]

    def __str__(self):
        title = self.title or "Untitled"
        return f"{title} - {self.user.username}"