from rest_framework import serializers
from .models import ClassRoom
from accounts.models import User
from schoolyear.models import SchoolYear

class ClassRoomSerializer(serializers.ModelSerializer):
    # Lecture : afficher le nom de l'année et du professeur principal
    year_name = serializers.ReadOnlyField(source='year.name')
    main_teacher_name = serializers.ReadOnlyField(source='main_teacher.username')

    # Lecture + écriture pour ManyToMany
    teachers = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Roles.TEACHER),
        many=True,
        required=False
    )
    students = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Roles.STUDENT),
        many=True,
        required=False
    )

    class Meta:
        model = ClassRoom
        fields = [
            'id',
            'name',
            'year',
            'year_name',
            'main_teacher',
            'main_teacher_name',
            'teachers',
            'students'
        ]
