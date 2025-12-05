import json
from datetime import time as time_cls
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Attendance, AttendanceSession
from django.db import IntegrityError
from .serializers import (
    AttendanceSerializer,
    AttendanceCreateSerializer,
    AttendanceSessionSerializer,
)
from .permissions import IsAdminOrTeacherOrOwner

from accounts.models import User
from students.models import Student
from classes.models import ClassRoom
from rfid.models import RFIDCard, RFIDModule
from qrcodes.models import QRCode


# -----------------------------------------------------------------
# CONFIG : Heure tard (08h30 par défaut)
# -----------------------------------------------------------------
DEFAULT_LATE_HOUR = getattr(settings, "ATTENDANCE_LATE_HOUR", (8, 30))
DEFAULT_LATE_THRESHOLD = time_cls(*DEFAULT_LATE_HOUR)


# -----------------------------------------------------------------
# 1) CRUD COMPLET Attendance
# -----------------------------------------------------------------
class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().select_related(
        "user", "student", "classroom", "school_year", "recorded_by"
    )
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacherOrOwner]

    def get_serializer_class(self):
        # Use a dedicated create/update serializer when writing
        if self.action in ("create", "update", "partial_update"):
            return AttendanceCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        # Ensure recorded_by and timestamps are set server-side
        serializer.save(recorded_by=self.request.user, date=timezone.localdate(), time=timezone.localtime().time())

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        if params.get("date"):
            qs = qs.filter(date=params["date"])
        if params.get("user"):
            qs = qs.filter(user__pk=params["user"])
        if params.get("student"):
            qs = qs.filter(student__pk=params["student"])
        if params.get("classroom"):
            qs = qs.filter(classroom__pk=params["classroom"])
        if params.get("role"):
            qs = qs.filter(role=params["role"])

        return qs


# -----------------------------------------------------------------
# 2) CRUD COMPLET Session
# -----------------------------------------------------------------
class AttendanceSessionViewSet(viewsets.ModelViewSet):
    queryset = AttendanceSession.objects.all().select_related("classroom", "school_year")
    serializer_class = AttendanceSessionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacherOrOwner]


