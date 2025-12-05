import os
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.timezone import now
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Fonction pour générer un chemin unique pour la photo
def user_photo_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.username}_{int(now().timestamp())}.{ext}"
    return os.path.join('users/photos/', filename)

class User(AbstractUser):
    # Définition des rôles
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STAFF = "STAFF", "Staff"
        TEACHER = "TEACHER", "Teacher"
        PARENT = "PARENT", "Parent"
        STUDENT = "STUDENT", "Student"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.STUDENT
    )

    # Photo de profil
    photo = models.ImageField(
        upload_to=user_photo_path,
        blank=True,
        null=True,
        default="users/photos/default.jpg"
    )

    # Identifiant unique
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


    # Champ matricule (sera généré plus tard)
    matricule = models.CharField(max_length=20, unique=True, blank=True, null=True)

    # Téléphone
    phone = models.CharField(max_length=20, blank=True, null=True)

    # Date de naissance
    birth_date = models.DateField(blank=True, null=True)

    # ⚡ Correction des conflits avec Django auth
    groups = models.ManyToManyField(
        Group,
        related_name="accounts_user_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups"
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="accounts_user_permissions_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions"
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

# Signal pour supprimer l'ancienne photo lorsqu'on en upload une nouvelle
@receiver(pre_save, sender=User)
def auto_delete_old_photo(sender, instance, **kwargs):
    if not instance.pk:
        return  # Nouvel utilisateur, rien à faire
    try:
        old_file = sender.objects.get(pk=instance.pk).photo
    except sender.DoesNotExist:
        return
    new_file = instance.photo
    if not old_file == new_file and os.path.isfile(old_file.path) and 'default.jpg' not in old_file.path:
        os.remove(old_file.path)
