from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import IntegrityError

from accounts.models import User
from .models import RFIDCard, RFIDModule
from .serializers import RFIDCardSerializer, RFIDModuleSerializer


# ----------------------------
# Ajouter une carte RFID
# ----------------------------
class CreateRFIDCard(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        uid = request.data.get("uid")

        if not uid:
            return Response({"error": "UID obligatoire"}, status=400)

        if RFIDCard.objects.filter(uid=uid).exists():
            return Response({"error": "Cette carte existe déjà"}, status=400)

        # Optional assignment: prefer explicit user_id if provided
        user = None
        user_id = request.data.get("user_id")
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"error": "Utilisateur introuvable"}, status=404)

        # Also allow quick assign to the request user with a flag
        assign_to_request_user = request.data.get("assign_to_request_user")
        if not user and assign_to_request_user in (True, "true", "1", "True"):
            if hasattr(request, "user") and request.user and request.user.is_authenticated:
                user = request.user

        try:
            card = RFIDCard.objects.create(
                uid=uid,
                label=request.data.get("label"),
                notes=request.data.get("notes"),
                user=user,
            )
        except IntegrityError as e:
            return Response({"error": "Impossible de créer la carte RFID : contrainte DB violée."}, status=400)

        return Response(RFIDCardSerializer(card).data, status=201)


# ----------------------------
# Voir cartes disponibles
# ----------------------------
class ListAvailableRFIDCards(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cards = RFIDCard.objects.filter(user__isnull=True)
        return Response(RFIDCardSerializer(cards, many=True).data)


# ----------------------------
# Assigner carte → utilisateur
# ----------------------------
class AssignRFIDCardToUser(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.data.get("user_id")
        card_id = request.data.get("card_id")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Utilisateur introuvable"}, status=404)

        try:
            card = RFIDCard.objects.get(id=card_id)
        except RFIDCard.DoesNotExist:
            return Response({"error": "Carte RFID introuvable"}, status=404)

        if card.user:
            return Response({"error": "Carte déja assignée"}, status=400)

        if hasattr(user, "rfid_card"):
            return Response({"error": "L'utilisateur a déjà une carte"}, status=400)

        card.user = user
        card.save()

        return Response({"message": "Carte assignée"}, status=200)


# ----------------------------
# CRÉER UN MODULE RFID
# ----------------------------
class CreateRFIDModule(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            module = RFIDModule.objects.create(
                name=request.data.get("name"),
                location=request.data.get("location"),
                notes=request.data.get("notes"),
            )
        except IntegrityError:
            return Response({"error": "Impossible de créer le module RFID (contrainte DB)."}, status=400)
        return Response(RFIDModuleSerializer(module).data, status=201)


# ----------------------------
# Lister modules RFID
# ----------------------------
class ListRFIDModules(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        modules = RFIDModule.objects.all()
        return Response(RFIDModuleSerializer(modules, many=True).data)


# -------------------------------------
# Vérification du module (ESP32)
# -------------------------------------
class CheckRFIDModule(APIView):

    def post(self, request):
        token = request.data.get("token")

        if not token:
            return Response({"error": "Token manquant"}, status=400)

        try:
            module = RFIDModule.objects.get(token=token)
        except RFIDModule.DoesNotExist:
            return Response({"valid": False}, status=403)

        return Response({
            "valid": True,
            "module": module.name,
            "location": module.location
        })
