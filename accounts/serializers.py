from rest_framework import serializers
from django.core.files.images import get_image_dimensions
from accounts.models import User
from students.models import Student
from classes.models import ClassRoom
from qrcodes.models import QRCode

# ----------------------------------------
# Serializer de base pour User
# ----------------------------------------
class UserSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(max_length=None, use_url=True, required=False)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "role", "photo",
            "phone", "birth_date", "matricule"
        ]
        read_only_fields = ["matricule"]

    def validate_photo(self, value):
        """Vérifie la taille maximale de l'image"""
        max_width = 1024
        max_height = 1024
        width, height = get_image_dimensions(value)
        if width > max_width or height > max_height:
            raise serializers.ValidationError(
                f"L'image ne doit pas dépasser {max_width}x{max_height} pixels."
            )
        return value

# ----------------------------------------
# Serializer pour le profil étudiant
# ----------------------------------------
class StudentInfoSerializer(serializers.ModelSerializer):
    classroom_name = serializers.ReadOnlyField(source='classroom.name')
    school_year_name = serializers.ReadOnlyField(source='school_year.name')
    parents_usernames = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['school_year', 'school_year_name', 'classroom', 'classroom_name', 'parents_usernames']

    def get_parents_usernames(self, obj):
        return [p.username for p in obj.parents.all()]

# ----------------------------------------
# Serializer complet pour me/full/
# ----------------------------------------
class UserFullSerializer(serializers.ModelSerializer):
    student_profile = StudentInfoSerializer(read_only=True)
    qr_code_url = serializers.ImageField(source='qr_code.code_image', read_only=True)
    teaching_classes = serializers.SerializerMethodField()
    children_usernames = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'photo', 'phone', 'birth_date', 'matricule',
            'student_profile', 'qr_code_url', 'teaching_classes', 'children_usernames'
        ]

    def get_teaching_classes(self, obj):
        # Retourne les noms des classes enseignées par cet utilisateur
        classes = getattr(obj, 'classes_teaching', None)
        if classes is None:
            return []
        try:
            return [c.name for c in classes.all()]
        except Exception:
            return []

    def get_children_usernames(self, obj):
        # Retourne les usernames des enfants si l'utilisateur est parent
        children = getattr(obj, 'children', None)
        if children is None:
            return []
        try:
            return [c.user.username for c in children.all()]
        except Exception:
            return []
