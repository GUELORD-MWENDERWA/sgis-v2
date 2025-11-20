from django.urls import path, include  # include importé correctement
from .views import (
    AttendanceViewSet,
    ScanAttendanceAPIView,   # anciennement ScanQRCodeView
    # Si tu as d'autres vues spécifiques comme MyAttendanceView, AttendanceListView, ValidateAttendanceView
    # elles doivent être importées ici
)

from rest_framework.routers import DefaultRouter

app_name = "attendance"

# Router pour CRUD complet (Admin/Teacher/Owner)
router = DefaultRouter()
router.register(r'crud', AttendanceViewSet, basename='attendance_crud')

urlpatterns = [
    # Scanner un QR code pour enregistrer présence
    path('scan/', ScanAttendanceAPIView.as_view(), name='scan_attendance'),

    # CRUD complet via router
    path('', include(router.urls)),

]

# ✅ Endpoints disponibles :
# POST /api/attendance/scan/           -> Scanner QR code
# GET  /api/attendance/crud/           -> Liste toutes les présences
# POST /api/attendance/crud/           -> Créer une présence manuellement
# GET  /api/attendance/crud/{id}/      -> Détails d'une présence
# PUT  /api/attendance/crud/{id}/      -> Modifier entièrement une présence
# PATCH /api/attendance/crud/{id}/    -> Modifier partiellement une présence
# DELETE /api/attendance/crud/{id}/   -> Supprimer une présence
