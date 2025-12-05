import json
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import QRCode
from .serializers import QRCodeSerializer
from .permissions import IsAdminOrSelf


class QRCodeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QRCode.objects.all()
    serializer_class = QRCodeSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            return [IsAdminOrSelf()]
        return []


class MyQRCodeView(APIView):
    """
    GET /api/qrcodes/my/
    Récupère le QR code de l'utilisateur connecté
    """
    permission_classes = [IsAuthenticated]

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
        "data": "{... string scannée ...}"
    }
    """
    def post(self, request):
        # Accept either a JSON string in `data` or a dict with token/matricule/user_id
        raw = request.data.get("data") if "data" in request.data else request.data

        if not raw:
            return Response({"error": "Aucune donnée transmise"}, status=400)

        try:
            if isinstance(raw, (str, bytes)):
                payload = json.loads(raw)
            elif isinstance(raw, dict):
                payload = raw
            else:
                payload = json.loads(json.dumps(raw))
        except Exception:
            return Response({"error": "QR code invalide"}, status=400)

        # On cherche l'utilisateur via le token UUID
        token = payload.get("token") or payload.get("code")
        matricule = payload.get("matricule")
        user_id = payload.get("user_id")

        user = None
        from accounts.models import User

        if user_id:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return Response({"error": "Utilisateur introuvable"}, status=404)

        if not user and matricule:
            try:
                user = User.objects.get(matricule=matricule)
            except User.DoesNotExist:
                return Response({"error": "Matricule non reconnu"}, status=404)

        if not user and token:
            try:
                qr = QRCode.objects.get(code=token)
                user = qr.user
            except QRCode.DoesNotExist:
                return Response({"error": "QR code non reconnu"}, status=404)

        if not user:
            return Response({"error": "Aucun utilisateur trouvé dans les données"}, status=400)

        return Response({
            "valid": True,
            "username": user.username,
            "role": user.role,
            "full_name": user.get_full_name(),
        })
