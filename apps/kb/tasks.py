"""
Celery tasks for KB app.
"""

from celery import shared_task
import logging

from apps.ai.clients import get_embedding_client

logger = logging.getLogger(__name__)


@shared_task
def embed_public_kb_card(card_id: str):
    """
    Generate and store embedding for a public KB card.
    
    Args:
        card_id: UUID of the card to embed
    """
    from apps.kb.models import PublicKBCard
    
    try:
        card = PublicKBCard.objects.get(id=card_id)
    except PublicKBCard.DoesNotExist:
        logger.error(f"Public KB card not found: {card_id}")
        return
    
    try:
        client = get_embedding_client()
        text = f"{card.title}\n{card.content}"
        if card.when_to_use:
            text += f"\n{card.when_to_use}"
        
        embedding = client.embed_text(text)
        card.embedding = embedding
        card.save(update_fields=["embedding"])
        
        logger.info(f"Embedded public KB card: {card_id}")
    except Exception as e:
        logger.error(f"Failed to embed public KB card {card_id}: {e}")


@shared_task
def embed_user_kb_card(card_id: str):
    """
    Generate and store embedding for a user KB card.
    
    Args:
        card_id: UUID of the card to embed
    """
    from apps.kb.models import UserKBCard
    
    try:
        card = UserKBCard.objects.get(id=card_id)
    except UserKBCard.DoesNotExist:
        logger.error(f"User KB card not found: {card_id}")
        return
    
    try:
        client = get_embedding_client()
        text = f"{card.title or ''}\n{card.content}"
        
        embedding = client.embed_text(text)
        card.embedding = embedding
        card.save(update_fields=["embedding"])
        
        logger.info(f"Embedded user KB card: {card_id}")
    except Exception as e:
        logger.error(f"Failed to embed user KB card {card_id}: {e}")


@shared_task
def backfill_embeddings():
    """
    Backfill embeddings for all KB cards that don't have one.
    """
    from apps.kb.models import PublicKBCard, UserKBCard
    
    # Public cards
    public_cards = PublicKBCard.objects.filter(embedding__isnull=True, is_active=True)
    public_count = public_cards.count()
    logger.info(f"Backfilling {public_count} public KB cards")
    
    for card in public_cards:
        embed_public_kb_card.delay(str(card.id))
    
    # User cards
    user_cards = UserKBCard.objects.filter(embedding__isnull=True)
    user_count = user_cards.count()
    logger.info(f"Backfilling {user_count} user KB cards")
    
    for card in user_cards:
        embed_user_kb_card.delay(str(card.id))
    
    return f"Queued {public_count} public and {user_count} user cards for embedding"