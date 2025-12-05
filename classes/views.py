from rest_framework import viewsets, permissions
from rest_framework.permissions import SAFE_METHODS

from .models import ClassRoom
from .serializers import ClassRoomSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permissions pour les classes :

    - Lecture (GET, HEAD, OPTIONS) → tous les utilisateurs authentifiés
    - Écriture (POST, PUT, PATCH, DELETE) → uniquement ADMIN
    """

    def has_permission(self, request, view):
        # Lecture autorisée si utilisateur authentifié
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated

        # Écriture réservée à l'admin
        return request.user.role == 'ADMIN'


class ClassRoomViewSet(viewsets.ModelViewSet):
    """
    CRUD complet pour ClassRoom :
    - GET → accessible à tout utilisateur authentifié
    - POST/PUT/PATCH/DELETE → uniquement ADMIN
    """

    queryset = (
        ClassRoom.objects.all()
        .select_related("year", "main_teacher")
        .prefetch_related("teachers", "students_profiles")  # étudiants via Student.classroom
    )

    serializer_class = ClassRoomSerializer
    permission_classes = [IsAdminOrReadOnly]
