from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, MemberResource, SupportRequest


# -------------------------
# Custom User Admin
# -------------------------


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    Email-only user admin.
    """

    ordering = ("email",)
    list_display = (
        "email",
        "first_name",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_staff", "is_active", "date_joined")
    search_fields = ("email", "first_name")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_verified",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    readonly_fields = ("date_joined", "last_login")

    # Remove username completely
    username = None


# -------------------------
# Member Resources Admin
# -------------------------


@admin.register(MemberResource)
class MemberResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "order", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "description")
    ordering = ("order", "-created_at")

    readonly_fields = ("created_at",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "description",
                    "file",
                    "thumbnail",
                )
            },
        ),
        (
            "Display settings",
            {
                "fields": (
                    "is_active",
                    "order",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at",),
            },
        ),
    )


# -------------------------
# Support Requests Admin
# -------------------------


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ("subject", "get_user_email", "created_at", "handled")
    list_filter = ("handled", "created_at")
    search_fields = ("subject", "message", "user__email")
    ordering = ("-created_at",)

    readonly_fields = ("subject", "message", "created_at", "get_user_email")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "get_user_email",
                    "subject",
                    "message",
                )
            },
        ),
        (
            "Status",
            {
                "fields": ("handled",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at",),
            },
        ),
    )

    def get_user_email(self, obj):
        return obj.user.email if obj.user else "-"

    get_user_email.short_description = "User Email"
