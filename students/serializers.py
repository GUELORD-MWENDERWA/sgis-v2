from rest_framework import serializers
from .models import Student
from accounts.models import User
from classes.models import ClassRoom
from schoolyear.models import SchoolYear

class StudentSerializer(serializers.ModelSerializer):
    # -------------------------------
    # Lecture : infos du User
    # -------------------------------
    username = serializers.ReadOnlyField(source='user.username')
    matricule = serializers.ReadOnlyField(source='user.matricule')
    photo = serializers.ImageField(source='user.photo', read_only=True)
    full_name = serializers.ReadOnlyField(source='user.get_full_name')

    # -------------------------------
    # Lecture/écriture : relations
    # -------------------------------
    school_year = serializers.PrimaryKeyRelatedField(queryset=SchoolYear.objects.all())
    classroom = serializers.PrimaryKeyRelatedField(queryset=ClassRoom.objects.all(), allow_null=True)
    parents = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='PARENT'),
        many=True,
        required=False
    )

    # -------------------------------
    # Lecture : champs calculés
    # -------------------------------
    classroom_name = serializers.ReadOnlyField(source='classroom.name')
    parent_usernames = serializers.SerializerMethodField()
    parent_matricules = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id',
            'user',
            'username',
            'full_name',
            'matricule',
            'photo',
            'school_year',
            'classroom',
            'classroom_name',
            'parents',
            'parent_usernames',
            'parent_matricules'
        ]

    # -------------------------------
    # Méthodes pour SerializerMethodField
    # -------------------------------
    def get_parent_usernames(self, obj):
        return [parent.username for parent in obj.parents.all()]

    def get_parent_matricules(self, obj):
        return [parent.matricule for parent in obj.parents.all()]

    # -------------------------------
    # Création / mise à jour automatique
    # -------------------------------
    def create(self, validated_data):
        parents_data = validated_data.pop('parents', [])
        student = Student.objects.create(**validated_data)
        if parents_data:
            student.parents.set(parents_data)
        return student

    def update(self, instance, validated_data):
        parents_data = validated_data.pop('parents', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if parents_data is not None:
            instance.parents.set(parents_data)
        instance.save()
        return instance
