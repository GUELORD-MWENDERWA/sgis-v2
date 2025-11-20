from rest_framework import viewsets, permissions
from .models import ClassRoom
from .serializers import ClassRoomSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Autorise tout le monde en lecture, mais seul l'admin peut écrire.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.role == 'ADMIN'

class ClassRoomViewSet(viewsets.ModelViewSet):
    """
    CRUD pour les classes :
    - Lecture ouverte à tous les utilisateurs authentifiés
    - Modification réservée à l'administrateur
    """
    queryset = ClassRoom.objects.all().select_related('year', 'main_teacher').prefetch_related('teachers', 'students')
    serializer_class = ClassRoomSerializer
    permission_classes = [IsAdminOrReadOnly]
