from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'school_year', 'get_parents', 'classroom')
    list_filter = ('school_year', 'classroom')
    search_fields = ('user__username', 'user__matricule')

    def get_parents(self, obj):
        return ", ".join([parent.username for parent in obj.parents.all()])
    get_parents.short_description = 'Parents'
