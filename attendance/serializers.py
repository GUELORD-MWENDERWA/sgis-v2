from rest_framework import serializers
from .models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    # Infos utilisateurs
    user_username = serializers.ReadOnlyField(source='user.username')
    student_username = serializers.ReadOnlyField(
        source='student.user.username', default=None
    )

    # Infos classe et année scolaire
    classroom_name = serializers.ReadOnlyField(source='classroom.name', default=None)
    school_year_name = serializers.ReadOnlyField(source='school_year.name', default=None)

    # Qui a enregistré la présence
    recorded_by_username = serializers.ReadOnlyField(source='recorded_by.username', default=None)

    class Meta:
        model = Attendance
        fields = [
            'id',
            'user',
            'user_username',
            'student',
            'student_username',
            'role',
            'school_year',
            'school_year_name',
            'classroom',
            'classroom_name',
            'action',
            'status',
            'reason',
            'date',
            'time',
            'entry_method',
            'recorded_by',
            'recorded_by_username',
            'note',
            'created_at',
        ]
        read_only_fields = [
            'date',
            'time',
            'entry_method',
            'created_at',
            'status',
            'user_username',
            'student_username',
            'classroom_name',
            'school_year_name',
            'recorded_by_username',
        ]
