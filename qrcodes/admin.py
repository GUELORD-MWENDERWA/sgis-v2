from django.contrib import admin
from django.utils.html import format_html
from .models import QRCode

@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "matricule", "created_at", "show_image")
    readonly_fields = ("code_image", "created_at", "show_image")
    search_fields = ("user__username", "user__matricule")
    list_filter = ("created_at",)

    def matricule(self, obj):
        return obj.user.matricule

    def show_image(self, obj):
        if obj.code_image:
            return format_html("<img src='{}' width='150' height='150' />", obj.code_image.url)
        return "Aucune image"

    show_image.short_description = "QR Code"
