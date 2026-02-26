"""
Admin configuration for trainer app.
"""

from django.contrib import admin

from apps.trainer.models import ErrorEvent, TrainingSession, TrainingTurn


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    """Admin for TrainingSession model."""

    list_display = (
        "id",
        "user",
        "scenario",
        "level",
        "track",
        "turn_count",
        "is_archived",
        "created_at",
    )
    list_filter = ("scenario", "level", "track", "is_archived")
    search_fields = ("user__username", "user__email", "title")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-updated_at",)
    raw_id_fields = ("user",)

    def turn_count(self, obj):
        return obj.turns.count()

    turn_count.short_description = "Turns"


@admin.register(TrainingTurn)
class TrainingTurnAdmin(admin.ModelAdmin):
    """Admin for TrainingTurn model."""

    list_display = (
        "id",
        "session",
        "turn_index",
        "status",
        "latency_ms",
        "created_at",
    )
    list_filter = ("status", "session__scenario")
    search_fields = ("session__user__username", "user_input")
    readonly_fields = ("id", "created_at")
    ordering = ("-created_at",)
    raw_id_fields = ("session",)


@admin.register(ErrorEvent)
class ErrorEventAdmin(admin.ModelAdmin):
    """Admin for ErrorEvent model."""

    list_display = (
        "id",
        "user",
        "scenario",
        "error_tag",
        "created_at",
    )
    list_filter = ("error_tag", "scenario")
    search_fields = ("user__username",)
    readonly_fields = ("id", "created_at")
    ordering = ("-created_at",)
    raw_id_fields = ("user", "session", "turn")