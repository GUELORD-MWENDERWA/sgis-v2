from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AttendanceViewSet,
    AttendanceSessionViewSet,
    ScanAttendanceAPIView,
    RFIDAttendanceAPIView,
    AttendanceReportAPIView,
    NotifyAbsencesAPIView
)

app_name = "attendance"

# -------------------------------------------
# ROUTER : CRUD PRESENCE + CRUD SESSION
# -------------------------------------------
router = DefaultRouter()
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'session', AttendanceSessionViewSet, basename='attendance_session')

# -------------------------------------------
# URLS COMPLETS
# -------------------------------------------
urlpatterns = [

    # ---- Enregistrement via scan QR ----
    path('scan/', ScanAttendanceAPIView.as_view(), name='scan'),

    # ---- Enregistrement via RFID ----
    path('rfid/', RFIDAttendanceAPIView.as_view(), name='rfid'),

    # ---- Rapport de présence ----
    path('report/', AttendanceReportAPIView.as_view(), name='report'),

    # ---- Notifications parents ----
    path('notify/', NotifyAbsencesAPIView.as_view(), name='notify'),

    # ---- CRUD Attendance + Sessions ----
    path('', include(router.urls)),
]


"""
ENDPOINTS DISPONIBLES :

--- QR CODE ---
POST   /api/attendance/scan/  

--- RFID MODULE ---
POST   /api/attendance/rfid/  

--- CRUD SINGLE PRESENCE ---
GET    /api/attendance/attendance/
POST   /api/attendance/attendance/
GET    /api/attendance/attendance/{id}/
PUT    /api/attendance/attendance/{id}/
PATCH  /api/attendance/attendance/{id}/
DELETE /api/attendance/attendance/{id}/

--- CRUD ATTENDANCE SESSION ---
GET    /api/attendance/session/
POST   /api/attendance/session/
GET    /api/attendance/session/{id}/
PUT    /api/attendance/session/{id}/
PATCH  /api/attendance/session/{id}/
DELETE /api/attendance/session/{id}/

--- REPORT ---
GET    /api/attendance/report/?classroom=1&start_date=2025-01-01&end_date=2025-01-31
GET    /api/attendance/report/?student=3&start_date=2025-01-01&end_date=2025-01-31

--- NOTIFY PARENTS ---
POST   /api/attendance/notify/
"""
