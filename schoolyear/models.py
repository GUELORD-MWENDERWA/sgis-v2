from django.db import models

# Create your models here.

class SchoolYear(models.Model):
    name = models.CharField(max_length=32, unique=True)  # ex: "2024-2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name
