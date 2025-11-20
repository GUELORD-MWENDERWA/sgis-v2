from django.contrib import admin
from .models import ClassRoom

@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'main_teacher')
    list_filter = ('year', 'main_teacher')
    search_fields = ('name', 'main_teacher__username', 'year__name')