# -----------------------------------------------------------------
# 3) SCAN QR CODE (Présence via QR Code)
# -----------------------------------------------------------------
class ScanAttendanceAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_current_session_for_user(self, user):
        """Récupère la session active pour l’utilisateur automatiquement"""
        now = timezone.localtime()
        today = now.date()
        current_time = now.time()
        student = getattr(user, "student_profile", None)
        if not student:
            return None
        classroom = student.classroom
        # Session ouverte et correspondant à l'heure actuelle
        # Compare using __time lookups and accept sessions with closed_at null
        session = AttendanceSession.objects.filter(
            classroom=classroom,
            date=today,
        ).filter(
            Q(opened_at__time__lte=current_time) & (Q(closed_at__isnull=True) | Q(closed_at__time__gte=current_time))
        ).first()
        return session

    def post(self, request):
        # Accept multiple payload shapes:
        # - {"data": "{\"token\": \"...\"}"}
        # - {"token": "..."}
        # - {"matricule": "..."}
        # - {"user_id": 2}
        payload = None
        raw = request.data.get("data") if "data" in request.data else request.data

        # Decode if it's a JSON string
        try:
            if isinstance(raw, (str, bytes)):
                payload = json.loads(raw)
            elif isinstance(raw, dict):
                payload = raw
            else:
                payload = json.loads(json.dumps(raw))
        except Exception:
            return Response({"error": "Invalid QR data"}, status=400)

        # Extract possible identifiers
        token_val = payload.get("token") if isinstance(payload, dict) else None
        matricule = payload.get("matricule") if isinstance(payload, dict) else None
        user_id = payload.get("user_id") if isinstance(payload, dict) else None
        rfid_uid = payload.get("rfid_uid") if isinstance(payload, dict) else None
        # accept short 'uid' key too
        if not rfid_uid and isinstance(payload, dict):
            rfid_uid = payload.get("uid")

        # allow top-level request fields too
        token_val = token_val or request.data.get("token")
        matricule = matricule or request.data.get("matricule")
        user_id = user_id or request.data.get("user_id")

        user = None

        # 1) user by explicit id
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=404)

        # 2) user by matricule
        if not user and matricule:
            try:
                user = User.objects.get(matricule=matricule)
            except User.DoesNotExist:
                return Response({"error": "Matricule not recognized"}, status=404)

        # 3) user by QR token/code
        qr = None
        if not user and token_val:
            try:
                qr = QRCode.objects.select_related("user").get(code=token_val)
                user = qr.user
            except QRCode.DoesNotExist:
                # try alternative field name
                try:
                    qr = QRCode.objects.select_related("user").get(token=token_val)
                    user = qr.user
                except Exception:
                    return Response({"error": "QR code not recognized"}, status=404)

        if not user:
            # If RFID UID present, try to resolve user via RFID card
            if rfid_uid:
                try:
                    card = RFIDCard.objects.select_related("user").get(uid=rfid_uid)
                except RFIDCard.DoesNotExist:
                    return Response({"error": "RFID card not recognized"}, status=404)

                if not card.user:
                    return Response({"error": "RFID card not assigned to a user"}, status=400)

                user = card.user
            else:
                return Response({"error": "No user information found in payload"}, status=400)

        role = user.role

        now = timezone.localtime()
        today = now.date()
        current_time = now.time()
        student = getattr(user, "student_profile", None)

        # Session automatique
        session = self.get_current_session_for_user(user)
        if not session:
            return Response({"error": "Aucune session active pour votre classe"}, status=400)

        # Présences existantes pour la session et la journée
        todays = Attendance.objects.filter(user=user, session=session, date=today).order_by("time")
        in_record = todays.filter(action=Attendance.ACTION_IN).first()
        out_record = todays.filter(action=Attendance.ACTION_OUT).first()

        # Fonction création enregistrement
        def create_record(action_val, status_val=Attendance.STATUS_UNKNOWN):
            try:
                return Attendance.objects.create(
                    user=user,
                    student=student if student else None,
                    role=role,
                    school_year=student.school_year if student else None,
                    classroom=student.classroom if student else None,
                    session=session,
                    action=action_val,
                    status=status_val,
                    date=today,
                    time=current_time,
                    entry_method=Attendance.ENTRY_QR,
                    recorded_by=request.user,
                )
            except IntegrityError:
                return None

        # --- Logique simple IN / OUT ---
        if not in_record:
            status_val = Attendance.STATUS_LATE if role == "STUDENT" and current_time > DEFAULT_LATE_THRESHOLD else Attendance.STATUS_PRESENT
            att = create_record(Attendance.ACTION_IN, status_val)
            if not att:
                return Response({"error": "Erreur lors de l'enregistrement de la présence."}, status=500)
            return Response({"action": "IN", "attendance": AttendanceSerializer(att).data}, status=201)

        if in_record and not out_record:
            att = create_record(Attendance.ACTION_OUT)
            if not att:
                return Response({"error": "Erreur lors de l'enregistrement de la présence."}, status=500)
            return Response({"action": "OUT", "attendance": AttendanceSerializer(att).data}, status=201)

        # Si IN et OUT déjà enregistrés, ne rien faire
        return Response({"note": "Présence déjà enregistrée pour la journée"}, status=200)


