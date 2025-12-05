from rest_framework import serializers
from .models import RFIDCard, RFIDModule


class RFIDCardSerializer(serializers.ModelSerializer):
    available = serializers.SerializerMethodField()

    class Meta:
        model = RFIDCard
        fields = [
            "id",
            "uid",
            "label",
            "notes",
            "user",
            "available",
            "created_at",
            "updated_at"
        ]

    def get_available(self, obj):
        return obj.user is None


class RFIDModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RFIDModule
        fields = [
            "id",
            "name",
            "location",
            "token",
            "notes",
            "created_at",
        ]
        read_only_fields = ["token", "created_at"]
