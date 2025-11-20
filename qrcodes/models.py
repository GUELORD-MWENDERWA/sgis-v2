import os
import json
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
from django.utils.timezone import now
from accounts.models import User


def qr_code_path(instance, filename):
    # Nouveau nom unique
    return f"qrcodes/{instance.user.username}_{int(now().timestamp())}.png"


class QRCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="qr_code")
    code_image = models.ImageField(upload_to=qr_code_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"QR Code - {self.user.username}"

    def generate_qr_bytes(self):
        payload = {
            "matricule": self.user.matricule,
            "username": self.user.username,
            "full_name": self.user.get_full_name(),
            "updated_at": now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        data = json.dumps(payload)

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

    def save(self, *args, **kwargs):
        regenerate = False

        # Si déjà un QR code existe → supprimer & régénérer
        if self.code_image and self.pk:
            regenerate = True

        buffer = self.generate_qr_bytes()

        # Supprimer l'ancien fichier
        if regenerate:
            if os.path.isfile(self.code_image.path):
                os.remove(self.code_image.path)

        filename = f"{self.user.username}_{int(now().timestamp())}.png"
        self.code_image.save(filename, ContentFile(buffer.getvalue()), save=False)

        buffer.close()

        super().save(*args, **kwargs)
