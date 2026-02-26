#!/usr/bin/env python
"""
Script to import KB cards from a JSON file.

Usage:
    python manage.py shell < scripts/import_kb_cards.py
    
Or:
    python scripts/import_kb_cards.py path/to/cards.json
"""

import json
import sys
import os

# Add project to path if running directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    
    import django
    django.setup()

from apps.kb.models import PublicKBCard


def import_cards_from_json(filepath: str):
    """Import KB cards from a JSON file."""
    with open(filepath, "r") as f:
        cards = json.load(f)
    
    created_count = 0
    updated_count = 0
    
    for card_data in cards:
        card, created = PublicKBCard.objects.update_or_create(
            title=card_data.get("title"),
            scenario=card_data.get("scenario"),
            defaults={
                "track": card_data.get("track", "workplace"),
                "level": card_data.get("level", "junior"),
                "subskill": card_data.get("subskill", "general"),
                "region_style": card_data.get("region_style", "EU"),
                "content": card_data.get("content", ""),
                "when_to_use": card_data.get("when_to_use"),
                "source_type": card_data.get("source_type", "template"),
                "is_active": card_data.get("is_active", True),
            }
        )
        
        if created:
            created_count += 1
        else:
            updated_count += 1
    
    print(f"Import complete: {created_count} created, {updated_count} updated")


def create_sample_cards():
    """Create sample KB cards for development."""
    sample_cards = [
        # Project Pitch Cards
        {
            "title": "Problem Statement Template",
            "scenario": "project_pitch",
            "track": "job_search",
            "level": "junior",
            "subskill": "problem_statement",
            "source_type": "template",
            "content": "Our team faced [PROBLEM] that was causing [IMPACT]. This affected [WHO] by [HOW].",
            "when_to_use": "Use at the beginning of your project description to set context.",
        },
        {
            "title": "Impact Statement with Metrics",
            "scenario": "project_pitch",
            "track": "job_search",
            "level": "junior",
            "subskill": "impact_statement",
            "source_type": "template",
            "content": "As a result, we achieved [METRIC] improvement in [AREA], reducing [X] from [Y] to [Z].",
            "when_to_use": "Use when describing the outcome of your project.",
        },
        {
            "title": "Role Clarification Pattern",
            "scenario": "project_pitch",
            "track": "job_search",
            "level": "junior",
            "subskill": "role_clarity",
            "source_type": "template",
            "content": "I was responsible for [SPECIFIC TASKS]. My key contributions included [CONTRIBUTION 1], [CONTRIBUTION 2], and [CONTRIBUTION 3].",
            "when_to_use": "Use to clearly communicate your specific role in a team project.",
        },
        {
            "title": "Trade-off Explanation",
            "scenario": "project_pitch",
            "track": "workplace",
            "level": "mid",
            "subskill": "trade_off",
            "source_type": "template",
            "content": "We chose [SOLUTION A] over [SOLUTION B] because [REASON]. While this meant [TRADE-OFF], the benefit was [ADVANTAGE].",
            "when_to_use": "Use when explaining technical decisions.",
        },
        # PR/Issue Cards
        {
            "title": "Constructive Code Review",
            "scenario": "pr_issue",
            "track": "workplace",
            "level": "junior",
            "subskill": "code_review",
            "source_type": "template",
            "content": "Have you considered [ALTERNATIVE]? I think it might [BENEFIT] because [REASON]. What do you think?",
            "when_to_use": "Use when suggesting improvements in code reviews.",
        },
        {
            "title": "PR Description Structure",
            "scenario": "pr_issue",
            "track": "workplace",
            "level": "junior",
            "subskill": "pr_description",
            "source_type": "template",
            "content": "## What\n[Brief description]\n\n## Why\n[Motivation/context]\n\n## How\n[Implementation approach]\n\n## Testing\n[How it was tested]",
            "when_to_use": "Use as a template for PR descriptions.",
        },
        {
            "title": "Bug Report Format",
            "scenario": "pr_issue",
            "track": "workplace",
            "level": "junior",
            "subskill": "bug_report",
            "source_type": "template",
            "content": "**Expected:** [What should happen]\n**Actual:** [What actually happens]\n**Steps to reproduce:**\n1. [Step 1]\n2. [Step 2]\n\n**Environment:** [Relevant details]",
            "when_to_use": "Use when reporting bugs or issues.",
        },
        {
            "title": "Blocking with Alternatives",
            "scenario": "pr_issue",
            "track": "workplace",
            "level": "mid",
            "subskill": "blocking_feedback",
            "source_type": "template",
            "content": "I have concerns about [ISSUE] because [REASON]. Could we consider [ALTERNATIVE 1] or [ALTERNATIVE 2] instead?",
            "when_to_use": "Use when blocking a PR while offering constructive alternatives.",
        },
        {
            "title": "Approving with Specifics",
            "scenario": "pr_issue",
            "track": "workplace",
            "level": "junior",
            "subskill": "approval",
            "source_type": "template",
            "content": "LGTM! I particularly like how you [SPECIFIC POSITIVE]. The [ASPECT] is clean and well-documented.",
            "when_to_use": "Use when approving PRs to give specific positive feedback.",
        },
        {
            "title": "Requesting Clarification",
            "scenario": "pr_issue",
            "track": "workplace",
            "level": "junior",
            "subskill": "clarification",
            "source_type": "template",
            "content": "Could you help me understand [ASPECT]? I'm not sure about [SPECIFIC QUESTION].",
            "when_to_use": "Use when you need more context about a change.",
        },
    ]
    
    created_count = 0
    for card_data in sample_cards:
        card, created = PublicKBCard.objects.update_or_create(
            title=card_data["title"],
            scenario=card_data["scenario"],
            defaults=card_data
        )
        if created:
            created_count += 1
    
    print(f"Created {created_count} sample KB cards")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        import_cards_from_json(sys.argv[1])
    else:
        print("No file provided. Creating sample cards...")
        create_sample_cards()