import os
import uuid
import qrcode
from io import BytesIO
from django.db import models
from django.core.files.base import ContentFile
from django.utils.timezone import now
from accounts.models import User


def qr_code_path(instance, filename):
    """
    Chemin de sauvegarde du QR Code
    """
    return f"qrcodes/{instance.user.username}_{instance.code}.png"


class QRCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="qr_code")

    # Token unique et sécurisé
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # Image générée automatiquement
    code_image = models.ImageField(upload_to=qr_code_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"QR Code - {self.user.username}"

    def generate_qr(self):
        """
        Génère le QR contenant uniquement le token UUID
        """
        data = f"ATT-QR:{self.code}"

        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image()

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    def save(self, *args, **kwargs):
        """
        Génération du QR Code uniquement si l'image n'existe pas
        """
        if not self.code_image:
            buffer = self.generate_qr()
            filename = f"{self.user.username}_{self.code}.png"
            self.code_image.save(filename, ContentFile(buffer.getvalue()), save=False)
            buffer.close()

        super().save(*args, **kwargs)
