from django.db import models
from django.utils import timezone
from accounts.models import User
from students.models import Student
from classes.models import ClassRoom
from schoolyear.models import SchoolYear

class Attendance(models.Model):
    ACTION_IN = "IN"
    ACTION_OUT = "OUT"
    ACTION_CHOICES = [
        (ACTION_IN, "Entrée"),
        (ACTION_OUT, "Sortie"),
    ]

    STATUS_PRESENT = "PRESENT"
    STATUS_LATE = "LATE"
    STATUS_UNKNOWN = "UNKNOWN"
    STATUS_CHOICES = [
        (STATUS_PRESENT, "Présent"),
        (STATUS_LATE, "En retard"),
        (STATUS_UNKNOWN, "Inconnu"),
    ]

    ENTRY_QR = "QR"
    ENTRY_MANUAL = "MANUAL"
    ENTRY_CHOICES = [
        (ENTRY_QR, "QR Code"),
        (ENTRY_MANUAL, "Manuel"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendance_records")
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name="attendances")
    role = models.CharField(max_length=20)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.SET_NULL, null=True, blank=True)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, blank=True)

    action = models.CharField(max_length=3, choices=ACTION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UNKNOWN)
    reason = models.CharField(max_length=100, blank=True)  # pour parents ou remarques

    date = models.DateField(default=timezone.localdate)
    time = models.TimeField(default=timezone.localtime)

    entry_method = models.CharField(max_length=10, choices=ENTRY_CHOICES, default=ENTRY_QR)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="attendance_recorders")
    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.user.username} - {self.role} - {self.date} {self.action}"

    def save(self, *args, **kwargs):
        # Calcul automatique du statut pour les élèves
        if self.role == "STUDENT" and self.action == self.ACTION_IN:
            late_hour, late_minute = 8, 30
            current_time = self.time
            if current_time.hour > late_hour or (current_time.hour == late_hour and current_time.minute > late_minute):
                self.status = self.STATUS_LATE
            else:
                self.status = self.STATUS_PRESENT
        super().save(*args, **kwargs)

    @classmethod
    def get_user_attendance(cls, user, school_year=None):
        qs = cls.objects.filter(user=user)
        if school_year:
            qs = qs.filter(school_year=school_year)
        return qs.order_by('date', 'time')
