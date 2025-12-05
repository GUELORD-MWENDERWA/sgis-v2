from django.db import models
from accounts.models import User
from classes.models import ClassRoom
from schoolyear.models import SchoolYear

class Student(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='student_profile'
    )
    school_year = models.ForeignKey(
        SchoolYear, 
        on_delete=models.CASCADE, 
        related_name='students'
    )
    classroom = models.ForeignKey(
        ClassRoom, 
        on_delete=models.SET_NULL,
        related_name='students_profiles',
        null=True,
        blank=True
    )
    parents = models.ManyToManyField(
        User,
        related_name='children',
        blank=True,
        limit_choices_to={'role': 'PARENT'}
    )

    # -------------------------------
    # Meta options
    # -------------------------------
    class Meta:
        unique_together = ('user', 'school_year')  # un élève ne peut pas être inscrit 2 fois la même année
        ordering = ['school_year', 'classroom__name', 'user__username']

    # -------------------------------
    # Représentation
    # -------------------------------
    def __str__(self):
        class_name = self.classroom.name if self.classroom else 'No Class'
        return f"{self.user.username} - {class_name} ({self.school_year.name})"

    # -------------------------------
    # Propriétés pratiques
    # -------------------------------
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def parent_names(self):
        return [parent.username for parent in self.parents.all()]

    @property
    def parent_matricules(self):
        return [parent.matricule for parent in self.parents.all()]

    @property
    def classroom_name(self):
        return self.classroom.name if self.classroom else None
