"""
AI client wrappers for LLM and embeddings.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Optional

from django.conf import settings

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate_structured(self, prompt: str, schema: dict) -> dict:
        """
        Generate structured output from the LLM.

        Args:
            prompt: The full prompt to send to the LLM
            schema: JSON schema for the expected output

        Returns:
            Parsed JSON response from the LLM
        """
        pass


class EmbeddingClient(ABC):
    """Abstract base class for embedding clients."""

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding vector for text.

        Args:
            text: The text to embed

        Returns:
            Embedding vector as list of floats
        """
        pass


class OpenAILLMClient(LLMClient):
    """OpenAI-based LLM client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or settings.LLM_API_KEY
        self.model = model or settings.LLM_MODEL_NAME

        if not self.api_key:
            logger.warning("OpenAI API key not configured")

    def generate_structured(self, prompt: str, schema: dict) -> dict:
        """Generate structured output using OpenAI."""
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")

        try:
            import openai

            client = openai.OpenAI(api_key=self.api_key)

            # Add JSON schema instruction to the prompt
            system_message = (
                "You are an engineering English trainer. "
                "Always respond with valid JSON matching the provided schema."
            )

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=2000,
            )

            content = response.choices[0].message.content
            return json.loads(content)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise


class OpenAIEmbeddingClient(EmbeddingClient):
    """OpenAI-based embedding client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or settings.LLM_API_KEY
        self.model = model or settings.EMBEDDING_MODEL_NAME

        if not self.api_key:
            logger.warning("OpenAI API key not configured")

    def embed_text(self, text: str) -> list[float]:
        """Generate embedding using OpenAI."""
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")

        try:
            import openai

            client = openai.OpenAI(api_key=self.api_key)

            response = client.embeddings.create(
                model=self.model,
                input=text,
            )

            return response.data[0].embedding

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise


class MockLLMClient(LLMClient):
    """Mock LLM client for development and testing."""

    def generate_structured(self, prompt: str, schema: dict) -> dict:
        """Generate mock structured output."""
        logger.info("Using mock LLM client")

        # Return a basic mock response
        return {
            "scores": {
                "clarity": 3,
                "conciseness": 3,
                "correctness": 3,
                "tone": 3,
                "actionability": 3,
            },
            "error_tags": ["too_vague"],
            "rewrites": [
                {
                    "original": "Your text",
                    "better": "Improved version of your text",
                    "why": "This version is more specific and actionable.",
                }
            ],
            "next_task": {
                "type": "follow_up_question",
                "text": "What specific metrics can you add?",
            },
            "templates_to_save": [],
        }


class MockEmbeddingClient(EmbeddingClient):
    """Mock embedding client for development and testing."""

    def embed_text(self, text: str) -> list[float]:
        """Generate mock embedding."""
        logger.info("Using mock embedding client")

        # Return a fixed-size zero vector
        return [0.0] * 1536


def get_llm_client() -> LLMClient:
    """Get the configured LLM client."""
    if settings.LLM_API_KEY:
        return OpenAILLMClient()
    return MockLLMClient()


def get_embedding_client() -> EmbeddingClient:
    """Get the configured embedding client."""
    if settings.LLM_API_KEY:
        return OpenAIEmbeddingClient()
    return MockEmbeddingClient()