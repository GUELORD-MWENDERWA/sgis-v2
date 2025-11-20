from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User

class UserAdmin(BaseUserAdmin):
    model = User

    list_display = ("username", "email", "role", "is_staff", "is_active", "photo_thumbnail", "matricule")
    list_filter = ("role", "is_staff", "is_active")

    fieldsets = (
        (None, {"fields": ("username", "email", "password", "role", "photo", "matricule")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "role", "is_staff", "is_active")}
        ),
    )

    search_fields = ("username", "email", "matricule")
    ordering = ("username",)

    readonly_fields = ("photo_thumbnail",)

    # Méthode pour afficher une miniature cliquable
    def photo_thumbnail(self, obj):
        if obj.photo:
            return format_html(
                '<a href="{0}" target="_blank"><img src="{0}" style="width:50px; height:50px; object-fit:cover;" /></a>',
                obj.photo.url
            )
        return "-"
    photo_thumbnail.short_description = "Photo"

admin.site.register(User, UserAdmin)
