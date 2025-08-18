from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserChangeForm, UserCreationForm

User = get_user_model()


class UserAdmin(BaseUserAdmin):
    list_filter = ("is_staff", "is_superuser", "is_active")

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        (None, {"fields": ("email", "password", "avatar", "role")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "role", "avatar"),
            },
        ),
    )
    list_display = (
        "email",
        "is_staff",
        "is_superuser",
        "is_admin",
        "is_teacher",
        "is_student",
        "is_guest",
        "is_active",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    ordering = ("email",)


admin.site.register(User, UserAdmin)
