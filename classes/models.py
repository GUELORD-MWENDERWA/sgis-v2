from django.db import models
from django.conf import settings
from schoolyear.models import SchoolYear

class ClassRoom(models.Model):
    name = models.CharField(max_length=50)  # ex: "6ème A"
    year = models.ForeignKey(
        SchoolYear,
        on_delete=models.CASCADE,
        related_name='classes'
    )
    main_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'TEACHER'},
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='main_classes'
    )
    # Plusieurs enseignants pour la classe
    teachers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'TEACHER'},
        related_name='classes_teaching',
        blank=True
    )
    # Les élèves assignés à cette classe
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'STUDENT'},
        related_name='classes_enrolled',
        blank=True
    )

    class Meta:
        unique_together = ('name', 'year')  # une classe unique par année scolaire
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.year})"
