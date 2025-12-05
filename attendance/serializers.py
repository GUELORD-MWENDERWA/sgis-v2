from rest_framework import serializers
from django.utils import timezone
from .models import Attendance, AttendanceSession
from rfid.models import RFIDCard

# ----------------------------------------------------------
# 1) SERIALIZER DES SESSIONS DE PRÉSENCE
# ----------------------------------------------------------
class AttendanceSessionSerializer(serializers.ModelSerializer):
    classroom_name = serializers.ReadOnlyField(source="classroom.name")
    school_year_name = serializers.ReadOnlyField(source="school_year.name")

    class Meta:
        model = AttendanceSession
        fields = [
            "id",
            "name",
            "classroom",
            "classroom_name",
            "school_year",
            "school_year_name",
            "date",
            "opened_at",
            "closed_at",
            "is_open",
        ]
        read_only_fields = ["opened_at", "closed_at", "is_open"]

# ----------------------------------------------------------
# 2) SERIALIZER COMPLET DES PRÉSENCES
# ----------------------------------------------------------
class AttendanceSerializer(serializers.ModelSerializer):
    # -------- Infos utilisateur --------
    user_username = serializers.ReadOnlyField(source='user.username')
    user_matricule = serializers.ReadOnlyField(source='user.matricule')
    student_username = serializers.ReadOnlyField(source='student.user.username', default=None)

    # -------- Infos classe / année --------
    classroom_name = serializers.ReadOnlyField(source='classroom.name', default=None)
    school_year_name = serializers.ReadOnlyField(source='school_year.name', default=None)

    # -------- Qui a enregistré --------
    recorded_by_username = serializers.ReadOnlyField(source='recorded_by.username', default=None)

    # -------- Session --------
    session_name = serializers.ReadOnlyField(source='session.name', default=None)
    opened_at = serializers.SerializerMethodField()
    closed_at = serializers.SerializerMethodField()

    # -------- RFID --------
    rfid_uid = serializers.ReadOnlyField(source='rfid_card.uid', default=None)
    rfid_label = serializers.ReadOnlyField(source='rfid_card.label', default=None)

    class Meta:
        model = Attendance
        fields = [
            'id',
            'session',
            'session_name',
            'opened_at',
            'closed_at',
            'user',
            'user_username',
            'user_matricule',
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
            'rfid_card',
            'rfid_uid',
            'rfid_label',
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
            'user_matricule',
            'student_username',
            'classroom_name',
            'school_year_name',
            'recorded_by_username',
            'session_name',
            'rfid_uid',
            'rfid_label',
            'opened_at',
            'closed_at',
        ]

    # -------- Conversion datetime → time pour session --------
    def get_opened_at(self, obj):
        return obj.session.opened_at.isoformat() if obj.session and obj.session.opened_at else None

    def get_closed_at(self, obj):
        return obj.session.closed_at.isoformat() if obj.session and obj.session.closed_at else None

# ----------------------------------------------------------
# 3) SERIALIZER POUR CRÉATION DE PRÉSENCE
# ----------------------------------------------------------
class AttendanceCreateSerializer(serializers.ModelSerializer):
    """
    Utilisé pour :
    - Scan QR
    - Scan RFID
    - Enregistrement manuel
    """
    rfid_uid = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Attendance
        fields = [
            "session",
            "user",
            "student",
            "role",
            "school_year",
            "classroom",
            "action",
            "reason",
            "note",
            "rfid_uid",
            "entry_method",
        ]

    def validate(self, attrs):
        session = attrs.get("session")

        if session and not session.is_open:
            raise serializers.ValidationError("Cette session est fermée.")

        # Vérification RFID
        rfid_uid = self.initial_data.get("rfid_uid")
        if rfid_uid:
            # user may be provided as instance or pk; attempt lookup by uid and accept assigned to any user if not matched
            try:
                if attrs.get("user"):
                    card = RFIDCard.objects.get(uid=rfid_uid, user=attrs.get("user"))
                else:
                    card = RFIDCard.objects.get(uid=rfid_uid)
            except RFIDCard.DoesNotExist:
                raise serializers.ValidationError(
                    f"Carte RFID '{rfid_uid}' introuvable ou non assignée à cet utilisateur."
                )
            attrs["rfid_card"] = card
            attrs["entry_method"] = Attendance.ENTRY_RFID

        else:
            # Si pas de RFID → QR ou MANUEL
            if not attrs.get("entry_method"):
                attrs["entry_method"] = Attendance.ENTRY_QR

        return attrs

    def create(self, validated_data):
        """
        Override create pour forcer la conversion du champ time en `time` et éviter l'erreur DRF
        """
        validated_data['date'] = timezone.localdate()
        validated_data['time'] = timezone.localtime().time()
        return super().create(validated_data)
