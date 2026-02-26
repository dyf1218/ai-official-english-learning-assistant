"""
Admin configuration for knowledge base app.
"""

from django.contrib import admin

from apps.kb.models import PublicKBCard, UserKBCard


@admin.register(PublicKBCard)
class PublicKBCardAdmin(admin.ModelAdmin):
    """Admin for PublicKBCard model."""

    list_display = (
        "title",
        "scenario",
        "level",
        "subskill",
        "source_type",
        "is_active",
        "created_at",
    )
    list_filter = ("scenario", "level", "source_type", "is_active", "region_style")
    search_fields = ("title", "content", "subskill")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("scenario", "level", "subskill")
    
    fieldsets = (
        (None, {
            "fields": ("id", "title", "content", "when_to_use")
        }),
        ("Classification", {
            "fields": ("track", "scenario", "level", "subskill", "region_style", "source_type")
        }),
        ("Status", {
            "fields": ("is_active",)
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    actions = ["activate_cards", "deactivate_cards"]

    @admin.action(description="Activate selected cards")
    def activate_cards(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} cards activated.")

    @admin.action(description="Deactivate selected cards")
    def deactivate_cards(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} cards deactivated.")


@admin.register(UserKBCard)
class UserKBCardAdmin(admin.ModelAdmin):
    """Admin for UserKBCard model."""

    list_display = (
        "title",
        "user",
        "scenario",
        "source_type",
        "created_at",
    )
    list_filter = ("scenario", "source_type")
    search_fields = ("title", "content", "user__username", "user__email")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)
    raw_id_fields = ("user",)