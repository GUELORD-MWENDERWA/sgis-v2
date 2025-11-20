from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from .models import QRCode

# -------------------------------------------------------
#  3) GENERATION / REGENERATION DU QR CODE
# -------------------------------------------------------
@receiver(post_save, sender=User)
def auto_create_or_update_qr(sender, instance, created, **kwargs):
    if created:
        # Nouveau user → créer un QR
        QRCode.objects.create(user=instance)
    else:
        # User modifié → QR déjà existant → régénérer
        if hasattr(instance, "qr_code"):
            instance.qr_code.save()
