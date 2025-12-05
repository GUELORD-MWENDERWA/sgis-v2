from rest_framework import serializers
from .models import QRCode


class QRCodeSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    qr_code_token = serializers.UUIDField(source='code', read_only=True)  # Nouveau champ pour le token
    qr_image_url = serializers.SerializerMethodField()

    class Meta:
        model = QRCode
        fields = ["id", "user", "qr_code_token", "qr_image_url", "created_at"]

    def get_qr_image_url(self, obj):
        if obj.code_image:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.code_image.url)
        return None
