"""
Admin configuration for reports app.
"""

from django.contrib import admin

from apps.reports.models import WeeklyReport


@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    """Admin for WeeklyReport model."""

    list_display = (
        "user",
        "period_start",
        "period_end",
        "total_turns",
        "created_at",
    )
    list_filter = ("period_start",)
    search_fields = ("user__username", "user__email")
    readonly_fields = ("id", "created_at")
    ordering = ("-period_end",)
    raw_id_fields = ("user",)

    def total_turns(self, obj):
        return obj.summary_json.get("total_turns", 0)

    total_turns.short_description = "Total Turns"