from rest_framework import serializers
from .models import ClassRoom
from accounts.models import User

class ClassRoomSerializer(serializers.ModelSerializer):
    # Lecture : afficher le nom de l'année et du professeur principal
    year_name = serializers.ReadOnlyField(source='year.name')
    main_teacher_name = serializers.ReadOnlyField(source='main_teacher.username')

    # ManyToMany enseignants
    teachers = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Roles.TEACHER),
        many=True,
        required=False
    )

    # Élèves -> seulement lecture car liés via Student.classroom
    students = serializers.SerializerMethodField()

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

    def get_students(self, obj):
        """
        Retourne une liste des IDs utilisateurs des élèves de cette classe.
        """
        return [
            student.user.id
            for student in obj.students_profiles.all()
        ]

    def create(self, validated_data):
        teachers_data = validated_data.pop('teachers', [])
        classroom = ClassRoom.objects.create(**validated_data)
        classroom.teachers.set(teachers_data)
        return classroom

    def update(self, instance, validated_data):
        teachers_data = validated_data.pop('teachers', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if teachers_data is not None:
            instance.teachers.set(teachers_data)
        instance.save()
        return instance
