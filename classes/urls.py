from rest_framework import routers
from django.urls import path, include
from .views import ClassRoomViewSet

app_name = "classes"  # utile pour le reverse et namespace

# Création du routeur automatique DRF
router = routers.DefaultRouter()
router.register(r'classes', ClassRoomViewSet, basename='classroom')

urlpatterns = [
    path('', include(router.urls)),
]

# Endpoints disponibles :
# GET    /api/classes/           -> Liste toutes les classes (tous les utilisateurs connectés)
# POST   /api/classes/           -> Crée une nouvelle classe (admin seulement)
# GET    /api/classes/{id}/      -> Détail d'une classe (tous les utilisateurs connectés)
# PUT    /api/classes/{id}/      -> Remplace entièrement une classe (admin seulement)
# PATCH  /api/classes/{id}/      -> Met à jour partiellement une classe (admin seulement)
# DELETE /api/classes/{id}/      -> Supprime une classe (admin seulement)
