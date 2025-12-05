from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    # -------------------------------
    # Colonnes affichées dans la liste
    # -------------------------------
    list_display = ('user_username', 'school_year_name', 'get_parents', 'classroom_name')
    
    # -------------------------------
    # Filtres disponibles
    # -------------------------------
    list_filter = ('school_year', 'classroom')
    
    # -------------------------------
    # Champs de recherche
    # -------------------------------
    search_fields = ('user__username', 'user__matricule', 'parents__username')

    # -------------------------------
    # Méthodes pour afficher les relations lisiblement
    # -------------------------------
    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = "User"

    def school_year_name(self, obj):
        return obj.school_year.name if obj.school_year else None
    school_year_name.short_description = "Année scolaire"

    def classroom_name(self, obj):
        return obj.classroom.name if obj.classroom else None
    classroom_name.short_description = "Classe"

    def get_parents(self, obj):
        """Affiche les parents associés à l’élève"""
        return ", ".join([parent.username for parent in obj.parents.all()])
    get_parents.short_description = "Parents"

