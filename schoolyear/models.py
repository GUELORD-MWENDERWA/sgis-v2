from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

class SchoolYear(models.Model):
    name = models.CharField(max_length=32, unique=True)  # ex: "2024-2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name


# ---------------------------------------------------
# Signaux : garantir qu'une seule année peut être active
# ---------------------------------------------------
@receiver(pre_save, sender=SchoolYear)
def ensure_single_active_year(sender, instance, **kwargs):
    if instance.is_active:
        # Désactiver toutes les autres années actives
        sender.objects.exclude(pk=instance.pk).update(is_active=False)
