from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.parsers import MultiPartParser, FormParser

from .models import User
from .serializers import UserSerializer
from .permissions import IsAdminOnly
from .serializers import UserFullSerializer


# ------------------------------------------------------------
# 1. CREATE USERS BY ROLE (ADMIN ONLY)
# ------------------------------------------------------------

class CreateStudentView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOnly]

    def perform_create(self, serializer):
        serializer.save(role="STUDENT")


class CreateParentView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOnly]

    def perform_create(self, serializer):
        serializer.save(role="PARENT")


class CreateTeacherView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOnly]

    def perform_create(self, serializer):
        serializer.save(role="TEACHER")


# ------------------------------------------------------------
# 2. GET CURRENT USER (PROFILE)
# ------------------------------------------------------------

class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class MeFullView(APIView):
    permission_classes = [IsAuthenticated]
 
    def get(self, request):
        serializer = UserFullSerializer(request.user)
        return Response(serializer.data)
    

# ------------------------------------------------------------
# 3. UPDATE PROFILE (email, phone, birth_date…)
# ------------------------------------------------------------

class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ------------------------------------------------------------
# 4. CHANGE PASSWORD
# ------------------------------------------------------------

from rest_framework import serializers

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old = serializer.validated_data["old_password"]
        new = serializer.validated_data["new_password"]

        if not user.check_password(old):
            return Response({"error": "Ancien mot de passe incorrect"}, status=400)

        user.set_password(new)
        user.save()

        return Response({"message": "Mot de passe changé avec succès"})


# ------------------------------------------------------------
# 5. UPLOAD PROFILE PHOTO
# ------------------------------------------------------------

class UploadProfilePhotoView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        user = request.user

        if "photo" not in request.data:
            return Response({"error": "Aucune photo fournie"}, status=400)

        user.photo = request.data["photo"]
        user.save()

        return Response({"message": "Photo uploadée avec succès"})


# ------------------------------------------------------------
# 6. LIST USERS (ADMIN ONLY)
# ------------------------------------------------------------

class ListUsersView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOnly]
