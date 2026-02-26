"""
Prompt templates for AI interactions.
"""

from apps.common.constants import Scenario

# Output JSON schema for LLM responses
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "scores": {
            "type": "object",
            "properties": {
                "clarity": {"type": "integer", "minimum": 1, "maximum": 5},
                "conciseness": {"type": "integer", "minimum": 1, "maximum": 5},
                "correctness": {"type": "integer", "minimum": 1, "maximum": 5},
                "tone": {"type": "integer", "minimum": 1, "maximum": 5},
                "actionability": {"type": "integer", "minimum": 1, "maximum": 5},
            },
            "required": ["clarity", "conciseness", "correctness", "tone", "actionability"],
        },
        "error_tags": {
            "type": "array",
            "items": {"type": "string"},
        },
        "rewrites": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "original": {"type": "string"},
                    "better": {"type": "string"},
                    "why": {"type": "string"},
                },
                "required": ["original", "better", "why"],
            },
        },
        "next_task": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "text": {"type": "string"},
            },
            "required": ["type", "text"],
        },
        "templates_to_save": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["title", "content"],
            },
        },
    },
    "required": ["scores", "error_tags", "rewrites", "next_task"],
}

# Base system prompt
SYSTEM_PROMPT = """You are an expert engineering English trainer specializing in helping software engineers communicate more effectively in professional settings.

Your role is to:
1. Analyze the user's written communication
2. Identify areas for improvement specific to engineering contexts
3. Provide actionable, specific feedback
4. Suggest improved versions with clear explanations

Key principles:
- Focus on engineering clarity, not general English
- Avoid generic encouragement; be specific and practical
- Prefer short, clear explanations
- Output no more than 3 rewrites
- Produce one concrete next task for the user

Error tags you can use:
- too_vague: Content lacks specificity
- too_long: Content is overly verbose
- missing_metric: No quantifiable data or metrics
- missing_role: Role/contribution unclear
- missing_impact: Impact/outcome not stated
- missing_next_step: No clear action item
- weak_tradeoff: Trade-off analysis weak or missing
- tone_too_direct: Tone may come across as too blunt
- tone_too_soft: Tone may be too passive
- unclear_request: Request is ambiguous
- unclear_expected_actual: Expected vs actual not clearly stated

Scoring dimensions (1-5 scale):
- clarity: How clear and understandable is the message?
- conciseness: Is it appropriately brief without losing meaning?
- correctness: Grammar, spelling, and technical accuracy
- tone: Is the tone appropriate for the context?
- actionability: Does it lead to clear next steps?
"""

# Scenario-specific prompts
SCENARIO_PROMPTS = {
    Scenario.PROJECT_PITCH: """
## Scenario: Project Pitch

You are evaluating a software engineer's project pitch or project description. This could be for:
- Interview self-introductions
- Team presentations
- Documentation
- Portfolio descriptions

Focus areas for project pitches:
1. Problem: Is the problem clearly stated?
2. Role: Is the engineer's specific contribution clear?
3. Solution: Is the technical approach explained well?
4. Impact: Are results quantified where possible?
5. Trade-offs: Are key decisions and trade-offs mentioned?

Common issues in project pitches:
- Vague descriptions ("worked on the backend")
- Missing metrics ("improved performance")
- Unclear role in team projects
- No mention of challenges/decisions made
""",
    Scenario.PR_ISSUE: """
## Scenario: PR / Issue Communication

You are evaluating a software engineer's written communication for pull requests, code reviews, or issue discussions.

Focus areas for PR/Issue communication:
1. Specificity: Is the context clear?
2. Collaboration tone: Is it constructive and professional?
3. Impact: Is the change/issue impact explained?
4. Next steps: Are action items clear?

Common issues in PR/Issue communication:
- Vague feedback ("this looks wrong")
- Missing context for the reviewer
- Tone that's too direct or dismissive
- No clear ask or next step
- Blocking without alternatives

For blocking feedback, always suggest alternatives.
For approvals, be specific about what was good.
""",
}


def build_feedback_prompt(
    scenario: str,
    level: str,
    user_input: str,
    retrieved_cards: list = None,
) -> str:
    """
    Build the full prompt for generating feedback.

    Args:
        scenario: The training scenario
        level: User's experience level
        user_input: The user's submitted text
        retrieved_cards: List of retrieved KB cards for context

    Returns:
        Complete prompt string
    """
    # Start with system context
    prompt_parts = [SYSTEM_PROMPT]

    # Add scenario-specific instructions
    scenario_prompt = SCENARIO_PROMPTS.get(scenario, "")
    if scenario_prompt:
        prompt_parts.append(scenario_prompt)

    # Add level context
    level_context = f"""
## User Level: {level}

Adjust your feedback complexity and expectations based on the user's level.
- Intern: Focus on fundamentals, be encouraging, explain basics
- Junior: Balance learning with practical tips
- Mid: Expect more polish, focus on nuance and advanced patterns
"""
    prompt_parts.append(level_context)

    # Add retrieved context if available
    if retrieved_cards:
        context_parts = ["## Reference Materials\n"]
        for card in retrieved_cards:
            context_parts.append(f"### {card.title}\n{card.content}\n")
        prompt_parts.append("\n".join(context_parts))

    # Add the user input
    prompt_parts.append(f"""
## User Input

Please analyze the following text and provide structured feedback:

---
{user_input}
---

## Output Requirements

Respond with a JSON object containing:
1. scores: Object with clarity, conciseness, correctness, tone, actionability (1-5 each)
2. error_tags: Array of applicable error tags from the controlled list
3. rewrites: Array of 1-3 rewrite suggestions, each with original, better, why
4. next_task: Object with type and text for the next training exercise
5. templates_to_save: Array of useful templates extracted (optional)

Focus on the most impactful improvements. Be specific and actionable.
""")

    return "\n\n".join(prompt_parts)


def build_intent_normalization_prompt(
    scenario: str,
    user_input: str,
) -> str:
    """
    Build prompt for intent normalization.

    This extracts structured information from user input to guide retrieval.

    Args:
        scenario: The training scenario
        user_input: The user's submitted text

    Returns:
        Prompt for intent normalization
    """
    return f"""Analyze this {scenario} text and extract key information for retrieval.

Text:
{user_input}

Return JSON with:
- scenario: The training scenario (project_pitch or pr_issue)
- subskills: Array of relevant subskills (e.g., impact_statement, trade_off, tone)
- retrieval_query: A search query to find relevant examples and templates
- track: job_search or workplace

Keep the retrieval_query focused and concise.
"""