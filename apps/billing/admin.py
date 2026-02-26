"""
Admin configuration for billing app.
"""

from django.contrib import admin

from apps.billing.models import UsageLedger


@admin.register(UsageLedger)
class UsageLedgerAdmin(admin.ModelAdmin):
    """Admin for UsageLedger model."""

    list_display = (
        "user",
        "feature",
        "units",
        "related_session_id",
        "created_at",
    )
    list_filter = ("feature", "created_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("id", "created_at")
    ordering = ("-created_at",)
    raw_id_fields = ("user",)