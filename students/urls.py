from rest_framework import routers
from django.urls import path, include
from .views import StudentViewSet

router = routers.DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')

urlpatterns = [
    path('', include(router.urls)),
]

# Endpoints disponibles :
# GET /api/students/          -> Liste des élèves (tous les utilisateurs connectés)
# POST /api/students/         -> Crée un élève (admin seulement)
# GET /api/students/{id}/     -> Détail d'un élève (tous les utilisateurs connectés)
# PUT /api/students/{id}/     -> Remplace entièrement un élève (admin seulement)
# PATCH /api/students/{id}/   -> Met à jour partiellement un élève (admin seulement)
# DELETE /api/students/{id}/  -> Supprime un élève (admin seulement)
