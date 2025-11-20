from rest_framework import serializers
from .models import QRCode


class QRCodeSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    matricule = serializers.CharField(source='user.matricule', read_only=True)
    qr_image_url = serializers.SerializerMethodField()

    class Meta:
        model = QRCode
        fields = ["id", "user", "matricule", "qr_image_url", "created_at"]

    def get_qr_image_url(self, obj):
        if obj.code_image:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.code_image.url)
        return None
