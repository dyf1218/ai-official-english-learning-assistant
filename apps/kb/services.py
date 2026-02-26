"""
Service layer for knowledge base app.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from django.contrib.auth.models import User
from django.db.models import QuerySet

from apps.common.constants import Scenario, UserKBSourceType
from apps.kb.models import PublicKBCard, UserKBCard

logger = logging.getLogger(__name__)


@dataclass
class RetrievalBundle:
    """Bundle of retrieved KB cards."""

    user_cards: list[UserKBCard]
    public_cards: list[PublicKBCard]

    @property
    def user_ids(self) -> list[str]:
        return [str(card.id) for card in self.user_cards]

    @property
    def public_ids(self) -> list[str]:
        return [str(card.id) for card in self.public_cards]

    @property
    def all_cards(self) -> list:
        """Return all cards merged."""
        return self.user_cards + self.public_cards


class RetrievalService:
    """Service for retrieving relevant KB cards."""

    def __init__(self, embedding_client=None):
        self.embedding_client = embedding_client

    def retrieve(
        self,
        user: User,
        scenario: str,
        level: str,
        normalized: dict,
        user_top_k: int = 3,
        public_top_k: int = 5,
    ) -> RetrievalBundle:
        """
        Retrieve relevant KB cards for a turn submission.

        Args:
            user: The user making the request
            scenario: Current training scenario
            level: User's experience level
            normalized: Normalized intent from user input
            user_top_k: Maximum number of user cards to retrieve
            public_top_k: Maximum number of public cards to retrieve

        Returns:
            RetrievalBundle containing user and public cards
        """
        query_text = normalized.get("retrieval_query", "")
        subskills = normalized.get("subskills", [])

        # Get query embedding if embedding client is available
        query_embedding = None
        if self.embedding_client and query_text:
            try:
                query_embedding = self.embedding_client.embed_text(query_text)
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")

        # Retrieve cards
        user_cards = self._search_user_cards(
            user=user,
            scenario=scenario,
            query_embedding=query_embedding,
            top_k=user_top_k,
        )

        public_cards = self._search_public_cards(
            scenario=scenario,
            level=level,
            subskills=subskills,
            query_embedding=query_embedding,
            top_k=public_top_k,
        )

        logger.info(
            f"Retrieved {len(user_cards)} user cards and "
            f"{len(public_cards)} public cards for {scenario}"
        )

        return RetrievalBundle(user_cards=user_cards, public_cards=public_cards)

    def _search_user_cards(
        self,
        user: User,
        scenario: str,
        query_embedding: Optional[list] = None,
        top_k: int = 3,
    ) -> list[UserKBCard]:
        """Search user KB cards."""
        queryset = UserKBCard.objects.filter(
            user=user,
            scenario=scenario,
        )

        if query_embedding:
            # Use vector similarity search
            # Note: This requires pgvector extension
            # For now, fall back to simple ordering
            pass

        return list(queryset.order_by("-created_at")[:top_k])

    def _search_public_cards(
        self,
        scenario: str,
        level: str,
        subskills: list[str],
        query_embedding: Optional[list] = None,
        top_k: int = 5,
    ) -> list[PublicKBCard]:
        """Search public KB cards."""
        queryset = PublicKBCard.objects.filter(
            scenario=scenario,
            level=level,
            is_active=True,
        )

        # Filter by subskills if provided
        if subskills:
            queryset = queryset.filter(subskill__in=subskills)

        if query_embedding:
            # Use vector similarity search
            # Note: This requires pgvector extension
            # For now, fall back to simple ordering
            pass

        return list(queryset.order_by("-updated_at")[:top_k])


class TemplateService:
    """Service for managing user templates."""

    @staticmethod
    def save_template(
        user: User,
        scenario: str,
        content: str,
        title: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> UserKBCard:
        """
        Save a template to user's KB.

        Args:
            user: The user saving the template
            scenario: The scenario this template is for
            content: The template content
            title: Optional title for the template
            metadata: Optional metadata (e.g., source session, turn)

        Returns:
            The created UserKBCard
        """
        card = UserKBCard.objects.create(
            user=user,
            scenario=scenario,
            source_type=UserKBSourceType.SAVED_TEMPLATE,
            title=title,
            content=content,
            metadata_json=metadata or {},
        )
        logger.info(f"Saved template {card.id} for user {user.username}")
        return card

    @staticmethod
    def list_templates(
        user: User,
        scenario: Optional[str] = None,
    ) -> QuerySet[UserKBCard]:
        """
        List user's saved templates.

        Args:
            user: The user whose templates to list
            scenario: Optional scenario filter

        Returns:
            QuerySet of UserKBCards
        """
        queryset = UserKBCard.objects.filter(
            user=user,
            source_type=UserKBSourceType.SAVED_TEMPLATE,
        )

        if scenario:
            queryset = queryset.filter(scenario=scenario)

        return queryset.order_by("-created_at")

    @staticmethod
    def delete_template(template_id: str, user: User) -> bool:
        """
        Delete a user's template.

        Args:
            template_id: The template ID to delete
            user: The user who owns the template

        Returns:
            True if deleted, False if not found
        """
        try:
            card = UserKBCard.objects.get(id=template_id, user=user)
            card.delete()
            logger.info(f"Deleted template {template_id} for user {user.username}")
            return True
        except UserKBCard.DoesNotExist:
            return False

    @staticmethod
    def get_template(template_id: str, user: User) -> Optional[UserKBCard]:
        """
        Get a specific template.

        Args:
            template_id: The template ID
            user: The user who owns the template

        Returns:
            UserKBCard or None
        """
        try:
            return UserKBCard.objects.get(id=template_id, user=user)
        except UserKBCard.DoesNotExist:
            return None