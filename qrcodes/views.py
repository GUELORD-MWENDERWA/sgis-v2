import json
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import QRCode
from .serializers import QRCodeSerializer
from .permissions import IsAdminOrSelf


class QRCodeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/qrcodes/ → liste (admin)
    GET /api/qrcodes/<id>/ → détail (admin ou propriétaire)
    """
    queryset = QRCode.objects.all()
    serializer_class = QRCodeSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            return [IsAdminOrSelf()]
        return []  # Admin gère via permission globale (settings)


class MyQRCodeView(APIView):
    """
    GET /api/qrcodes/my/
    Récupère le QR code de l'utilisateur connecté
    """
    def get(self, request):
        if not hasattr(request.user, "qr_code"):
            return Response({"error": "QR code non généré"}, status=404)

        serializer = QRCodeSerializer(request.user.qr_code, context={"request": request})
        return Response(serializer.data)


class ValidateQRCodeData(APIView):
    """
    POST /api/qrcodes/validate/
    Body:
    {
        "data": "{... string json lu après scan ...}"
    }
    """
    def post(self, request):
        raw = request.data.get("data")
        if not raw:
            return Response({"error": "Aucune donnée transmise"}, status=400)

        try:
            payload = json.loads(raw)
        except:
            return Response({"error": "QR code invalide"}, status=400)

        matricule = payload.get("matricule")
        if not matricule:
            return Response({"error": "Données QR invalides"}, status=400)

        # Retrouver l’utilisateur
        from accounts.models import User
        try:
            user = User.objects.get(matricule=matricule)
        except User.DoesNotExist:
            return Response({"error": "Utilisateur non trouvé"}, status=404)

        return Response({
            "valid": True,
            "matricule": user.matricule,
            "username": user.username,
            "role": user.role,
            "full_name": user.get_full_name(),
        })
