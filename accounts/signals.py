from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from .models import User
import os

# -------------------------------------------------------
#  1) GÉNÉRATION AUTOMATIQUE DU MATRICULE
# -------------------------------------------------------
@receiver(post_save, sender=User)
def generate_matricule(sender, instance, created, **kwargs):
    if created and not instance.matricule:
        prefix = instance.role[:3].upper()
        random_code = get_random_string(6).upper()
        instance.matricule = f"{prefix}-{random_code}"
        instance.save(update_fields=['matricule'])


# -------------------------------------------------------
#  2) RENOMMER PHOTO (NE PAS TOUCHER default.jpg)
# -------------------------------------------------------
@receiver(post_save, sender=User)
def rename_photo(sender, instance, **kwargs):
    if not instance.photo:
        return

    old_path = instance.photo.path

    # Ne jamais renommer default.jpg
    if "default.jpg" in old_path:
        return

    ext = old_path.split('.')[-1]
    new_filename = f"{instance.username}.{ext}"
    new_path = os.path.join(os.path.dirname(old_path), new_filename)

    if old_path != new_path:
        try:
            os.rename(old_path, new_path)
            instance.photo.name = f'users/photos/{new_filename}'
            instance.save(update_fields=['photo'])
        except FileNotFoundError:
            pass
