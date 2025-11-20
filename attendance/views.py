import json
from datetime import time as time_cls
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Attendance
from .serializers import AttendanceSerializer
from .permissions import IsAdminOrTeacherOrOwner
from accounts.models import User
from students.models import Student
from django.conf import settings

# Heure limite pour considérer un étudiant en retard
DEFAULT_LATE_HOUR = getattr(settings, "ATTENDANCE_LATE_HOUR", (8, 30))
DEFAULT_LATE_THRESHOLD = time_cls(*DEFAULT_LATE_HOUR) if isinstance(DEFAULT_LATE_HOUR, (list, tuple)) else time_cls(8, 30)

# -------------------------------------------------------------------
# 1️⃣ CRUD complet pour Attendance (Admin/Teacher/Owner)
# -------------------------------------------------------------------
class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().select_related(
        'user', 'student', 'classroom', 'school_year', 'recorded_by'
    )
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacherOrOwner]

    def get_queryset(self):
        qs = super().get_queryset()
        q_date = self.request.query_params.get('date')
        q_user = self.request.query_params.get('user')
        q_student = self.request.query_params.get('student')
        q_class = self.request.query_params.get('classroom')
        q_role = self.request.query_params.get('role')

        if q_date:
            qs = qs.filter(date=q_date)
        if q_user:
            qs = qs.filter(user__pk=q_user)
        if q_student:
            qs = qs.filter(student__pk=q_student)
        if q_class:
            qs = qs.filter(classroom__pk=q_class)
        if q_role:
            qs = qs.filter(role=q_role)
        return qs

# -------------------------------------------------------------------
# 2️⃣ API pour scanner un QR code et enregistrer la présence
# -------------------------------------------------------------------
class ScanAttendanceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payload = request.data.get('data')
        matricule = request.data.get('matricule')
        user_id = request.data.get('user_id')
        reason = request.data.get('reason', '')

        # Décoder le QR code si fourni
        if payload:
            try:
                decoded = json.loads(payload)
                matricule = decoded.get('matricule') or decoded.get('username') or decoded.get('id')
            except:
                return Response({"error": "QR data invalid"}, status=status.HTTP_400_BAD_REQUEST)

        # Récupérer l'utilisateur
        user = None
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        elif matricule:
            try:
                user = User.objects.get(matricule=matricule)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "matricule or user_id or data required"}, status=status.HTTP_400_BAD_REQUEST)

        role = user.role
        student = getattr(user, 'student_profile', None)
        now = timezone.localtime()
        today = now.date()
        current_time = now.time()

        todays = Attendance.objects.filter(user=user, date=today).order_by('time')
        in_record = todays.filter(action=Attendance.ACTION_IN).first()
        out_record = todays.filter(action=Attendance.ACTION_OUT).first()

        # Fonction interne pour créer un enregistrement
        def create_record(action_val, status_val=Attendance.STATUS_UNKNOWN):
            return Attendance.objects.create(
                user=user,
                student=student if student else None,
                role=role,
                school_year=student.year if student else None,
                classroom=student.classroom if student else None,
                action=action_val,
                status=status_val,
                reason=reason if role == 'PARENT' else '',
                date=today,
                time=current_time,
                entry_method=Attendance.ENTRY_QR,
                recorded_by=request.user
            )

        # ---------------------------
        # Logique spécifique aux parents
        # ---------------------------
        if role == 'PARENT':
            if not reason:
                return Response({"error": "Reason required for parent"}, status=400)
            action_val = Attendance.ACTION_IN if not in_record else Attendance.ACTION_OUT
            att = create_record(action_val)
            serializer = AttendanceSerializer(att)
            return Response({"action": action_val, "attendance": serializer.data}, status=201)

        # ---------------------------
        # Logique pour STUDENT / TEACHER / ADMIN
        # ---------------------------
        # Premier passage → IN
        if not in_record:
            status_val = Attendance.STATUS_PRESENT
            if role == 'STUDENT' and current_time > DEFAULT_LATE_THRESHOLD:
                status_val = Attendance.STATUS_LATE
            att = create_record(Attendance.ACTION_IN, status_val)
            serializer = AttendanceSerializer(att)
            return Response({"action": "IN", "attendance": serializer.data}, status=201)

        # Déjà passé IN mais pas OUT → OUT
        if in_record and not out_record:
            att = create_record(Attendance.ACTION_OUT, Attendance.STATUS_UNKNOWN)
            serializer = AttendanceSerializer(att)
            return Response({"action": "OUT", "attendance": serializer.data}, status=201)

        # Cas nouveau passage après IN et OUT → nouvelle session IN
        status_val = Attendance.STATUS_PRESENT
        if role == 'STUDENT' and current_time > DEFAULT_LATE_THRESHOLD:
            status_val = Attendance.STATUS_LATE
        att = create_record(Attendance.ACTION_IN, status_val)
        serializer = AttendanceSerializer(att)
        return Response({"action": "IN", "attendance": serializer.data, "note": "New session"}, status=201)
