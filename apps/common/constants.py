"""
Centralized enums and constants for SE English Trainer.
"""

from django.db import models


class Scenario(models.TextChoices):
    """Training scenario types."""

    PROJECT_PITCH = "project_pitch", "Project Pitch"
    PR_ISSUE = "pr_issue", "PR / Issue Communication"


class Track(models.TextChoices):
    """Training tracks."""

    JOB_SEARCH = "job_search", "Job Search"
    WORKPLACE = "workplace", "Workplace"


class Level(models.TextChoices):
    """User experience levels."""

    INTERN = "intern", "Intern"
    JUNIOR = "junior", "Junior"
    MID = "mid", "Mid-level"


class ErrorTag(models.TextChoices):
    """Controlled vocabulary for error tags."""

    TOO_VAGUE = "too_vague", "Too Vague"
    TOO_LONG = "too_long", "Too Long"
    MISSING_METRIC = "missing_metric", "Missing Metric"
    MISSING_ROLE = "missing_role", "Missing Role"
    MISSING_IMPACT = "missing_impact", "Missing Impact"
    MISSING_NEXT_STEP = "missing_next_step", "Missing Next Step"
    WEAK_TRADEOFF = "weak_tradeoff", "Weak Trade-off"
    TONE_TOO_DIRECT = "tone_too_direct", "Tone Too Direct"
    TONE_TOO_SOFT = "tone_too_soft", "Tone Too Soft"
    UNCLEAR_REQUEST = "unclear_request", "Unclear Request"
    UNCLEAR_EXPECTED_ACTUAL = "unclear_expected_actual", "Unclear Expected vs Actual"


class KBSourceType(models.TextChoices):
    """Types of knowledge base card sources."""

    TEMPLATE = "template", "Template"
    RUBRIC = "rubric", "Rubric"
    EXAMPLE = "example", "Example"
    QUESTION_PATTERN = "question_pattern", "Question Pattern"


class UserKBSourceType(models.TextChoices):
    """Types of user knowledge base card sources."""

    SAVED_TEMPLATE = "saved_template", "Saved Template"
    UPLOADED_MATERIAL = "uploaded_material", "Uploaded Material"
    BEST_OUTPUT = "best_output", "Best Output"


class TurnStatus(models.TextChoices):
    """Status of a training turn."""

    SUCCESS = "success", "Success"
    ERROR = "error", "Error"
    FALLBACK = "fallback", "Fallback"


class PlanType(models.TextChoices):
    """User subscription plan types."""

    FREE = "free", "Free"
    BASIC = "basic", "Basic"
    PRO = "pro", "Pro"


class PlanStatus(models.TextChoices):
    """User subscription plan status."""

    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    TRIAL = "trial", "Trial"


class UsageFeature(models.TextChoices):
    """Features that consume usage quota."""

    TURN_SUBMIT = "turn_submit", "Turn Submit"
    TEMPLATE_SAVE = "template_save", "Template Save"
    REPORT_GENERATE = "report_generate", "Report Generate"


class RegionStyle(models.TextChoices):
    """Regional communication style."""

    EU = "EU", "European"
    US = "US", "US"
    APAC = "APAC", "Asia Pacific"


# Default values
DEFAULT_MONTHLY_TURN_LIMIT = {
    PlanType.FREE: 10,
    PlanType.BASIC: 100,
    PlanType.PRO: 500,
}

# Scoring dimensions
SCORING_DIMENSIONS = [
    "clarity",
    "conciseness",
    "correctness",
    "tone",
    "actionability",
]

# Next task types
class NextTaskType(models.TextChoices):
    """Types of next tasks suggested by AI."""

    FOLLOW_UP_QUESTION = "follow_up_question", "Follow-up Question"
    REWRITE_EXERCISE = "rewrite_exercise", "Rewrite Exercise"
    NEW_SCENARIO = "new_scenario", "New Scenario"