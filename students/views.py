from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Student
from .serializers import StudentSerializer
from classes.models import ClassRoom
from schoolyear.models import SchoolYear

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Lecture : tous les utilisateurs authentifiés
    Écriture : seulement ADMIN
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'ADMIN'

class StudentViewSet(viewsets.ModelViewSet):
    """
    CRUD pour les étudiants avec sélection obligatoire de la classe.
    """
    queryset = Student.objects.all().select_related(
        'user', 'school_year', 'classroom'
    ).prefetch_related('parents')
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrReadOnly]

    def create(self, request, *args, **kwargs):
        # -------------------------------
        # Récupération des données
        # -------------------------------
        data = request.data.copy()
        school_year_id = data.get('school_year')
        classroom_id = data.get('classroom')

        # -------------------------------
        # Vérifier l'année scolaire
        # -------------------------------
        if not school_year_id:
            return Response(
                {"error": "school_year est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # -------------------------------
        # Liste des classes disponibles
        # -------------------------------
        classes = ClassRoom.objects.filter(year_id=school_year_id)
        if classroom_id:
            # Vérifier que la classe choisie est valide
            if not classes.filter(id=classroom_id).exists():
                return Response(
                    {"error": "La classe choisie n'existe pas pour cette année scolaire."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Proposer les classes disponibles
            class_list = [{"id": c.id, "name": c.name} for c in classes]
            if not class_list:
                return Response(
                    {"error": "Aucune classe existante pour cette année scolaire. Créez-en une d'abord."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {
                    "message": "Veuillez choisir une classe pour l'élève.",
                    "available_classes": class_list
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # -------------------------------
        # Création du Student après choix de la classe
        # -------------------------------
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        qs = super().get_queryset()
        year_id = self.request.query_params.get('school_year')
        class_id = self.request.query_params.get('classroom')
        parent_id = self.request.query_params.get('parent')

        if year_id:
            qs = qs.filter(school_year_id=year_id)
        if class_id:
            qs = qs.filter(classroom_id=class_id)
        if parent_id:
            qs = qs.filter(parents__id=parent_id)
        return qs
