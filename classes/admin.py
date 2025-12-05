from django.contrib import admin
from .models import ClassRoom

@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    # -------------------------------
    # Colonnes affichées dans la liste
    # -------------------------------
    list_display = (
        'name',
        'year_name',
        'main_teacher_username',
        'get_teachers',
        'get_students',
    )

    # -------------------------------
    # Filtres disponibles
    # -------------------------------
    list_filter = (
        'year',
        'main_teacher',
        'teachers',
    )

    # -------------------------------
    # Champs de recherche
    # -------------------------------
    search_fields = (
        'name',
        'main_teacher__username',
        'teachers__username',
        'students_profiles__user__username',
        'year__name',
    )

    # -------------------------------
    # Méthodes pour afficher ManyToMany lisiblement
    # -------------------------------
    def main_teacher_username(self, obj):
        return obj.main_teacher.username if obj.main_teacher else None
    main_teacher_username.short_description = "Professeur principal"

    def year_name(self, obj):
        return obj.year.name if obj.year else None
    year_name.short_description = "Année scolaire"

    def get_teachers(self, obj):
        """Affiche tous les enseignants assignés à cette classe"""
        return ", ".join([teacher.username for teacher in obj.teachers.all()])
    get_teachers.short_description = 'Enseignants'

    def get_students(self, obj):
        """Affiche tous les élèves assignés à la classe via Student.classroom"""
        return ", ".join([s.user.username for s in obj.students_profiles.all()])
    get_students.short_description = 'Élèves'
