from django.contrib import admin
from .models import QRCode

@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "matricule", "created_at", "show_image")
    readonly_fields = ("code_image", "created_at")
    search_fields = ("user__username", "user__matricule")
    list_filter = ("created_at",)

    def matricule(self, obj):
        return obj.user.matricule

    def show_image(self, obj):
        if obj.code_image:
            return f"<img src='{obj.code_image.url}' width='120' />"
        return "Aucune image"
    show_image.allow_tags = True
    show_image.short_description = "QR Code"
