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

    def __str__(self):
        return f"{self.user.username} - {self.classroom.name if self.classroom else 'No Class'} ({self.school_year.name})"
