from django.contrib import admin
from .models import Attendance, AttendanceSession

# -------------------------------------------------------
# Admin pour les sessions de présence
# -------------------------------------------------------
@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'classroom',
        'school_year',
        'date',
        'opened_at',
        'closed_at',
        'is_open',
    )
    list_filter = ('classroom', 'school_year', 'date', 'is_open')
    search_fields = ('name', 'classroom__name', 'school_year__name')


# -------------------------------------------------------
# Admin pour les présences
# -------------------------------------------------------
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user_username',
        'role',
        'student_username',
        'classroom_name',
        'school_year_name',
        'session_name',       # ← nouvelle colonne
        'date',
        'time',
        'action',
        'status',
        'reason',
        'recorded_by_username',
    )

    list_filter = (
        'role',
        'status',
        'date',
        'classroom',
        'school_year',
    )

    search_fields = (
        'user__username',
        'user__matricule',
        'student__user__username',
        'reason',
    )

    # Méthodes pour afficher les relations lisiblement
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

    def session_name(self, obj):
        return obj.session.name if obj.session else None
    session_name.short_description = "Session"
