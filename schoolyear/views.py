from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import SchoolYear
from .serializers import SchoolYearSerializer

class SchoolYearViewSet(viewsets.ModelViewSet):
    """
    CRUD pour l'année scolaire.
    Seul l'administrateur peut gérer les années.
    """
    queryset = SchoolYear.objects.all()
    serializer_class = SchoolYearSerializer
    permission_classes = [IsAdminUser]
