from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from .models import QRCode


#generation automatique des QR codes pour les nouveaux utilisateurs
@receiver(post_save, sender=User)
def create_qr_for_new_user(sender, instance, created, **kwargs):
    """
    - Crée un QR pour chaque nouvel utilisateur
    - Ne touche pas aux utilisateurs existants
    """
    if created:
        QRCode.objects.create(user=instance)
