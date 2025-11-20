from rest_framework import serializers
from .models import Student
from accounts.models import User
from classes.models import ClassRoom
from schoolyear.models import SchoolYear

class StudentSerializer(serializers.ModelSerializer):
    # Lecture : infos du User
    username = serializers.ReadOnlyField(source='user.username')
    matricule = serializers.ReadOnlyField(source='user.matricule')
    photo = serializers.ImageField(source='user.photo', read_only=True)

    # Lecture/écriture : relations
    school_year = serializers.PrimaryKeyRelatedField(queryset=SchoolYear.objects.all())
    classroom = serializers.PrimaryKeyRelatedField(queryset=ClassRoom.objects.all(), allow_null=True)
    parents = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Roles.PARENT),
        many=True,
        required=False
    )

    class Meta:
        model = Student
        fields = [
            'id',
            'user',
            'username',
            'matricule',
            'photo',
            'school_year',
            'classroom',
            'parents'
        ]

