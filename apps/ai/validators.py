"""
Output validation for AI responses.
"""

import logging
from typing import Optional

from apps.common.constants import ErrorTag, SCORING_DIMENSIONS

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when AI output validation fails."""

    pass


def validate_llm_output(output: dict) -> dict:
    """
    Validate and normalize LLM output.

    Args:
        output: Raw output from LLM

    Returns:
        Validated and normalized output

    Raises:
        ValidationError: If output is invalid and cannot be fixed
    """
    if not isinstance(output, dict):
        raise ValidationError("Output must be a dictionary")

    validated = {}

    # Validate scores
    validated["scores"] = _validate_scores(output.get("scores", {}))

    # Validate error tags
    validated["error_tags"] = _validate_error_tags(output.get("error_tags", []))

    # Validate rewrites
    validated["rewrites"] = _validate_rewrites(output.get("rewrites", []))

    # Validate next task
    validated["next_task"] = _validate_next_task(output.get("next_task", {}))

    # Validate templates to save (optional)
    validated["templates_to_save"] = _validate_templates(
        output.get("templates_to_save", [])
    )

    return validated


def _validate_scores(scores: dict) -> dict:
    """Validate and normalize scores."""
    if not isinstance(scores, dict):
        scores = {}

    validated_scores = {}
    for dimension in SCORING_DIMENSIONS:
        value = scores.get(dimension)
        if isinstance(value, (int, float)):
            # Clamp to valid range
            validated_scores[dimension] = max(1, min(5, int(value)))
        else:
            # Default to middle score
            validated_scores[dimension] = 3

    return validated_scores


def _validate_error_tags(error_tags: list) -> list:
    """Validate error tags against controlled vocabulary."""
    if not isinstance(error_tags, list):
        return []

    valid_tags = ErrorTag.values
    validated = []

    for tag in error_tags:
        if isinstance(tag, str) and tag in valid_tags:
            validated.append(tag)
        else:
            logger.warning(f"Ignoring invalid error tag: {tag}")

    return validated


def _validate_rewrites(rewrites: list) -> list:
    """Validate rewrite suggestions."""
    if not isinstance(rewrites, list):
        return []

    validated = []
    for i, rewrite in enumerate(rewrites):
        if i >= 3:  # Max 3 rewrites
            break

        if not isinstance(rewrite, dict):
            continue

        validated_rewrite = {
            "original": str(rewrite.get("original", ""))[:500],
            "better": str(rewrite.get("better", ""))[:500],
            "why": str(rewrite.get("why", ""))[:300],
        }

        # Skip if missing essential fields
        if validated_rewrite["better"]:
            validated.append(validated_rewrite)

    return validated


def _validate_next_task(next_task: dict) -> dict:
    """Validate next task suggestion."""
    if not isinstance(next_task, dict):
        return {
            "type": "follow_up_question",
            "text": "What specific improvements can you make to your text?",
        }

    return {
        "type": str(next_task.get("type", "follow_up_question"))[:50],
        "text": str(next_task.get("text", ""))[:500],
    }


def _validate_templates(templates: list) -> list:
    """Validate templates to save."""
    if not isinstance(templates, list):
        return []

    validated = []
    for template in templates:
        if not isinstance(template, dict):
            continue

        validated_template = {
            "title": str(template.get("title", ""))[:255],
            "content": str(template.get("content", ""))[:1000],
        }

        # Skip if missing content
        if validated_template["content"]:
            validated.append(validated_template)

    return validated


def create_fallback_output(user_input: str) -> dict:
    """
    Create a fallback output when LLM fails.

    Args:
        user_input: The original user input

    Returns:
        A minimal valid output structure
    """
    return {
        "scores": {
            "clarity": 3,
            "conciseness": 3,
            "correctness": 3,
            "tone": 3,
            "actionability": 3,
        },
        "error_tags": [],
        "rewrites": [
            {
                "original": user_input[:100] if len(user_input) > 100 else user_input,
                "better": "We encountered an issue analyzing your text. Please try again.",
                "why": "System is temporarily unable to provide detailed feedback.",
            }
        ],
        "next_task": {
            "type": "follow_up_question",
            "text": "Please try submitting your text again.",
        },
        "templates_to_save": [],
    }