# -----------------------------------------------------------------
# 4) SCAN RFID (Modules physiques ESP32 / Arduino)
# -----------------------------------------------------------------
class RFIDAttendanceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_current_session_for_user(self, user):
        """Récupère la session active pour l’utilisateur automatiquement"""
        now = timezone.localtime()
        today = now.date()
        current_time = now.time()
        student = getattr(user, "student_profile", None)
        if not student:
            return None
        classroom = student.classroom
        session = AttendanceSession.objects.filter(
            classroom=classroom,
            date=today,
        ).filter(
            Q(opened_at__time__lte=current_time) & (Q(closed_at__isnull=True) | Q(closed_at__time__gte=current_time))
        ).first()
        return session

    def post(self, request):
        uid = request.data.get("rfid_uid")
        module_token = request.data.get("module_token")

        if not uid:
            return Response({"error": "rfid_uid required"}, status=400)
        if not module_token:
            return Response({"error": "module_token required"}, status=400)

        # Vérifier module RFID
        try:
            module = RFIDModule.objects.get(token=module_token)
        except RFIDModule.DoesNotExist:
            return Response({"error": "Invalid RFID module"}, status=403)

        # Vérifier carte RFID
        try:
            card = RFIDCard.objects.get(uid=uid)
        except RFIDCard.DoesNotExist:
            return Response({"error": "Unknown RFID card"}, status=404)

        if not card.user:
            return Response({"error": "Card not assigned to a user"}, status=400)

        user = card.user
        role = user.role
        now = timezone.localtime()
        today = now.date()
        current_time = now.time()
        student = getattr(user, "student_profile", None)

        # Session automatique
        session = self.get_current_session_for_user(user)
        if not session:
            return Response({"error": "No active session for your class"}, status=400)

        # Présences du jour pour cette session
        todays = Attendance.objects.filter(user=user, session=session, date=today).order_by("time")
        in_record = todays.filter(action=Attendance.ACTION_IN).first()
        out_record = todays.filter(action=Attendance.ACTION_OUT).first()

        # Fonction création enregistrement
        def create_record(action_val, status_val=Attendance.STATUS_UNKNOWN):
            try:
                return Attendance.objects.create(
                    user=user,
                    student=student if student else None,
                    role=role,
                    school_year=student.school_year if student else None,
                    classroom=student.classroom if student else None,
                    session=session,
                    action=action_val,
                    status=status_val,
                    reason="",  # pas besoin de raison pour RFID
                    date=today,
                    time=current_time,
                    entry_method=Attendance.ENTRY_RFID,
                    recorded_by=request.user,
                )
            except IntegrityError:
                return None

        # IN / OUT simple
        if not in_record:
            status_val = Attendance.STATUS_LATE if role == "STUDENT" and current_time > DEFAULT_LATE_THRESHOLD else Attendance.STATUS_PRESENT
            att = create_record(Attendance.ACTION_IN, status_val)
            if not att:
                return Response({"error": "Erreur lors de l'enregistrement RFID."}, status=500)
            return Response({"action": "IN", "attendance": AttendanceSerializer(att).data}, status=201)

        if in_record and not out_record:
            att = create_record(Attendance.ACTION_OUT)
            if not att:
                return Response({"error": "Erreur lors de l'enregistrement RFID."}, status=500)
            return Response({"action": "OUT", "attendance": AttendanceSerializer(att).data}, status=201)

        # Si IN et OUT déjà enregistrés, ne rien faire
        return Response({"note": "Présence déjà enregistrée pour la journée"}, status=200)


# -----------------------------------------------------------------
# 5) Rapport élève ou classe
# -----------------------------------------------------------------
class AttendanceReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        classroom_id = request.query_params.get("classroom")
        student_id = request.query_params.get("student")
        start = request.query_params.get("start_date")
        end = request.query_params.get("end_date")

        if classroom_id:
            classroom = get_object_or_404(ClassRoom, pk=classroom_id)
            report = Attendance.get_class_report(classroom, start, end)
        elif student_id:
            student = get_object_or_404(Student, pk=student_id)
            report = Attendance.get_student_report(student, start, end)
        else:
            return Response({"error": "classroom or student parameter required"}, status=400)

        return Response(report)


# -----------------------------------------------------------------
# 6) Notification aux parents
# -----------------------------------------------------------------
def send_absence_notification(student, reason=""):
    subject = f"Absence / Retard: {student.user.username}"
    message = f"""
Bonjour,

L'élève {student.user.username} est absent ou en retard.
Raison: {reason}

Merci.
"""
    recipients = [p.email for p in student.parents.all() if p.email]
    if recipients:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients)


class NotifyAbsencesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        student_id = request.data.get("student_id")
        reason = request.data.get("reason", "")

        if not student_id:
            return Response({"error": "student_id required"}, status=400)

        student = get_object_or_404(Student, pk=student_id)
        send_absence_notification(student, reason)

        return Response({"status": "notification sent"})
