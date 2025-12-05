from rest_framework import routers
from django.urls import path, include
from .views import SchoolYearViewSet

router = routers.DefaultRouter()
router.register(r'schoolyears', SchoolYearViewSet, basename='schoolyear')

urlpatterns = [
    path('schoolyear/', include(router.urls)),  # API CRUD pour SchoolYear (Admin seulement)
]
