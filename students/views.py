from rest_framework import viewsets, permissions
from .models import Student
from .serializers import StudentSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Autorise tout le monde à lire, mais seul l'admin peut écrire.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.role == 'ADMIN'

class StudentViewSet(viewsets.ModelViewSet):
    """
    CRUD pour les élèves :
    - Lecture ouverte à tous les utilisateurs authentifiés
    - Modification réservée à l'administrateur
    """
    queryset = Student.objects.all().select_related('user', 'school_year', 'classroom').prefetch_related('parents')
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrReadOnly]
