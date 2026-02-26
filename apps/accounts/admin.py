"""
Admin configuration for accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from apps.accounts.models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile."""

    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"


class UserAdmin(BaseUserAdmin):
    """Extended User admin with profile inline."""

    inlines = (UserProfileInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile model."""

    list_display = (
        "user",
        "plan",
        "plan_status",
        "monthly_turn_used",
        "monthly_turn_limit",
        "created_at",
    )
    list_filter = ("plan", "plan_status")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)