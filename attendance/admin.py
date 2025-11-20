from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    # Affichage des colonnes dans la liste
    list_display = (
        'id',
        'user_username',   # username de l'utilisateur
        'role',
        'student_username', # username de l'étudiant lié
        'classroom_name',   # nom de la classe
        'school_year_name', # nom de l'année scolaire
        'date',
        'time',
        'action',
        'status',
        'reason',
        'recorded_by_username', # username de la personne qui a enregistré
    )

    # Filtres disponibles sur la liste
    list_filter = (
        'role',
        'status',
        'date',
        'classroom',
        'school_year',
    )

    # Champs de recherche
    search_fields = (
        'user__username',
        'user__matricule',
        'student__user__username',
        'reason',
    )

    # Pour afficher les attributs liés
    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = "User"

    def student_username(self, obj):
        return obj.student.user.username if obj.student else None
    student_username.short_description = "Student"

    def classroom_name(self, obj):
        return obj.classroom.name if obj.classroom else None
    classroom_name.short_description = "Classroom"

    def school_year_name(self, obj):
        return obj.school_year.name if obj.school_year else None
    school_year_name.short_description = "School Year"

    def recorded_by_username(self, obj):
        return obj.recorded_by.username if obj.recorded_by else None
    recorded_by_username.short_description = "Recorded By"
