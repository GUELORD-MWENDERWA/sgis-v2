import uuid
from django.db import models
from django.utils.timezone import now
from accounts.models import User


# ------------------------------
#  Carte RFID (badge physique)
# ------------------------------
class RFIDCard(models.Model):
    uid = models.CharField(max_length=255, unique=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, related_name="rfid_card", null=True, blank=True)

    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def is_available(self):
        return self.user is None

    def __str__(self):
        return f"{self.uid} - {self.label or 'Sans label'}"


# --------------------------------------
#  Module matériel RFID (ESP32 / Arduino)
# --------------------------------------
class RFIDModule(models.Model):
    # Exemple : "Entrée principale", "Sortie", "Cantine"
    name = models.CharField(max_length=255)

    # Endroit physique où le module est installé
    location = models.CharField(max_length=255, blank=True, null=True)

    # TOKEN UNIQUE généré automatiquement
    token = models.CharField(max_length=100, unique=True, default=uuid.uuid4)

    # Pour mettre une note : "Module bleu avec antenne longue"
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Module {self.name} ({self.location})"
