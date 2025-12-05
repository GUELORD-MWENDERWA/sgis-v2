from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import User
from students.models import Student
from classes.models import ClassRoom
from schoolyear.models import SchoolYear
from rfid.models import RFIDCard, RFIDModule

# ------------------------------
#  1) SESSIONS DE PRÉSENCE
# ------------------------------
class AttendanceSession(models.Model):
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="attendance_sessions")
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name="attendance_sessions")
    name = models.CharField(max_length=50, default="Session de présence")
    date = models.DateField(default=timezone.localdate)
    opened_at = models.DateTimeField(default=timezone.now)
    closed_at = models.DateTimeField(null=True, blank=True)
    is_open = models.BooleanField(default=True)
    
    # Heure limite pour être considéré présent
    limit_hour = models.IntegerField(default=8)
    limit_minute = models.IntegerField(default=30)

    def close(self):
        if not self.is_open:
            return
        self.is_open = False
        self.closed_at = timezone.now()
        self.save(update_fields=["is_open", "closed_at"])

    def __str__(self):
        return f"{self.classroom.name} - {self.date} - {'Ouverte' if self.is_open else 'Fermée'}"

# ------------------------------
#  2) ENREGISTREMENT DE PRÉSENCE
# ------------------------------
def get_current_time():
    """Retourne uniquement l'heure locale pour TimeField"""
    return timezone.localtime().time()

class Attendance(models.Model):
    # Types entrée/sortie
    ACTION_IN = "IN"
    ACTION_OUT = "OUT"
    ACTION_CHOICES = [(ACTION_IN, "Entrée"), (ACTION_OUT, "Sortie")]

    # Statuts
    STATUS_PRESENT = "PRESENT"
    STATUS_LATE = "LATE"
    STATUS_UNKNOWN = "UNKNOWN"
    STATUS_CHOICES = [(STATUS_PRESENT, "Présent"), (STATUS_LATE, "En retard"), (STATUS_UNKNOWN, "Inconnu")]

    # Méthodes d'entrée
    ENTRY_QR = "QR"
    ENTRY_MANUAL = "MANUAL"
    ENTRY_RFID = "RFID"
    ENTRY_CHOICES = [(ENTRY_QR, "QR Code"), (ENTRY_MANUAL, "Manuel"), (ENTRY_RFID, "RFID")]

    # Relations
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name="records", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendance_records")
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name="attendances")
    role = models.CharField(max_length=20)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.SET_NULL, null=True, blank=True)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Données de présence
    action = models.CharField(max_length=3, choices=ACTION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UNKNOWN)
    reason = models.CharField(max_length=100, blank=True)
    date = models.DateField(default=timezone.localdate)
    time = models.TimeField(default=get_current_time)  # <-- corrigé ici
    entry_method = models.CharField(max_length=10, choices=ENTRY_CHOICES, default=ENTRY_QR)

    # RFID
    rfid_card = models.ForeignKey(RFIDCard, on_delete=models.SET_NULL, null=True, blank=True, related_name="attendance_records")
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="attendance_recorders")
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-time']
        indexes = [
            models.Index(fields=['student', 'date']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.role} - {self.date} {self.action} ({self.entry_method})"

    # ---------------- Logic de retard automatique ----------------
    def save(self, *args, **kwargs):
        if self.role == "STUDENT" and self.action == self.ACTION_IN:
            if self.session:
                late_hour = self.session.limit_hour
                late_minute = self.session.limit_minute
            else:
                late_hour, late_minute = 8, 30
            t = self.time
            if t.hour > late_hour or (t.hour == late_hour and t.minute > late_minute):
                self.status = self.STATUS_LATE
            else:
                self.status = self.STATUS_PRESENT
        super().save(*args, **kwargs)

    # ---------------- UTILITAIRES / RAPPORTS ----------------
    @classmethod
    def get_user_attendance(cls, user, school_year=None):
        qs = cls.objects.filter(user=user)
        if school_year:
            qs = qs.filter(school_year=school_year)
        return qs.order_by('date', 'time')

    @classmethod
    def get_student_report(cls, student, start_date=None, end_date=None):
        qs = cls.objects.filter(student=student)
        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)

        total_days = qs.values('date').distinct().count()
        total_present = qs.filter(action=cls.ACTION_IN, status=cls.STATUS_PRESENT).count()
        total_late = qs.filter(action=cls.ACTION_IN, status=cls.STATUS_LATE).count()
        total_absent = total_days - total_present - total_late
        percent_present = round((total_present / total_days) * 100, 2) if total_days else 0
        percent_late = round((total_late / total_days) * 100, 2) if total_days else 0
        percent_absent = round((total_absent / total_days) * 100, 2) if total_days else 0

        # Calcul temps total passé
        time_spent = timedelta()
        dates = qs.values_list('date', flat=True).distinct()
        for d in dates:
            ins = list(qs.filter(date=d, action=cls.ACTION_IN).order_by('time'))
            outs = list(qs.filter(date=d, action=cls.ACTION_OUT).order_by('time'))
            for i, entry in enumerate(ins):
                try:
                    exit_time = outs[i].time
                except IndexError:
                    exit_time = datetime.now().time()
                entry_time = entry.time
                dt_entry = datetime.combine(datetime.today(), entry_time)
                dt_exit = datetime.combine(datetime.today(), exit_time)
                if dt_exit < dt_entry:
                    dt_exit += timedelta(days=1)  # gérer passage minuit
                time_spent += dt_exit - dt_entry

        return {
            "student": student.user.username,
            "total_days": total_days,
            "present": total_present,
            "late": total_late,
            "absent": total_absent,
            "percent_present": percent_present,
            "percent_late": percent_late,
            "percent_absent": percent_absent,
            "time_spent_total": str(time_spent),
        }

    @classmethod
    def get_class_report(cls, classroom, start_date=None, end_date=None):
        report = {}
        students = classroom.students_profiles.all()
        for student in students:
            report[student.user.username] = cls.get_student_report(student, start_date, end_date)
        return report

    # ---------------- Enregistrement via RFID ----------------
    @classmethod
    def record_rfid(cls, rfid_uid, module_name=None):
        try:
            card = RFIDCard.objects.get(uid=rfid_uid)
        except RFIDCard.DoesNotExist:
            return {"error": "Carte RFID non reconnue"}

        user = card.user
        if not user:
            return {"error": "Carte non assignée à un utilisateur"}

        # Déterminer le rôle et l’étudiant
        # Student profile may not exist; use getattr
        student = getattr(user, "student_profile", None)
        if student:
            role = "STUDENT"
        else:
            role = getattr(user, "role", "STAFF") or "STAFF"

        # Determine classroom: prefer student's classroom when available
        classroom = None
        if student and getattr(student, "classroom", None):
            classroom = student.classroom
        else:
            # try to infer from user's related objects if any (graceful fallback)
            try:
                classroom = user.classroom_set.first()
            except Exception:
                classroom = None

        # Déterminer la session ouverte pour la classe
        session = None
        if classroom:
            session = AttendanceSession.objects.filter(classroom=classroom, is_open=True).last()

        record = cls.objects.create(
            user=user,
            student=student,
            role=role,
            classroom=classroom,
            school_year=session.school_year if session else None,
            session=session,
            action=cls.ACTION_IN,
            entry_method=cls.ENTRY_RFID,
            rfid_card=card,
            date=timezone.localdate(),
            time=timezone.localtime().time(),
        )
        return {"success": True, "record_id": record.id}
