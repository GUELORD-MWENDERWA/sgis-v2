from django.db import models
from django.conf import settings
from schoolyear.models import SchoolYear

class ClassRoom(models.Model):
    name = models.CharField(max_length=50, help_text="Nom de la classe, ex: 6ème A")
    
    year = models.ForeignKey(
        SchoolYear,
        on_delete=models.CASCADE,
        related_name='classes',
        help_text="Année scolaire à laquelle appartient la classe"
    )
    
    main_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'TEACHER'},
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='main_classes',
        help_text="Professeur principal de la classe"
    )
    
    teachers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'TEACHER'},
        related_name='classes_teaching',
        blank=True,
        help_text="Autres enseignants de la classe"
    )
    
    # Ne pas stocker directement les élèves ici, on gère via Student.school_year + classroom
    # students = models.ManyToManyField(
    #     settings.AUTH_USER_MODEL,
    #     limit_choices_to={'role': 'STUDENT'},
    #     related_name='classes_enrolled',
    #     blank=True
    # )
    
    class Meta:
        unique_together = ('name', 'year')  # une classe unique par année scolaire
        ordering = ['name']
        verbose_name = "Classe"
        verbose_name_plural = "Classes"

    def __str__(self):
        return f"{self.name} ({self.year})"

    def get_students(self):
        """
        Retourne tous les élèves assignés à cette classe via le modèle Student.
        """
        return self.students_profiles.all()  # basé sur Student.classroom
